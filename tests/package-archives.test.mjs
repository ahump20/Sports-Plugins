import {test} from 'node:test';
import assert from 'node:assert/strict';
import {existsSync, mkdtempSync, rmSync, readFileSync} from 'node:fs';
import {spawnSync} from 'node:child_process';
import {tmpdir} from 'node:os';
import {join, resolve} from 'node:path';
const root = resolve(import.meta.dirname, '..');
const script = join(root, 'scripts/package-plugins.py');
function run(output, plugin = 'gameday-ops') {
  assert.ok(existsSync(script), 'Reproducible packager must exist');
  return spawnSync('python3', [script, '--plugin', plugin, '--output', output], {encoding: 'utf8', cwd: root});
}
test('plugin archive includes portable and compatibility manifests without a marketplace wrapper', () => {
  const temp = mkdtempSync(join(tmpdir(), 'sports-zip-'));
  try {
    const result = run(temp); assert.equal(result.status, 0, result.stderr);
    const manifest = JSON.parse(result.stdout); assert.equal(manifest.length, 1);
    const zip = join(temp, manifest[0].file);
    const inspect = spawnSync('python3', ['-c', 'import json,sys,zipfile; z=zipfile.ZipFile(sys.argv[1]); print(json.dumps(z.namelist()))', zip], {encoding: 'utf8'});
    assert.equal(inspect.status, 0, inspect.stderr); const names = JSON.parse(inspect.stdout);
    for (const name of ['plugin.json', '.claude-plugin/plugin.json', '.codex-plugin/plugin.json', 'LICENSE', 'skills/gameday-packet/scripts/game_packet.py']) assert.ok(names.includes(name), name);
    assert.ok(names.every(n => !n.includes('__pycache__') && !n.endsWith('.pyc') && !n.includes('marketplace.json')));
    assert.equal(manifest[0].sha256.length, 64);
  } finally {rmSync(temp, {recursive: true, force: true});}
});
test('archive bytes are reproducible from the same input', () => {
  const first = mkdtempSync(join(tmpdir(), 'sports-zip-a-')); const second = mkdtempSync(join(tmpdir(), 'sports-zip-b-'));
  try {
    const a = run(first); const b = run(second); assert.equal(a.status, 0, a.stderr); assert.equal(b.status, 0, b.stderr);
    const aa = JSON.parse(a.stdout)[0]; const bb = JSON.parse(b.stdout)[0];
    assert.equal(aa.sha256, bb.sha256); assert.deepEqual(readFileSync(join(first, aa.file)), readFileSync(join(second, bb.file)));
  } finally {rmSync(first, {recursive: true, force: true}); rmSync(second, {recursive: true, force: true});}
});
test('packager rejects unknown and traversing plugin selections', () => {
  const temp = mkdtempSync(join(tmpdir(), 'sports-zip-invalid-'));
  try {for (const name of ['../outside', 'not-a-plugin']) {const result = run(temp, name); assert.equal(result.status, 2); assert.match(result.stderr, /Unknown plugin/);}}
  finally {rmSync(temp, {recursive: true, force: true});}
});
