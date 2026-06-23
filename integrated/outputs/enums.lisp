;; next section imported from file inputs/enums.h

(cffi:defcenum test-enum
  (:test-enum-one 0)
  (:test-enum-two 1)
  (:test-enum-five 5))

(cffi:defcenum typed-enum
  (:typed-enum-test 0))

(defconstant +outer-inner-ten+ 10)
(defconstant +outer-inner-other+ 11)

(cffi:defcstruct outer
  (typed :short #| typed-enum |#)
  (inner-enum :short #| enum (unnamed at inputs/enums.h:13:3) |#))
