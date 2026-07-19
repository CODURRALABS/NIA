// Nebulara CLI - Command Line Interface
// Compiler/nbs_cli.c - The 'nebulara' command
// Usage: nebulara run <file.nbs> | nebulara build <file.nbs> | nebulara repl

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <ctype.h>
#include <time.h>
#include <math.h>
#include <inttypes.h>

// FFI platform headers
#ifdef _WIN32
#include <windows.h>
typedef HMODULE NbsFFIHandle;
#else
#include <dlfcn.h>
typedef void* NbsFFIHandle;
#endif

// ============================================================================
// VM Types (shared with interpreter)
// ============================================================================

#define VAL_NULL 0
#define VAL_INT 1
#define VAL_STRING 2
#define VAL_BOOL 3
#define VAL_ARRAY 4
#define VAL_ERROR 5

typedef struct Value Value;
typedef struct { Value* items; int count, cap; } ValueArray;
struct Value {
    int type;
    union { int64_t i; char* s; int b; ValueArray* a; } as;
};

Value val_int_v(int64_t v) { return (Value){VAL_INT, {.i=v}}; }
Value val_null_v(void) { return (Value){VAL_NULL, {0}}; }
Value val_string_v(const char* s) { Value v={VAL_STRING}; v.as.s=strdup(s); return v; }
Value val_bool_v(int b) { return (Value){VAL_BOOL, {.b=b}}; }

const char* val_type_name(Value v) {
    switch(v.type){
        case VAL_NULL: return "null";
        case VAL_INT: return "int";
        case VAL_STRING: return "string";
        case VAL_BOOL: return "bool";
        case VAL_ARRAY: return "array";
        case VAL_ERROR: return "error";
        default: return "unknown";
    }
}

// Deep copy a value (strings are duplicated, arrays are deep-copied)
Value val_copy(Value v) {
    if (v.type == VAL_STRING) return val_string_v(v.as.s);
    if (v.type == VAL_ARRAY) {
        ValueArray* src = v.as.a;
        ValueArray* dst = calloc(1, sizeof(ValueArray));
        dst->cap = src->count > 0 ? src->count : 8;
        dst->items = calloc(dst->cap, sizeof(Value));
        dst->count = src->count;
        for (int i = 0; i < src->count; i++)
            dst->items[i] = val_copy(src->items[i]);
        Value rv = {VAL_ARRAY}; rv.as.a = dst;
        return rv;
    }
    return v; // int, bool, null are copied by value
}

Value val_to_string(Value v) {
    char buf[128];
    switch(v.type){
        case VAL_NULL: return val_string_v("null");
        case VAL_INT: snprintf(buf,128,"%" PRId64,v.as.i); return val_string_v(buf);
        case VAL_BOOL: return val_string_v(v.as.b?"true":"false");
        case VAL_STRING: return val_string_v(v.as.s);
        case VAL_ARRAY: return val_string_v("[array]");
        case VAL_ERROR: return val_string_v("[error]");
        default: return val_string_v("unknown");
    }
}

int val_truthy(Value v) {
    if (v.type == VAL_NULL) return 0;
    if (v.type == VAL_INT) return v.as.i != 0;
    if (v.type == VAL_BOOL) return v.as.b;
    if (v.type == VAL_STRING) return v.as.s[0] != 0;
    if (v.type == VAL_ARRAY) return v.as.a->count > 0;
    return 0;
}

