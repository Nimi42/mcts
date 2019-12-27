#include "str-node-dict.h"

char * print_items_str_node(struct Bucket *bucket) {
    int size;
    char * key, * val;

    key = bucket->key;

    PyObject *repr = PyObject_Str(bucket->value->state);
    val = (char *) PyUnicode_AsUTF8(repr);

    size = 11 + strlen(key) + strlen(val) + 1;

    char *bucket_as_str = malloc((size + 1) * sizeof(char));
    sprintf(bucket_as_str, "key: %s\n%s", key, val);
    
    return bucket_as_str;
}