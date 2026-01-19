;; next section imported from file inputs/capitalization.h

(cffi:defcstruct foo
  (a-bear :int)
  (b :int))

(cffi:defcfun ("camelCaseFunctionName" camel-case-function-name) :int
  (test :int))

(cffi:defcfun ("TitleCaseFunction" title-case-function) :int
  (test-foo :int))

(cffi:defcfun ("stringDNE" string-dne) :int)

(cffi:defcfun ("IString" istring) :void)

(cffi:defcfun ("snake_case_function" snake-case-function) :int
  (weird-name :double))

(cffi:defcfun ("SDL_testThing" sdl-test-thing) :int)
