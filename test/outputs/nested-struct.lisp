;; next section imported from file inputs/nested_struct.h

(cffi:defcstruct a-b
  (a :int)
  (b :int))

(cffi:defcstruct a
  (b (:struct a-b))
  (c :int))
