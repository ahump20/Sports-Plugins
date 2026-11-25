# Source routes and observed limitations

These are discovery routes, not guaranteed APIs. Open the page and confirm its
season, scope and update date on each use. The examples checked on November 25,
2026 below are deliberately labeled **2025 historical benchmarks**.

| Request | Preferred evidence | Discovery route |
|---|---|---|
| NCAA national team/player statistics | NCAA division and season tables, qualification rules | [NCAA baseball statistics directory](https://www.ncaa.org/championships/statistics-and-records/baseball/) |
| Team record, schedule and box scores | School season-specific schedule; conference/NCAA reconciliation | [Texas 2025 text schedule](https://texaslonghorns.com/sports/baseball/schedule/text/2025) |
| Team/player counting stats | School cumulative tables and PDF; conference totals | [Texas 2025 stats](https://texaslonghorns.com/sports/baseball/stats/2025), [cumulative PDF](https://s3.us-east-2.amazonaws.com/sidearm.nextgen.sites/texassports_com/stats/baseball/2025/pdf/cume.pdf) |
| Roster, jersey, class and position | Explicit season roster and player biography | [Texas 2025 roster](https://texaslonghorns.com/sports/baseball/roster/2025) |
| Conference standings | Official conference season table; NCAA year-end archive | [NCAA standings archive](https://s3.amazonaws.com/fs.ncaa.org/Docs/stats/baseball_RB/Standings.pdf) |
| Conference team/individual stats | Published season tables; overall/conference selection | [ACC 2025](https://theacc.com/stats.aspx?path=baseball&year=2025), [Big 12 2025](https://big12sports.com/stats.aspx?path=baseball&year=2025), [OVC 2025](https://static.ovcsports.com/custompages/stats/baseball/2025/confstat.htm) |
| Records, history and championships | Association record books and school media guides | NCAA directory above; school's official archives |
| NAIA or junior college | The appropriate association and school/conference | [NAIA baseball](https://www.naia.org/sports/bsb/index), [NJCAA baseball](https://www.njcaa.org/sports/bsb/index); inspect these discovery destinations before claiming coverage |

The NCAA directory links `stats.ncaa.org/rankings?division=1&sport_code=MBA`
(also divisions 2 and 3) and `stats.ncaa.org/stats_sports/MBA/teams?division_filter=1`.
Direct requests returned HTTP 403 during the investigation. Do not describe a
blocked fetch as an empty leaderboard. No documented universal NCAA JSON API
was established in this repair.

## Historical checks and traps

- Texas's 2025 schedule and cumulative PDF agree on **44–14 overall, 22–8
  SEC**. The PDF says **as of June 1, 2025**. These facts cannot be relabeled
  as 2026 or today's record.
- Ethan Mendoza's 2025 batting line is **225 AB, 75 H, 9 2B, 4 3B, 5 HR,
  107 TB, 36 BB, 6 HBP, 1 SF**. The displayed AVG/OBP/SLG/OPS are
  **.333/.437/.476/.913**. Raw-count OBP plus SLG is .9121227 (displayed
  .912); the published .913 equals the sum of rounded .437 and .476. Retain
  published and derived OPS separately. This small display-rounding difference
  does not invalidate the counts.
- Luke Harrison's 2025 PDF line has **70.2 IP, 63 H, 24 ER, 24 BB, 72 SO**.
  That is **212 outs**, giving ERA `24 × 27 / 212 = 3.0566…` and WHIP
  `(63 + 24) × 3 / 212 = 1.2311…`.
- Texas's 2025 HTML summary panel repeats opponent AB as 1,980, but the
  detailed opponent batting total/PDF says 1,862. Its double-play summary
  repeats doubles (128/69); the PDF says double plays turned 46/31. Preserve
  both observations and identify the conflict instead of flattening sections.
- An unversioned Texas roster served **2027** while `/stats/2026` served 2026.
  A year in a URL or archive menu is not sufficient season evidence.
- [SEC 2025 conference-only statistics](https://assets.espn.go.com/sec/baseball/2025/lgconf.htm)
  and [standings summary](https://a.espncdn.com/sec/baseball/2025/lgsumm.htm) were only
  through **April 15, 2025** (Texas 29–5/13–2). Their year-specific URLs do
  not establish final-season coverage.
- The NCAA `Standings.pdf` path is mutable: inspect its year inside the file.
- The [OVC statistics directory](https://ovcsports.com/sports/2024/1/29/BB_0129240701.aspx)
  labels its sortable XML data unofficial. Preserve that label even though
  the publisher is the official conference.

For reusable data, retain exact URLs, observed titles/season evidence, source
cutoffs, retrieval timestamps, field definitions and the parts actually read.
Source terms still apply to bulk collection and redistribution.
