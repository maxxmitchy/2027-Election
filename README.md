# 2027 Election

An evidence-based, version-controlled research archive on Nigeria's 2027 presidential election.

This project is being built as **evidence infrastructure**, not as a political blog, campaign resource, opinion site or advocacy platform. Its purpose is to preserve what can reasonably be established from public evidence and make that information retrievable by humans and AI systems.

## Core principle

**Evidence → Structured Record → Verification → Version History → Retrieval → Review → Correction**

## Foundation architecture

The canonical model separates durable **People** from **Candidacies** and **Elections**, and separates **Offices**, **OfficeHoldings** and **Administrations**. Claims, evidence and sources are distinct objects. Economic research separates metrics, observations, calculations, analyses and results. Reviews are independent from evidence. Material changes create new versions rather than destructive edits.

## Integrity architecture

Round 4 establishes implementation-level contracts for bitemporal history, append-only versions, selective dependency invalidation, dataset revisions, cryptographic provenance metadata and automated invariant testing. All temporal intervals use `[start,end)` semantics; transaction time is distinct from valid time.

## Evidence and provenance

Every material assertion should be traceable through:

`CLAIM → EVIDENCE → SOURCE → RETRIEVAL → VERSION → REVIEW → CORRECTION HISTORY`

Evidence relationships are typed. Social-media records and archived artifacts retain provenance metadata. Cryptographic hashes can be verified later without redesigning the domain model.

## Controlled source-ingestion experiment

Gate 3 has now exercised the model against real public artifacts: an official NBS CPI publication, the NBS CPI dataset catalog, a Reuters report, a Proshare X statement, a CBN homepage snapshot and an independent Premium Times report. The experiment preserves source/retrieval metadata, hashes, typed evidence relationships, contradiction, correction, source revision and retrieval failure states.

The experiment is **not candidate research**. Candidate dossiers and political research remain prohibited until Gate 4.

## Economic analysis

Economic observations preserve definitions, units, geography, observation periods, publication dates, source and dataset versions. Derived calculations retain exact input versions. Temporal change is explicitly separated from causal attribution.

## Historical integrity

Valid time answers when a represented fact applied. Transaction time answers when the database recorded or knew a version. Bitemporal reconstruction first selects the transaction-visible snapshot and then evaluates valid time within that snapshot.

## AI retrieval target

A future answer should be concise but traceable:

**ANSWER → EVIDENCE → CALCULATION → SOURCES → CONFIDENCE → CONTEXT/LIMITATIONS → DATABASE SNAPSHOT**

The answer record retains exact dependency versions so corrections to source data can identify stale downstream answers while preserving historical answers for reconstruction.

## Repository structure

- `methodology/` — research, source, verification, economic, review, correction, temporal, dependency and integrity standards.
- `schemas/` — machine-readable contracts for canonical entities and derived records.
- `tests/` — automated/property-testing acceptance criteria and executable integrity/ingestion tests.
- `candidates/` — candidate-facing views; not populated during the foundation/ingestion gates.
- `administrations/` — administration periods and governance analysis; not populated during the foundation/ingestion gates.
- `economy/` — indicators, observations, prices, inflation, exchange rates, debt and other measurable series.
- `events/` — dated historical events.
- `sources/` — source metadata and archival references.
- `evidence/` — structured claim/evidence records.
- `reviews/` — independent reviews, separate from evidence.
- `datasets/` — imported or curated datasets.

## Gate status

**GATE 2 — OPEN WITH DOCUMENTED EVIDENCE QUALIFICATION.** The independent Reviewer accepted accumulated runtime evidence while explicitly recording that commit `1c1dbc14dafd4b27e80aeaf86e496a23ae86d784` does **not** have a clean CI execution. The project does not claim otherwise.

**GATE 3 — CONTROLLED SOURCE INGESTION PASS (recommended).** The ingestion validator executed successfully against commit `b26cccd58b9e6ea1c8e28ecbdd8affe5ea162328` in GitHub Actions run `33319986354`, job `99280145039`, with 7/7 tests passing and evidence artifact `9734598011` uploaded.

This Gate 3 result authorizes only controlled ingestion experiments. It does **not** authorize candidate research. Candidate research remains gated behind Gate 4.