// Free a value and all its children
void val_free(Value v) {
    if (v.type == VAL_STRING) { free(v.as.s); return; }
    if (v.type == VAL_ARRAY) {
        ValueArray* a = v.as.a;
        if (a) {
            for (int i = 0; i < a->count; i++) val_free(a->items[i]);
            free(a->items);
            free(a);
        }
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

// ============================================================================
// OPCODES
// ============================================================================

#define OP_PUSH_INT   0x01
#define OP_PUSH_STR   0x02
#define OP_PUSH_BOOL  0x03
#define OP_POP        0x04
#define OP_ADD        0x05
#define OP_SUB        0x06
#define OP_MUL        0x07
#define OP_DIV        0x08
#define OP_MOD        0x09
#define OP_NEG        0x0A
#define OP_EQ         0x0B
#define OP_NEQ        0x0C
#define OP_LT         0x0D
#define OP_GT         0x0E
#define OP_LTE        0x0F
#define OP_GTE        0x10
#define OP_AND        0x11
#define OP_OR         0x12
#define OP_NOT        0x13
#define OP_STORE      0x14
#define OP_LOAD       0x15
#define OP_PRINT      0x16
#define OP_JUMP       0x17
#define OP_JUMP_IFNOT 0x18
#define OP_HALT       0x19
#define OP_CALL       0x1A
#define OP_RET        0x1B
#define OP_ARRAY_NEW  0x1C
#define OP_ARRAY_GET  0x1D
#define OP_ARRAY_LEN  0x1E
#define OP_TYPEOF     0x1F
#define OP_TOSTR      0x20
#define OP_TONUM      0x21
#define OP_ABS        0x22
#define OP_STRING_ADD 0x23
#define OP_MIN        0x24
#define OP_MAX        0x25
#define OP_SQRT       0x26
#define OP_POW        0x27
#define OP_FLOOR      0x28
#define OP_CEIL       0x29
#define OP_ROUND      0x2A
#define OP_READ_FILE  0x2B
#define OP_WRITE_FILE 0x2C
#define OP_ARRAY_PUSH 0x2D
#define OP_ARRAY_POP  0x2E
#define OP_SUBSTR     0x2F
#define OP_CHAR_AT    0x30
#define OP_TO_UPPER   0x31
#define OP_TO_LOWER   0x32
#define OP_WRITE_BYTES 0x47
#define OP_STR_EQ     0x33
#define OP_ARRAY_SET  0x34
#define OP_PUSH_NULL  0x35
#define OP_DUP        0x36
#define OP_SWAP       0x37
#define OP_EXIT       0x38
#define OP_BREAK      0x39
#define OP_CONTINUE   0x3A
#define OP_BITAND     0x3B
#define OP_BITOR      0x3C
#define OP_LSHIFT     0x3D
#define OP_RSHIFT     0x3E
#define OP_TRY        0x3F
#define OP_CATCH      0x40
#define OP_THROW      0x41
#define OP_FINALLY    0x42
#define OP_ENDTRY     0x43
#define OP_CHAR       0x44
#define OP_ORD        0x45
#define OP_IMPORT     0x46

// ============================================================================
// LEXER
// ============================================================================

typedef enum {
    T_INT, T_STR, T_IDENT, T_PLUS, T_MINUS, T_STAR, T_SLASH, T_MOD,
    T_EQ, T_NEQ, T_LT, T_GT, T_LTE, T_GTE, T_AND, T_OR, T_NOT,
    T_ASSIGN, T_LPAREN, T_RPAREN, T_LBRACKET, T_RBRACKET,
    T_COMMA, T_COLON, T_PRINT, T_IF, T_ELSE, T_ELSEIF, T_THEN,
    T_WHILE, T_FOR, T_TO, T_STEP, T_FUNC, T_END, T_RETURN, T_LET, T_BREAK, T_CONTINUE,
    T_BITAND, T_BITOR, T_LSHIFT, T_RSHIFT,
    T_TRY, T_CATCH, T_THROW, T_FINALLY,
    T_IMPORT,
    T_TRUE, T_FALSE, T_NULL,
    T_EOF
} TT;

typedef struct { TT type; char txt[256]; int64_t ival; int line; } Tk;
typedef struct { const char*s; int p,l,line; } Lx;

static Tk tks[8192]; static int tn=0,tp=0;

static Tk lx(Lx*l) {
    while(l->p<l->l) {
        char c=l->s[l->p];
        if(c==' '||c=='\t'||c=='\r') { l->p++; continue; }
        if(c=='\n') { l->p++; l->line++; continue; }
        if(c=='#') { while(l->p<l->l&&l->s[l->p]!='\n')l->p++; continue; }
        break;
    }
    Tk t={0};
    t.line=l->line;
    if(l->p>=l->l){t.type=T_EOF;return t;}
    char c=l->s[l->p];

    if(c>='0'&&c<='9'){
        int64_t v=0;
        while(l->p<l->l&&l->s[l->p]>='0'&&l->s[l->p]<='9')v=v*10+(l->s[l->p++]-'0');
        t.type=T_INT;t.ival=v;return t;
    }
    if(c=='"'){
        l->p++;int i=0;
        while(l->p<l->l&&l->s[l->p]!='"'&&i<254){
            if(l->s[l->p]=='\\'){
                if(l->p+1<l->l){
                    l->p++;char e=l->s[l->p++];
                    if(e=='n')t.txt[i++]='\n';else if(e=='t')t.txt[i++]='\t';
                    else if(e=='\\')t.txt[i++]='\\';else if(e=='"')t.txt[i++]='"';
                    else if(e=='0')t.txt[i++]='\0';else t.txt[i++]=e;
                } else { l->p++; }
            } else t.txt[i++]=l->s[l->p++];
        }
        t.txt[i]=0;if(l->p<l->l)l->p++;t.type=T_STR;return t;
    }
    if((c>='a'&&c<='z')||(c>='A'&&c<='Z')||c=='_'){
        int i=0;
        while(l->p<l->l&&i<254&&((l->s[l->p]>='a'&&l->s[l->p]<='z')||(l->s[l->p]>='A'&&l->s[l->p]<='Z')||(l->s[l->p]>='0'&&l->s[l->p]<='9')||l->s[l->p]=='_'||l->s[l->p]=='!'||l->s[l->p]=='?'))t.txt[i++]=l->s[l->p++];
        t.txt[i]=0;
        if(!strcmp(t.txt,"PRINT"))t.type=T_PRINT;
        else if(!strcmp(t.txt,"IF?")||!strcmp(t.txt,"IF"))t.type=T_IF;
        else if(!strcmp(t.txt,"ELSE"))t.type=T_ELSE;
        else if(!strcmp(t.txt,"ELSEIF")||!strcmp(t.txt,"ELSEIF?"))t.type=T_ELSEIF;
        else if(!strcmp(t.txt,"THEN"))t.type=T_THEN;
        else if(!strcmp(t.txt,"WHILE?")||!strcmp(t.txt,"WHILE"))t.type=T_WHILE;
        else if(!strcmp(t.txt,"FOR!"))t.type=T_FOR;
        else if(!strcmp(t.txt,"TO"))t.type=T_TO;
        else if(!strcmp(t.txt,"STEP"))t.type=T_STEP;
        else if(!strcmp(t.txt,"FUNC!"))t.type=T_FUNC;
        else if(!strcmp(t.txt,"END!"))t.type=T_END;
        else if(!strcmp(t.txt,"RETURN"))t.type=T_RETURN;
        else if(!strcmp(t.txt,"LET"))t.type=T_LET;
        else if(!strcmp(t.txt,"AND"))t.type=T_AND;
        else if(!strcmp(t.txt,"OR"))t.type=T_OR;
        else if(!strcmp(t.txt,"NOT"))t.type=T_NOT;
        else if(!strcmp(t.txt,"BREAK"))t.type=T_BREAK;
        else if(!strcmp(t.txt,"CONTINUE"))t.type=T_CONTINUE;
        else if(!strcmp(t.txt,"TRUE")){t.type=T_TRUE;}
        else if(!strcmp(t.txt,"FALSE")){t.type=T_FALSE;}
        else if(!strcmp(t.txt,"NULL")){t.type=T_NULL;}
        else if(!strcmp(t.txt,"TRY!"))t.type=T_TRY;
        else if(!strcmp(t.txt,"CATCH!"))t.type=T_CATCH;
        else if(!strcmp(t.txt,"THROW"))t.type=T_THROW;
        else if(!strcmp(t.txt,"FINALLY!"))t.type=T_FINALLY;
        else if(!strcmp(t.txt,"IMPORT"))t.type=T_IMPORT;
        else t.type=T_IDENT;
        return t;
    }
    l->p++;t.txt[0]=c;t.txt[1]=0;
    switch(c){
        case '+':t.type=T_PLUS;break;case '-':t.type=T_MINUS;break;
        case '*':t.type=T_STAR;break;case '/':t.type=T_SLASH;break;
        case '%':t.type=T_MOD;break;
        case '=':if(l->p<l->l&&l->s[l->p]=='='){l->p++;t.txt[1]='=';t.type=T_EQ;}else t.type=T_ASSIGN;break;
        case '!':if(l->p<l->l&&l->s[l->p]=='='){l->p++;t.txt[1]='=';t.type=T_NEQ;}else t.type=T_NOT;break;
        case '<':if(l->p<l->l&&l->s[l->p]=='='){l->p++;t.txt[1]='=';t.type=T_LTE;}else if(l->p<l->l&&l->s[l->p]=='<'){l->p++;t.txt[1]='<';t.type=T_LSHIFT;}else t.type=T_LT;break;
        case '>':if(l->p<l->l&&l->s[l->p]=='='){l->p++;t.txt[1]='=';t.type=T_GTE;}else if(l->p<l->l&&l->s[l->p]=='>'){l->p++;t.txt[1]='>';t.type=T_RSHIFT;}else t.type=T_GT;break;
        case '&':t.type=T_BITAND;break;
        case '|':t.type=T_BITOR;break;
        case '(':t.type=T_LPAREN;break;case ')':t.type=T_RPAREN;break;
        case '[':t.type=T_LBRACKET;break;case ']':t.type=T_RBRACKET;break;
        case ',':t.type=T_COMMA;break;case ':':t.type=T_COLON;break;
    }
    return t;
}

// ============================================================================
// BYTECODE COMPILER
// ============================================================================

static uint8_t bytecode[131072];
static int bclen=0;
static char strings[65536][256];
static int strcount=0;

// Loop break/continue patch stack
typedef struct { int break_patches[64]; int break_count; int continue_patches[64]; int continue_count; int continue_ip; } LoopInfo;
static LoopInfo loop_stack[64];
static int loop_sp=0;

// Try/catch patch stack
typedef struct { int end_patches[32]; int end_count; } TryInfo;
static TryInfo try_stack[32];
static int try_sp=0;

static void bc(uint8_t b){
    if(bclen>=131072){fprintf(stderr,"Compiler error: bytecode overflow\n");exit(1);}
    bytecode[bclen++]=b;
}
static void bc64(int64_t v){for(int i=0;i<8;i++)bc((v>>(i*8))&0xFF);}
static void bc32(int32_t v){for(int i=0;i<4;i++)bc((v>>(i*8))&0xFF);}

static char varnames[256][64];
static int varcount=0;

static int var_idx(const char* name){
    for(int i=0;i<varcount;i++)if(!strcmp(varnames[i],name))return i;
    if(varcount>=256){fprintf(stderr,"Compiler error: too many variables\n");exit(1);}
    strncpy(varnames[varcount],name,63);varnames[varcount][63]=0;return varcount++;
}

static int str_idx(const char* s){
    for(int i=0;i<strcount;i++)if(!strcmp(strings[i],s))return i;
    if(strcount>=65536){fprintf(stderr,"Compiler error: too many strings\n");exit(1);}
    strncpy(strings[strcount],s,255);strings[strcount][255]=0;return strcount++;
}

// Function table
typedef struct { char name[64]; int addr; char params[8][64]; int param_count; int entry_varcount; int local_count; } FuncEntry;
static FuncEntry func_table[256];
static int func_count=0;

static int ft_add(const char* name, int addr) {
    if(func_count>=256){fprintf(stderr,"Compiler error: too many functions\n");exit(1);}
    int idx = func_count++;
    strncpy(func_table[idx].name, name, 63);func_table[idx].name[63]=0;
    func_table[idx].addr = addr;
    func_table[idx].param_count = 0;
    func_table[idx].entry_varcount = 0;
    func_table[idx].local_count = 0;
    return idx;
}
static void ft_add_param(int idx, const char* pname) {
    if (idx >= 0 && func_table[idx].param_count < 8) {
        strncpy(func_table[idx].params[func_table[idx].param_count], pname, 63);
        func_table[idx].params[func_table[idx].param_count][63]=0;
        func_table[idx].param_count++;
    }
}
static int ft_find(const char* name) {
    for(int i=0;i<func_count;i++) if(!strcmp(func_table[i].name, name)) return i;
    return -1;
}

static void compile_expr(void);
static void compile_stmt(void);
static void compile_block(void);

static void compile_primary(void) {
    if(tp>=tn)return;
    Tk* t=&tks[tp];
    if(t->type==T_INT){tp++;bc(OP_PUSH_INT);bc64(t->ival);return;}
    if(t->type==T_STR){tp++;int si=str_idx(t->txt);bc(OP_PUSH_STR);bc32(si);return;}
    if(t->type==T_TRUE){tp++;bc(OP_PUSH_BOOL);bc(1);return;}
    if(t->type==T_FALSE){tp++;bc(OP_PUSH_BOOL);bc(0);return;}
    if(t->type==T_NULL){tp++;bc(OP_PUSH_NULL);return;}
    if(t->type==T_IDENT){
        if(tp+1<tn && tks[tp+1].type==T_LPAREN) {
            if(!strcmp(t->txt,"TO_STRING")||!strcmp(t->txt,"TYPEOF")||!strcmp(t->txt,"LEN")||
               !strcmp(t->txt,"TO_NUMBER")||
               !strcmp(t->txt,"ABS")||!strcmp(t->txt,"MIN")||!strcmp(t->txt,"MAX")||
               !strcmp(t->txt,"SQRT")||!strcmp(t->txt,"POW")||!strcmp(t->txt,"FLOOR")||
               !strcmp(t->txt,"CEIL")||!strcmp(t->txt,"ROUND")||!strcmp(t->txt,"READ_FILE")||
               !strcmp(t->txt,"WRITE_FILE")||!strcmp(t->txt,"SUBSTR")||!strcmp(t->txt,"CHAR_AT")||
               !strcmp(t->txt,"TO_UPPER")||!strcmp(t->txt,"TO_LOWER")||
               !strcmp(t->txt,"WRITE_BYTES")||
               !strcmp(t->txt,"CHAR")||!strcmp(t->txt,"ORD")) {
                char fname[64]; strncpy(fname,t->txt,63); fname[63]=0; tp+=2;
                int nargs=0;
                if(tp<tn&&tks[tp].type!=T_RPAREN) {
                    compile_expr(); nargs++;
                    while(tp<tn&&tks[tp].type==T_COMMA) { tp++; compile_expr(); nargs++; }
                }
                if(tp<tn&&tks[tp].type==T_RPAREN)tp++;
                if(!strcmp(fname,"TO_STRING"))bc(OP_TOSTR);
                else if(!strcmp(fname,"TO_NUMBER"))bc(OP_TONUM);
                else if(!strcmp(fname,"TYPEOF"))bc(OP_TYPEOF);
                else if(!strcmp(fname,"LEN"))bc(OP_ARRAY_LEN);
                else if(!strcmp(fname,"ABS"))bc(OP_ABS);
                else if(!strcmp(fname,"MIN"))bc(OP_MIN);
                else if(!strcmp(fname,"MAX"))bc(OP_MAX);
                else if(!strcmp(fname,"SQRT"))bc(OP_SQRT);
                else if(!strcmp(fname,"POW"))bc(OP_POW);
                else if(!strcmp(fname,"FLOOR"))bc(OP_FLOOR);
                else if(!strcmp(fname,"CEIL"))bc(OP_CEIL);
                else if(!strcmp(fname,"ROUND"))bc(OP_ROUND);
                else if(!strcmp(fname,"READ_FILE"))bc(OP_READ_FILE);
                else if(!strcmp(fname,"WRITE_FILE"))bc(OP_WRITE_FILE);
                else if(!strcmp(fname,"SUBSTR"))bc(OP_SUBSTR);
                else if(!strcmp(fname,"CHAR_AT"))bc(OP_CHAR_AT);
                else if(!strcmp(fname,"TO_UPPER"))bc(OP_TO_UPPER);
                else if(!strcmp(fname,"TO_LOWER"))bc(OP_TO_LOWER);
                else if(!strcmp(fname,"WRITE_BYTES"))bc(OP_WRITE_BYTES);
                else if(!strcmp(fname,"CHAR"))bc(OP_CHAR);
                else if(!strcmp(fname,"ORD"))bc(OP_ORD);
                return;
            }
            // User-defined or unknown function call
            char fname[64]; strncpy(fname, t->txt, 63); fname[63]=0;
            tp+=2; // skip name and (
            // Push args in reverse order
            int arg_count=0;
            while(tp<tn && tks[tp].type!=T_RPAREN) {
                compile_expr();
                arg_count++;
                if(tp<tn && tks[tp].type==T_COMMA) tp++;
            }
            if(tp<tn) tp++; // skip )
            bc(OP_CALL);
            int si=str_idx(fname);
            bc32(si);
            bc32(arg_count);
            return;
        }
        tp++;bc(OP_LOAD);bc32(var_idx(t->txt));
        // Array indexing: arr[i]
        while(tp<tn && tks[tp].type==T_LBRACKET){
            tp++;compile_expr();
            if(tp<tn&&tks[tp].type==T_RBRACKET)tp++;
            bc(OP_ARRAY_GET);
        }
        return;
    }
    if(t->type==T_LPAREN){tp++;compile_expr();if(tp<tn&&tks[tp].type==T_RPAREN)tp++;return;}
    if(t->type==T_MINUS){tp++;compile_primary();bc(OP_NEG);return;}
    if(t->type==T_NOT){tp++;compile_primary();bc(OP_NOT);return;}
    if(t->type==T_LBRACKET){
        tp++;int count=0;
        while(tp<tn&&tks[tp].type!=T_RBRACKET){compile_expr();count++;if(tp<tn&&tks[tp].type==T_COMMA)tp++;}
        if(tp<tn)tp++;
        bc(OP_ARRAY_NEW);bc32(count);return;
    }
    // Fallback: push 0
    tp++;bc(OP_PUSH_INT);bc64(0);
}

// Precedence: 1=multiplicative (* / %), 2=additive (+ - << >> & |), 3=comparison (== != < > <= >=)
static void compile_mul(void) {
    compile_primary();
    while(tp<tn&&(tks[tp].type==T_STAR||tks[tp].type==T_SLASH||tks[tp].type==T_MOD)){
        TT op=tks[tp].type;tp++;
        compile_primary();
        switch(op){
            case T_STAR:bc(OP_MUL);break;case T_SLASH:bc(OP_DIV);break;
            case T_MOD:bc(OP_MOD);break;default:break;
        }
    }
}
static void compile_add(void) {
    compile_mul();
    while(tp<tn&&(tks[tp].type==T_PLUS||tks[tp].type==T_MINUS||
                   tks[tp].type==T_BITAND||tks[tp].type==T_BITOR||
                   tks[tp].type==T_LSHIFT||tks[tp].type==T_RSHIFT)){
        TT op=tks[tp].type;tp++;
        compile_mul();
        switch(op){
            case T_PLUS:bc(OP_ADD);break;case T_MINUS:bc(OP_SUB);break;
            case T_BITAND:bc(OP_BITAND);break;case T_BITOR:bc(OP_BITOR);break;
            case T_LSHIFT:bc(OP_LSHIFT);break;case T_RSHIFT:bc(OP_RSHIFT);break;
            default:break;
        }
    }
}
static void compile_comparison(void) {
    compile_add();
    while(tp<tn&&(tks[tp].type==T_EQ||tks[tp].type==T_NEQ||
                  tks[tp].type==T_LT||tks[tp].type==T_GT||
                  tks[tp].type==T_LTE||tks[tp].type==T_GTE)){
        TT op=tks[tp].type;tp++;
        compile_add();
        switch(op){
            case T_EQ:bc(OP_EQ);break;case T_NEQ:bc(OP_NEQ);break;
            case T_LT:bc(OP_LT);break;case T_GT:bc(OP_GT);break;
            case T_LTE:bc(OP_LTE);break;case T_GTE:bc(OP_GTE);break;
            default:break;
        }
    }
}

static void compile_expr(void) {
    compile_comparison();
    while(tp<tn&&(tks[tp].type==T_AND||tks[tp].type==T_OR)){
        TT op=tks[tp].type;tp++;
        compile_comparison();
        if(op==T_AND)bc(OP_AND);else bc(OP_OR);
    }
}

static void compile_stmt(void) {
    if(tp>=tn)return;
    Tk* t=&tks[tp];

    if(t->type==T_BREAK){
        tp++;
        if(loop_sp>0){
            bc(OP_JUMP);int patch=bclen;bc32(0);
            LoopInfo* li=&loop_stack[loop_sp-1];
            if(li->break_count<64) li->break_patches[li->break_count++]=patch;
        }
        return;
    }
    if(t->type==T_CONTINUE){
        tp++;
        if(loop_sp>0){
            LoopInfo* li=&loop_stack[loop_sp-1];
            bc(OP_JUMP);
            if(li->continue_count<64) li->continue_patches[li->continue_count++]=bclen;
            bc32(0); // patched later
        }
        return;
    }

    // TRY! ... CATCH! err: ... FINALLY! ... END!
    if(t->type==T_TRY){
        tp++;
        // Emit OP_TRY which pushes current IP to try stack and sets catch handler
        bc(OP_TRY);int try_patch=bclen;bc32(0);
        // Compile try body
        compile_block();
        // Jump to end (skip catch/finally)
        bc(OP_JUMP);int end_jump=bclen;bc32(0);
        // Patch try to point to catch handler
        {int32_t o=bclen-try_patch-4;memcpy(bytecode+try_patch,&o,4);}
        // CATCH! block
        if(tp<tn&&tks[tp].type==T_CATCH){
            tp++;
            // Store error in variable if named
            if(tp<tn&&tks[tp].type==T_IDENT){
                int idx=var_idx(tks[tp].txt);tp++;
                bc(OP_STORE);bc32(idx);
            }
            compile_block();
        }
        // FINALLY! block (optional)
        if(tp<tn&&tks[tp].type==T_FINALLY){
            tp++;
            compile_block();
        }
        // Patch end jump
        {int32_t o=bclen-end_jump-4;memcpy(bytecode+end_jump,&o,4);}
        if(tp<tn&&tks[tp].type==T_END)tp++;
        return;
    }
    // THROW expression
    if(t->type==T_THROW){
        tp++;
        compile_expr();
        bc(OP_THROW);
        return;
    }
    // IMPORT "path"
    if(t->type==T_IMPORT){
        tp++;
        if(tp<tn && tks[tp].type==T_STR){
            int si=str_idx(tks[tp].txt);
            tp++;
            bc(OP_IMPORT);bc32(si);
        }
        return;
    }

    if(t->type==T_PRINT){tp++;compile_expr();bc(OP_PRINT);return;}

    if(t->type==T_LET){
        tp++;
        if(tp<tn&&tks[tp].type==T_IDENT){
            int idx=var_idx(tks[tp].txt);tp++;
            if(tp<tn&&tks[tp].type==T_ASSIGN)tp++;
            compile_expr();
            bc(OP_STORE);bc32(idx);
        }
        return;
    }
    if(t->type==T_IDENT&&tp+1<tn&&tks[tp+1].type==T_ASSIGN){
        int idx=var_idx(t->txt);tp+=2;
        compile_expr();
        bc(OP_STORE);bc32(idx);
        return;
    }
    // Array indexing assignment: arr[i] = value
    if(t->type==T_IDENT&&tp+2<tn&&tks[tp+1].type==T_LBRACKET){
        int idx=var_idx(t->txt);tp++;
        bc(OP_LOAD);bc32(idx);
        tp++;compile_expr();
        if(tp<tn&&tks[tp].type==T_RBRACKET)tp++;
        if(tp<tn&&tks[tp].type==T_ASSIGN)tp++;
        compile_expr();
        bc(OP_ARRAY_SET);
        bc(OP_STORE);bc32(idx);
        return;
    }
    if(t->type==T_IF){
        tp++;
        compile_expr();
        if(tp<tn&&tks[tp].type==T_THEN)tp++;
        if(tp<tn&&tks[tp].type==T_COLON)tp++;
        bc(OP_JUMP_IFNOT);int p1=bclen;bc32(0);
        compile_block();
        // Track JUMP locations that need patching to END
        int end_patches[64]; int end_patch_count=0;
        // Handle ELSE / ELSEIF chains
        while(tp<tn&&(tks[tp].type==T_ELSE||tks[tp].type==T_ELSEIF)){
            int is_elseif=(tks[tp].type==T_ELSEIF);
            tp++;
            if(is_elseif){
                // ELSEIF? <condition>:
                bc(OP_JUMP);end_patches[end_patch_count++]=bclen;bc32(0);
                {int32_t o=bclen-p1-4;memcpy(bytecode+p1,&o,4);}
                compile_expr();
                if(tp<tn&&tks[tp].type==T_THEN)tp++;
                if(tp<tn&&tks[tp].type==T_COLON)tp++;
                bc(OP_JUMP_IFNOT);p1=bclen;bc32(0);
            }else{
                // Plain ELSE:
                if(tp<tn&&tks[tp].type==T_COLON)tp++;
                bc(OP_JUMP);int p2=bclen;bc32(0);
                {int32_t o=bclen-p1-4;memcpy(bytecode+p1,&o,4);}
                p1=p2; // else block ends at p2
            }
            compile_block();
        }
        // Patch JUMP_IFNOT (fall-through) to END
        {int32_t o=bclen-p1-4;memcpy(bytecode+p1,&o,4);}
        // Patch all ELSEIF skip-to-end JUMPs
        for(int ei=0;ei<end_patch_count;ei++){
            int32_t o=bclen-end_patches[ei]-4;memcpy(bytecode+end_patches[ei],&o,4);
        }
        if(tp<tn&&tks[tp].type==T_END)tp++;
        return;
    }
    if(t->type==T_WHILE){
        tp++;
        int loop=bclen;
        // Push loop info for BREAK/CONTINUE
        loop_stack[loop_sp].break_count=0;
        loop_stack[loop_sp].continue_count=0;
        loop_sp++;
        compile_expr();
        if(tp<tn&&tks[tp].type==T_THEN)tp++;
        if(tp<tn&&tks[tp].type==T_COLON)tp++;
        bc(OP_JUMP_IFNOT);int p1=bclen;bc32(0);
        compile_block();
        bc(OP_JUMP);bc32(loop-bclen-4);
        {int32_t o=bclen-p1-4;memcpy(bytecode+p1,&o,4);}
        // Patch all BREAK jumps to here
        loop_sp--;
        for(int bi=0;bi<loop_stack[loop_sp].break_count;bi++){
            int patch=loop_stack[loop_sp].break_patches[bi];
            int32_t o=bclen-patch-4;memcpy(bytecode+patch,&o,4);
        }
        // Patch all CONTINUE jumps to loop start
        for(int ci=0;ci<loop_stack[loop_sp].continue_count;ci++){
            int patch=loop_stack[loop_sp].continue_patches[ci];
            int32_t o=loop-patch-4;memcpy(bytecode+patch,&o,4);
        }
        if(tp<tn&&tks[tp].type==T_END)tp++;
        return;
    }
    if(t->type==T_FOR){
        tp++;
        if(tp<tn&&tks[tp].type==T_IDENT){
            int idx=var_idx(tks[tp].txt);tp++;
            if(tp<tn&&tks[tp].type==T_ASSIGN)tp++;
            compile_expr(); // start
            bc(OP_STORE);bc32(idx);
            if(tp<tn&&tks[tp].type==T_TO)tp++;
            compile_expr(); // end
            int end_idx=var_idx("__for_end");
            bc(OP_STORE);bc32(end_idx);
            // Optional STEP
            int step_idx=-1;
            if(tp<tn&&tks[tp].type==T_STEP){
                tp++;
                compile_expr(); // step value
                step_idx=var_idx("__for_step");
                bc(OP_STORE);bc32(step_idx);
            }

            int loop=bclen;
            loop_stack[loop_sp].break_count=0;
            loop_stack[loop_sp].continue_count=0;
            loop_sp++;
            bc(OP_LOAD);bc32(idx);
            bc(OP_LOAD);bc32(end_idx);
            bc(OP_LTE); // current <= end
            bc(OP_JUMP_IFNOT);int p1=bclen;bc32(0);
            // body
            if(tp<tn&&tks[tp].type==T_COLON)tp++;
            compile_block();
            // Record increment position for CONTINUE patching
            int increment_pos=bclen;
            // increment
            bc(OP_LOAD);bc32(idx);
            if(step_idx>=0){
                bc(OP_LOAD);bc32(step_idx);
            }else{
                bc(OP_PUSH_INT);bc64(1);
            }
            bc(OP_ADD);
            bc(OP_STORE);bc32(idx);
            bc(OP_JUMP);bc32(loop-bclen-4);
            {int32_t o=bclen-p1-4;memcpy(bytecode+p1,&o,4);}
            // Patch all BREAK jumps
            loop_sp--;
            for(int bi=0;bi<loop_stack[loop_sp].break_count;bi++){
                int patch=loop_stack[loop_sp].break_patches[bi];
                int32_t o=bclen-patch-4;memcpy(bytecode+patch,&o,4);
            }
            // Patch all CONTINUE jumps to increment step
            for(int ci=0;ci<loop_stack[loop_sp].continue_count;ci++){
                int patch=loop_stack[loop_sp].continue_patches[ci];
                int32_t o=increment_pos-patch-4;memcpy(bytecode+patch,&o,4);
            }
        }
        if(tp<tn&&tks[tp].type==T_END)tp++;
        return;
    }
    if(t->type==T_FUNC){
        tp++;
        // Parse: FUNC! name param1 param2 ... :  body  END!
        if(tp<tn && tks[tp].type==T_IDENT) {
            char fname[64]; strncpy(fname, tks[tp].txt, 63); fname[63]=0;
            int fi = ft_add(fname, bclen);
            func_table[fi].entry_varcount = varcount;
            tp++;
            // Parse parameters
            while(tp<tn && tks[tp].type!=T_COLON && tks[tp].type!=T_END && tks[tp].type!=T_EOF) {
                if(tks[tp].type==T_IDENT) {
                    ft_add_param(fi, tks[tp].txt);
                }
                tp++;
            }
            if(tp<tn && tks[tp].type==T_COLON) tp++;
            // Emit JUMP over body
            bc(OP_JUMP); int skip_patch=bclen; bc32(0);
            // Record correct function address (after the JUMP)
            func_table[fi].addr = bclen;
            // Compile body
            compile_block();
            // Record local variable count for this function
            func_table[fi].local_count = varcount - func_table[fi].entry_varcount;
            // Implicit return 0
            bc(OP_PUSH_INT); bc64(0); bc(OP_RET);
            // Patch JUMP to skip over body
            {int32_t o=bclen-skip_patch-4; memcpy(bytecode+skip_patch, &o, 4);}
            if(tp<tn && tks[tp].type==T_END) tp++;
        }
        return;
    }
    if(t->type==T_RETURN){
        tp++;
        if(tp<tn&&tks[tp].type!=T_END&&tks[tp].type!=T_EOF)compile_expr();
        else bc(OP_PUSH_INT),bc64(0);
        bc(OP_RET);return;
    }
    // Expression statement
    compile_expr();
}

static void compile_block(void) {
    while(tp<tn&&tks[tp].type!=T_END&&tks[tp].type!=T_ELSE&&tks[tp].type!=T_ELSEIF&&tks[tp].type!=T_CATCH&&tks[tp].type!=T_FINALLY&&tks[tp].type!=T_EOF)compile_stmt();
}

// ============================================================================
// VM EXECUTION
// ============================================================================

#define VM_STACK_SIZE 4096
#define VM_VAR_SIZE 4096
#define VM_CALL_STACK_SIZE 256
#define VM_MAX_INSTRUCTIONS 2000000000LL

static Value vm_stack[VM_STACK_SIZE];
static int vm_sp=0;
static Value vm_vars[VM_VAR_SIZE];
static int vm_var_sp=0;
static int vm_var_base=0;
static int vm_running=1;
static int g_argc=0;
static char** g_argv=NULL;

// Error state
static char vm_error_msg[256]= {0};
static int vm_has_error=0;

// VM exception handler stack
typedef struct { int handler_ip; int saved_sp; int saved_call_sp; } VMTryFrame;
static VMTryFrame vm_try_stack[32];
static int vm_try_sp=0;

typedef struct { int ret_ip; int var_base; int var_sp; int saved_var_idx[256]; Value saved_vars[256]; int saved_count; } VMCallFrame;
static VMCallFrame vm_call_stack[VM_CALL_STACK_SIZE];
static int vm_call_sp=0;

// VM error handling
static int vm_handler_ip = -1; // Set by OP_TRY, checked by errors
static void vm_set_error(const char* msg) {
    snprintf(vm_error_msg, 256, "%s", msg);
    // Check if we have a try handler
    if(vm_try_sp > 0) {
        vm_try_sp--;
        vm_sp = vm_try_stack[vm_try_sp].saved_sp;
        vm_call_sp = vm_try_stack[vm_try_sp].saved_call_sp;
        // Push error message on stack
        vm_stack[vm_sp++] = val_string_v(msg);
        // Signal to vm_exec to jump
        vm_handler_ip = vm_try_stack[vm_try_sp].handler_ip;
        vm_has_error = 0; // Clear error so VM continues
    } else {
        vm_has_error = 1;
    }
}

static void vm_push(Value v) {
    if(vm_sp >= VM_STACK_SIZE) {
        vm_set_error("Stack overflow");
        return;
    }
    vm_stack[vm_sp++] = v;
}

static Value vm_pop(void) {
    if(vm_sp <= 0) {
        vm_set_error("Stack underflow");
        return val_null_v();
    }
    return vm_stack[--vm_sp];
}

static void vm_exec(uint8_t* code, int len, char strtable[][256], int strcount) {
    int ip=0;
    long long ins_count=0;
    vm_has_error = 0;
    vm_error_msg[0] = 0;
    vm_handler_ip = -1;

    while(ip<len && !vm_has_error){
        // Check if we need to jump to exception handler
        if(vm_handler_ip >= 0) {
            ip = vm_handler_ip;
            vm_handler_ip = -1;
            continue;
        }
        uint8_t op=code[ip];
        ins_count++;
        if(ins_count>VM_MAX_INSTRUCTIONS) {
            fprintf(stderr, "Runtime error: instruction limit exceeded (%lld instructions)\n", VM_MAX_INSTRUCTIONS);
            return;
        }
        ip++;
        switch(op){
        case OP_PUSH_INT:{int64_t v;memcpy(&v,code+ip,8);ip+=8;vm_push(val_int_v(v));}break;
        case OP_PUSH_STR:{int32_t si;memcpy(&si,code+ip,4);ip+=4;
            if(si>=0 && si<strcount) vm_push(val_string_v(strtable[si]));
            else { vm_set_error("Invalid string index"); return; }
        }break;
        case OP_PUSH_BOOL:{uint8_t b=code[ip++];vm_push(val_bool_v(b));}break;
        case OP_PUSH_NULL:{vm_push(val_null_v());}break;
        case OP_ADD:{Value b=vm_pop(),a=vm_pop();
            if(a.type==VAL_ARRAY&&b.type==VAL_ARRAY){
                ValueArray*aa=a.as.a,*ba=b.as.a;
                int nc=aa->count+ba->count;
                ValueArray*result=calloc(1,sizeof(ValueArray));
                result->cap=nc>0?nc:8;result->items=calloc(result->cap,sizeof(Value));result->count=0;
                for(int i=0;i<aa->count;i++)result->items[result->count++]=val_copy(aa->items[i]);
                for(int i=0;i<ba->count;i++)result->items[result->count++]=val_copy(ba->items[i]);
                Value vr={VAL_ARRAY};vr.as.a=result;vm_push(vr);val_free(a);val_free(b);
            } else if(a.type==VAL_ARRAY){
                ValueArray*aa=a.as.a;
                int nc=aa->count+1;
                ValueArray*result=calloc(1,sizeof(ValueArray));
                result->cap=nc;result->items=calloc(result->cap,sizeof(Value));result->count=0;
                for(int i=0;i<aa->count;i++)result->items[result->count++]=val_copy(aa->items[i]);
                result->items[result->count++]=val_copy(b);
                Value vr={VAL_ARRAY};vr.as.a=result;vm_push(vr);val_free(a);val_free(b);
            } else if(b.type==VAL_ARRAY){
                ValueArray*ba=b.as.a;
                int nc=1+ba->count;
                ValueArray*result=calloc(1,sizeof(ValueArray));
                result->cap=nc;result->items=calloc(result->cap,sizeof(Value));result->count=0;
                result->items[result->count++]=val_copy(a);
                for(int i=0;i<ba->count;i++)result->items[result->count++]=val_copy(ba->items[i]);
                Value vr={VAL_ARRAY};vr.as.a=result;vm_push(vr);val_free(a);val_free(b);
            } else if(a.type==VAL_INT&&b.type==VAL_INT)vm_push(val_int_v(a.as.i+b.as.i));
            else{Value sa=val_to_string(a),sb=val_to_string(b);
                int len2=(int)strlen(sa.as.s)+(int)strlen(sb.as.s)+1;
                char*buf=malloc(len2);strcpy(buf,sa.as.s);strcat(buf,sb.as.s);
                val_free(sa);val_free(sb);val_free(a);val_free(b);
                vm_push(val_string_v(buf));free(buf);}
        }break;
        case OP_SUB:{Value b=vm_pop(),a=vm_pop();
            if(a.type==VAL_INT&&b.type==VAL_INT) vm_push(val_int_v(a.as.i-b.as.i));
            else vm_push(val_int_v(0));
            val_free(a);val_free(b);}break;
        case OP_MUL:{Value b=vm_pop(),a=vm_pop();
            if(a.type==VAL_INT&&b.type==VAL_INT) vm_push(val_int_v(a.as.i*b.as.i));
            else vm_push(val_int_v(0));
            val_free(a);val_free(b);}break;
        case OP_DIV:{Value b=vm_pop(),a=vm_pop();
            if(a.type!=VAL_INT||b.type!=VAL_INT){vm_set_error("Division requires integers");val_free(a);val_free(b);}
            else if(b.as.i==0){vm_set_error("Division by zero");val_free(a);val_free(b);}
            else{vm_push(val_int_v(a.as.i/b.as.i));val_free(a);val_free(b);}
        }break;
        case OP_MOD:{Value b=vm_pop(),a=vm_pop();
            if(a.type!=VAL_INT||b.type!=VAL_INT){vm_set_error("Modulo requires integers");val_free(a);val_free(b);}
            else if(b.as.i==0){vm_set_error("Modulo by zero");val_free(a);val_free(b);}
            else{vm_push(val_int_v(a.as.i%b.as.i));val_free(a);val_free(b);}
        }break;
        case OP_NEG:{Value a=vm_pop();vm_push(val_int_v(-a.as.i));val_free(a);}break;
        case OP_EQ:{Value b=vm_pop(),a=vm_pop();
            int eq=(a.type==b.type)?(
                a.type==VAL_NULL?1:a.type==VAL_INT?a.as.i==b.as.i:
                a.type==VAL_BOOL?a.as.b==b.as.b:a.type==VAL_STRING?strcmp(a.as.s,b.as.s)==0:0):0;
            vm_push(val_bool_v(eq));val_free(a);val_free(b);
        }break;
        case OP_NEQ:{Value b=vm_pop(),a=vm_pop();
            int eq=(a.type==b.type)?(
                a.type==VAL_NULL?1:a.type==VAL_INT?a.as.i==b.as.i:
                a.type==VAL_BOOL?a.as.b==b.as.b:a.type==VAL_STRING?strcmp(a.as.s,b.as.s)==0:0):0;
            vm_push(val_bool_v(!eq));val_free(a);val_free(b);
        }break;
        case OP_LT:{Value b=vm_pop(),a=vm_pop();
            if(a.type==VAL_INT&&b.type==VAL_INT) vm_push(val_bool_v(a.as.i<b.as.i));
            else if(a.type==VAL_STRING&&b.type==VAL_STRING) vm_push(val_bool_v(strcmp(a.as.s,b.as.s)<0));
            else vm_push(val_bool_v(0));
            val_free(a);val_free(b);}break;
        case OP_GT:{Value b=vm_pop(),a=vm_pop();
            if(a.type==VAL_INT&&b.type==VAL_INT) vm_push(val_bool_v(a.as.i>b.as.i));
            else if(a.type==VAL_STRING&&b.type==VAL_STRING) vm_push(val_bool_v(strcmp(a.as.s,b.as.s)>0));
            else vm_push(val_bool_v(0));
            val_free(a);val_free(b);}break;
        case OP_LTE:{Value b=vm_pop(),a=vm_pop();
            if(a.type==VAL_INT&&b.type==VAL_INT) vm_push(val_bool_v(a.as.i<=b.as.i));
            else vm_push(val_bool_v(0));
            val_free(a);val_free(b);}break;
        case OP_GTE:{Value b=vm_pop(),a=vm_pop();
            if(a.type==VAL_INT&&b.type==VAL_INT) vm_push(val_bool_v(a.as.i>=b.as.i));
            else vm_push(val_bool_v(0));
            val_free(a);val_free(b);}break;
        case OP_AND:{Value b=vm_pop(),a=vm_pop();vm_push(val_bool_v(val_truthy(a)&&val_truthy(b)));val_free(a);val_free(b);}break;
        case OP_OR:{Value b=vm_pop(),a=vm_pop();vm_push(val_bool_v(val_truthy(a)||val_truthy(b)));val_free(a);val_free(b);}break;
        case OP_NOT:{Value a=vm_pop();vm_push(val_bool_v(!val_truthy(a)));val_free(a);}break;
        case OP_BITAND:{Value b=vm_pop(),a=vm_pop();vm_push(val_int_v(a.as.i&b.as.i));val_free(a);val_free(b);}break;
        case OP_BITOR:{Value b=vm_pop(),a=vm_pop();vm_push(val_int_v(a.as.i|b.as.i));val_free(a);val_free(b);}break;
        case OP_LSHIFT:{Value b=vm_pop(),a=vm_pop();vm_push(val_int_v(a.as.i<<(int)b.as.i));val_free(a);val_free(b);}break;
        case OP_RSHIFT:{Value b=vm_pop(),a=vm_pop();vm_push(val_int_v(a.as.i>>(int)b.as.i));val_free(a);val_free(b);}break;
        case OP_STORE:{int32_t idx;memcpy(&idx,code+ip,4);ip+=4;
            int vi=vm_var_base+idx;
            if(vi<0||vi>=VM_VAR_SIZE){vm_set_error("Variable index out of bounds");break;}
            val_free(vm_vars[vi]);vm_vars[vi]=vm_pop();
        }break;
        case OP_LOAD:{int32_t idx;memcpy(&idx,code+ip,4);ip+=4;
            int vi=vm_var_base+idx;
            if(vi<0||vi>=VM_VAR_SIZE){vm_set_error("Variable index out of bounds");break;}
            Value v=vm_vars[vi];
            if(v.type==VAL_STRING)vm_push(val_string_v(v.as.s));
            else if(v.type==VAL_ARRAY){
                ValueArray* src=v.as.a;
                ValueArray* dst=calloc(1,sizeof(ValueArray));
                dst->cap=src->count>0?src->count:8;
                dst->items=calloc(dst->cap,sizeof(Value));
                dst->count=src->count;
                for(int i=0;i<src->count;i++)dst->items[i]=val_copy(src->items[i]);
                Value rv={VAL_ARRAY};rv.as.a=dst;vm_push(rv);
            } else vm_push(v);
        }break;
        case OP_PRINT:{Value v=vm_pop();Value s=val_to_string(v);
            printf("%s\n",s.as.s);
            val_free(s);val_free(v);
        }break;
        case OP_JUMP:{int32_t off;memcpy(&off,code+ip,4);ip+=4;ip+=off;}break;
        case OP_JUMP_IFNOT:{int32_t off;memcpy(&off,code+ip,4);ip+=4;Value v=vm_pop();
            if(!val_truthy(v))ip+=off;
            val_free(v);}break;
        case OP_ARRAY_NEW:{int32_t count;memcpy(&count,code+ip,4);ip+=4;
            Value arr={VAL_ARRAY};arr.as.a=calloc(1,sizeof(ValueArray));
            arr.as.a->cap=count>0?count:8;arr.as.a->items=calloc(arr.as.a->cap,sizeof(Value));arr.as.a->count=0;
            for(int i=0;i<count;i++)arr.as.a->items[arr.as.a->count++]=vm_pop();
            // Reverse
            for(int i=0;i<arr.as.a->count/2;i++){Value tmp=arr.as.a->items[i];arr.as.a->items[i]=arr.as.a->items[arr.as.a->count-1-i];arr.as.a->items[arr.as.a->count-1-i]=tmp;}
            vm_push(arr);
        }break;
        case OP_ARRAY_GET:{Value idx=vm_pop(),arr=vm_pop();
            if(arr.type==VAL_ARRAY && idx.type==VAL_INT){
                int i=(int)idx.as.i;
                if(i>=0 && i<arr.as.a->count){
                    Value v=arr.as.a->items[i];
                    if(v.type==VAL_STRING) vm_push(val_string_v(v.as.s));
                    else vm_push(v);
                } else { vm_push(val_null_v()); }
            } else { vm_push(val_null_v()); }
            val_free(arr);val_free(idx);
        }break;
        case OP_TOSTR:{Value v=vm_pop();Value s=val_to_string(v);val_free(v);vm_push(s);}break;
        case OP_TONUM:{Value v=vm_pop();
            if(v.type==VAL_STRING){int64_t n=atoll(v.as.s);val_free(v);vm_push(val_int_v(n));}
            else if(v.type==VAL_INT){vm_push(v);}
            else{val_free(v);vm_push(val_int_v(0));}
        }break;
        case OP_TYPEOF:{Value v=vm_pop();const char*tn2=val_type_name(v);vm_push(val_string_v(tn2));val_free(v);}break;
        case OP_ARRAY_LEN:{Value v=vm_pop();
            if(v.type==VAL_ARRAY){int c=v.as.a->count;vm_push(val_int_v(c));val_free(v);}
            else if(v.type==VAL_STRING){int c=(int)strlen(v.as.s);vm_push(val_int_v(c));val_free(v);}
            else{val_free(v);vm_push(val_int_v(0));}
        }break;
        case OP_ABS:{Value v=vm_pop();if(v.type==VAL_INT&&v.as.i<0)v.as.i=-v.as.i;vm_push(v);}break;
        case OP_MIN:{Value b=vm_pop(),a=vm_pop();
            int64_t va=a.type==VAL_INT?a.as.i:0, vb=b.type==VAL_INT?b.as.i:0;
            vm_push(val_int_v(va<vb?va:vb));val_free(a);val_free(b);}break;
        case OP_MAX:{Value b=vm_pop(),a=vm_pop();
            int64_t va=a.type==VAL_INT?a.as.i:0, vb=b.type==VAL_INT?b.as.i:0;
            vm_push(val_int_v(va>vb?va:vb));val_free(a);val_free(b);}break;
        case OP_SQRT:{Value v=vm_pop();
            double d=v.type==VAL_INT?(double)v.as.i:0;
            vm_push(val_int_v((int64_t)sqrt(d)));val_free(v);}break;
        case OP_POW:{Value b=vm_pop(),a=vm_pop();
            double base=a.type==VAL_INT?(double)a.as.i:0;
            double exp=b.type==VAL_INT?(double)b.as.i:0;
            vm_push(val_int_v((int64_t)pow(base,exp)));val_free(a);val_free(b);}break;
        case OP_FLOOR:{Value v=vm_pop();
            if(v.type==VAL_INT)vm_push(v);
            else{val_free(v);vm_push(val_int_v(0));}}break;
        case OP_CEIL:{Value v=vm_pop();
            if(v.type==VAL_INT)vm_push(v);
            else{val_free(v);vm_push(val_int_v(0));}}break;
        case OP_ROUND:{Value v=vm_pop();
            if(v.type==VAL_INT)vm_push(v);
            else{val_free(v);vm_push(val_int_v(0));}}break;
        case OP_READ_FILE:{Value v=vm_pop();
            if(v.type==VAL_STRING){
                FILE*f=fopen(v.as.s,"rb");
                if(f){fseek(f,0,SEEK_END);long fsize=ftell(f);
                    if(fsize<0){fclose(f);vm_push(val_string_v(""));}
                    else{fseek(f,0,SEEK_SET);
                    char*buf=malloc(fsize+1);size_t read=fread(buf,1,fsize,f);buf[read]=0;fclose(f);
                    vm_push(val_string_v(buf));free(buf);}}
                else{vm_set_error("Cannot open file");vm_push(val_string_v(""));}
            }else{val_free(v);vm_set_error("READ_FILE requires string argument");vm_push(val_string_v(""));}}break;
        case OP_WRITE_FILE:{Value v2=vm_pop(),v1=vm_pop();
            if(v1.type==VAL_STRING&&v2.type==VAL_STRING){
                FILE*f=fopen(v1.as.s,"wb");
                if(f){fwrite(v2.as.s,1,strlen(v2.as.s),f);fclose(f);}
                else{vm_set_error("Cannot write file");}
            }
            val_free(v1);val_free(v2);vm_push(val_int_v(0));}break;
        case OP_WRITE_BYTES:{Value arr=vm_pop(),fn=vm_pop();
            if(fn.type==VAL_STRING&&arr.type==VAL_ARRAY){
                FILE*f=fopen(fn.as.s,"wb");
                if(f){
                    for(int i=0;i<arr.as.a->count;i++){
                        uint8_t b=(uint8_t)(arr.as.a->items[i].as.i&0xFF);
                        fwrite(&b,1,1,f);
                    }
                    fclose(f);
                } else { vm_set_error("Cannot write file"); }
            }
            val_free(fn);val_free(arr);vm_push(val_int_v(0));}break;
        case OP_ARRAY_PUSH:{Value val=vm_pop(),arr=vm_pop();
            if(arr.type==VAL_ARRAY){
                if(arr.as.a->count>=arr.as.a->cap){
                    int newcap=arr.as.a->cap*2;
                    Value* newitems=realloc(arr.as.a->items,newcap*sizeof(Value));
                    if(!newitems){vm_set_error("Out of memory");val_free(val);val_free(arr);break;}
                    arr.as.a->items=newitems;
                    arr.as.a->cap=newcap;
                }
                arr.as.a->items[arr.as.a->count++]=val;
            } else val_free(val);
            vm_push(arr);
        }break;
        case OP_ARRAY_POP:{Value arr=vm_pop();
            if(arr.type==VAL_ARRAY && arr.as.a->count>0){
                Value v=arr.as.a->items[--arr.as.a->count];
                if(v.type==VAL_STRING)vm_push(val_string_v(v.as.s));
                else if(v.type==VAL_ARRAY) vm_push(val_copy(v));
                else vm_push(v);
            } else vm_push(val_null_v());
            val_free(arr);
        }break;
        case OP_ARRAY_SET:{Value val=vm_pop(),idx=vm_pop(),arr=vm_pop();
            if(arr.type==VAL_ARRAY && idx.type==VAL_INT){
                int i=(int)idx.as.i;
                if(i>=0 && i<arr.as.a->count){val_free(arr.as.a->items[i]);arr.as.a->items[i]=val;}
                else val_free(val);
            } else val_free(val);
            vm_push(arr);
        }break;
        case OP_SUBSTR:{Value len=vm_pop(),start=vm_pop(),str=vm_pop();
            if(str.type==VAL_STRING && start.type==VAL_INT && len.type==VAL_INT){
                int s=(int)start.as.i, l=(int)len.as.i, slen=(int)strlen(str.as.s);
                if(s<0)s=0; if(s>slen)s=slen; if(s+l>slen)l=slen-s;
                if(l<0)l=0;
                char*buf=malloc(l+1);memcpy(buf,str.as.s+s,l);buf[l]=0;
                vm_push(val_string_v(buf));free(buf);
            } else { vm_push(val_string_v("")); }
            val_free(str);val_free(start);val_free(len);
        }break;
        case OP_CHAR_AT:{Value idx=vm_pop(),str=vm_pop();
            if(str.type==VAL_STRING && idx.type==VAL_INT){
                int i=(int)idx.as.i; int slen=(int)strlen(str.as.s);
                if(i>=0 && i<slen){vm_push(val_int_v((int)(unsigned char)str.as.s[i]));}
                else vm_push(val_int_v(0));
            } else vm_push(val_int_v(0));
            val_free(str);val_free(idx);
        }break;
        case OP_TO_UPPER:{Value v=vm_pop();
            if(v.type==VAL_STRING){char*buf=strdup(v.as.s);for(char*p=buf;*p;p++)*p=(char)toupper((unsigned char)*p);vm_push(val_string_v(buf));free(buf);}
            else vm_push(v);
        }break;
        case OP_TO_LOWER:{Value v=vm_pop();
            if(v.type==VAL_STRING){char*buf=strdup(v.as.s);for(char*p=buf;*p;p++)*p=(char)tolower((unsigned char)*p);vm_push(val_string_v(buf));free(buf);}
            else vm_push(v);
        }break;
        case OP_STR_EQ:{Value b=vm_pop(),a=vm_pop();
            int eq=0;
            if(a.type==VAL_STRING && b.type==VAL_STRING) eq=(strcmp(a.as.s,b.as.s)==0);
            vm_push(val_bool_v(eq));val_free(a);val_free(b);
        }break;
        case OP_DUP:{Value v=vm_stack[vm_sp-1];
            if(v.type==VAL_STRING) vm_push(val_string_v(v.as.s));
            else if(v.type==VAL_ARRAY) vm_push(val_copy(v));
            else vm_push(v);
        }break;
        case OP_SWAP:{Value b=vm_pop(),a=vm_pop();vm_push(b);vm_push(a);}break;
        case OP_EXIT:{int code2=0;if(vm_sp>0){Value v=vm_pop();if(v.type==VAL_INT)code2=(int)v.as.i;val_free(v);}exit(code2);}break;
        case OP_CHAR:{Value v=vm_pop();
            if(v.type==VAL_INT){char buf[2]={(char)v.as.i,0};vm_push(val_string_v(buf));}
            else{val_free(v);vm_push(val_string_v(""));}
        }break;
        case OP_ORD:{Value v=vm_pop();
            if(v.type==VAL_STRING && strlen(v.as.s)>0){vm_push(val_int_v((int)(unsigned char)v.as.s[0]));val_free(v);}
            else{val_free(v);vm_push(val_int_v(0));}
        }break;
        case OP_THROW:{Value v=vm_pop();
            if(vm_try_sp > 0) {
                // Set error and let vm_set_error handle the jump
                vm_set_error(v.type==VAL_STRING ? v.as.s : "Exception thrown");
                val_free(v);
            } else {
                fprintf(stderr, "Uncaught exception: ");
                if(v.type==VAL_STRING) fprintf(stderr, "%s\n", v.as.s);
                else { Value s=val_to_string(v); fprintf(stderr, "%s\n", s.as.s); val_free(s); }
                val_free(v);
                vm_has_error = 1;
            }
        }break;
        case OP_TRY:{int32_t handler_off;memcpy(&handler_off,code+ip,4);ip+=4;
            // Push handler onto try stack
            if(vm_try_sp < 32) {
                vm_try_stack[vm_try_sp].handler_ip = ip + handler_off;
                vm_try_stack[vm_try_sp].saved_sp = vm_sp;
                vm_try_stack[vm_try_sp].saved_call_sp = vm_call_sp;
                vm_try_sp++;
            }
        }break;
        case OP_CATCH:{/* handled by compiler with JUMP patching */}break;
        case OP_FINALLY:{/* handled by compiler with JUMP patching */}break;
        case OP_ENDTRY:{if(vm_try_sp>0)vm_try_sp--;}break;
        case OP_CALL:{int32_t name_idx;memcpy(&name_idx,code+ip,4);ip+=4;
            int32_t arity;memcpy(&arity,code+ip,4);ip+=4;
            if(name_idx<0||name_idx>=strcount){vm_set_error("Invalid function name index");break;}
            const char* name=strings[name_idx];
            // Built-in functions
            if(!strcmp(name,"LEN")){Value v=vm_pop();
                if(v.type==VAL_STRING){vm_push(val_int_v((int64_t)strlen(v.as.s)));val_free(v);}
                else if(v.type==VAL_ARRAY){vm_push(val_int_v(v.as.a->count));val_free(v);}
                else{val_free(v);vm_push(val_int_v(0));}
            } else if(!strcmp(name,"TYPEOF")){Value v=vm_pop();vm_push(val_string_v(val_type_name(v)));val_free(v);}
            else if(!strcmp(name,"TO_STRING")){Value v=vm_pop();vm_push(val_to_string(v));val_free(v);}
            else if(!strcmp(name,"TO_NUMBER")){Value v=vm_pop();
                if(v.type==VAL_STRING){int64_t n=atoll(v.as.s);val_free(v);vm_push(val_int_v(n));}
                else if(v.type==VAL_INT){vm_push(v);}
                else{val_free(v);vm_push(val_int_v(0));}
            } else if(!strcmp(name,"RANDOM")){for(int i=0;i<arity;i++)val_free(vm_pop());vm_push(val_int_v(rand()%100));}
            else if(!strcmp(name,"TIME")){for(int i=0;i<arity;i++)val_free(vm_pop());vm_push(val_int_v((int64_t)time(NULL)));}
            else if(!strcmp(name,"ABS")){Value v=vm_pop();if(v.type==VAL_INT&&v.as.i<0)v.as.i=-v.as.i;vm_push(v);}
            else if(!strcmp(name,"ARGUMENT_COUNT")){for(int i=0;i<arity;i++)val_free(vm_pop());vm_push(val_int_v(g_argc));}
            else if(!strcmp(name,"ARGUMENT")){Value v=vm_pop();
                if(v.type==VAL_INT && v.as.i>=0 && v.as.i<g_argc){
                    vm_push(val_string_v(g_argv[v.as.i]));
                } else { val_free(v); vm_push(val_string_v("")); }
            } else if(!strcmp(name,"CHAR")){Value v=vm_pop();
                if(v.type==VAL_INT){char buf[2]={(char)v.as.i,0};vm_push(val_string_v(buf));}
                else{val_free(v);vm_push(val_string_v(""));}
            } else if(!strcmp(name,"ORD")){Value v=vm_pop();
                if(v.type==VAL_STRING && strlen(v.as.s)>0){vm_push(val_int_v((int)(unsigned char)v.as.s[0]));val_free(v);}
                else{val_free(v);vm_push(val_int_v(0));}
            } else if(!strcmp(name,"READ_FILE")){Value v=vm_pop();
                if(v.type==VAL_STRING){
                    FILE*f=fopen(v.as.s,"rb");
                    if(f){fseek(f,0,SEEK_END);long fsize=ftell(f);
                        if(fsize<0){fclose(f);vm_push(val_string_v(""));}
                        else{fseek(f,0,SEEK_SET);
                        char*buf=malloc(fsize+1);size_t r=fread(buf,1,fsize,f);buf[r]=0;fclose(f);
                        vm_push(val_string_v(buf));free(buf);}}
                    else{vm_set_error("Cannot open file");vm_push(val_string_v(""));}
                }else{val_free(v);vm_set_error("READ_FILE requires string");vm_push(val_string_v(""));}
            } else if(!strcmp(name,"WRITE_FILE")){Value v2=vm_pop(),v1=vm_pop();
                if(v1.type==VAL_STRING&&v2.type==VAL_STRING){
                    FILE*f=fopen(v1.as.s,"wb");
                    if(f){fwrite(v2.as.s,1,strlen(v2.as.s),f);fclose(f);}
                    else{vm_set_error("Cannot write file");}
                }
                val_free(v1);val_free(v2);vm_push(val_int_v(0));
            } else if(!strcmp(name,"WRITE_BYTES")){Value arr=vm_pop(),fn=vm_pop();
                if(fn.type==VAL_STRING&&arr.type==VAL_ARRAY){
                    FILE*f=fopen(fn.as.s,"wb");
                    if(f){
                        for(int i=0;i<arr.as.a->count;i++){
                            uint8_t b=(uint8_t)(arr.as.a->items[i].as.i&0xFF);
                            fwrite(&b,1,1,f);
                        }
                        fclose(f);
                    } else { vm_set_error("Cannot write file"); }
                }
                val_free(fn);val_free(arr);vm_push(val_int_v(0));
            } else if(!strcmp(name,"FFI_LOAD")){Value path_val=vm_pop(),name_val=vm_pop();
                if(name_val.type==VAL_STRING&&path_val.type==VAL_STRING){
                    ffi_load_lib(name_val.as.s,path_val.as.s);
                    val_free(name_val);val_free(path_val);vm_push(val_int_v(0));
                }else{fprintf(stderr,"FFI_LOAD requires two string arguments\n");
                    val_free(name_val);val_free(path_val);vm_push(val_int_v(-1));}
            } else if(!strcmp(name,"FFI_REGISTER")){Value pc_val=vm_pop(),rt_val=vm_pop(),fn_val=vm_pop(),ln_val=vm_pop();
                if(ln_val.type==VAL_STRING&&fn_val.type==VAL_STRING&&rt_val.type==VAL_INT&&pc_val.type==VAL_INT){
                    int rc=ffi_register_func(ln_val.as.s,fn_val.as.s,(NbsFFIType)rt_val.as.i,(int)pc_val.as.i);
                    val_free(ln_val);val_free(fn_val);val_free(rt_val);val_free(pc_val);vm_push(val_int_v(rc));
                }else{fprintf(stderr,"FFI_REGISTER requires (string, string, int, int)\n");
                    val_free(ln_val);val_free(fn_val);val_free(rt_val);val_free(pc_val);vm_push(val_int_v(-1));}
            } else if(!strcmp(name,"FFI_CALL")){int ffi_argc=arity-2;if(ffi_argc<0)ffi_argc=0;
                Value ffi_args[16];
                for(int i=ffi_argc-1;i>=0;i--) ffi_args[i]=vm_pop();
                Value fn_val=vm_pop(),ln_val=vm_pop();
                Value result=val_int_v(0);
                if(ln_val.type==VAL_STRING&&fn_val.type==VAL_STRING){
                    NbsFFILib*lib=NULL;NbsFFIFunc*func=NULL;
                    for(int i=0;i<ffi_lib_count;i++){
                        if(strcmp(ffi_libs[i].name,ln_val.as.s)==0){lib=&ffi_libs[i];break;}
                    }
                    if(lib){for(int j=0;j<lib->func_count;j++){
                        if(strcmp(lib->functions[j].name,fn_val.as.s)==0){func=&lib->functions[j];break;}
                    }}
                    if(lib&&func){
                        void*fn=ffi_resolve_func(lib,func);
                        if(fn){
                            intptr_t vals[16];
                            for(int k=0;k<ffi_argc&&k<16;k++){
                                if(ffi_args[k].type==VAL_INT) vals[k]=(intptr_t)ffi_args[k].as.i;
                                else if(ffi_args[k].type==VAL_STRING) vals[k]=(intptr_t)ffi_args[k].as.s;
                                else vals[k]=0;
                            }
                            typedef intptr_t(*ffi_fn)();
                            ffi_fn call=(ffi_fn)fn;
                            intptr_t ret=call(
                                ffi_argc>0?vals[0]:0,ffi_argc>1?vals[1]:0,
                                ffi_argc>2?vals[2]:0,ffi_argc>3?vals[3]:0,
                                ffi_argc>4?vals[4]:0,ffi_argc>5?vals[5]:0);
                            switch(func->return_type){
                                case NBS_FFI_INT:case NBS_FFI_VOID:result=val_int_v((int64_t)ret);break;
                                case NBS_FFI_STRING:case NBS_FFI_POINTER:
                                    if(ret)result=val_string_v((const char*)ret);else result=val_null_v();break;
                                default:result=val_int_v((int64_t)ret);break;
                            }
                        }
                    }else{fprintf(stderr,"FFI_CALL: library or function not found: %s.%s\n",ln_val.as.s,fn_val.as.s);}
                }
                for(int i=0;i<ffi_argc;i++)val_free(ffi_args[i]);
                val_free(ln_val);val_free(fn_val);vm_push(result);
            } else {
                // User-defined function
                int fi=ft_find(name);
                if(fi<0){
                    char errmsg[256];snprintf(errmsg,256,"Undefined function '%s'",name);
                    vm_set_error(errmsg);break;
                }
                if(vm_call_sp>=VM_CALL_STACK_SIZE){vm_set_error("Call stack overflow");break;}
                // Save return address + old var_base
                vm_call_stack[vm_call_sp].ret_ip=ip;
                vm_call_stack[vm_call_sp].var_base=vm_var_base;
                vm_call_stack[vm_call_sp].var_sp=vm_var_sp;
                vm_call_stack[vm_call_sp].saved_count=0;
                // Save param slots and local variable slots
                int sc=0;
                // Mark which indices have been saved (to avoid duplicates)
                int saved_flag[256]={0};
                // 1) Save param slots (will be overwritten by args)
                int pcount=func_table[fi].param_count<arity?func_table[fi].param_count:arity;
                for(int i=0;i<pcount;i++){
                    const char* pname=func_table[fi].params[i];
                    int gidx=var_idx(pname);
                    if(gidx>=0 && gidx<256 && !saved_flag[gidx] && sc<256){
                        vm_call_stack[vm_call_sp].saved_var_idx[sc]=gidx;
                        vm_call_stack[vm_call_sp].saved_vars[sc]=vm_vars[gidx];
                        vm_call_stack[vm_call_sp].saved_count=++sc;
                        saved_flag[gidx]=1;
                    }
                }
                // 2) Save local variables (new names created inside function body)
                int ev=func_table[fi].entry_varcount;
                int lc=func_table[fi].local_count;
                for(int i=ev;i<ev+lc && i<256;i++){
                    if(!saved_flag[i] && sc<256){
                        vm_call_stack[vm_call_sp].saved_var_idx[sc]=i;
                        vm_call_stack[vm_call_sp].saved_vars[sc]=vm_vars[i];
                        vm_call_stack[vm_call_sp].saved_count=++sc;
                        saved_flag[i]=1;
                    }
                }
                // Assign params in REVERSE order so params[0] gets leftmost arg
                for(int i=pcount-1;i>=0;i--){
                    const char* pname=func_table[fi].params[i];
                    int gidx=var_idx(pname);
                    if(gidx>=0 && gidx<VM_VAR_SIZE){
                        vm_vars[gidx]=vm_pop();
                    }
                }
                vm_call_sp++;
                // Discard remaining args
                for(int i=arity;i>func_table[fi].param_count;i--)val_free(vm_pop());
                // Jump to function
                ip=func_table[fi].addr;
            }
        }break;
        case OP_RET:{Value v=vm_pop();
            if(vm_call_sp>0){vm_call_sp--;
                // Restore saved global variable slots
                for(int i=0;i<vm_call_stack[vm_call_sp].saved_count;i++){
                    int gidx=vm_call_stack[vm_call_sp].saved_var_idx[i];
                    if(gidx>=0 && gidx<VM_VAR_SIZE){
                        val_free(vm_vars[gidx]);
                        vm_vars[gidx]=vm_call_stack[vm_call_sp].saved_vars[i];
                    }
                }
                ip=vm_call_stack[vm_call_sp].ret_ip;
                vm_var_base=vm_call_stack[vm_call_sp].var_base;
                vm_var_sp=vm_call_stack[vm_call_sp].var_sp;}
            else{vm_push(v);return;}
            vm_push(v);
        }break;
        case OP_IMPORT:{int32_t si;memcpy(&si,code+ip,4);ip+=4;
            const char*path=strings[si];
            static char imp_files[64][256];static int imp_count=0;
            int skip=0;for(int i=0;i<imp_count;i++)if(!strcmp(imp_files[i],path)){skip=1;break;}
            if(skip)break;
            if(imp_count<64){strncpy(imp_files[imp_count],path,255);imp_files[imp_count][255]=0;imp_count++;}
            FILE*f=fopen(path,"rb");
            if(!f){char msg[256];snprintf(msg,256,"Cannot open import '%s'",path);vm_set_error(msg);break;}
            fseek(f,0,SEEK_END);long sz=ftell(f);fseek(f,0,SEEK_SET);
            char*src=malloc(sz+1);size_t r=fread(src,1,sz,f);src[r]=0;fclose(f);
            int saved_bclen=bclen;
            int saved_tn=tn,saved_tp=tp;
            Lx imp_lx={src,0,(int)r,1};
            tn=0;tp=0;
            do{tks[tn++]=lx(&imp_lx);}while(tks[tn-1].type!=T_EOF&&tn<8192);
            while(tp<tn&&tks[tp].type!=T_EOF)compile_stmt();
            int saved_sp=vm_sp;
            int saved_call_sp=vm_call_sp;
            vm_exec(bytecode+saved_bclen,bclen-saved_bclen,strings,strcount);
            vm_sp=saved_sp;
            vm_call_sp=saved_call_sp;
            tn=saved_tn;tp=saved_tp;
            free(src);
        }break;
        case OP_HALT:return;
        default:
            fprintf(stderr, "Runtime error: unknown opcode 0x%02X at ip=%d\n", op, ip-1);
            return;
        }
    }
    if(vm_has_error) {
        fprintf(stderr, "Runtime error: %s\n", vm_error_msg);
    }
}

// ============================================================================
// CLI
// ============================================================================

static void print_version(void) {
    fprintf(stderr, "Nebulara v2.0 - AI-Native Programming Language\n");
    fprintf(stderr, "Usage:\n");
    fprintf(stderr, "  nebulara run <file.nbs>     Execute a .nbs file\n");
    fprintf(stderr, "  nebulara build <file.nbs>   Compile to bytecode\n");
    fprintf(stderr, "  nebulara repl               Interactive REPL\n");
    fprintf(stderr, "  nebulara version            Show version\n");
    fprintf(stderr, "  nebulara help               Show this help\n");
    fprintf(stderr, "  nebulara highlight <file>   Syntax highlight\n");
}

static void cleanup_vm(void) {
    for (int i = 0; i < VM_VAR_SIZE; i++) val_free(vm_vars[i]);
    for (int i = 0; i < vm_sp; i++) val_free(vm_stack[i]);
    memset(vm_vars, 0, sizeof(vm_vars));
    memset(vm_stack, 0, sizeof(vm_stack));
}

static int run_file(const char* path) {
    FILE* f = fopen(path, "rb");
    if (!f) { fprintf(stderr, "Error: cannot open '%s'\n", path); return 1; }
    fseek(f, 0, SEEK_END);
    long len = ftell(f);
    if(len<0){fclose(f);fprintf(stderr,"Error: cannot determine file size\n");return 1;}
    fseek(f, 0, SEEK_SET);
    char* src = (char*)malloc(len + 1);
    if(!src){fclose(f);fprintf(stderr,"Error: out of memory\n");return 1;}
    size_t read=fread(src, 1, len, f);
    src[read] = 0;
    fclose(f);

    // Reset compiler state
    func_count = 0;

    // Lex
    Lx lx_state = {src, 0, (int)read, 1};
    tn = 0; tp = 0;
    do { tks[tn++] = lx(&lx_state); } while (tks[tn-1].type != T_EOF && tn < 8192);

    // Compile
    bclen = 0;
    varcount = 0;
    strcount = 0;
    while (tp < tn && tks[tp].type != T_EOF) compile_stmt();
    bc(OP_HALT);
    fprintf(stderr, "Compiled %d bytes, %d variables, %d strings, %d functions\n", bclen, varcount, strcount, func_count);

    // Reset VM state
    cleanup_vm();
    vm_sp = 0;
    vm_var_sp = 0;
    vm_var_base = 0;
    vm_call_sp = 0;
    vm_running = 1;
    for (int i = 0; i < strcount; i++) vm_vars[i].type = VAL_NULL;

    // Execute
    vm_exec(bytecode, bclen, strings, strcount);

    // Cleanup
    cleanup_vm();
    free(src);
    return vm_has_error ? 1 : 0;
}

static int build_file(const char* path) {
    FILE* f = fopen(path, "rb");
    if (!f) { fprintf(stderr, "Error: cannot open '%s'\n", path); return 1; }
    fseek(f, 0, SEEK_END);
    long len = ftell(f);
    if(len<0){fclose(f);fprintf(stderr,"Error: cannot determine file size\n");return 1;}
    fseek(f, 0, SEEK_SET);
    char* src = (char*)malloc(len + 1);
    if(!src){fclose(f);fprintf(stderr,"Error: out of memory\n");return 1;}
    size_t read=fread(src, 1, len, f);
    src[read] = 0;
    fclose(f);

    // Reset compiler state
    func_count = 0;

    // Lex
    Lx lx_state = {src, 0, (int)read, 1};
    tn = 0; tp = 0;
    do { tks[tn++] = lx(&lx_state); } while (tks[tn-1].type != T_EOF && tn < 8192);

    // Compile
    bclen = 0;
    varcount = 0;
    strcount = 0;
    while (tp < tn && tks[tp].type != T_EOF) compile_stmt();
    bc(OP_HALT);

    // Write bytecode
    char outpath[512];
    snprintf(outpath, sizeof(outpath), "%s.nbsc", path);
    FILE* out = fopen(outpath, "wb");
    if (!out) { fprintf(stderr, "Error: cannot write '%s'\n", outpath); free(src); return 1; }
    // Write header: magic, version, counts
    fwrite("NBS1", 1, 4, out);
    uint32_t ver=2;fwrite(&ver,4,1,out);
    uint32_t bc32=(uint32_t)bclen;fwrite(&bc32,4,1,out);
    uint32_t sc32=(uint32_t)strcount;fwrite(&sc32,4,1,out);
    uint32_t fc32=(uint32_t)func_count;fwrite(&fc32,4,1,out);
    // Write string table
    for(int i=0;i<strcount;i++){
        uint32_t slen=(uint32_t)strlen(strings[i]);
        fwrite(&slen,4,1,out);
        fwrite(strings[i],1,slen,out);
    }
    // Write function table
    for(int i=0;i<func_count;i++){
        uint32_t nlen=(uint32_t)strlen(func_table[i].name);
        fwrite(&nlen,4,1,out);
        fwrite(func_table[i].name,1,nlen,out);
        fwrite(&func_table[i].addr,4,1,out);
        fwrite(&func_table[i].param_count,4,1,out);
        for(int j=0;j<func_table[i].param_count;j++){
            uint32_t plen=(uint32_t)strlen(func_table[i].params[j]);
            fwrite(&plen,4,1,out);
            fwrite(func_table[i].params[j],1,plen,out);
        }
    }
    // Write bytecode
    fwrite(bytecode, 1, bclen, out);
    fclose(out);
    printf("Compiled %s -> %s (%d bytes, %d functions)\n", path, outpath, bclen, func_count);
    free(src);
    return 0;
}

// Syntax highlighting (simple ANSI terminal output)
static int highlight_file(const char* path) {
    FILE* f = fopen(path, "rb");
    if (!f) { fprintf(stderr, "Error: cannot open '%s'\n", path); return 1; }
    fseek(f, 0, SEEK_END);
    long len = ftell(f);
    if(len<0){fclose(f);return 1;}
    fseek(f, 0, SEEK_SET);
    char* src = (char*)malloc(len + 1);
    if(!src){fclose(f);return 1;}
    size_t read=fread(src, 1, len, f);
    src[read] = 0;
    fclose(f);

    Lx lx_state = {src, 0, (int)read, 1};
    int token_count = 0;
    Tk tokens[8192];
    do { tokens[token_count++] = lx(&lx_state); } while (tokens[token_count-1].type != T_EOF && token_count < 8192);

    for(int i=0; i<token_count; i++){
        Tk* t = &tokens[i];
        switch(t->type){
            case T_INT: printf("\033[33m%lld\033[0m", t->ival); break;
            case T_STR: printf("\033[32m\"%s\"\033[0m", t->txt); break;
            case T_PRINT: case T_IF: case T_ELSE: case T_ELSEIF: case T_THEN:
            case T_WHILE: case T_FOR: case T_TO: case T_FUNC: case T_END:
            case T_RETURN: case T_LET: case T_BREAK: case T_CONTINUE:
            case T_AND: case T_OR: case T_NOT:
            case T_TRY: case T_CATCH: case T_THROW: case T_FINALLY:
                printf("\033[36m%s\033[0m", t->txt); break;
            case T_IDENT: printf("\033[37m%s\033[0m", t->txt); break;
            case T_PLUS: case T_MINUS: case T_STAR: case T_SLASH: case T_MOD:
            case T_EQ: case T_NEQ: case T_LT: case T_GT: case T_LTE: case T_GTE:
            case T_ASSIGN: case T_BITAND: case T_BITOR: case T_LSHIFT: case T_RSHIFT:
                printf("\033[35m%s\033[0m", t->txt); break;
            case T_LPAREN: case T_RPAREN: case T_LBRACKET: case T_RBRACKET:
                printf("\033[33m%s\033[0m", t->txt); break;
            case T_COMMA: case T_COLON:
                printf("\033[37m%s\033[0m", t->txt); break;
            case T_EOF: break;
            default: printf("%s", t->txt); break;
        }
        // Add space after tokens (except at line end)
        if(i < token_count-1 && tokens[i].type != T_EOF){
            if(tokens[i].line != tokens[i+1].line) printf("\n");
            else if(tokens[i+1].type != T_COMMA && tokens[i+1].type != T_COLON &&
                    tokens[i].type != T_COMMA && tokens[i].type != T_COLON &&
                    tokens[i].type != T_LPAREN && tokens[i+1].type != T_RPAREN &&
                    tokens[i].type != T_LBRACKET && tokens[i+1].type != T_RBRACKET)
                printf(" ");
        }
    }
    printf("\n");
    free(src);
    return 0;
}

static void repl(void) {
    printf("Nebulara v2.0 > Type 'exit' to quit\n");
    char line[1024];
    // Initialize VM state for REPL
    memset(vm_vars, 0, sizeof(vm_vars));
    func_count = 0;
    while (1) {
        printf(">> ");
        fflush(stdout);
        if (!fgets(line, sizeof(line), stdin)) break;
        // Remove newline
        int len = (int)strlen(line);
        while (len > 0 && (line[len-1]=='\n'||line[len-1]=='\r')) line[--len]=0;
        if (len == 0) continue;
        if (strcmp(line, "exit") == 0 || strcmp(line, "quit") == 0) break;

        // Lex + compile + run inline
        Lx lx_state = {line, 0, len, 1};
        tn = 0; tp = 0;
        do { tks[tn++] = lx(&lx_state); } while (tks[tn-1].type != T_EOF && tn < 8192);

        bclen = 0;
        int saved_varcount = varcount;
        int saved_strcount = strcount;
        while (tp < tn && tks[tp].type != T_EOF) compile_stmt();
        bc(OP_HALT);

        // Reset VM stack (but keep variables for REPL persistence)
        for (int i = 0; i < vm_sp; i++) val_free(vm_stack[i]);
        vm_sp = 0;
        vm_call_sp = 0;
        vm_running = 1;
        vm_has_error = 0;

        vm_exec(bytecode, bclen, strings, strcount);

        if(vm_has_error) fprintf(stderr, "Error: %s\n", vm_error_msg);
    }
    cleanup_vm();
}

int main(int argc, char** argv) {
    if (argc < 2) { print_version(); return 0; }

    // Store global args for ARGUMENT_COUNT/ARGUMENT builtins
    g_argc = argc;
    g_argv = argv;

    if (strcmp(argv[1], "run") == 0) {
        if (argc < 3) { fprintf(stderr, "Usage: nebulara run <file.nbs>\n"); return 1; }
        return run_file(argv[2]);
    } else if (strcmp(argv[1], "build") == 0) {
        if (argc < 3) { fprintf(stderr, "Usage: nebulara build <file.nbs>\n"); return 1; }
        return build_file(argv[2]);
    } else if (strcmp(argv[1], "highlight") == 0) {
        if (argc < 3) { fprintf(stderr, "Usage: nebulara highlight <file.nbs>\n"); return 1; }
        return highlight_file(argv[2]);
    } else if (strcmp(argv[1], "repl") == 0) {
        repl();
        return 0;
    } else if (strcmp(argv[1], "version") == 0) {
        fprintf(stderr, "Nebulara v2.0\n");
        return 0;
    } else if (strcmp(argv[1], "help") == 0) {
        print_version();
        return 0;
    } else {
        // If it's a file, just run it
        return run_file(argv[1]);
    }
}
