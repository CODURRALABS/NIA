/*
 * neb-pipeline.c - Connected Compilation Pipeline
 * 
 * Takes .nbs source -> tokens -> AST -> IR -> JS/Python transpilation
 * Reuses the lexer/parser from nbs-bootstrap.c
 *
 * Build: gcc -o neb-pipeline.exe neb-pipeline.c -static -O2
 * Usage: neb-pipeline.exe <file.nbs> [--target js|py|ir|check]
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>
#include <stdarg.h>
#include <stdint.h>
#include "neb-semantic.c"
#include "neb-ir.c"

/* ============================================================================
 * LEXER (copied from nbs-bootstrap.c, adapted)
 * ============================================================================ */

typedef enum {
    TOK_INT_LIT, TOK_STRING_LIT, TOK_IDENT,
    TOK_FUNC, TOK_DATA, TOK_RUN, TOK_END,
    TOK_IF, TOK_ELSE, TOK_THEN, TOK_WHILE, TOK_FOR, TOK_TO, TOK_STEP,
    TOK_RETURN, TOK_BREAK, TOK_CONTINUE,
    TOK_PRINT, TOK_LET, TOK_CONST,
    TOK_PLUS, TOK_MINUS, TOK_STAR, TOK_SLASH, TOK_PERCENT,
    TOK_EQ, TOK_NEQ, TOK_LT, TOK_GT, TOK_LTE, TOK_GTE,
    TOK_AND, TOK_OR, TOK_NOT, TOK_ASSIGN,
    TOK_DOT, TOK_COMMA, TOK_COLON, TOK_SEMICOLON,
    TOK_LPAREN, TOK_RPAREN, TOK_LBRACKET, TOK_RBRACKET,
    TOK_ELSEIF, TOK_TRUE, TOK_FALSE, TOK_NULL,
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
    if (c >= '0' && c <= '9') {
        int64_t val = 0;
        while (l->pos < l->len && l->src[l->pos] >= '0' && l->src[l->pos] <= '9')
            val = val * 10 + lexer_advance(l) - '0';
        tok.type = TOK_INT_LIT;
        tok.int_val = val;
        sprintf(tok.text, "%lld", val);
        return tok;
    }
    if (c == '"') {
        lexer_advance(l);
        int start = l->pos;
        while (l->pos < l->len && l->src[l->pos] != '"') {
            if (l->src[l->pos] == '\\') l->pos++;
            l->pos++;
        }
        int di = 0;
        for (int si = start; si < l->pos && di < 255; si++) {
            if (l->src[si] == '\\' && si + 1 < l->pos) { si++;
                if (l->src[si] == 'n') tok.text[di++] = '\n';
                else if (l->src[si] == 't') tok.text[di++] = '\t';
                else if (l->src[si] == '\\') tok.text[di++] = '\\';
                else if (l->src[si] == '"') tok.text[di++] = '"';
                else tok.text[di++] = l->src[si];
            } else { tok.text[di++] = l->src[si]; }
        }
        tok.text[di] = 0;
        tok.type = TOK_STRING_LIT;
        if (l->pos < l->len) lexer_advance(l);
        return tok;
    }
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
        if (strcmp(tok.text, "FUNC!") == 0) tok.type = TOK_FUNC;
        else if (strcmp(tok.text, "END!") == 0) tok.type = TOK_END;
        else if (strcmp(tok.text, "IF?") == 0) tok.type = TOK_IF;
        else if (strcmp(tok.text, "ELSE") == 0) tok.type = TOK_ELSE;
        else if (strcmp(tok.text, "ELSEIF?") == 0) tok.type = TOK_ELSEIF;
        else if (strcmp(tok.text, "WHILE?") == 0) tok.type = TOK_WHILE;
        else if (strcmp(tok.text, "FOR!") == 0) tok.type = TOK_FOR;
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
        else if (strcmp(tok.text, "NULL") == 0) { tok.type = TOK_NULL; }
        else if (strcmp(tok.text, "TRUE") == 0) { tok.type = TOK_TRUE; }
        else if (strcmp(tok.text, "FALSE") == 0) { tok.type = TOK_FALSE; }
        else tok.type = TOK_IDENT;
        return tok;
    }
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
        else tok.type = TOK_LT;
    }
    else if (c == '>') {
        if (lexer_peek(l) == '=') { lexer_advance(l); tok.text[1] = '='; tok.text[2] = 0; tok.type = TOK_GTE; }
        else tok.type = TOK_GT;
    }
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

/* ============================================================================
 * AST (subset needed for pipeline)
 * ============================================================================ */

typedef enum {
    NODE_INT, NODE_STRING, NODE_IDENT, NODE_BINARY, NODE_UNARY,
    NODE_TRUE, NODE_FALSE, NODE_NULL,
    NODE_ASSIGN, NODE_PRINT, NODE_BLOCK, NODE_IF, NODE_WHILE, NODE_FOR,
    NODE_FUNC_DEF, NODE_FUNC_CALL, NODE_RETURN, NODE_BREAK, NODE_CONTINUE,
    NODE_ARRAY_LIT, NODE_ARRAY_INDEX, NODE_ARRAY_LEN,
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
    ASTNode* third;
    ASTNode** children;
    int child_count;
    char params[8][128];
    int param_count;
    int line;
};

ASTNode* ast_new(NodeType type) {
    ASTNode* n = (ASTNode*)calloc(1, sizeof(ASTNode));
    n->type = type;
    return n;
}

/* ============================================================================
 * PARSER (subset: expressions, statements, blocks)
 * ============================================================================ */

typedef struct {
    NbsToken tokens[4096];
    int pos, count;
} Parser;

NbsToken parser_peek(Parser* p) {
    if (p->pos >= p->count) return (NbsToken){TOK_EOF};
    return p->tokens[p->pos];
}
NbsToken parser_advance(Parser* p) { return p->tokens[p->pos++]; }

int get_precedence(NbsTokenType t) {
    switch (t) {
        case TOK_OR: return 1; case TOK_AND: return 2;
        case TOK_EQ: case TOK_NEQ: return 3;
        case TOK_LT: case TOK_GT: case TOK_LTE: case TOK_GTE: return 4;
        case TOK_PLUS: case TOK_MINUS: return 5;
        case TOK_STAR: case TOK_SLASH: case TOK_PERCENT: return 6;
        case TOK_NOT: return 7;
        default: return 0;
    }
}

