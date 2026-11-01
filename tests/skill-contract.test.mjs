import {test} from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
const read = path => readFileSync(new URL('../' + path, import.meta.url), 'utf8');
test('Texas workflow distinguishes collection, inference, and unsupported quantitative models', () => {
  const skill = read('plugins/texas-longhorns-intel/skills/texas-longhorns-baseball-intelligence/SKILL.md');
  assert.match(skill, /first SEC baseball season was 2025/);
  assert.match(skill, /Do not manufacture HAV-F/);
  assert.match(skill, /retrieval time is not/i);
  assert.doesNotMatch(skill, /Score each dimension 1-5|Overpaid.*reassess or divest/);
  assert.ok(skill.split(/\s+/).length < 750, 'Trigger workflow should not preload an entire product specification');
});
test('conference workflow does not derive schedule strength from standings alone', () => {
  const skill = read('plugins/cbb-sabermetrics/skills/conference-strength/SKILL.md');
  assert.match(skill, /Standings alone cannot establish strength of schedule/);
  assert.match(skill, /do not construct.*power index/i);
});
test('active command and agent routing no longer requires nonexistent game-day plugins', () => {
  const agent = read('plugins/cbb-sabermetrics/agents/college-baseball-intelligence.md');
  const command = read('plugins/texas-longhorns-intel/commands/texas-scout.md');
  assert.doesNotMatch(agent, /bsi-gameday-ops/);
  assert.match(agent, /gameday-packet/);
  assert.doesNotMatch(command, /HAV-F scoring applied|overpay flags/);
});

test('metric interpretation does not certify talent or remove late-season uncertainty', () => {
  const skill = read('plugins/cbb-sabermetrics/skills/interpreting-advanced-metrics/SKILL.md');
  assert.doesNotMatch(skill, /Everything \| Nothing|first 3 weeks|regression is coming/);
  assert.match(skill, /not a validated talent forecast/);
});
