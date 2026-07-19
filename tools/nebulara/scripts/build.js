#!/usr/bin/env node
'use strict';

const { execSync } = require('child_process');
const path = require('path');
const fs = require('fs');

const buildDir = path.resolve(__dirname, '..', 'build');
if (!fs.existsSync(buildDir)) fs.mkdirSync(buildDir, { recursive: true });

const isWin = process.platform === 'win32';
const exe = isWin ? '.exe' : '';

function findGCC() {
    const candidates = isWin ? [
        'C:\\mingw-w64\\mingw32\\bin\\gcc.exe',
        'C:\\mingw64\\bin\\gcc.exe',
        'gcc',
    ] : ['gcc'];

    for (const gcc of candidates) {
        try {
            execSync(`"${gcc}" --version`, { stdio: 'ignore', shell: true });
            return gcc;
        } catch {}
    }
    return null;
}

const gcc = findGCC();
if (!gcc) {
    console.error('Error: GCC not found. Install MinGW-w64 (Windows) or gcc (Linux/Mac).');
    process.exit(1);
}

const flags = '-static -O2';

const targets = [
    { src: 'Compiler/nbs-bootstrap.c', out: `nebulara${exe}`, extra: '-lm' },
    { src: 'Compiler/nbs_cli.c', out: `neb-cli${exe}`, extra: '-lm' },
    { src: 'Compiler/neb-pipeline.c', out: `neb-pipeline${exe}`, extra: '' },
    { src: 'Compiler/neb-codegen.c', out: `neb-codegen${exe}`, extra: '' },
    { src: 'Compiler/neb-ffi.c', out: `neb-ffi${exe}`, extra: '' },
    { src: 'Compiler/neb-knowledge.c', out: `neb-knowledge${exe}`, extra: '' },
];

let ok = 0, fail = 0;
for (const t of targets) {
    const src = path.resolve(__dirname, '..', t.src);
    if (!fs.existsSync(src)) { console.log(`SKIP ${t.out} (${t.src} not found)`); continue; }
    const out = path.join(buildDir, t.out);
    const extra = t.extra ? ' ' + t.extra : '';
    const cmd = `"${gcc}" ${flags} "${src}" -o "${out}"${extra}`;
    console.log(`Building ${t.out}...`);
    try {
        execSync(cmd, { stdio: 'pipe', shell: true });
        console.log(`  OK: ${t.out}`);
        ok++;
    } catch (err) {
        console.error(`  FAILED: ${t.out}`);
        fail++;
    }
}

console.log(`\nBuild complete: ${ok} succeeded, ${fail} failed`);
if (fail > 0) process.exit(1);
