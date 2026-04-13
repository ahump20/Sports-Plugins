# champion-enigma-engine

**Biometric-visual AI framework for quantifying athlete intangibles — grounded in 2025 research, feasibility-rated, no magic-box claims.**

The Champion Enigma Engine (CEE) measures what separates champions — emotional resilience, focus, mental toughness, neurological efficiency, clutch behavior — using multi-modal biometrics + psychometrics + cognitive testing. This plugin scaffolds the framework. Actual ML training and inference happens in downstream HuggingFace-based pipelines.

## Install

**Claude Code:**
```
/plugin marketplace add ahump20/Sports-Plugins
/plugin install champion-enigma-engine
```

**Codex CLI:**
```
codex plugins add ahump20/Sports-Plugins
codex plugins install champion-enigma-engine
```

## The Four Components

| Component | What it reads | Feasibility |
|---|---|---|
| **VCA** Visual Cortex Analyzer | Face, gaze, body language | Feasible (basics), Emerging (body lang), Speculative (micro-expressions in live) |
| **PD** Physiological Decoder | HRV, HR, EEG, GSR, respiration | Feasible (readiness), Emerging (flow state), Speculative (neural efficiency) |
| **PP** Psychological Profiler | Mental toughness, cognitive profile, pressure response | Feasible (surveys + cognitive tests), Emerging (biometric proxies for pressure) |
| **NQE** Neural Quantification Engine | Multimodal fusion → actionable readouts | Feasible (narrow scope), Speculative (career prediction) |

## What You Get

### 4 Skills

- **`cee-framework`** — canonical framework, feasibility ratings, governing principles. Load first for any CEE work.
- **`visual-cortex-analyzer`** — VCA protocols, sensors, output schema, anti-overclaim rules.
- **`physiological-decoder`** — PD protocols for HRV / flow / stress, with consent and privacy rules.
- **`psychological-profiler`** — PP protocols for mental toughness / cognitive profile / pressure response.

### 1 Agent

- **`cee-evaluator`** — end-to-end athlete evaluation agent. Coordinates across VCA / PD / PP and applies NQE fusion logic. Produces scouting reports and daily readiness with feasibility tags.

### 2 Commands

- **`/cee-evaluate athlete=<id> mode=<mode>`** — produce a CEE readout (daily-readiness, scouting, clutch-profile, full).
- **`/cee-compare a=<id> b=<id>`** — side-by-side comparison with feasibility-aware caveats.

## Governing Principles

1. **No overstated claims.** Every metric tags its feasibility tier.
2. **Multi-modal over single-modal.** Face + HRV + survey ≫ face alone.
3. **Context-aware.** Signals are reported; humans interpret.
4. **Personalized baselines.** Per-athlete models beat population norms.
5. **Consent-first.** Biometric data belongs to the athlete.

## What CEE Does NOT Do

- Predict career trajectory.
- Judge character from a single signal.
- Make binary yes/no draft decisions.
- Replace sports psychologists, performance coaches, or scouts.

## Downstream Dependencies (recommended)

This plugin is the doctrine layer. For actual ML pipelines, pair with:

- **huggingface-skills** (`huggingface-vision-trainer`, `transformers-js`) — model training + edge inference.
- **data-engineering** skills — for Airflow/dbt pipelines that move raw wearable data into the `cee_*` analytics tables.
- **cloudflare:durable-objects** — for real-time state during live sessions.

## Origin

Based on the 175-line 2025 feasibility & operationalization report at `~/Documents/champion_enigma_engine.md` — the full literature review and deployment strategy. This plugin is the executive summary + ops layer. The report is the evidence base.

Austin Humphrey conceived CEE as a tool to put pro-grade biometric-visual intelligence in the hands of athletes who don't have a full sports science staff — from the individual high-school prospect to the mid-major college program to the scout evaluating across tiers.

Born to blaze the path beaten less.
