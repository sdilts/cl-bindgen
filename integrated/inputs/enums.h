enum test_enum {
  TEST_ENUM_ONE,
  TEST_ENUM_TWO,
  TEST_ENUM_FIVE = 5,
};

enum {
  ANNON_ENUM_CONSTANT = 20
};

enum typed_enum : short {
  TYPED_ENUM_TEST
};

struct outer {
  enum test_enum test_enum;
  enum typed_enum typed;
  enum {
    OUTER_INNER_TEN = 10,
    OUTER_INNER_OTHER
  } inner_enum;
};

typedef enum { TYPEDEF_ENUM_VAL } typedef_enum;

typedef enum inner_typedef_enum {
	INNER_TYPEDEF_VAL
} inner_typedef;
