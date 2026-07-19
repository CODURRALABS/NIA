// Nebulara Self-Hosted Interpreter
// Compiler/nbs-bootstrap.c - Interprets .nbs programs directly
// Phase 2: Full interpreter with strings, control flow, functions, arrays

#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>
#include <stdarg.h>
#include <time.h>
#include <math.h>
#include <errno.h>

// FFI platform headers
#ifdef _WIN32
#include <windows.h>
typedef HMODULE NbsFFIHandle;
#else
#include <dlfcn.h>
typedef void* NbsFFIHandle;
#endif

// ============================================================================
// VALUE SYSTEM — Tagged union for dynamic typing
// ============================================================================

#define VAL_NULL    0
#define VAL_INT     1
#define VAL_STRING  2
#define VAL_BOOL    3
#define VAL_ARRAY   4
#define VAL_FUNC    5

typedef struct Value Value;
typedef struct ValueArray ValueArray;

struct Value {
    int type;
    union {
        int64_t i;
        char* s;
        int b;
        ValueArray* a;
        int func_idx;
    } as;
};

struct ValueArray {
    Value* items;
    int count;
    int capacity;
};

Value val_null(void) { return (Value){VAL_NULL, {0}}; }
Value val_int(int64_t v) { return (Value){VAL_INT, {.i = v}}; }
Value val_bool(int v) { return (Value){VAL_BOOL, {.b = v}}; }
Value val_string(const char* s) {
    Value v; v.type = VAL_STRING;
    v.as.s = (char*)malloc(strlen(s) + 1);
    strcpy(v.as.s, s);
    return v;
}
Value val_array(void) {
    Value v; v.type = VAL_ARRAY;
    v.as.a = (ValueArray*)calloc(1, sizeof(ValueArray));
    return v;
}

void val_free(Value v) {
    if (v.type == VAL_STRING) free(v.as.s);
    if (v.type == VAL_ARRAY && v.as.a) {
        for (int i = 0; i < v.as.a->count; i++) val_free(v.as.a->items[i]);
        free(v.as.a->items);
        free(v.as.a);
    }
}

Value val_copy(Value v) {
    if (v.type == VAL_STRING) return val_string(v.as.s);
    if (v.type == VAL_ARRAY) {
        Value arr = val_array();
        for (int i = 0; i < v.as.a->count; i++) {
            if (arr.as.a->count >= arr.as.a->capacity) {
                arr.as.a->capacity = arr.as.a->capacity ? arr.as.a->capacity * 2 : 8;
                arr.as.a->items = (Value*)realloc(arr.as.a->items, arr.as.a->capacity * sizeof(Value));
            }
            arr.as.a->items[arr.as.a->count++] = val_copy(v.as.a->items[i]);
        }
        return arr;
    }
    return v;
}

int val_is_truthy(Value v) {
    if (v.type == VAL_NULL) return 0;
    if (v.type == VAL_BOOL) return v.as.b;
    if (v.type == VAL_INT) return v.as.i != 0;
    if (v.type == VAL_STRING) return v.as.s[0] != 0;
    if (v.type == VAL_ARRAY) return v.as.a->count > 0;
    return 1;
}

const char* val_type_name(Value v) {
    switch (v.type) {
        case VAL_NULL: return "null";
        case VAL_INT: return "int";
        case VAL_STRING: return "string";
        case VAL_BOOL: return "bool";
        case VAL_ARRAY: return "array";
        case VAL_FUNC: return "func";
        default: return "unknown";
    }
}

// ============================================================================
// FFI SYSTEM — Foreign Function Interface
// ============================================================================

typedef enum {
    NBS_FFI_VOID, NBS_FFI_INT, NBS_FFI_FLOAT, NBS_FFI_DOUBLE,
    NBS_FFI_STRING, NBS_FFI_POINTER
} NbsFFIType;

typedef struct {
    char name[256];
    NbsFFIType return_type;
    int param_count;
    NbsFFIHandle handle;
    void* fn_ptr;
} NbsFFIFunc;

typedef struct {
    char name[256];
    char path[512];
    NbsFFIFunc functions[256];
    int func_count;
    int is_loaded;
} NbsFFILib;

static NbsFFILib ffi_libs[64];
static int ffi_lib_count = 0;

static int ffi_load_lib(const char* name, const char* path) {
    if (ffi_lib_count >= 64) return -1;
    NbsFFILib* lib = &ffi_libs[ffi_lib_count];
    memset(lib, 0, sizeof(NbsFFILib));
    strncpy(lib->name, name, 255);
    strncpy(lib->path, path, 511);
    lib->func_count = 0;
#ifdef _WIN32
    lib->is_loaded = 1;
#else
    void* handle = dlopen(path, RTLD_LAZY);
    lib->is_loaded = (handle != NULL);
    if (!handle) fprintf(stderr, "FFI WARNING: could not load '%s': %s\n", path, dlerror());
#endif
    ffi_lib_count++;
    return 0;
}

static int ffi_register_func(const char* lib_name, const char* func_name, NbsFFIType ret_type, int param_count) {
    for (int i = 0; i < ffi_lib_count; i++) {
        if (strcmp(ffi_libs[i].name, lib_name) == 0) {
            NbsFFILib* lib = &ffi_libs[i];
            if (lib->func_count >= 256) return -2;
            NbsFFIFunc* func = &lib->functions[lib->func_count];
            memset(func, 0, sizeof(NbsFFIFunc));
            strncpy(func->name, func_name, 255);
            func->return_type = ret_type;
            func->param_count = param_count;
            lib->func_count++;
            return 0;
        }
    }
    return -1;
}

static void* ffi_resolve_func(NbsFFILib* lib, NbsFFIFunc* func) {
    if (func->fn_ptr) return func->fn_ptr;
#ifdef _WIN32
    HMODULE h = LoadLibraryA(lib->path);
    if (!h) { fprintf(stderr, "FFI ERROR: Cannot load '%s'\n", lib->path); return NULL; }
    func->fn_ptr = (void*)GetProcAddress(h, func->name);
#else
    void* handle = dlopen(lib->path, RTLD_LAZY);
    if (!handle) { fprintf(stderr, "FFI ERROR: Cannot load '%s': %s\n", lib->path, dlerror()); return NULL; }
    func->fn_ptr = dlsym(handle, func->name);
#endif
    if (!func->fn_ptr) fprintf(stderr, "FFI ERROR: Symbol '%s' not found in '%s'\n", func->name, lib->path);
    return func->fn_ptr;
}

Value val_to_string(Value v) {
    char buf[128];
    switch (v.type) {
        case VAL_NULL: return val_string("null");
        case VAL_INT: snprintf(buf, sizeof(buf), "%lld", v.as.i); return val_string(buf);
        case VAL_BOOL: return val_string(v.as.b ? "true" : "false");
        case VAL_STRING: return val_string(v.as.s);
        case VAL_ARRAY: snprintf(buf, sizeof(buf), "[array %d]", v.as.a->count); return val_string(buf);
        default: return val_string("unknown");
    }
}

Value val_add(Value a, Value b) {
    if (a.type == VAL_INT && b.type == VAL_INT) return val_int(a.as.i + b.as.i);
    if (a.type == VAL_ARRAY && b.type == VAL_ARRAY) {
        Value result = val_array();
        for (int i = 0; i < a.as.a->count; i++) {
            if (result.as.a->count >= result.as.a->capacity) {
                result.as.a->capacity = result.as.a->capacity ? result.as.a->capacity * 2 : 8;
                result.as.a->items = (Value*)realloc(result.as.a->items, result.as.a->capacity * sizeof(Value));
            }
            result.as.a->items[result.as.a->count++] = val_copy(a.as.a->items[i]);
        }
        for (int i = 0; i < b.as.a->count; i++) {
            if (result.as.a->count >= result.as.a->capacity) {
                result.as.a->capacity = result.as.a->capacity ? result.as.a->capacity * 2 : 8;
                result.as.a->items = (Value*)realloc(result.as.a->items, result.as.a->capacity * sizeof(Value));
            }
            result.as.a->items[result.as.a->count++] = val_copy(b.as.a->items[i]);
        }
        return result;
    }
    if (a.type == VAL_ARRAY && b.type != VAL_ARRAY) {
        Value result = val_array();
        for (int i = 0; i < a.as.a->count; i++) {
            if (result.as.a->count >= result.as.a->capacity) {
                result.as.a->capacity = result.as.a->capacity ? result.as.a->capacity * 2 : 8;
                result.as.a->items = (Value*)realloc(result.as.a->items, result.as.a->capacity * sizeof(Value));
            }
            result.as.a->items[result.as.a->count++] = val_copy(a.as.a->items[i]);
        }
        if (result.as.a->count >= result.as.a->capacity) {
            result.as.a->capacity = result.as.a->capacity ? result.as.a->capacity * 2 : 8;
            result.as.a->items = (Value*)realloc(result.as.a->items, result.as.a->capacity * sizeof(Value));
        }
        result.as.a->items[result.as.a->count++] = val_copy(b);
        return result;
    }
    if (a.type != VAL_ARRAY && b.type == VAL_ARRAY) {
        Value result = val_array();
        if (result.as.a->count >= result.as.a->capacity) {
            result.as.a->capacity = result.as.a->capacity ? result.as.a->capacity * 2 : 8;
            result.as.a->items = (Value*)realloc(result.as.a->items, result.as.a->capacity * sizeof(Value));
        }
        result.as.a->items[result.as.a->count++] = val_copy(a);
        for (int i = 0; i < b.as.a->count; i++) {
            if (result.as.a->count >= result.as.a->capacity) {
                result.as.a->capacity = result.as.a->capacity ? result.as.a->capacity * 2 : 8;
                result.as.a->items = (Value*)realloc(result.as.a->items, result.as.a->capacity * sizeof(Value));
            }
            result.as.a->items[result.as.a->count++] = val_copy(b.as.a->items[i]);
        }
        return result;
    }
    if (a.type == VAL_STRING || b.type == VAL_STRING) {
        Value sa = val_to_string(a);
        Value sb = val_to_string(b);
        int len = strlen(sa.as.s) + strlen(sb.as.s) + 1;
        char* buf = (char*)malloc(len);
        strcpy(buf, sa.as.s);
        strcat(buf, sb.as.s);
        val_free(sa); val_free(sb);
        Value r; r.type = VAL_STRING; r.as.s = buf;
        return r;
    }
    return val_null();
}

Value val_sub(Value a, Value b) {
    if (a.type == VAL_INT && b.type == VAL_INT) return val_int(a.as.i - b.as.i);
    return val_null();
}

Value val_mul(Value a, Value b) {
    if (a.type == VAL_INT && b.type == VAL_INT) return val_int(a.as.i * b.as.i);
    return val_null();
}

Value val_div(Value a, Value b) {
    if (a.type == VAL_INT && b.type == VAL_INT) {
        if (b.as.i == 0) { fprintf(stderr, "Runtime error: division by zero\n"); exit(1); }
        return val_int(a.as.i / b.as.i);
    }
    return val_null();
}

Value val_mod(Value a, Value b) {
    if (a.type == VAL_INT && b.type == VAL_INT) {
        if (b.as.i == 0) { fprintf(stderr, "Runtime error: modulo by zero\n"); exit(1); }
        return val_int(a.as.i % b.as.i);
    }
    return val_null();
}

int val_equals(Value a, Value b) {
    if (a.type == b.type) {
        switch (a.type) {
            case VAL_NULL: return 1;
            case VAL_INT: return a.as.i == b.as.i;
            case VAL_BOOL: return a.as.b == b.as.b;
            case VAL_STRING: return strcmp(a.as.s, b.as.s) == 0;
            default: return 0;
        }
    }
    // Cross-type: bool <-> int, null <-> int(0)
    if (a.type == VAL_BOOL && b.type == VAL_INT) return a.as.b == (b.as.i != 0);
    if (a.type == VAL_INT && b.type == VAL_BOOL) return (a.as.i != 0) == b.as.b;
    if (a.type == VAL_NULL && b.type == VAL_INT) return b.as.i == 0;
    if (a.type == VAL_INT && b.type == VAL_NULL) return a.as.i == 0;
    return 0;
}

int val_less(Value a, Value b) {
    if (a.type == VAL_INT && b.type == VAL_INT) return a.as.i < b.as.i;
    return 0;
}

int val_greater(Value a, Value b) {
    if (a.type == VAL_INT && b.type == VAL_INT) return a.as.i > b.as.i;
    return 0;
}

// ============================================================================
// LEXER
// ============================================================================

