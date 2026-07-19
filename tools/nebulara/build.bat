@echo off
echo ========================================
echo Nebulara Build
echo ========================================

if not exist build mkdir build

set FAIL=0

echo [1/6] Building interpreter...
gcc -static -O2 -Wall "Compiler\nbs-bootstrap.c" -o "build\nebulara.exe" -lm
if %errorlevel% neq 0 (echo [FAIL] Interpreter build failed & set FAIL=1) else (echo [OK] build\nebulara.exe)

echo [2/6] Building CLI...
gcc -static -O2 -Wall "Compiler\nbs_cli.c" -o "build\neb-cli.exe" -lm
if %errorlevel% neq 0 (echo [FAIL] CLI build failed & set FAIL=1) else (echo [OK] build\neb-cli.exe)

echo [3/6] Building pipeline (includes semantic analyzer)...
gcc -O2 -Wall "Compiler\neb-pipeline.c" -o "build\neb-pipeline.exe"
if %errorlevel% neq 0 (echo [FAIL] Pipeline build failed & set FAIL=1) else (echo [OK] build\neb-pipeline.exe)

echo [4/6] Building native codegen...
gcc -static -O2 -Wall "Compiler\neb-codegen.c" -o "build\neb-codegen.exe"
if %errorlevel% neq 0 (echo [FAIL] Codegen build failed & set FAIL=1) else (echo [OK] build\neb-codegen.exe)

echo [5/6] Building FFI module...
gcc -static -O2 -Wall "Compiler\neb-ffi.c" -o "build\neb-ffi.exe"
if %errorlevel% neq 0 (echo [FAIL] FFI build failed & set FAIL=1) else (echo [OK] build\neb-ffi.exe)

echo [6/6] Building knowledge graph...
gcc -static -O2 -Wall "Compiler\neb-knowledge.c" -o "build\neb-knowledge.exe"
if %errorlevel% neq 0 (echo [FAIL] Knowledge graph build failed & set FAIL=1) else (echo [OK] build\neb-knowledge.exe)

if %FAIL% neq 0 (
    echo.
    echo Build FAILED
    exit /b 1
)

echo.
echo Running tests...
build\nebulara.exe test\hello.nbs
if %errorlevel% neq 0 (echo [FAIL] Test failed & exit /b 1)
echo [OK] All tests passed

echo.
echo Build complete! 6 binaries in build\
