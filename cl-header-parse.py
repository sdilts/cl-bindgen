import sys
import os.path
from typing import NamedTuple

import clang.cindex as clang

import mangler
import typetransformer

# name managler interface:
# can_mangle(string): returns true if the entity knows how to mangle the string
# mangle(string): returns the mangled string

class Transformers(NamedTuple):
    manglers : list
    type_processor : typetransformer.TypeTransformer


def process_macro_def(cursor, transformers, output):
    print("Processing macro definition\n", file=sys.stderr)

def process_struct_decl(cursor, transformers, output):
    print("Processing struct decl\n", file=sys.stderr)

def process_enum_decl(cursor, transformers, output):
    print("Processing enum decl\n", file=sys.stderr)

def process_func_decl(cursor, transformers, output):
    print("Processing function decl\n", file=sys.stderr)
    name = cursor.spelling
    mangled_name = name
    for mangler in transformers.manglers:
        if mangler.can_mangle(name):
            name = mangler.mangle(name)

    ret_type = cursor.result_type
    lisp_ret_type = transformers.type_processor.cursor_lisp_type_str(ret_type)

    output.write("(defcfun ")
    if name != mangled_name:
        output.write(f'("{name}" {mangled_name})')
    else:
        output.write(f'"{name}"')

    output.write(f" {lisp_ret_type}")

    for arg in cursor.get_arguments():
        arg_name = arg.spelling

        arg_type_name = transformers.type_processor.cursor_lisp_type_str(arg.type)

        if arg_name == None:
            arg_name = "unknown"

        output.write(f"\n  ({arg_name} {arg_type_name})")

    output.write(")\n\n")

def process_typedef_decl(cursor, transformers, output):
    print("Processing typedef decl\n", file=sys.stderr)

def unrecognized_cursorkind(cursor, transformers, output):
    print(f"Don't recognize cursor:", file=sys.stderr)
    print("Source location", cursor.location.file, file=sys.stderr)
    print("Kind:", cursor.kind, file=sys.stderr)
    print("Spelling:", cursor.spelling, file=sys.stderr)

def process_file(filepath, transformers, args=[], output=sys.stdout):
    print(f"Processing file: {filepath}", file=sys.stderr)
    print(f"Arguments to clang: {args}", file=sys.stderr)

    if not os.path.isfile(filepath):
        print(f"Error: file doesn't exist: {filepath}", file=sys.stderr)
        exit(1)

    index = clang.Index.create()
    tu = index.parse(filepath, args=args,
                     options=clang.TranslationUnit.PARSE_DETAILED_PROCESSING_RECORD)

    root_cursor = tu.cursor

    for child in root_cursor.get_children():
        location = child.location
        if location.file and location.file.name == filepath:
            handler_func = process_file.visit_table.get(child.kind, unrecognized_cursorkind)
            handler_func(child, transformers, output)

process_file.visit_table = {
    clang.CursorKind.MACRO_DEFINITION : process_macro_def,
    clang.CursorKind.STRUCT_DECL : process_struct_decl,
    clang.CursorKind.ENUM_DECL : process_enum_decl,
    clang.CursorKind.FUNCTION_DECL : process_func_decl,
    clang.CursorKind.TYPEDEF_DECL : process_typedef_decl
}


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(f"Not enough arguments: {len(sys.argv)} given", file=sys.stderr)
        exit(1)

    processors = Transformers(manglers=[], type_processor=typetransformer.TypeTransformer())

    process_file(sys.argv[1], processors, args=sys.argv[2:1])
