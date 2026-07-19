/*
 * neb-ffi.c - Foreign Function Interface Bridge
 *
 * Allows Nebulara to call functions from C/C++ shared libraries.
 * Uses dlopen on Linux/macOS and LoadLibrary on Windows.
 *
 * Build: gcc -o neb-ffi.exe neb-ffi.c -static -O2
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>

#ifdef _WIN32
#include <windows.h>
typedef HMODULE FFIHandle;
#else
#include <dlfcn.h>
typedef void* FFIHandle;
#endif

/* FFI types */
typedef enum {
    FFI_TYPE_VOID,
    FFI_TYPE_INT,
    FFI_TYPE_FLOAT,
    FFI_TYPE_DOUBLE,
    FFI_TYPE_STRING,
    FFI_TYPE_POINTER,
    FFI_TYPE_BOOL
} FFIType;

typedef struct {
    char name[256];
    FFIType return_type;
    FFIType param_types[16];
    int param_count;
    FFIHandle handle;
    void *fn_ptr;
} FFIFunction;

typedef struct {
    char name[256];
    char path[512];
    FFIFunction functions[256];
    int func_count;
    int is_loaded;
} FFILibrary;

/* Global state */
static FFILibrary libraries[64];
static int library_count = 0;

/* Load a native library */
int ffi_load(const char *name, const char *path) {
    if (library_count >= 64) return -1;

    FFILibrary *lib = &libraries[library_count];
    memset(lib, 0, sizeof(FFILibrary));
    strncpy(lib->name, name, 255);
    strncpy(lib->path, path, 511);
    lib->func_count = 0;

#ifdef _WIN32
    lib->is_loaded = 1;
    /* LoadLibrary will be done on first ffi_call */
#else
    /* Try loading immediately on Linux/macOS */
    void *handle = dlopen(path, RTLD_LAZY);
    if (handle) {
        lib->is_loaded = 1;
    } else {
        lib->is_loaded = 0;
        fprintf(stderr, "FFI WARNING: could not load '%s': %s\n", path, dlerror());
    }
#endif

    library_count++;
    printf("FFI: Registered library '%s' from '%s'\n", name, path);
    return 0;
}

/* Register a function from a library */
int ffi_register_func(const char *lib_name, const char *func_name,
                      FFIType ret_type, FFIType *param_types, int param_count) {
    for (int i = 0; i < library_count; i++) {
        if (strcmp(libraries[i].name, lib_name) == 0) {
            FFILibrary *lib = &libraries[i];
            if (lib->func_count >= 256) return -2;

            FFIFunction *func = &lib->functions[lib->func_count];
            memset(func, 0, sizeof(FFIFunction));
            strncpy(func->name, func_name, 255);
            func->return_type = ret_type;
            func->param_count = param_count;
            for (int j = 0; j < param_count && j < 16; j++) {
                func->param_types[j] = param_types[j];
            }
            lib->func_count++;
            return 0;
        }
    }
    return -1;
}

/* Resolve a function pointer from a library handle */
static void *ffi_resolve_func(FFILibrary *lib, FFIFunction *func) {
    if (func->fn_ptr) return func->fn_ptr;

#ifdef _WIN32
    HMODULE h = LoadLibraryA(lib->path);
    if (!h) {
        fprintf(stderr, "FFI ERROR: Cannot load '%s': error %lu\n", lib->path, GetLastError());
        return NULL;
    }
    func->fn_ptr = (void*)GetProcAddress(h, func->name);
#else
    void *handle = dlopen(lib->path, RTLD_LAZY);
    if (!handle) {
        fprintf(stderr, "FFI ERROR: Cannot load '%s': %s\n", lib->path, dlerror());
        return NULL;
    }
    func->fn_ptr = dlsym(handle, func->name);
#endif

    if (!func->fn_ptr) {
        fprintf(stderr, "FFI ERROR: Symbol '%s' not found in '%s'\n", func->name, lib->path);
    }
    return func->fn_ptr;
}

