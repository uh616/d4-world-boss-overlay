#!/usr/bin/env node
/**
 * release.js — usage: npm run release -- 2.2.0
 * 1. Updates package.json version
 * 2. Commits the change
 * 3. Creates git tag vX.X.X
 * 4. Pushes master + tag → triggers GitHub Actions build
 */

const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

const version = process.argv[2];
if (!version || !/^\d+\.\d+\.\d+$/.test(version)) {
    console.error('Usage: npm run release -- <version>   e.g.  npm run release -- 2.2.0');
    process.exit(1);
}

const tag = `v${version}`;
const pkgPath = path.join(__dirname, '..', 'package.json');
const pkg = JSON.parse(fs.readFileSync(pkgPath, 'utf8'));

console.log(`\n🚀 Releasing ${tag}  (was ${pkg.version})\n`);

// 1. Update package.json
pkg.version = version;
fs.writeFileSync(pkgPath, JSON.stringify(pkg, null, 2) + '\n', 'utf8');
console.log('✅ package.json updated');

// 2. Commit
execSync(`git add package.json`, { stdio: 'inherit' });
execSync(`git commit -m "chore: release ${tag}"`, { stdio: 'inherit' });
console.log('✅ Committed');

// 3. Tag
try {
    execSync(`git tag ${tag}`, { stdio: 'inherit' });
} catch {
    // Tag might already exist locally — delete and recreate
    execSync(`git tag -d ${tag}`, { stdio: 'inherit' });
    execSync(`git tag ${tag}`, { stdio: 'inherit' });
}
console.log(`✅ Tagged ${tag}`);

// 4. Push
execSync(`git push origin master --tags`, { stdio: 'inherit' });
console.log(`\n✅ Pushed! GitHub Actions is now building the release.\n`);
console.log(`   Check progress: https://github.com/uh616/d4-world-boss-overlay/actions`);