ASTNode* parse_expression(Parser* p);
ASTNode* parse_primary(Parser* p) {
    NbsToken tok = parser_peek(p);
    if (tok.type == TOK_INT_LIT) { parser_advance(p); ASTNode* n = ast_new(NODE_INT); n->int_val = tok.int_val; strcpy(n->str_val, tok.text); return n; }
    if (tok.type == TOK_TRUE) { parser_advance(p); return ast_new(NODE_TRUE); }
    if (tok.type == TOK_FALSE) { parser_advance(p); return ast_new(NODE_FALSE); }
    if (tok.type == TOK_NULL) { parser_advance(p); return ast_new(NODE_NULL); }
    if (tok.type == TOK_STRING_LIT) { parser_advance(p); ASTNode* n = ast_new(NODE_STRING); strcpy(n->str_val, tok.text); return n; }
    if (tok.type == TOK_IDENT) {
        parser_advance(p);
        if (parser_peek(p).type == TOK_LBRACKET) {
            parser_advance(p);
            ASTNode* idx = parse_expression(p);
            if (parser_peek(p).type == TOK_RBRACKET) parser_advance(p);
            ASTNode* n = ast_new(NODE_ARRAY_INDEX);
            ASTNode* id = ast_new(NODE_IDENT); strcpy(id->str_val, tok.text);
            n->left = id; n->right = idx; return n;
        }
        if (parser_peek(p).type == TOK_LPAREN) {
            parser_advance(p);
            ASTNode* n = ast_new(NODE_FUNC_CALL); strcpy(n->str_val, tok.text);
            n->children = NULL; n->child_count = 0;
            if (parser_peek(p).type != TOK_RPAREN) {
                int cap = 8; n->children = (ASTNode**)malloc(cap * sizeof(ASTNode*));
                do {
                    if (n->child_count >= cap) { cap *= 2; n->children = (ASTNode**)realloc(n->children, cap * sizeof(ASTNode*)); }
                    n->children[n->child_count++] = parse_expression(p);
                } while (parser_peek(p).type == TOK_COMMA && (parser_advance(p), 1));
            }
            if (parser_peek(p).type == TOK_RPAREN) parser_advance(p);
            return n;
        }
        /* Built-in: LEN, TYPEOF, TO_STRING, TO_NUMBER */
        if ((strcmp(tok.text, "LEN") == 0 || strcmp(tok.text, "TYPEOF") == 0 ||
             strcmp(tok.text, "TO_STRING") == 0 || strcmp(tok.text, "TO_NUMBER") == 0) &&
            parser_peek(p).type == TOK_LPAREN) {
            parser_advance(p);
            ASTNode* n = ast_new(NODE_ARRAY_LEN); /* reuse node type for builtins */
            if (strcmp(tok.text, "TO_STRING") == 0 || strcmp(tok.text, "TO_NUMBER") == 0)
                n->type = NODE_FUNC_CALL;
            strcpy(n->str_val, tok.text);
            n->left = parse_expression(p);
            if (parser_peek(p).type == TOK_RPAREN) parser_advance(p);
            return n;
        }
        ASTNode* n = ast_new(NODE_IDENT); strcpy(n->str_val, tok.text); return n;
    }
    if (tok.type == TOK_LPAREN) { parser_advance(p); ASTNode* expr = parse_expression(p); if (parser_peek(p).type == TOK_RPAREN) parser_advance(p); return expr; }
    if (tok.type == TOK_LBRACKET) {
        parser_advance(p); ASTNode* n = ast_new(NODE_ARRAY_LIT); n->children = NULL; n->child_count = 0;
        int cap = 8; n->children = (ASTNode**)malloc(cap * sizeof(ASTNode*));
        if (parser_peek(p).type != TOK_RBRACKET) {
            do { if (n->child_count >= cap) { cap *= 2; n->children = (ASTNode**)realloc(n->children, cap * sizeof(ASTNode*)); } n->children[n->child_count++] = parse_expression(p); } while (parser_peek(p).type == TOK_COMMA && (parser_advance(p), 1));
        }
        if (parser_peek(p).type == TOK_RBRACKET) parser_advance(p);
        return n;
    }
    if (tok.type == TOK_MINUS) { parser_advance(p); ASTNode* n = ast_new(NODE_UNARY); strcpy(n->op, "-"); n->left = parse_primary(p); return n; }
    if (tok.type == TOK_NOT) { parser_advance(p); ASTNode* n = ast_new(NODE_UNARY); strcpy(n->op, "NOT"); n->left = parse_primary(p); return n; }
    parser_advance(p);
    return ast_new(NODE_INT);
}

ASTNode* parse_expression_bp(Parser* p, int min_prec) {
    ASTNode* left = parse_primary(p);
    while (get_precedence(parser_peek(p).type) >= min_prec) {
        NbsToken op = parser_advance(p);
        int prec = get_precedence(op.type);
        ASTNode* right = parse_expression_bp(p, prec + 1);
        ASTNode* bin = ast_new(NODE_BINARY); strcpy(bin->op, op.text); bin->left = left; bin->right = right;
        left = bin;
    }
    return left;
}
ASTNode* parse_expression(Parser* p) { return parse_expression_bp(p, 1); }

