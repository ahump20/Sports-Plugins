import { test } from 'node:test';
import assert from 'node:assert/strict';
import { existsSync, readFileSync, mkdtempSync, mkdirSync, writeFileSync, rmSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join, resolve } from 'node:path';
const root = resolve(import.meta.dirname, '..');
const checkerPath = join(root, 'scripts/package-contract.mjs');
async function checker() {
  assert.ok(existsSync(checkerPath), 'package-contract validator must exist');
  return (await import(checkerPath)).checkPackage;
}
test('native Codex and Claude catalogs list the same seven working plugins', () => {
  const path = join(root, '.agents/plugins/marketplace.json');
  assert.ok(existsSync(path), 'native Codex marketplace must exist');
  const codex = JSON.parse(readFileSync(path));
  const claude = JSON.parse(readFileSync(join(root, '.claude-plugin/marketplace.json')));
  assert.deepEqual(codex.plugins.map(p => p.name).sort(), claude.plugins.map(p => p.name).sort());
  assert.equal(codex.plugins.length, 7);
  for (const p of codex.plugins) assert.ok(existsSync(join(root, p.source.path, 'plugin.json')));
});
test('every listed plugin passes the actual package contract', async () => {
  const check = await checker();
  const catalog = JSON.parse(readFileSync(join(root, '.claude-plugin/marketplace.json')));
  for (const p of catalog.plugins) assert.deepEqual(check(join(root, p.source)), [], p.name);
});
function fixture() {
  const dir = mkdtempSync(join(tmpdir(), 'sports-package-'));
  mkdirSync(join(dir, '.claude-plugin')); mkdirSync(join(dir, '.codex-plugin')); mkdirSync(join(dir, 'skills/example'), {recursive: true});
  writeFileSync(join(dir, 'skills/example/SKILL.md'), '---\nname: example\ndescription: Example workflow\n---\nUse it.\n');
  const metadata = {name: 'example', version: '1.0.0', description: 'Example'};
  writeFileSync(join(dir, '.claude-plugin/plugin.json'), JSON.stringify(metadata));
  writeFileSync(join(dir, '.codex-plugin/plugin.json'), JSON.stringify({...metadata, skills: './skills/'}));
  writeFileSync(join(dir, 'plugin.json'), JSON.stringify({$schema: 'https://agent-plugins.org/schemas/1.0.0/plugin.schema.json', ...metadata}));
  return dir;
}
test('rejects path traversal, absent components and mismatched identities', async () => {
  const check = await checker(); const dir = fixture();
  try {
    assert.deepEqual(check(dir), []);
    const path = join(dir, '.codex-plugin/plugin.json');
    const data = JSON.parse(readFileSync(path));
    writeFileSync(path, JSON.stringify({...data, skills: '../outside'}));
    assert.ok(check(dir).some(e => /path|outside|escape/.test(e)));
    writeFileSync(path, JSON.stringify({...data, name: 'wrong'}));
    assert.ok(check(dir).some(e => /name|identity/.test(e)));
    writeFileSync(path, JSON.stringify({...data, interface: {composerIcon: './assets/missing.svg'}}));
    assert.ok(check(dir).some(e => /missing|exist/.test(e)));
  } finally { rmSync(dir, {recursive: true, force: true}); }
});
