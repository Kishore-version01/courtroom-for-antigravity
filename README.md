# ⚖️ The Courtroom Skill

> **Adversarial stress-testing and grand jury deliberation for software architectures, technical proposals, refactors, and product decisions.**

---

## 🏛️ What is Courtroom?

Most AI coding assistants suffer from **"yes-man" confirmation bias**: whenever you propose a stack choice, architecture design, or risky refactor, the AI almost always replies:
> *"That sounds like a great idea! Here is how to do it."*

This leads to catastrophic technical debt, ignored failure modes, unbudgeted infrastructure costs, and security vulnerabilities discovered too late.

The **Courtroom Skill** eliminates this bias by putting your proposal **on trial**. It convenes an adversarial courtroom where:
- **The Prosecution** ruthlessly builds the steelmanned case for failure, uncovering hidden operational costs, edge cases, attack vectors, and maintenance debt.
- **The Defence** builds the steelmanned counter-case, validating feasibility, realistic mitigations, and execution paths.
- **An Adaptive Jury** of 5–12 specialized expert personas evaluates the record in **genuinely isolated context windows** and casts independent, blind votes (`GUILTY` / `NOT GUILTY` / `ABSTAIN`).
- **The Presiding Judge** synthesizes the verdict into `.court/VERDICT.md`, strictly cataloging all non-negotiable critical objections and generating an actionable **Roadmap to Acquittal**.

---

## ⚡ Key Highlights

- **Adaptive Juror Empanelment:** Automatically selects relevant jurors from a 25+ expert roster based on proposal domain (e.g., SRE, Security Red-Teamer, Frugal CFO, Scalability Architect, Minimalist).
- **Dual Trial Depths:**
  - **Full Grand Jury:** Complete adversarial cycle with openings, evidentiary examinations, cross-rebuttals, blind voting, and comprehensive verdict.
  - **Speed Trial (`--speed`):** Rapid 3-juror single-turn pressure test for smaller everyday decisions.
- **Strict Context Isolation:** Jurors evaluate the trial dossier independently without seeing peer evaluations, preventing groupthink and anchoring bias.
- **Evidentiary Integrity:** Strict taxonomic separation of **[FACT]**, **[ASSUMPTION]**, and **[OPINION]**. Zero tolerance for hallucinated benchmarks or fabricated citations.
- **Preserved Minority Dissent:** The Judge is forbidden from discarding critical objections. Any objection raised by even a single juror is preserved in the final verdict.
- **Case History & Retrials:** Retains trials under `.court/cases/<case-id>/`. Allows retrial when new evidence or mitigations are provided (`/court --retrial <case-id>`).

---

## 📂 Project Structure

```text
skill/
├── README.md                      # Project overview (this file)
├── PROJECT.md                     # Comprehensive architecture and system specification
├── Person A.md                    # Work breakdown & instructions for Person A (Systems Architect)
├── Person B.md                    # Work breakdown & instructions for Person B (Adversarial Designer)
├── agent.md                       # Guidelines and constraints for AI agents developing this repo
├── .gitignore                     # Git ignore rules
│
├── SKILL.md                       # Antigravity skill manifest & command router (/court)
├── court_engine.py                # Core Python state machine, empanelment, and ballot tallying
│
├── scripts/
│   └── run_trial_workflow.py      # Subagent orchestration engine (parallel execution & isolation)
│
├── schemas/
│   ├── juror_schema.json          # JSON Schema for juror persona definitions
│   ├── ballot_schema.json         # JSON Schema for juror vote ballots
│   └── dossier_schema.json        # JSON Schema for compiled trial dossiers
│
└── references/
    ├── jurors.json                # Roster of 25+ specialized juror personas
    ├── evidence_rules.md          # Evidentiary standard and claim taxonomy
    └── templates/
        ├── trial_dossier.md       # Template for compiled prosecution/defence briefs
        └── verdict_template.md    # Template for generating .court/VERDICT.md
```

---

## 👥 Collaborative Team Split

This project is partitioned into two modular, parallel streams:

| Role | Owner | Focus Area | Key Files |
| :--- | :--- | :--- | :--- |
| **Person A** | Systems Architect | Orchestration, state machine, subagent concurrency, CLI. | `court_engine.py`, `scripts/run_trial_workflow.py`, `SKILL.md` |
| **Person B** | Adversarial Designer | Personas, evidentiary law, prompt engineering, reporting. | `references/jurors.json`, `references/evidence_rules.md`, templates |

*Read [Person A.md](file:///c:/Programs/skill/Person%20A.md) and [Person B.md](file:///c:/Programs/skill/Person%20B.md) for detailed task lists and step-by-step guides.*

---

## 🚀 Quick Usage (Once Installed)

```bash
# Run a Full Grand Jury trial on a proposal
/court Migrate our Postgres monolith to DynamoDB and Lambda microservices

# Run a quick Speed Trial on a smaller decision
/court --speed Replace Axios with native fetch in our frontend client

# Retrial a previously convicted proposal with new evidence
/court --retrial 2026-11-21_dynamodb-migration
```