ASTNode* parse_block(Parser* p);
ASTNode* parse_statement(Parser* p) {
    NbsToken tok = parser_peek(p);
    if (tok.type == TOK_PRINT) { parser_advance(p); ASTNode* n = ast_new(NODE_PRINT); n->left = parse_expression(p); return n; }
    if (tok.type == TOK_LET || tok.type == TOK_CONST || (tok.type == TOK_IDENT && p->pos + 1 < p->count && p->tokens[p->pos + 1].type == TOK_ASSIGN)) {
        if (tok.type == TOK_LET || tok.type == TOK_CONST) parser_advance(p);
        NbsToken name = parser_peek(p); if (name.type == TOK_IDENT) parser_advance(p);
        if (parser_peek(p).type == TOK_ASSIGN) parser_advance(p);
        ASTNode* n = ast_new(NODE_ASSIGN); strcpy(n->str_val, name.text); n->right = parse_expression(p); return n;
    }
    if (tok.type == TOK_IF) {
        parser_advance(p);
        ASTNode* root = ast_new(NODE_IF); ASTNode* current = root;
        root->left = parse_expression(p);
        if (parser_peek(p).type == TOK_THEN) parser_advance(p);
        if (parser_peek(p).type == TOK_COLON) parser_advance(p);
        root->right = parse_block(p);
        while (parser_peek(p).type == TOK_ELSEIF) {
            parser_advance(p); ASTNode* elseif = ast_new(NODE_IF);
            elseif->left = parse_expression(p);
            if (parser_peek(p).type == TOK_THEN) parser_advance(p);
            if (parser_peek(p).type == TOK_COLON) parser_advance(p);
            elseif->right = parse_block(p);
            current->third = elseif; current = elseif;
        }
        if (parser_peek(p).type == TOK_ELSE) { parser_advance(p); if (parser_peek(p).type == TOK_COLON) parser_advance(p); current->third = parse_block(p); }
        if (parser_peek(p).type == TOK_END) parser_advance(p);
        return root;
    }
    if (tok.type == TOK_WHILE) {
        parser_advance(p); ASTNode* n = ast_new(NODE_WHILE); n->left = parse_expression(p);
        if (parser_peek(p).type == TOK_THEN) parser_advance(p);
        if (parser_peek(p).type == TOK_COLON) parser_advance(p);
        n->right = parse_block(p); if (parser_peek(p).type == TOK_END) parser_advance(p); return n;
    }
    if (tok.type == TOK_FOR) {
        parser_advance(p); ASTNode* n = ast_new(NODE_FOR);
        NbsToken var = parser_peek(p); if (var.type == TOK_IDENT) parser_advance(p);
        strcpy(n->str_val, var.text);
        if (parser_peek(p).type == TOK_ASSIGN) parser_advance(p);
        ASTNode* start = parse_expression(p);
        if (parser_peek(p).type == TOK_TO) parser_advance(p);
        ASTNode* end = parse_expression(p);
        ASTNode* step = NULL;
        if (parser_peek(p).type == TOK_STEP) { parser_advance(p); step = parse_expression(p); }
        ASTNode* range = ast_new(NODE_BINARY); strcpy(range->op, "TO"); range->left = start; range->right = end;
        if (step) { ASTNode* sn = ast_new(NODE_BINARY); strcpy(sn->op, "STEP"); sn->left = range; sn->right = step; n->left = sn; }
        else n->left = range;
        if (parser_peek(p).type == TOK_COLON) parser_advance(p);
        n->right = parse_block(p);
        if (parser_peek(p).type == TOK_END) parser_advance(p);
        return n;
    }
    if (tok.type == TOK_FUNC) {
        parser_advance(p); ASTNode* n = ast_new(NODE_FUNC_DEF);
        NbsToken name = parser_peek(p); if (name.type == TOK_IDENT) parser_advance(p);
        strcpy(n->str_val, name.text); n->param_count = 0;
        while (parser_peek(p).type != TOK_COLON && parser_peek(p).type != TOK_EOF) {
            NbsToken param = parser_advance(p);
            if (param.type == TOK_IDENT) strcpy(n->params[n->param_count++], param.text);
        }
        if (parser_peek(p).type == TOK_COLON) parser_advance(p);
        n->right = parse_block(p);
        if (parser_peek(p).type == TOK_END) parser_advance(p);
        return n;
    }
    if (tok.type == TOK_RETURN) { parser_advance(p); ASTNode* n = ast_new(NODE_RETURN); if (parser_peek(p).type != TOK_END && parser_peek(p).type != TOK_EOF && parser_peek(p).type != TOK_ELSE && parser_peek(p).type != TOK_ELSEIF) n->left = parse_expression(p); return n; }
    if (tok.type == TOK_BREAK) { parser_advance(p); return ast_new(NODE_BREAK); }
    if (tok.type == TOK_CONTINUE) { parser_advance(p); return ast_new(NODE_CONTINUE); }
    ASTNode* expr = parse_expression(p); return expr;
}

ASTNode* parse_block(Parser* p) {
    ASTNode* block = ast_new(NODE_BLOCK); int cap = 16;
    block->children = (ASTNode**)malloc(cap * sizeof(ASTNode*)); block->child_count = 0;
    while (parser_peek(p).type != TOK_END && parser_peek(p).type != TOK_EOF && parser_peek(p).type != TOK_ELSE && parser_peek(p).type != TOK_ELSEIF) {
        if (block->child_count >= cap) { cap *= 2; block->children = (ASTNode**)realloc(block->children, cap * sizeof(ASTNode*)); }
        block->children[block->child_count++] = parse_statement(p);
    }
    return block;
}

ASTNode* parse_program(Parser* p) {
    ASTNode* prog = ast_new(NODE_PROGRAM); int cap = 64;
    prog->children = (ASTNode**)malloc(cap * sizeof(ASTNode*)); prog->child_count = 0;
    while (parser_peek(p).type != TOK_EOF) {
        if (prog->child_count >= cap) { cap *= 2; prog->children = (ASTNode**)realloc(prog->children, cap * sizeof(ASTNode*)); }
        prog->children[prog->child_count++] = parse_statement(p);
    }
    return prog;
}

/* ============================================================================
 * TARGET: JavaScript transpiler (AST -> JS)
 * ============================================================================ */

static char js_out[65536];
static int js_pos = 0;
static int js_indent = 0;

void js_init(void) { js_pos = 0; js_indent = 0; }
void js_indent_fn(void) { for (int i = 0; i < js_indent; i++) { js_out[js_pos++] = ' '; js_out[js_pos++] = ' '; } }
void js_str(const char* s) { while (*s) js_out[js_pos++] = *s++; }
void js_line(void) { js_out[js_pos++] = '\n'; js_indent_fn(); }

void js_transpile_expr(ASTNode* n) {
    if (!n) return;
    switch (n->type) {
        case NODE_INT: { char buf[32]; sprintf(buf, "%lld", n->int_val); js_str(buf); } break;
        case NODE_TRUE: js_str("true"); break;
        case NODE_FALSE: js_str("false"); break;
        case NODE_NULL: js_str("null"); break;
        case NODE_STRING: js_str("'"); js_str(n->str_val); js_str("'"); break;
        case NODE_IDENT: js_str(n->str_val); break;
        case NODE_BINARY: js_str("("); js_transpile_expr(n->left); js_str(" "); js_str(n->op); js_str(" "); js_transpile_expr(n->right); js_str(")"); break;
        case NODE_UNARY: js_str(n->op[0] == '-' ? "(-" : "(!"); js_transpile_expr(n->left); js_str(")"); break;
        case NODE_FUNC_CALL: js_str(n->str_val); js_str("("); for (int i = 0; i < n->child_count; i++) { if (i) js_str(", "); js_transpile_expr(n->children[i]); } js_str(")"); break;
        case NODE_ARRAY_INDEX: js_transpile_expr(n->left); js_str("["); js_transpile_expr(n->right); js_str("]"); break;
        case NODE_ARRAY_LEN: js_transpile_expr(n->left); js_str(".length"); break;
        default: js_str("/* ? */"); break;
    }
}

