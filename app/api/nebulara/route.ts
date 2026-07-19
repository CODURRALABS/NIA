import { NextResponse } from 'next/server';
import { execFileSync } from 'child_process';
import { writeFileSync, unlinkSync, existsSync, readFileSync } from 'fs';
import { join } from 'path';
import { tmpdir } from 'os';

const NEBULARA_DIR = join(process.cwd(), 'tools', 'nebulara');
const BUILD_DIR = join(NEBULARA_DIR, 'build');

function findBinary(): string | null {
    const candidates = [
        join(BUILD_DIR, 'nebulara.exe'),
        join(NEBULARA_DIR, 'nebulara.exe'),
    ];
    for (const p of candidates) {
        if (existsSync(p)) return p;
    }
    return null;
}

function findPipeline(): string | null {
    const candidates = [
        join(BUILD_DIR, 'neb-pipeline.exe'),
        join(NEBULARA_DIR, 'neb-pipeline.exe'),
    ];
    for (const p of candidates) {
        if (existsSync(p)) return p;
    }
    return null;
}

function executeNBS(code: string, timeout = 10000): { success: boolean; output: string; error?: string } {
    const bin = findBinary();
    if (!bin) {
        return { success: false, output: '', error: 'Nebulara binary not built. Run build.bat in tools/nebulara/' };
    }

    const tempFile = join(tmpdir(), `nia_neb_${Date.now()}.nbs`);
    try {
        writeFileSync(tempFile, code, 'utf-8');
        const result = execFileSync(bin, [tempFile], {
            timeout,
            encoding: 'utf-8',
            windowsHide: true,
        });
        return { success: true, output: result };
    } catch (err: any) {
        return {
            success: false,
            output: err.stdout || '',
            error: err.stderr || err.message || 'Execution failed',
        };
    } finally {
        if (existsSync(tempFile)) unlinkSync(tempFile);
    }
}

function transpileNBS(code: string, target: 'js' | 'py'): { success: boolean; output: string; error?: string } {
    const pipeline = findPipeline();
    if (!pipeline) {
        return { success: false, output: '', error: 'Nebulara pipeline not built.' };
    }

    const ext = target === 'js' ? '.js' : '.py';
    const tempIn = join(tmpdir(), `nia_trans_${Date.now()}.nbs`);
    const tempOut = join(tmpdir(), `nia_trans_${Date.now()}${ext}`);

    try {
        writeFileSync(tempIn, code, 'utf-8');
        const result = execFileSync(pipeline, [tempIn, '--target', target, '--output', tempOut], {
            timeout: 10000,
            encoding: 'utf-8',
            windowsHide: true,
        });

        if (existsSync(tempOut)) {
            const output = readFileSync(tempOut, 'utf-8');
            return { success: true, output };
        }
        return { success: false, output: result, error: 'Transpilation produced no output' };
    } catch (err: any) {
        return { success: false, output: '', error: err.stderr || err.message };
    } finally {
        if (existsSync(tempIn)) unlinkSync(tempIn);
        if (existsSync(tempOut)) unlinkSync(tempOut);
    }
}

function generateNBS(goal: string): string {
    const g = goal.toLowerCase();

    if (g.includes('hello') || g.includes('greet')) {
        return 'PRINT("Hello from NIA via Nebulara!")';
    }
    if (g.includes('fibonacci')) {
        return `FUNC! fibonacci(n):\n    IF? n <= 1 THEN:\n        RETURN n\n    END!\n    RETURN fibonacci(n - 1) + fibonacci(n - 2)\nEND!\n\nFOR! i = 0 TO 10:\n    PRINT(fibonacci(i))\nEND!`;
    }
    if (g.includes('factorial')) {
        return `FUNC! factorial(n):\n    IF? n <= 1 THEN:\n        RETURN 1\n    END!\n    RETURN n * factorial(n - 1)\nEND!\n\nPRINT(factorial(10))`;
    }
    if (g.includes('array') || g.includes('sum')) {
        return `LET arr = [10, 20, 30, 40, 50]\nLET total = 0\nFOR! i = 0 TO 5:\n    total = total + arr[i]\nEND!\nPRINT("Sum: " + TO_STRING(total))`;
    }
    if (g.includes('math')) {
        return `PRINT("Square root of 144: " + TO_STRING(SQRT(144)))\nPRINT("2 to the power of 10: " + TO_STRING(POW(2, 10)))\nPRINT("Random number: " + TO_STRING(RANDOM()))\nPRINT("Absolute of -42: " + TO_STRING(ABS(-42)))`;
    }

    return `PRINT("NIA Nebulara: ${goal}")`;
}

export async function POST(req: Request) {
    try {
        const { action, code, goal, target } = await req.json();

        switch (action) {
            case 'execute': {
                if (!code) {
                    return NextResponse.json({ error: 'Code required for execution' }, { status: 400 });
                }
                const result = executeNBS(code);
                return NextResponse.json(result);
            }

            case 'generate': {
                if (!goal) {
                    return NextResponse.json({ error: 'Goal required for generation' }, { status: 400 });
                }
                const generated = generateNBS(goal);
                const execResult = executeNBS(generated);
                return NextResponse.json({
                    success: true,
                    code: generated,
                    execution: execResult,
                    goal,
                });
            }

            case 'transpile': {
                if (!code) {
                    return NextResponse.json({ error: 'Code required for transpilation' }, { status: 400 });
                }
                const t = (target as 'js' | 'py') || 'js';
                const result = transpileNBS(code, t);
                return NextResponse.json({ ...result, target: t });
            }

            case 'status': {
                return NextResponse.json({
                    binary: findBinary(),
                    pipeline: findPipeline(),
                    stdLib: existsSync(join(NEBULARA_DIR, 'std')),
                    ready: !!findBinary(),
                });
            }

            default:
                return NextResponse.json({ error: `Unknown action: ${action}` }, { status: 400 });
        }
    } catch (error: any) {
        console.error('[Nebulara API] Error:', error);
        return NextResponse.json({ error: error.message }, { status: 500 });
    }
}
