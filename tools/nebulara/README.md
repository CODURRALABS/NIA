# Nebulara

**Nebulara - The AI-Native Universal Programming Language**

An interpreter and transpiler for .nbs programs, with bytecode compilation, standard library, and npm distribution.

[![License: Proprietary](https://img.shields.io/badge/License-Proprietary-red.svg)]()
[![Status: Active Development](https://img.shields.io/badge/Status-Active-brightgreen.svg)]()

## Quick Start

```bash
# Install from npm
npm install -g @codurra/nebulara

# Run a .nbs file
neb run hello.nbs

# Transpile to JavaScript
neb transpile hello.nbs --target js

# Transpile to Python
neb transpile hello.nbs --target py

# Run the interactive REPL
neb repl
```

### Building from source

```bash
# Using npm
node scripts/build.js

# Using Make (Linux/macOS/MinGW)
make all

# Using batch file (Windows)
build.bat
```

## Language Syntax (Dialect A)

```
# Comments start with #

# Variables
LET name = "Nebulara"
LET count = 42
LET flag = TRUE
LET nothing = NULL

# Constants
CONST PI = 314

# Arithmetic
LET result = 10 + 5 * 2 - 3 / 1

# Strings
LET greeting = "Hello, " + name
PRINT(TO_UPPER(greeting))
PRINT(LEN(greeting))
PRINT(CHAR_AT(greeting, 0))
PRINT(SUBSTR(greeting, 0, 5))
PRINT(TRIM("  hello  "))

# Bitwise operations
PRINT(5 & 3)        # 1 (AND)
PRINT(5 | 3)        # 7 (OR)
PRINT(1 << 3)       # 8 (left shift)
PRINT(16 >> 2)      # 4 (right shift)

# Arrays
LET arr = [10, 20, 30, 40]
PRINT(arr[0])           # 10
arr[1] = 99             # Array mutation
PUSH(arr, 50)           # Append
LET last = POP(arr)     # Remove last

# Control flow
IF? count > 10 THEN:
    PRINT("big")
ELSEIF? count > 5 THEN:
    PRINT("medium")
ELSE:
    PRINT("small")
END!

# Loops
WHILE? count > 0 THEN:
    count = count - 1
END!

FOR! i = 0 TO 10 (STEP 2):
    PRINT(i)
END!

# Break and CONTINUE
FOR! i = 0 TO 100:
    IF? i == 5 THEN: BREAK END!
    IF? i % 2 == 0 THEN: CONTINUE END!
    PRINT(i)
END!

# Functions
FUNC! add(a, b):
    RETURN a + b
END!

LET sum = add(3, 4)

# Recursive functions
FUNC! factorial(n):
    IF? n <= 1 THEN:
        RETURN 1
    END!
    RETURN n * factorial(n - 1)
END!

# Exception handling
TRY!:
    THROW "something went wrong"
CATCH! err:
    PRINT("Caught: " + err)
ENDTRY!

# Type checking
PRINT(TYPEOF(42))           # int
PRINT(TYPEOF("hello"))      # string
PRINT(TYPEOF(TRUE))         # bool
PRINT(TYPEOF(NULL))         # null
PRINT(TYPEOF([1, 2, 3]))    # array

# Built-in functions
PRINT(ABS(-42))             # 42
PRINT(MIN(10, 20))          # 10
PRINT(MAX(10, 20))          # 20
PRINT(SQRT(16))             # 4
PRINT(POW(2, 10))           # 1024
PRINT(CHAR(65))             # A
PRINT(ORD("Z"))             # 90
PRINT(RANDOM())             # 0-99
PRINT(TIME())               # Unix timestamp
```

## Architecture

### Interpreters

| Binary | Source | Description |
|--------|--------|-------------|
| `nebulara.exe` | `nbs-bootstrap.c` | Primary interpreter (2200+ lines). Full AST, bytecode compiler, VM with 40+ opcodes. |
| `neb-cli.exe` | `nbs_cli.c` | Extended CLI interpreter. Additional features: TRY/CATCH, bitwise ops, build-to-bytecode, syntax highlighting. |

### Toolchain Modules

| Binary | Source | Description |
|--------|--------|-------------|
| `neb-pipeline.exe` | `neb-pipeline.c` | `.nbs` to JavaScript/Python transpiler (end-to-end) |
| `neb-semantic.exe` | `neb-semantic.c` | Scope and type checker (standalone demo) |
| `neb-ir.exe` | `neb-ir.c` | Three-address code IR (standalone demo) |
| `neb-codegen.exe` | `neb-codegen.c` | x86/x64 instruction encoder (standalone demo) |
| `neb-transpiler-js.exe` | `neb-transpiler-js.c` | JS transpiler helpers |
| `neb-transpiler-py.exe` | `neb-transpiler-py.c` | Python transpiler helpers |
| `neb-ffi.exe` | `neb-ffi.c` | FFI bridge (stub) |
| `neb-knowledge.exe` | `neb-knowledge.c` | Knowledge graph (standalone demo) |

### Standard Library (`std/`)

| File | Functions |
|------|-----------|
| `primitives.nbs` | `IS_INT()`, `IS_STRING()`, `IS_BOOL()`, `IS_NULL()`, `IS_ARRAY()`, `IS_FUNC()`, `IS_NUMBER()` |
| `math.nbs` | `abs()`, `min()`, `max()`, `clamp()`, `sum_array()`, `average()` |
| `string.nbs` | `concat()`, `repeat()`, `reverse()`, `contains()`, `to_upper()`, `to_lower()`, `trim()`, `substring()` |
| `collections.nbs` | `find()`, `contains()`, `reverse_array()`, `sum_array()`, `max_array()`, `min_array()` |
| `time.nbs` | `now()`, `elapsed()`, `sleep()` (stub) |
| `json.nbs` | `json_stringify()` (wraps TO_STRING), `json_parse()` (stub) |
| `net.nbs` | All stubs |

### npm Package

```
@codurra/nebulara
  bin/neb.js          - CLI entry point (neb / nebulara commands)
  dist/index.js       - Programmatic API
  registry/           - Local package registry
  build/              - All 10 compiled binaries
```

**API:**
```javascript
const { run, runString, transpileToJS, transpileToPython, check } = require('@codurra/nebulara');

run('./hello.nbs');
runString('PRINT("Hello!")');
transpileToJS('./app.nbs');      // Returns JavaScript source
transpileToPython('./app.nbs');   // Returns Python source
check('./app.nbs');               // Type checking
```

### Registry

```bash
# Publish a package
neb publish ./my-package

# Install a package
neb install @username/package-name

# Search packages
neb search "web framework"
```

## Built-in Functions (35+)

| Function | Description |
|----------|-------------|
| `PRINT(expr)` | Print value with newline |
| `LEN(x)` | String length or array count |
| `TYPEOF(x)` | Returns type name as string |
| `TO_STRING(x)` | Convert to string |
| `TO_NUMBER(x)` | Convert to integer |
| `TO_UPPER(s)` | Uppercase string |
| `TO_LOWER(s)` | Lowercase string |
| `CHAR_AT(s, i)` | Character at index (returns 1-char string) |
| `SUBSTR(s, start, len)` | Extract substring |
| `TRIM(s)` | Remove leading/trailing whitespace |
| `CHAR(n)` | Integer to ASCII character |
| `ORD(s)` | First character to integer |
| `ABS(n)` | Absolute value |
| `MIN(a, b)` | Minimum of two values |
| `MAX(a, b)` | Maximum of two values |
| `SQRT(n)` | Square root |
| `POW(base, exp)` | Exponentiation |
| `RANDOM()` | Random integer 0-99 |
| `TIME()` | Current Unix timestamp |
| `READ_FILE(path)` | Read file contents as string |
| `WRITE_FILE(path, content)` | Write string to file |
| `PUSH(arr, val)` | Append value to array |
| `POP(arr)` | Remove and return last element |

## Test Suite

```
test/hello.nbs          - Basic PRINT, LET, arithmetic
test/test-functions.nbs  - Functions, params, return values
test/test-loops.nbs     - WHILE, FOR, FOR with STEP
test/test-control.nbs   - BREAK/CONTINUE
test/test-recursion.nbs - Factorial, Fibonacci
test/test-arrays.nbs    - Indexing, length, sum, string arrays
test/test-strings.nbs   - Concatenation, builtins, type checking
```

Run all tests: `node scripts/test.js`

## License

Proprietary - CODURRA Labs & Technologies