void js_transpile_stmt(ASTNode* n) {
    if (!n) return;
    switch (n->type) {
        case NODE_PRINT: js_str("console.log("); js_transpile_expr(n->left); js_str(")"); js_line(); break;
        case NODE_ASSIGN: js_str("let "); js_str(n->str_val); js_str(" = "); js_transpile_expr(n->right); js_line(); break;
        case NODE_FUNC_DEF: js_str("function "); js_str(n->str_val); js_str("("); for (int i = 0; i < n->param_count; i++) { if (i) js_str(", "); js_str(n->params[i]); } js_str(") {"); js_line(); js_indent++; js_transpile_stmt(n->right); js_indent--; js_indent_fn(); js_str("}"); js_line(); break;
        case NODE_RETURN: js_str("return "); js_transpile_expr(n->left); js_line(); break;
        case NODE_BREAK: js_str("break"); js_line(); break;
        case NODE_CONTINUE: js_str("continue"); js_line(); break;
        case NODE_IF: js_str("if ("); js_transpile_expr(n->left); js_str(") {"); js_line(); js_indent++; js_transpile_stmt(n->right); js_indent--; js_indent_fn(); js_str("}"); if (n->third && n->third->type == NODE_IF) { js_str(" else "); js_transpile_stmt(n->third); } else if (n->third) { js_str(" else {"); js_line(); js_indent++; js_transpile_stmt(n->third); js_indent--; js_indent_fn(); js_str("}"); } js_line(); break;
        case NODE_WHILE: js_str("while ("); js_transpile_expr(n->left); js_str(") {"); js_line(); js_indent++; js_transpile_stmt(n->right); js_indent--; js_indent_fn(); js_str("}"); js_line(); break;
        case NODE_FOR: js_str("for (let "); js_str(n->str_val); js_str(" = "); if (n->left->type == NODE_BINARY && strcmp(n->left->op, "STEP") == 0) { js_transpile_expr(n->left->left->left); js_str("; "); js_str(n->str_val); js_str(" <= "); js_transpile_expr(n->left->left->right); js_str("; "); js_str(n->str_val); js_str(" += "); js_transpile_expr(n->left->right); } else { js_transpile_expr(n->left->left); js_str("; "); js_str(n->str_val); js_str(" <= "); js_transpile_expr(n->left->right); js_str("; "); js_str(n->str_val); js_str("++"); } js_str(") {"); js_line(); js_indent++; js_transpile_stmt(n->right); js_indent--; js_indent_fn(); js_str("}"); js_line(); break;
        case NODE_BLOCK: for (int i = 0; i < n->child_count; i++) js_transpile_stmt(n->children[i]); break;
        case NODE_PROGRAM: for (int i = 0; i < n->child_count; i++) js_transpile_stmt(n->children[i]); break;
        default: js_transpile_expr(n); js_line(); break;
    }
}

const char* transpile_to_js(ASTNode* ast) {
    js_init();
    js_str("'use strict';"); js_line(); js_line();
    js_transpile_stmt(ast);
    js_out[js_pos] = 0;
    return js_out;
}

/* ============================================================================
 * TARGET: Python transpiler (AST -> Python)
 * ============================================================================ */

static char py_out[65536];
static int py_pos = 0;
static int py_indent = 0;

void py_init(void) { py_pos = 0; py_indent = 0; }
void py_indent_fn(void) { for (int i = 0; i < py_indent; i++) { py_out[py_pos++] = ' '; py_out[py_pos++] = ' '; py_out[py_pos++] = ' '; py_out[py_pos++] = ' '; } }
void py_str(const char* s) { while (*s) py_out[py_pos++] = *s++; }
void py_line(void) { py_out[py_pos++] = '\n'; py_indent_fn(); }

void py_transpile_expr(ASTNode* n) {
    if (!n) return;
    switch (n->type) {
        case NODE_INT: { char buf[32]; sprintf(buf, "%lld", n->int_val); py_str(buf); } break;
        case NODE_TRUE: py_str("True"); break;
        case NODE_FALSE: py_str("False"); break;
        case NODE_NULL: py_str("None"); break;
        case NODE_STRING: py_str("'"); py_str(n->str_val); py_str("'"); break;
        case NODE_IDENT: py_str(n->str_val); break;
        case NODE_BINARY: {
            const char* op = n->op;
            if (strcmp(op, "!=") == 0) op = "!=";
            py_str("("); py_transpile_expr(n->left); py_str(" "); py_str(op); py_str(" "); py_transpile_expr(n->right); py_str(")");
        } break;
        case NODE_UNARY: py_str(n->op[0] == '-' ? "(-" : "(not "); py_transpile_expr(n->left); py_str(")"); break;
        case NODE_FUNC_CALL: {
            if (strcmp(n->str_val, "LEN") == 0) { py_str("len("); py_transpile_expr(n->left); py_str(")"); }
            else if (strcmp(n->str_val, "TYPEOF") == 0) { py_str("type("); py_transpile_expr(n->left); py_str(").__name__"); }
            else if (strcmp(n->str_val, "TO_STRING") == 0) { py_str("str("); py_transpile_expr(n->left); py_str(")"); }
            else if (strcmp(n->str_val, "TO_NUMBER") == 0) { py_str("int("); py_transpile_expr(n->left); py_str(")"); }
            else { py_str(n->str_val); py_str("("); for (int i = 0; i < n->child_count; i++) { if (i) py_str(", "); py_transpile_expr(n->children[i]); } py_str(")"); }
        } break;
        case NODE_ARRAY_INDEX: py_transpile_expr(n->left); py_str("["); py_transpile_expr(n->right); py_str("]"); break;
        case NODE_ARRAY_LEN: py_str("len("); py_transpile_expr(n->left); py_str(")"); break;
        default: py_str("pass # ?"); break;
    }
}

void py_transpile_stmt(ASTNode* n) {
    if (!n) return;
    switch (n->type) {
        case NODE_PRINT: py_str("print("); py_transpile_expr(n->left); py_str(")"); py_line(); break;
        case NODE_ASSIGN: py_str(n->str_val); py_str(" = "); py_transpile_expr(n->right); py_line(); break;
        case NODE_FUNC_DEF: py_str("def "); py_str(n->str_val); py_str("("); for (int i = 0; i < n->param_count; i++) { if (i) py_str(", "); py_str(n->params[i]); } py_str("):"); py_line(); py_indent++; py_transpile_stmt(n->right); py_indent--; py_line(); break;
        case NODE_RETURN: py_str("return "); py_transpile_expr(n->left); py_line(); break;
        case NODE_BREAK: py_str("break"); py_line(); break;
        case NODE_CONTINUE: py_str("continue"); py_line(); break;
        case NODE_IF: py_str("if "); py_transpile_expr(n->left); py_str(":"); py_line(); py_indent++; py_transpile_stmt(n->right); py_indent--; if (n->third && n->third->type == NODE_IF) { py_indent_fn(); py_str("el"); py_transpile_stmt(n->third); } else if (n->third) { py_indent_fn(); py_str("else:"); py_line(); py_indent++; py_transpile_stmt(n->third); py_indent--; } break;
        case NODE_WHILE: py_str("while "); py_transpile_expr(n->left); py_str(":"); py_line(); py_indent++; py_transpile_stmt(n->right); py_indent--; py_line(); break;
        case NODE_FOR: py_str("for "); py_str(n->str_val); py_str(" in range("); if (n->left->type == NODE_BINARY && strcmp(n->left->op, "STEP") == 0) { py_transpile_expr(n->left->left->left); py_str(", "); py_transpile_expr(n->left->left->right); py_str(" + 1, "); py_transpile_expr(n->left->right); } else { py_transpile_expr(n->left->left); py_str(", "); py_transpile_expr(n->left->right); py_str(" + 1"); } py_str("):"); py_line(); py_indent++; py_transpile_stmt(n->right); py_indent--; py_line(); break;
        case NODE_BLOCK: for (int i = 0; i < n->child_count; i++) py_transpile_stmt(n->children[i]); break;
        case NODE_PROGRAM: py_str("from typing import Any\n\n"); for (int i = 0; i < n->child_count; i++) py_transpile_stmt(n->children[i]); break;
        default: py_transpile_expr(n); py_line(); break;
    }
}

