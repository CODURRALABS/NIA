/*
 * neb-ir.c - Intermediate Representation for Nebulara
 * 
 * Three-address code IR with SSA-like properties:
 * - Linear sequence of operations
 * - Each instruction has at most 3 operands
 * - Phi functions for control flow merge points
 * - Basic blocks for CFG construction
 *
 * Build: gcc -o neb-ir.exe neb-ir.c -static -O2
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

/* IR Instruction Types */
typedef enum {
    /* Arithmetic */
    IR_ADD, IR_SUB, IR_MUL, IR_DIV, IR_MOD,
    IR_NEG,
    
    /* Comparison */
    IR_EQ, IR_NEQ, IR_LT, IR_GT, IR_LTE, IR_GTE,
    
    /* Logical */
    IR_AND, IR_OR, IR_NOT,
    
    /* Memory */
    IR_LOAD_IMM,    /* load immediate value */
    IR_LOAD_VAR,    /* load variable */
    IR_STORE_VAR,   /* store to variable */
    IR_LOAD_ARRAY,  /* array index */
    IR_STORE_ARRAY, /* array store */
    
    /* Control flow */
    IR_LABEL,       /* label target */
    IR_GOTO,        /* unconditional jump */
    IR_IF_GOTO,     /* conditional jump */
    IR_CALL,        /* function call */
    IR_RET,         /* return */
    
    /* Special */
    IR_PRINT,       /* print to stdout */
    IR_PHI,         /* phi function for SSA */
    IR_NOP,
    
    /* String */
    IR_STR_CONCAT,  /* string concatenation */
    
    /* Type */
    IR_TYPEOF,
    IR_TO_STRING,
    IR_TO_NUMBER,
    
    /* Array */
    IR_ARRAY_LEN,
    IR_ARRAY_NEW,
    
    IR_OP_COUNT
} IROpcode;

typedef struct {
    char *name;
    int id;
} IRFunc;

typedef struct {
    IROpcode op;
    int line;
    int col;
    
    /* Operands (indices into symbol/value tables) */
    int dst;        /* destination register/variable */
    int src1;       /* first source operand */
    int src2;       /* second source operand */
    int imm;        /* immediate value */
    char str[256];  /* string literal */
    
    /* Labels */
    int label_id;
    int target_label;
    
    /* Call info */
    char func_name[256];
    int arg_count;
    int args[16];   /* argument operand indices */
} IRInstruction;

typedef struct {
    char name[256];
    int id;
    int is_param;
} IRVariable;

typedef struct {
    IRInstruction instructions[4096];
    int count;
    
    IRVariable variables[1024];
    int var_count;
    
    /* Basic blocks */
    int block_starts[1024];
    int block_ends[1024];
    int block_count;
    
    /* Label table */
    int label_targets[1024];
    
    int next_var;
    int next_label;
} IRProgram;

/* IR Program */
static IRProgram ir_program;

/* Variable allocation */
int ir_alloc_var(const char *name) {
    int id = ir_program.var_count;
    strncpy(ir_program.variables[id].name, name, 255);
    ir_program.variables[id].id = id;
    ir_program.var_count++;
    return id;
}

int ir_next_temp(void) {
    char name[32];
    snprintf(name, 32, "t%d", ir_program.next_var);
    return ir_alloc_var(name);
}

/* Emit instructions */
void ir_emit(IROpcode op, int line, int col) {
    IRInstruction *i = &ir_program.instructions[ir_program.count];
    i->op = op;
    i->line = line;
    i->col = col;
    i->dst = -1;
    i->src1 = -1;
    i->src2 = -1;
    i->imm = 0;
    i->label_id = -1;
    i->target_label = -1;
    i->arg_count = 0;
    ir_program.count++;
}

void ir_emit_imm(int dst, int imm, int line, int col) {
    ir_emit(IR_LOAD_IMM, line, col);
    ir_program.instructions[ir_program.count - 1].dst = dst;
    ir_program.instructions[ir_program.count - 1].imm = imm;
}

void ir_emit_binary(int dst, int src1, int src2, IROpcode op, int line, int col) {
    ir_emit(op, line, col);
    ir_program.instructions[ir_program.count - 1].dst = dst;
    ir_program.instructions[ir_program.count - 1].src1 = src1;
    ir_program.instructions[ir_program.count - 1].src2 = src2;
}

void ir_emit_label(int label_id) {
    ir_emit(IR_LABEL, 0, 0);
    ir_program.instructions[ir_program.count - 1].label_id = label_id;
    ir_program.label_targets[label_id] = ir_program.count - 1;
}

void ir_emit_goto(int label_id, int line, int col) {
    ir_emit(IR_GOTO, line, col);
    ir_program.instructions[ir_program.count - 1].target_label = label_id;
}

void ir_emit_if_goto(int cond, int label_id, int line, int col) {
    ir_emit(IR_IF_GOTO, line, col);
    ir_program.instructions[ir_program.count - 1].src1 = cond;
    ir_program.instructions[ir_program.count - 1].target_label = label_id;
}

