import { describe, it } from "node:test";
import assert from "node:assert/strict";
import { readFileSync, existsSync } from "node:fs";
import { join, dirname } from "node:path";
import { fileURLToPath } from "node:url";
import { checkMcpConfig, findMcpConfigs } from "../scripts/mcp-config.mjs";

const ROOT = join(dirname(fileURLToPath(import.meta.url)), "..");

/** Resolve plugin directory — handles both `path` and `source` keys. */
function pluginDir(plugin) {
  const raw = plugin.path ?? plugin.source;
  if (!raw) return null;
  return raw.startsWith("./") ? raw.slice(2) : raw;
}

describe("marketplace.json", () => {
  const marketplacePath = join(ROOT, ".claude-plugin", "marketplace.json");

  it("exists and is valid JSON", () => {
    assert.ok(existsSync(marketplacePath), "marketplace.json must exist");
    const data = JSON.parse(readFileSync(marketplacePath, "utf-8"));
    assert.ok(data.name && data.owner, "must have name and owner");
    assert.ok(Array.isArray(data.plugins), "must have plugins array");
  });

  it("all listed plugins with a local path have required files", () => {
    const data = JSON.parse(readFileSync(marketplacePath, "utf-8"));
    const allPlugins = data.plugins;

    for (const plugin of allPlugins) {
      const dir = pluginDir(plugin);
      if (!dir) continue; // skip plugins with no local path (coming-soon, etc.)

      const absDir = join(ROOT, dir);
      const metaPath = join(absDir, ".claude-plugin", "plugin.json");
      const readmePath = join(absDir, "README.md");

      assert.ok(
        existsSync(metaPath),
        `${plugin.name}: missing .claude-plugin/plugin.json`
      );
      assert.ok(
        existsSync(readmePath),
        `${plugin.name}: missing README.md`
      );

      // Validate plugin.json structure
      const meta = JSON.parse(readFileSync(metaPath, "utf-8"));
      assert.ok(meta.name, `${plugin.name}: plugin.json missing "name"`);
      assert.ok(
        meta.description,
        `${plugin.name}: plugin.json missing "description"`
      );
    }
  });

  it("all .mcp.json files are valid JSON", () => {
    const data = JSON.parse(readFileSync(marketplacePath, "utf-8"));
    const allPlugins = data.plugins;

    for (const plugin of allPlugins) {
      const dir = pluginDir(plugin);
      if (!dir) continue;

      const mcpPath = join(ROOT, dir, ".mcp.json");
      if (existsSync(mcpPath)) {
        assert.doesNotThrow(
          () => JSON.parse(readFileSync(mcpPath, "utf-8")),
          `${plugin.name}: .mcp.json is not valid JSON`
        );
      }
    }
  });
});

describe(".mcp.json shape", () => {
  const remote = (server) => ({ mcpServers: { bsi: server } });

  it("accepts a remote server and a local one", () => {
    assert.deepEqual(checkMcpConfig(remote({ type: "http", url: "https://example.com/mcp" })), []);
    assert.deepEqual(checkMcpConfig(remote({ type: "sse", url: "https://example.com/sse", headers: { A: "b" } })), []);
    assert.deepEqual(checkMcpConfig(remote({ command: "npx", args: ["-y", "pkg"] })), []);
  });

  it("rejects servers at the top level instead of under mcpServers", () => {
    const errors = checkMcpConfig({ "bsi-mcp": { type: "http", url: "https://example.com/mcp" } });
    assert.ok(errors.some((e) => e.includes('"bsi-mcp"')), errors.join("; "));
    assert.ok(errors.some((e) => e.includes('missing "mcpServers"')), errors.join("; "));
  });

  it("rejects tool lists and other keys the format doesn't have", () => {
    const errors = checkMcpConfig(remote({
      type: "http", url: "https://example.com/mcp", tools: [], serverInfo: {}, remotes: [],
    }));
    for (const key of ["tools", "serverInfo", "remotes"]) {
      assert.ok(errors.includes(`bsi: unknown key "${key}"`), errors.join("; "));
    }
  });

  it("rejects a remote server without an https url", () => {
    assert.ok(checkMcpConfig(remote({ type: "http", url: "http://example.com/mcp" })).length);
    assert.ok(checkMcpConfig(remote({ type: "http" })).length);
    assert.ok(checkMcpConfig(remote({ type: "websocket", url: "https://example.com" })).length);
    assert.ok(checkMcpConfig({ mcpServers: {} }).length);
  });

  it("every .mcp.json in the repo passes, listed in the marketplace or not", () => {
    const paths = findMcpConfigs(ROOT);
    assert.ok(paths.length > 0, "expected at least one .mcp.json");
    for (const rel of paths) {
      const errors = checkMcpConfig(JSON.parse(readFileSync(join(ROOT, rel), "utf-8")));
      assert.deepEqual(errors, [], `${rel}: ${errors.join("; ")}`);
    }
  });

  it("every Blaze config points at the live sabermetrics server", () => {
    for (const rel of findMcpConfigs(ROOT)) {
      const { mcpServers } = JSON.parse(readFileSync(join(ROOT, rel), "utf-8"));
      for (const [name, s] of Object.entries(mcpServers)) {
        const host = s.url ? new URL(s.url).hostname : "";
        if (host === "blazesportsintel.com" || host.endsWith(".blazesportsintel.com")) {
          assert.equal(s.url, "https://sabermetrics.blazesportsintel.com/mcp", `${rel} ${name}`);
        }
      }
    }
  });
});
