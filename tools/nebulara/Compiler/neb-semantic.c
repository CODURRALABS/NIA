/*
 * neb-semantic.c - Semantic Analysis Module for Nebulara
 * 
 * Phase 1: Symbol table construction and scope resolution
 * Phase 2: Type checking and inference
 * Phase 3: Error reporting with source locations
 *
 * Build: gcc -o neb-semantic.exe neb-semantic.c -static -O2
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

/* Types */
typedef enum {
    TYPE_UNKNOWN = 0,
    TYPE_INT,
    TYPE_STRING,
    TYPE_BOOL,
    TYPE_ARRAY,
    TYPE_NULL,
    TYPE_FUNC,
    TYPE_FUNC_REF
} NebType;

typedef struct {
    char name[256];
    NebType type;
    int line;
    int col;
    int is_mutable;
    int is_initialized;
} Symbol;

typedef struct Scope {
    Symbol symbols[256];
    int count;
    struct Scope *parent;
    char scope_name[128];
} Scope;

/* Global state */
static Scope *current_scope = NULL;
static int error_count = 0;
static int warning_count = 0;

/* Scope management */
Scope *scope_create(const char *name, Scope *parent) {
    Scope *s = (Scope *)calloc(1, sizeof(Scope));
    strncpy(s->scope_name, name, 127);
    s->parent = parent;
    s->count = 0;
    return s;
}

void scope_push(const char *name) {
    current_scope = scope_create(name, current_scope);
}

void scope_pop() {
    Scope *old = current_scope;
    if (old && old->parent) {
        current_scope = old->parent;
    }
    free(old);
}

/* Symbol operations */
int symbol_define(const char *name, NebType type, int line, int col, int is_mutable) {
    if (!current_scope) return -1;
    if (current_scope->count >= 256) return -2;
    
    /* Check for duplicate in current scope */
    for (int i = 0; i < current_scope->count; i++) {
        if (strcmp(current_scope->symbols[i].name, name) == 0) {
            fprintf(stderr, "SEMANTIC ERROR [%d:%d]: '%s' already defined in this scope\n",
                    line, col, name);
            error_count++;
            return -3;
        }
    }
    
    Symbol *s = &current_scope->symbols[current_scope->count];
    strncpy(s->name, name, 255);
    s->type = type;
    s->line = line;
    s->col = col;
    s->is_mutable = is_mutable;
    s->is_initialized = 0;
    current_scope->count++;
    return 0;
}

Symbol *symbol_lookup(const char *name) {
    Scope *s = current_scope;
    while (s) {
        for (int i = 0; i < s->count; i++) {
            if (strcmp(s->symbols[i].name, name) == 0) {
                return &s->symbols[i];
            }
        }
        s = s->parent;
    }
    return NULL;
}

int symbol_resolve(const char *name, int line, int col) {
    Symbol *s = symbol_lookup(name);
    if (!s) {
        fprintf(stderr, "SEMANTIC ERROR [%d:%d]: '%s' not defined\n", line, col, name);
        error_count++;
        return -1;
    }
    return 0;
}

/* Type checking */
const char *type_name(NebType t) {
    switch (t) {
        case TYPE_INT:     return "int";
        case TYPE_STRING:  return "string";
        case TYPE_BOOL:    return "bool";
        case TYPE_ARRAY:   return "array";
        case TYPE_NULL:    return "null";
        case TYPE_FUNC:
        case TYPE_FUNC_REF: return "func";
        default:           return "unknown";
    }
}

NebType type_check_binary(NebType left, const char *op, NebType right, int line, int col) {
    /* Arithmetic: int + int = int */
    if ((strcmp(op, "+") == 0 || strcmp(op, "-") == 0 || 
         strcmp(op, "*") == 0 || strcmp(op, "/") == 0 || strcmp(op, "%") == 0)) {
        if (left == TYPE_INT && right == TYPE_INT) return TYPE_INT;
        /* String concatenation */
        if (left == TYPE_STRING && right == TYPE_STRING) return TYPE_STRING;
        fprintf(stderr, "SEMANTIC ERROR [%d:%d]: type mismatch: %s %s %s\n",
                line, col, type_name(left), op, type_name(right));
        error_count++;
        return TYPE_UNKNOWN;
    }
    
    /* Comparison: same-type operands */
    if (strcmp(op, "==") == 0 || strcmp(op, "!=") == 0 ||
        strcmp(op, "<") == 0 || strcmp(op, ">") == 0 ||
        strcmp(op, "<=") == 0 || strcmp(op, ">=") == 0) {
        if (left == right) return TYPE_BOOL;
        /* Allow null comparison */
        if (left == TYPE_NULL || right == TYPE_NULL) return TYPE_BOOL;
        fprintf(stderr, "SEMANTIC WARNING [%d:%d]: comparing %s with %s\n",
                line, col, type_name(left), type_name(right));
        warning_count++;
        return TYPE_BOOL;
    }
    
    return TYPE_UNKNOWN;
}

