# CBB plugin evaluation — November 25, 2026

The before/after JSON files are **static Plugin Eval heuristics**, not an
accuracy score, measured token usage or a live behavior benchmark.

Plugin Eval 0.1.2's budget reader crashes on this repository's valid string
`interface.defaultPrompt` (`join is not a function`). Evaluation used a temporary
package copy with the same string represented as a one-element array. The
original manifests were not changed to accommodate the evaluator.

The original package scores 81. The expanded candidate initially scores 54,
mostly because adding executable retrieval code/tests increases the evaluator's
estimated deferred-token cost and its function-length/complexity warnings.
The candidate also received a trigger-wording warning, which was corrected.
The final reviewed candidate scores **58**, including after the HTTP/parser
repairs. Budget and complexity warnings remain; the report is not a passing
accuracy certificate.
Keep the actual reports; do not treat a lower word/code count as evidence that
the old data path was more accurate. The parser's tested span/season handling
is retained rather than discarded to improve a static score.

Behavioral evaluation found and corrected concrete problems:

- Empty objects inside nonempty MCP result arrays passed the original check.
- Invalid source cutoff strings and negative ties could pass the diagnostic.
- The diagnostic omitted the negotiated MCP version header.
- An academic-year range such as 1999–00 could be mislabeled 1999 by the
  initial HTML helper; invalid ranges could leak their first year.
- Real roster HTML includes advertisement rows and separate staff tables;
  raw row counts must not become player counts.
- Inline/comments must not split numeric tokens; malformed spans and truncated
  HTTP responses must produce failure observations rather than tracebacks.
- Trickle-body and chunk-header reads must obey the overall download deadline.
- An SSE result can arrive before the stream closes; the diagnostic must return
  that result, preserve session handling and honor the discovered season schema.
- Published Mendoza OPS .913 differs from raw-count OPS .9121227 through
  display rounding. This is explicitly distinguished from inconsistent counts.

The independent review reproduced the issues and rechecked the MCP corrections.
Regression tests cover all corrections. See the [verification note](../../verification-2026-11-25-cbb.md)
for executed checks, real source reads and remaining host/server limits.
