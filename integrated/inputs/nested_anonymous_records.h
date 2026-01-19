struct nested_union {
    short flag;
	union {
		int a;
		int b;
	};
};

struct nested_struct {
	struct {
		short a;
		short b;
	};
	char c;
};
