;; next section imported from file inputs/typedef.h

(cffi:defcstruct foo
  (a :int))

(cffi:defctype foo-type (:struct foo))

(cffi:defcfun ("do_someting" do-someting) :void
  (p foo-type))

(cffi:defctype function-thing :void #| int (const void *, int) |#)

(cffi:defcfun ("function_with_thing" function-with-thing) :int
  (fn (:pointer function-thing)))
