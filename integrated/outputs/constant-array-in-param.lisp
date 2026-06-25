;; next section imported from file inputs/constant_array_in_param.h

(cffi:defcfun "test" :void
  (args :pointer #| :float :count 4 |#)
  (ints :pointer #| :int :count 10 |#))
