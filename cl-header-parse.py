import sys
import os.path
from typing import NamedTuple

import clang.cindex as clang

from mangler import UnderscoreMangler
import typetransformer

# name managler interface:
# can_mangle(string): returns true if the entity knows how to mangle the string
# mangle(string): returns the mangled string

class FileProcessor:

    def __init__(self, output, enum_manglers=[], type_manglers=[], name_manglers=[]):
        self.output = output
        self.enum_manglers = enum_manglers
        # self.type_manglers = type_manglers
        self.name_manglers = name_manglers

        self.type_processor = typetransformer.TypeTransformer(type_manglers)

    @staticmethod
    def _mangle_thing(thing, manglers):
        for mangler in manglers:
            if mangler.can_mangle(thing):
                thing = mangler.mangle(thing)
        return thing

    def _process_macro_def(self, cursor):
        location = cursor.location
        spelling = cursor.spelling
        print(f"Found macro {spelling} definition in: {location.file}:{location.line}:{location.column}\n",
              file=sys.stderr)
        self.output.write("#| MACRO_DEFINITION\n")
        self.output.write(f"(defconstant +{spelling}+ ACTUAL_VALUE_HERE)\n")
        self.output.write("#|\n\n")

    def _process_struct_decl(self, cursor):
        print("Processing struct decl\n", file=sys.stderr)

    def _process_enum(self, name, cursor):
        self.output.write(f"(defcenum {name}")
        for field in cursor.get_children():
            name = self._mangle_thing(field.spelling, self.enum_manglers)

            self.output.write(f"\n  ({name} {field.enum_value})")
        self.output.write(")\n\n")

    def _process_enum_decl(self, cursor):
        print("Enum is anonymous:", cursor.is_anonymous())
        name = cursor.spelling
        if name:
            name = self.type_processor.mangle_type(name)
        else:
            location = cursor.location
            print(f"WARNING: Name not given for enum at {location.file}:{location.line}:{location.column}\n")
        self._process_enum(name, cursor)

    def _process_func_decl(self, cursor):
        name = cursor.spelling
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
            arg_name = arg.spelling
            arg_type_name = self.type_processor.cursor_lisp_type_str(arg.type)

            if arg_name == None:
                arg_name = "unknown"

            self.output.write(f"\n  ({arg_name} {arg_type_name})")

        self.output.write(")\n\n")

    def _process_typedef_decl(self, cursor):
        print("Processing typedef decl\n", file=sys.stderr)

    def _unrecognized_cursorkind(self, cursor):
        print(f"Don't recognize cursor:", file=sys.stderr)
        print("Source location", cursor.location.file, file=sys.stderr)
        print("Kind:", cursor.kind, file=sys.stderr)
        print("Spelling:", cursor.spelling, file=sys.stderr)

    visit_table = {
        clang.CursorKind.MACRO_DEFINITION : _process_macro_def,
        clang.CursorKind.STRUCT_DECL : _process_struct_decl,
        clang.CursorKind.ENUM_DECL : _process_enum_decl,
        clang.CursorKind.FUNCTION_DECL : _process_func_decl,
        clang.CursorKind.TYPEDEF_DECL : _process_typedef_decl
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
                if not handler_func:
                    self._unrecognized_cursorkind(child)
                else:
                    handler_func(self, child)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(f"Not enough arguments: {len(sys.argv)} given", file=sys.stderr)
        exit(1)

    u_managler = UnderscoreMangler()
    enum_manglers = [u_managler]
    type_managlers = [u_managler]
    name_managlers = [u_managler]
    processor = FileProcessor(sys.stdout,
                              enum_manglers=enum_manglers,
                              type_manglers=type_managlers,
                              name_manglers=name_managlers)

    processor.process_file(sys.argv[1], args=sys.argv[2:1])
