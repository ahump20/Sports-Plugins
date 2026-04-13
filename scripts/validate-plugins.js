#!/usr/bin/env node

/**
 * Plugin validation script.
 *
 * Checks that every plugin registered in the marketplace manifest has the
 * required file structure: plugin.json, README.md, and at least one skill.
 *
 * Referenced by .codex/environments/environment.toml.
 */

import { readFileSync, existsSync, readdirSync, statSync } from 'node:fs';
import { join, resolve } from 'node:path';

const ROOT = resolve(import.meta.dirname, '..');
const MARKETPLACE_PATH = join(ROOT, '.claude-plugin', 'marketplace.json');

let exitCode = 0;

function fail(msg) {
  console.error(`  ✗ ${msg}`);
  exitCode = 1;
}

function pass(msg) {
  console.log(`  ✓ ${msg}`);
}

// ---------------------------------------------------------------------------
// Load marketplace manifest
// ---------------------------------------------------------------------------

if (!existsSync(MARKETPLACE_PATH)) {
  console.error(`Marketplace manifest not found: ${MARKETPLACE_PATH}`);
  process.exit(1);
}

const marketplace = JSON.parse(readFileSync(MARKETPLACE_PATH, 'utf-8'));
const plugins = marketplace.plugins;

if (!Array.isArray(plugins) || plugins.length === 0) {
  console.error('Marketplace manifest contains no plugins.');
  process.exit(1);
}

console.log(`\nValidating ${plugins.length} plugin(s)...\n`);

// ---------------------------------------------------------------------------
// Validate each plugin
// ---------------------------------------------------------------------------

for (const entry of plugins) {
  const name = entry.name;
  const pluginDir = resolve(ROOT, entry.source);
  console.log(`Plugin: ${name}`);

  // 1. Plugin directory exists
  if (!existsSync(pluginDir) || !statSync(pluginDir).isDirectory()) {
    fail(`Directory not found: ${pluginDir}`);
    continue;
  }
  pass('Directory exists');

  // 2. plugin.json exists and is valid JSON
  const pluginJson = join(pluginDir, '.claude-plugin', 'plugin.json');
  if (!existsSync(pluginJson)) {
    fail('Missing .claude-plugin/plugin.json');
  } else {
    try {
      const manifest = JSON.parse(readFileSync(pluginJson, 'utf-8'));
      if (!manifest.name || !manifest.version) {
        fail('plugin.json missing required fields (name, version)');
      } else {
        pass(`plugin.json valid (${manifest.name} v${manifest.version})`);
      }
    } catch {
      fail('plugin.json is not valid JSON');
    }
  }

  // 3. README.md exists
  const readme = join(pluginDir, 'README.md');
  if (!existsSync(readme)) {
    fail('Missing README.md');
  } else {
    const content = readFileSync(readme, 'utf-8');
    if (content.length < 100) {
      fail('README.md is too short (< 100 chars) — needs real content');
    } else {
      pass('README.md present and has content');
    }
  }

  // 4. At least one skill
  const skillsDir = join(pluginDir, 'skills');
  if (!existsSync(skillsDir) || !statSync(skillsDir).isDirectory()) {
    fail('Missing skills/ directory');
  } else {
    const skills = readdirSync(skillsDir).filter(
      (d) => statSync(join(skillsDir, d)).isDirectory(),
    );
    if (skills.length === 0) {
      fail('No skills found in skills/ directory');
    } else {
      // Check each skill has a SKILL.md
      for (const skill of skills) {
        const skillMd = join(skillsDir, skill, 'SKILL.md');
        if (!existsSync(skillMd)) {
          fail(`Skill "${skill}" missing SKILL.md`);
        } else {
          const content = readFileSync(skillMd, 'utf-8');
          if (content.length < 200) {
            fail(`Skill "${skill}" SKILL.md is too short — needs actionable content`);
          } else {
            pass(`Skill "${skill}" — SKILL.md valid (${content.length} chars)`);
          }
        }
      }
    }
  }

  // 5. src/ directory with TypeScript entry point
  const srcDir = join(pluginDir, 'src');
  if (!existsSync(srcDir) || !statSync(srcDir).isDirectory()) {
    fail('Missing src/ directory');
  } else {
    const indexTs = join(srcDir, 'index.ts');
    if (!existsSync(indexTs)) {
      fail('Missing src/index.ts entry point');
    } else {
      pass('src/index.ts present');
    }
  }

  console.log('');
}

// ---------------------------------------------------------------------------
// Summary
// ---------------------------------------------------------------------------

if (exitCode === 0) {
  console.log('All plugins validated successfully ✓\n');
} else {
  console.error('Validation failed — see errors above.\n');
}

process.exit(exitCode);
