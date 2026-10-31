/** Verify actual package files, not only a manifest's name and description. */
import { existsSync, readFileSync, readdirSync, realpathSync, statSync } from 'node:fs';
import { resolve, relative, isAbsolute, join } from 'node:path';
const SCHEMA = 'https://agent-plugins.org/schemas/1.0.0/plugin.schema.json';
const SEMVER = /^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)(?:-[0-9A-Za-z.-]+)?(?:\+[0-9A-Za-z.-]+)?$/;
const text = value => typeof value === 'string' && value.trim().length > 0;
function within(root, candidate) {
  const rel = relative(root, candidate);
  return !rel.startsWith('..') && !isAbsolute(rel);
}
export function checkPackage(packageRoot) {
  const errors = []; const root = resolve(packageRoot);
  if (!existsSync(root)) return ['Package directory does not exist'];
  const realRoot = realpathSync(root);
  function localPath(value, label, directory = false) {
    if (!text(value) || !value.startsWith('./') || !within(root, resolve(root, value))) { errors.push(`${label}: path must stay inside the package and begin ./`); return null; }
    const target = resolve(root, value);
    if (!existsSync(target)) { errors.push(`${label}: referenced path is missing: ${value}`); return null; }
    if (!within(realRoot, realpathSync(target))) { errors.push(`${label}: symlink escapes package`); return null; }
    if (directory ? !statSync(target).isDirectory() : !statSync(target).isFile()) { errors.push(`${label}: wrong component type`); return null; }
    return target;
  }
  const manifests = [];
  for (const filename of ['plugin.json', '.claude-plugin/plugin.json', '.codex-plugin/plugin.json']) {
    let data;
    try { data = JSON.parse(readFileSync(join(root, filename), 'utf8')); } catch { errors.push(`${filename}: missing or invalid JSON`); continue; }
    if (!data || Array.isArray(data) || typeof data !== 'object') { errors.push(`${filename}: manifest must be an object`); continue; }
    if (!text(data.name) || !text(data.description) || !SEMVER.test(data.version ?? '')) errors.push(`${filename}: valid name, description and semantic version required`);
    if (filename === 'plugin.json' && data.$schema !== SCHEMA) errors.push('plugin.json: portable schema declaration missing or incorrect');
    if (filename === '.codex-plugin/plugin.json') {
      localPath(data.skills ?? './skills/', 'skills', true);
      if (data.mcpServers !== undefined) localPath(data.mcpServers, 'mcpServers');
      const ui = data.interface ?? {};
      for (const key of ['composerIcon', 'logo']) if (ui[key] !== undefined) localPath(ui[key], 'interface.' + key);
      if (ui.screenshots !== undefined && !Array.isArray(ui.screenshots)) errors.push('interface.screenshots must be an array');
      else for (const image of ui.screenshots ?? []) localPath(image, 'interface.screenshots');
    }
    manifests.push(data);
  }
  if (new Set(manifests.map(m => m.name)).size > 1) errors.push('Manifest name identity mismatch');
  if (new Set(manifests.map(m => m.version)).size > 1) errors.push('Manifest version mismatch');
  const skills = join(root, 'skills'); const names = new Set(); let count = 0;
  if (existsSync(skills)) for (const entry of readdirSync(skills, {withFileTypes: true})) {
    if (!entry.isDirectory() || entry.name.startsWith('.')) continue;
    const filename = localPath('./skills/' + entry.name + '/SKILL.md', entry.name + ' skill');
    if (!filename) continue;
    const body = readFileSync(filename, 'utf8');
    const front = /^---\r?\n([\s\S]*?)\r?\n---(?:\r?\n|$)/.exec(body);
    const name = front?.[1].match(/^name:\s*([a-z0-9-]+)\s*$/m)?.[1];
    if (!name || !/^description:\s*\S/m.test(front?.[1] ?? '')) errors.push(`${entry.name}: skill frontmatter requires name and description`);
    else if (names.has(name)) errors.push(`${entry.name}: duplicate skill name`);
    else names.add(name);
    count++;
  }
  if (!count) errors.push('Package has no discoverable skills');
  if (existsSync(join(root, '.mcp.json'))) {
    try {
      const portable = JSON.parse(readFileSync(join(root, 'mcp.json'), 'utf8'));
      const legacy = JSON.parse(readFileSync(join(root, '.mcp.json'), 'utf8'));
      if (portable.$schema !== 'https://agent-plugins.org/schemas/1.0.0/mcp.schema.json') errors.push('mcp.json: portable schema declaration missing');
      if (JSON.stringify(Object.keys(portable.mcpServers ?? {}).sort()) !== JSON.stringify(Object.keys(legacy.mcpServers ?? {}).sort())) errors.push('Portable and legacy MCP server names differ');
      for (const [name, server] of Object.entries(legacy.mcpServers ?? {})) {
        const target = portable.mcpServers?.[name];
        if (!target || target.url !== server.url || target.type !== (server.type === 'http' ? 'streamable-http' : server.type)) errors.push(`MCP connection ${name} differs between package formats`);
      }
    } catch { errors.push('mcp.json: portable MCP configuration is missing or invalid'); }
  }
  return errors;
}
export function checkCatalog(root) {
  const errors = [];
  try {
    const claude = JSON.parse(readFileSync(join(root, '.claude-plugin/marketplace.json'), 'utf8'));
    const codex = JSON.parse(readFileSync(join(root, '.agents/plugins/marketplace.json'), 'utf8'));
    const names = claude.plugins.map(p => p.name);
    if (new Set(names).size !== names.length) errors.push('Duplicate Claude catalog identity');
    if (JSON.stringify([...names].sort()) !== JSON.stringify(codex.plugins.map(p => p.name).sort())) errors.push('Host catalogs disagree about plugin identities');
    for (const entry of claude.plugins) {
      const counterpart = codex.plugins.find(p => p.name === entry.name);
      if (!counterpart || counterpart.source?.source !== 'local' || counterpart.source.path !== entry.source) errors.push(`${entry.name}: host catalog paths differ`);
      if (!text(entry.source) || !entry.source.startsWith('./plugins/') || !within(resolve(root), resolve(root, entry.source))) errors.push(`${entry.name}: invalid catalog path`);
      for (const dependency of entry.dependencies ?? []) if (!names.includes(dependency)) errors.push(`${entry.name}: unknown dependency ${dependency}`);
    }
  } catch (error) { errors.push('Catalog cannot be read: ' + error.message); }
  return errors;
}
