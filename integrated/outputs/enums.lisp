;; next section imported from file inputs/enums.h

(cffi:defcenum test-enum
  (:test-enum-one 0)
  (:test-enum-two 1)
  (:test-enum-five 5))

(cffi:defcenum (typed-enum :short)
  (:typed-enum-test 0))

(defconstant +outer-inner-ten+ 10)
(defconstant +outer-inner-other+ 11)

(cffi:defcstruct outer
  (test-enum test-enum)
  (typed :short #| typed-enum |#)
  (inner-enum :short #| enum (unnamed at inputs/enums.h:14:3) |#))
