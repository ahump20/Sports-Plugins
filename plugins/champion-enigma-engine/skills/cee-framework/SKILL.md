---
name: cee-framework
description: "Canonical framework for the Champion Enigma Engine (CEE) — the biometric-visual AI system for quantifying athlete intangibles. Use when the user asks about CEE, Champion Enigma Engine, athlete intangibles, mental toughness quantification, killer instinct, biometric-visual AI, neurological efficiency, flow state detection, multimodal athlete evaluation, or references to the four components (VCA / PD / PP / NQE). Triggers on: \"Champion Enigma\", \"CEE\", \"athlete intangibles\", \"mental toughness AI\", \"biometric vision\", \"flow state\", \"neural efficiency\", \"multimodal performance prediction\", \"scouting AI\", \"intangible quantification\", \"Champion Quotient\". Load this first when any CEE work begins — it establishes which capabilities are Feasible / Emerging / Speculative and governs the rest of the plugin's skills."
---

# Champion Enigma Engine Framework

Quantifying the intangibles that separate champions — grounded in 2025 research, feasibility-rated so no magic-box claims ship.

## The Four Components

1. **Visual Cortex Analyzer (VCA)** — face, gaze, body language
2. **Physiological Decoder (PD)** — stress, flow state, neurological efficiency
3. **Psychological Profiler (PP)** — mental toughness, cognitive profile
4. **Neural Quantification Engine (NQE)** — multimodal synthesis + performance prediction

Each has its own skill (`visual-cortex-analyzer`, `physiological-decoder`, `psychological-profiler`) detailing capabilities, sensors, and protocols. NQE integration logic lives in this framework skill — it's the fusion layer, not a standalone capability.

## Feasibility Ratings (2025)

| Capability | Rating | Notes |
|---|---|---|
| Facial Emotion Recognition (basic emotions, fatigue) | **Feasible** | 97.7% accuracy in controlled thermal-imaging study; macro-expressions reliable. |
| Micro-Expression Analysis (live sports) | **Speculative** | Research-level, not production-ready in uncontrolled environments. |
| Eye Gaze / Focus Tracking | **Feasible** | Tobii, WIN Reality VR already deployed with elite athletes; "quiet eye" is validated. |
| Body Language Emotion Decoding | **Emerging** | ~68.9% accuracy for positive/negative state from posture; nuance limited. |
| Stress Detection (HRV / GSR) | **Feasible** | WHOOP, Oura, Polar already mainstream; well-validated. |
| Flow State Detection | **Emerging** | Demonstrated with EEG + wearables in studies; practical in training environments. |
| Neurological Efficiency | **Speculative** | Lab evidence exists; no standard metric, requires EEG. |
| Mental Toughness Profiling | **Emerging** | Indirect via questionnaires + biometric proxies; composite models reaching R² ≈ 0.90. |
| "Killer Instinct" / Competitive Drive | **Speculative** | Inferrable from clutch-performance stats + psych data; no direct biometric. |
| Multimodal Performance Prediction | **Feasible** (narrow scope) | Zone7-style injury risk, per-athlete readiness models work with bespoke training data. |
| General "Champion Potential" Index | **Speculative** | AI can rank on measured traits; long-term career prediction remains unreliable. |

## Governing Principles

1. **No overstated claims.** Every CEE output tags its feasibility tier. A "clutch score" is reported as "composite index, ±large uncertainty", not "confirmed killer instinct."
2. **Multi-modal over single-modal.** Single-signal inference (face alone, HRV alone) is weaker than fused inference. Always integrate.
3. **Context-aware.** A grimace can be pain, not mental strain. A high HRV can be recovery, not composure. The Engine reports signals; humans interpret.
4. **Personalized baselines.** Population-level norms are weaker than per-athlete baselines trained on 30+ days of data.
5. **Consent-first.** Biometric data belongs to the athlete. The framework surfaces what's legal (practice, consenting training) and flags what isn't (covert in-game monitoring, non-consenting minors).

## NQE Integration Pattern

The Neural Quantification Engine combines VCA + PD + PP outputs into actionable readouts. Four realistic NQE deliverables today:

1. **Daily Readiness Score** — physical + mental + focus sub-scores, drives training prescription.
2. **Clutch Performance Likelihood** — probabilistic ("80% probability of maintaining performance under playoff pressure, based on 47 comparable situations"). Never deterministic.
3. **Skill Improvement Trajectory** — trend projection from adaptation curves ("if current HRV + reaction-time trend holds, expect 0.08s sprint improvement in 2 months").
4. **Multidimensional Comparisons** — composite "mental-fitness index" vs. peer cohort. Useful for scouting IF the comparison cohort has matched data.

What NQE does NOT do:
- Predict career trajectory ("this 19-year-old will become the next X").
- Judge character from a single signal.
- Make binary yes/no draft decisions.

## Deployment Modes

### Individual Athlete Training
Wearable suite (WHOOP + HRV strap + optional EEG headband during focus drills) + AR/VR sessions (WIN Reality for hitters, NeuroTracker for decision-makers, etc.) → daily readiness → targeted psych drills.

### Team Scouting
Controlled combine environment (eye-tracker + cognitive battery + physiological baseline) + game-tape VCA analysis + NQE composite report for the scouting department. Flagged as decision-support, not decision-maker.

## Integration with BSI Stack

- **Data:** CEE outputs write to `bsi-analytics-db` (D1) under a dedicated `cee_*` table namespace.
- **MCP:** future `mcp__claude_ai_Champion_Enigma_Engine__*` tools (not yet live) will expose query access.
- **Compute:** VCA and NQE model training happens via `huggingface-vision-trainer` skill (not bundled here — pairs with this plugin).
- **UI:** readiness dashboards on blazesportsintel.com behind auth (Stripe-keyed).

## Referenced research

A 175-line feasibility report lives at `~/Documents/champion_enigma_engine.md` with the full 2025 literature review. This skill is the executive-summary ops layer; the report is the evidence base.
