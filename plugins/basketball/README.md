# basketball

```
/plugin marketplace add ahump20/Sports-Plugins
/plugin install basketball@Sports-Plugins
```

| Skill | What it does |
|---|---|
| `basketball-rules` | NBA, WNBA, NCAA and FIBA rules where they differ and where models get them wrong |
| `basketball-analytics` | `hoops.py` builds possessions, offensive and defensive rating and the Four Factors from every box score of a season, and computes true shooting, effective field goal percentage and usage |
| `basketball-data` | Verified sportsdataverse, nba_api and Basketball-Reference sources, codes and traps |

Checked against published numbers in `skills/basketball-analytics/tests`:

| Case | Expected | Source |
|---|---|---|
| Stephen Curry 2015-16 TS% / eFG% | .669 / .630 | Basketball-Reference |
| 2015-16 Warriors ORtg / DRtg | 115.2 / 104.3, within 0.5 | Basketball-Reference |

```
python3 -m unittest discover -s plugins/basketball/skills/basketball-analytics/tests
SPORTS_LIVE=1 python3 -m unittest discover -s plugins/basketball/skills/basketball-analytics/tests   # downloads NBA and college box scores
```

Python 3.9+, standard library only.
