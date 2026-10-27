import { describe, it, before, after } from "node:test";
import assert from "node:assert/strict";
import { createServer } from "node:http";

// The seven tools the Blaze Sports Intel MCP serves. The plugin docs promise
// exactly these, so a rename or removal on the server should fail here first.
const TOOLS = [
  "bsi_get_scoreboard",
  "bsi_get_standings",
  "bsi_get_rankings",
  "bsi_get_player_stats",
  "bsi_get_team_schedule",
  "bsi_get_match_detail",
  "bsi_search_intel",
];
const LIVE_URL = "https://sabermetrics.blazesportsintel.com/mcp";

let nextId = 1;
async function rpc(url, method, params = {}) {
  const res = await fetch(url, {
    method: "POST",
    headers: { "content-type": "application/json", accept: "application/json, text/event-stream" },
    body: JSON.stringify({ jsonrpc: "2.0", id: nextId++, method, params }),
  });
  assert.equal(res.status, 200, `${method}: HTTP ${res.status}`);
  const text = await res.text();
  // Streamable HTTP may answer as an event stream; take the last data line.
  const body = res.headers.get("content-type")?.includes("text/event-stream")
    ? text.split("\n").filter((l) => l.startsWith("data:")).pop()?.slice(5)
    : text;
  const msg = JSON.parse(body);
  assert.ok(!msg.error, `${method}: ${JSON.stringify(msg.error)}`);
  return msg.result;
}

/** Initialize, list tools, and call one, the way a client would on connect. */
async function checkServer(url) {
  const init = await rpc(url, "initialize", {
    protocolVersion: "2024-11-05",
    capabilities: {},
    clientInfo: { name: "sports-plugins-ci", version: "1" },
  });
  assert.ok(init.serverInfo?.name, "initialize returns serverInfo");
  assert.ok(init.capabilities?.tools, "server offers tools");

  const { tools } = await rpc(url, "tools/list");
  assert.deepEqual(tools.map((t) => t.name).sort(), [...TOOLS].sort());

  const rankings = await rpc(url, "tools/call", { name: "bsi_get_rankings", arguments: {} });
  assert.ok(!rankings.isError, `bsi_get_rankings errored: ${JSON.stringify(rankings.content)}`);
  assert.ok(rankings.content?.[0]?.text?.length > 0, "bsi_get_rankings returned text");
}

describe("Blaze MCP client check", () => {
  // A stand-in shaped like the deployed worker, so the check itself is tested
  // on every run and the weekly live job only fails when the server changes.
  let server;
  let url;
  before(async () => {
    server = createServer((req, res) => {
      let raw = "";
      req.on("data", (c) => (raw += c));
      req.on("end", () => {
        const { id, method } = JSON.parse(raw);
        const result = {
          initialize: { protocolVersion: "2024-11-05", capabilities: { tools: {} }, serverInfo: { name: "blaze-sports-intel", version: "4.0.0" } },
          "tools/list": { tools: TOOLS.map((name) => ({ name, inputSchema: { type: "object" } })) },
          "tools/call": { content: [{ type: "text", text: '{"rankings":[]}' }] },
        }[method];
        res.writeHead(200, { "content-type": "application/json" });
        res.end(JSON.stringify({ jsonrpc: "2.0", id, result }));
      });
    });
    await new Promise((r) => server.listen(0, "127.0.0.1", r));
    url = `http://127.0.0.1:${server.address().port}/mcp`;
  });
  after(() => server.close());

  it("passes against a server shaped like the deployed one", async () => {
    await checkServer(url);
  });
});

describe("Blaze MCP live", { skip: !process.env.SPORTS_LIVE && "set SPORTS_LIVE=1 to hit the live server" }, () => {
  it("serves the seven documented tools and answers a call", async () => {
    await checkServer(LIVE_URL);
  });
});
