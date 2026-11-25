#!/usr/bin/env node
import {pathToFileURL} from 'node:url';

export const REQUIRED_TOOLS = [
  'bsi_get_scoreboard', 'bsi_get_standings', 'bsi_get_rankings',
  'bsi_get_player_stats', 'bsi_get_team_schedule', 'bsi_get_match_detail', 'bsi_search_intel',
];
const SEASON_TOOLS = ['bsi_get_standings', 'bsi_get_rankings', 'bsi_get_player_stats', 'bsi_get_team_schedule'];
const LIVE_URL = 'https://sabermetrics.blazesportsintel.com/mcp';
const own = (object, key) => Object.prototype.hasOwnProperty.call(object, key);
const nonempty = value => typeof value === 'string' && value.trim().length > 0;
const count = value => Number.isInteger(value) && value >= 0;
function sourceUrl(value) {
  if (typeof value !== 'string' || !/^https?:\/\//i.test(value)) return false;
  try {
    const url = new URL(value);
    return ['http:', 'https:'].includes(url.protocol) && Boolean(url.hostname);
  } catch { return false; }
}
function isoDate(value) {
  if (typeof value !== 'string' || !/^\d{4}-\d{2}-\d{2}(?:T\d{2}:\d{2}(?::\d{2}(?:\.\d+)?)?(?:Z|[+-]\d{2}:\d{2}))?$/.test(value)) return false;
  const datePart = value.slice(0, 10);
  const day = new Date(datePart + 'T00:00:00Z');
  return Number.isFinite(Date.parse(value)) && Number.isFinite(day.getTime()) && day.toISOString().startsWith(datePart);
}

function usableRow(name, row) {
  if (!row || typeof row !== 'object' || Array.isArray(row)) return false;
  if (name === 'bsi_get_standings') {
    return nonempty(row.team) && ((count(row.wins) && count(row.losses)) || (count(row.confWins) && count(row.confLosses)));
  }
  if (name === 'bsi_get_rankings') return nonempty(row.team) && Number.isInteger(row.rank) && row.rank > 0;
  if (name === 'bsi_get_team_schedule') {
    return (nonempty(row.id) || count(row.id)) && isoDate(row.date) &&
      (nonempty(row.name) || (Array.isArray(row.competitors) && row.competitors.length >= 2 && row.competitors.every(team => nonempty(team.team))));
  }
  if (name === 'bsi_get_player_stats') {
    return nonempty(row.name) && nonempty(row.team) && [row.battingStats, row.pitchingStats].some(stats =>
      stats && typeof stats === 'object' && !Array.isArray(stats) && Object.values(stats).some(value => typeof value === 'number' && Number.isFinite(value)));
  }
  if (name === 'bsi_get_team_roster') return nonempty(row.name);
  return false;
}

export function inspectCatalog(tools) {
  const problems = [];
  if (!Array.isArray(tools)) return ['tools/list did not return a tools array'];
  const names = tools.map(tool => tool.name);
  if (new Set(names).size !== names.length) problems.push('Duplicate tool names');
  for (const name of REQUIRED_TOOLS) {
    const tool = tools.find(tool => tool.name === name);
    if (!tool) { problems.push('Missing tool: ' + name); continue; }
    if (tool.inputSchema?.type !== 'object') problems.push(name + ': invalid input schema');
    if (tool.annotations?.readOnlyHint !== true) problems.push(name + ': not declared read-only');
    if (SEASON_TOOLS.includes(name) && !tool.inputSchema?.properties?.season) {
      problems.push(name + ': no explicit season input');
    }
  }
  return problems;
}

export function parseToolResult(result) {
  if (result?.isError) throw new Error('Tool reported isError');
  if (result?.structuredContent && typeof result.structuredContent === 'object') return result.structuredContent;
  for (const item of result?.content ?? []) {
    if (item.type !== 'text') continue;
    try {
      const value = JSON.parse(item.text);
      if (value && typeof value === 'object' && !Array.isArray(value)) return value;
    } catch { /* A text explanation is not a data envelope. */ }
  }
  throw new Error('No structured JSON data envelope');
}

function rowsFor(name, data) {
  if (name === 'bsi_get_standings') {
    return (Array.isArray(data.standings) ? data.standings : []).flatMap(group =>
      Array.isArray(group?.teams) ? group.teams : Array.isArray(group?.standings) ? group.standings : []);
  }
  if (name === 'bsi_get_player_stats') return [...(Array.isArray(data.players) ? data.players : []), ...(data.player ? [data.player] : [])];
  const key = {bsi_get_rankings: 'rankings', bsi_get_team_schedule: 'schedule', bsi_get_team_roster: 'roster'}[name];
  return key && Array.isArray(data[key]) ? data[key] : [];
}

/** Checks the data contract, not independent source truth or currentness. */
export function inspectResult(name, result, requestedSeason) {
  let data;
  try { data = parseToolResult(result); }
  catch (error) { return {contract: 'fail', availability: 'unknown', problems: [error.message], warnings: []}; }
  const problems = [];
  const warnings = [];
  const meta = data.meta ?? {};
  const rows = rowsFor(name, data);
  const unavailable = ['unavailable', 'ambiguous', 'source_unavailable', 'unsupported_season'].includes(data.status);
  if (!['ok', 'partial', 'unavailable', 'ambiguous', 'source_unavailable', 'unsupported_season'].includes(data.status)) {
    problems.push('Missing or unknown data status');
  }
  if (typeof meta.source !== 'string' || !meta.source.trim()) problems.push('Missing source identity');
  if (!Array.isArray(meta.source_urls) || meta.source_urls.length === 0 ||
      meta.source_urls.some(url => !sourceUrl(url))) {
    problems.push('Missing source URLs');
  }
  if (!isoDate(meta.retrieved_at) || !meta.retrieved_at.includes('T')) problems.push('Missing or invalid retrieval timestamp');
  if (!own(meta, 'source_as_of')) problems.push('Missing source cutoff field (explicit null is allowed)');
  else if (meta.source_as_of === null) warnings.push('Source cutoff is unknown; this cannot establish current or final data.');
  else if (!isoDate(meta.source_as_of)) problems.push('Invalid source cutoff (use an ISO date/time or null)');
  if (!nonempty(meta.coverage) && !(meta.coverage && typeof meta.coverage === 'object' && !Array.isArray(meta.coverage) && Object.keys(meta.coverage).length)) problems.push('Missing coverage declaration');
  if (meta.requested_season !== requestedSeason) problems.push('Requested season not preserved');
  if (!own(meta, 'season')) problems.push('Observed season not reported');
  if (!unavailable && meta.season !== requestedSeason) problems.push('Observed season does not match the request');
  if (!unavailable && (!nonempty(meta.season_verification) || /unknown|unverified|request.only/i.test(meta.season_verification))) {
    problems.push('Observed season lacks source verification');
  }
  if (unavailable && rows.length) problems.push('Unavailable/ambiguous result contains selected result rows');
  if (!unavailable && rows.length === 0) problems.push('Empty result cannot establish usable standings, rankings, schedule or player data');
  if (!unavailable && rows.some(row => !usableRow(name, row))) problems.push('Result contains unusable rows (missing identity or category data)');
  if (unavailable && !data.message && !data.error && !data.reason && !data.note && !data.warnings?.length) {
    problems.push('Unavailable result has no explanation');
  }
  if (data.status === 'partial') warnings.push('Provider declares partial coverage; do not treat this as a complete season or population.');
  if (name === 'bsi_get_rankings' && rows.length && (!nonempty(data.poll) || (!isoDate(data.release) && !isoDate(meta.source_as_of)))) {
    problems.push('Rankings lack poll identity or publication cutoff');
  }
  if (name === 'bsi_get_standings') {
    for (const row of rows) {
      if (!row || typeof row !== 'object') continue;
      for (const field of ['wins', 'losses', 'ties', 'confWins', 'confLosses', 'confTies', 'gamesPlayed']) {
        if (row[field] != null && (!Number.isInteger(row[field]) || row[field] < 0)) problems.push('Invalid record field: ' + field);
      }
      if (Number.isInteger(row.wins) && Number.isInteger(row.losses) && Number.isInteger(row.gamesPlayed)) {
        const ties = Number.isInteger(row.ties) ? row.ties : 0;
        if (row.gamesPlayed < row.wins + row.losses + ties) problems.push('Games played is smaller than recorded decisions');
      }
    }
  }
  return {
    contract: problems.length ? 'fail' : 'pass',
    availability: unavailable ? 'unavailable' : rows.length ? 'available' : 'unknown',
    rows: rows.length, season: meta.season ?? null, source: meta.source ?? null,
    verification: 'Contract checks only; source truth and completeness need independent verification.',
    problems, warnings,
  };
}

async function readRpcMessage(response, id) {
  if (!response.headers.get('content-type')?.includes('text/event-stream')) return response.json();
  if (!response.body) throw new Error('Empty SSE response');
  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let buffer = '';
  let data = [];
  try {
    while (true) {
      const {value, done} = await reader.read();
      buffer += decoder.decode(value, {stream: !done});
      // SSE permits CR, LF, and CRLF. Retain a trailing CR until the next chunk.
      let newline;
      while ((newline = /\r\n|\r|\n/.exec(buffer))) {
        if (!done && newline[0] === '\r' && newline.index === buffer.length - 1) break;
        const line = buffer.slice(0, newline.index);
        buffer = buffer.slice(newline.index + newline[0].length);
        if (line === '') {
          if (data.length) {
            const message = JSON.parse(data.join('\n'));
            data = [];
            if (message.id === id) return message;
          }
        } else if (line === 'data' || line.startsWith('data:')) {
          data.push(line === 'data' ? '' : line.slice(5).replace(/^ /, ''));
        }
      }
      if (done) throw new Error('No matching SSE response');
    }
  } finally {
    await reader.cancel().catch(() => {});
    reader.releaseLock();
  }
}

function seasonArguments(tool, args) {
  const schema = tool.inputSchema;
  const seasonSchema = schema?.properties?.season;
  if (!seasonSchema) throw new Error('Server cannot honor explicit season; no unsupported arguments sent.');
  const allowedKeys = ['type', 'description', 'title', 'default', 'examples', 'enum', 'const', 'minimum', 'maximum', 'exclusiveMinimum', 'exclusiveMaximum', 'multipleOf', 'minLength', 'maxLength', 'pattern'];
  if (Object.keys(seasonSchema).some(key => !allowedKeys.includes(key)) || !['integer', 'number', 'string'].includes(seasonSchema.type)) {
    throw new Error('Unsupported season schema; no unsupported arguments sent.');
  }
  const value = seasonSchema.type === 'string' ? String(args.season) : args.season;
  if ((seasonSchema.enum && !seasonSchema.enum.includes(value)) || (own(seasonSchema, 'const') && seasonSchema.const !== value)) {
    throw new Error('Requested season is outside the advertised schema.');
  }
  if (typeof value === 'number') {
    if ((own(seasonSchema, 'minimum') && value < seasonSchema.minimum) ||
        (own(seasonSchema, 'maximum') && value > seasonSchema.maximum) ||
        (own(seasonSchema, 'exclusiveMinimum') && value <= seasonSchema.exclusiveMinimum) ||
        (own(seasonSchema, 'exclusiveMaximum') && value >= seasonSchema.exclusiveMaximum) ||
        (own(seasonSchema, 'multipleOf') && value % seasonSchema.multipleOf !== 0)) {
      throw new Error('Requested season is outside the advertised schema.');
    }
  } else if ((own(seasonSchema, 'minLength') && value.length < seasonSchema.minLength) ||
      (own(seasonSchema, 'maxLength') && value.length > seasonSchema.maxLength) ||
      (own(seasonSchema, 'pattern') && !new RegExp(seasonSchema.pattern, 'u').test(value))) {
    throw new Error('Requested season is outside the advertised schema.');
  }
  const resolved = {...args, season: value};
  if (schema.required?.some(key => !own(resolved, key))) throw new Error('Required tool arguments are unavailable.');
  return resolved;
}

export async function checkMcp(url = LIVE_URL, season = 2025) {
  let nextId = 1;
  let sessionId;
  let protocolVersion;
  async function rpc(method, params = {}) {
    const id = nextId++;
    const headers = {'content-type': 'application/json', accept: 'application/json, text/event-stream'};
    if (sessionId) headers['mcp-session-id'] = sessionId;
    if (protocolVersion) headers['mcp-protocol-version'] = protocolVersion;
    const response = await fetch(url, {
      method: 'POST', headers, body: JSON.stringify({jsonrpc: '2.0', id, method, params}),
      signal: AbortSignal.timeout(30000),
    });
    sessionId = response.headers.get('mcp-session-id') ?? sessionId;
    if (!response.ok) throw new Error(method + ': HTTP ' + response.status);
    const responseMessage = await readRpcMessage(response, id);
    if (!responseMessage || responseMessage.id !== id || responseMessage.error) throw new Error(method + ': ' + JSON.stringify(responseMessage?.error ?? 'No matching response'));
    return responseMessage.result;
  }
  const initialized = await rpc('initialize', {
    protocolVersion: '2025-06-18', capabilities: {}, clientInfo: {name: 'sports-plugins-data-check', version: '0.4.0'},
  });
  if (!initialized?.serverInfo?.name || !initialized.capabilities?.tools) throw new Error('Missing server identity or tools capability');
  if (!['2024-11-05', '2025-03-26', '2025-06-18'].includes(initialized.protocolVersion)) throw new Error('Unsupported negotiated MCP protocol version');
  protocolVersion = initialized.protocolVersion;
  const headers = {'content-type': 'application/json', accept: 'application/json, text/event-stream'};
  if (sessionId) headers['mcp-session-id'] = sessionId;
  headers['mcp-protocol-version'] = protocolVersion;
  const notification = await fetch(url, {
    method: 'POST', headers, body: JSON.stringify({jsonrpc: '2.0', method: 'notifications/initialized'}),
    signal: AbortSignal.timeout(30000),
  });
  if (!notification.ok) throw new Error('notifications/initialized: HTTP ' + notification.status);
  const tools = [];
  const cursors = new Set();
  let cursor;
  do {
    const page = await rpc('tools/list', cursor ? {cursor} : {});
    if (!Array.isArray(page.tools)) throw new Error('Invalid tools/list page');
    tools.push(...page.tools);
    cursor = page.nextCursor;
    if (cursor && cursors.has(cursor)) throw new Error('Repeated tools/list cursor');
    if (cursor) cursors.add(cursor);
    if (cursors.size > 10) throw new Error('Too many tools/list pages');
  } while (cursor);
  const catalogProblems = inspectCatalog(tools);
  const checks = [];
  for (const [name, args] of [
    ['bsi_get_standings', {conference: 'SEC', season}],
    ['bsi_get_rankings', {season}],
    ['bsi_get_team_schedule', {team: 'texas', season}],
    ['bsi_get_player_stats', {player: 'Ethan Mendoza', team: 'texas', season}],
  ]) {
    const tool = tools.find(tool => tool.name === name);
    if (!tool) continue;
    try { checks.push({name, ...inspectResult(name, await rpc('tools/call', {name, arguments: seasonArguments(tool, args)}), season)}); }
    catch (error) { checks.push({name, contract: 'fail', availability: 'unknown', problems: [error.message]}); }
  }
  const contractPassed = !catalogProblems.length && checks.length === 4 && checks.every(check => check.contract === 'pass');
  return {
    endpoint: url, checked_at: new Date().toISOString(), requested_season: season,
    server: initialized.serverInfo, connectivity: 'pass', catalogProblems, checks,
    contract: contractPassed ? 'pass' : 'fail',
    data_available_for_all_checks: checks.length === 4 && checks.every(check => check.availability === 'available' && check.contract === 'pass'),
    verification: 'No independent factual accuracy or complete-season certification is implied.',
  };
}

if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) {
  const args = process.argv.slice(2);
  const value = key => args.includes(key) ? args[args.indexOf(key) + 1] : undefined;
  if (args.includes('--help')) {
    console.log('Usage: node scripts/check-cbb-mcp.mjs [--url HTTPS_ENDPOINT] [--season YYYY]\nChecks read-only metadata/data contracts; does not certify factual accuracy. Exit 1 if contract or required data is unavailable.');
  } else {
    const season = Number(value('--season') ?? 2025);
    if (!Number.isInteger(season) || season < 1900 || season > 2200) throw new Error('Invalid season');
    try {
      const report = await checkMcp(value('--url') ?? LIVE_URL, season);
      console.log(JSON.stringify(report, null, 2));
      if (report.contract !== 'pass' || !report.data_available_for_all_checks) process.exitCode = 1;
    } catch (error) { console.error(error.message); process.exitCode = 1; }
  }
}
