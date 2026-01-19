;; next section imported from file inputs/builtin_pointers.h

(cffi:defcstruct t
  (d (:pointer :double))
  (f (:pointer :float))
  (a (:pointer :int))
  (b (:pointer :long))
  (ld (:pointer :long-double))
  (ll (:pointer :long-long))
  (s :short)
  (ui (:pointer :unsigned-int))
  (ul (:pointer :unsigned-long))
  (ull (:pointer :unsigned-long-long))
  (us (:pointer :unsigned-short))
  (v (:pointer :void))
  (c (:pointer :char))
  (uc (:pointer :unsigned-char))
  (sc (:pointer :signed-char)))
