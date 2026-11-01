import {test} from 'node:test';
import assert from 'node:assert/strict';
import {existsSync, mkdtempSync, rmSync, readFileSync, mkdirSync, copyFileSync, writeFileSync, readdirSync, symlinkSync} from 'node:fs';
import {createHash} from 'node:crypto';
import {spawnSync} from 'node:child_process';
import {tmpdir} from 'node:os';
import {join, resolve} from 'node:path';
const root = resolve(import.meta.dirname, '..');
function run(output, plugin = 'gameday-ops', repository = root) {
  const script = join(repository, 'scripts/package-plugins.py');
  assert.ok(existsSync(script), 'Reproducible packager must exist');
  const selections = (Array.isArray(plugin) ? plugin : [plugin]).flatMap(name => ['--plugin', name]);
  return spawnSync('python3', [script, ...selections, '--output', output], {encoding: 'utf8', cwd: repository});
}
function archiveFixture(zuluSource = './plugins/zulu') {
  const repository = mkdtempSync(join(tmpdir(), 'sports-release-'));
  mkdirSync(join(repository, 'scripts'));
  mkdirSync(join(repository, '.claude-plugin'));
  copyFileSync(join(root, 'scripts/package-plugins.py'), join(repository, 'scripts/package-plugins.py'));
  const plugins = [{name: 'alpha', source: './plugins/alpha'}, {name: 'zulu', source: zuluSource}];
  writeFileSync(join(repository, '.claude-plugin/marketplace.json'), JSON.stringify({plugins}));
  for (const plugin of plugins) {
    const source = join(repository, plugin.source);
    mkdirSync(join(source, '.claude-plugin'), {recursive: true});
    mkdirSync(join(source, '.codex-plugin'));
    mkdirSync(join(source, 'skills/example'), {recursive: true});
    const metadata = {name: plugin.name, version: '1.0.0', description: 'Release fixture'};
    writeFileSync(join(source, 'plugin.json'), JSON.stringify({$schema: 'https://agent-plugins.org/schemas/1.0.0/plugin.schema.json', ...metadata}));
    writeFileSync(join(source, '.claude-plugin/plugin.json'), JSON.stringify(metadata));
    writeFileSync(join(source, '.codex-plugin/plugin.json'), JSON.stringify({...metadata, skills: './skills/'}));
    writeFileSync(join(source, 'LICENSE'), 'Example package license\n');
    writeFileSync(join(source, 'skills/example/SKILL.md'), '---\nname: example\ndescription: Example workflow\n---\nUse it.\n');
  }
  return repository;
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
    assert.equal(manifest[0].sha256, createHash('sha256').update(readFileSync(zip)).digest('hex'));
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
for (const relativeOutput of ['plugins/zulu', 'plugins/zulu/skills/releases']) {
  test(`packager rejects archive output at ${relativeOutput} in an unselected plugin`, () => {
    const repository = archiveFixture(); const output = join(repository, relativeOutput);
    try {
      const before = existsSync(output) ? readdirSync(output).sort() : null;
      const result = run(output, 'alpha', repository);
      assert.equal(result.status, 2, result.stderr);
      assert.match(result.stderr, /outside.*plugin source/);
      assert.deepEqual(existsSync(output) ? readdirSync(output).sort() : null, before);
    } finally {rmSync(repository, {recursive: true, force: true});}
  });
}
test('packager rejects output equal to the selected plugin source', () => {
  const repository = archiveFixture(); const output = join(repository, 'plugins/zulu');
  try {
    const before = readdirSync(output).sort();
    const result = run(output, 'zulu', repository);
    assert.equal(result.status, 2, result.stderr);
    assert.match(result.stderr, /outside.*plugin source/);
    assert.deepEqual(readdirSync(output).sort(), before);
  } finally {rmSync(repository, {recursive: true, force: true});}
});
test('packager checks every source before writing the first selected archive', () => {
  const repository = archiveFixture(); const output = join(repository, 'plugins/zulu/skills/releases');
  try {
    const result = run(output, ['alpha', 'zulu'], repository);
    assert.equal(result.status, 2, result.stderr);
    assert.match(result.stderr, /outside.*plugin source/);
    assert.ok(!existsSync(output), 'Invalid output must be rejected before any directory or archive is created');
  } finally {rmSync(repository, {recursive: true, force: true});}
});
test('packager uses catalog source paths when rejecting archive output', () => {
  const repository = archiveFixture('./plugins/alternate-zulu');
  const output = join(repository, 'plugins/alternate-zulu/skills/releases');
  try {
    const result = run(output, 'alpha', repository);
    assert.equal(result.status, 2, result.stderr);
    assert.match(result.stderr, /outside.*plugin source/);
    assert.ok(!existsSync(output));
  } finally {rmSync(repository, {recursive: true, force: true});}
});
test('packager rejects a symlink alias into another plugin source', () => {
  const repository = archiveFixture(); const alias = join(repository, 'source-alias');
  const output = join(alias, 'skills/releases');
  try {
    symlinkSync(join(repository, 'plugins/zulu'), alias, 'dir');
    const result = run(output, 'alpha', repository);
    assert.equal(result.status, 2, result.stderr);
    assert.match(result.stderr, /outside.*plugin source/);
    assert.ok(!existsSync(output));
  } finally {rmSync(repository, {recursive: true, force: true});}
});