const char* transpile_to_python(ASTNode* ast) {
    py_init();
    py_transpile_stmt(ast);
    py_out[py_pos] = 0;
    return py_out;
}

/* ============================================================================
 * SEMANTIC ANALYSIS BRIDGE
 * ============================================================================ */

typedef struct {
    int error_count;
    int warning_count;
    struct { int line; char msg[256]; } errors[128];
} SemaContext;

SemaContext *sema_new_context(void) {
    SemaContext *ctx = (SemaContext *)calloc(1, sizeof(SemaContext));
    scope_push("global");
    return ctx;
}

void sema_free_context(SemaContext *ctx) {
    scope_pop();
    free(ctx);
}

static void sema_ctx_error(SemaContext *ctx, int line, const char *fmt, ...) {
    if (ctx->error_count >= 128) return;
    va_list args;
    va_start(args, fmt);
    vsnprintf(ctx->errors[ctx->error_count].msg, 256, fmt, args);
    va_end(args);
    ctx->errors[ctx->error_count].line = line;
    ctx->error_count++;
}

void sema_print_errors(SemaContext *ctx) {
    for (int i = 0; i < ctx->error_count; i++) {
        fprintf(stderr, "Semantic error [line %d]: %s\n",
                ctx->errors[i].line, ctx->errors[i].msg);
    }
    if (ctx->error_count == 0) {
        printf("Semantic analysis: PASS\n");
    } else {
        printf("Semantic analysis: %d error(s), %d warning(s)\n",
               ctx->error_count, ctx->warning_count);
    }
}

int sema_has_errors(SemaContext *ctx) {
    return ctx->error_count > 0;
}

static int is_sema_keyword(const char *t) {
    return strcmp(t, "LET") == 0 || strcmp(t, "CONST") == 0 ||
           strcmp(t, "FUNC!") == 0 || strcmp(t, "END!") == 0 ||
           strcmp(t, "IF?") == 0 || strcmp(t, "ELSE") == 0 ||
           strcmp(t, "ELSEIF?") == 0 || strcmp(t, "WHILE?") == 0 ||
           strcmp(t, "FOR!") == 0 || strcmp(t, "TO") == 0 ||
           strcmp(t, "STEP") == 0 || strcmp(t, "RETURN") == 0 ||
           strcmp(t, "BREAK") == 0 || strcmp(t, "CONTINUE") == 0 ||
           strcmp(t, "PRINT") == 0 || strcmp(t, "AND") == 0 ||
           strcmp(t, "OR") == 0 || strcmp(t, "NOT") == 0 ||
           strcmp(t, "TRUE") == 0 || strcmp(t, "FALSE") == 0 ||
           strcmp(t, "NULL") == 0 || strcmp(t, "THEN") == 0 ||
           strcmp(t, "TRY") == 0 || strcmp(t, "CATCH") == 0 ||
           strcmp(t, "THROW") == 0;
}

static int is_sema_builtin(const char *t) {
    return strcmp(t, "PRINT") == 0 || strcmp(t, "LEN") == 0 ||
           strcmp(t, "TYPEOF") == 0 || strcmp(t, "TYPE") == 0 ||
           strcmp(t, "TO_STRING") == 0 || strcmp(t, "TO_NUMBER") == 0 ||
           strcmp(t, "TO_INT") == 0 || strcmp(t, "INPUT") == 0 ||
           strcmp(t, "RANDOM") == 0 || strcmp(t, "TIME") == 0 ||
           strcmp(t, "CONCAT") == 0 || strcmp(t, "WAIT") == 0 ||
           strcmp(t, "SUBSTR") == 0 || strcmp(t, "CHAR_AT") == 0 ||
           strcmp(t, "TRIM") == 0 || strcmp(t, "TO_UPPER") == 0 ||
           strcmp(t, "TO_LOWER") == 0 || strcmp(t, "CHAR") == 0 ||
           strcmp(t, "ORD") == 0 || strcmp(t, "ABS") == 0 ||
           strcmp(t, "MIN") == 0 || strcmp(t, "MAX") == 0 ||
           strcmp(t, "SQRT") == 0 || strcmp(t, "POW") == 0 ||
           strcmp(t, "FLOOR") == 0 || strcmp(t, "CEIL") == 0 ||
           strcmp(t, "ROUND") == 0 || strcmp(t, "PUSH") == 0 ||
           strcmp(t, "POP") == 0 || strcmp(t, "READ_FILE") == 0 ||
           strcmp(t, "WRITE_FILE") == 0 ||
           strcmp(t, "IS_INT") == 0 || strcmp(t, "IS_STRING") == 0 ||
           strcmp(t, "IS_BOOL") == 0 || strcmp(t, "IS_NULL") == 0 ||
           strcmp(t, "IS_ARRAY") == 0 || strcmp(t, "IS_FUNC") == 0 ||
           strcmp(t, "IS_NUMBER") == 0;
}

