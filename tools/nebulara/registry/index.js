/**
 * @codurra/nebulara-registry - Package Registry Prototype
 * 
 * Local package registry for Nebulara packages.
 * Uses a simple JSON-based package database.
 */

'use strict';

const fs = require('fs');
const path = require('path');
const crypto = require('crypto');

const REGISTRY_DIR = path.join(__dirname, 'data');
const PACKAGES_DB = path.join(REGISTRY_DIR, 'packages.json');

/**
 * Initialize the registry
 */
function init() {
    if (!fs.existsSync(REGISTRY_DIR)) {
        fs.mkdirSync(REGISTRY_DIR, { recursive: true });
    }
    if (!fs.existsSync(PACKAGES_DB)) {
        fs.writeFileSync(PACKAGES_DB, JSON.stringify({ packages: {} }, null, 2));
    }
}

/**
 * Load the packages database
 */
function loadDB() {
    init();
    return JSON.parse(fs.readFileSync(PACKAGES_DB, 'utf8'));
}

/**
 * Save the packages database
 */
function saveDB(db) {
    fs.writeFileSync(PACKAGES_DB, JSON.stringify(db, null, 2));
}

/**
 * Publish a package
 * @param {string} name - Package name (e.g., "mylib")
 * @param {string} version - Semantic version (e.g., "1.0.0")
 * @param {string} sourcePath - Path to .nbs file
 * @param {object} meta - { description, author, tags }
 */
function publish(name, version, sourcePath, meta = {}) {
    if (!fs.existsSync(sourcePath)) {
        throw new Error(`Source file not found: ${sourcePath}`);
    }

    const db = loadDB();
    
    if (!db.packages[name]) {
        db.packages[name] = { versions: {}, created: new Date().toISOString() };
    }

    if (db.packages[name].versions[version]) {
        throw new Error(`Package ${name}@${version} already exists`);
    }

    const source = fs.readFileSync(sourcePath, 'utf8');
    const hash = crypto.createHash('sha256').update(source).digest('hex');

    db.packages[name].versions[version] = {
        source,
        hash,
        description: meta.description || '',
        author: meta.author || '',
        tags: meta.tags || [],
        published: new Date().toISOString(),
        size: Buffer.byteLength(source)
    };

    db.packages[name].description = meta.description || db.packages[name].description;
    db.packages[name].author = meta.author || db.packages[name].author;

    saveDB(db);
    return { name, version, hash };
}

/**
 * Install (download) a package
 * @param {string} name - Package name
 * @param {string} version - Version (or "latest")
 * @param {string} destDir - Destination directory
 */
function install(name, version = 'latest', destDir = './') {
    const db = loadDB();
    
    if (!db.packages[name]) {
        throw new Error(`Package ${name} not found`);
    }

    const pkg = db.packages[name];
    
    if (version === 'latest') {
        const versions = Object.keys(pkg.versions);
        version = versions[versions.length - 1];
    }

    if (!pkg.versions[version]) {
        throw new Error(`Package ${name}@${version} not found`);
    }

    const ver = pkg.versions[version];
    const outPath = path.join(destDir, `${name}.nbs`);
    fs.writeFileSync(outPath, ver.source);

    return { name, version, path: outPath, hash: ver.hash };
}

/**
 * Search packages
 * @param {string} query - Search query
 * @returns {Array} Matching packages
 */
function search(query) {
    const db = loadDB();
    const results = [];
    const q = query.toLowerCase();

    for (const [name, pkg] of Object.entries(db.packages)) {
        if (name.toLowerCase().includes(q) ||
            (pkg.description || '').toLowerCase().includes(q)) {
            const versions = Object.keys(pkg.versions);
            results.push({
                name,
                description: pkg.description,
                author: pkg.author,
                version: versions[versions.length - 1],
                versions: versions.length
            });
        }
    }

    return results;
}

/**
 * Get package info
 * @param {string} name - Package name
 * @returns {object} Package info
 */
function info(name) {
    const db = loadDB();
    
    if (!db.packages[name]) {
        throw new Error(`Package ${name} not found`);
    }

    const pkg = db.packages[name];
    const versions = Object.keys(pkg.versions);

    return {
        name,
        description: pkg.description,
        author: pkg.author,
        created: pkg.created,
        latest: versions[versions.length - 1],
        versions: versions.map(v => ({
            version: v,
            published: pkg.versions[v].published,
            size: pkg.versions[v].size,
            hash: pkg.versions[v].hash
        }))
    };
}

/**
 * List all packages
 * @returns {Array}
 */
function list() {
    const db = loadDB();
    return Object.keys(db.packages).map(name => ({
        name,
        description: db.packages[name].description,
        versions: Object.keys(db.packages[name].versions).length
    }));
}

module.exports = {
    init,
    publish,
    install,
    search,
    info,
    list
};
