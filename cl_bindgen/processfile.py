import sys
import os.path
from typing import NamedTuple
from enum import Enum

import clang.cindex as clang
from clang.cindex import TypeKind, CursorKind

class FileProcessor:

    class ElaboratedType(Enum):
        UNION  = 0
        STRUCT = 1
        ENUM   = 2

    # This table contains types that don't have to be inferred or otherwise
    # built based off of the cursor type
    _builtin_table = {
        TypeKind.BOOL       : ":bool",
        TypeKind.DOUBLE     : ":double",
        TypeKind.FLOAT      : ":float",
        TypeKind.INT        : ":int",
        TypeKind.LONG       : ":long",
        TypeKind.LONGDOUBLE : ":long-double",
        TypeKind.LONGLONG   : ":long-long",
        TypeKind.SHORT      : ":short",
        TypeKind.UINT       : ":unsigned-int",
        TypeKind.ULONG      : ":unsigned-long",
        TypeKind.ULONGLONG  : ":unsigned-long-long",
        TypeKind.USHORT     : ":unsigned-short",
        TypeKind.VOID       : ":void",
        # Char types:
        # According to http://clang-developers.42468.n3.nabble.com/CXTypeKind-for-plain-char-td4036902.html,
        # we can ignore signedness for CHAR_U and CHAR_S, but not UCHAR and SCHAR:
        TypeKind.CHAR_U : ":char",
        TypeKind.CHAR_S : ":char",
        TypeKind.SCHAR  : ":signed-char",
        TypeKind.UCHAR  : "::unsigned-char"
    }

   # There a few typdefs that are known to CFFI that we don't need to manually define:
    _known_typedefs = {
        "uint64_t" : ":uint64",
        "uint32_t" : ":uint32",
        "uint16_t" : ":uint16",
        "uint8_t"  : ":uint8",
        "int64_t" : ":int64",
        "int32_t" : ":int32",
        "int16_t" : ":int16",
        "int8_t"  : ":int8",
    }

    def __init__(self, output, enum_manglers=[], type_manglers=[],
                 name_manglers=[], typedef_manglers=[], constant_manglers=[]):
        self.output = output
        self.enum_manglers = enum_manglers
        self.type_manglers = type_manglers
        self.typedef_manglers = typedef_manglers
        self.name_manglers = name_manglers
        self.constant_manglers = constant_manglers

        self.skipped_record_decls = dict()
        self.skipped_enum_decls = dict()

    @staticmethod
    def _mangle_string(thing, manglers):
        for mangler in manglers:
            if mangler.can_mangle(thing):
                thing = mangler.mangle(thing)
        return thing

    def _determine_elaborated_type(self, type_obj):
        named_type = type_obj.get_named_type()
        named_type_kind = named_type.kind
        if named_type_kind == TypeKind.RECORD:
            type_decl = type_obj.get_declaration()
            if type_decl.kind == CursorKind.UNION_DECL:
                return self.ElaboratedType.UNION
            elif type_decl.kind == CursorKind.STRUCT_DECL:
                return self.ElaboratedType.STRUCT
            else:
                raise Exception(f"Unknown cursorkind: {type_decl.kind}")
        elif named_type_kind == TypeKind.ENUM:
            return self.ElaboratedType.ENUM

    def _cursor_lisp_type_str(self, type_obj):
        assert(type(type_obj) == clang.Type)
        kind = type_obj.kind
        known_type = self._builtin_table.get(kind)
        if known_type:
            return known_type
        elif kind == TypeKind.TYPEDEF:
            type_decl = type_obj.get_declaration()
            # try the known typedefs:
            type_decl_str = type_decl.type.spelling
            known_type = self._known_typedefs.get(type_decl_str)
            if known_type:
                return known_type
            else:
                # assume that the typedef name is precded by ":":
                return ":" + type_decl_str
        elif kind == TypeKind.POINTER:
            # emit the type of pointer:
            pointee_type = type_obj.get_pointee()
            type_str = "(:pointer " + self._cursor_lisp_type_str(pointee_type) + ")"
            return type_str
        elif kind == TypeKind.ELABORATED:
            # Either a struct, union, or enum: (any type that looks like "struct foo", "enum foo", etc
            named_type = type_obj.get_named_type()
            named_type_kind = named_type.kind
            if named_type_kind == TypeKind.RECORD:
                type_decl = type_obj.get_declaration()
                mangled_name = self._mangle_string(type_decl.spelling, self.type_manglers)
                if type_decl.kind == CursorKind.UNION_DECL:
                    return "(:union " + mangled_name + ")"
                elif type_decl.kind == CursorKind.STRUCT_DECL:
                    return "(:struct " + mangled_name + ")"
                else:
                    raise Exception("Unknown cursorkind")
            elif named_type_kind == TypeKind.ENUM:
                return ":int ; " + self._mangle_string(named_type.spelling, self.type_manglers) + "\n"
        elif kind == TypeKind.INCOMPLETEARRAY:
            elem_type = type_obj.element_type
            return "(:pointer " + self._cursor_lisp_type_str(elem_type) + ") ; array \n"
        elif kind == TypeKind.CONSTANTARRAY:
            elem_type = type_obj.element_type
            num_elems = type_obj.element_count
            type_str = self._cursor_lisp_type_str(elem_type)
            return f"(:pointer {type_str}) ; array (size {num_elems})\n"
        elif kind == TypeKind.FUNCTIONPROTO:
            return f":pointer ; function ptr {type_obj.spelling}\n"
        elif kind == TypeKind.ENUM:
            return ":int ; " + self._mangle_string(type_obj.spelling, self.type_manglers) + "\n"

        raise Exception(f"Don't know how to handle type: {type_obj.spelling} {kind}")
        return type_obj.spelling

    def _process_macro_def(self, cursor):
        location = cursor.location
        spelling = self._mangle_string(cursor.spelling.lower(), self.constant_manglers)
        print(f"Found macro {spelling} definition in: {location.file}:{location.line}:{location.column}\n",
              file=sys.stderr)
        self.output.write("#| MACRO_DEFINITION\n")
        self.output.write(f"(defconstant {spelling} ACTUAL_VALUE_HERE)\n")
        self.output.write("|#\n\n")

    def _process_record(self, name, actual_type, cursor):
        output = ""
        if actual_type == self.ElaboratedType.UNION:
            output += f"(defcunion {name}"
        else:
            output += f"(defcstruct {name}"

        this_type = cursor.type

        for field in this_type.get_fields():
            field_name = self._mangle_string(field.spelling.lower(), self.name_manglers)
            if field.is_anonymous():
                assert(field.type.kind == clang.TypeKind.ELABORATED)
                inner_name = name + '-' + field_name
                actual_elaborated_type = self._determine_elaborated_type(field.type)
                if actual_elaborated_type == self.ElaboratedType.ENUM:
                    decl = field.type.get_declaration()
                    self._process_enum_as_constants(decl)
                    ret_val = ":int"
                elif actual_elaborated_type == self.ElaboratedType.UNION:
                    self._process_record(inner_name, actual_elaborated_type, field)
                    field_type =  "(:union " + name + '-' + field_name + ")"
                else:
                    # struct type
                    self._process_record(inner_name, actual_elaborated_type, field)
                    field_type = "(:struct " + name + '-' + field_name + ")"
            else:
                field_type = self._cursor_lisp_type_str(field.type)
            output += f"\n  ({field_name} {field_type})"
        output += ")\n\n"
        sys.stdout.write(output)

    def _process_struct_decl(self, cursor):
        name = cursor.spelling
        if name:
            mangled_name = self._mangle_string(name.lower(), self.type_manglers)
            self._process_record(mangled_name, self.ElaboratedType.STRUCT, cursor)
        else:
            self.skipped_record_decls[cursor.hash] = (self.ElaboratedType.STRUCT, cursor)

    def _process_union_decl(self, cursor):
        name = cursor.spelling.lower()
        if name:
            mangled_name = self.mangle_type(name, self.type_manglers)
            self._process_record(mangled_name, self.ElaboratedType.UNION, cursor)
        else:
            self.skipped_record_decls[cursor.hash] = (self.ElaboratedType.UNION, cursor)

    def _process_realized_enum(self, name, cursor):
        self.output.write(f"(defcenum {name}")
        for field in cursor.get_children():
            name = self._mangle_string(field.spelling.lower(), self.enum_manglers)

            self.output.write(f"\n  ({name} {field.enum_value})")
        self.output.write(")\n\n")

    def _process_enum_as_constants(self, cursor):
        for field in cursor.get_children():
            field_name = self._mangle_string(field.spelling.lower(), self.constant_manglers)
            self.output.write(f"(defconstant {field_name} {field.enum_value})\n")
        self.output.write("\n")

    def _process_enum_decl(self, cursor):
        name = cursor.spelling
        if name:
            name = self._mangle_string(name.lower(), self.type_manglers)
            self._process_realized_enum(name, cursor)
        else:
            self.skipped_enum_decls[cursor.hash] = cursor

    def _process_func_decl(self, cursor):
        name = cursor.spelling.lower()
        # mangle function names the same way as typenames:
        mangled_name = self._mangle_string(name, self.type_manglers)

        ret_type = cursor.result_type
        lisp_ret_type = self._cursor_lisp_type_str(ret_type)

        self.output.write("(defcfun ")
        if name != mangled_name:
            self.output.write(f'("{name}" {mangled_name})')
        else:
            self.output.write(f'"{name}"')
        self.output.write(f" {lisp_ret_type}")

        for arg in cursor.get_arguments():
            arg_name = arg.spelling.lower()
            arg_type_name = self._cursor_lisp_type_str(arg.type)
            arg_mangled_name = self._mangle_string(arg_name, self.name_manglers)

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
            base_type_str = self._cursor_lisp_type_str(underlying_type)
        mangled_name = self._mangle_string(cursor.spelling.lower(),
                                                         self.typedef_manglers)
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
        clang.CursorKind.MACRO_DEFINITION    : _process_macro_def,
        clang.CursorKind.STRUCT_DECL         : _process_struct_decl,
        clang.CursorKind.ENUM_DECL           : _process_enum_decl,
        clang.CursorKind.FUNCTION_DECL       : _process_func_decl,
        clang.CursorKind.TYPEDEF_DECL        : _process_typedef_decl,
        clang.CursorKind.UNION_DECL          : _process_union_decl,
        clang.CursorKind.VAR_DECL            : _process_var_decl,
        clang.CursorKind.INCLUSION_DIRECTIVE : _no_op,
        clang.CursorKind.MACRO_INSTANTIATION : _no_op,
    }

    def process_file(self,filepath, args=[]):
        if not os.path.isfile(filepath):
            print(f"Error: file doesn't exist: {filepath}", file=sys.stderr)
            return 1

        print(f"Processing file: {filepath}", file=sys.stderr)
        print(f"Arguments to clang: {args}", file=sys.stderr)

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
            if type == self.ElaboratedType.STRUCT:
                sys.stderr.write("WARNING: Skipping unamed struct decl at ")
                sys.stderr.write(f"{location.file}:{location.line}:{location.column}\n")
            else:
                sys.stderr.write("WARNING: Skipping unamed union decl at ")
                sys.stderr.write(f"{location.file}:{location.line}:{location.column}\n")
