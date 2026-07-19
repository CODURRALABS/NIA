# Nebulara Language

**AI-Native Universal Programming Language**

## Quick Start

```bash
npm install @codurra/nebulara
neb run program.nbs
neb test           # run built-in test suite
```

## What is Nebulara?

Nebulara is a simple, readable programming language designed for AI-native workflows. It features a C-like syntax with English keywords, optional semicolons, and built-in support for AI/ML operations.

## Features

- **Simple Syntax** - No mandatory semicolons, colons, or brackets
- **Zero Dependencies** - Self-contained interpreter and CLI
- **AI-Native** - Neural primitives, knowledge graph, agent orchestration
- **Multi-Target** - Interpreter, transpiler (JS/Python), native compiler
- **NPM Distribution** - Easy install, cross-platform

## Language Basics

```nebulara
# Variable declaration
LET name = "Nebulara"
LET x = 42

# Function definition
FUNC! add(a, b):
  RETURN a + b
END!

PRINT add(3, 4)  # prints 7

# Control flow
IF? x > 10:
  PRINT "big"
ELSE:
  PRINT "small"
END!

# Loops
FOR! i = 1 TO 5:
  PRINT i
END!

WHILE? x < 100:
  x = x * 2
END!
```

## Documentation

- [SPEC.md](../SPEC.md) - Language specification
- [CHANGELOG.md](CHANGELOG.md) - Version history

## License

Proprietary - All rights reserved.
