;; next section imported from file inputs/nested_anonymous_records.h

(cffi:defcunion nested-union-anon-0
  (a :int)
  (b :int))

(cffi:defcstruct nested-union
  (flag :short)
  (anon-0 (:union nested-union-anon-0)))

(cffi:defcunion nested-struct-anon-0
  (a :short)
  (b :short))

(cffi:defcstruct nested-struct
  (anon-0 (:struct nested-struct-anon-0))
  (c :char))