typedef enum {
    // Literals
    TOK_INT_LIT, TOK_STRING_LIT, TOK_IDENT,
    // Keywords
    TOK_FUNC, TOK_DATA, TOK_RUN, TOK_END,
    TOK_IF, TOK_ELSE, TOK_THEN, TOK_WHILE, TOK_FOR, TOK_TO, TOK_STEP,
    TOK_RETURN, TOK_BREAK, TOK_CONTINUE,
    TOK_PRINT, TOK_LET, TOK_CONST,
    // Operators
    TOK_PLUS, TOK_MINUS, TOK_STAR, TOK_SLASH, TOK_PERCENT,
    TOK_EQ, TOK_NEQ, TOK_LT, TOK_GT, TOK_LTE, TOK_GTE,
    TOK_AND, TOK_OR, TOK_NOT, TOK_ASSIGN,
    TOK_DOT, TOK_COMMA, TOK_COLON, TOK_SEMICOLON,
    TOK_LPAREN, TOK_RPAREN, TOK_LBRACKET, TOK_RBRACKET,
    TOK_ELSEIF, TOK_TRUE, TOK_FALSE, TOK_NULL,
    // Bitwise operators
    TOK_BITAND, TOK_BITOR, TOK_LSHIFT, TOK_RSHIFT,
    // Exception handling keywords
    TOK_TRY, TOK_CATCH, TOK_THROW, TOK_FINALLY, TOK_ENDTRY, TOK_IMPORT,
    // Special
    TOK_EOF, TOK_ERROR
} NbsTokenType;

typedef struct {
    NbsTokenType type;
    char text[256];
    int64_t int_val;
    int line;
} NbsToken;

typedef struct {
    const char* src;
    int pos, len, line;
} Lexer;

Lexer lexer_new(const char* src) {
    Lexer l = {src, 0, (int)strlen(src), 1};
    return l;
}

char lexer_peek(Lexer* l) {
    if (l->pos >= l->len) return 0;
    return l->src[l->pos];
}

char lexer_advance(Lexer* l) {
    char c = l->src[l->pos++];
    if (c == '\n') l->line++;
    return c;
}

void lexer_skip_whitespace(Lexer* l) {
    while (l->pos < l->len) {
        char c = l->src[l->pos];
        if (c == ' ' || c == '\t' || c == '\r' || c == '\n') { l->pos++; if (c == '\n') l->line++; }
        else if (c == '#') { while (l->pos < l->len && l->src[l->pos] != '\n') l->pos++; }
        else break;
    }
}

NbsToken lexer_next(Lexer* l) {
    lexer_skip_whitespace(l);
    NbsToken tok = {0};
    tok.line = l->line;

    if (l->pos >= l->len) { tok.type = TOK_EOF; return tok; }

    char c = l->src[l->pos];

    // Numbers
    if (c >= '0' && c <= '9') {
        int64_t val = 0;
        while (l->pos < l->len && l->src[l->pos] >= '0' && l->src[l->pos] <= '9')
            val = val * 10 + lexer_advance(l) - '0';
        tok.type = TOK_INT_LIT;
        tok.int_val = val;
        sprintf(tok.text, "%lld", val);
        return tok;
    }

    // Strings
    if (c == '"') {
        lexer_advance(l);
        int start = l->pos;
        while (l->pos < l->len && l->src[l->pos] != '"') {
            if (l->src[l->pos] == '\\') l->pos++; // skip escaped char
            l->pos++;
        }
        int slen = l->pos - start;
        if (slen > 255) slen = 255;
        // Copy with escape processing
        int di = 0;
        for (int si = start; si < l->pos && di < 255; si++) {
            if (l->src[si] == '\\' && si + 1 < l->pos) {
                si++;
                if (l->src[si] == 'n') tok.text[di++] = '\n';
                else if (l->src[si] == 't') tok.text[di++] = '\t';
                else if (l->src[si] == '\\') tok.text[di++] = '\\';
                else if (l->src[si] == '"') tok.text[di++] = '"';
                else tok.text[di++] = l->src[si];
            } else {
                tok.text[di++] = l->src[si];
            }
        }
        tok.text[di] = 0;
        tok.type = TOK_STRING_LIT;
        if (l->pos < l->len) lexer_advance(l); // skip closing quote
        return tok;
    }

    // Identifiers and keywords
    if ((c >= 'a' && c <= 'z') || (c >= 'A' && c <= 'Z') || c == '_') {
        int start = l->pos;
        while (l->pos < l->len && (
            (l->src[l->pos] >= 'a' && l->src[l->pos] <= 'z') ||
            (l->src[l->pos] >= 'A' && l->src[l->pos] <= 'Z') ||
            (l->src[l->pos] >= '0' && l->src[l->pos] <= '9') ||
            l->src[l->pos] == '_' || l->src[l->pos] == '!' || l->src[l->pos] == '?'
        )) l->pos++;
        int slen = l->pos - start;
        memcpy(tok.text, l->src + start, slen);
        tok.text[slen] = 0;

        // Keywords (Nebulara syntax)
        if (strcmp(tok.text, "FUNC!") == 0) tok.type = TOK_FUNC;
        else if (strcmp(tok.text, "DATA!") == 0) tok.type = TOK_DATA;
        else if (strcmp(tok.text, "RUN!") == 0) tok.type = TOK_RUN;
        else if (strcmp(tok.text, "END!") == 0) tok.type = TOK_END;
        else if (strcmp(tok.text, "IF?") == 0) tok.type = TOK_IF;
        else if (strcmp(tok.text, "ELSE") == 0) tok.type = TOK_ELSE;
        else if (strcmp(tok.text, "WHILE?") == 0) tok.type = TOK_WHILE;
        else if (strcmp(tok.text, "FOR!") == 0) tok.type = TOK_FOR;
        else if (strcmp(tok.text, "THEN") == 0) tok.type = TOK_THEN;
    else if (strcmp(tok.text, "TO") == 0) tok.type = TOK_TO;
        else if (strcmp(tok.text, "STEP") == 0) tok.type = TOK_STEP;
        else if (strcmp(tok.text, "RETURN") == 0) tok.type = TOK_RETURN;
        else if (strcmp(tok.text, "BREAK") == 0) tok.type = TOK_BREAK;
        else if (strcmp(tok.text, "CONTINUE") == 0) tok.type = TOK_CONTINUE;
        else if (strcmp(tok.text, "PRINT") == 0) tok.type = TOK_PRINT;
        else if (strcmp(tok.text, "LET") == 0) tok.type = TOK_LET;
        else if (strcmp(tok.text, "CONST") == 0) tok.type = TOK_CONST;
        else if (strcmp(tok.text, "AND") == 0) tok.type = TOK_AND;
        else if (strcmp(tok.text, "OR") == 0) tok.type = TOK_OR;
        else if (strcmp(tok.text, "NOT") == 0) tok.type = TOK_NOT;
        else if (strcmp(tok.text, "NULL") == 0) { tok.type = TOK_NULL; strcpy(tok.text, "null"); }
        else if (strcmp(tok.text, "TRUE") == 0) { tok.type = TOK_TRUE; strcpy(tok.text, "true"); }
        else if (strcmp(tok.text, "FALSE") == 0) { tok.type = TOK_FALSE; strcpy(tok.text, "false"); }
        else if (strcmp(tok.text, "ELSEIF?") == 0) tok.type = TOK_ELSEIF;
        else if (strcmp(tok.text, "TRY!") == 0) tok.type = TOK_TRY;
        else if (strcmp(tok.text, "CATCH!") == 0) tok.type = TOK_CATCH;
        else if (strcmp(tok.text, "THROW") == 0) tok.type = TOK_THROW;
        else if (strcmp(tok.text, "FINALLY!") == 0) tok.type = TOK_FINALLY;
        else if (strcmp(tok.text, "ENDTRY!") == 0) tok.type = TOK_ENDTRY;
        else if (strcmp(tok.text, "IMPORT") == 0) tok.type = TOK_IMPORT;
        else tok.type = TOK_IDENT;
        return tok;
    }

    // Operators
    lexer_advance(l);
    tok.text[0] = c; tok.text[1] = 0;

    if (c == '+') tok.type = TOK_PLUS;
    else if (c == '-') tok.type = TOK_MINUS;
    else if (c == '*') tok.type = TOK_STAR;
    else if (c == '/') tok.type = TOK_SLASH;
    else if (c == '%') tok.type = TOK_PERCENT;
    else if (c == '=') {
        if (lexer_peek(l) == '=') { lexer_advance(l); tok.text[1] = '='; tok.text[2] = 0; tok.type = TOK_EQ; }
        else tok.type = TOK_ASSIGN;
    }
    else if (c == '!') {
        if (lexer_peek(l) == '=') { lexer_advance(l); tok.text[1] = '='; tok.text[2] = 0; tok.type = TOK_NEQ; }
        else { tok.type = TOK_ERROR; }
    }
    else if (c == '<') {
        if (lexer_peek(l) == '=') { lexer_advance(l); tok.text[1] = '='; tok.text[2] = 0; tok.type = TOK_LTE; }
        else if (lexer_peek(l) == '<') { lexer_advance(l); tok.text[1] = '<'; tok.text[2] = 0; tok.type = TOK_LSHIFT; }
        else tok.type = TOK_LT;
    }
    else if (c == '>') {
        if (lexer_peek(l) == '=') { lexer_advance(l); tok.text[1] = '='; tok.text[2] = 0; tok.type = TOK_GTE; }
        else if (lexer_peek(l) == '>') { lexer_advance(l); tok.text[1] = '>'; tok.text[2] = 0; tok.type = TOK_RSHIFT; }
        else tok.type = TOK_GT;
    }
    else if (c == '&') tok.type = TOK_BITAND;
    else if (c == '|') tok.type = TOK_BITOR;
    else if (c == '(') tok.type = TOK_LPAREN;
    else if (c == ')') tok.type = TOK_RPAREN;
    else if (c == '[') tok.type = TOK_LBRACKET;
    else if (c == ']') tok.type = TOK_RBRACKET;
    else if (c == '.') tok.type = TOK_DOT;
    else if (c == ',') tok.type = TOK_COMMA;
    else if (c == ':') tok.type = TOK_COLON;
    else if (c == ';') tok.type = TOK_SEMICOLON;
    else tok.type = TOK_ERROR;

    return tok;
}

// ============================================================================
// AST NODES
// ============================================================================

typedef enum {
    NODE_INT, NODE_STRING, NODE_IDENT, NODE_BINARY, NODE_UNARY,
    NODE_TRUE, NODE_FALSE, NODE_NULL,
    NODE_ASSIGN, NODE_PRINT, NODE_BLOCK, NODE_IF, NODE_WHILE, NODE_FOR,
    NODE_FUNC_DEF, NODE_FUNC_CALL, NODE_RETURN, NODE_BREAK, NODE_CONTINUE,
    NODE_ARRAY_LIT, NODE_ARRAY_INDEX, NODE_ARRAY_LEN, NODE_ARRAY_ASSIGN,
    NODE_LEN, NODE_TYPEOF, NODE_TOSTR, NODE_TONUM,
    NODE_TRY, NODE_THROW, NODE_IMPORT,
    NODE_PROGRAM
} NodeType;

typedef struct ASTNode ASTNode;

struct ASTNode {
    NodeType type;
    int64_t int_val;
    char str_val[256];
    char op[8];
    ASTNode* left;
    ASTNode* right;
    ASTNode* third;      // for IF (else branch)
    ASTNode** children;  // for blocks
    int child_count;
    char params[8][128]; // function parameter names
    int param_count;
    int line;
};

ASTNode* ast_new(NodeType type) {
    ASTNode* n = (ASTNode*)calloc(1, sizeof(ASTNode));
    n->type = type;
    return n;
}

// ============================================================================
// PARSER — Recursive descent
// ============================================================================

typedef struct {
    NbsToken tokens[4096];
    int pos, count;
    int has_error;
    char error_msg[512];
} Parser;

void parser_error(Parser* p, const char* msg, int line) {
    if (!p->has_error) {
        p->has_error = 1;
        snprintf(p->error_msg, sizeof(p->error_msg), "Line %d: %s", line, msg);
    }
}

NbsToken parser_peek(Parser* p) {
    if (p->pos >= p->count) return (NbsToken){TOK_EOF};
    return p->tokens[p->pos];
}

NbsToken parser_advance(Parser* p) {
    return p->tokens[p->pos++];
}

NbsToken parser_expect(Parser* p, NbsTokenType type) {
    NbsToken tok = parser_peek(p);
    if (tok.type != type) {
        char buf[256];
        snprintf(buf, sizeof(buf), "Expected NbsToken type %d, got '%s'", type, tok.text);
        parser_error(p, buf, tok.line);
    }
    return parser_advance(p);
}

