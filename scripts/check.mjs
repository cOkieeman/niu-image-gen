import assert from 'node:assert/strict';
import { existsSync, readFileSync } from 'node:fs';
import { dirname, resolve, sep } from 'node:path';
import { fileURLToPath } from 'node:url';
import { spawnSync } from 'node:child_process';

const root = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const readJson = path => JSON.parse(readFileSync(resolve(root, path), 'utf8'));
const portable = readJson('plugin.json');
const legacy = readJson('.codex-plugin/plugin.json');
const pkg = readJson('package.json');
const market = readJson('.agents/plugins/marketplace.json');

assert.equal(portable.name, 'niu-image-gen');
for (const manifest of [legacy, pkg]) {
  assert.equal(manifest.name, portable.name);
  assert.equal(manifest.version, portable.version);
}
assert.equal(portable.license, 'Apache-2.0');
assert.deepEqual(portable.extensions['com.openai'].interface, legacy.interface);

function checkPath(path) {
  assert.ok(path.startsWith('./'), `Relative plugin path required: ${path}`);
  assert.ok(!path.split(/[\\/]/).includes('..'), `Parent traversal: ${path}`);
  const target = resolve(root, path);
  assert.ok(target === root || target.startsWith(root + sep), `Path escapes plugin: ${path}`);
  assert.ok(existsSync(target), `Missing plugin resource: ${path}`);
}

checkPath(legacy.skills);
checkPath(legacy.interface.composerIcon);
checkPath(legacy.interface.logo);
assert.equal(market.name, 'niu-image-gen');
assert.equal(market.plugins.length, 1);
const entry = market.plugins[0];
assert.equal(entry.name, portable.name);
assert.equal(entry.source.source, 'local');
assert.equal(entry.source.path, './');
checkPath(entry.source.path);
assert.equal(entry.policy.installation, 'AVAILABLE');
assert.equal(entry.policy.authentication, 'ON_USE');
assert.equal(entry.category, 'Productivity');

for (const path of ['skills/niu-image-gen/SKILL.md', 'skills/niu-image-gen/agents/openai.yaml', 'LICENSE', 'NOTICE', 'README.md', 'UPSTREAM.md']) {
  assert.ok(existsSync(resolve(root, path)), `Missing package file: ${path}`);
}
const skill = readFileSync(resolve(root, 'skills/niu-image-gen/SKILL.md'), 'utf8');
assert.ok(!skill.includes('$HOME/plugins/niu-image-gen'), 'Obsolete script location');
assert.ok(skill.includes('220s') && skill.includes('250s'), 'Timeout documentation out of sync');

const help = spawnSync(process.execPath, [resolve(root, 'scripts/generate.mjs'), '--help'], { encoding: 'utf8', timeout: 10000 });
assert.equal(help.error, undefined);
assert.equal(help.status, 0, help.stderr);
for (const flag of ['--prompt', '--batch', '--edit', '--get-config']) {
  assert.ok(help.stdout.includes(flag), `Missing CLI help: ${flag}`);
}
console.log(`Validated Niu Image Gen ${portable.version}: manifests, marketplace, assets, skill paths and CLI help.`);

const python = process.env.NIU_PYTHON || 'python';
const pythonEnv = { ...process.env, PYTHONIOENCODING: 'utf-8', PYTHONDONTWRITEBYTECODE: '1' };
const gemini = resolve(root, 'skills/momo-image-gen/scripts/generate_image.py');
const geminiHelp = spawnSync(python, [gemini, '--help'], { encoding: 'utf8', timeout: 10000, env: pythonEnv });
assert.equal(geminiHelp.error, undefined, 'Python is required; set NIU_PYTHON to its executable path if needed.');
assert.equal(geminiHelp.status, 0, geminiHelp.stderr);
assert.ok(geminiHelp.stdout.includes('--input-image'));
assert.ok(geminiHelp.stdout.includes('--image-size'));
const tests = spawnSync(python, ['-m', 'unittest', 'discover', '-s', 'tests', '-v'], {
  cwd: root, encoding: 'utf8', timeout: 30000, env: pythonEnv
});
assert.equal(tests.error, undefined);
process.stdout.write(tests.stdout);
process.stdout.write(tests.stderr);
assert.equal(tests.status, 0, 'Offline Gemini integration checks failed');
