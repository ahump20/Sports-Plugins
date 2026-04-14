---
name: psychological-profiler
description: "Psychological Profiler (PP) — the CEE component that quantifies mental toughness, cognitive profile, and competitive drive via combined psychometric surveys, biometric proxies, and cognitive testing. Use when the user asks about mental toughness measurement, clutch performance profiling, killer instinct quantification, cognitive agility tests, or athlete psychological assessment in the context of CEE. Triggers on: \"mental toughness\", \"killer instinct\", \"clutch\", \"competitive drive\", \"psych profile\", \"cognitive agility\", \"deCervo\", \"uHIT\", \"NeuroTracker\", \"Mental Toughness Index\", \"PP\", \"psychological profiler\", \"sports psychology AI\". Loads after cee-framework."
---

# Psychological Profiler (PP)

The CEE's mental-attribute module — mental toughness, cognitive profile, competitive drive.

## Feasibility map

| Sub-capability | Rating | Primary evidence |
|---|---|---|
| Mental Toughness (from surveys) | Feasible | SMTQ, MTI validated in sports psych literature. |
| Composite mental+biometric models | Emerging | 2025 study: hybrid model R² ≈ 0.90 vs. 0.77 physical-only. |
| Cognitive Agility (reaction, decision) | Feasible | deCervo uHIT, NeuroTracker, BATAK deployed with elite athletes. |
| "Killer Instinct" inference | Speculative | No direct biometric; composite from clutch stats + psych data. |
| Character assessment from video/voice | Speculative | Commercial claims exist; regulators warn against; high false-positive risk. |
| Resilience trajectory (longitudinal) | Emerging | Works with 60+ days of data + baseline psych metrics. |

## Three input streams

### 1. Psychometric surveys (Feasible)

- **Mental Toughness Index (MTI)** — 8-item validated scale.
- **Sport Mental Toughness Questionnaire (SMTQ)** — 14-item, three subscales (confidence, constancy, control).
- **Athlete Engagement Questionnaire (AEQ)** — measures dedication, vigor, enthusiasm.
- **Competitive State Anxiety Inventory-2 (CSAI-2)** — pre-competition anxiety measurement.

Administered baseline + quarterly. Scores serve as direct inputs to NQE composite.

### 2. Cognitive testing (Feasible)

- **deCervo uHIT** — pitch-recognition/decision-making drills for baseball (extends to softball).
- **NeuroTracker** — 3D multiple-object tracking; visual attention + working memory.
- **Stroop tasks** — executive control under interference.
- **Simple reaction-time batteries** — baseline cognitive floor.

Scheduled weekly in training. Outputs feed per-athlete cognitive-profile vector.

### 3. Behavior + biometric proxies (Emerging)

- **Clutch performance stats** — WPA (Win Probability Added) in high-leverage situations, late-and-close splits, playoff vs. regular-season deltas.
- **Physiological response to pressure** — from `physiological-decoder` skill (HRV/GSR in pressure vs. neutral).
- **Post-failure recovery** — how quickly biometrics and performance return to baseline after a negative play.

Combined with surveys, these become a richer profile. Alone, they are proxies only.

## Protocols

### Baseline Profile (quarterly)
1. Athlete completes MTI + SMTQ + AEQ + CSAI-2.
2. Four cognitive tests in a 45-min session, with PD recording (HRV, GSR).
3. Output: psychological profile vector (12-dim) with per-athlete Z-scores.

### Pressure Response Profile (game/simulation)
1. Identify pressure moments (high leverage, late-game, playoff).
2. For each, capture:
   - Outcome (success/failure).
   - Physiological response (from PD).
   - Behavioral response (from VCA: posture, gaze).
   - Post-moment recovery time.
3. Aggregate over 20+ moments → Pressure Response Profile with confidence bounds.

### Longitudinal Resilience Tracking (season)
1. Weekly micro-survey (1-min: stress, mood, motivation).
2. Monthly full psychometric retake.
3. Trajectory visible over 60+ days; trend direction matters more than absolute score.

## Output schema

```json
{
  "athlete_id": "...",
  "assessment_date": "ISO 8601",
  "pp_outputs": {
    "mental_toughness_index": 6.8,
    "engagement": {
      "dedication": 5.2,
      "vigor": 4.9,
      "enthusiasm": 5.5
    },
    "cognitive_profile": {
      "reaction_time_ms": 245,
      "decision_accuracy": 0.87,
      "attention_tracking_score": 7.2,
      "executive_control_index": 0.79
    },
    "pressure_response_profile": {
      "success_rate_high_leverage": 0.61,
      "physiological_calm_index": 0.73,
      "recovery_time_seconds_mean": 18
    },
    "longitudinal_trend": "stable_improving",
    "confidence": {
      "mti": 0.95,
      "cognitive": 0.92,
      "pressure": 0.70
    }
  },
  "feasibility_tags": {
    "mti": "feasible",
    "cognitive": "feasible",
    "pressure": "emerging",
    "killer_instinct_inference": "speculative"
  }
}
```

## Anti-overclaim rules

1. **Never report "killer instinct detected"** as a Boolean. Report composite index with feasibility tag: Speculative.
2. **Do not judge character.** A low mental-toughness score is not a verdict on the athlete — it's a snapshot of a measurement at one point in time, with a standard error.
3. **Context matters.** Off-field circumstances (family events, injuries) affect scores. Never interpret a single drop as a trait regression without context.
4. **Avoid deterministic framing.** "Athlete X has mental toughness" → replace with "Athlete X scores at the 75th percentile of their cohort on the MTI; the composite NQE resilience index places them in the top quartile".

## Integration with NQE

PP outputs have high weight in NQE for readiness prediction, moderate weight for clutch-performance forecasting, and low weight for injury risk (where physical signals dominate). NQE treats PP as a stable latent trait with slow drift rather than a daily-variable signal.

## Ethics and Consent

- Psychometric surveys collected with athlete's informed consent, including explicit data-sharing scope.
- Results shared with athlete before coaching staff.
- Athletes have veto power on including PP scores in team-internal reports.
- Not used for compensation decisions or contract leverage.
- For minors (recruiting HS athletes), parental + athlete consent required, and biometric components are limited to voluntary tests only.

## Tools (downstream implementation)

- **Administration**: custom web form for surveys, deCervo/NeuroTracker licenses for cognitive tests.
- **Analysis**: Python psychometric libraries (`psy`, `factor_analyzer`).
- **Storage**: writes to `cee_pp_observations` in `bsi-analytics-db` (encrypted at rest, athlete-keyed access).