// Expression parsing (Pratt parser for precedence)
int get_precedence(NbsTokenType t) {
    switch (t) {
        case TOK_OR: return 1;
        case TOK_AND: return 2;
        case TOK_BITOR: return 3;
        case TOK_BITAND: return 4;
        case TOK_EQ: case TOK_NEQ: return 5;
        case TOK_LT: case TOK_GT: case TOK_LTE: case TOK_GTE: case TOK_LSHIFT: case TOK_RSHIFT: return 6;
        case TOK_PLUS: case TOK_MINUS: return 7;
        case TOK_STAR: case TOK_SLASH: case TOK_PERCENT: return 8;
        case TOK_NOT: return 9;
        default: return 0;
    }
}

ASTNode* parse_expression(Parser* p);

ASTNode* parse_primary(Parser* p) {
    NbsToken tok = parser_peek(p);

    if (tok.type == TOK_INT_LIT) {
        parser_advance(p);
        ASTNode* n = ast_new(NODE_INT);
        n->int_val = tok.int_val;
        strcpy(n->str_val, tok.text);
        n->line = tok.line;
        return n;
    }

    if (tok.type == TOK_TRUE) {
        parser_advance(p);
        ASTNode* n = ast_new(NODE_TRUE);
        n->line = tok.line;
        return n;
    }
    if (tok.type == TOK_FALSE) {
        parser_advance(p);
        ASTNode* n = ast_new(NODE_FALSE);
        n->line = tok.line;
        return n;
    }
    if (tok.type == TOK_NULL) {
        parser_advance(p);
        ASTNode* n = ast_new(NODE_NULL);
        n->line = tok.line;
        return n;
    }

    if (tok.type == TOK_STRING_LIT) {
        parser_advance(p);
        ASTNode* n = ast_new(NODE_STRING);
        strcpy(n->str_val, tok.text);
        n->line = tok.line;
        return n;
    }

    if (tok.type == TOK_IDENT) {
        parser_advance(p);
        // Check for array index: ident[expr]
        if (parser_peek(p).type == TOK_LBRACKET) {
            parser_advance(p);
            ASTNode* idx = parse_expression(p);
            parser_expect(p, TOK_RBRACKET);
            ASTNode* n = ast_new(NODE_ARRAY_INDEX);
            ASTNode* id = ast_new(NODE_IDENT);
            strcpy(id->str_val, tok.text);
            n->left = id;
            n->right = idx;
            n->line = tok.line;
            return n;
        }
        // Check for function call: ident(args)
        if (parser_peek(p).type == TOK_LPAREN) {
            parser_advance(p);
            ASTNode* n = ast_new(NODE_FUNC_CALL);
            strcpy(n->str_val, tok.text);
            n->children = NULL;
            n->child_count = 0;
            if (parser_peek(p).type != TOK_RPAREN) {
                int cap = 8;
                n->children = (ASTNode**)malloc(cap * sizeof(ASTNode*));
                do {
                    if (n->child_count >= cap) {
                        cap *= 2;
                        n->children = (ASTNode**)realloc(n->children, cap * sizeof(ASTNode*));
                    }
                    n->children[n->child_count++] = parse_expression(p);
                } while (parser_peek(p).type == TOK_COMMA && (parser_advance(p), 1));
            }
            parser_expect(p, TOK_RPAREN);
            n->line = tok.line;
            return n;
        }
        // Built-in functions
        if (strcmp(tok.text, "LEN") == 0 && parser_peek(p).type == TOK_LPAREN) {
            parser_advance(p);
            ASTNode* n = ast_new(NODE_ARRAY_LEN);
            n->left = parse_expression(p);
            parser_expect(p, TOK_RPAREN);
            n->line = tok.line;
            return n;
        }
        if (strcmp(tok.text, "TYPEOF") == 0 && parser_peek(p).type == TOK_LPAREN) {
            parser_advance(p);
            ASTNode* n = ast_new(NODE_TYPEOF);
            n->left = parse_expression(p);
            parser_expect(p, TOK_RPAREN);
            n->line = tok.line;
            return n;
        }
        if (strcmp(tok.text, "TO_STRING") == 0 && parser_peek(p).type == TOK_LPAREN) {
            parser_advance(p);
            ASTNode* n = ast_new(NODE_TOSTR);
            n->left = parse_expression(p);
            parser_expect(p, TOK_RPAREN);
            n->line = tok.line;
            return n;
        }
        if (strcmp(tok.text, "TO_NUMBER") == 0 && parser_peek(p).type == TOK_LPAREN) {
            parser_advance(p);
            ASTNode* n = ast_new(NODE_TONUM);
            n->left = parse_expression(p);
            parser_expect(p, TOK_RPAREN);
            n->line = tok.line;
            return n;
        }
        ASTNode* n = ast_new(NODE_IDENT);
        strcpy(n->str_val, tok.text);
        n->line = tok.line;
        return n;
    }

    if (tok.type == TOK_LPAREN) {
        parser_advance(p);
        ASTNode* expr = parse_expression(p);
        parser_expect(p, TOK_RPAREN);
        return expr;
    }

    if (tok.type == TOK_LBRACKET) {
        parser_advance(p);
        ASTNode* n = ast_new(NODE_ARRAY_LIT);
        n->children = NULL;
        n->child_count = 0;
        int cap = 8;
        n->children = (ASTNode**)malloc(cap * sizeof(ASTNode*));
        if (parser_peek(p).type != TOK_RBRACKET) {
            do {
                if (n->child_count >= cap) {
                    cap *= 2;
                    n->children = (ASTNode**)realloc(n->children, cap * sizeof(ASTNode*));
                }
                n->children[n->child_count++] = parse_expression(p);
            } while (parser_peek(p).type == TOK_COMMA && (parser_advance(p), 1));
        }
        parser_expect(p, TOK_RBRACKET);
        n->line = tok.line;
        return n;
    }

    if (tok.type == TOK_MINUS) {
        parser_advance(p);
        ASTNode* n = ast_new(NODE_UNARY);
        strcpy(n->op, "-");
        n->left = parse_primary(p);
        n->line = tok.line;
        return n;
    }

    if (tok.type == TOK_NOT) {
        parser_advance(p);
        ASTNode* n = ast_new(NODE_UNARY);
        strcpy(n->op, "NOT");
        n->left = parse_primary(p);
        n->line = tok.line;
        return n;
    }

    parser_error(p, "Unexpected NbsToken in expression", tok.line);
    parser_advance(p);
    return ast_new(NODE_INT);
}

ASTNode* parse_expression_bp(Parser* p, int min_prec) {
    ASTNode* left = parse_primary(p);

    while (get_precedence(parser_peek(p).type) >= min_prec) {
        NbsToken op = parser_advance(p);
        int prec = get_precedence(op.type);
        ASTNode* right = parse_expression_bp(p, prec + 1);

        ASTNode* bin = ast_new(NODE_BINARY);
        strcpy(bin->op, op.text);
        bin->left = left;
        bin->right = right;
        bin->line = op.line;
        left = bin;
    }

    return left;
}

ASTNode* parse_expression(Parser* p) {
    return parse_expression_bp(p, 1);
}

// Statement parsing
ASTNode* parse_statement(Parser* p);
ASTNode* parse_block(Parser* p);

ASTNode* parse_block(Parser* p) {
    ASTNode* block = ast_new(NODE_BLOCK);
    int cap = 16;
    block->children = (ASTNode**)malloc(cap * sizeof(ASTNode*));
    block->child_count = 0;

    while (parser_peek(p).type != TOK_END && parser_peek(p).type != TOK_EOF &&
           parser_peek(p).type != TOK_ELSE && parser_peek(p).type != TOK_ELSEIF &&
           parser_peek(p).type != TOK_CATCH && parser_peek(p).type != TOK_FINALLY &&
           parser_peek(p).type != TOK_ENDTRY) {
        if (block->child_count >= cap) {
            cap *= 2;
            block->children = (ASTNode**)realloc(block->children, cap * sizeof(ASTNode*));
        }
        block->children[block->child_count++] = parse_statement(p);
    }
    return block;
}

ASTNode* parse_statement(Parser* p) {
    NbsToken tok = parser_peek(p);

    // PRINT expr
    if (tok.type == TOK_PRINT) {
        parser_advance(p);
        ASTNode* n = ast_new(NODE_PRINT);
        n->left = parse_expression(p);
        n->line = tok.line;
        return n;
    }

    // LET ident = expr  or  ident = expr
    if (tok.type == TOK_LET || tok.type == TOK_CONST ||
        (tok.type == TOK_IDENT && p->pos + 1 < p->count && p->tokens[p->pos + 1].type == TOK_ASSIGN)) {
        if (tok.type == TOK_LET || tok.type == TOK_CONST) parser_advance(p);
        NbsToken name = parser_expect(p, TOK_IDENT);
        parser_expect(p, TOK_ASSIGN);
        ASTNode* n = ast_new(NODE_ASSIGN);
        strcpy(n->str_val, name.text);
        n->right = parse_expression(p);
        n->line = tok.line;
        return n;
    }

    // IF? expr THEN: block (ELSEIF? expr: block)* (ELSE: block) END!
    if (tok.type == TOK_IF) {
        parser_advance(p);
        ASTNode* root = ast_new(NODE_IF);
        ASTNode* current = root;
        root->left = parse_expression(p);
        if (parser_peek(p).type == TOK_THEN) parser_advance(p);
        parser_expect(p, TOK_COLON);
        root->right = parse_block(p);
        // Handle ELSEIF? chains: each ELSEIF becomes a nested IF in the third branch
        while (parser_peek(p).type == TOK_ELSEIF) {
            parser_advance(p);
            ASTNode* elseif = ast_new(NODE_IF);
            elseif->left = parse_expression(p);
            if (parser_peek(p).type == TOK_THEN) parser_advance(p);
            parser_expect(p, TOK_COLON);
            elseif->right = parse_block(p);
            current->third = elseif;
            current = elseif;
        }
        if (parser_peek(p).type == TOK_ELSE) {
            parser_advance(p);
            if (parser_peek(p).type == TOK_COLON) parser_advance(p);
            current->third = parse_block(p);
        }
        parser_expect(p, TOK_END);
        root->line = tok.line;
        return root;
    }

    // WHILE? expr: block END!
    if (tok.type == TOK_WHILE) {
        parser_advance(p);
        ASTNode* n = ast_new(NODE_WHILE);
        n->left = parse_expression(p);
        if (parser_peek(p).type == TOK_THEN) parser_advance(p); // skip optional THEN
        parser_expect(p, TOK_COLON);
        n->right = parse_block(p);
        parser_expect(p, TOK_END);
        n->line = tok.line;
        return n;
    }

    // FOR! var = start TO end (STEP step): block END!
    if (tok.type == TOK_FOR) {
        parser_advance(p);
        NbsToken var = parser_expect(p, TOK_IDENT);
        parser_expect(p, TOK_ASSIGN);
        ASTNode* start = parse_expression(p);
        parser_expect(p, TOK_TO);
        ASTNode* end = parse_expression(p);
        ASTNode* step = NULL;
        if (parser_peek(p).type == TOK_STEP) {
            parser_advance(p);
            step = parse_expression(p);
        }
        parser_expect(p, TOK_COLON);
        ASTNode* body = parse_block(p);
        parser_expect(p, TOK_END);

        ASTNode* n = ast_new(NODE_FOR);
        strcpy(n->str_val, var.text);
        ASTNode* range = ast_new(NODE_BINARY);
        strcpy(range->op, "TO");
        range->left = start;
        range->right = end;
        if (step) {
            ASTNode* stepnode = ast_new(NODE_BINARY);
            strcpy(stepnode->op, "STEP");
            stepnode->left = range;
            stepnode->right = step;
            n->left = stepnode;
        } else {
            n->left = range;
        }
        n->right = body;
        n->line = tok.line;
        return n;
    }

    // FUNC! name param1 param2: block END!
    if (tok.type == TOK_FUNC) {
        parser_advance(p);
        NbsToken name = parser_expect(p, TOK_IDENT);
        ASTNode* n = ast_new(NODE_FUNC_DEF);
        strcpy(n->str_val, name.text);
        n->param_count = 0;
        // Collect parameter names until colon
        while (parser_peek(p).type != TOK_COLON && parser_peek(p).type != TOK_EOF) {
            NbsToken param = parser_advance(p);
            if (param.type == TOK_IDENT) {
                strcpy(n->params[n->param_count++], param.text);
            }
        }
        parser_expect(p, TOK_COLON);
        ASTNode* body = parse_block(p);
        parser_expect(p, TOK_END);
        n->right = body;
        n->line = tok.line;
        return n;
    }

    // RETURN expr
    if (tok.type == TOK_RETURN) {
        parser_advance(p);
        ASTNode* n = ast_new(NODE_RETURN);
        if (parser_peek(p).type != TOK_END && parser_peek(p).type != TOK_EOF &&
            parser_peek(p).type != TOK_ELSE && parser_peek(p).type != TOK_ELSEIF) {
            n->left = parse_expression(p);
        }
        n->line = tok.line;
        return n;
    }

    if (tok.type == TOK_BREAK) { parser_advance(p); ASTNode* n = ast_new(NODE_BREAK); n->line = tok.line; return n; }
    if (tok.type == TOK_CONTINUE) { parser_advance(p); ASTNode* n = ast_new(NODE_CONTINUE); n->line = tok.line; return n; }

    // THROW expr
    if (tok.type == TOK_THROW) {
        parser_advance(p);
        ASTNode* n = ast_new(NODE_THROW);
        n->left = parse_expression(p);
        n->line = tok.line;
        return n;
    }

    // TRY!: block CATCH! var: block (FINALLY!: block)? ENDTRY!
    if (tok.type == TOK_TRY) {
        parser_advance(p);
        if (parser_peek(p).type == TOK_COLON) parser_advance(p);
        ASTNode* n = ast_new(NODE_TRY);
        n->right = parse_block(p);  // try block
        if (parser_peek(p).type == TOK_CATCH) {
            parser_advance(p);
            NbsToken errvar = parser_peek(p);
            if (errvar.type == TOK_IDENT) {
                parser_advance(p);
                strcpy(n->str_val, errvar.text);  // error variable name
            }
            if (parser_peek(p).type == TOK_COLON) parser_advance(p);
            n->third = parse_block(p);  // catch block
        }
        if (parser_peek(p).type == TOK_FINALLY) {
            parser_advance(p);
            if (parser_peek(p).type == TOK_COLON) parser_advance(p);
            // finally block — we append it to catch block for simplicity
            ASTNode* finally_block = parse_block(p);
            if (n->third) {
                // Append finally statements to catch block
                ASTNode* catch_blk = n->third;
                for (int i = 0; i < finally_block->child_count; i++) {
                    if (catch_blk->child_count >= 16) break;
                    catch_blk->children[catch_blk->child_count++] = finally_block->children[i];
                }
            } else {
                n->third = finally_block;
            }
        }
        parser_expect(p, TOK_ENDTRY);
        n->line = tok.line;
        return n;
    }

    // IMPORT "path"
    if (tok.type == TOK_IMPORT) {
        parser_advance(p);
        NbsToken path = parser_expect(p, TOK_STRING_LIT);
        ASTNode* n = ast_new(NODE_IMPORT);
        strcpy(n->str_val, path.text);
        n->line = tok.line;
        return n;
    }

    // Expression statement (may be array assignment: arr[i] = expr)
    ASTNode* expr = parse_expression(p);
    // Check for array assignment: expr[i] = value
    if (expr->type == NODE_ARRAY_INDEX && parser_peek(p).type == TOK_ASSIGN) {
        parser_advance(p);
        ASTNode* n = ast_new(NODE_ARRAY_ASSIGN);
        n->left = expr;   // NODE_ARRAY_INDEX (left=array, right=index)
        n->right = parse_expression(p);
        n->line = tok.line;
        return n;
    }
    return expr;
}

