#ifndef STRING_NODE_DICT_H
#define STRING_NODE_DICT_H

/**
 * str-py-dict.h
 *   Dict from string to py.
 */

#undef VALUE_TYPE
#undef FUNC_POSTFIX

#define VALUE_TYPE struct Node
#define FUNC_POSTFIX(NAME) NAME ## _str_node

#include "generic-dict.h"

#endif // STRING_PY_DICT_H