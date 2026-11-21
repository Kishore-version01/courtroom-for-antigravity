# 📜 PROJECT.md: Courtroom Skill Specification & Architecture

## 1. Vision & Core Philosophy

The Courtroom Skill provides **automated adversarial red-teaming** for technical designs, architectural shifts, product ideas, and refactoring plans. It operates on the legal principle that **ideas must defend themselves beyond a reasonable doubt** before engineering hours are spent implementing them.

### Principles:
1. **Adversarial by Default:** The prosecution does not hold back; it actively seeks out the conditions under which the proposal collapses.
2. **True Context Isolation:** Jurors evaluate the record without peer visibility to eliminate consensus bias and anchoring.
3. **No Hallucinated Evidence:** Claims must be grounded in real-world facts, specifications, or codebase evidence. Missing data must result in assumptions or abstentions.
4. **Minority Voice Protection:** The Judge cannot dismiss critical objections simply because a majority voted `NOT GUILTY`.

---

## 2. Trial Modes

### Mode 1: Full Grand Jury (Default)
Used for high-stakes decisions (e.g., architectural rewrites, database migrations, security design, framework adoptions).
- **Jury Size:** 5 to 7 dynamically selected jurors.
- **Workflow:**
  1. Proposal Intake & Domain Classification.
  2. Dynamic Empanelment of specialized Juror Panel.
  3. Prosecution Opening (The Steelmanned Failure Case).
  4. Defence Opening (The Feasibility & Mitigation Case).
  5. Evidence Examination (Classification into Fact / Assumption / Opinion).
  6. Rebuttal & Cross-Examination exchange.
  7. Parallel, isolated Juror deliberations & ballot submission.
  8. Judicial Synthesis & generation of `.court/VERDICT.md`.

### Mode 2: Speed Trial (`--speed`)
Used for quick, everyday engineering decisions (e.g., small refactors, library swaps, API formatting).
- **Jury Size:** Exactly 3 jurors (1 Minimalist/Pragmatist, 1 Skeptic/Risk Hawk, 1 Domain Specialist).
- **Workflow:**
  1. Intake & Fast Empanelment.
  2. Single-shot dual-column Prosecution vs Defence brief.
  3. Single-shot parallel voting.
  4. Concise ruling rendered directly to markdown.

---

## 3. Empanelment Engine & Juror Pool

Jurors are selected dynamically from `references/jurors.json` using proposal keyword and domain scoring.

### Juror Pool Categories (25+ Roster):
1. **Architecture & Systems:** The Minimalist (anti-overengineering), The Scalability Architect, The Legacy Custodian (day-2 operations).
2. **Security & Governance:** The Adversarial Red-Teamer, The Compliance Officer, The Supply-Chain Hawk.
3. **Operations & SRE:** The 3 AM On-Call SRE, The FinOps / Cost Auditor, The Observability Engineer.
4. **Product & Business:** The Cynical Competitor, The Frugal CFO, The Confused End-User, The Churn Analyst.
5. **Specialized Engineering:** Database Internals Specialist, DX / Frontend Engineer, Embedded / Systems Engineer.

### Mandatory Empanelment Guardrails:
- **The "Tough Skeptic" Mandate:** Every panel must contain at least 2 jurors whose baseline philosophy is antagonistic to the proposal's category (e.g., The Minimalist on a distributed system plan).
- **The "Operator" Mandate:** Every panel must contain at least 1 real-world maintenance or operations persona (e.g., SRE, Junior Dev, CFO).
- **Anti-Homogeneity:** No two jurors with identical primary lenses may sit on the same trial.

---

## 4. Evidentiary Taxonomy & Strict Grounding

Every point raised in the trial must be tagged in the evidentiary ledger:

| Tag | Definition | Evidentiary Standard |
| :--- | :--- | :--- |
| **`[FACT]`** | Verifiable technical truth, verified repo path, or official spec. | Must cite a file path, line number, benchmark, or official documentation URL. |
| **`[ASSUMPTION]`** | Unverified premise or forecast (e.g., *"traffic will 5x"*). | Permitted as a working hypothesis, but tagged as a risk variable. |
| **`[OPINION]`** | Subjective preference or philosophical style (e.g., *"clean code"*). | Permitted, but weighted lower in juror scoring. |

### The Right to Abstain:
If critical facts or architectural parameters are missing, jurors are instructed to vote **`ABSTAIN`** and specify the missing requirement under `information_gap`. If $> 33\%$ of jurors abstain, the trial results in a **MISTRIAL (Insufficient Evidence)**.

---

## 5. Voting Algorithm & Judicial Rules

### Ballot Structure:
Each juror submits a structured JSON ballot:
- `vote`: `"GUILTY"` (proposal rejected), `"NOT GUILTY"` (proposal approved), or `"ABSTAIN"`.
- `confidence`: Integer $1$ to $5$.
- `critical_objections`: List of must-fix blockers.
- `concessions_to_defence`: Valid points acknowledged in the defence.
- `dissenting_view`: Reason for breaking from conventional view.

### Tallying Thresholds:
- **Acquitted (`NOT GUILTY`):** $\ge 60\%$ of non-abstaining jurors vote `NOT GUILTY`.
- **Convicted (`GUILTY`):** $> 40\%$ of non-abstaining jurors vote `GUILTY` (the burden of proof is high).
- **Mistrial:** $> 33\%$ of all jurors vote `ABSTAIN`.

### The Non-Discardable Objections Rule:
The Judge is **strictly prohibited** from omitting or smoothing over any `critical_objection` raised by any juror—even from a lone dissenter. All critical objections must be explicitly enumerated in `VERDICT.md` under **Fatal Flaws & Objections**.

### The Roadmap to Acquittal:
If a proposal is convicted (`GUILTY`), the Judge must outline an actionable, prioritized checklist of conditions that, if fulfilled, would flip the verdict upon retrial.

---

## 6. Case Persistence & Retrial Lifecycle

Trials are preserved locally in the workspace under `.court/`:
```text
.court/
├── registry.json
└── cases/
    └── <case-id>/
        ├── proposal.md
        ├── dossier.json
        ├── ballots/
        │   ├── juror_sre.json
        │   └── juror_cfo.json
        ├── VERDICT.md
        └── retrials/
            └── v2/
```
When invoked with `/court --retrial <case-id>`, the engine reconvenes the **exact same jury panel** to evaluate whether the updated proposal satisfies the previous acquittal checklist.

---

## 7. Delivery Milestones

1. **Milestone 1:** Data Schemas locked down in `schemas/`.
2. **Milestone 2:** Core Juror Pool (10 initial, then 25+) in `references/jurors.json`.
3. **Milestone 3:** Core Engine (`court_engine.py`) and Workflow Orchestrator (`run_trial_workflow.py`).
4. **Milestone 4:** Evidentiary rules and role prompt templates (Prosecution, Defence, Judge).
5. **Milestone 5:** Antigravity `SKILL.md` packaging and end-to-end integration testing.