ASTNode* parse_program(Parser* p) {
    ASTNode* prog = ast_new(NODE_PROGRAM);
    int cap = 64;
    prog->children = (ASTNode**)malloc(cap * sizeof(ASTNode*));
    prog->child_count = 0;

    while (parser_peek(p).type != TOK_EOF) {
        if (prog->child_count >= cap) {
            cap *= 2;
            prog->children = (ASTNode**)realloc(prog->children, cap * sizeof(ASTNode*));
        }
        prog->children[prog->child_count++] = parse_statement(p);
    }
    return prog;
}

// ============================================================================
// BYTECODE COMPILER
// ============================================================================

typedef enum {
    BC_PUSH_INT, BC_PUSH_STR, BC_PUSH_BOOL, BC_PUSH_NULL,
    BC_POP, BC_DUP, BC_SWAP,
    BC_ADD, BC_SUB, BC_MUL, BC_DIV, BC_MOD, BC_NEG,
    BC_EQ, BC_NEQ, BC_LT, BC_GT, BC_LTE, BC_GTE,
    BC_AND, BC_OR, BC_NOT,
    BC_BITAND, BC_BITOR, BC_LSHIFT, BC_RSHIFT,
    BC_STORE, BC_LOAD,
    BC_JUMP, BC_JUMP_IF, BC_JUMP_IFNOT,
    BC_CALL, BC_RET,
    BC_PRINT, BC_ARRAY_NEW, BC_ARRAY_GET, BC_ARRAY_SET, BC_ARRAY_LEN, BC_ARRAY_PUSH, BC_ARRAY_POP,
    BC_LEN, BC_TYPEOF, BC_TOSTR, BC_TONUM,
    BC_TRY, BC_CATCH, BC_THROW, BC_ENDTRY, BC_IMPORT,
    BC_HALT
} BCOp;

typedef struct {
    uint8_t* code;
    int pos, cap;
} BytecodeBuf;

void bc_init(BytecodeBuf* b) {
    b->cap = 65536;
    b->code = (uint8_t*)malloc(b->cap);
    b->pos = 0;
}

void bc_emit(BytecodeBuf* b, uint8_t byte) {
    if (b->pos >= b->cap) {
        b->cap *= 2;
        b->code = (uint8_t*)realloc(b->code, b->cap);
    }
    b->code[b->pos++] = byte;
}

void bc_emit_i64(BytecodeBuf* b, int64_t v) {
    for (int i = 0; i < 8; i++) bc_emit(b, (v >> (i * 8)) & 0xFF);
}

void bc_emit_i32(BytecodeBuf* b, int32_t v) {
    for (int i = 0; i < 4; i++) bc_emit(b, (v >> (i * 8)) & 0xFF);
}

int bc_patch(BytecodeBuf* b, int addr) {
    int offset = b->pos - addr - 4;
    b->code[addr] = offset & 0xFF;
    b->code[addr + 1] = (offset >> 8) & 0xFF;
    b->code[addr + 2] = (offset >> 16) & 0xFF;
    b->code[addr + 3] = (offset >> 24) & 0xFF;
    return offset;
}

// String table
typedef struct {
    char** strings;
    int count, cap;
} StringTable;

void st_init(StringTable* st) {
    st->cap = 256;
    st->strings = (char**)malloc(st->cap * sizeof(char*));
    st->count = 0;
}

int st_intern(StringTable* st, const char* s) {
    for (int i = 0; i < st->count; i++)
        if (strcmp(st->strings[i], s) == 0) return i;
    if (st->count >= st->cap) {
        st->cap *= 2;
        st->strings = (char**)realloc(st->strings, st->cap * sizeof(char*));
    }
    st->strings[st->count] = strdup(s);
    return st->count++;
}

// Function table
typedef struct {
    char name[128];
    int addr;
    int arity;
    char params[8][128];
    int param_count;
    uint8_t *code;
} FuncEntry;

typedef struct {
    FuncEntry* entries;
    int count, cap;
} FuncTable;

void ft_init(FuncTable* ft) {
    ft->cap = 64;
    ft->entries = (FuncEntry*)malloc(ft->cap * sizeof(FuncEntry));
    ft->count = 0;
}

int ft_add(FuncTable* ft, const char* name, int addr, char params[][128], int param_count, uint8_t *code) {
    if (ft->count >= ft->cap) {
        ft->cap *= 2;
        ft->entries = (FuncEntry*)realloc(ft->entries, ft->cap * sizeof(FuncEntry));
    }
    FuncEntry* e = &ft->entries[ft->count];
    strcpy(e->name, name);
    e->addr = addr;
    e->arity = param_count;
    e->param_count = param_count;
    for (int i = 0; i < param_count; i++) strcpy(e->params[i], params[i]);
    e->code = code;
    return ft->count++;
}

int ft_find(FuncTable* ft, const char* name) {
    for (int i = 0; i < ft->count; i++)
        if (strcmp(ft->entries[i].name, name) == 0) return i;
    return -1;
}

// Loop break/continue patch stack
typedef struct { int break_patches[64]; int break_count; int continue_patches[64]; int continue_count; int continue_ip; } LoopInfo;
static LoopInfo loop_stack[64];
static int loop_sp = 0;

// Compiler state
typedef struct {
    BytecodeBuf* bc;
    StringTable* strings;
    FuncTable* funcs;
} Compiler;

