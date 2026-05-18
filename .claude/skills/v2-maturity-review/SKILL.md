---
name: v2-maturity-review
description: Review V2 controllable-flux motor deliverables for maturity wording, production-drawing boundaries, and validation evidence claims.
---

# V2 Maturity Review

Use this skill when reviewing or updating V2 controllable-flux motor scheme documents, image prompts, simulation coverage, or Codex/Claude review packages.

## Review scope

Check these paths when relevant:

- `engineering/v2/**`
- `models/scheme_simulation_coverage.json`
- `models/*lut*.json`
- `models/*schema*.json`
- `claude-review/docs/**`
- `codex-review/docs/**`
- `wiki/**`
- `gpt-image-2/**`

## Required maturity boundaries

Do not allow concept artifacts to be described as production release artifacts.

Required global posture unless true evidence exists:

```json
{
  "engineering_validated": false,
  "production_drawing_ready": false,
  "manufacturing_release_ready": false
}
```

Acceptable artifact terms:

- `concept_drawing`
- `parameter_sheet`
- `source_design_file` only when actual CAD/EDA/source design files exist
- `simulation_input`
- `manufacturing_release` only with manufacturing release evidence

Disallowed without evidence:

- production-ready drawing
- true production drawing
- engineering validated
- manufacturing release ready
- bench validated
- FEA validated
- HIL validated
- safety certified

## Scheme-specific checks

### S02

- `60 A` is only an `r02_proxy_soft_gate_a`.
- `30 A` is the `r03_production_target_a`.
- Do not claim 60 A jump thresholds as production acceptance.

### S04

- `models/flux_lut_sample.json` is a `synthetic_fixture`.
- It only proves schema/runtime smoke binding.
- It is not FEA-derived flux validation.

### Image generation

- PNGs, prompts, and image sidecars are concept illustrations.
- Prompts must require redaction and approval before external upload.
- `gpt-image-2/config/model.json` must not contain real endpoint or API key.
- `gpt-image-2/config/model.local.json` must remain untracked.

## Output format

Return:

1. `PASS` or `FAIL`
2. Blocking issues with `file_path:line_number`
3. Non-blocking wording improvements
4. Required tests or docs to update