/* Type inference from literal */
NebType infer_type_from_literal(const char *value) {
    if (!value) return TYPE_NULL;
    if (value[0] == '"') return TYPE_STRING;
    if (value[0] == '[') return TYPE_ARRAY;
    if (strcmp(value, "TRUE") == 0 || strcmp(value, "FALSE") == 0) return TYPE_BOOL;
    if (strcmp(value, "NULL") == 0) return TYPE_NULL;
    /* Check if number */
    int i = 0;
    if (value[0] == '-' || value[0] == '+') i = 1;
    int is_num = 1;
    for (; value[i]; i++) {
        if (value[i] < '0' || value[i] > '9') { is_num = 0; break; }
    }
    if (is_num && i > 0) return TYPE_INT;
    return TYPE_UNKNOWN;
}

/* Built-in function validation */
NebType check_builtin(const char *name, int arg_count, NebType *arg_types, int line, int col) {
    if (strcmp(name, "PRINT") == 0) return TYPE_NULL;
    if (strcmp(name, "LEN") == 0) {
        if (arg_count != 1) {
            fprintf(stderr, "SEMANTIC ERROR [%d:%d]: LEN expects 1 argument, got %d\n",
                    line, col, arg_count);
            error_count++;
            return TYPE_UNKNOWN;
        }
        if (arg_types[0] != TYPE_STRING && arg_types[0] != TYPE_ARRAY) {
            fprintf(stderr, "SEMANTIC ERROR [%d:%d]: LEN expects string or array, got %s\n",
                    line, col, type_name(arg_types[0]));
            error_count++;
            return TYPE_UNKNOWN;
        }
        return TYPE_INT;
    }
    if (strcmp(name, "TYPEOF") == 0) return TYPE_STRING;
    if (strcmp(name, "TO_STRING") == 0) return TYPE_STRING;
    if (strcmp(name, "TO_NUMBER") == 0) return TYPE_INT;
    if (strcmp(name, "RANDOM") == 0) return TYPE_INT;
    if (strcmp(name, "TIME") == 0) return TYPE_INT;
    if (strcmp(name, "CONCAT") == 0) return TYPE_STRING;
    
    return TYPE_UNKNOWN;
}

/* Report results */
void semantic_report(void) {
    if (error_count == 0 && warning_count == 0) {
        printf("Semantic analysis: PASS (no errors, no warnings)\n");
    } else {
        printf("Semantic analysis: %d error(s), %d warning(s)\n", error_count, warning_count);
    }
}

int semantic_errors(void) {
    return error_count;
}

/* Demo/test function */
#ifdef NEB_SEMANTIC_TEST
int main(void) {
    printf("=== Nebulara Semantic Analysis Module ===\n\n");
    
    /* Create global scope */
    scope_push("global");
    
    /* Define variables */
    symbol_define("x", TYPE_INT, 1, 5, 1);
    symbol_define("name", TYPE_STRING, 2, 5, 1);
    symbol_define("PI", TYPE_INT, 3, 5, 0);
    
    /* Create function scope */
    scope_push("factorial");
    symbol_define("n", TYPE_INT, 10, 10, 1);
    
    /* Test lookup */
    Symbol *s = symbol_lookup("n");
    if (s) printf("Found '%s' of type %s (defined at line %d)\n", 
                  s->name, type_name(s->type), s->line);
    
    /* Test undefined variable */
    symbol_resolve("undefined_var", 15, 5);
    
    /* Test type checking */
    type_check_binary(TYPE_INT, "+", TYPE_INT, 20, 10);
    type_check_binary(TYPE_INT, "+", TYPE_STRING, 21, 10);
    type_check_binary(TYPE_STRING, "+", TYPE_STRING, 22, 10);
    
    /* Test built-ins */
    NebType args[] = { TYPE_STRING };
    check_builtin("LEN", 1, args, 30, 5);
    check_builtin("PRINT", 1, args, 31, 5);
    
    scope_pop();  /* pop factorial scope */
    scope_pop();  /* pop global scope */
    
    semantic_report();
    return error_count > 0 ? 1 : 0;
}
#endif