void compile_node(Compiler* c, ASTNode* node) {
    if (!node) return;

    switch (node->type) {
        case NODE_INT:
            bc_emit(c->bc, BC_PUSH_INT);
            bc_emit_i64(c->bc, node->int_val);
            break;

        case NODE_TRUE:
            bc_emit(c->bc, BC_PUSH_BOOL);
            bc_emit(c->bc, 1);
            break;

        case NODE_FALSE:
            bc_emit(c->bc, BC_PUSH_BOOL);
            bc_emit(c->bc, 0);
            break;

        case NODE_NULL:
            bc_emit(c->bc, BC_PUSH_NULL);
            break;

        case NODE_STRING: {
            bc_emit(c->bc, BC_PUSH_STR);
            int idx = st_intern(c->strings, node->str_val);
            bc_emit_i32(c->bc, idx);
        } break;

        case NODE_IDENT:
            bc_emit(c->bc, BC_LOAD);
            bc_emit_i32(c->bc, st_intern(c->strings, node->str_val));
            break;

        case NODE_BINARY:
            compile_node(c, node->left);
            compile_node(c, node->right);
            if (strcmp(node->op, "+") == 0) bc_emit(c->bc, BC_ADD);
            else if (strcmp(node->op, "-") == 0) bc_emit(c->bc, BC_SUB);
            else if (strcmp(node->op, "*") == 0) bc_emit(c->bc, BC_MUL);
            else if (strcmp(node->op, "/") == 0) bc_emit(c->bc, BC_DIV);
            else if (strcmp(node->op, "%") == 0) bc_emit(c->bc, BC_MOD);
            else if (strcmp(node->op, "==") == 0) bc_emit(c->bc, BC_EQ);
            else if (strcmp(node->op, "!=") == 0) bc_emit(c->bc, BC_NEQ);
            else if (strcmp(node->op, "<") == 0) bc_emit(c->bc, BC_LT);
            else if (strcmp(node->op, ">") == 0) bc_emit(c->bc, BC_GT);
            else if (strcmp(node->op, "<=") == 0) bc_emit(c->bc, BC_LTE);
            else if (strcmp(node->op, ">=") == 0) bc_emit(c->bc, BC_GTE);
            else if (strcmp(node->op, "AND") == 0) bc_emit(c->bc, BC_AND);
            else if (strcmp(node->op, "OR") == 0) bc_emit(c->bc, BC_OR);
            else if (strcmp(node->op, "&") == 0) bc_emit(c->bc, BC_BITAND);
            else if (strcmp(node->op, "|") == 0) bc_emit(c->bc, BC_BITOR);
            else if (strcmp(node->op, "<<") == 0) bc_emit(c->bc, BC_LSHIFT);
            else if (strcmp(node->op, ">>") == 0) bc_emit(c->bc, BC_RSHIFT);
            break;

        case NODE_UNARY:
            compile_node(c, node->left);
            if (strcmp(node->op, "-") == 0) bc_emit(c->bc, BC_NEG);
            else if (strcmp(node->op, "NOT") == 0) bc_emit(c->bc, BC_NOT);
            break;

        case NODE_ASSIGN:
            compile_node(c, node->right);
            bc_emit(c->bc, BC_STORE);
            bc_emit_i32(c->bc, st_intern(c->strings, node->str_val));
            break;

        case NODE_PRINT:
            compile_node(c, node->left);
            bc_emit(c->bc, BC_PRINT);
            break;

        case NODE_IF:
            compile_node(c, node->left);
            bc_emit(c->bc, BC_JUMP_IFNOT);
            int patch1 = c->bc->pos;
            bc_emit_i32(c->bc, 0);
            compile_node(c, node->right);
            if (node->third) {
                bc_emit(c->bc, BC_JUMP);
                int patch2 = c->bc->pos;
                bc_emit_i32(c->bc, 0);
                bc_patch(c->bc, patch1);
                compile_node(c, node->third);
                bc_patch(c->bc, patch2);
            } else {
                bc_patch(c->bc, patch1);
            }
            break;

        case NODE_WHILE: {
            int loop_start = c->bc->pos;
            // Push loop info for BREAK/CONTINUE
            loop_stack[loop_sp].break_count = 0;
            loop_stack[loop_sp].continue_count = 0;
            loop_sp++;
            compile_node(c, node->left);
            bc_emit(c->bc, BC_JUMP_IFNOT);
            int patch1 = c->bc->pos;
            bc_emit_i32(c->bc, 0);
            compile_node(c, node->right);
            bc_emit(c->bc, BC_JUMP);
            bc_emit_i32(c->bc, loop_start - (c->bc->pos + 4));
            bc_patch(c->bc, patch1);
            // Patch all BREAK jumps to here
            loop_sp--;
            for (int bi = 0; bi < loop_stack[loop_sp].break_count; bi++) {
                int pa = loop_stack[loop_sp].break_patches[bi];
                int32_t o = c->bc->pos - pa - 4;
                c->bc->code[pa] = o & 0xFF;
                c->bc->code[pa+1] = (o >> 8) & 0xFF;
                c->bc->code[pa+2] = (o >> 16) & 0xFF;
                c->bc->code[pa+3] = (o >> 24) & 0xFF;
            }
            // Patch all CONTINUE jumps to loop start
            for (int ci = 0; ci < loop_stack[loop_sp].continue_count; ci++) {
                int pa = loop_stack[loop_sp].continue_patches[ci];
                int32_t o = loop_start - pa - 4;
                c->bc->code[pa] = o & 0xFF;
                c->bc->code[pa+1] = (o >> 8) & 0xFF;
                c->bc->code[pa+2] = (o >> 16) & 0xFF;
                c->bc->code[pa+3] = (o >> 24) & 0xFF;
            }
        } break;

        case NODE_FOR: {
            // Init
            ASTNode* range = node->left;
            ASTNode* start = range->left;
            ASTNode* end = range->right;
            ASTNode* step = NULL;
            // Check for STEP node
            if (range->type == NODE_BINARY && strcmp(range->op, "STEP") == 0) {
                start = range->left->left;
                end = range->left->right;
                step = range->right;
            }
            compile_node(c, start);
            bc_emit(c->bc, BC_STORE);
            bc_emit_i32(c->bc, st_intern(c->strings, node->str_val));

            // Condition
            int loop_start = c->bc->pos;
            bc_emit(c->bc, BC_LOAD);
            bc_emit_i32(c->bc, st_intern(c->strings, node->str_val));
            compile_node(c, end);
            bc_emit(c->bc, BC_LTE);
            bc_emit(c->bc, BC_JUMP_IFNOT);
            int patch1 = c->bc->pos;
            bc_emit_i32(c->bc, 0);

            // Body
            loop_stack[loop_sp].break_count = 0;
            loop_stack[loop_sp].continue_count = 0;
            loop_sp++;
            compile_node(c, node->right);
            // Record increment position for CONTINUE patching
            int increment_pos = c->bc->pos;

            // Increment
            bc_emit(c->bc, BC_LOAD);
            bc_emit_i32(c->bc, st_intern(c->strings, node->str_val));
            if (step) {
                compile_node(c, step);
            } else {
                bc_emit(c->bc, BC_PUSH_INT);
                bc_emit_i64(c->bc, 1);
            }
            bc_emit(c->bc, BC_ADD);
            bc_emit(c->bc, BC_STORE);
            bc_emit_i32(c->bc, st_intern(c->strings, node->str_val));

            bc_emit(c->bc, BC_JUMP);
            bc_emit_i32(c->bc, loop_start - (c->bc->pos + 4));
            bc_patch(c->bc, patch1);
            // Patch all BREAK jumps to here (end of loop)
            loop_sp--;
            for (int bi = 0; bi < loop_stack[loop_sp].break_count; bi++) {
                int pa = loop_stack[loop_sp].break_patches[bi];
                int32_t o = c->bc->pos - pa - 4;
                c->bc->code[pa] = o & 0xFF;
                c->bc->code[pa+1] = (o >> 8) & 0xFF;
                c->bc->code[pa+2] = (o >> 16) & 0xFF;
                c->bc->code[pa+3] = (o >> 24) & 0xFF;
            }
            // Patch all CONTINUE jumps to increment step
            for (int ci = 0; ci < loop_stack[loop_sp].continue_count; ci++) {
                int pa = loop_stack[loop_sp].continue_patches[ci];
                int32_t o = increment_pos - pa - 4;
                c->bc->code[pa] = o & 0xFF;
                c->bc->code[pa+1] = (o >> 8) & 0xFF;
                c->bc->code[pa+2] = (o >> 16) & 0xFF;
                c->bc->code[pa+3] = (o >> 24) & 0xFF;
            }
        } break;

        case NODE_FUNC_DEF: {
            // Skip over the JUMP at runtime
            bc_emit(c->bc, BC_JUMP);
            int skip_patch = c->bc->pos;
            bc_emit_i32(c->bc, 0);
            // Function body starts here — record address AFTER the jump
            int func_idx = ft_add(c->funcs, node->str_val, c->bc->pos, node->params, node->param_count);
            compile_node(c, node->right);
            bc_emit(c->bc, BC_PUSH_NULL);
            bc_emit(c->bc, BC_RET);
            bc_patch(c->bc, skip_patch);
            (void)func_idx;
        } break;

        case NODE_FUNC_CALL: {
            // Special-case PUSH(arr, val) and POP(arr) for in-place mutation
            if (strcmp(node->str_val, "PUSH") == 0 && node->child_count == 2 &&
                node->children[0]->type == NODE_IDENT) {
                // PUSH(arr, val): load arr, load val, BC_ARRAY_PUSH, DUP, STORE arr
                compile_node(c, node->children[0]);  // LOAD arr
                compile_node(c, node->children[1]);  // LOAD val
                bc_emit(c->bc, BC_ARRAY_PUSH);
                bc_emit(c->bc, BC_DUP);
                bc_emit(c->bc, BC_STORE);
                bc_emit_i32(c->bc, st_intern(c->strings, node->children[0]->str_val));
                break;
            }
            if (strcmp(node->str_val, "POP") == 0 && node->child_count == 1 &&
                node->children[0]->type == NODE_IDENT) {
                // POP(arr): BC_ARRAY_POP pushes [modified_arr, popped_val]
                // SWAP → [popped_val, modified_arr] → STORE arr → [popped_val]
                compile_node(c, node->children[0]);  // LOAD arr
                bc_emit(c->bc, BC_ARRAY_POP);        // pushes modified_arr, then popped_val
                bc_emit(c->bc, BC_SWAP);             // → [popped_val, modified_arr]
                bc_emit(c->bc, BC_STORE);            // stores modified_arr → arr
                bc_emit_i32(c->bc, st_intern(c->strings, node->children[0]->str_val));
                // stack now has [popped_val]
                break;
            }
            // Push args in reverse
            for (int i = node->child_count - 1; i >= 0; i--)
                compile_node(c, node->children[i]);
            bc_emit(c->bc, BC_CALL);
            bc_emit_i32(c->bc, st_intern(c->strings, node->str_val));
            bc_emit_i32(c->bc, node->child_count);
        } break;

        case NODE_RETURN:
            if (node->left) compile_node(c, node->left);
            else { bc_emit(c->bc, BC_PUSH_NULL); }
            bc_emit(c->bc, BC_RET);
            break;

        case NODE_BREAK:
            bc_emit(c->bc, BC_JUMP);
            if (loop_sp > 0) {
                LoopInfo* li = &loop_stack[loop_sp - 1];
                if (li->break_count < 64)
                    li->break_patches[li->break_count++] = c->bc->pos;
            }
            bc_emit_i32(c->bc, 0); // patched later
            break;

        case NODE_CONTINUE:
            bc_emit(c->bc, BC_JUMP);
            if (loop_sp > 0) {
                LoopInfo* li = &loop_stack[loop_sp - 1];
                if (li->continue_count < 64)
                    li->continue_patches[li->continue_count++] = c->bc->pos;
            }
            bc_emit_i32(c->bc, 0); // patched later
            break;

        case NODE_ARRAY_ASSIGN:
            // node->left is NODE_ARRAY_INDEX (left=array ident, right=index)
            // node->right is value expression
            // We need to: load array, load index, load value, BC_ARRAY_SET, store back
            {
                ASTNode* arr_idx = node->left;
                ASTNode* arr_ident = arr_idx->left;
                if (arr_ident->type == NODE_IDENT) {
                    compile_node(c, arr_ident);       // push array (deep copy)
                    compile_node(c, arr_idx->right);  // push index
                    compile_node(c, node->right);     // push value
                    bc_emit(c->bc, BC_ARRAY_SET);
                    bc_emit(c->bc, BC_STORE);
                    bc_emit_i32(c->bc, st_intern(c->strings, arr_ident->str_val));
                }
            }
            break;

        case NODE_TRY: {
            bc_emit(c->bc, BC_TRY);
            int try_patch = c->bc->pos;
            bc_emit_i32(c->bc, 0);
            compile_node(c, node->right);  // try block
            bc_emit(c->bc, BC_ENDTRY);
            bc_emit(c->bc, BC_JUMP);
            int catch_patch = c->bc->pos;
            bc_emit_i32(c->bc, 0);
            bc_patch(c->bc, try_patch);
            if (node->third) {
                // Store error into catch variable if specified
                if (node->str_val[0]) {
                    // Load error from stack (pushed by BC_THROW handler)
                    // Actually, for simplicity: CATCH block just runs, error is in str_val variable
                    bc_emit(c->bc, BC_STORE);
                    bc_emit_i32(c->bc, st_intern(c->strings, node->str_val));
                }
                compile_node(c, node->third);  // catch block
            }
            bc_patch(c->bc, catch_patch);
        } break;

        case NODE_THROW:
            compile_node(c, node->left);
            bc_emit(c->bc, BC_THROW);
            break;

        case NODE_IMPORT: {
            bc_emit(c->bc, BC_IMPORT);
            int idx = st_intern(c->strings, node->str_val);
            bc_emit_i32(c->bc, idx);
        } break;

        case NODE_ARRAY_LIT:
            for (int i = 0; i < node->child_count; i++)
                compile_node(c, node->children[i]);
            bc_emit(c->bc, BC_ARRAY_NEW);
            bc_emit_i32(c->bc, node->child_count);
            break;

        case NODE_ARRAY_INDEX:
            compile_node(c, node->left);
            compile_node(c, node->right);
            bc_emit(c->bc, BC_ARRAY_GET);
            break;

        case NODE_ARRAY_LEN:
            compile_node(c, node->left);
            bc_emit(c->bc, BC_ARRAY_LEN);
            break;

        case NODE_TYPEOF:
            compile_node(c, node->left);
            bc_emit(c->bc, BC_TYPEOF);
            break;

        case NODE_TOSTR:
            compile_node(c, node->left);
            bc_emit(c->bc, BC_TOSTR);
            break;

        case NODE_TONUM:
            compile_node(c, node->left);
            bc_emit(c->bc, BC_TONUM);
            break;

        case NODE_BLOCK:
            for (int i = 0; i < node->child_count; i++)
                compile_node(c, node->children[i]);
            break;

        case NODE_PROGRAM:
            for (int i = 0; i < node->child_count; i++)
                compile_node(c, node->children[i]);
            bc_emit(c->bc, BC_HALT);
            break;

        default: break;
    }
}

// ============================================================================
// VM EXECUTION
// ============================================================================

typedef struct {
    Value stack[8192];
    int sp;
    Value vars[1024];   // global variables (indexed by string table)
    uint8_t* code;
    int ip;
    int running;
    StringTable* strings;
    FuncTable* funcs;
    int debug;

    // Call stack with variable save/restore for recursion
    struct {
        int ret_ip;
        int saved_var_idx[256];
        Value saved_vars[256];
        int saved_count;
    } call_stack[256];
    int call_sp;

    // Try/catch stack
    struct {
        int handler_ip;
        int saved_sp;
    } try_stack[64];
    int try_sp;

    int code_len;
    char imported[64][256];
    int imported_count;
    uint8_t* imported_bcs[64];
    int imported_bc_count;
} VM;

void vm_init(VM* vm, uint8_t* code, StringTable* strings, FuncTable* funcs) {
    memset(vm, 0, sizeof(VM));
    vm->code = code;
    vm->strings = strings;
    vm->funcs = funcs;
    vm->running = 1;
    for (int i = 0; i < 1024; i++) vm->vars[i] = val_null();
}

int vm_run(VM* vm, uint8_t* code, int code_len);

