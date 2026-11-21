# 🤖 AGENTS.md: Agent Guidelines for Developing the Courtroom Skill

> **Context:** This repository contains the source code, prompts, schemas, and configurations for the **Courtroom Skill** in Antigravity / Gemini CLI.

---

## 1. Core Directives & Guiding Principles

When assisting either **Person A** or **Person B** on this repository, you must adhere strictly to the following standards:

1. **Adversarial Integrity:**  
   Never generate lenient or generic prosecution arguments. When writing or testing court prompts, the Prosecution must ruthlessly attack structural flaws, operational vulnerabilities, and economic costs.
2. **True Subagent Isolation:**  
   In all orchestration code (`run_trial_workflow.py`), ensure juror prompts are context-isolated. A juror subagent must never receive the output, ballot, or thoughts of another juror. If a fallback is necessary, prominently tag:
   `[SIMULATION NOTICE]: Sequential persona fallback executed.`
3. **Inviolable Minority Preservation:**  
   The Judge can never dismiss or summarize away a `critical_objection` raised by any juror—even from a lone dissenter. All objections must reach `VERDICT.md`.
4. **No Fabricated Evidence:**  
   Never fabricate fake CVEs, fake benchmarks, or unverified library methods in trial examples. All factual claims must be verifiable. Missing information must be labeled `[ASSUMPTION]` or trigger `ABSTAIN`.

---

## 2. Technical Stack & Conventions

- **Language:** Python 3.10+ (standard library preferred; minimal external dependencies).
- **Type Annotations:** Full type hinting (`from typing import List, Dict, Optional, Any`) across all engine code.
- **Data Validation:** JSON Schemas (draft-07 or draft-2020-12 compatible) stored under `schemas/`. All engine inputs and outputs must validate against these schemas.
- **Paths & Cross-Platform:** Always use `pathlib.Path` or `os.path.join` to ensure compatibility with Windows, macOS, and Linux environments.
- **Formatting:** Clean Markdown for all templates and verdict reports. Mermaid diagrams are encouraged for architecture and trial flow visualization.

---

## 3. How to Assist Person A vs Person B

### When the user is working on **Person A** tasks (Systems / Engine):
- Focus on: `court_engine.py`, `scripts/run_trial_workflow.py`, `SKILL.md`, and schema validation.
- Ensure state persistence cleanly writes into `.court/cases/<case-id>/`.
- Make sure command parsing handles `/court`, `/court --speed`, and `/court --retrial <case-id>`.

### When the user is working on **Person B** tasks (Jurors & Prompts):
- Focus on: `references/jurors.json`, `references/evidence_rules.md`, and templates in `references/templates/`.
- Ensure each of the 25+ juror personas has an authentic, distinct voice and a clear philosophical bias.
- Keep the `[FACT]` vs `[ASSUMPTION]` vs `[OPINION]` taxonomy sharp in all prompts.

---

## 4. Key File Map

| Path | Purpose |
| :--- | :--- |
| `README.md` | General overview and usage instructions. |
| `PROJECT.md` | Complete architectural specification and system rules. |
| `Person A.md` | Systems Architect task list and roadmap. |
| `Person B.md` | Adversarial Designer task list and roadmap. |
| `SKILL.md` | Antigravity skill declaration. |
| `court_engine.py` | Core state machine and scoring engine. |
| `scripts/run_trial_workflow.py` | Subagent workflow script. |
| `references/jurors.json` | 25+ juror personas roster. |
| `references/evidence_rules.md` | Evidentiary taxonomy and rules. |
| `references/templates/` | Templates for dossier and `VERDICT.md`. |
| `schemas/` | JSON schemas for juror, ballot, and dossier. |
