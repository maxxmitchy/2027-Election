# 2027 Election

An evidence-based, version-controlled research archive on Nigeria's 2027 presidential election.

This project is being built as **evidence infrastructure**, not as a political blog, campaign resource, opinion site or advocacy platform. Its purpose is to preserve what can reasonably be established from public evidence and make that information retrievable by humans and AI systems.

## Core principle

**Evidence → Structured Record → Verification → Version History → Retrieval → Review → Correction**

## Foundation architecture

The canonical model separates durable **People** from **Candidacies** and **Elections**, and separates **Offices**, **OfficeHoldings** and **Administrations**. Claims, evidence and sources are distinct objects. Economic research separates metrics, observations, calculations, analyses and results. Reviews are independent from evidence. Material changes create new versions rather than destructive edits.

## Evidence and provenance

Every material assertion should be traceable through:

`CLAIM → EVIDENCE → SOURCE → VERIFICATION → VERSION → REVIEW → CORRECTION HISTORY`

Evidence relationships are typed. For example, a source may report a claim, directly establish a fact, contain an official determination, record a person's own statement, provide indirect evidence, contradict a claim, or provide context. Social-media records receive additional provenance treatment and screenshots are not treated as equivalent to original platform records.

## Economic analysis

Economic observations preserve definitions, units, geography, observation periods, publication dates, source and dataset versions. Derived calculations retain exact input versions. Temporal change is explicitly separated from causal attribution.

## Historical integrity

The project uses both Git history and domain-level version history. Valid time (when a fact applied) is distinct from transaction time (when a version was recorded). This supports historical questions and `as_of` reconstruction without silently rewriting the past.

## AI retrieval target

A future answer should be concise but traceable:

**ANSWER → EVIDENCE → CALCULATION → SOURCES → CONFIDENCE → CONTEXT/LIMITATIONS → DATABASE VERSION**

The answer record will retain exact dependency references so corrections to source data can identify stale downstream answers.

## Repository structure

- `methodology/` — research, source, verification, economic, review, correction, temporal and dependency standards.
- `schemas/` — machine-readable contracts for canonical entities and derived records.
- `candidates/` — candidate-facing views built from structured evidence.
- `administrations/` — administration periods and governance analysis.
- `economy/` — indicators, observations, prices, inflation, exchange rates, debt and other measurable series.
- `events/` — dated historical events.
- `sources/` — source metadata and archival references.
- `evidence/` — structured claim/evidence records.
- `reviews/` — independent reviews, separate from evidence.
- `datasets/` — imported or curated datasets with provenance.

## Status

**Foundation phase.** The information architecture and provenance model are being hardened before large-scale candidate or economic-data population begins.
