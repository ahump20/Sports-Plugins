import {describe, it} from 'node:test';
import assert from 'node:assert/strict';
import {createServer} from 'node:http';
import {REQUIRED_TOOLS, inspectCatalog, inspectResult, checkMcp} from '../scripts/check-cbb-mcp.mjs';

const meta = {
  source: 'synthetic-test-provider', source_urls: ['https://example.org/baseball/2025'],
  fetched_at: '2025-06-01T12:00:00Z', retrieved_at: '2026-11-25T12:00:00Z',
  requested_season: 2025, season: 2025, season_verification: 'source-season-field',
  source_as_of: '2025-06-01', coverage: 'synthetic test fixture, selected rows',
};
const result = data => ({content: [{type: 'text', text: JSON.stringify(data)}]});
const rankings = () => ({status: 'partial', rankings: [{rank: 1, team: 'Synthetic University', record: '10-2'}], poll: 'Synthetic test poll', release: '2025-06-01', meta: {...meta}});

describe('Blaze MCP evidence contract (synthetic fixtures)', () => {
  it('allows additional tools without freezing the server to seven capabilities', () => {
    const tools = [...REQUIRED_TOOLS, 'bsi_get_team_roster'].map(name => ({
      name, inputSchema: {type: 'object', properties: {season: {type: 'integer'}}}, annotations: {readOnlyHint: true},
    }));
    assert.deepEqual(inspectCatalog(tools), []);
  });
  it('rejects a catalog that cannot express the requested season', () => {
    const tools = REQUIRED_TOOLS.map(name => ({name, inputSchema: {type: 'object'}, annotations: {readOnlyHint: true}}));
    assert.ok(inspectCatalog(tools).some(problem => problem.includes('no explicit season')));
  });
  it('rejects the old nonempty-text success case with empty rankings', () => {
    assert.equal(inspectResult('bsi_get_rankings', result({rankings: []}), 2025).contract, 'fail');
  });
  it('accepts a scoped partial observation without calling it complete', () => {
    const report = inspectResult('bsi_get_rankings', result(rankings()), 2025);
    assert.equal(report.contract, 'pass');
    assert.equal(report.availability, 'available');
    assert.ok(report.warnings.some(warning => warning.includes('partial coverage')));
  });
  it('does not replace a missing source season with requested season', () => {
    const data = rankings(); data.meta.season = null;
    assert.equal(inspectResult('bsi_get_rankings', result(data), 2025).contract, 'fail');
  });
  it('rejects a fallback to a different season', () => {
    const data = rankings(); data.meta.season = 2026;
    assert.equal(inspectResult('bsi_get_rankings', result(data), 2025).contract, 'fail');
  });
  it('fresh retrieval time cannot replace source cutoff metadata', () => {
    const data = rankings(); delete data.meta.source_as_of;
    assert.equal(inspectResult('bsi_get_rankings', result(data), 2025).contract, 'fail');
  });
  it('accepts an explicit unknown cutoff while retaining the currentness warning', () => {
    const data = rankings(); data.meta.source_as_of = null;
    const report = inspectResult('bsi_get_rankings', result(data), 2025);
    assert.equal(report.contract, 'pass');
    assert.ok(report.warnings.some(warning => warning.includes('cannot establish current')));
  });
  it('honest unavailability passes contract checks but never a data-availability check', () => {
    const data = {status: 'unavailable', rankings: [], message: 'Source blocked', meta: {...meta, season: null}};
    const report = inspectResult('bsi_get_rankings', result(data), 2025);
    assert.equal(report.contract, 'pass');
    assert.equal(report.availability, 'unavailable');
  });
  it('an unavailable response must not contain a selected player from ambiguous matches', () => {
    const data = {status: 'ambiguous', players: [{name: 'Smith'}], message: 'Multiple matches', meta};
    assert.equal(inspectResult('bsi_get_player_stats', result(data), 2025).contract, 'fail');
    data.players = []; data.player = {name: 'Smith'};
    assert.equal(inspectResult('bsi_get_player_stats', result(data), 2025).contract, 'fail');
  });
  it('a provider label without source URLs is insufficient provenance', () => {
    const data = rankings(); delete data.meta.source_urls;
    assert.equal(inspectResult('bsi_get_rankings', result(data), 2025).contract, 'fail');
  });
  it('source URLs must identify an absolute HTTP(S) location', () => {
    for (const url of ['https://', 'http://', '/baseball/2025', 'javascript:alert(1)', 'https://[broken']) {
      const data = rankings(); data.meta.source_urls = [url];
      assert.equal(inspectResult('bsi_get_rankings', result(data), 2025).contract, 'fail', url);
    }
    for (const url of ['https://example.org/baseball/2025', 'http://example.org:8080/stats?season=2025', 'HTTPS://example.org/stats']) {
      const data = rankings(); data.meta.source_urls = [url];
      assert.equal(inspectResult('bsi_get_rankings', result(data), 2025).contract, 'pass', url);
    }
  });
  it('keeps missing conference records distinct from zeros', () => {
    const data = {status: 'partial', standings: [{conference: 'SEC', teams: [{team: 'Synthetic University', wins: 10, losses: 2, confWins: null, confLosses: null, gamesPlayed: 12}]}], meta};
    assert.equal(inspectResult('bsi_get_standings', result(data), 2025).contract, 'pass');
    assert.equal(data.standings[0].teams[0].confWins, null);
  });
  it('rejects impossible record arithmetic', () => {
    const data = {status: 'partial', standings: [{teams: [{wins: 10, losses: 2, gamesPlayed: 5}]}], meta};
    assert.equal(inspectResult('bsi_get_standings', result(data), 2025).contract, 'fail');
  });
  it('tool errors cannot count as usable observations', () => {
    assert.equal(inspectResult('bsi_get_rankings', {isError: true, content: []}, 2025).contract, 'fail');
  });
  it('nonempty arrays of empty or identity-only rows are not usable statistics', () => {
    for (const [name, fields] of [
      ['bsi_get_standings', {standings: [{teams: [{}]}]}],
      ['bsi_get_rankings', {rankings: [{}], poll: 'Test poll', release: '2025-06-01'}],
      ['bsi_get_team_schedule', {schedule: [{}]}],
      ['bsi_get_player_stats', {players: [{name: 'Synthetic Player', team: 'Synthetic University'}]}],
    ]) assert.equal(inspectResult(name, result({status: 'partial', ...fields, meta}), 2025).contract, 'fail', name);
  });
  it('rejects invalid source cutoff dates', () => {
    for (const cutoff of ['banana', '2025-02-30', '']) {
      const data = rankings(); data.meta.source_as_of = cutoff;
      assert.equal(inspectResult('bsi_get_rankings', result(data), 2025).contract, 'fail');
    }
  });
  it('a malformed poll release cannot substitute for the unknown source cutoff', () => {
    const data = rankings(); data.meta.source_as_of = null; data.release = 'banana';
    assert.equal(inspectResult('bsi_get_rankings', result(data), 2025).contract, 'fail');
  });
  it('rejects negative ties rather than subtracting them from decisions', () => {
    const data = {status: 'partial', standings: [{teams: [{team: 'Texas', wins: 44, losses: 14, ties: -2, gamesPlayed: 56}]}], meta};
    assert.equal(inspectResult('bsi_get_standings', result(data), 2025).contract, 'fail');
  });
  it('malformed row values return diagnostic failures rather than throwing', () => {
    for (const row of [null, 'Texas', {}, 0]) {
      const data = {status: 'partial', standings: [{teams: [row]}], meta};
      assert.equal(inspectResult('bsi_get_standings', result(data), 2025).contract, 'fail');
    }
  });
});

