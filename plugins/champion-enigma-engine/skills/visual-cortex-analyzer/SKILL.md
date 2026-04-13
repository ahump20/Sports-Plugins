---
name: visual-cortex-analyzer
description: "Visual Cortex Analyzer (VCA) — the CEE component that reads face, gaze, and body language to infer mental state. Use when the user asks about face-emotion recognition, eye tracking, gaze patterns, quiet eye, body-language AI, posture analysis, or athlete vision evaluation in the context of the Champion Enigma Engine. Triggers on: \"facial emotion\", \"micro-expression\", \"eye tracking\", \"gaze\", \"quiet eye\", \"body language AI\", \"posture analysis\", \"VCA\", \"visual cortex\", \"thermal imaging athlete\", \"Tobii\", \"WIN Reality\", \"vision coaching\". Loads after cee-framework sets feasibility governance."
---

# Visual Cortex Analyzer (VCA)

The CEE's vision module — face, gaze, body language read for mental-state inference.

## Feasibility map

| Sub-capability | Rating | Primary evidence |
|---|---|---|
| Basic facial emotion (happy/angry/sad) | Feasible | Mature FER APIs; 97.7% fatigue/pain classification from thermal imaging (2025). |
| Micro-expressions in live sports | Speculative | Research demos only; poor lighting + occlusion kill accuracy. |
| Eye gaze (fixation, quiet eye) | Feasible | Tobii hardware, VR eye-trackers; quiet eye linked to elite performance in multiple sports. |
| Body language (positive/negative state) | Emerging | ~68.9% accuracy on tennis posture study; clear cues work, nuance doesn't. |
| "Killer look" / psychological dominance | Speculative | No peer-reviewed protocol; stay in the Emerging/Speculative lane. |

## Sensors

- **Face**: standard RGB camera at 60fps, supplemented with thermal imaging for fatigue/pain biomarkers (cheek raises, nose wrinkles, lip spreads). Thermal works in low light.
- **Gaze**: Tobii Pro Glasses (on-field for practice), VR-integrated (WIN Reality, Oculus for Business) for lab/simulation.
- **Body**: pose estimation via OpenPose or MediaPipe from broadcast footage or dedicated practice cameras.

## Protocols

### Training Session Protocol
1. Camera + gaze setup 5 min before drill.
2. Baseline 60-second neutral-state capture.
3. During drill, capture gaze fixation durations, facial expressions at decision points, posture snapshots between reps.
4. Post-drill, compute:
   - **Quiet eye duration** per attempt (ms) — fixation on target before execution.
   - **Fatigue biomarker index** — composite of thermal facial signals.
   - **Posture state** — positive/negative classification per inter-rep interval.

### Game-Tape Protocol (broadcast footage)
1. Identify high-leverage moments (at-bats, penalty kicks, free throws, late-game possessions).
2. For each, extract 3-second window: approach → execution.
3. Run pose estimation + body-language classifier on the approach.
4. Report as "posture state: positive / negative / ambiguous" with confidence score. Never declare "killer instinct".

## Output schema

```json
{
  "athlete_id": "...",
  "session_id": "...",
  "timestamp": "ISO 8601",
  "vca_outputs": {
    "quiet_eye_ms_mean": 380,
    "quiet_eye_ms_stddev": 60,
    "fatigue_biomarker_index": 0.23,
    "posture_state_sequence": ["positive", "positive", "negative", "positive"],
    "confidence": {
      "quiet_eye": 0.92,
      "fatigue": 0.78,
      "posture": 0.68
    }
  },
  "feasibility_tags": {
    "quiet_eye": "feasible",
    "fatigue": "feasible",
    "posture": "emerging"
  }
}
```

## Anti-overclaim rules

1. **Never report "emotion X detected"** for sub-second windows in live game footage. The rating is Speculative for those conditions.
2. **Always report with feasibility tag.** Downstream NQE fusion weights outputs by their tag.
3. **Broadcast footage loses fidelity.** Note "derived from broadcast footage, not controlled capture" in any VCA output so consumers know the uncertainty.
4. **Culturally and individually calibrated.** Baseline resting expression varies by athlete. Any classification uses per-athlete baseline if available, else flags "population-baseline used".

## Integration with NQE

VCA outputs feed into the Neural Quantification Engine as one of three input streams. NQE weights VCA signal by its per-athlete reliability (how well the classifier has performed historically on that athlete's feature profile). This prevents overweighting noisy signals from poorly-lit game tape.

## Tools (downstream implementation)

- **Training**: `huggingface-vision-trainer` skill with emotion-FER model fine-tuned on the athlete's baseline.
- **Inference**: `transformers-js` for edge-side analysis on training-session video.
- **Storage**: writes to `cee_vca_observations` table in `bsi-analytics-db`.
