;; next section imported from file inputs/forward_declaration.h

(cffi:defcstruct foo)

(cffi:defcunion bar)

(cffi:defcunion bar
  (a (:pointer (:struct foo)))
  (b :int))

(cffi:defcstruct foo
  (b (:pointer (:union bar))))