static int is_sema_literal_or_punct(const char *t) {
    if (!t || !t[0]) return 1;
    /* String literals (double or single quoted) */
    if (t[0] == '"') return 1;
    if (t[0] == '\'') return 1;
    /* Numbers */
    if ((t[0] == '-' || t[0] == '+') && t[1] >= '0' && t[1] <= '9') {
        int i = 2; for (; t[i]; i++) if (t[i] < '0' || t[i] > '9') return 0;
        return 1;
    }
    if (t[0] >= '0' && t[0] <= '9') return 1;
    /* Single-char punctuation */
    if (t[1] == '\0' && (t[0] == '=' || t[0] == '+' || t[0] == '-' || t[0] == '*' ||
        t[0] == '/' || t[0] == '%' || t[0] == '(' || t[0] == ')' ||
        t[0] == '[' || t[0] == ']' || t[0] == ',' || t[0] == ':' ||
        t[0] == ';' || t[0] == '.' || t[0] == '!' || t[0] == '&' ||
        t[0] == '|' || t[0] == '<' || t[0] == '>')) return 1;
    /* Two-char operators */
    if (strcmp(t, "==") == 0 || strcmp(t, "!=") == 0 ||
        strcmp(t, "<=") == 0 || strcmp(t, ">=") == 0 ||
        strcmp(t, "<<") == 0 || strcmp(t, ">>") == 0) return 1;
    return 0;
}

int sema_analyze(SemaContext *ctx, const char **tokens, int *token_types, int token_count) {
    for (int i = 0; i < token_count; i++) {
        const char *t = tokens[i];
        if (!t) continue;
        /* Skip string and int literals — they're never definitions */
        if (token_types && (token_types[i] == TOK_STRING_LIT || token_types[i] == TOK_INT_LIT)) continue;
        if ((strcmp(t, "LET") == 0 || strcmp(t, "CONST") == 0) && i + 1 < token_count) {
            const char *name = tokens[i + 1];
            if (symbol_lookup(name)) {
                sema_ctx_error(ctx, i + 1, "duplicate definition of '%s'", name);
            } else {
                symbol_define(name, TYPE_UNKNOWN, i + 1, 0, strcmp(t, "LET") == 0);
            }
            i++;
            continue;
        }
        if (strcmp(t, "FUNC!") == 0 && i + 1 < token_count) {
            const char *name = tokens[i + 1];
            if (symbol_lookup(name)) {
                sema_ctx_error(ctx, i + 1, "duplicate definition of function '%s'", name);
            } else {
                symbol_define(name, TYPE_FUNC, i + 1, 0, 0);
            }
            i++;
            int depth = 1;
            while (i + 1 < token_count && depth > 0) {
                i++;
                if (strcmp(tokens[i], "FUNC!") == 0 || strcmp(tokens[i], "IF?") == 0 ||
                    strcmp(tokens[i], "WHILE?") == 0 || strcmp(tokens[i], "FOR!") == 0 ||
                    strcmp(tokens[i], "TRY") == 0) depth++;
                else if (strcmp(tokens[i], "END!") == 0) depth--;
            }
            continue;
        }
    }
    for (int i = 0; i < token_count; i++) {
        const char *t = tokens[i];
        if (!t) continue;
        /* Skip string and int literals */
        if (token_types && (token_types[i] == TOK_STRING_LIT || token_types[i] == TOK_INT_LIT)) continue;
        if (strcmp(t, "FUNC!") == 0 && i + 1 < token_count) {
            i++;
            int depth = 1;
            while (i + 1 < token_count && depth > 0) {
                i++;
                if (strcmp(tokens[i], "FUNC!") == 0 || strcmp(tokens[i], "IF?") == 0 ||
                    strcmp(tokens[i], "WHILE?") == 0 || strcmp(tokens[i], "FOR!") == 0 ||
                    strcmp(tokens[i], "TRY") == 0) depth++;
                else if (strcmp(tokens[i], "END!") == 0) depth--;
            }
            continue;
        }
        if (is_sema_keyword(t) || is_sema_builtin(t) || is_sema_literal_or_punct(t)) continue;
        if (!symbol_lookup(t)) {
            sema_ctx_error(ctx, i + 1, "'%s' is not defined", t);
        }
    }
    return ctx->error_count;
}

/* ============================================================================
 * IR LOWERING (AST -> IR)
 * ============================================================================ */

static int ir_break_stack[64];
static int ir_continue_stack[64];
static int ir_break_top = 0;
static int ir_continue_top = 0;

static int ir_find_var(const char *name) {
    for (int i = 0; i < ir_program.var_count; i++)
        if (strcmp(ir_program.variables[i].name, name) == 0)
            return ir_program.variables[i].id;
    return -1;
}

static int ir_get_var(const char *name) {
    int idx = ir_find_var(name);
    if (idx >= 0) return idx;
    return ir_alloc_var(name);
}

static IROpcode ast_op_to_ir(const char *op) {
    if (strcmp(op, "+") == 0) return IR_ADD;
    if (strcmp(op, "-") == 0) return IR_SUB;
    if (strcmp(op, "*") == 0) return IR_MUL;
    if (strcmp(op, "/") == 0) return IR_DIV;
    if (strcmp(op, "%") == 0) return IR_MOD;
    if (strcmp(op, "==") == 0) return IR_EQ;
    if (strcmp(op, "!=") == 0) return IR_NEQ;
    if (strcmp(op, "<") == 0) return IR_LT;
    if (strcmp(op, ">") == 0) return IR_GT;
    if (strcmp(op, "<=") == 0) return IR_LTE;
    if (strcmp(op, ">=") == 0) return IR_GTE;
    if (strcmp(op, "AND") == 0) return IR_AND;
    if (strcmp(op, "OR") == 0) return IR_OR;
    return IR_NOP;
}

