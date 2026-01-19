;; next section imported from file inputs/standard_types.h

(cffi:defcfun ("std_int_fn" std-int-fn) :int8
  "A function with a bunch of standard types"
  (foo :int16)
  (bar :int32)
  (baz :int64))

(cffi:defcfun ("uint_fn" uint-fn) :uint8
  (foo :uint16)
  (bar :uint32)
  (baz :uint64))

(cffi:defcfun ("standard_sizes" standard-sizes) :size
  (uint-pointer :uintptr)
  (int-ptr :intptr)
  (unsigned-size :ssize)
  (pointer-diff :ptrdiff))
