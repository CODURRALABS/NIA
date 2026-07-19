import { NextResponse } from 'next/server';
import { spawn } from 'child_process';
import path from 'path';
import fs from 'fs';
import os from 'os';

export async function POST(req: Request) {
    try {
        const { command, autonomous = false } = await req.json();

        if (!command || typeof command !== 'string') {
            return NextResponse.json({ error: 'Command string is required' }, { status: 400 });
        }

        const goalFile = path.join(os.tmpdir(), `nia_goal_${Date.now()}.json`);
        fs.writeFileSync(goalFile, JSON.stringify({
            goal: command,
            autonomous
        }));

        const scriptPath = path.join(process.cwd(), 'core', 'pulse', 'runtime', 'chat.py');

        const result = await new Promise<{ stdout: string; stderr: string }>((resolve, reject) => {
            const proc = spawn('python', [scriptPath, '--goal-file', goalFile], {
                cwd: path.join(process.cwd(), 'core', 'pulse'),
                stdio: ['pipe', 'pipe', 'pipe']
            });

            let stdout = '';
            let stderr = '';
            proc.stdout.on('data', (data: Buffer) => { stdout += data.toString(); });
            proc.stderr.on('data', (data: Buffer) => { stderr += data.toString(); });
            proc.on('close', (code: number | null) => {
                try { fs.unlinkSync(goalFile); } catch {}
                if (code === 0) resolve({ stdout, stderr });
                else reject(new Error(stderr || `Process exited with code ${code}`));
            });
            proc.on('error', (err) => {
                try { fs.unlinkSync(goalFile); } catch {}
                reject(err);
            });
        });

        if (result.stderr) {
            console.warn("Control stderr:", result.stderr);
        }

        return NextResponse.json({
            message: "Action executed successfully",
            output: result.stdout.trim()
        });
    } catch (error: any) {
        console.error("Control API Error:", error);
        return NextResponse.json({ error: error.message || 'Failed to execute control' }, { status: 500 });
    }
}