int ir_lower_expr(ASTNode *n) {
    if (!n) return -1;
    switch (n->type) {
        case NODE_INT: {
            int d = ir_next_temp();
            ir_emit_imm(d, (int)n->int_val, n->line, 0);
            return d;
        }
        case NODE_STRING: {
            int d = ir_next_temp();
            ir_emit(IR_LOAD_IMM, n->line, 0);
            ir_program.instructions[ir_program.count - 1].dst = d;
            strncpy(ir_program.instructions[ir_program.count - 1].str, n->str_val, 255);
            return d;
        }
        case NODE_TRUE: {
            int d = ir_next_temp();
            ir_emit_imm(d, 1, n->line, 0);
            return d;
        }
        case NODE_FALSE: {
            int d = ir_next_temp();
            ir_emit_imm(d, 0, n->line, 0);
            return d;
        }
        case NODE_NULL: {
            int d = ir_next_temp();
            ir_emit_imm(d, 0, n->line, 0);
            return d;
        }
        case NODE_IDENT: {
            int vi = ir_get_var(n->str_val);
            int d = ir_next_temp();
            ir_emit(IR_LOAD_VAR, n->line, 0);
            ir_program.instructions[ir_program.count - 1].dst = d;
            ir_program.instructions[ir_program.count - 1].src1 = vi;
            return d;
        }
        case NODE_BINARY: {
            int l = ir_lower_expr(n->left);
            int r = ir_lower_expr(n->right);
            int d = ir_next_temp();
            ir_emit_binary(d, l, r, ast_op_to_ir(n->op), n->line, 0);
            return d;
        }
        case NODE_UNARY: {
            int l = ir_lower_expr(n->left);
            int d = ir_next_temp();
            IROpcode op = (strcmp(n->op, "-") == 0) ? IR_NEG : IR_NOT;
            ir_emit(op, n->line, 0);
            ir_program.instructions[ir_program.count - 1].dst = d;
            ir_program.instructions[ir_program.count - 1].src1 = l;
            return d;
        }
        case NODE_FUNC_CALL: {
            int args[16];
            int argc = n->child_count < 16 ? n->child_count : 16;
            for (int i = 0; i < argc; i++)
                args[i] = ir_lower_expr(n->children[i]);

            if (strcmp(n->str_val, "LEN") == 0 && argc == 1) {
                int d = ir_next_temp();
                ir_emit(IR_ARRAY_LEN, n->line, 0);
                ir_program.instructions[ir_program.count - 1].dst = d;
                ir_program.instructions[ir_program.count - 1].src1 = args[0];
                return d;
            }
            if (strcmp(n->str_val, "TYPEOF") == 0 && argc == 1) {
                int d = ir_next_temp();
                ir_emit(IR_TYPEOF, n->line, 0);
                ir_program.instructions[ir_program.count - 1].dst = d;
                ir_program.instructions[ir_program.count - 1].src1 = args[0];
                return d;
            }
            if (strcmp(n->str_val, "TO_STRING") == 0 && argc == 1) {
                int d = ir_next_temp();
                ir_emit(IR_TO_STRING, n->line, 0);
                ir_program.instructions[ir_program.count - 1].dst = d;
                ir_program.instructions[ir_program.count - 1].src1 = args[0];
                return d;
            }
            if (strcmp(n->str_val, "TO_NUMBER") == 0 && argc == 1) {
                int d = ir_next_temp();
                ir_emit(IR_TO_NUMBER, n->line, 0);
                ir_program.instructions[ir_program.count - 1].dst = d;
                ir_program.instructions[ir_program.count - 1].src1 = args[0];
                return d;
            }

            int d = ir_next_temp();
            ir_emit(IR_CALL, n->line, 0);
            IRInstruction *ins = &ir_program.instructions[ir_program.count - 1];
            ins->dst = d;
            strncpy(ins->func_name, n->str_val, 255);
            ins->arg_count = argc;
            for (int i = 0; i < argc; i++)
                ins->args[i] = args[i];
            return d;
        }
        case NODE_ARRAY_LIT: {
            int d = ir_next_temp();
            ir_emit(IR_ARRAY_NEW, n->line, 0);
            IRInstruction *ins = &ir_program.instructions[ir_program.count - 1];
            ins->dst = d;
            ins->imm = n->child_count;
            ins->arg_count = n->child_count;
            for (int i = 0; i < n->child_count && i < 16; i++)
                ins->args[i] = ir_lower_expr(n->children[i]);
            return d;
        }
        case NODE_ARRAY_INDEX: {
            int arr = ir_lower_expr(n->left);
            int idx = ir_lower_expr(n->right);
            int d = ir_next_temp();
            ir_emit(IR_LOAD_ARRAY, n->line, 0);
            ir_program.instructions[ir_program.count - 1].dst = d;
            ir_program.instructions[ir_program.count - 1].src1 = arr;
            ir_program.instructions[ir_program.count - 1].src2 = idx;
            return d;
        }
        case NODE_ARRAY_LEN: {
            int l = ir_lower_expr(n->left);
            int d = ir_next_temp();
            ir_emit(IR_ARRAY_LEN, n->line, 0);
            ir_program.instructions[ir_program.count - 1].dst = d;
            ir_program.instructions[ir_program.count - 1].src1 = l;
            return d;
        }
        default:
            return -1;
    }
}

