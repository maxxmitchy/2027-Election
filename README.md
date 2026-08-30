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
- `tests/` — automated/property-testing acceptance criteria and future executable test suites.
- `candidates/` — candidate-facing views built from structured evidence.
- `administrations/` — administration periods and governance analysis.
- `economy/` — indicators, observations, prices, inflation, exchange rates, debt and other measurable series.
- `events/` — dated historical events.
- `sources/` — source metadata and archival references.
- `evidence/` — structured claim/evidence records.
- `reviews/` — independent reviews, separate from evidence.
- `datasets/` — imported or curated datasets.

## Status

**Foundation / integrity-hardening phase.** Round 4 has specified implementation-level controls but has not claimed runtime production readiness. The research gate remains closed pending independent review and execution of the database/CI enforcement layer.
