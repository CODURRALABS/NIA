#!/usr/bin/env node
'use strict';

const { execFileSync } = require('child_process');
const path = require('path');
const fs = require('fs');

const buildDir = path.resolve(__dirname, '..', 'build');
const testDir = path.resolve(__dirname, '..', 'test');
const isWin = process.platform === 'win32';
const exe = isWin ? 'nebulara.exe' : 'nebulara';
const bin = path.join(buildDir, exe);

if (!fs.existsSync(bin)) {
    console.error('Binary not found. Run "npm run build" first.');
    process.exit(1);
}

const tests = [
    { name: 'hello', file: 'hello.nbs', expected: ['Hello from Nebulara!', '42', '30'] },
    { name: 'functions', file: 'test-functions.nbs', expected: ['Function tests:', '7', '30', '30'] },
    { name: 'loops', file: 'test-loops.nbs', expected: ['1','2','3','4','5','0','5','10','15','20'] },
    { name: 'recursion', file: 'test-recursion.nbs', expected: ['120','3628800','55','610'] },
    { name: 'arrays', file: 'test-arrays.nbs', expected: ['10','30','50','5','150','hello','world','3'] },
    { name: 'strings', file: 'test-strings.nbs', expected: ['Hello World','8','42','130','string','int','true','false','null','bool','bool','null'] },
    { name: 'break', file: 'test-control.nbs', hasBreak: true, hasContinue: true },
];

let passed = 0, failed = 0;

for (const t of tests) {
    const filePath = path.join(testDir, t.file);
    if (!fs.existsSync(filePath)) {
        console.log(`SKIP  ${t.name} (file not found)`);
        continue;
    }
    try {
        const out = execFileSync(bin, [filePath], { encoding: 'utf8', timeout: 5000 });
        const lines = out.trim().split('\n').map(l => l.trim()).filter(l => l);

        if (t.expected) {
            const allFound = t.expected.every(e => lines.includes(e));
            if (allFound) {
                console.log(`PASS  ${t.name}`);
                passed++;
            } else {
                const missing = t.expected.filter(e => !lines.includes(e));
                console.log(`FAIL  ${t.name}`);
                console.log(`  Missing: ${missing.join(', ')}`);
                console.log(`  Got:      ${lines.join(', ')}`);
                failed++;
            }
        } else {
            console.log(`PASS  ${t.name} (output: ${lines.length} lines)`);
            passed++;
        }
    } catch (err) {
        console.log(`FAIL  ${t.name}: ${err.message}`);
        failed++;
    }
}

console.log(`\n${passed} passed, ${failed} failed`);
process.exit(failed > 0 ? 1 : 0);