static void vm_exec_import(VM* vm, const char* source, const char* path) {
    for (int i = 0; i < vm->imported_count; i++) {
        if (strcmp(vm->imported[i], path) == 0) return;
    }
    if (vm->imported_count < 64) {
        strncpy(vm->imported[vm->imported_count], path, 255);
        vm->imported[vm->imported_count][255] = 0;
        vm->imported_count++;
    }

    Lexer lexer = lexer_new(source);
    Parser *parser = (Parser*)calloc(1, sizeof(Parser));
    while (1) {
        NbsToken tok = lexer_next(&lexer);
        if (parser->count >= 4096) {
            fprintf(stderr, "Import error: too many tokens in '%s'\n", path);
            free(parser);
            return;
        }
        parser->tokens[parser->count++] = tok;
        if (tok.type == TOK_EOF) break;
    }

    ASTNode* ast = parse_program(parser);
    if (parser->has_error) {
        fprintf(stderr, "Import error in '%s': %s\n", path, parser->error_msg);
        free(parser);
        return;
    }
    free(parser);

    BytecodeBuf imported_bc;
    bc_init(&imported_bc);
    Compiler compiler = {&imported_bc, vm->strings, vm->funcs};
    compile_node(&compiler, ast);

    /* Execute imported code with recursive vm_run.
       Save/restore all VM state so the outer loop continues correctly. */
    int saved_sp = vm->sp;
    int saved_call_sp = vm->call_sp;
    int saved_ip = vm->ip;
    int saved_running = vm->running;
    uint8_t *saved_code = vm->code;

    vm_run(vm, imported_bc.code, imported_bc.pos);

    vm->sp = saved_sp;
    vm->call_sp = saved_call_sp;
    vm->code = saved_code;
    vm->ip = saved_ip;
    vm->running = saved_running;

    if (vm->imported_bc_count < 64)
        vm->imported_bcs[vm->imported_bc_count++] = imported_bc.code;
    else
        free(imported_bc.code);
}

