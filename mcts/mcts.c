#include "mcts.h"


/**
 * String constants to access python methods. The state object has to define these methods.
 */
static PyObject *get_proposed_action;
static PyObject *get_unexplored_actions;
static PyObject *take_action;
static PyObject *is_terminal;
static PyObject *get_reward;

/**
 * Global variable to set dictionary size
 */
static unsigned int num_children;

/**
 * Declaration of internal methods
 */
static struct Node * new_node(PyObject *state, struct Node *parent);
static struct Bucket * get_next_best_state(struct Node *node, double exploration_value);
static void backpropogate(struct Node *node, int reward);
static int rollout(PyObject *state);
static struct Node * selection(struct Node *node);
static void execute(struct Node *root);


static struct Node * new_node(PyObject *state, struct Node *parent) {
    // Call is terminal on state to initialize the node
    PyObject *terminal = PyObject_CallMethodObjArgs(state, is_terminal, NULL);

    #ifdef NULL_CHECKS
    if (!terminal || terminal == Py_None) {
        printf("ERROR:  Result from is_terminal is either NULL or None.\n");
        return NULL;
    }
    #endif

    // Create the node
    struct Node *node = malloc(sizeof(*node));
    node->state=state;
    node->parent=parent;
    node->is_terminal = Py_True == terminal;
    node->is_explored = node->is_terminal;
    node->num_visits = 0;
    node->total_reward = 0;
    node->children = dict_create_str_node(num_children);

    Py_DECREF(terminal);

    return node;
}

static struct Bucket * get_next_best_state(struct Node *parent, double exploration_value) {
    double best_value = -DBL_MAX;
    struct Bucket *best_node = NULL;

    struct Dict *dict = parent->children;
    struct Bucket *item;
    struct Node *child;
    for (unsigned int i = 0; i < dict->size; ++i) {

        // ToDo: Dictionary iterate items
        item = dict->items[i];

        if (item != NULL) {
            child = item->value;
            double node_value = (child->total_reward / (double) child->num_visits) +
                (exploration_value * sqrt(2 * log(parent->num_visits) / (double) child->num_visits));

            if (node_value > best_value) {
                best_value = node_value;
                best_node = item;
            }
        }
    }

    return best_node;
}

static void backpropogate(struct Node *node, int reward) {
    #ifdef DEBUG
    printf("#######\t\t\tBACKPROPAGATE\t\t   #######\n\n");
    char buf[50];
    #endif

    while (node != NULL) {
        node->num_visits++;
        node->total_reward += reward;

        #ifdef DEBUG
        sprintf(buf, "Number of Visits: %4d\nTotal Reward:     %4d\n", node->num_visits, node->total_reward);
        ml_append(buf, '\n');
        #endif

        node = node->parent;
    }
    #ifdef DEBUG
    ml_flush('\t');
    #endif
}

static int rollout(PyObject *state) {
    #ifdef DEBUG
    printf("########\t\tROLLOUT\t\t\t  ########\n\n");
    #endif

    PyObject *action;
    PyObject *new_state;
    PyObject *terminate = PyObject_CallMethodObjArgs(state, is_terminal, NULL);

    Py_INCREF(state);

    while (terminate == Py_False) {
        Py_DECREF(terminate);

        action = PyObject_CallMethodObjArgs(state, get_proposed_action, NULL);


        #ifdef NULL_CHECKS
        if (!action || action == Py_None) {
            printf("ERROR:");
            printf("\tget_proposed_action returned None or NULL\n");
            printf("\tis get_proposed_action implemented?\n");
            return 0;
        }
        #endif

        new_state = PyObject_CallMethodObjArgs(state, take_action, action, NULL);

        #ifdef NULL_CHECKS
        if (!state || state == Py_None) {
            printf("ERROR:");
            printf("\ttake_action returned None or NULL\n");
            printf("\tis take_action implemented?\n");
            return 0;
        }
        #endif

        terminate = PyObject_CallMethodObjArgs(new_state, is_terminal, NULL);

        Py_DECREF(action);
        Py_DECREF(state);

        state = new_state;

        #ifdef DEBUG
        PyObject *str_repr = PyObject_Str(state);
        ml_append(PyUnicode_AsUTF8(str_repr), '\n');
        Py_DECREF(str_repr);
        #endif
    }
    PyObject *reward = PyObject_CallMethodObjArgs(state, get_reward, NULL);
    int result = (int) PyLong_AsLong(reward);

    #ifdef DEBUG
    ml_flush('\t');
    printf("\tReward: %d\n\n", result);
    #endif

    Py_DECREF(terminate);
    Py_DECREF(state);
    Py_DECREF(reward);

    return result;
}

