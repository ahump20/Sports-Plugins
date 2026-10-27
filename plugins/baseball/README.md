# baseball

```
/plugin marketplace add ahump20/Sports-Plugins
/plugin install baseball@Sports-Plugins
```

| Skill | What it does |
|---|---|
| `baseball-rules` | Rulings, scoring decisions and how MLB, NCAA and high school rules differ, with rule numbers from the 2026 MLB and current NCAA rulebooks |
| `baseball-analytics` | `saber.py` computes slash line, wOBA, wRC+, FIP and rates from counting stats, pulls MLB lines from the Stats API, and builds league constants for college from totals |
| `baseball-data` | Verified MLB Stats API, Baseball Savant and Lahman URLs, JSON paths and traps |

Checked against published numbers in `skills/baseball-analytics/tests`:

| Case | Expected | Source |
|---|---|---|
| Shohei Ohtani 2024 wOBA | .431 | FanGraphs, Baseball Savant |
| Tarik Skubal 2024 FIP | 2.49 | FanGraphs |
| MLB 2024 wOBA scale from league totals | 1.242 | FanGraphs Guts |

```
python3 -m unittest discover -s plugins/baseball/skills/baseball-analytics/tests
SPORTS_LIVE=1 python3 -m unittest discover -s plugins/baseball/skills/baseball-analytics/tests   # also hits the MLB Stats API
```

Python 3.9+, standard library only.