describe('Blaze MCP transport lifecycle', () => {
  for (const variant of [
    {name: 'JSON with integer seasons', format: 'json', schema: {type: 'integer'}},
    {name: 'SSE that stays open after a matching result', format: 'sse', schema: {type: 'integer'}},
    {name: 'JSON with a string-season enum', format: 'json', schema: {type: 'string', enum: ['2025']}},
    {name: 'an unsupported season schema without calling tools', format: 'json', schema: {anyOf: [{type: 'string'}, {type: 'integer'}]}, rejects: true},
    {name: 'an out-of-range season without calling tools', format: 'json', schema: {type: 'integer', minimum: 2026}, rejects: true},
  ]) it('negotiates the protocol, session and catalog pages for ' + variant.name, async () => {
    const calls = [];
    const server = createServer((request, response) => {
      let raw = '';
      request.on('data', chunk => { raw += chunk; });
      request.on('end', () => {
        const message = JSON.parse(raw);
        calls.push({method: message.method, headers: request.headers, args: message.params?.arguments});
        if (message.method !== 'initialize') {
          if (request.headers['mcp-protocol-version'] !== '2025-06-18' || request.headers['mcp-session-id'] !== 'test-session') {
            response.writeHead(400); response.end(); return;
          }
        }
        let payload;
        if (message.method === 'initialize') {
          response.setHeader('mcp-session-id', 'test-session');
          payload = {protocolVersion: '2025-06-18', serverInfo: {name: 'synthetic-server', version: 'test'}, capabilities: {tools: {}}};
        } else if (message.method === 'notifications/initialized') {
          response.writeHead(202); response.end(); return;
        } else if (message.method === 'tools/list') {
          const page = message.params?.cursor ? REQUIRED_TOOLS.slice(3) : REQUIRED_TOOLS.slice(0, 3);
          payload = {tools: page.map(name => ({name, inputSchema: {type: 'object', properties: {season: variant.schema}}, annotations: {readOnlyHint: true}})), ...(!message.params?.cursor ? {nextCursor: 'page-two'} : {})};
        } else {
          const name = message.params.name;
          const observations = {
            bsi_get_standings: {standings: [{conference: 'SEC', teams: [{team: 'Synthetic University', wins: 10, losses: 2}]}]},
            bsi_get_rankings: rankings(),
            bsi_get_team_schedule: {schedule: [{id: 'synthetic-1', date: '2025-03-01T12:00Z', name: 'Synthetic game', status: {completed: false}}]},
            bsi_get_player_stats: {players: [{name: 'Synthetic Player', team: 'Synthetic University', battingStats: {atBats: 10, hits: 0, hitByPitch: null}}]},
          }[name];
          payload = result({status: 'partial', meta, ...observations});
        }
        const encoded = JSON.stringify({jsonrpc: '2.0', id: message.id, result: payload});
        if (variant.format === 'sse') {
          response.writeHead(200, {'content-type': 'text/event-stream'});
          response.write(': heartbeat\r\ndata: {"jsonrpc":"2.0","method":"notifications/progress"}\r\n\r\ndata: ' + encoded + '\r');
          setImmediate(() => response.write('\n\r\n'));
          // Deliberately keep the response open. The client must stop at its result.
        } else {
          response.writeHead(200, {'content-type': 'application/json'});
          response.end(encoded);
        }
      });
    });
    await new Promise(resolve => server.listen(0, '127.0.0.1', resolve));
    const guard = setTimeout(() => server.closeAllConnections(), 5000);
    try {
      const report = await checkMcp('http://127.0.0.1:' + server.address().port + '/mcp', 2025);
      assert.equal(report.contract, variant.rejects ? 'fail' : 'pass', JSON.stringify(report));
      assert.equal(report.data_available_for_all_checks, !variant.rejects);
      assert.deepEqual(calls.slice(0, 4).map(call => call.method), ['initialize', 'notifications/initialized', 'tools/list', 'tools/list']);
      const toolCalls = calls.filter(call => call.method === 'tools/call');
      assert.equal(toolCalls.length, variant.rejects ? 0 : 4);
      for (const call of toolCalls) assert.equal(call.args.season, variant.schema.type === 'string' ? '2025' : 2025);
    } finally {
      clearTimeout(guard);
      server.closeAllConnections();
      await new Promise(resolve => server.close(resolve));
    }
  });
});

describe('Blaze MCP live data contract', {skip: !process.env.SPORTS_LIVE && 'set SPORTS_LIVE=1 for live provider checks'}, () => {
  it('returns season-scoped data and provenance, separately from connectivity', async () => {
    const report = await checkMcp(undefined, Number(process.env.CBB_TEST_SEASON ?? 2025));
    assert.equal(report.connectivity, 'pass');
    assert.equal(report.contract, 'pass', JSON.stringify(report, null, 2));
    assert.equal(report.data_available_for_all_checks, true, JSON.stringify(report, null, 2));
  });
});
