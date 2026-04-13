#!/usr/bin/env node

/**
 * Validate that all plugins in the marketplace have the required structure.
 * Usage: node scripts/validate-plugins.mjs
 */

import { readFileSync, existsSync } from "node:fs";
import { join } from "node:path";

const ROOT = new URL("..", import.meta.url).pathname;

function fail(msg) {
  console.error(`  ✗ ${msg}`);
  return false;
}

function pass(msg) {
  console.log(`  ✓ ${msg}`);
  return true;
}

function validatePlugin(pluginPath) {
  const abs = join(ROOT, pluginPath);
  let ok = true;

  // Required: .claude-plugin/plugin.json
  const metaPath = join(abs, ".claude-plugin", "plugin.json");
  if (!existsSync(metaPath)) {
    ok = fail(`${pluginPath}: missing .claude-plugin/plugin.json`) && ok;
  } else {
    try {
      const meta = JSON.parse(readFileSync(metaPath, "utf-8"));
      if (!meta.name) ok = fail(`${pluginPath}: plugin.json missing "name"`) && ok;
      if (!meta.description) ok = fail(`${pluginPath}: plugin.json missing "description"`) && ok;
      pass(`${pluginPath}: plugin.json valid`);
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

  // Optional: .mcp.json — validate JSON if present
  const mcpPath = join(abs, ".mcp.json");
  if (existsSync(mcpPath)) {
    try {
      JSON.parse(readFileSync(mcpPath, "utf-8"));
      pass(`${pluginPath}: .mcp.json valid`);
    } catch (e) {
      ok = fail(`${pluginPath}: .mcp.json is not valid JSON — ${e.message}`) && ok;
    }
  }

  return ok;
}

// Load marketplace
const marketplacePath = join(ROOT, ".claude-plugin", "marketplace.json");
if (!existsSync(marketplacePath)) {
  console.error("✗ Missing .claude-plugin/marketplace.json");
  process.exit(1);
}

const marketplace = JSON.parse(readFileSync(marketplacePath, "utf-8"));
let allOk = true;

console.log("Validating plugins...\n");

for (const plugin of marketplace.plugins ?? []) {
  console.log(`Plugin: ${plugin.name}`);
  if (!validatePlugin(plugin.path)) allOk = false;
  console.log();
}

for (const plugin of marketplace.external_plugins ?? []) {
  console.log(`External: ${plugin.name}`);
  if (!validatePlugin(plugin.path)) allOk = false;
  console.log();
}

if (allOk) {
  console.log("All plugins valid ✓");
} else {
  console.error("\nSome plugins have issues.");
  process.exit(1);
}
