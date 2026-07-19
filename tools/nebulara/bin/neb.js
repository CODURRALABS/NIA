#!/usr/bin/env node
'use strict';

const { execFileSync } = require('child_process');
const path = require('path');
const fs = require('fs');

const args = process.argv.slice(2);
const exeName = process.platform === 'win32' ? 'nebulara.exe' : 'nebulara';

// Try to find the native binary
function findBinary() {
    // In installed package: bin/../build/
    const pkgRoot = path.resolve(__dirname, '..');
    const candidates = [
        path.join(pkgRoot, 'build', exeName),
        path.join(pkgRoot, exeName),
    ];
    for (const p of candidates) {
        if (fs.existsSync(p)) return p;
    }
    return null;
}

const bin = findBinary();
if (!bin) {
    console.error('Error: Nebulara binary not found. Run "npm run build" first.');
    process.exit(1);
}

try {
    execFileSync(bin, args, { stdio: 'inherit' });
} catch (err) {
    if (err.status !== undefined) process.exit(err.status);
    process.exit(1);
}
