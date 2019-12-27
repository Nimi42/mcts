#include "generic-dict.h"

unsigned int FUNC_POSTFIX(hash)(KEY_TYPE *key, int size) {
	int hash = 0;
	int c;

	while((c = *key++)) {
		hash = ((hash << 5) + hash) + c;
	}

	hash %= size;
	return hash;
}
