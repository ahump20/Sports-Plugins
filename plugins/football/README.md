# football

```
/plugin marketplace add ahump20/Sports-Plugins
/plugin install football@Sports-Plugins
```

| Skill | What it does |
|---|---|
| `football-rules` | NFL and NCAA rules where they differ and where models get them wrong, with rule references |
| `football-analytics` | `nflfast.py` computes NFL team and player EPA, success rate and CPOE from nflverse play-by-play, plus NFL passer rating and NCAA passing efficiency; `cfbfast.py` does the same for college from sportsdataverse play-by-play and official box scores |
| `football-data` | Verified nflverse, sportsdataverse and College Football Data sources (play-by-play, box scores, adjusted ratings, polls, recruiting, transfer portal), keys, sign conventions and limits |

Checked against published numbers in `skills/football-analytics/tests`:

| Case | Expected | Source |
|---|---|---|
| Lamar Jackson 2024 passing EPA | 172.279 | nflverse player stats |
| Patrick Mahomes, 2024 week 1 passing EPA | 11.084 | nflverse player stats |
| Josh Allen 2023 passing EPA | 91.693 | nflverse player stats |
| Aaron Rodgers 2011 passer rating | 122.5 | Packers.com |
| Joe Burrow 2019 NCAA efficiency | 202.0 | Davey O'Brien Award |
| Texas 2024 offense: 1,108 plays, 92.49 EPA, 509 successes | match | sportsdataverse advanced game boxes |
| Texas at Michigan 2024: Texas 68 plays, 11.43 EPA; Ewers 14.64 passing EPA | exact | sportsdataverse advanced game boxes |
| Quinn Ewers 2024: 293/445, 3,472 yds, 31 TD, 12 INT | 148.98 | NCAA, via cfbstats.com |

```
python3 -m unittest discover -s plugins/football/skills/football-analytics/tests
SPORTS_LIVE=1 python3 -m unittest discover -s plugins/football/skills/football-analytics/tests   # downloads 2023 and 2024 NFL and 2024 college play-by-play
```

Python 3.9+, standard library only.
