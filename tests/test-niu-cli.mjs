import assert from 'node:assert/strict';
import { mkdtempSync, mkdirSync, readFileSync, writeFileSync, readdirSync, rmSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { resolve, join, dirname, basename } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';
import { spawnSync } from 'node:child_process';
import test from 'node:test';

const root = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const png = Buffer.from('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+aX1sAAAAASUVORK5CYII=', 'base64');

function runCase(kind, model, args, expectedCalls, expectedFiles) {
  const home = mkdtempSync(join(tmpdir(), 'niu-cli-check-'));
  try {
    mkdirSync(join(home, '.codex'));
    writeFileSync(join(home, '.codex', 'niu-image-gen-config.json'), JSON.stringify({ apiKey: 'test-local-key', quickMode: { count: 1 } }));
    const source = join(home, 'source.png');
    const secondSource = join(home, 'second.png');
    writeFileSync(source, png);
    writeFileSync(secondSource, png);
    const output = join(home, 'images');
    const callLog = join(home, 'calls.jsonl');
    const expanded = args.map(arg => arg === '<image>' ? source : arg === '<second-image>' ? secondSource : arg);
    const child = spawnSync(process.execPath, ['--import', pathToFileURL(resolve(root, 'tests/mock-image-fetch.mjs')).href, resolve(root, 'scripts/generate.mjs'), ...expanded, '--quality', '1K', '--ratio', 'square', '--output-dir', output], {
      encoding: 'utf8', timeout: 20000,
      env: { ...process.env, HOME: home, USERPROFILE: home, NIU_TEST_KIND: kind, NIU_TEST_MODEL: model, NIU_TEST_CALLS: callLog }
    });
    assert.equal(child.error, undefined);
    assert.equal(child.status, 0, child.stdout + child.stderr);
    const calls = readFileSync(callLog, 'utf8').trim().split('\n').map(line => JSON.parse(line));
    assert.equal(calls.length, expectedCalls);
    const files = readdirSync(output).filter(name => name.endsWith('.png'));
    assert.equal(files.length, expectedFiles);
    for (const file of files) assert.deepEqual(readFileSync(join(output, file)), png);
  } finally {
    assert.equal(dirname(home), resolve(tmpdir()));
    assert.ok(basename(home).startsWith('niu-cli-check-'));
    rmSync(home, { recursive: true, force: true });
  }
}

test('default generation keeps the existing model', () => {
  runCase('generate', 'gpt-image-2-x', ['--prompt', 'cat'], 1, 1);
});
test('single generation accepts image2.5', () => {
  runCase('generate', 'gpt-image-2.5', ['--model', 'gpt-image-2.5', '--prompt', 'cat'], 1, 1);
});
test('generation variations keep the selected model', () => {
  runCase('generate', 'gpt-image-2.5', ['--model', 'gpt-image-2.5', '--prompt', 'cat', '--count', '2'], 2, 2);
});
test('batch generation keeps the selected model', () => {
  runCase('generate', 'gpt-image-2.5', ['--model', 'gpt-image-2.5', '--batch-inline', 'cat', 'dog'], 2, 2);
});
test('image2.5 edit uses the dedicated multipart endpoint', () => {
  runCase('edit', 'gpt-image-2.5', ['--model', 'gpt-image-2.5', '--edit', '--image', '<image>', '--prompt', 'blue scarf'], 1, 1);
});
test('edit variations preserve model and count', () => {
  runCase('edit', 'gpt-image-2.5', ['--model', 'gpt-image-2.5', '--edit', '--image', '<image>', '--prompt', 'blue scarf', '--count', '2'], 1, 2);
});
test('batch edits preserve the selected model', () => {
  runCase('edit', 'gpt-image-2.5', ['--model', 'gpt-image-2.5', '--edit', '--image', '<image>', '--image', '<second-image>', '--prompt', 'blue scarf'], 2, 2);
});
test('default editing also uses the dedicated endpoint', () => {
  runCase('edit', 'gpt-image-2-x', ['--edit', '--image', '<image>', '--prompt', 'blue scarf'], 1, 1);
});
