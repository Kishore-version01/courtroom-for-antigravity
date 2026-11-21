# ⚖️ Person B: Adversarial Designer & Juror Master

## Role Overview
You own the **legal and adversarial intelligence of the court**. Your job is to make sure the AI never acts as a yes-man, the prosecution is genuinely relentless, the defence is realistic, the 25+ juror personas have distinct philosophical lenses, evidentiary standards are strictly enforced, and the resulting `VERDICT.md` provides clear value.

---

## 🎯 Primary Files Owned

1. `references/jurors.json` (The 25+ specialized juror personas roster)
2. `references/evidence_rules.md` (Rules of evidence, fact vs assumption vs opinion)
3. `references/templates/verdict_template.md` (Markdown blueprint for `.court/VERDICT.md`)
4. `references/templates/trial_dossier.md` (Structure for opening arguments & cross-examinations)
5. `schemas/juror_schema.json` (Specification for juror attributes)

---

## 📋 Step-by-Step Task Checklist

### Phase 1: Juror Persona Roster (`references/jurors.json`)
- [ ] **Define the 25+ Juror Pool across 5 domains:**
  1. **Architecture & Systems:**
     - *The Minimalist:* Fanatical about YAGNI, complexity budgets, and simple boring tech.
     - *The Scalability Architect:* Focused on concurrency bottlenecks, lock contention, horizontal scaling limits.
     - *The Legacy Custodian:* Focused on day-2 operational maintenance, tech debt, documentation, and deprecation pain.
  2. **Security & Governance:**
     - *The Adversarial Red-Teamer:* Hunts for auth bypass, injection, data leakage, and supply-chain blast radiuses.
     - *The Compliance & Privacy Officer:* Focuses on GDPR, SOC2, encryption at rest/transit, auditability.
     - *The Dependency Hawk:* Attacked by third-party risks, vendor lock-in, unmaintained open-source packages.
  3. **Operations & Reliability:**
     - *The 3 AM On-Call SRE:* Thinks solely about observability, graceful degradation, alert storms, failure recovery.
     - *The FinOps Auditor:* Scrutinizes cloud costs, data transfer bills, compute unit economics, idle capacity.
  4. **Product & Business:**
     - *The Cynical Competitor:* Asks why an existing open-source tool or competitor doesn't already make this obsolete.
     - *The Frugal CFO:* Demands proof of ROI, runway preservation, and opportunity cost evaluation.
     - *The Confused First-Time User:* Tests cognitive load, onboarding friction, and API usability.
  5. **Specialized Engineering:**
     - *Database Internals Specialist:* Indexes, ACID vs BASE, connection pooling, write-amplification.
     - *DX / Frontend Specialist:* Bundle size, developer ergonomic friction, hot-reload speeds.
- [ ] For each persona, define:
  - `id`, `name`, `category`, `description`
  - `philosophical_bias` (what they instinctively hate or love)
  - `fatal_flaw_triggers` (what triggers an automatic `GUILTY` vote)
  - `remedy_requirements` (what evidence flips them to `NOT GUILTY`)

### Phase 2: Evidentiary Law & Anti-Hallucination (`evidence_rules.md`)
- [ ] **Establish Strict Claim Classification:**
  - Create definitions and examples for `[FACT]`, `[ASSUMPTION]`, and `[OPINION]`.
  - Enforce the **Grounding Mandate:** Any claim stating performance numbers, API features, or library capabilities must cite an empirical source (local repo path, official spec, or verified benchmark). No invented benchmarks.
- [ ] **Formulate Abstention Directives:**
  - Guide jurors on when to invoke their **Right to Abstain**. If critical sizing, traffic, or security params are missing, they must vote `ABSTAIN` rather than guessing.

### Phase 3: Adversarial Prompts & Templates
- [ ] **The Prosecution Prompt Template:**
  - Teach the prosecutor persona to avoid petty nitpicks and instead target structural failure modes, operational risks, hidden costs, and unconsidered edge cases.
- [ ] **The Defence Prompt Template:**
  - Teach the defence to steelman the proposal, ground the benefits in reality, acknowledge trade-offs honestly, and offer concrete mitigations.
- [ ] **The Judicial Synthesis Template (`verdict_template.md`):**
  - Ensure the template enforces the **Non-Discardable Objections Rule**.
  - Structure the **Roadmap to Acquittal** so the user receives a direct checklist of tasks to fix.

### Phase 4: Test Suite & Trial Benchmarks
- [ ] **Craft 3 Benchmark Test Proposals:**
  1. *Test Case 1 (Should Pass):* A sane, well-mitigated refactor (e.g., adding an index and connection pooler to solve slow queries).
  2. *Test Case 2 (Should Fail):* An over-engineered resume-driven architecture (e.g., migrating an internal 50-user admin panel to microservices and Kafka).
  3. *Test Case 3 (Should Mistrial):* An underspecified proposal with missing technical criteria (e.g., "rewrite the backend in Go to make it fast").

---

## 🤝 Integration Contract with Person A

- **You consume:** `schemas/ballot_schema.json` and `schemas/dossier_schema.json` from Person A.
- **You provide Person A:** `references/jurors.json` (so Person A's empanelment engine can filter it) and the prompt templates in `references/templates/`.
- Ensure your juror JSON strictly follows `schemas/juror_schema.json`.

---

## 🧪 Testing Your Work
1. Read through the prompts and personas: do they feel genuinely distinct? Would two jurors give completely different reasons for voting against the same proposal?
2. Run your benchmark cases through the prompt templates and confirm that Test Case 2 gets aggressively convicted and Test Case 3 triggers abstentions.
