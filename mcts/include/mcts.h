#ifndef MCTS_C_BACKEND_H
#define MCTS_C_BACKEND_H

#include <Python.h>
#include <stdbool.h>
#include <float.h>

#ifdef DEBUG
#include "multiline.h"
#endif

struct Node {
    PyObject *state;
    struct Node *parent;
    struct Dict *children;
    int total_reward, num_visits;
    bool is_terminal, is_explored;
};

#include "str-node-dict.h"

#endif // MCTS_C_BACKEND_H