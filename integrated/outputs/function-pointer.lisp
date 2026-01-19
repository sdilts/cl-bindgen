;; next section imported from file inputs/function_pointer.h

(cffi:defcstruct a
  (foo :pointer #| function ptr void () |#)
  (boo :pointer #| function ptr void (int) |#))
