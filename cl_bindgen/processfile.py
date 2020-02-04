import sys
import os.path
import errno
import copy
from enum import Enum
from dataclasses import dataclass, field
from collections import namedtuple

import clang.cindex as clang
from clang.cindex import TypeKind, CursorKind

@dataclass
class ProcessOptions:
    typedef_manglers: list = field(default_factory=lambda: [])
    enum_manglers: list = field(default_factory=lambda: [])
    type_manglers: list = field(default_factory=lambda: [])
    name_manglers: list = field(default_factory=lambda: [])
    constant_manglers: list = field(default_factory=lambda: [])

    output: str = field(default_factory=lambda: ":stdout")
    package : str = None
    arguments: list = field(default_factory=lambda: [])

    def __copy__(self, memo=None):
        return ProcessOptions(list(self.typedef_manglers),
                              list(self.enum_manglers),
                              list(self.type_manglers),
                              list(self.name_manglers),
                              list(self.constant_manglers),
                              output=self.output,
                              package=copy.copy(self.package),
                              arguments=copy.copy(self.arguments))

    @staticmethod
    def output_file_from_option(option, open_args):
        """ Open the file specified by `option` """
        if option.output == ":stdout":
            return sys.stdout
        elif option.output == ":stderr":
            return sys.stderr
        else:
            # TODO: try to do something intellegent here to avoid/warn when overwriting files?
            try:
                return open(option.output, open_args)
            except IsADirectoryError as err:
                print(f"Error: Specified output file {err.filename} is a directory",
                      file=sys.stderr)
                exit(err.errno)

_ParseData = namedtuple('ParseData', ['skipped_enums', 'skipped_records'])

class ElaboratedType(Enum):
    UNION  = 0
    STRUCT = 1
    ENUM   = 2

def _mangle_string(thing, manglers):
    for mangler in manglers:
        if mangler.can_mangle(thing):
            thing = mangler.mangle(thing)
    return thing

def _determine_elaborated_type(type_obj):
    named_type = type_obj.get_named_type()
    named_type_kind = named_type.kind
    if named_type_kind == TypeKind.RECORD:
        type_decl = type_obj.get_declaration()
        if type_decl.kind == CursorKind.UNION_DECL:
            return ElaboratedType.UNION
        elif type_decl.kind == CursorKind.STRUCT_DECL:
            return ElaboratedType.STRUCT
        else:
            raise Exception(f"Unknown cursorkind: {type_decl.kind}")
    elif named_type_kind == TypeKind.ENUM:
        return ElaboratedType.ENUM

def _cursor_lisp_type_str(type_obj, options):
    assert(type(type_obj) == clang.Type)
    kind = type_obj.kind
    known_type = _cursor_lisp_type_str._builtin_table.get(kind)
    if known_type:
        return known_type
    elif kind == TypeKind.TYPEDEF:
        type_decl = type_obj.get_declaration()
        # try the known typedefs:
        type_decl_str = type_decl.type.spelling
        known_type = _cursor_lisp_type_str._known_typedefs.get(type_decl_str)
        if known_type:
            return known_type
        else:
            # assume that the typedef name is precded by ":":
            return ":" + type_decl_str
    elif kind == TypeKind.POINTER:
        # emit the type of pointer:
        pointee_type = type_obj.get_pointee()
        type_str = "(:pointer " + _cursor_lisp_type_str(pointee_type, options) + ")"
        return type_str
    elif kind == TypeKind.ELABORATED:
        # Either a struct, union, or enum: (any type that looks like "struct foo", "enum foo", etc
        named_type = type_obj.get_named_type()
        named_type_kind = named_type.kind
        if named_type_kind == TypeKind.RECORD:
            type_decl = type_obj.get_declaration()
            mangled_name = _mangle_string(type_decl.spelling, options.type_manglers)
            if type_decl.kind == CursorKind.UNION_DECL:
                return "(:union " + mangled_name + ")"
            elif type_decl.kind == CursorKind.STRUCT_DECL:
                return "(:struct " + mangled_name + ")"
            else:
                raise Exception("Unknown cursorkind")
        elif named_type_kind == TypeKind.ENUM:
            return ":int ; " + _mangle_string(named_type.spelling, options.type_manglers) + "\n"
    elif kind == TypeKind.INCOMPLETEARRAY:
        elem_type = type_obj.element_type
        return "(:pointer " + _cursor_lisp_type_str(elem_type, options) + ") ; array \n"
    elif kind == TypeKind.CONSTANTARRAY:
        elem_type = type_obj.element_type
        num_elems = type_obj.element_count
        type_str = _cursor_lisp_type_str(elem_type, options)
        return f"(:pointer {type_str}) ; array (size {num_elems})\n"
    elif kind == TypeKind.FUNCTIONPROTO:
        return f":pointer ; function ptr {type_obj.spelling}\n"
    elif kind == TypeKind.ENUM:
        return ":int ; " + _mangle_string(type_obj.spelling, options.type_manglers) + "\n"

    raise Exception(f"Don't know how to handle type: {type_obj.spelling} {kind}")

