/**
 * Shape check for a plugin's .mcp.json, matching what Claude Code loads:
 * a top-level "mcpServers" object, each server either remote (http/sse with
 * an https url) or local (stdio with a command). Tool lists, server info and
 * other extra keys are not part of the format; the server reports its own
 * tools at runtime.
 */

import { readdirSync, existsSync } from "node:fs";
import { join } from "node:path";

const REMOTE_TYPES = new Set(["http", "sse"]);
const SERVER_KEYS = new Set([
  "type", "url", "headers", "headersHelper", "oauth",
  "command", "args", "env", "cwd",
]);

/** Return a list of problems with a parsed .mcp.json; empty means valid. */
export function checkMcpConfig(config) {
  const errors = [];
  if (!config || typeof config !== "object" || Array.isArray(config)) {
    return ["must be a JSON object"];
  }
  for (const key of Object.keys(config)) {
    if (key !== "mcpServers") errors.push(`unexpected top-level key "${key}" (servers go under "mcpServers")`);
  }
  const servers = config.mcpServers;
  if (!servers || typeof servers !== "object" || Array.isArray(servers)) {
    errors.push('missing "mcpServers" object');
    return errors;
  }
  const names = Object.keys(servers);
  if (names.length === 0) errors.push('"mcpServers" is empty');
  for (const name of names) {
    const s = servers[name];
    if (!s || typeof s !== "object" || Array.isArray(s)) {
      errors.push(`${name}: must be an object`);
      continue;
    }
    for (const key of Object.keys(s)) {
      if (!SERVER_KEYS.has(key)) errors.push(`${name}: unknown key "${key}"`);
    }
    const type = s.type ?? (s.command ? "stdio" : undefined);
    if (REMOTE_TYPES.has(type)) {
      let url;
      try { url = new URL(s.url); } catch { url = null; }
      if (!url || url.protocol !== "https:") errors.push(`${name}: "${type}" server needs an https "url"`);
      if (s.command) errors.push(`${name}: a remote server takes no "command"`);
    } else if (type === "stdio") {
      if (typeof s.command !== "string" || !s.command) errors.push(`${name}: stdio server needs a "command"`);
      if (s.url) errors.push(`${name}: a stdio server takes no "url"`);
    } else {
      errors.push(`${name}: "type" must be http, sse or stdio`);
    }
  }
  return errors;
}

/** Every .mcp.json one level under plugins/ and external_plugins/, as repo-relative paths. */
export function findMcpConfigs(root) {
  const found = [];
  for (const top of ["plugins", "external_plugins"]) {
    const dir = join(root, top);
    if (!existsSync(dir)) continue;
    for (const entry of readdirSync(dir, { withFileTypes: true })) {
      if (!entry.isDirectory()) continue;
      const rel = join(top, entry.name, ".mcp.json");
      if (existsSync(join(root, rel))) found.push(rel);
    }
  }
  return found.sort();
}
