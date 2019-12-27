#ifndef GENERIC_DICT_H
#define GENERIC_DICT_H

#ifndef KEY_TYPE
#define KEY_TYPE char
#endif

#ifndef VALUE_TYPE
#define VALUE_TYPE void
#endif

#ifndef FUNC_POSTFIX
#define FUNC_POSTFIX(NAME) NAME
#endif

#include <stdlib.h>
#include <stdio.h>
#include <string.h>

struct Bucket 
{
	KEY_TYPE *key;
	VALUE_TYPE *value;
	struct Bucket *next;
};

struct Dict
{
	unsigned int size;
	struct Bucket **items;
};

// Access dictionary
int FUNC_POSTFIX(dict_put)(struct Dict *dict, KEY_TYPE *key, VALUE_TYPE *value);
VALUE_TYPE * FUNC_POSTFIX(dict_get)(struct Dict *dict, KEY_TYPE *key);

// Dictionary creation and destruction
struct Dict * FUNC_POSTFIX(dict_create)(unsigned int size);
void FUNC_POSTFIX(dict_destroy)(struct Dict *hashtable);

// Type specific free methods for non primitive values
void FUNC_POSTFIX(free_key)(KEY_TYPE *key);
void FUNC_POSTFIX(free_value)(VALUE_TYPE *value);

// Hash function
unsigned int FUNC_POSTFIX(hash)(KEY_TYPE *key, int size);

// Print the dictionary
int FUNC_POSTFIX(dict_print)(struct Dict *dict);
char * FUNC_POSTFIX(print_items)(struct Bucket *bucket);


#endif // GENERIC_DICT_H