static struct Node * selection(struct Node *parent) {
    #ifdef DEBUG
    printf("##########\t\tSELECT\t\t\t##########\n\n");
    #endif

    while (!parent->is_terminal) {
        if (parent->is_explored) {
            parent = get_next_best_state(parent, sqrt(2))->value;

            #ifdef DEBUG
            PyObject *str_repr = PyObject_Str(parent->state);
            ml_append(PyUnicode_AsUTF8(str_repr), '\n');
            Py_DECREF(str_repr);
            #endif
        }
        else {
            // If parent is not fully explored, it will be expanded.
            // Easier to implement when not using an extra function
            PyObject *item;
            if ((item = PyIter_Next(parent->state))) {
                #ifdef DEBUG
                ml_flush('\t');
                printf("#########\t\tEXPAND\t\t\t #########\n\n");
                #endif

                char *action = strdup(PyUnicode_AsUTF8(item));

                if (dict_get_str_node(parent->children, action) == NULL) {
                    PyObject *new_state = PyObject_CallMethodObjArgs(parent->state, take_action, item, NULL);

                    #ifdef NULL_CHECKS
                    if (!new_state || new_state == Py_None) {
                        printf("ERROR:\n");
                        printf("\tCall to take_action should neither be NULL nor None.\n");
                        printf("\tIs take_action implemented?.\n");
                        goto exit_error;
                    }
                    #endif

                    struct Node *child_node = new_node(new_state, parent);
                    dict_put_str_node(parent->children, action, child_node);

                    #ifdef DEBUG
                    PyObject *str_repr = PyObject_Str(new_state);
                    printf("%s\n", PyUnicode_AsUTF8(str_repr));
                    Py_DECREF(str_repr);
                    #endif

                    Py_DECREF(item);
                    return child_node;
                }

                free(action);
                #ifdef DEBUG
                printf("ERROR: Generator probably returned duplicate items. (Equal actions)\n");
                goto exit_error;
                #endif
            }
            parent->is_explored = true; // No more possible nodes to expand in PyIter_Next.
        }
    }

    #ifdef DEBUG
        ml_flush('\t');
    #endif

    return parent;

    #ifdef DEBUG
    exit_error:
        printf("\n#####\t#####\t#####\t#####\t#####\t#####\t#####\t#####\n\n");
        printf("Children of current Node to be expanded:\n\n");
        dict_print_str_node(parent->children);
        return NULL;
    #endif
}

static void execute(struct Node *root) {
    struct Node *node;
    int reward;
    node = selection(root);
    reward = rollout(node->state);
    backpropogate(node, reward);
}

static PyObject * search(PyObject *self, PyObject *state) {
    Py_INCREF(state);
    struct Node *root = new_node(state, NULL);

    for (int i = 0; i < 5000; ++i) {
        #ifdef DEBUG
        printf("###########\t\tITERATION: %3d ###########\n\n", i);
        #endif

        execute(root);
    }

    struct Bucket *item = get_next_best_state(root, 0);
    PyObject *ret = PyUnicode_FromString(item->key);

    free_value_str_node(root);

    return ret;
}

static PyMethodDef mctsMethods[] = {
    {"search",  search, METH_O,
     "Execute a shell command."},
    {NULL, NULL, 0, NULL}        /* Sentinel */
};

static struct PyModuleDef mctsmodule = {
    PyModuleDef_HEAD_INIT,
    "backend",   /* name of module */
    NULL, /* module documentation, may be NULL */
    -1,       /* size of per-interpreter state of the module, or -1 if the module keeps state in global variables. */
    mctsMethods
};


PyMODINIT_FUNC PyInit_backend(void) {
    get_proposed_action = PyUnicode_InternFromString("get_proposed_action");
    get_unexplored_actions = PyUnicode_InternFromString("get_unexplored_actions");
    take_action = PyUnicode_InternFromString("take_action");
    is_terminal = PyUnicode_InternFromString("is_terminal");
    get_reward = PyUnicode_InternFromString("get_reward");
    num_children = 10 * (5/4.0);
    return PyModule_Create(&mctsmodule);
}