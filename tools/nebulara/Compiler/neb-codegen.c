/*
 * neb-codegen.c - Native x86/x64 Code Generation for Nebulara
 * 
 * Generates native machine code from IR instructions.
 * Supports x86-32 (i686) and x64 (x86-64) targets.
 *
 * Build: gcc -o neb-codegen.exe neb-codegen.c -static -O2
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

/* Codegen targets */
typedef enum {
    TARGET_X86_32,
    TARGET_X64,
    TARGET_ARM64
} CodegenTarget;

/* x86 Registers */
typedef enum {
    /* 32-bit */
    EAX = 0, ECX, EDX, EBX, ESP, EBP, ESI, EDI,
    /* 64-bit */
    RAX = 0, RCX, RDX, RBX, RSP, RBP, RSI, RDI,
    R8, R9, R10, R11, R12, R13, R14, R15
} Register;

/* Register allocation */
typedef struct {
    int reg[16];        /* 1=used, 0=free */
    int spill_count;
    CodegenTarget target;
} RegAlloc;

/* Code buffer */
typedef struct {
    unsigned char *code;
    int size;
    int capacity;
    int labels[1024];
    int label_targets[1024];
    int label_count;
} CodeBuffer;

static CodeBuffer code_buf;
static RegAlloc reg_alloc;
static CodegenTarget current_target = TARGET_X64;

/* Code buffer management */
void code_init(void) {
    code_buf.capacity = 65536;
    code_buf.code = (unsigned char *)malloc(code_buf.capacity);
    code_buf.size = 0;
    code_buf.label_count = 0;
    memset(&reg_alloc, 0, sizeof(RegAlloc));
    reg_alloc.target = current_target;
}

void code_emit(unsigned char byte) {
    if (code_buf.size >= code_buf.capacity) {
        code_buf.capacity *= 2;
        code_buf.code = (unsigned char *)realloc(code_buf.code, code_buf.capacity);
    }
    code_buf.code[code_buf.size++] = byte;
}

void code_emit32(unsigned int val) {
    code_emit(val & 0xFF);
    code_emit((val >> 8) & 0xFF);
    code_emit((val >> 16) & 0xFF);
    code_emit((val >> 24) & 0xFF);
}

void code_emit64(unsigned long long val) {
    code_emit32(val & 0xFFFFFFFF);
    code_emit32((val >> 32) & 0xFFFFFFFF);
}

/* Register management */
int reg_alloc_alloc(void) {
    for (int i = 0; i < 16; i++) {
        if (!reg_alloc.reg[i]) {
            reg_alloc.reg[i] = 1;
            return i;
        }
    }
    /* All registers used - spill */
    reg_alloc.spill_count++;
    return -1;
}

void reg_free(int reg) {
    if (reg >= 0 && reg < 16) {
        reg_alloc.reg[reg] = 0;
    }
}

/* x86/x64 instruction encoding */
void emit_mov_reg_imm(int reg, unsigned long long imm) {
    if (current_target == TARGET_X64) {
        /* REX.W prefix for 64-bit */
        if (reg >= 8) {
            code_emit(0x49);
        } else {
            code_emit(0x48);
        }
        code_emit(0xB8 + (reg & 7));
        code_emit64(imm);
    } else {
        /* 32-bit: MOV r32, imm32 */
        code_emit(0xB8 + reg);
        code_emit32((unsigned int)imm);
    }
}

void emit_mov_reg_reg(int dst, int src) {
    if (current_target == TARGET_X64) {
        code_emit(0x48); /* REX.W */
    }
    code_emit(0x89);
    code_emit(0xC0 + (((src & 7) << 3) | (dst & 7)));
}

void emit_add_reg_reg(int dst, int src) {
    if (current_target == TARGET_X64) {
        code_emit(0x48); /* REX.W */
    }
    code_emit(0x01);
    code_emit(0xC0 + (((src & 7) << 3) | (dst & 7)));
}

void emit_sub_reg_reg(int dst, int src) {
    if (current_target == TARGET_X64) {
        code_emit(0x48); /* REX.W */
    }
    code_emit(0x29);
    code_emit(0xC0 + (((src & 7) << 3) | (dst & 7)));
}

void emit_imul_reg_reg(int dst, int src) {
    if (current_target == TARGET_X64) {
        code_emit(0x48); /* REX.W */
    }
    code_emit(0x0F);
    code_emit(0xAF);
    code_emit(0xC0 + (((dst & 7) << 3) | (src & 7)));
}

