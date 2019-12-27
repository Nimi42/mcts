#ifndef MULTILINE_PRINT_H
#define MULTILINE_PRINT_H

#include <stdlib.h>
#include <stdio.h>
#include <string.h>

void ml_append(const char *seq, char delim);
void ml_flush(char offset);

#endif // MULTILINE_PRINT_H