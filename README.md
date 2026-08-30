# 2027 Election

An evidence-based, version-controlled research archive on Nigeria's 2027 presidential election.

This project is being built as **evidence infrastructure**, not as a political blog, campaign resource, opinion site or advocacy platform. Its purpose is to preserve what can reasonably be established from public evidence and make that information retrievable by humans and AI systems.

## Core principle

**Evidence → Structured Record → Verification → Version History → Retrieval → Review → Correction**

## Editorial standards

- Evidence before assertion.
- Primary sources before secondary sources whenever available.
- Facts, allegations, statements, analysis, estimates and opinions are explicitly distinguished.
- Important claims are corroborated where practical.
- Contradictory evidence is preserved rather than hidden.
- Historical information is not presented as current without verification.
- Important numerical claims carry provenance and reproducible calculations.
- Temporal change is distinguished from causal attribution.
- Corrections create a historical trail rather than silently rewriting records.
- Community reviews supplement evidence but never substitute for it.
- Uncertainty is represented honestly.

## Architecture

```text
PUBLIC SOURCES → RESEARCH → EVIDENCE LEDGER → VERSION-CONTROLLED RECORDS
→ STRUCTURED DATABASE → API / AI RETRIEVAL → CLEAN ANSWER → PUBLIC REVIEW
→ CORRECTION / NEW VERSION ↺
```

GitHub is the canonical research and provenance layer. The eventual database is the retrieval layer. The model is deliberately database-agnostic.

## Repository structure

- `methodology/` — research, source, verification, economic, review and correction standards.
- `schemas/` — machine-readable data contracts.
- `candidates/` — candidate dossiers built from evidence records.
- `administrations/` — administration-level records and timelines.
- `economy/` — indicators, prices, inflation, exchange rates, debt and other measurable series.
- `events/` — dated political and historical events.
- `sources/` — source metadata and archival references.
- `evidence/` — structured claim/evidence records.
- `reviews/` — public and internal reviews, kept separate from evidence.
- `datasets/` — imported or curated datasets with provenance.

## AI retrieval target

A future answer should be concise but traceable:

**ANSWER → EVIDENCE → CALCULATION → SOURCES → CONFIDENCE → CONTEXT/LIMITATIONS → DATABASE VERSION**

Historical retrieval must support an `as_of` concept so the system can reconstruct what the database said at a particular time.

## Status

**Foundation phase.** Information architecture, provenance rules and initial schemas are established. Candidate population and economic datasets have not yet begun.