void ir_lower_stmt(ASTNode *n) {
    if (!n) return;
    switch (n->type) {
        case NODE_ASSIGN: {
            int src = ir_lower_expr(n->right);
            int vi = ir_get_var(n->str_val);
            ir_emit(IR_STORE_VAR, n->line, 0);
            ir_program.instructions[ir_program.count - 1].dst = vi;
            ir_program.instructions[ir_program.count - 1].src1 = src;
            break;
        }
        case NODE_PRINT: {
            int arg = ir_lower_expr(n->left);
            ir_emit(IR_PRINT, n->line, 0);
            ir_program.instructions[ir_program.count - 1].src1 = arg;
            break;
        }
        case NODE_IF: {
            int L_end = ir_new_label();
            ASTNode *conds[64];
            ASTNode *bodies[64];
            int count = 0;
            ASTNode *else_body = NULL;
            ASTNode *cur = n;
            while (cur && cur->type == NODE_IF) {
                conds[count] = cur->left;
                bodies[count] = cur->right;
                count++;
                cur = cur->third;
            }
            if (cur) else_body = cur;
            for (int i = 0; i < count; i++) {
                int c = ir_lower_expr(conds[i]);
                int neg = ir_next_temp();
                ir_emit(IR_NOT, n->line, 0);
                ir_program.instructions[ir_program.count - 1].dst = neg;
                ir_program.instructions[ir_program.count - 1].src1 = c;
                int L_skip = (i < count - 1 || else_body) ? ir_new_label() : L_end;
                ir_emit_if_goto(neg, L_skip, n->line, 0);
                ir_lower_stmt(bodies[i]);
                ir_emit_goto(L_end, n->line, 0);
                ir_emit_label(L_skip);
            }
            if (else_body) ir_lower_stmt(else_body);
            ir_emit_label(L_end);
            break;
        }
        case NODE_WHILE: {
            int L_top = ir_new_label();
            int L_end = ir_new_label();
            ir_break_stack[ir_break_top++] = L_end;
            ir_continue_stack[ir_continue_top++] = L_top;
            ir_emit_label(L_top);
            int c = ir_lower_expr(n->left);
            int neg = ir_next_temp();
            ir_emit(IR_NOT, n->line, 0);
            ir_program.instructions[ir_program.count - 1].dst = neg;
            ir_program.instructions[ir_program.count - 1].src1 = c;
            ir_emit_if_goto(neg, L_end, n->line, 0);
            ir_lower_stmt(n->right);
            ir_emit_goto(L_top, n->line, 0);
            ir_emit_label(L_end);
            ir_break_top--;
            ir_continue_top--;
            break;
        }
        case NODE_FOR: {
            int vi = ir_get_var(n->str_val);
            int L_check = ir_new_label();
            int L_end = ir_new_label();
            ir_break_stack[ir_break_top++] = L_end;
            ir_continue_stack[ir_continue_top++] = L_check;
            ASTNode *start_e, *end_e, *step_e = NULL;
            if (n->left && n->left->type == NODE_BINARY && strcmp(n->left->op, "STEP") == 0) {
                start_e = n->left->left->left;
                end_e = n->left->left->right;
                step_e = n->left->right;
            } else {
                start_e = n->left->left;
                end_e = n->left->right;
            }
            int ts = ir_lower_expr(start_e);
            ir_emit(IR_STORE_VAR, n->line, 0);
            ir_program.instructions[ir_program.count - 1].dst = vi;
            ir_program.instructions[ir_program.count - 1].src1 = ts;
            ir_emit_label(L_check);
            int te = ir_lower_expr(end_e);
            int ti = ir_next_temp();
            ir_emit(IR_LOAD_VAR, n->line, 0);
            ir_program.instructions[ir_program.count - 1].dst = ti;
            ir_program.instructions[ir_program.count - 1].src1 = vi;
            int cmp = ir_next_temp();
            ir_emit_binary(cmp, ti, te, IR_GT, n->line, 0);
            ir_emit_if_goto(cmp, L_end, n->line, 0);
            ir_lower_stmt(n->right);
            int ti2 = ir_next_temp();
            ir_emit(IR_LOAD_VAR, n->line, 0);
            ir_program.instructions[ir_program.count - 1].dst = ti2;
            ir_program.instructions[ir_program.count - 1].src1 = vi;
            int tstep;
            if (step_e) {
                tstep = ir_lower_expr(step_e);
            } else {
                tstep = ir_next_temp();
                ir_emit_imm(tstep, 1, n->line, 0);
            }
            int tnew = ir_next_temp();
            ir_emit_binary(tnew, ti2, tstep, IR_ADD, n->line, 0);
            ir_emit(IR_STORE_VAR, n->line, 0);
            ir_program.instructions[ir_program.count - 1].dst = vi;
            ir_program.instructions[ir_program.count - 1].src1 = tnew;
            ir_emit_goto(L_check, n->line, 0);
            ir_emit_label(L_end);
            ir_break_top--;
            ir_continue_top--;
            break;
        }
        case NODE_FUNC_DEF: {
            int L_body = ir_new_label();
            ir_emit_goto(L_body, n->line, 0);
            ir_emit_label(L_body);
            ir_lower_stmt(n->right);
            if (ir_program.count == 0 || ir_program.instructions[ir_program.count - 1].op != IR_RET) {
                int z = ir_next_temp();
                ir_emit_imm(z, 0, n->line, 0);
                ir_emit(IR_RET, n->line, 0);
                ir_program.instructions[ir_program.count - 1].src1 = z;
            }
            break;
        }
        case NODE_RETURN: {
            int src = n->left ? ir_lower_expr(n->left) : -1;
            ir_emit(IR_RET, n->line, 0);
            ir_program.instructions[ir_program.count - 1].src1 = src;
            break;
        }
        case NODE_BREAK: {
            if (ir_break_top > 0)
                ir_emit_goto(ir_break_stack[ir_break_top - 1], n->line, 0);
            break;
        }
        case NODE_CONTINUE: {
            if (ir_continue_top > 0)
                ir_emit_goto(ir_continue_stack[ir_continue_top - 1], n->line, 0);
            break;
        }
        case NODE_BLOCK:
        case NODE_PROGRAM:
            for (int i = 0; i < n->child_count; i++)
                ir_lower_stmt(n->children[i]);
            break;
        default:
            ir_lower_expr(n);
            break;
    }
}

IRProgram *ast_to_ir(ASTNode *ast) {
    ir_reset();
    ir_lower_stmt(ast);
    return &ir_program;
}

/* ============================================================================
 * MAIN
 * ============================================================================ */

int main(int argc, char** argv) {
    if (argc < 2) {
        fprintf(stderr, "Nebulara Pipeline v2.0\n");
        fprintf(stderr, "Usage: %s <file.nbs> [--target js|py|ir|check] [--check] [--ir]\n", argv[0]);
        return 1;
    }

    const char* target = "check";
    const char* filename = NULL;
    int do_check = 0;
    for (int i = 1; i < argc; i++) {
        if (strcmp(argv[i], "--check") == 0) { do_check = 1; }
        else if (strcmp(argv[i], "--ir") == 0) { target = "ir"; }
        else if (strcmp(argv[i], "--target") == 0 && i + 1 < argc) { target = argv[++i]; }
        else { filename = argv[i]; }
    }
    if (!filename) { fprintf(stderr, "No file specified\n"); return 1; }

    FILE* f = fopen(filename, "rb");
    if (!f) { fprintf(stderr, "Error: cannot open '%s'\n", filename); return 1; }
    fseek(f, 0, SEEK_END);
    long len = ftell(f);
    fseek(f, 0, SEEK_SET);
    char* src = (char*)malloc(len + 1);
    fread(src, 1, len, f);
    src[len] = 0;
    fclose(f);

    /* Lex */
    Lexer lexer = lexer_new(src);
    Parser parser = {0};
    while (1) {
        NbsToken tok = lexer_next(&lexer);
        parser.tokens[parser.count++] = tok;
        if (tok.type == TOK_EOF) break;
        if (parser.count >= 4096) { fprintf(stderr, "Error: too many tokens\n"); free(src); return 1; }
    }
    free(src);

    /* Parse */
    ASTNode* ast = parse_program(&parser);

    /* Semantic analysis */
    SemaContext *sema_ctx = sema_new_context();
    const char **token_texts = (const char **)malloc(parser.count * sizeof(char *));
    int *token_types = (int *)malloc(parser.count * sizeof(int));
    for (int i = 0; i < parser.count; i++) {
        token_texts[i] = parser.tokens[i].text;
        token_types[i] = parser.tokens[i].type;
    }
    sema_analyze(sema_ctx, token_texts, token_types, parser.count);
    free(token_texts);
    free(token_types);

    /* --check mode: analyze and report only */
    if (do_check || strcmp(target, "check") == 0) {
        sema_print_errors(sema_ctx);
        int status = sema_has_errors(sema_ctx) ? 1 : 0;
        sema_free_context(sema_ctx);
        return status;
    }

    /* Transpile mode: abort if there are semantic errors */
    if (sema_has_errors(sema_ctx)) {
        sema_print_errors(sema_ctx);
        fprintf(stderr, "Aborting transpilation due to semantic errors.\n");
        sema_free_context(sema_ctx);
        return 1;
    }
    sema_free_context(sema_ctx);

    /* Output */
    if (strcmp(target, "js") == 0) {
        printf("%s", transpile_to_js(ast));
    } else if (strcmp(target, "py") == 0) {
        printf("%s", transpile_to_python(ast));
    } else if (strcmp(target, "ir") == 0) {
        ast_to_ir(ast);
        ir_print();
    }
    return 0;
}
