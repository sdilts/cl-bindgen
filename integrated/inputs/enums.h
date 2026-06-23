enum test_enum {
  TEST_ENUM_ONE,
  TEST_ENUM_TWO,
  TEST_ENUM_FIVE = 5,
};

enum typed_enum : short {
	TYPED_ENUM_TEST
};

struct outer {
  enum typed_enum typed;
  enum : short {
	  OUTER_INNER_TEN = 10,
    OUTER_INNER_OTHER
  } inner_enum;
};