int vm_run(VM* vm, uint8_t* code, int code_len) {
    vm->code = code;
    vm->ip = 0;
    while (vm->running && vm->ip < code_len) {
        uint8_t op = vm->code[vm->ip];
        if (vm->debug) fprintf(stderr, "IP=%d OP=0x%02X SP=%d\n", vm->ip, op, vm->sp);
        vm->ip++;

        switch (op) {
            case BC_HALT:
                vm->running = 0;
                break;

            case BC_PUSH_INT: {
                int64_t v;
                memcpy(&v, vm->code + vm->ip, 8);
                vm->ip += 8;
                vm->stack[vm->sp++] = val_int(v);
            } break;

            case BC_PUSH_STR: {
                int32_t idx;
                memcpy(&idx, vm->code + vm->ip, 4);
                vm->ip += 4;
                vm->stack[vm->sp++] = val_string(vm->strings->strings[idx]);
            } break;

            case BC_PUSH_BOOL: {
                uint8_t b = vm->code[vm->ip++];
                vm->stack[vm->sp++] = val_bool(b);
            } break;

            case BC_PUSH_NULL:
                vm->stack[vm->sp++] = val_null();
                break;

            case BC_POP:
                val_free(vm->stack[--vm->sp]);
                break;

            case BC_DUP:
                vm->stack[vm->sp] = vm->stack[vm->sp - 1];
                vm->sp++;
                break;

            case BC_SWAP: {
                Value a = vm->stack[vm->sp - 2];
                Value b = vm->stack[vm->sp - 1];
                vm->stack[vm->sp - 2] = b;
                vm->stack[vm->sp - 1] = a;
            } break;

            case BC_ADD: {
                Value b = vm->stack[--vm->sp];
                Value a = vm->stack[--vm->sp];
                vm->stack[vm->sp++] = val_add(a, b);
                val_free(a); val_free(b);
            } break;

            case BC_SUB: {
                Value b = vm->stack[--vm->sp];
                Value a = vm->stack[--vm->sp];
                vm->stack[vm->sp++] = val_sub(a, b);
            } break;

            case BC_MUL: {
                Value b = vm->stack[--vm->sp];
                Value a = vm->stack[--vm->sp];
                vm->stack[vm->sp++] = val_mul(a, b);
            } break;

            case BC_DIV: {
                Value b = vm->stack[--vm->sp];
                Value a = vm->stack[--vm->sp];
                vm->stack[vm->sp++] = val_div(a, b);
            } break;

            case BC_MOD: {
                Value b = vm->stack[--vm->sp];
                Value a = vm->stack[--vm->sp];
                vm->stack[vm->sp++] = val_mod(a, b);
            } break;

            case BC_NEG: {
                Value a = vm->stack[--vm->sp];
                if (a.type == VAL_INT) vm->stack[vm->sp++] = val_int(-a.as.i);
                else vm->stack[vm->sp++] = val_null();
            } break;

            case BC_EQ: {
                Value b = vm->stack[--vm->sp];
                Value a = vm->stack[--vm->sp];
                vm->stack[vm->sp++] = val_bool(val_equals(a, b));
            } break;

            case BC_NEQ: {
                Value b = vm->stack[--vm->sp];
                Value a = vm->stack[--vm->sp];
                vm->stack[vm->sp++] = val_bool(!val_equals(a, b));
            } break;

            case BC_LT: {
                Value b = vm->stack[--vm->sp];
                Value a = vm->stack[--vm->sp];
                vm->stack[vm->sp++] = val_bool(val_less(a, b));
            } break;

            case BC_GT: {
                Value b = vm->stack[--vm->sp];
                Value a = vm->stack[--vm->sp];
                vm->stack[vm->sp++] = val_bool(val_greater(a, b));
            } break;

            case BC_LTE: {
                Value b = vm->stack[--vm->sp];
                Value a = vm->stack[--vm->sp];
                vm->stack[vm->sp++] = val_bool(val_less(a, b) || val_equals(a, b));
            } break;

            case BC_GTE: {
                Value b = vm->stack[--vm->sp];
                Value a = vm->stack[--vm->sp];
                vm->stack[vm->sp++] = val_bool(val_greater(a, b) || val_equals(a, b));
            } break;

            case BC_AND: {
                Value b = vm->stack[--vm->sp];
                Value a = vm->stack[--vm->sp];
                vm->stack[vm->sp++] = val_bool(val_is_truthy(a) && val_is_truthy(b));
            } break;

            case BC_OR: {
                Value b = vm->stack[--vm->sp];
                Value a = vm->stack[--vm->sp];
                vm->stack[vm->sp++] = val_bool(val_is_truthy(a) || val_is_truthy(b));
            } break;

            case BC_NOT: {
                Value a = vm->stack[--vm->sp];
                vm->stack[vm->sp++] = val_bool(!val_is_truthy(a));
            } break;

            case BC_BITAND: {
                Value b = vm->stack[--vm->sp];
                Value a = vm->stack[--vm->sp];
                vm->stack[vm->sp++] = val_int(a.as.i & b.as.i);
            } break;

            case BC_BITOR: {
                Value b = vm->stack[--vm->sp];
                Value a = vm->stack[--vm->sp];
                vm->stack[vm->sp++] = val_int(a.as.i | b.as.i);
            } break;

            case BC_LSHIFT: {
                Value b = vm->stack[--vm->sp];
                Value a = vm->stack[--vm->sp];
                vm->stack[vm->sp++] = val_int(a.as.i << (int)b.as.i);
            } break;

            case BC_RSHIFT: {
                Value b = vm->stack[--vm->sp];
                Value a = vm->stack[--vm->sp];
                vm->stack[vm->sp++] = val_int(a.as.i >> (int)b.as.i);
            } break;

            case BC_STORE: {
                int32_t idx;
                memcpy(&idx, vm->code + vm->ip, 4);
                vm->ip += 4;
                val_free(vm->vars[idx]);
                vm->vars[idx] = vm->stack[--vm->sp];
            } break;

            case BC_LOAD: {
                int32_t idx;
                memcpy(&idx, vm->code + vm->ip, 4);
                vm->ip += 4;
                Value v = vm->vars[idx];
                // Deep copy strings and arrays to avoid double-free
                if (v.type == VAL_STRING) vm->stack[vm->sp++] = val_string(v.as.s);
                else if (v.type == VAL_ARRAY) {
                    Value arr = val_array();
                    for (int i = 0; i < v.as.a->count; i++) {
                        if (arr.as.a->count >= arr.as.a->capacity) {
                            arr.as.a->capacity = arr.as.a->capacity ? arr.as.a->capacity * 2 : 8;
                            arr.as.a->items = (Value*)realloc(arr.as.a->items, arr.as.a->capacity * sizeof(Value));
                        }
                        // Deep copy each element
                        Value elem = v.as.a->items[i];
                        if (elem.type == VAL_STRING) arr.as.a->items[arr.as.a->count++] = val_string(elem.as.s);
                        else arr.as.a->items[arr.as.a->count++] = elem;
                    }
                    vm->stack[vm->sp++] = arr;
                } else {
                    vm->stack[vm->sp++] = v;
                }
            } break;

            case BC_JUMP: {
                int32_t offset;
                memcpy(&offset, vm->code + vm->ip, 4);
                vm->ip += 4;
                vm->ip += offset;
            } break;

            case BC_JUMP_IF: {
                int32_t offset;
                memcpy(&offset, vm->code + vm->ip, 4);
                vm->ip += 4;
                Value v = vm->stack[--vm->sp];
                if (val_is_truthy(v)) vm->ip += offset;
            } break;

            case BC_JUMP_IFNOT: {
                int32_t offset;
                memcpy(&offset, vm->code + vm->ip, 4);
                vm->ip += 4;
                Value v = vm->stack[--vm->sp];
                if (!val_is_truthy(v)) vm->ip += offset;
            } break;

            case BC_PRINT: {
                Value v = vm->stack[--vm->sp];
                Value s = val_to_string(v);
                printf("%s\n", s.as.s);
                val_free(s);
                val_free(v);
            } break;

            case BC_CALL: {
                int32_t name_idx;
                memcpy(&name_idx, vm->code + vm->ip, 4);
                vm->ip += 4;
                int32_t arity;
                memcpy(&arity, vm->code + vm->ip, 4);
                vm->ip += 4;

                const char* name = vm->strings->strings[name_idx];

                // Built-in functions
                if (strcmp(name, "LEN") == 0) {
                    Value v = vm->stack[--vm->sp];
                    if (v.type == VAL_STRING) {
                        int len = (int)strlen(v.as.s);
                        val_free(v);
                        vm->stack[vm->sp++] = val_int(len);
                    } else if (v.type == VAL_ARRAY) {
                        int len = v.as.a->count;
                        val_free(v);
                        vm->stack[vm->sp++] = val_int(len);
                    } else {
                        val_free(v);
                        vm->stack[vm->sp++] = val_int(0);
                    }
                } else if (strcmp(name, "TYPEOF") == 0) {
                    Value v = vm->stack[--vm->sp];
                    vm->stack[vm->sp++] = val_string(val_type_name(v));
                    val_free(v);
                } else if (strcmp(name, "TO_STRING") == 0) {
                    Value v = vm->stack[--vm->sp];
                    vm->stack[vm->sp++] = val_to_string(v);
                    val_free(v);
                } else if (strcmp(name, "TO_NUMBER") == 0) {
                    Value v = vm->stack[--vm->sp];
                    if (v.type == VAL_STRING) {
                        int64_t n = atoll(v.as.s);
                        val_free(v);
                        vm->stack[vm->sp++] = val_int(n);
                    } else if (v.type == VAL_INT) {
                        vm->stack[vm->sp++] = v;
                    } else {
                        val_free(v);
                        vm->stack[vm->sp++] = val_int(0);
                    }
                } else if (strcmp(name, "RANDOM") == 0) {
                    for (int i = 0; i < arity; i++) val_free(vm->stack[--vm->sp]);
                    vm->stack[vm->sp++] = val_int(rand() % 100);
                } else if (strcmp(name, "TIME") == 0) {
                    for (int i = 0; i < arity; i++) val_free(vm->stack[--vm->sp]);
                    vm->stack[vm->sp++] = val_int((int64_t)time(NULL));
                } else if (strcmp(name, "TO_UPPER") == 0) {
                    Value v = vm->stack[--vm->sp];
                    if (v.type == VAL_STRING) {
                        int len = strlen(v.as.s);
                        char* buf = (char*)malloc(len + 1);
                        for (int i = 0; i < len; i++) buf[i] = toupper((unsigned char)v.as.s[i]);
                        buf[len] = 0;
                        val_free(v);
                        vm->stack[vm->sp++] = val_string(buf);
                        free(buf);
                    } else { val_free(v); vm->stack[vm->sp++] = val_string(""); }
                } else if (strcmp(name, "TO_LOWER") == 0) {
                    Value v = vm->stack[--vm->sp];
                    if (v.type == VAL_STRING) {
                        int len = strlen(v.as.s);
                        char* buf = (char*)malloc(len + 1);
                        for (int i = 0; i < len; i++) buf[i] = tolower((unsigned char)v.as.s[i]);
                        buf[len] = 0;
                        val_free(v);
                        vm->stack[vm->sp++] = val_string(buf);
                        free(buf);
                    } else { val_free(v); vm->stack[vm->sp++] = val_string(""); }
                } else if (strcmp(name, "CHAR_AT") == 0) {
                    Value v = vm->stack[--vm->sp];
                    Value idx_val = vm->stack[--vm->sp];
                    if (v.type == VAL_STRING && idx_val.type == VAL_INT) {
                        int len = strlen(v.as.s);
                        if (idx_val.as.i >= 0 && idx_val.as.i < len) {
                            char ch[2] = { v.as.s[idx_val.as.i], 0 };
                            vm->stack[vm->sp++] = val_string(ch);
                        } else { vm->stack[vm->sp++] = val_null(); }
                    } else { vm->stack[vm->sp++] = val_null(); }
                    val_free(v); val_free(idx_val);
                } else if (strcmp(name, "SUBSTR") == 0) {
                    Value v = vm->stack[--vm->sp];
                    Value start_val = vm->stack[--vm->sp];
                    Value len_val = vm->stack[--vm->sp];
                    if (v.type == VAL_STRING && start_val.type == VAL_INT && len_val.type == VAL_INT) {
                        int slen = strlen(v.as.s);
                        int start = (int)start_val.as.i;
                        int len = (int)len_val.as.i;
                        if (start < 0) start = 0;
                        if (start >= slen) { vm->stack[vm->sp++] = val_string(""); }
                        else {
                            if (start + len > slen) len = slen - start;
                            char* buf = (char*)malloc(len + 1);
                            memcpy(buf, v.as.s + start, len);
                            buf[len] = 0;
                            vm->stack[vm->sp++] = val_string(buf);
                            free(buf);
                        }
                    } else { vm->stack[vm->sp++] = val_string(""); }
                    val_free(v); val_free(start_val); val_free(len_val);
                } else if (strcmp(name, "TRIM") == 0) {
                    Value v = vm->stack[--vm->sp];
                    if (v.type == VAL_STRING) {
                        const char* s = v.as.s;
                        while (*s == ' ' || *s == '\t' || *s == '\n' || *s == '\r') s++;
                        int len = strlen(s);
                        while (len > 0 && (s[len-1] == ' ' || s[len-1] == '\t' || s[len-1] == '\n' || s[len-1] == '\r')) len--;
                        char* buf = (char*)malloc(len + 1);
                        memcpy(buf, s, len);
                        buf[len] = 0;
                        val_free(v);
                        vm->stack[vm->sp++] = val_string(buf);
                        free(buf);
                    } else { val_free(v); vm->stack[vm->sp++] = val_string(""); }
                } else if (strcmp(name, "CHAR") == 0) {
                    Value v = vm->stack[--vm->sp];
                    if (v.type == VAL_INT) {
                        char ch[2] = { (char)v.as.i, 0 };
                        vm->stack[vm->sp++] = val_string(ch);
                    } else { vm->stack[vm->sp++] = val_string(""); val_free(v); }
                } else if (strcmp(name, "ORD") == 0) {
                    Value v = vm->stack[--vm->sp];
                    if (v.type == VAL_STRING && strlen(v.as.s) > 0) {
                        vm->stack[vm->sp++] = val_int((unsigned char)v.as.s[0]);
                    } else { vm->stack[vm->sp++] = val_int(0); val_free(v); }
                } else if (strcmp(name, "ABS") == 0) {
                    Value v = vm->stack[--vm->sp];
                    if (v.type == VAL_INT) vm->stack[vm->sp++] = val_int(v.as.i < 0 ? -v.as.i : v.as.i);
                    else { vm->stack[vm->sp++] = val_int(0); val_free(v); }
                } else if (strcmp(name, "MIN") == 0) {
                    Value b = vm->stack[--vm->sp]; Value a = vm->stack[--vm->sp];
                    if (a.type == VAL_INT && b.type == VAL_INT)
                        vm->stack[vm->sp++] = val_int(a.as.i < b.as.i ? a.as.i : b.as.i);
                    else vm->stack[vm->sp++] = val_int(0);
                    val_free(a); val_free(b);
                } else if (strcmp(name, "MAX") == 0) {
                    Value b = vm->stack[--vm->sp]; Value a = vm->stack[--vm->sp];
                    if (a.type == VAL_INT && b.type == VAL_INT)
                        vm->stack[vm->sp++] = val_int(a.as.i > b.as.i ? a.as.i : b.as.i);
                    else vm->stack[vm->sp++] = val_int(0);
                    val_free(a); val_free(b);
                } else if (strcmp(name, "SQRT") == 0) {
                    Value v = vm->stack[--vm->sp];
                    if (v.type == VAL_INT) vm->stack[vm->sp++] = val_int((int64_t)sqrt((double)v.as.i));
                    else { vm->stack[vm->sp++] = val_int(0); val_free(v); }
                } else if (strcmp(name, "POW") == 0) {
                    Value b = vm->stack[--vm->sp]; Value a = vm->stack[--vm->sp];
                    if (a.type == VAL_INT && b.type == VAL_INT)
                        vm->stack[vm->sp++] = val_int((int64_t)pow((double)b.as.i, (double)a.as.i));
                    else vm->stack[vm->sp++] = val_int(0);
                    val_free(a); val_free(b);
                } else if (strcmp(name, "FLOOR") == 0) {
                    Value v = vm->stack[--vm->sp];
                    vm->stack[vm->sp++] = v;
                } else if (strcmp(name, "CEIL") == 0) {
                    Value v = vm->stack[--vm->sp];
                    vm->stack[vm->sp++] = v;
                } else if (strcmp(name, "ROUND") == 0) {
                    Value v = vm->stack[--vm->sp];
                    vm->stack[vm->sp++] = v;
                } else if (strcmp(name, "PUSH") == 0) {
                    Value val = vm->stack[--vm->sp];
                    Value arr = vm->stack[--vm->sp];
                    if (arr.type == VAL_ARRAY) {
                        if (arr.as.a->count >= arr.as.a->capacity) {
                            int newcap = arr.as.a->capacity ? arr.as.a->capacity * 2 : 8;
                            arr.as.a->items = (Value*)realloc(arr.as.a->items, newcap * sizeof(Value));
                            arr.as.a->capacity = newcap;
                        }
                        arr.as.a->items[arr.as.a->count++] = val;
                    } else val_free(val);
                    vm->stack[vm->sp++] = arr;
                } else if (strcmp(name, "POP") == 0) {
                    Value arr = vm->stack[--vm->sp];
                    if (arr.type == VAL_ARRAY && arr.as.a->count > 0) {
                        Value v = arr.as.a->items[--arr.as.a->count];
                        vm->stack[vm->sp++] = v;
                    } else vm->stack[vm->sp++] = val_null();
                    val_free(arr);
                } else if (strcmp(name, "READ_FILE") == 0) {
                    Value v = vm->stack[--vm->sp];
                    if (v.type == VAL_STRING) {
                        FILE* fp = fopen(v.as.s, "rb");
                        if (fp) {
                            fseek(fp, 0, SEEK_END);
                            long sz = ftell(fp);
                            fseek(fp, 0, SEEK_SET);
                            char* buf = (char*)malloc(sz + 1);
                            fread(buf, 1, sz, fp);
                            buf[sz] = 0;
                            fclose(fp);
                            vm->stack[vm->sp++] = val_string(buf);
                            free(buf);
                        } else vm->stack[vm->sp++] = val_null();
                    } else { vm->stack[vm->sp++] = val_null(); val_free(v); }
                } else if (strcmp(name, "WRITE_FILE") == 0) {
                    Value v = vm->stack[--vm->sp];
                    Value content = vm->stack[--vm->sp];
                    if (v.type == VAL_STRING && content.type == VAL_STRING) {
                        FILE* fp = fopen(v.as.s, "wb");
                        if (fp) {
                            fwrite(content.as.s, 1, strlen(content.as.s), fp);
                            fclose(fp);
                            vm->stack[vm->sp++] = val_bool(1);
                        } else vm->stack[vm->sp++] = val_bool(0);
                    } else vm->stack[vm->sp++] = val_bool(0);
                    val_free(v); val_free(content);
                } else if (strcmp(name, "FFI_LOAD") == 0) {
                    Value path_val = vm->stack[--vm->sp];
                    Value name_val = vm->stack[--vm->sp];
                    if (name_val.type == VAL_STRING && path_val.type == VAL_STRING) {
                        ffi_load_lib(name_val.as.s, path_val.as.s);
                        val_free(name_val); val_free(path_val);
                        vm->stack[vm->sp++] = val_int(0);
                    } else {
                        fprintf(stderr, "FFI_LOAD requires two string arguments\n");
                        val_free(name_val); val_free(path_val);
                        vm->stack[vm->sp++] = val_int(-1);
                    }
                } else if (strcmp(name, "FFI_REGISTER") == 0) {
                    Value param_count_val = vm->stack[--vm->sp];
                    Value ret_type_val = vm->stack[--vm->sp];
                    Value func_name_val = vm->stack[--vm->sp];
                    Value lib_name_val = vm->stack[--vm->sp];
                    if (lib_name_val.type == VAL_STRING && func_name_val.type == VAL_STRING &&
                        ret_type_val.type == VAL_INT && param_count_val.type == VAL_INT) {
                        int rc = ffi_register_func(lib_name_val.as.s, func_name_val.as.s,
                            (NbsFFIType)ret_type_val.as.i, (int)param_count_val.as.i);
                        val_free(lib_name_val); val_free(func_name_val);
                        val_free(ret_type_val); val_free(param_count_val);
                        vm->stack[vm->sp++] = val_int(rc);
                    } else {
                        fprintf(stderr, "FFI_REGISTER requires (string, string, int, int)\n");
                        val_free(lib_name_val); val_free(func_name_val);
                        val_free(ret_type_val); val_free(param_count_val);
                        vm->stack[vm->sp++] = val_int(-1);
                    }
                } else if (strcmp(name, "FFI_CALL") == 0) {
                    int ffi_argc = arity - 2;
                    if (ffi_argc < 0) ffi_argc = 0;
                    Value ffi_args[16];
                    for (int i = ffi_argc - 1; i >= 0; i--) {
                        ffi_args[i] = vm->stack[--vm->sp];
                    }
                    Value func_name_val = vm->stack[--vm->sp];
                    Value lib_name_val = vm->stack[--vm->sp];
                    Value result = val_int(0);
                    if (lib_name_val.type == VAL_STRING && func_name_val.type == VAL_STRING) {
                        NbsFFILib* lib = NULL;
                        NbsFFIFunc* func = NULL;
                        for (int i = 0; i < ffi_lib_count; i++) {
                            if (strcmp(ffi_libs[i].name, lib_name_val.as.s) == 0) {
                                lib = &ffi_libs[i]; break;
                            }
                        }
                        if (lib) {
                            for (int j = 0; j < lib->func_count; j++) {
                                if (strcmp(lib->functions[j].name, func_name_val.as.s) == 0) {
                                    func = &lib->functions[j]; break;
                                }
                            }
                        }
                        if (lib && func) {
                            void* fn = ffi_resolve_func(lib, func);
                            if (fn) {
                                intptr_t vals[16];
                                for (int k = 0; k < ffi_argc && k < 16; k++) {
                                    if (ffi_args[k].type == VAL_INT)
                                        vals[k] = (intptr_t)ffi_args[k].as.i;
                                    else if (ffi_args[k].type == VAL_STRING)
                                        vals[k] = (intptr_t)ffi_args[k].as.s;
                                    else
                                        vals[k] = 0;
                                }
                                typedef intptr_t (*ffi_fn)();
                                ffi_fn call = (ffi_fn)fn;
                                intptr_t ret = call(
                                    ffi_argc > 0 ? vals[0] : 0,
                                    ffi_argc > 1 ? vals[1] : 0,
                                    ffi_argc > 2 ? vals[2] : 0,
                                    ffi_argc > 3 ? vals[3] : 0,
                                    ffi_argc > 4 ? vals[4] : 0,
                                    ffi_argc > 5 ? vals[5] : 0
                                );
                                switch (func->return_type) {
                                    case NBS_FFI_INT: case NBS_FFI_VOID:
                                        result = val_int((int64_t)ret); break;
                                    case NBS_FFI_STRING: case NBS_FFI_POINTER:
                                        if (ret) result = val_string((const char*)ret);
                                        else result = val_null();
                                        break;
                                    default:
                                        result = val_int((int64_t)ret); break;
                                }
                            }
                        } else {
                            fprintf(stderr, "FFI_CALL: library or function not found: %s.%s\n",
                                lib_name_val.as.s, func_name_val.as.s);
                        }
                    }
                    for (int i = 0; i < ffi_argc; i++) val_free(ffi_args[i]);
                    val_free(lib_name_val); val_free(func_name_val);
                    vm->stack[vm->sp++] = result;
                } else {
                    // User-defined function
                    int fi = ft_find(vm->funcs, name);
                    if (fi < 0) {
                        fprintf(stderr, "Runtime error: undefined function '%s'\n", name);
                        return 1;
                    }
                    if (vm->debug) fprintf(stderr, "CALL '%s' -> addr=%d\n", name, vm->funcs->entries[fi].addr);
                    if (vm->call_sp >= 256) {
                        fprintf(stderr, "Runtime error: call stack overflow\n");
                        return 1;
                    }
                    // Save variables that will be overwritten by params and locals
                    vm->call_stack[vm->call_sp].ret_ip = vm->ip;
                    vm->call_stack[vm->call_sp].saved_count = 0;
                    int sc = 0;
                    int saved_flag[256] = {0};
                    // Save param slots
                    int pcount = vm->funcs->entries[fi].param_count < arity ? vm->funcs->entries[fi].param_count : arity;
                    for (int i = 0; i < pcount && sc < 256; i++) {
                        int param_idx = st_intern(vm->strings, vm->funcs->entries[fi].params[i]);
                        if (param_idx >= 0 && param_idx < 1024 && !saved_flag[param_idx]) {
                            vm->call_stack[vm->call_sp].saved_var_idx[sc] = param_idx;
                            vm->call_stack[vm->call_sp].saved_vars[sc] = vm->vars[param_idx];
                            vm->call_stack[vm->call_sp].saved_count = ++sc;
                            saved_flag[param_idx] = 1;
                        }
                    }
                    // Store arguments (in reverse so params[0] gets leftmost arg)
                    for (int i = pcount - 1; i >= 0; i--) {
                        int param_idx = st_intern(vm->strings, vm->funcs->entries[fi].params[i]);
                        val_free(vm->vars[param_idx]);
                        vm->vars[param_idx] = vm->stack[--vm->sp];
                    }
                    // Discard remaining args
                    for (int i = arity; i > vm->funcs->entries[fi].param_count; i--)
                        val_free(vm->stack[--vm->sp]);
                    vm->call_sp++;
                    vm->ip = vm->funcs->entries[fi].addr;
                }
            } break;

            case BC_RET: {
                Value v = vm->stack[--vm->sp];
                if (vm->debug) fprintf(stderr, "RET call_sp=%d\n", vm->call_sp);
                if (vm->call_sp > 0) {
                    vm->call_sp--;
                    // Restore saved variables
                    for (int i = 0; i < vm->call_stack[vm->call_sp].saved_count; i++) {
                        int gidx = vm->call_stack[vm->call_sp].saved_var_idx[i];
                        if (gidx >= 0 && gidx < 1024) {
                            val_free(vm->vars[gidx]);
                            vm->vars[gidx] = vm->call_stack[vm->call_sp].saved_vars[i];
                        }
                    }
                    vm->ip = vm->call_stack[vm->call_sp].ret_ip;
                } else {
                    vm->running = 0;
                }
                vm->stack[vm->sp++] = v;
            } break;

            case BC_ARRAY_NEW: {
                int32_t count;
                memcpy(&count, vm->code + vm->ip, 4);
                vm->ip += 4;
                Value arr = val_array();
                arr.as.a->capacity = count > 0 ? count : 8;
                arr.as.a->items = (Value*)malloc(arr.as.a->capacity * sizeof(Value));
                arr.as.a->count = 0;
                for (int i = count - 1; i >= 0; i--) {
                    arr.as.a->items[arr.as.a->count++] = vm->stack[--vm->sp];
                }
                // Reverse to correct order
                for (int i = 0; i < arr.as.a->count / 2; i++) {
                    Value tmp = arr.as.a->items[i];
                    arr.as.a->items[i] = arr.as.a->items[arr.as.a->count - 1 - i];
                    arr.as.a->items[arr.as.a->count - 1 - i] = tmp;
                }
                vm->stack[vm->sp++] = arr;
            } break;

            case BC_ARRAY_GET: {
                Value idx = vm->stack[--vm->sp];
                Value arr = vm->stack[--vm->sp];
                if (arr.type == VAL_ARRAY && idx.type == VAL_INT) {
                    if (idx.as.i >= 0 && idx.as.i < arr.as.a->count)
                        vm->stack[vm->sp++] = arr.as.a->items[idx.as.i];
                    else
                        vm->stack[vm->sp++] = val_null();
                } else if (arr.type == VAL_STRING && idx.type == VAL_INT) {
                    int len = (int)strlen(arr.as.s);
                    if (idx.as.i >= 0 && idx.as.i < len) {
                        char ch[2] = { arr.as.s[idx.as.i], 0 };
                        vm->stack[vm->sp++] = val_string(ch);
                    } else {
                        vm->stack[vm->sp++] = val_null();
                    }
                } else {
                    vm->stack[vm->sp++] = val_null();
                }
            } break;

            case BC_ARRAY_SET: {
                Value val = vm->stack[--vm->sp];
                Value idx = vm->stack[--vm->sp];
                Value arr = vm->stack[--vm->sp];
                if (arr.type == VAL_ARRAY && idx.type == VAL_INT) {
                    if (idx.as.i >= 0 && idx.as.i < arr.as.a->count) {
                        val_free(arr.as.a->items[idx.as.i]);
                        arr.as.a->items[idx.as.i] = val;
                    }
                }
                vm->stack[vm->sp++] = arr;
            } break;

            case BC_ARRAY_LEN: {
                Value arr = vm->stack[--vm->sp];
                if (arr.type == VAL_ARRAY)
                    vm->stack[vm->sp++] = val_int(arr.as.a->count);
                else if (arr.type == VAL_STRING)
                    vm->stack[vm->sp++] = val_int((int)strlen(arr.as.s));
                else
                    vm->stack[vm->sp++] = val_int(0);
            } break;

            case BC_TYPEOF: {
                Value v = vm->stack[--vm->sp];
                vm->stack[vm->sp++] = val_string(val_type_name(v));
                val_free(v);
            } break;

            case BC_TOSTR: {
                Value v = vm->stack[--vm->sp];
                vm->stack[vm->sp++] = val_to_string(v);
                val_free(v);
            } break;

            case BC_TONUM: {
                Value v = vm->stack[--vm->sp];
                if (v.type == VAL_STRING) {
                    int64_t n = atoll(v.as.s);
                    val_free(v);
                    vm->stack[vm->sp++] = val_int(n);
                } else if (v.type == VAL_INT) {
                    vm->stack[vm->sp++] = v;
                } else {
                    val_free(v);
                    vm->stack[vm->sp++] = val_int(0);
                }
            } break;

            case BC_ARRAY_PUSH: {
                Value val = vm->stack[--vm->sp];
                Value arr = vm->stack[--vm->sp];
                if (arr.type == VAL_ARRAY) {
                    if (arr.as.a->count >= arr.as.a->capacity) {
                        int newcap = arr.as.a->capacity ? arr.as.a->capacity * 2 : 8;
                        arr.as.a->items = (Value*)realloc(arr.as.a->items, newcap * sizeof(Value));
                        arr.as.a->capacity = newcap;
                    }
                    arr.as.a->items[arr.as.a->count++] = val;
                } else {
                    val_free(val);
                }
                vm->stack[vm->sp++] = arr;
            } break;

            case BC_ARRAY_POP: {
                Value arr = vm->stack[--vm->sp];
                Value popped = val_null();
                if (arr.type == VAL_ARRAY && arr.as.a->count > 0) {
                    popped = arr.as.a->items[--arr.as.a->count];
                }
                vm->stack[vm->sp++] = arr;      // push modified array (element removed)
                vm->stack[vm->sp++] = popped;    // push popped value
            } break;

            case BC_TRY: {
                int32_t handler_offset;
                memcpy(&handler_offset, vm->code + vm->ip, 4);
                vm->ip += 4;
                if (vm->try_sp < 64) {
                    vm->try_stack[vm->try_sp].handler_ip = vm->ip + handler_offset;
                    vm->try_stack[vm->try_sp].saved_sp = vm->sp;
                    vm->try_sp++;
                }
            } break;

            case BC_CATCH: break;

            case BC_THROW: {
                Value err = vm->stack[--vm->sp];
                if (vm->try_sp > 0) {
                    vm->try_sp--;
                    vm->sp = vm->try_stack[vm->try_sp].saved_sp;
                    vm->ip = vm->try_stack[vm->try_sp].handler_ip;
                    vm->stack[vm->sp++] = err;
                } else {
                    fprintf(stderr, "Uncaught exception: %s\n", err.type == VAL_STRING ? err.as.s : "unknown");
                    val_free(err);
                    return 1;
                }
            } break;

            case BC_ENDTRY: break;

            case BC_IMPORT: {
                int32_t idx;
                memcpy(&idx, vm->code + vm->ip, 4);
                vm->ip += 4;
                const char* path = vm->strings->strings[idx];
                FILE* f = fopen(path, "rb");
                if (!f) {
                    fprintf(stderr, "Runtime error: cannot open import '%s'\n", path);
                    break;
                }
                fseek(f, 0, SEEK_END);
                long sz = ftell(f);
                fseek(f, 0, SEEK_SET);
                char* buf = (char*)malloc(sz + 1);
                fread(buf, 1, sz, f);
                buf[sz] = 0;
                fclose(f);
                vm_exec_import(vm, buf, path);
                free(buf);
            } break;

            default:
                fprintf(stderr, "Runtime error: unknown opcode 0x%02X at IP=%d\n", op, vm->ip - 1);
                return 1;
        }
    }
    return 0;
}

