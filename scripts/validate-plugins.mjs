#!/usr/bin/env node

/**
 * Validate that all plugins in the marketplace have the required structure.
 * Usage: node scripts/validate-plugins.mjs
 */

import { readFileSync, existsSync } from "node:fs";
import { join, dirname } from "node:path";
import { fileURLToPath } from "node:url";
import { checkMcpConfig, findMcpConfigs } from "./mcp-config.mjs";

import { checkPackage, checkCatalog } from "./package-contract.mjs";

const ROOT = join(dirname(fileURLToPath(import.meta.url)), "..");

function fail(msg) {
  console.error(`  ✗ ${msg}`);
  return false;
}

function pass(msg) {
  console.log(`  ✓ ${msg}`);
  return true;
}

/** Resolve plugin directory — handles both `path` and `source` keys. */
function resolvePluginPath(plugin) {
  const raw = plugin.path ?? plugin.source;
  if (!raw) return null;
  return raw.startsWith("./") ? raw.slice(2) : raw;
}

function validatePlugin(pluginPath) {
  const abs = join(ROOT, pluginPath);
  let ok = true;

  if (pluginPath.startsWith("plugins/")) {
    const problems = checkPackage(abs);
    for (const problem of problems) { fail(`${pluginPath}: ${problem}`); ok = false; }
    if (problems.length === 0) pass(`${pluginPath}: portable, Claude and Codex components agree`);
  }

  // Required: .claude-plugin/plugin.json
  const metaPath = join(abs, ".claude-plugin", "plugin.json");
  if (!existsSync(metaPath)) {
    ok = fail(`${pluginPath}: missing .claude-plugin/plugin.json`) && ok;
  } else {
    try {
      const meta = JSON.parse(readFileSync(metaPath, "utf-8"));
      if (!meta.name) ok = fail(`${pluginPath}: plugin.json missing "name"`) && ok;
      if (!meta.description) ok = fail(`${pluginPath}: plugin.json missing "description"`) && ok;
      if (meta.name && meta.description) pass(`${pluginPath}: plugin.json valid`);
    } catch (e) {
      ok = fail(`${pluginPath}: plugin.json is not valid JSON — ${e.message}`) && ok;
    }
  }

  // Required: README.md
  const readmePath = join(abs, "README.md");
  if (!existsSync(readmePath)) {
    ok = fail(`${pluginPath}: missing README.md`) && ok;
  } else {
    pass(`${pluginPath}: README.md present`);
  }

  // Optional: .mcp.json
  const mcpPath = join(pluginPath, ".mcp.json");
  if (existsSync(join(ROOT, mcpPath))) ok = validateMcpConfig(mcpPath) && ok;

  return ok;
}

function validateMcpConfig(relPath) {
  let config;
  try {
    config = JSON.parse(readFileSync(join(ROOT, relPath), "utf-8"));
  } catch (e) {
    return fail(`${relPath} is not valid JSON — ${e.message}`);
  }
  const errors = checkMcpConfig(config);
  if (errors.length === 0) return pass(`${relPath} valid`);
  for (const err of errors) fail(`${relPath}: ${err}`);
  return false;
}

// Load marketplace
const marketplacePath = join(ROOT, ".claude-plugin", "marketplace.json");
if (!existsSync(marketplacePath)) {
  console.error("✗ Missing .claude-plugin/marketplace.json");
  process.exit(1);
}

const marketplace = JSON.parse(readFileSync(marketplacePath, "utf-8"));
let allOk = true;
for (const problem of checkCatalog(ROOT)) { fail(problem); allOk = false; }

console.log("Validating plugins...\n");

for (const plugin of marketplace.plugins ?? []) {
  const pPath = resolvePluginPath(plugin);
  if (!pPath) {
    console.log(`Plugin: ${plugin.name} (no local path — skipped)`);
    console.log();
    continue;
  }
  console.log(`Plugin: ${plugin.name}`);
  if (!validatePlugin(pPath)) allOk = false;
  console.log();
}

for (const plugin of marketplace.external_plugins ?? []) {
  const pPath = resolvePluginPath(plugin);
  if (!pPath) {
    console.log(`External: ${plugin.name} (no local path — skipped)`);
    console.log();
    continue;
  }
  console.log(`External: ${plugin.name}`);
  if (!validatePlugin(pPath)) allOk = false;
  console.log();
}

// Plugins not listed in the marketplace still ship their .mcp.json
const listed = new Set(
  [...(marketplace.plugins ?? []), ...(marketplace.external_plugins ?? [])]
    .map(resolvePluginPath)
    .filter(Boolean)
    .map((p) => join(p, ".mcp.json")),
);
const unlisted = findMcpConfigs(ROOT).filter((p) => !listed.has(p));
if (unlisted.length) {
  console.log("Unlisted MCP configs");
  for (const p of unlisted) if (!validateMcpConfig(p)) allOk = false;
  console.log();
}

if (allOk) {
  console.log("All plugins valid ✓");
} else {
  console.error("\nSome plugins have issues.");
  process.exit(1);
}
