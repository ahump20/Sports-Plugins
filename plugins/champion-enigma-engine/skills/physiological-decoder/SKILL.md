---
name: physiological-decoder
description: "Physiological Decoder (PD) — the CEE component that reads internal biometric signals (heart rate, HRV, brain activity, skin conductance) to infer stress, flow state, and neurological efficiency. Use when the user asks about HRV analysis, flow state detection, EEG in sports, wearable readiness scores, neurological efficiency, or fatigue/recovery modeling in the context of the Champion Enigma Engine. Triggers on: \"HRV\", \"heart rate variability\", \"flow state\", \"EEG athlete\", \"WHOOP\", \"Oura\", \"recovery score\", \"readiness\", \"neurological efficiency\", \"stress detection\", \"GSR\", \"biofeedback\", \"transient hypofrontality\", \"Zone7\", \"PD\", \"physiological decoder\". Loads after cee-framework."
---

# Physiological Decoder (PD)

The CEE's internal-biometric module — HRV, heart rate, EEG, GSR, respiration → stress / flow / neural efficiency.

## Feasibility map

| Sub-capability | Rating | Primary evidence |
|---|---|---|
| Stress / Recovery via HRV | Feasible | WHOOP, Oura, Polar all deployed; HRV widely validated. |
| Daily Readiness Score | Feasible | Commercial products shipping (WHOOP "recovery", Oura "readiness"). |
| Flow State Detection | Emerging | 2024 study: alpha/theta EEG + U-shape HRV + reduced motion characterize flow; feasible with multi-sensor rig in training. |
| Neurological Efficiency | Speculative | Lab evidence (lower cortical activation for same task in elites); portable EEG exists but no standard metric. |
| In-Game Real-Time Monitoring | Speculative | EEG impractical on field; HRV chest straps feasible but often not permitted. |

## Sensors

- **HRV + HR**: WHOOP strap, Polar H10 chest strap, Oura ring. Sampling 1Hz adequate for readiness; higher sampling needed for in-session flow detection.
- **EEG**: Muse headband (2-channel consumer), Emotiv EPOC X (14-channel research-grade), Neurable/Mendi for wearable motorized experiments. Used in training, not in live competition.
- **GSR (skin conductance)**: Shimmer3 GSR+, Empatica E4 (both consumer-research). Reflects sympathetic nervous arousal.
- **Respiration**: Polar chest strap with breathing extraction, or dedicated Respbelt sensors.

## Protocols

### Daily Readiness Assessment
1. Morning capture, first 10 minutes after waking.
2. HRV (5-min RMSSD) + resting HR + sleep quality from prior night + self-report mood (1–10).
3. Composite score, decomposed into:
   - **Physical**: HRV vs. 30-day rolling baseline.
   - **Mental**: self-report + morning HR responsiveness.
   - **Focus**: optional cognitive test (3-min NeuroTracker score or deCervo decision drill).

### In-Session Flow Detection (training only)
1. Athlete wears Muse EEG + Polar HR + motion sensor (any phone).
2. During focus-heavy drill (batting practice, free throws, simulation):
   - EEG alpha (8–13 Hz) and theta (4–8 Hz) power computed in 10-sec windows.
   - HRV rolling RMSSD.
   - Movement variance from motion sensor.
3. Flow signature: ↑ alpha + ↑ theta in frontal region, U-shape HRV (moderate, not extreme), ↓ unnecessary movement.
4. Report as probability (0–1), with confidence interval, NOT binary "in flow" / "not in flow".

### Clutch Response Profile (multi-session)
1. Capture HRV, HR, GSR during designated high-stakes scenarios (mock pressure drills or actual playoff moments when consented).
2. Build per-athlete baseline of physiological response to pressure.
3. NQE uses this profile to flag "Athlete X typically shows low stress response in high-leverage situations" — a descriptive statistic, not a character judgment.

## Output schema

```json
{
  "athlete_id": "...",
  "session_id": "...",
  "timestamp": "ISO 8601",
  "pd_outputs": {
    "readiness": {
      "physical": 0.87,
      "mental": 0.72,
      "focus": 0.91,
      "composite": 0.83
    },
    "flow_probability": 0.68,
    "stress_response_index": 0.34,
    "hrv_rmssd_rolling": 58.2,
    "confidence": {
      "readiness": 0.95,
      "flow": 0.70,
      "stress": 0.88
    }
  },
  "feasibility_tags": {
    "readiness": "feasible",
    "flow": "emerging",
    "neural_efficiency": "speculative"
  }
}
```

## Anti-overclaim rules

1. **HRV alone is not stress.** HRV reflects parasympathetic tone, which correlates with but does not equal stress. Always report as "stress proxy" not "stress measurement".
2. **Flow is emerging, not diagnostic.** Flow probability is a research output. Never report "athlete entered flow state at 14:23" — report "flow signature intensified in 14:20–14:30 window".
3. **Neural efficiency requires controlled tasks.** A generic EEG reading is not neural efficiency. The metric requires a specific cognitive task with a known brain-activation benchmark.
4. **Sensor compliance matters.** If the athlete didn't wear the sensor or it had poor contact, report "insufficient data" rather than extrapolating.

## Integration with NQE

PD signals are the most reliable input stream in the CEE suite for daily readiness. NQE weights PD highest for "today's training load recommendation" and lower for "career prediction" (where it lacks signal).

## Consent and Privacy

- All biometric data belongs to the athlete.
- Use respects CBA terms where applicable (e.g., NWSL's explicit biometric-data clauses — the framework defaults to opt-in).
- Data stored encrypted; athlete has deletion rights on demand.
- No sharing with external parties without written consent.

## Tools (downstream implementation)

- **Ingest**: WHOOP API, Oura API, Polar H10 BLE, raw EEG via LSL (Lab Streaming Layer).
- **Compute**: per-athlete baseline models trained on HuggingFace; HRV analysis via `hrv-analysis` Python library.
- **Storage**: writes to `cee_pd_observations` in `bsi-analytics-db`.
