---
name: predictive-modeling
description: Use when the task involves building a win probability model, player projection system, regression analysis, or any predictive or forecasting component for sports data. Covers methodology selection, feature engineering for sports, model implementation in TypeScript/Python, and output calibration.
---

# Predictive Modeling

Use this skill when the task requires producing a model that forecasts future performance, estimates probability, or ranks players or teams based on historical data. Good sports models are transparent about their assumptions, honest about uncertainty, and useful to someone making a real decision.

## Working Model

Before building any model, establish:

- **Prediction target**: Win probability? Player seasonal projection? Team standings? Injury risk?
- **Feature availability**: What data is actually available? Statcast-level, counting stats only, or schedule/context data?
- **Evaluation method**: How will the model be tested? Holdout season, cross-validation, or Brier score on live events?
- **Consumer**: Internal analytics, public-facing display, or coaching decision support?

Never build a model without a defined evaluation method. A model that cannot be scored is not a model — it is a guess with math.

## Model Type Selection

| Prediction task | Recommended approach |
|----------------|---------------------|
| Win probability (in-game) | Logistic regression or gradient boosted tree on run diff + inning + outs |
| Player season projection | 3-year weighted average (Marcel-style) + regression to mean |
| Standings projection | Monte Carlo simulation using team run differential |
| Pitcher ERA projection | FIP/xFIP regression to mean (regress toward 4.20 for college) |
| Draft value | Positional scarcity ranking with wRC+ and FIP tiers |

Default to the simplest model that has an acceptable accuracy. A Marcel projection is more useful than an untested neural network.

## Marcel-Style Player Projection (College Baseball)

The Marcel system (developed for MLB by Tom Tango) works well for college with minor adjustments:

### Batting projection

```
Projected wOBA = (3 × wOBA_yr1 + 4 × wOBA_yr2 + 5 × wOBA_yr3 + 4 × lgAvg × reliabilityPA)
                 / (3 × PA_yr1 + 4 × PA_yr2 + 5 × PA_yr3 + 4 × reliabilityPA)
```

Where:
- `yr1` = most recent season, `yr3` = three seasons ago
- `reliabilityPA` = 200 PA (MLB standard); use 150 for college (shorter seasons)
- `lgAvg` = conference average wOBA for the year

Apply a playing-time adjustment: weight projections by PA share in each prior season.

### Pitching projection

```
Projected FIP = (3 × FIP_yr1 + 4 × FIP_yr2 + 5 × FIP_yr3 + 4 × lgAvgFIP × reliabilityIP)
                / (3 × IP_yr1 + 4 × IP_yr2 + 5 × IP_yr3 + 4 × reliabilityIP)
```

`reliabilityIP` = 80 IP for college pitchers (starters).

Regression to mean is stronger for college because:
- Smaller sample sizes
- Higher year-to-year variance (roster churn, transfer portal)
- Developmental curves are steeper

## Win Probability Model

### Feature set

```typescript
interface GameState {
  inning: number;         // 1–9 (or extra)
  isTopHalf: boolean;
  outs: number;           // 0, 1, 2
  runnersOn: number;      // Bitmap: 1B=1, 2B=2, 3B=4 → 0–7
  homeScore: number;
  awayScore: number;
  runDifferential: number; // homeScore - awayScore (from home team perspective)
}
```

### Logistic regression approach

```typescript
// Train on historical NCAA game states → final outcome
// Features: inning, half, outs, runners, run_diff, inning × run_diff interaction
// Output: P(home team wins | current state)

function winProbability(state: GameState, coefficients: number[]): number {
  const x = buildFeatureVector(state, coefficients);
  const logit = dotProduct(x, coefficients);
  return 1 / (1 + Math.exp(-logit));
}
```

Minimum training data: 5,000 game-states with known outcomes. Below that, use a lookup table from published college baseball win-expectancy research.

### Output calibration

Check that the model's predicted probabilities match actual win rates:
- At 70% predicted: ~70% of those games should result in the predicted team winning.
- Use Brier Score = mean((predicted_prob − actual_outcome)²). Target: < 0.20.
- Use reliability diagram to visualize calibration.

## Uncertainty Communication

Every model output must include an uncertainty indicator:

```typescript
interface Projection {
  playerId: string;
  projectedWoba: number;
  projectedPA: number;
  confidence: 'high' | 'medium' | 'low';  // Based on PA sample
  note?: string;   // e.g. "Transfer — no prior D1 sample"
}
```

Confidence tiers:
- **High**: 3 years of D1 data, 300+ career PA
- **Medium**: 1–2 years of D1 data, 150–300 PA
- **Low**: < 1 year of D1 data, < 150 PA, or transfer with no prior D1 record

Always display the confidence tier alongside any projection in the UI.

## Texas Longhorns Projection Notes

For Texas specifically:
- Disch-Falk is a hitter-friendly park — apply a park factor adjustment when projecting ERA/FIP for home games (approximately +5–8% run environment relative to neutral).
- Transfer portal additions from lower conferences should carry a "Low" confidence tag for at least half a season.
- UT's pitching development program has historically improved FIP by ~0.3–0.5 runs from freshman to junior seasons — a mild upward adjustment is defensible for returning arms.

## Hard Rules

- Never publish a model without a stated evaluation metric and sample size.
- Never project a player with fewer than 50 career PA without a "Low confidence — preliminary" label.
- Never present point estimates without ranges: show the 25th–75th percentile band wherever feasible.
- Always regress to the mean for college players — raw performance over one season is insufficient to project without regression.
- Never compare a college model's outputs directly to MLB projections without adjusting for level-of-play.
- Document every feature used in the model, including any that were tried and dropped. This makes the model reviewable.