# This table contains types that don't have to be inferred or otherwise
# built based off of the cursor type
_cursor_lisp_type_str._builtin_table = {
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
_cursor_lisp_type_str._known_typedefs = {
    "uint64_t" : ":uint64",
    "uint32_t" : ":uint32",
    "uint16_t" : ":uint16",
    "uint8_t"  : ":uint8",
    "int64_t" : ":int64",
    "int32_t" : ":int32",
    "int16_t" : ":int16",
    "int8_t"  : ":int8",
}

def _process_macro_def(cursor, data, output, options):
    location = cursor.location
    spelling = _mangle_string(cursor.spelling.lower(), options.constant_manglers)
    print(f"Found macro {spelling} definition in: {location.file}:{location.line}:{location.column}\n",
          file=sys.stderr)
    output.write("#| MACRO_DEFINITION\n")
    output.write(f"(defconstant {spelling} ACTUAL_VALUE_HERE)\n")
    output.write("|#\n\n")

def _process_record(name, actual_type, cursor, output, options):
    output_str = ""
    if actual_type == ElaboratedType.UNION:
        output_str += f"(defcunion {name}"
    else:
        output_str += f"(defcstruct {name}"

    this_type = cursor.type

    for field in this_type.get_fields():
        field_name = _mangle_string(field.spelling.lower(), options.name_manglers)
        if field.is_anonymous():
            assert(field.type.kind == clang.TypeKind.ELABORATED)
            inner_name = name + '-' + field_name
            actual_elaborated_type = _determine_elaborated_type(field.type)
            if actual_elaborated_type == ElaboratedType.ENUM:
                decl = field.type.get_declaration()
                _process_enum_as_constants(decl, output, options)
                field_type = ":int"
            elif actual_elaborated_type == ElaboratedType.UNION:
                _process_record(inner_name, actual_elaborated_type, field, output, options)
                field_type =  "(:union " + name + '-' + field_name + ")"
            else:
                # struct type
                _process_record(inner_name, actual_elaborated_type, field, output, options)
                field_type = "(:struct " + name + '-' + field_name + ")"
        else:
            field_type = _cursor_lisp_type_str(field.type, options)
        output_str += f"\n  ({field_name} {field_type})"
    output_str += ")\n\n"
    output.write(output_str)

def _process_struct_decl(cursor, data, output, options):
    name = cursor.spelling
    if name:
        mangled_name = _mangle_string(name.lower(), options.type_manglers)
        _process_record(mangled_name, ElaboratedType.STRUCT, cursor, output, options)
    else:
        data.skipped_records[cursor.hash] = (ElaboratedType.STRUCT, cursor)

def _process_union_decl(cursor, data, output, options):
    name = cursor.spelling
    if name:
        mangled_name = _mangle_string(name.lower(), options.type_manglers)
        _process_record(mangled_name, ElaboratedType.UNION, cursor, output, options)
    else:
        data.skipped_records[cursor.hash] = (ElaboratedType.UNION, cursor)

def _process_realized_enum(name, cursor, output, options):
    output.write(f"(defcenum {name}")
    for field in cursor.get_children():
        name = _mangle_string(field.spelling.lower(), options.enum_manglers)

        output.write(f"\n  ({name} {field.enum_value})")
    output.write(")\n\n")

def _process_enum_as_constants(cursor, output, options):
    for field in cursor.get_children():
        field_name = _mangle_string(field.spelling.lower(), options.constant_manglers)
        output.write(f"(defconstant {field_name} {field.enum_value})\n")
    output.write("\n")

def _process_enum_decl(cursor, data, output, options):
    name = cursor.spelling
    if name:
        name = _mangle_string(name.lower(), options.type_manglers)
        _process_realized_enum(name, cursor, output, options)
    else:
        data.skipped_enums[cursor.hash] = cursor

def _process_func_decl(cursor, data, output, options):
    name = cursor.spelling.lower()
    # mangle function names the same way as typenames:
    mangled_name = _mangle_string(name, options.type_manglers)

    ret_type = cursor.result_type
    lisp_ret_type = _cursor_lisp_type_str(ret_type, options)

    output.write("(defcfun ")
    if name != mangled_name:
        output.write(f'("{name}" {mangled_name})')
    else:
        output.write(f'"{name}"')
    output.write(f" {lisp_ret_type}")

    for arg in cursor.get_arguments():
        arg_name = arg.spelling.lower()
        arg_type_name = _cursor_lisp_type_str(arg.type, options)
        arg_mangled_name = _mangle_string(arg_name, options.name_manglers)

        if arg_name == None:
            arg_name = "unknown"

        output.write(f"\n  ({arg_mangled_name} {arg_type_name})")

    output.write(")\n\n")

def _process_typedef_decl(cursor, data, output, options):
    name = cursor.spelling.lower()
    underlying_type = cursor.underlying_typedef_type
    base_decl = underlying_type.get_declaration()
    base_decl_hash = base_decl.hash
    base_type_str = None
    # Ensure that the type we are typdefing wasn't skipped:
    if base_decl_hash in data.skipped_enums:
        del data.skipped_enums[base_decl_hash]
        base_type_str = name.replace('_', '-') + "-enum"
        _process_realized_enum(base_type_str, base_decl, output, options)
    else:
        decl_type = data.skipped_records.get(base_decl_hash)
        if decl_type:
            del data.skipped_records[base_decl_hash]
            base_type_str = name.replace('_', '-') + "-record"
            _process_record(base_type_str, decl_type[0], base_decl, output, options)

    if not base_type_str:
        base_type_str = _cursor_lisp_type_str(underlying_type, options)
    mangled_name = _mangle_string(cursor.spelling.lower(),
                                                     options.typedef_manglers)
    output.write(f"(defctype {mangled_name} {base_type_str})\n\n")

def _no_op(cursor, data, output, options):
    pass

def _process_var_decl(cursor, data, output, options):
    location = cursor.location
    var_name = cursor.spelling
    print(f"WARNING: Not processing var decl {var_name} at {location.file}:{location.line}:{location.column}\n",
          file=sys.stderr)

def _unrecognized_cursorkind(cursor):
    location = cursor.location
    print(f"WARNING: Not processing {cursor.kind} {location.file}:{location.line}:{location.column}\n",
          file=sys.stderr)

def process_file(filepath, options):
    if os.path.isdir(filepath):
        raise IsADirectoryError(errno.EISDIR, filepath)
    elif not os.path.isfile(filepath):
        raise FileNotFoundError(errno.ENOENT, filepath)

    output = ProcessOptions.output_file_from_option(options, 'w')

    index = clang.Index.create()
    tu = index.parse(filepath, args=options.arguments,
                     options=clang.TranslationUnit.PARSE_DETAILED_PROCESSING_RECORD|clang.TranslationUnit.PARSE_SKIP_FUNCTION_BODIES)

    root_cursor = tu.cursor

    data = _ParseData(dict(), dict())

    if options.package:
        output.write(f'(cl:in-package #:{options.package})\n\n')

    for child in root_cursor.get_children():
        location = child.location
        if location.file and location.file.name == filepath:
            handler_func = process_file._visit_table.get(child.kind)
            if handler_func:
                handler_func(child, data, output, options)
            else:
                _unrecognized_cursorkind(child)

    # Once the file has been processed, if there are unused enums, output them as constants:
    for cursor in data.skipped_enums.values():
        _process_enum_as_constants(cursor, output, options)
    # issue warnings for anonymus structs:
    for (type, cursor) in data.skipped_records.values():
        if type == ElaboratedType.STRUCT:
            sys.stderr.write("WARNING: Skipped unamed struct decl at ")
            sys.stderr.write(f"{location.file}:{location.line}:{location.column}\n")
        else:
            sys.stderr.write("WARNING: Skipped unamed union decl at ")
            sys.stderr.write(f"{location.file}:{location.line}:{location.column}\n")
process_file._visit_table = {
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
