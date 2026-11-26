# Integration Contract: Person A ↔ Person B (Phase 2)

> **Status:** Active (`1.0.0`)  
> **Schemas:** `schemas/ballot_schema.json`, `schemas/dossier_schema.json`  
> **Validator Module:** `schema_validator.py`

---

## 1. Juror Response Format (`ballot_schema.json`)

When a juror agent is instructed to cast a ballot, its output **must** be raw, valid JSON conforming strictly to `schemas/ballot_schema.json` (JSON Schema Draft 2020-12).

### Exact Required Structure

```json
{
  "vote": "NOT_GUILTY",
  "confidence": 78,
  "critical_objections": [
    "The migration plan lacks a rollback strategy."
  ],
  "concessions": [
    "The proposed database may reduce operational overhead."
  ],
  "dissent": "The benefits may outweigh the migration risks if rollback protections are implemented."
}
```

### Strict Rules for Prompt Templates
1. **No Markdown code fences** (` ```json ... ``` `) and **no surrounding commentary**.
2. **Exact `vote` values (case-sensitive):** `"GUILTY"`, `"NOT_GUILTY"`, or `"ABSTAIN"`.
   - Do **not** use `"NOT GUILTY"` (with a space), `"APPROVE"`, `"REJECT"`, or lowercase variants.
3. **`confidence`:** Integer `0`–`100` inclusive (no floats like `85.5`).
4. **`critical_objections`:** Array of non-empty strings (`[]` allowed). Every objection is preserved verbatim without deduplication or dismissal.
5. **`concessions`:** Array of non-empty strings (`[]` allowed).
6. **`dissent`:** String (`""` allowed).
7. **No extra properties (`additionalProperties: false`):** Do **not** include `juror_id`, `juror_name`, `timestamp`, `case_id`, or `information_gap` inside the ballot JSON. The engine stores juror identity and execution metadata separately.

---

## 2. Trial Dossier Contract (`dossier_schema.json`)

The dossier is the frozen, domain-agnostic record delivered to every isolated juror agent.

### Top-Level Required Fields

| Field | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `schema_version` | `string` | Yes | Must be `"1.0.0"` (SemVer). |
| `case` | `object` | Yes | `case_id` (str), `title` (str), `proposal` (str), optional `created_at` (ISO 8601 date-time with timezone). |
| `prosecution` | `object` | Yes | `summary` (str) and `arguments` (array of `{id, claim, tag, evidence_refs?}`). |
| `defence` | `object` | Yes | `summary` (str) and `arguments` (array of `{id, claim, tag, evidence_refs?}`). |
| `evidence` | `array` | Yes | Array of `{evidence_id, title, content, source, evidence_type, metadata?}`. |
| `constraints` | `array` | Yes | Array of `{id, category, description}`. |
| `assumptions` | `array` | Yes | Array of `{id, statement, risk_note?}`. |
| `context` | `array` | Yes | Array of `{id, topic, detail}`. |

### Argument & Evidence Rules
- Each argument's `tag` must be one of `"FACT"`, `"ASSUMPTION"`, or `"OPINION"`.
- Empty arrays (`[]`) are valid for `arguments`, `evidence`, `constraints`, `assumptions`, and `context`—do **not** omit the key or substitute `null` or `"none"`.
- `additionalProperties: false` is enforced across all dossier objects.

---

## 3. Schema Versioning Strategy (`MAJOR.MINOR.PATCH`)

- **MAJOR (`X.0.0`):** Breaking changes (removing required fields, changing field types, changing `vote` enum values, restructuring required objects).
- **MINOR (`1.X.0`):** Backward-compatible additions (adding optional fields or optional metadata).
- **PATCH (`1.0.X`):** Non-structural clarifications (descriptions, documentation improvements).

Person A will never introduce a breaking schema change without coordinating with Person B and bumping the `MAJOR` version.
