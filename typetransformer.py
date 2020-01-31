import clang.cindex as clang
from clang.cindex import TypeKind, CursorKind

class TypeTransformer:

    # This table contains types that don't have to be inferred or otherwise
    # built based off of the cursor type
    builtin_table = {
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

    known_typedefs = {
        "uint64_t" : ":uint64",
        "uint32_t" : ":uint32",
        "uint16_t" : ":uint16",
        "uint8_t"  : ":uint8",
        "int64_t" : ":int64",
        "int32_t" : ":int32",
        "int16_t" : ":int16",
        "int8_t"  : ":int8",
    }

    def __init__(self):
        pass

    def cursor_lisp_type_str(self, type_obj):
        assert(type(type_obj) == clang.Type)
        kind = type_obj.kind
        known_type = self.builtin_table.get(kind)
        if known_type:
            return known_type
        elif kind == TypeKind.TYPEDEF:
            type_decl = type_obj.get_declaration()
            # try the known typedefs:
            type_decl_str = type_decl.type.spelling
            known_type = self.known_typedefs.get(type_decl_str)
            if known_type:
                return known_type
            else:
                # assume that the typedef name is precded by ":":
                return ":" + type_decl_str

        elif kind == TypeKind.POINTER:
            # emit the type of pointer:
            pointee_type = type_obj.get_pointee()
            type_str = "(:pointer " + self.cursor_lisp_type_str(pointee_type) + ")"
            return type_str

        elif kind == TypeKind.ELABORATED:
            # Either a struct, union, or enum: (any type that looks like "struct foo", "enum foo", etc.
            named_type = type_obj.get_named_type()
            named_type_kind = named_type.kind
            if named_type_kind == TypeKind.RECORD:
                type_decl = type_obj.get_declaration()
                if type_decl.kind == CursorKind.UNION_DECL:
                    return "(:union " + type_decl.spelling + ")"
                elif type_decl.kind == CursorKind.STRUCT_DECL:
                    return "(:struct " + type_decl.spelling + ")"
                else:
                    raise Exception("Unknown cursorkind")
            elif named_type_kind == TypeKind.ENUM:
                return ":int ; " + named_type.spelling + "\n"

        elif kind == TypeKind.INCOMPLETEARRAY:
            elem_type = type_obj.element_type
            return "(:pointer " + self.cursor_lisp_type_str(elem_type) + ") ; array \n"
        elif kind == TypeKind.CONSTANTARRAY:
            elem_type = type_obj.element_type
            num_elems = type_obj.element_count
            type_str = self.cursor_lisp_type_str(elem_type)
            return f"(:pointer {type_str}) ; array (size {num_elems})\n"

        raise Exception(f"Don't know how to handle type: {type_obj.spelling}")
        return type_obj.spelling
