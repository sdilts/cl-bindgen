;; next section imported from file inputs/enums.h

(cffi:defcenum test-enum
  (:test-enum-one 0)
  (:test-enum-two 1)
  (:test-enum-five 5))

(cffi:defcenum anon-enum-0
  (+annon-enum-constant+ 20))

(cffi:defcenum (typed-enum :short)
  (:typed-enum-test 0))

(cffi:defcenum outer-inner-enum
  (+outer-inner-ten+ 10)
  (+outer-inner-other+ 11))

(cffi:defcstruct outer
  (test-enum test-enum)
  (typed :short #| typed-enum |#)
  (inner-enum outer-inner-enum))

(cffi:defcenum typedef-enum
  (:typedef-enum-val 0))

(cffi:defctype typedef-enum typedef-enum)

(cffi:defcenum inner-typedef-enum
  (:inner-typedef-val 0))

(cffi:defctype inner-typedef inner-typedef-enum)