// ============================================================================
// MAIN
// ============================================================================

int main(int argc, char** argv) {
    srand((unsigned)time(NULL));

    if (argc < 2) {
        fprintf(stderr, "Nebulara Interpreter v2.0\n");
        fprintf(stderr, "Usage: %s <file.nbs>\n", argv[0]);
        return 1;
    }

    FILE* f = fopen(argv[1], "rb");
    if (!f) { fprintf(stderr, "Error: cannot open '%s'\n", argv[1]); return 1; }
    fseek(f, 0, SEEK_END);
    long len = ftell(f);
    fseek(f, 0, SEEK_SET);
    char* src = (char*)malloc(len + 1);
    fread(src, 1, len, f);
    src[len] = 0;
    fclose(f);

    // Lex
    Lexer lexer = lexer_new(src);
    Parser parser = {0};
    parser.pos = 0;
    while (1) {
        NbsToken tok = lexer_next(&lexer);
        parser.tokens[parser.count++] = tok;
        if (tok.type == TOK_EOF) break;
        if (parser.count >= 4096) {
            fprintf(stderr, "Error: too many tokens\n");
            free(src);
            return 1;
        }
    }
    free(src);

    // Parse
    ASTNode* ast = parse_program(&parser);
    if (parser.has_error) {
        fprintf(stderr, "Parse error: %s\n", parser.error_msg);
        return 1;
    }

    // Compile
    BytecodeBuf bc;
    bc_init(&bc);
    StringTable strings;
    st_init(&strings);
    FuncTable funcs;
    ft_init(&funcs);

    Compiler compiler = {&bc, &strings, &funcs};
    compile_node(&compiler, ast);

    // Execute
    VM* vm = (VM*)calloc(1, sizeof(VM));
    vm_init(vm, bc.code, &strings, &funcs);
    vm->debug = 0;
    for (int i = 1; i < argc; i++) {
        if (strcmp(argv[i], "-d") == 0 || strcmp(argv[i], "--debug") == 0) vm->debug = 1;
    }
    int result = vm_run(vm, bc.code, bc.pos);

    // Cleanup
    for (int i = 0; i < vm->imported_bc_count; i++) free(vm->imported_bcs[i]);
    free(vm);
    free(bc.code);
    for (int i = 0; i < strings.count; i++) free(strings.strings[i]);
    free(strings.strings);
    free(funcs.entries);

    return result;
}
