# Handoff Protocol

Live coverage stays in bsi-gameday-ops. Depth goes back to the intelligence skills.

---

## When to hand off

| User says... | Route to |
|-------------|----------|
| "Write a feature about this game" | `college-baseball-intelligence` → Mode 3: Editorial |
| "Deep dive on [player] from tonight's game" | `college-baseball-intelligence` → Mode 2: Analytics |
| "Break down Texas's performance tonight" | `texas-longhorns-baseball-intelligence` → Game Breakdown |
| "Preview tomorrow's matchup" | `college-baseball-intelligence` → Mode 5: Scouting |
| "What are the postseason implications?" | `college-baseball-intelligence` → Mode 6: Postseason |
| "Compare [Team A] and [Team B]" | `college-baseball-intelligence` → Mode 2: Analytics |
| "How does this affect the SEC race?" | `college-baseball-intelligence` → Mode 2: Analytics |

## When to stay

- "What's the score?"
- "Update me on the game"
- "What happened?" (about a game that just ended)
- "How's the national slate looking?"
- "Any upsets tonight?"
- "What are the live games right now?"

## Gray zone

If it's ambiguous whether the ask is "live coverage" or "deep analysis,"
default to staying in gameday-ops and delivering the fast version. If the
user wants more depth, they'll ask — and then you hand off.
