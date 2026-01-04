typedef struct foo {
	int a;
} foo_type;

void do_someting(foo_type p);

typedef int FunctionThing(const void *thing, int data);

int function_with_thing(FunctionThing *fn);
