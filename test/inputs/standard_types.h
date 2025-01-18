#include <stdint.h>
#include <stddef.h>
#include <sys/types.h>

int8_t std_int_fn(int16_t foo, int32_t bar, int64_t baz);

uint8_t uint_fn(uint16_t foo, uint32_t bar, uint64_t baz);

size_t standard_sizes(uintptr_t uint_pointer, intptr_t int_ptr,
                      ssize_t unsigned_size, ptrdiff_t pointer_diff);