void emit_cmp_reg_reg(int reg1, int reg2) {
    if (current_target == TARGET_X64) {
        code_emit(0x48); /* REX.W */
    }
    code_emit(0x39);
    code_emit(0xC0 + (((reg2 & 7) << 3) | (reg1 & 7)));
}

void emit_jcc(int condition, int offset) {
    code_emit(0x0F);
    code_emit(0x80 + condition);
    code_emit32(offset);
}

/* Syscall for Linux/macOS */
void emit_syscall_exit(int exit_code) {
    /* mov rax, 60 (sys_exit) */
    emit_mov_reg_imm(RAX, 60);
    /* mov rdi, exit_code */
    emit_mov_reg_imm(RDI, exit_code);
    /* syscall */
    code_emit(0x0F);
    code_emit(0x05);
}

/* Windows x64 calling convention stub */
void emit_win64_call_stub(void) {
    /* sub rsp, 40 (shadow space) */
    if (current_target == TARGET_X64) {
        code_emit(0x48);
        code_emit(0x83);
        code_emit(0xEC);
        code_emit(0x28);
    }
}

/* Labels */
int codegen_new_label(void) {
    return code_buf.label_count++;
}

void codegen_label(int label) {
    code_buf.label_targets[label] = code_buf.size;
}

/* Save code to file */
int codegen_save(const char *filename) {
    FILE *f = fopen(filename, "wb");
    if (!f) return -1;
    
    /* ELF64 header */
    unsigned char elf_header[64] = {
        0x7F, 'E', 'L', 'F',  /* magic */
        2,                     /* 64-bit */
        1,                     /* little-endian */
        1,                     /* ELF version */
        0, 0, 0, 0, 0, 0, 0, 0,  /* padding */
        2, 0,                  /* ET_EXEC */
        0x3E, 0,              /* x86-64 */
        1, 0, 0, 0,           /* ELF version */
        0, 0, 0, 0,           /* entry point (set below) */
        64, 0, 0, 0,          /* phoff */
        0, 0, 0, 0,           /* shoff */
        0, 0, 0, 0,           /* flags */
        64, 0,                 /* ehsize */
        56, 0,                 /* phentsize */
        1, 0,                  /* phnum */
        64, 0,                 /* shentsize */
        0, 0,                  /* shnum */
        0, 0                   /* shstrndx */
    };
    
    /* Set entry point to 0x400000 + 64 (ELF header) + 56 (program header) */
    unsigned int entry = 0x400000 + 64 + 56;
    memcpy(&elf_header[24], &entry, 4);
    
    /* Program header */
    unsigned char prog_header[56] = {0};
    prog_header[0] = 1;        /* PT_LOAD */
    prog_header[4] = 5;        /* PF_R | PF_X */
    memcpy(&prog_header[8], &entry, 4);   /* p_offset */
    unsigned int vaddr = 0x400000;
    memcpy(&prog_header[12], &vaddr, 4);  /* p_vaddr */
    memcpy(&prog_header[20], &vaddr, 4);  /* p_paddr */
    unsigned int filesz = 56 + code_buf.size;
    unsigned int memsz = filesz;
    memcpy(&prog_header[24], &filesz, 4);
    memcpy(&prog_header[28], &memsz, 4);
    prog_header[32] = 0x00;  /* align low byte */
    prog_header[33] = 0x10;  /* align = 0x1000 */
    
    fwrite(elf_header, 1, 64, f);
    fwrite(prog_header, 1, 56, f);
    fwrite(code_buf.code, 1, code_buf.size, f);
    fclose(f);
    return 0;
}

/* Print code as hex dump */
void codegen_dump_hex(void) {
    printf("=== Native Code (%d bytes) ===\n", code_buf.size);
    for (int i = 0; i < code_buf.size; i++) {
        if (i % 16 == 0) printf("%04X: ", i);
        printf("%02X ", code_buf.code[i]);
        if (i % 16 == 15) printf("\n");
    }
    if (code_buf.size % 16 != 0) printf("\n");
    printf("=== End Native Code ===\n");
}

void codegen_free(void) {
    free(code_buf.code);
    code_buf.code = NULL;
}

/* Demo: generate simple function */
int main(int argc, char *argv[]) {
    printf("=== Nebulara Native Codegen Module ===\n\n");
    printf("Target: x86-64\n\n");
    
    current_target = TARGET_X64;
    code_init();
    
    /* Generate: mov rax, 42; ret */
    int rax = reg_alloc_alloc();
    emit_mov_reg_imm(rax, 42);
    reg_free(rax);
    
    /* ret instruction */
    code_emit(0xC3);
    
    codegen_dump_hex();
    codegen_free();
    
    printf("\nNative codegen module: OK\n");
    return 0;
}
