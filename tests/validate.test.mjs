import { describe, it } from "node:test";
import assert from "node:assert/strict";
import { readFileSync, existsSync } from "node:fs";
import { join, dirname } from "node:path";
import { fileURLToPath } from "node:url";

const ROOT = join(dirname(fileURLToPath(import.meta.url)), "..");

describe("marketplace.json", () => {
  const marketplacePath = join(ROOT, ".claude-plugin", "marketplace.json");

  it("exists and is valid JSON", () => {
    assert.ok(existsSync(marketplacePath), "marketplace.json must exist");
    const data = JSON.parse(readFileSync(marketplacePath, "utf-8"));
    assert.ok(data.marketplace, "must have marketplace key");
    assert.ok(data.plugins, "must have plugins array");
    assert.ok(data.external_plugins, "must have external_plugins array");
  });

  it("all listed plugins have required files", () => {
    const data = JSON.parse(readFileSync(marketplacePath, "utf-8"));
    const allPlugins = [...data.plugins, ...data.external_plugins];

    for (const plugin of allPlugins) {
      const pluginDir = join(ROOT, plugin.path);
      const metaPath = join(pluginDir, ".claude-plugin", "plugin.json");
      const readmePath = join(pluginDir, "README.md");

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
    const allPlugins = [...data.plugins, ...data.external_plugins];

    for (const plugin of allPlugins) {
      const mcpPath = join(ROOT, plugin.path, ".mcp.json");
      if (existsSync(mcpPath)) {
        assert.doesNotThrow(
          () => JSON.parse(readFileSync(mcpPath, "utf-8")),
          `${plugin.name}: .mcp.json is not valid JSON`
        );
      }
    }
  });
});
