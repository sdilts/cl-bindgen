struct foo;

union bar;

union bar {
	struct foo *a;
	int b;
};

struct foo {
	union bar *b;
};