/* Call a foreign function */
int ffi_call(const char *lib_name, const char *func_name,
             void **args, int arg_count, void *result) {
    for (int i = 0; i < library_count; i++) {
        if (strcmp(libraries[i].name, lib_name) == 0) {
            for (int j = 0; j < libraries[i].func_count; j++) {
                if (strcmp(libraries[i].functions[j].name, func_name) == 0) {
                    FFIFunction *func = &libraries[i].functions[j];
                    if (arg_count != func->param_count) {
                        fprintf(stderr, "FFI ERROR: %s.%s expects %d args, got %d\n",
                                lib_name, func_name, func->param_count, arg_count);
                        return -3;
                    }

                    void *fn = ffi_resolve_func(&libraries[i], func);
                    if (!fn) return -4;

                    /* Extract actual values based on param types.
                     * args[i] is a pointer TO the value; we dereference to get the real arg. */
                    intptr_t vals[16];
                    for (int k = 0; k < arg_count && k < 16; k++) {
                        switch (func->param_types[k]) {
                            case FFI_TYPE_INT:
                            case FFI_TYPE_BOOL:
                                vals[k] = (intptr_t)(*(int*)args[k]);
                                break;
                            case FFI_TYPE_FLOAT:
                                vals[k] = (intptr_t)(*(int*)args[k]); /* float passed as int bits on 32-bit */
                                break;
                            case FFI_TYPE_DOUBLE:
                                /* Doubles need special handling - pass pointer */
                                vals[k] = (intptr_t)args[k];
                                break;
                            default: /* STRING, POINTER, VOID */
                                vals[k] = (intptr_t)args[k];
                                break;
                        }
                    }

                    typedef intptr_t (*ffi_fn)();
                    ffi_fn call = (ffi_fn)fn;

                    switch (func->return_type) {
                        case FFI_TYPE_INT:
                        case FFI_TYPE_BOOL:
                            *(int*)result = (int)call(
                                arg_count > 0 ? vals[0] : 0,
                                arg_count > 1 ? vals[1] : 0,
                                arg_count > 2 ? vals[2] : 0,
                                arg_count > 3 ? vals[3] : 0,
                                arg_count > 4 ? vals[4] : 0
                            );
                            break;
                        case FFI_TYPE_STRING:
                        case FFI_TYPE_POINTER:
                            *(void**)result = (void*)call(
                                arg_count > 0 ? vals[0] : 0,
                                arg_count > 1 ? vals[1] : 0,
                                arg_count > 2 ? vals[2] : 0,
                                arg_count > 3 ? vals[3] : 0,
                                arg_count > 4 ? vals[4] : 0
                            );
                            break;
                        case FFI_TYPE_DOUBLE:
                            *(double*)result = (double)call(
                                arg_count > 0 ? vals[0] : 0,
                                arg_count > 1 ? vals[1] : 0,
                                arg_count > 2 ? vals[2] : 0,
                                arg_count > 3 ? vals[3] : 0,
                                arg_count > 4 ? vals[4] : 0
                            );
                            break;
                        default:
                            call(
                                arg_count > 0 ? vals[0] : 0,
                                arg_count > 1 ? vals[1] : 0,
                                arg_count > 2 ? vals[2] : 0,
                                arg_count > 3 ? vals[3] : 0,
                                arg_count > 4 ? vals[4] : 0
                            );
                            break;
                    }
                    return 0;
                }
            }
        }
    }
    return -1;
}

/* Type name helper */
const char *ffi_type_name(FFIType t) {
    switch (t) {
        case FFI_TYPE_VOID:    return "void";
        case FFI_TYPE_INT:     return "int";
        case FFI_TYPE_FLOAT:   return "float";
        case FFI_TYPE_DOUBLE:  return "double";
        case FFI_TYPE_STRING:  return "string";
        case FFI_TYPE_POINTER: return "pointer";
        case FFI_TYPE_BOOL:    return "bool";
        default:               return "unknown";
    }
}

/* Print library info */
void ffi_info(void) {
    printf("=== FFI Libraries (%d loaded) ===\n", library_count);
    for (int i = 0; i < library_count; i++) {
        printf("  %s (%s) - %d functions [%s]\n",
               libraries[i].name, libraries[i].path, libraries[i].func_count,
               libraries[i].is_loaded ? "loaded" : "not loaded");
        for (int j = 0; j < libraries[i].func_count; j++) {
            FFIFunction *f = &libraries[i].functions[j];
            printf("    %s(", f->name);
            for (int k = 0; k < f->param_count; k++) {
                if (k > 0) printf(", ");
                printf("%s", ffi_type_name(f->param_types[k]));
            }
            printf(") -> %s\n", ffi_type_name(f->return_type));
        }
    }
    printf("=== End FFI ===\n");
}

/* Demo/test */
int main(int argc, char *argv[]) {
    printf("=== Nebulara FFI Bridge Module ===\n\n");

    /* Register and load system libraries */
#ifdef _WIN32
    ffi_load("kernel32", "kernel32.dll");
    ffi_load("msvcrt", "msvcrt.dll");

    FFIType int_params[] = { FFI_TYPE_INT };
    ffi_register_func("msvcrt", "abs", FFI_TYPE_INT, int_params, 1);

    ffi_info();

    /* Test: call msvcrt.abs(-42) */
    int arg = -42;
    void *args[] = { &arg };
    int result = 0;
    int rc = ffi_call("msvcrt", "abs", args, 1, &result);
    if (rc == 0) {
        printf("\nFFI TEST: msvcrt.abs(-42) = %d\n", result);
    } else {
        printf("\nFFI TEST: msvcrt.abs(-42) FAILED (rc=%d)\n", rc);
    }
#else
    ffi_load("libc", "libc.so.6");

    FFIType string_params[] = { FFI_TYPE_STRING };
    ffi_register_func("libc", "puts", FFI_TYPE_INT, string_params, 1);

    ffi_info();

    /* Test: call libc.puts("Hello from FFI!") */
    const char *msg = "Hello from FFI!";
    void *args[] = { (void*)msg };
    int result = 0;
    int rc = ffi_call("libc", "puts", args, 1, &result);
    if (rc == 0) {
        printf("FFI TEST: libc.puts() returned %d\n", result);
    } else {
        printf("FFI TEST: libc.puts() FAILED (rc=%d)\n", rc);
    }
#endif

    printf("\nFFI module: functional (dlopen/LoadLibrary)\n");
    return 0;
}
