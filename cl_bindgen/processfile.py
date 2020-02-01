import sys
import os.path
from typing import NamedTuple

import clang.cindex as clang

from cl_bindgen.mangler import UnderscoreMangler, KeywordMangler, PrefixMangler, RegexSubMangler
import cl_bindgen.typetransformer as typetransformer

# name managler interface:
# can_mangle(string): returns true if the entity knows how to mangle the string
# mangle(string): returns the mangled string

class FileProcessor:

    def __init__(self, output, enum_manglers=[], type_manglers=[],
                 name_manglers=[], typedef_manglers=[], constant_manglers=[]):
        self.output = output
        self.enum_manglers = enum_manglers
        # self.type_manglers = type_manglers
        self.name_manglers = name_manglers
        self.constant_manglers = constant_manglers

        self.type_processor = typetransformer.TypeTransformer(type_manglers, typedef_manglers)

        self.skipped_record_decls = dict()
        self.skipped_enum_decls = dict()

    @staticmethod
    def _mangle_thing(thing, manglers):
        for mangler in manglers:
            if mangler.can_mangle(thing):
                thing = mangler.mangle(thing)
        return thing

    def _process_macro_def(self, cursor):
        location = cursor.location
        spelling = self._mangle_thing(cursor.spelling.lower(), self.constant_manglers)
        print(f"Found macro {spelling} definition in: {location.file}:{location.line}:{location.column}\n",
              file=sys.stderr)
        self.output.write("#| MACRO_DEFINITION\n")
        self.output.write(f"(defconstant {spelling} ACTUAL_VALUE_HERE)\n")
        self.output.write("|#\n\n")

    def _process_record(self, name, actual_type, cursor):
        output = ""
        if actual_type == typetransformer.ElaboratedType.UNION:
            output += f"(defcunion {name}"
        else:
            output += f"(defcstruct {name}"

        this_type = cursor.type

        for field in this_type.get_fields():
            field_name = self._mangle_thing(field.spelling.lower(), self.name_manglers)
            if field.is_anonymous():
                assert(field.type.kind == clang.TypeKind.ELABORATED)
                inner_name = name + '-' + field_name
                actual_elaborated_type = self.type_processor.determine_elaborated_type(field.type)
                if actual_elaborated_type == typetransformer.ElaboratedType.ENUM:
                    decl = field.type.get_declaration()
                    self._process_enum_as_constants(decl)
                    ret_val = ":int"
                elif actual_elaborated_type == typetransformer.ElaboratedType.UNION:
                    self._process_record(inner_name, actual_elaborated_type, field)
                    field_type =  "(:union " + name + '-' + field_name + ")"
                else:
                    # struct type
                    self._process_record(inner_name, actual_elaborated_type, field)
                    field_type = "(:struct " + name + '-' + field_name + ")"
            else:
                field_type = self.type_processor.cursor_lisp_type_str(field.type)
            output += f"\n  ({field_name} {field_type})"
        output += ")\n\n"
        sys.stdout.write(output)

    def _process_struct_decl(self, cursor):
        name = cursor.spelling.lower()
        if name:
            mangled_name = self.type_processor.mangle_type(name)
            self._process_record(mangled_name, typetransformer.ElaboratedType.STRUCT, cursor)
        else:
            self.skipped_record_decls[cursor.hash] = (typetransformer.ElaboratedType.STRUCT, cursor)

    def _process_union_decl(self, cursor):
        name = cursor.spelling.lower()
        if name:
            mangled_name = self.type_processor.mangle_type(name)
            self._process_record(mangled_name, typetransformer.ElaboratedType.UNION, cursor)
        else:
            self.skipped_record_decls[cursor.hash] = (typetransformer.ElaboratedType.UNION, cursor)

    def _process_realized_enum(self, name, cursor):
        self.output.write(f"(defcenum {name}")
        for field in cursor.get_children():
            name = self._mangle_thing(field.spelling.lower(), self.enum_manglers)

            self.output.write(f"\n  ({name} {field.enum_value})")
        self.output.write(")\n\n")

    def _process_enum_as_constants(self, cursor):
        for field in cursor.get_children():
            field_name = self._mangle_thing(field.spelling.lower(), self.constant_manglers)
            self.output.write(f"(defconstant {field_name} {field.enum_value})\n")
        self.output.write("\n")

    def _process_enum_decl(self, cursor):
        name = cursor.spelling.lower()
        if name:
            name = self.type_processor.mangle_type(name)
            self._process_realized_enum(name, cursor)
        else:
            self.skipped_enum_decls[cursor.hash] = cursor

    def _process_func_decl(self, cursor):
        name = cursor.spelling.lower()
        # mangle function names the same way as typenames:
        mangled_name = self.type_processor.mangle_type(name)

        ret_type = cursor.result_type
        lisp_ret_type = self.type_processor.cursor_lisp_type_str(ret_type)

        self.output.write("(defcfun ")
        if name != mangled_name:
            self.output.write(f'("{name}" {mangled_name})')
        else:
            self.output.write(f'"{name}"')
        self.output.write(f" {lisp_ret_type}")

        for arg in cursor.get_arguments():
            arg_name = arg.spelling.lower()
            arg_type_name = self.type_processor.cursor_lisp_type_str(arg.type)
            arg_mangled_name = self._mangle_thing(arg_name, self.name_manglers)

            if arg_name == None:
                arg_name = "unknown"

            self.output.write(f"\n  ({arg_mangled_name} {arg_type_name})")

        self.output.write(")\n\n")

    def _process_typedef_decl(self, cursor):
        name = cursor.spelling.lower()
        underlying_type = cursor.underlying_typedef_type
        base_decl = underlying_type.get_declaration()
        base_decl_hash = base_decl.hash
        base_type_str = None
        # Ensure that the type we are typdefing wasn't skipped:
        if base_decl_hash in self.skipped_enum_decls:
            del self.skipped_enum_decls[base_decl_hash]
            base_type_str = name.replace('_', '-') + "-enum"
            self._process_realized_enum(base_type_str, base_decl)
        else:
            decl_type = self.skipped_record_decls.get(base_decl_hash)
            if decl_type:
                del self.skipped_record_decls[base_decl_hash]
                base_type_str = name.replace('_', '-') + "-record"
                self._process_record(base_type_str, decl_type[0], base_decl)

        if not base_type_str:
            base_type_str = self.type_processor.cursor_lisp_type_str(underlying_type)
        mangled_name = self.type_processor.mangle_typedef(cursor.spelling.lower())
        self.output.write(f"(defctype {mangled_name} {base_type_str})\n\n")

    def _no_op(self,cursor):
        pass

    def _process_var_decl(self, cursor):
        location = cursor.location
        print(f"WARNING: Not processing var decl {location.file}:{location.line}:{location.column}\n",
              file=sys.stderr)

    def _unrecognized_cursorkind(self, cursor):
        location = cursor.location
        print(f"WARNING: Not processing {cursor.kind} {location.file}:{location.line}:{location.column}\n",
              file=sys.stderr)

    visit_table = {
        clang.CursorKind.MACRO_DEFINITION : _process_macro_def,
        clang.CursorKind.STRUCT_DECL   : _process_struct_decl,
        clang.CursorKind.ENUM_DECL     : _process_enum_decl,
        clang.CursorKind.FUNCTION_DECL : _process_func_decl,
        clang.CursorKind.TYPEDEF_DECL  : _process_typedef_decl,
        clang.CursorKind.UNION_DECL    : _process_union_decl,
        clang.CursorKind.VAR_DECL      : _process_var_decl,
        clang.CursorKind.INCLUSION_DIRECTIVE : _no_op,
        clang.CursorKind.MACRO_INSTANTIATION       : _no_op,
    }

    def process_file(self,filepath, args=[]):
        print(f"Processing file: {filepath}", file=sys.stderr)
        print(f"Arguments to clang: {args}", file=sys.stderr)

        if not os.path.isfile(filepath):
            print(f"Error: file doesn't exist: {filepath}", file=sys.stderr)
            exit(1)

        index = clang.Index.create()
        tu = index.parse(filepath, args=args,
                         options=clang.TranslationUnit.PARSE_DETAILED_PROCESSING_RECORD|clang.TranslationUnit.PARSE_SKIP_FUNCTION_BODIES)

        root_cursor = tu.cursor

        for child in root_cursor.get_children():
            location = child.location
            if location.file and location.file.name == filepath:
                handler_func = self.visit_table.get(child.kind)
                if handler_func:
                    handler_func(self, child)
                else:
                    self._unrecognized_cursorkind(child)

        # Once the file has been processed, if there are unused enums, output them as constants:
        for cursor in self.skipped_enum_decls.values():
            self._process_enum_as_constants(cursor)
        # issue warnings for anonymus structs:
        for (type, cursor) in self.skipped_record_decls.values():
            if type == typetransformer.ElaboratedType.STRUCT:
                sys.stderr.write("WARNING: Skipping unamed struct decl at ")
                sys.stderr.write(f"{location.file}:{location.line}:{location.column}\n")
            else:
                sys.stderr.write("WARNING: Skipping unamed union decl at ")
                sys.stderr.write(f"{location.file}:{location.line}:{location.column}\n")
