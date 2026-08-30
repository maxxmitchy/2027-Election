# Phase 5 — Research Workbench Methodology

Version: `phase5-research-workbench-v1`

Phase 5 converts a serious natural-language research question into an explicit, auditable investigation plan. It is an extension of the existing deterministic evidence infrastructure, not a replacement factual engine.

## Boundary

Natural language may be interpreted deterministically. Evidence, source classification, temporal semantics, calculations, provenance and answerability remain evidence-system responsibilities. No truth probability is produced.

## Lifecycle

`DRAFT → SCOPED → DECOMPOSED → EVIDENCE_REQUIRED → RESEARCHING → PRIMARY_VERIFICATION → CONTRADICTION_REVIEW → QUANTITATIVE_REVIEW → CAUSAL_REVIEW → READY_FOR_REVIEW → REVIEWED → ANSWERABLE / PARTIALLY_ANSWERABLE / BLOCKED → CLOSED`

## Discovery versus verification

A source discovered by search is not automatically evidence. The workbench records retrieved sources separately from verified evidence. Primary-source classification is explicit and never inferred from citation prominence.

## Gaps

Known unknowns and not-yet-investigated questions are distinct. Missing primary sources, unavailable artifacts, unresolved contradictions and incomplete quantitative inputs become explicit research gaps and can generate tasks.

## Domain safeguards

Policy states remain distinct from outcomes; legal allegations remain distinct from findings; election nomination remains distinct from results; public statements establish statement occurrence, not proposition truth; temporal association does not establish causation; quantitative records retain metric, unit, geography, period and dataset/version identity.

## Review boundary

The system may require human review but may not silently mark a claim reviewed. Review is not evidence.

## Candidate scope

Only `bola-ahmed-tinubu`, `peter-gregory-obi`, and `atiku-abubakar` are permitted. Candidate 4 remains blocked. Candidate-specific research logic is prohibited.

## Reproducibility

Every investigation records question, interpretation version, methodology version, candidate scope, as-of value, database snapshot, generation timestamp, source references, requirements, gaps, tasks and answerability state. A PASS status requires actual CI execution against the exact tested SHA.
