#include "str-node-dict.h"

void FUNC_POSTFIX(free_key)(KEY_TYPE *key) {
    free(key);
}

void FUNC_POSTFIX(free_value)(VALUE_TYPE *value) {
    Py_DECREF(value->state);
	FUNC_POSTFIX(dict_destroy)(value->children);
	free(value);
}