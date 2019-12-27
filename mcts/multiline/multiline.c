#include "include/multiline.h"

struct Lines {
	unsigned count;
	struct Column *head;
	struct Column *toe;
};

struct Column {
	unsigned count;
	unsigned lines;
	char **content;
	struct Column *next;
};

static struct Lines *g_lines = NULL;

static const char ARROW_BLANK[8] = "       ";
static const char ARROW[8] = "  -->  ";

static struct Column * new_column(unsigned num_lines, unsigned num_chars) {
	struct Column *col = malloc(sizeof(struct Column));
	char **content = malloc(num_lines * sizeof(char *));
	col->content = content;
	col->count = num_chars;
	col->next = NULL;

	return col;
}

static void free_lines(void) {
	struct Column *head = g_lines->head;
	struct Column *tmp;
	while (head != NULL) {
		tmp = head;
		head = head->next;
		for (unsigned i = 0; i < tmp->lines; ++i) {
			free(tmp->content[i]);
		}
		free(tmp->content);
		free(tmp);
	}
	free(g_lines);
	g_lines = NULL;
}

static struct Column * to_column_seq(const char *block, char delim) {
	char c;
	unsigned i, j;
	unsigned num_chars = 0, num_lines = 0;

	j = 0;
	
	c = 1;
	for (i = 0; c; ++i) {
		c = block[i];
		if (c == delim || c == '\0') {
			if (j > num_chars)
				num_chars = j;
			j = 0;
			++num_lines;
		} else {
			++j;
		} 
	}

	struct Column *col = new_column(num_lines, num_chars);
	char *seq;

	col->lines = num_lines;	

	for (i = 0; i < num_lines; ++i) {
		c = *block++;
		seq = malloc((num_chars + 1) * sizeof(char));
		for (j = 0; j < num_chars; ++j) {
			if (c == delim || c == '\0') {
				seq[j] = ' ';
			} else {
				seq[j] = c;
				c = *block++;
			}
		}
		seq[j] = '\0';
		col->content[i] = seq;
	}

	return col;
}

static void append(struct Column *col) {
	if (g_lines == NULL) {
		g_lines = malloc(sizeof(struct Lines));

		g_lines->count = col->lines;
		g_lines->head = col;
		g_lines->toe = g_lines->head;
	} else {
		
		if (g_lines->count < col->lines) {
			g_lines->count = col->lines;
		}
		g_lines->toe->next = col;
		g_lines->toe = col;
	}
}

void ml_append(const char *seq, char delim){
	append(to_column_seq(seq, delim));
}

void ml_flush(char offset) {
	if (g_lines != NULL) {
		struct Column *head;
		unsigned num_lines = g_lines->count;
		unsigned half = (num_lines / 2) + ((num_lines % 2) - 1);

		for (unsigned i = 0; i < num_lines; ++i) {
			printf("%c", offset);		
			head = g_lines->head;
			if (head->lines > i) {
				printf("%s", head->content[i]);
			} else {
				char tmp[head->count + 1];
				memset(tmp, ' ', head->count);
				tmp[head->count] = '\0';
				printf("%s", tmp);
			}
			head = head->next;

			while(head != NULL) {
				if (i == half) {
					printf("%s", ARROW);
				} else {
					printf("%s", ARROW_BLANK);
				}

				if (head->lines > i) {
					printf("%s", head->content[i]);
				} else {
					char tmp[head->count + 1];
					memset(tmp, ' ', head->count);
					tmp[head->count] = '\0';
					printf("%s", tmp);
				}
				head = head->next;
			}
			printf("\n");
		}
		free_lines();
	}	
}