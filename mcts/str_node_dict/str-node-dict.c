/**
 * str-py-dict.c
 *   Dict from string to int.
 */

// Header file with Macro definitions for String to Py
#include "mcts.h"

// Generic Dictionary functions
#include "generic/generic-create.gnrc"
#include "generic/generic-destroy.gnrc"
#include "generic/generic-put.gnrc"
#include "generic/generic-get.gnrc"
#include "generic/generic-print.gnrc"

// Type specific functions
#include "typed/str-node-free.c"
#include "typed/str-hash.c"
#include "typed/str-node-print.c"
