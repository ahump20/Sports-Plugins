import { test } from 'node:test';
import assert from 'node:assert/strict';
import { existsSync, readFileSync, mkdtempSync, mkdirSync, writeFileSync, rmSync, symlinkSync } from 'node:fs';
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
  writeFileSync(join(dir, 'LICENSE'), 'Example package license\n');
  return dir;
}
test('rejects packages without a LICENSE file', async () => {
  const check = await checker(); const dir = fixture();
  try {
    rmSync(join(dir, 'LICENSE'));
    assert.ok(check(dir).some(e => /LICENSE.*missing/.test(e)));
  } finally { rmSync(dir, {recursive: true, force: true}); }
});
test('rejects a directory in place of the LICENSE file', async () => {
  const check = await checker(); const dir = fixture();
  try {
    rmSync(join(dir, 'LICENSE'));
    mkdirSync(join(dir, 'LICENSE'));
    assert.ok(check(dir).some(e => /LICENSE.*type/.test(e)));
  } finally { rmSync(dir, {recursive: true, force: true}); }
});
test('rejects a LICENSE symlink outside the package', async () => {
  const check = await checker(); const dir = fixture();
  const outside = mkdtempSync(join(tmpdir(), 'sports-license-'));
  try {
    rmSync(join(dir, 'LICENSE'));
    writeFileSync(join(outside, 'LICENSE'), 'External license\n');
    symlinkSync(join(outside, 'LICENSE'), join(dir, 'LICENSE'));
    assert.ok(check(dir).some(e => /LICENSE.*symlink.*escape/.test(e)));
  } finally {
    rmSync(dir, {recursive: true, force: true});
    rmSync(outside, {recursive: true, force: true});
  }
});
test('rejects a LICENSE symlink even when its target is inside the package', async () => {
  const check = await checker(); const dir = fixture();
  try {
    writeFileSync(join(dir, 'license-text.txt'), 'Example package license\n');
    rmSync(join(dir, 'LICENSE'));
    symlinkSync('license-text.txt', join(dir, 'LICENSE'));
    assert.ok(check(dir).some(e => /LICENSE.*symlink/i.test(e)));
  } finally { rmSync(dir, {recursive: true, force: true}); }
});
test('rejects a skill frontmatter name that differs from its directory', async () => {
  const check = await checker(); const dir = fixture();
  try {
    writeFileSync(join(dir, 'skills/example/SKILL.md'), '---\nname: renamed\ndescription: Example workflow\n---\nUse it.\n');
    assert.ok(check(dir).some(e => /example.*name.*match.*directory/.test(e)));
  } finally { rmSync(dir, {recursive: true, force: true}); }
});
test('reports the skill directory mismatch before a duplicate name', async () => {
  const check = await checker(); const dir = fixture();
  try {
    mkdirSync(join(dir, 'skills/renamed'));
    writeFileSync(join(dir, 'skills/renamed/SKILL.md'), '---\nname: example\ndescription: Another workflow\n---\nUse it.\n');
    const errors = check(dir);
    assert.ok(errors.some(e => /renamed.*name.*match.*directory/.test(e)), errors.join('; '));
    assert.ok(!errors.some(e => /duplicate skill name/.test(e)), errors.join('; '));
  } finally { rmSync(dir, {recursive: true, force: true}); }
});
const mcpSchema = 'https://agent-plugins.org/schemas/1.0.0/mcp.schema.json';
const portableMcp = mcpServers => ({$schema: mcpSchema, mcpServers});
const remoteServer = {type: 'streamable-http', url: 'https://example.test/mcp'};
const invalidPortableMcp = [
  ['invalid JSON', '{', /invalid/],
  ['null configuration', 'null', /object/],
  ['array configuration', [], /object/],
  ['missing schema', {mcpServers: {}}, /schema/],
  ['incorrect schema', {$schema: 'https://example.test/schema', mcpServers: {}}, /schema/],
  ['unexpected top-level key', {...portableMcp({}), tools: []}, /unexpected.*tools/],
  ['missing servers', {$schema: mcpSchema}, /mcpServers.*object/],
  ['null servers', portableMcp(null), /mcpServers.*object/],
  ['array servers', portableMcp([]), /mcpServers.*object/],
  ['null server', portableMcp({example: null}), /example.*object/],
  ['array server', portableMcp({example: []}), /example.*object/],
  ['implicit stdio transport', portableMcp({example: {command: 'node'}}), /example.*type/],
  ['legacy http transport', portableMcp({example: {type: 'http', url: 'https://example.test/mcp'}}), /example.*type/],
  ['missing stdio command', portableMcp({example: {type: 'stdio'}}), /example.*command/],
  ['empty stdio command', portableMcp({example: {type: 'stdio', command: ''}}), /example.*command/],
  ['non-string stdio command', portableMcp({example: {type: 'stdio', command: 1}}), /example.*command/],
  ['non-array args', portableMcp({example: {type: 'stdio', command: 'node', args: '--help'}}), /example.*args/],
  ['non-string argument', portableMcp({example: {type: 'stdio', command: 'node', args: [1]}}), /example.*args/],
  ['array env', portableMcp({example: {type: 'stdio', command: 'node', env: []}}), /example.*env/],
  ['non-string env value', portableMcp({example: {type: 'stdio', command: 'node', env: {PORT: 80}}}), /example.*env/],
  ['reserved root env', portableMcp({example: {type: 'stdio', command: 'node', env: {PLUGIN_ROOT: './'}}}), /example.*PLUGIN_ROOT/],
  ['reserved data env', portableMcp({example: {type: 'stdio', command: 'node', env: {PLUGIN_DATA: './'}}}), /example.*PLUGIN_DATA/],
  ['absolute cwd', portableMcp({example: {type: 'stdio', command: 'node', cwd: '/tmp'}}), /example.*cwd/],
  ['non-string cwd', portableMcp({example: {type: 'stdio', command: 'node', cwd: 1}}), /example.*cwd/],
  ['relative cwd escape', portableMcp({example: {type: 'stdio', command: 'node', cwd: './../../outside'}}), /example.*cwd.*(?:escape|inside|within)/],
  ['PLUGIN_ROOT cwd escape', portableMcp({example: {type: 'stdio', command: 'node', cwd: '${PLUGIN_ROOT}/../outside'}}), /example.*cwd.*(?:escape|inside|within)/],
  ['remote field on stdio', portableMcp({example: {type: 'stdio', command: 'node', url: 'https://example.test'}}), /example.*url/],
  ['missing remote url', portableMcp({example: {type: 'streamable-http'}}), /example.*url/],
  ['empty remote url', portableMcp({example: {...remoteServer, url: ''}}), /example.*url/],
  ['non-string remote url', portableMcp({example: {...remoteServer, url: 1}}), /example.*url/],
  ['array headers', portableMcp({example: {...remoteServer, headers: []}}), /example.*headers/],
  ['non-string header value', portableMcp({example: {...remoteServer, headers: {Authorization: 1}}}), /example.*headers/],
  ['stdio field on remote', portableMcp({example: {...remoteServer, command: 'node'}}), /example.*command/],
];
for (const [label, configuration, expectedError] of invalidPortableMcp) {
  test(`rejects portable MCP ${label} without a legacy configuration`, async () => {
    const check = await checker(); const dir = fixture();
    try {
      writeFileSync(join(dir, 'mcp.json'), typeof configuration === 'string' ? configuration : JSON.stringify(configuration));
      const errors = check(dir);
      assert.ok(errors.some(e => /mcp\.json/.test(e) && expectedError.test(e)), errors.join('; '));
    } finally { rmSync(dir, {recursive: true, force: true}); }
  });
}
function setStdioCwd(dir, cwd) {
  writeFileSync(join(dir, 'mcp.json'), JSON.stringify(portableMcp({example: {type: 'stdio', command: 'node', cwd}})));
}
for (const [label, cwd, missingTarget] of [
  ['relative link', './outside-link', false],
  ['PLUGIN_ROOT link', '${PLUGIN_ROOT}/outside-link', false],
  ['relative link with missing descendants', './outside-link/missing/run', false],
  ['PLUGIN_ROOT link with missing descendants', '${PLUGIN_ROOT}/outside-link/missing/run', false],
  ['relative link followed by parent traversal', './outside-link/..', false],
  ['PLUGIN_ROOT link followed by parent traversal', '${PLUGIN_ROOT}/outside-link/..', false],
  ['relative dangling link', './outside-link', true],
  ['PLUGIN_ROOT dangling link', '${PLUGIN_ROOT}/outside-link', true],
]) {
  test(`rejects portable MCP cwd escape through a ${label}`, async () => {
    const check = await checker(); const dir = fixture();
    const outside = mkdtempSync(join(tmpdir(), 'sports-cwd-outside-'));
    try {
      if (!missingTarget) mkdirSync(join(outside, 'target'));
      symlinkSync(join(outside, 'target'), join(dir, 'outside-link'), 'dir');
      setStdioCwd(dir, cwd);
      const errors = check(dir);
      assert.ok(errors.some(e => /mcp\.json.*example.*cwd.*(?:escape|inside|within)/.test(e)), errors.join('; '));
    } finally {
      rmSync(dir, {recursive: true, force: true});
      rmSync(outside, {recursive: true, force: true});
    }
  });
}
test('accepts existing and nonexistent portable MCP cwd paths inside the resolved package root', async () => {
  const check = await checker(); const dir = fixture();
  try {
    mkdirSync(join(dir, 'runtime'));
    mkdirSync(join(dir, '..cache'));
    symlinkSync(join(dir, 'runtime'), join(dir, 'runtime-link'), 'dir');
    symlinkSync(join(dir, 'planned'), join(dir, 'planned-link'), 'dir');
    for (const cwd of [
      './', '${PLUGIN_ROOT}', './skills', '${PLUGIN_ROOT}/skills',
      './missing/child', '${PLUGIN_ROOT}/missing/child',
      './missing/../skills', '${PLUGIN_ROOT}/missing/../skills',
      './runtime-link', '${PLUGIN_ROOT}/runtime-link',
      './runtime-link/missing/child', '${PLUGIN_ROOT}/runtime-link/missing/child',
      './planned-link/child', '${PLUGIN_ROOT}/planned-link/child',
      './..cache', '${PLUGIN_ROOT}/..cache',
      '${PLUGIN_DATA}', '${PLUGIN_DATA}/cache',
    ]) {
      setStdioCwd(dir, cwd);
      assert.deepEqual(check(dir), [], cwd);
    }
  } finally { rmSync(dir, {recursive: true, force: true}); }
});
test('uses the real package root when checking cwd through a package directory alias', async () => {
  const check = await checker(); const dir = fixture();
  const aliases = mkdtempSync(join(tmpdir(), 'sports-cwd-alias-'));
  try {
    const alias = join(aliases, 'package');
    symlinkSync(dir, alias, 'dir');
    for (const cwd of ['./skills', '${PLUGIN_ROOT}/skills', './missing/child', '${PLUGIN_ROOT}/missing/child']) {
      setStdioCwd(dir, cwd);
      assert.deepEqual(check(alias), [], cwd);
    }
  } finally {
    rmSync(aliases, {recursive: true, force: true});
    rmSync(dir, {recursive: true, force: true});
  }
});
test('accepts portable MCP transports and optional fields without a legacy configuration', async () => {
  const check = await checker(); const dir = fixture();
  try {
    const configurations = [
      {},
      {local: {type: 'stdio', command: 'node', args: ['./server.mjs'], env: {MODE: 'release'}, cwd: './scripts'}},
      {local: {type: 'stdio', command: 'node', cwd: '${PLUGIN_ROOT}/scripts'}},
      {local: {type: 'stdio', command: 'node', cwd: '${PLUGIN_DATA}'}},
      {remote: {...remoteServer, headers: {Authorization: 'Bearer ${TOKEN}'}}},
      {remote: {type: 'sse', url: 'https://example.test/sse', headers: {Accept: 'text/event-stream'}}},
    ];
    for (const servers of configurations) {
      writeFileSync(join(dir, 'mcp.json'), JSON.stringify(portableMcp(servers)));
      assert.deepEqual(check(dir), [], JSON.stringify(servers));
    }
  } finally { rmSync(dir, {recursive: true, force: true}); }
});
test('rejects a legacy MCP package missing its portable companion', async () => {
  const check = await checker(); const dir = fixture();
  try {
    writeFileSync(join(dir, '.mcp.json'), JSON.stringify({mcpServers: {example: {type: 'http', url: 'https://example.test/mcp'}}}));
    assert.ok(check(dir).some(e => /mcp\.json.*missing/.test(e)));
  } finally { rmSync(dir, {recursive: true, force: true}); }
});
test('compares MCP server names and connections when both formats exist', async () => {
  const check = await checker(); const dir = fixture();
  try {
    writeFileSync(join(dir, 'mcp.json'), JSON.stringify(portableMcp({example: remoteServer})));
    const legacyPath = join(dir, '.mcp.json');
    writeFileSync(legacyPath, JSON.stringify({mcpServers: {example: {...remoteServer, type: 'http'}}}));
    assert.deepEqual(check(dir), []);
    writeFileSync(legacyPath, JSON.stringify({mcpServers: {different: {...remoteServer, type: 'http'}}}));
    assert.ok(check(dir).some(e => /server names differ/.test(e)));
    writeFileSync(legacyPath, JSON.stringify({mcpServers: {example: {type: 'http', url: 'https://other.test/mcp'}}}));
    assert.ok(check(dir).some(e => /connection example differs/.test(e)));
    writeFileSync(legacyPath, JSON.stringify({mcpServers: {example: {...remoteServer, type: 'sse'}}}));
    assert.ok(check(dir).some(e => /connection example differs/.test(e)));
  } finally { rmSync(dir, {recursive: true, force: true}); }
});
const stdioServer = {type: 'stdio', command: 'node', args: ['./server.mjs', '--port', '3000'], cwd: './runtime', env: {MODE: 'release', PORT: '3000'}};
for (const [field, legacyServer] of [
  ['command', {...stdioServer, command: 'python3'}],
  ['args', {...stdioServer, args: ['--port', './server.mjs', '3000']}],
  ['cwd', {...stdioServer, cwd: './other'}],
  ['env', {...stdioServer, env: {MODE: 'release', PORT: '4000'}}],
]) {
  test(`rejects differing stdio ${field} between portable and legacy MCP configurations`, async () => {
    const check = await checker(); const dir = fixture();
    try {
      writeFileSync(join(dir, 'mcp.json'), JSON.stringify(portableMcp({example: stdioServer})));
      writeFileSync(join(dir, '.mcp.json'), JSON.stringify({mcpServers: {example: legacyServer}}));
      assert.ok(check(dir).some(e => /MCP connection example differs/.test(e)));
    } finally { rmSync(dir, {recursive: true, force: true}); }
  });
}
test('accepts matching stdio launches with environment keys in a different order', async () => {
  const check = await checker(); const dir = fixture();
  try {
    writeFileSync(join(dir, 'mcp.json'), JSON.stringify(portableMcp({example: stdioServer})));
    writeFileSync(join(dir, '.mcp.json'), JSON.stringify({mcpServers: {example: {...stdioServer, env: {PORT: '3000', MODE: 'release'}}}}));
    assert.deepEqual(check(dir), []);
  } finally { rmSync(dir, {recursive: true, force: true}); }
});
test('accepts a matching legacy stdio launch with an implicit transport type', async () => {
  const check = await checker(); const dir = fixture();
  try {
    const legacyServer = {...stdioServer};
    delete legacyServer.type;
    writeFileSync(join(dir, 'mcp.json'), JSON.stringify(portableMcp({example: stdioServer})));
    writeFileSync(join(dir, '.mcp.json'), JSON.stringify({mcpServers: {example: legacyServer}}));
    assert.deepEqual(check(dir), []);
  } finally { rmSync(dir, {recursive: true, force: true}); }
});
test('accepts equivalent default stdio fields and resolved package cwd paths', async () => {
  const check = await checker(); const dir = fixture();
  try {
    mkdirSync(join(dir, 'runtime'));
    symlinkSync('runtime', join(dir, 'runtime-link'), 'dir');
    for (const [portableServer, legacyServer] of [
      [{type: 'stdio', command: 'node'}, {type: 'stdio', command: 'node', args: [], env: {}, cwd: '${PLUGIN_ROOT}'}],
      [{...stdioServer, cwd: './missing/../skills'}, {...stdioServer, cwd: '${PLUGIN_ROOT}/skills'}],
      [{...stdioServer, cwd: './runtime-link'}, {...stdioServer, cwd: '${PLUGIN_ROOT}/runtime'}],
    ]) {
      writeFileSync(join(dir, 'mcp.json'), JSON.stringify(portableMcp({example: portableServer})));
      writeFileSync(join(dir, '.mcp.json'), JSON.stringify({mcpServers: {example: legacyServer}}));
      assert.deepEqual(check(dir), [], JSON.stringify([portableServer, legacyServer]));
    }
  } finally { rmSync(dir, {recursive: true, force: true}); }
});
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