int ir_new_label(void) {
    return ir_program.next_label++;
}

/* Print IR */
const char *ir_op_name(IROpcode op) {
    switch (op) {
        case IR_ADD:        return "ADD";
        case IR_SUB:        return "SUB";
        case IR_MUL:        return "MUL";
        case IR_DIV:        return "DIV";
        case IR_MOD:        return "MOD";
        case IR_NEG:        return "NEG";
        case IR_EQ:         return "EQ";
        case IR_NEQ:        return "NEQ";
        case IR_LT:         return "LT";
        case IR_GT:         return "GT";
        case IR_LTE:        return "LTE";
        case IR_GTE:        return "GTE";
        case IR_AND:        return "AND";
        case IR_OR:         return "OR";
        case IR_NOT:        return "NOT";
        case IR_LOAD_IMM:   return "LOAD_IMM";
        case IR_LOAD_VAR:   return "LOAD_VAR";
        case IR_STORE_VAR:  return "STORE_VAR";
        case IR_LOAD_ARRAY: return "LOAD_ARRAY";
        case IR_STORE_ARRAY:return "STORE_ARRAY";
        case IR_LABEL:      return "LABEL";
        case IR_GOTO:       return "GOTO";
        case IR_IF_GOTO:    return "IF_GOTO";
        case IR_CALL:       return "CALL";
        case IR_RET:        return "RET";
        case IR_PRINT:      return "PRINT";
        case IR_PHI:        return "PHI";
        case IR_NOP:        return "NOP";
        case IR_STR_CONCAT: return "STR_CONCAT";
        case IR_TYPEOF:     return "TYPEOF";
        case IR_TO_STRING:  return "TO_STRING";
        case IR_TO_NUMBER:  return "TO_NUMBER";
        case IR_ARRAY_LEN:  return "ARRAY_LEN";
        case IR_ARRAY_NEW:  return "ARRAY_NEW";
        default:            return "UNKNOWN";
    }
}

void ir_print(void) {
    printf("=== IR Output ===\n");
    for (int i = 0; i < ir_program.count; i++) {
        IRInstruction *ins = &ir_program.instructions[i];
        printf("%4d: ", i);
        
        switch (ins->op) {
            case IR_LABEL:
                printf("L%d:", ins->label_id);
                break;
            case IR_LOAD_IMM:
                printf("  %s t%d, %d", ir_op_name(ins->op), ins->dst, ins->imm);
                break;
            case IR_ADD: case IR_SUB: case IR_MUL: case IR_DIV: case IR_MOD:
            case IR_EQ: case IR_NEQ: case IR_LT: case IR_GT: case IR_LTE: case IR_GTE:
            case IR_AND: case IR_OR:
            case IR_STR_CONCAT:
                printf("  %s t%d, t%d, t%d", ir_op_name(ins->op), ins->dst, ins->src1, ins->src2);
                break;
            case IR_NOT: case IR_NEG:
                printf("  %s t%d, t%d", ir_op_name(ins->op), ins->dst, ins->src1);
                break;
            case IR_GOTO:
                printf("  GOTO L%d", ins->target_label);
                break;
            case IR_IF_GOTO:
                printf("  IF t%d GOTO L%d", ins->src1, ins->target_label);
                break;
            case IR_PRINT:
                printf("  PRINT t%d", ins->src1);
                break;
            case IR_RET:
                printf("  RET t%d", ins->src1);
                break;
            case IR_STORE_VAR:
                printf("  STORE %s, t%d", ir_program.variables[ins->dst].name, ins->src1);
                break;
            case IR_LOAD_VAR:
                printf("  LOAD t%d, %s", ins->dst, ir_program.variables[ins->src1].name);
                break;
            default:
                printf("  %s", ir_op_name(ins->op));
                break;
        }
        printf("\n");
    }
    printf("=== End IR ===\n");
}

void ir_reset(void) {
    ir_program.count = 0;
    ir_program.var_count = 0;
    ir_program.block_count = 0;
    ir_program.next_var = 0;
    ir_program.next_label = 0;
}

/* Demo */
#ifdef NEB_IR_TEST
int main(void) {
    printf("=== Nebulara IR Module ===\n\n");
    
    /* Generate IR for: LET x = 3 + 4; PRINT x */
    int v_x = ir_alloc_var("x");
    int t1 = ir_next_temp();
    int t2 = ir_next_temp();
    int t3 = ir_next_temp();
    
    ir_emit_imm(t1, 3, 1, 9);
    ir_emit_imm(t2, 4, 1, 13);
    ir_emit_binary(t3, t1, t2, IR_ADD, 1, 11);
    ir_emit(IR_STORE_VAR, 1, 5);
    ir_program.instructions[ir_program.count - 1].dst = v_x;
    ir_program.instructions[ir_program.count - 1].src1 = t3;
    ir_emit(IR_PRINT, 2, 1);
    ir_program.instructions[ir_program.count - 1].src1 = v_x;
    
    ir_print();
    ir_reset();
    
    printf("\nIR module: OK\n");
    return 0;
}
#endif
