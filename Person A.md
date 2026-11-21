# 🛠️ Person A: Systems Architect & Engine Developer

## Role Overview
You own the **technical execution engine**, **subagent concurrency**, **state persistence**, and **Antigravity CLI integration**. Your job is to make sure the trial runs smoothly, isolated subagents are properly spawned, ballots are tallied accurately, and case histories are preserved.

---

## 🎯 Primary Files Owned

1. `court_engine.py` (Core Python Trial Engine & State Machine)
2. `scripts/run_trial_workflow.py` (Antigravity `run_workflow` subagent orchestrator)
3. `SKILL.md` (Antigravity skill declaration & CLI router)
4. `schemas/ballot_schema.json` & `schemas/dossier_schema.json` (Interface schemas)

---

## 📋 Step-by-Step Task Checklist

### Phase 1: Schemas & Foundation
- [ ] **Define JSON Schemas:**
  - Create `schemas/dossier_schema.json` to define what the Prosecution, Defence, and Evidence payload looks like.
  - Create `schemas/ballot_schema.json` to enforce the exact structure of juror responses (`vote`, `confidence`, `critical_objections`, `concessions`, `dissent`).
- [ ] **Scaffold `court_engine.py`:**
  - Implement case ID generation: `YYYY-MM-DD_<slugified-title>`.
  - Implement directory setup: `.court/cases/<case-id>/ballots/`.

### Phase 2: Dynamic Juror Empanelment
- [ ] **Build the Empanelment Algorithm in `court_engine.py`:**
  - Load `references/jurors.json` (created by Person B).
  - Implement a domain/keyword scoring function to rank relevance against the proposal text.
  - Enforce the **Tough Skeptic Rule** (at least 2 adversarial personas).
  - Enforce the **Operator Rule** (at least 1 ops/maintenance persona).
  - Output a panel of 5–7 jurors (Full Grand Jury) or 3 jurors (Speed Trial).

### Phase 3: Subagent Isolation & Workflow Engine
- [ ] **Implement `scripts/run_trial_workflow.py`:**
  - Use Antigravity's dynamic workflow primitives: `from run_workflow import agent, parallel, phase`.
  - Implement parallel juror deliberation:
    ```python
    # Example snippet
    async def deliberate_fn(juror):
        prompt = build_juror_prompt(juror, dossier)
        return await agent(prompt=prompt, schema=BALLOT_SCHEMA, role=juror["name"])
    
    ballots = await parallel(empanelled_jurors, deliberate_fn)
    ```
  - Ensure juror subagents receive **only** the compiled trial dossier—zero access to other jurors' intermediate deliberations.
  - Implement a clean **Sequential Fallback mode** in case dynamic workflows cannot run, adding the required `[SIMULATION NOTICE]` header.

### Phase 4: Ballot Box & Judicial Tallying
- [ ] **Build Ballot Aggregator & Vote Tally in `court_engine.py`:**
  - Parse and validate all juror ballots against `ballot_schema.json`.
  - Calculate tally: `Not Guilty` percentage vs `Guilty` vs `Abstain`.
  - Apply thresholds: $\ge 60\%$ Acquittal, $> 40\%$ Convicted, $> 33\%$ Mistrial.
  - Aggregate all `critical_objections` without deduplication or dismissal.

### Phase 5: Antigravity Skill Definition (`SKILL.md`)
- [ ] **Author `SKILL.md`:**
  - Create standard YAML frontmatter with `name: court` and clear activation descriptions.
  - Route `/court <proposal>`, `/court --speed <proposal>`, and `/court --retrial <case-id>`.

---

## 🤝 Integration Contract with Person B

- **Person B provides:** `references/jurors.json`, `references/evidence_rules.md`, and prompt templates in `references/templates/`.
- **You consume:** `jurors.json` in your empanelment algorithm and the prompt templates in your workflow runner.
- **You provide Person B:** The validated JSON schemas (`schemas/ballot_schema.json` and `schemas/dossier_schema.json`) so Person B can write prompts that match your parser.

---

## 🧪 Testing Your Work
1. **Empanelment Test:** Run `python court_engine.py --test-empanel "Migrate Postgres to DynamoDB"` and verify that at least one DB specialist, one SRE, and one minimalist are selected.
2. **Workflow Test:** Run a mock parallel deliberation with 3 jurors and verify that 3 valid JSON ballots are saved to disk.
3. **Tally Test:** Feed mock ballots with 4 Guilty / 3 Not Guilty and confirm a `GUILTY` outcome with all 4 objections preserved.
