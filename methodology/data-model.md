# Normalized Domain Model

## Purpose

The canonical model separates identity, participation, office occupancy, administrations, evidence, measurement, analysis, review and version history. Prose dossiers are views over structured records, not the source of truth.

## Political identity and elections

**Person** is a durable real-world identity. A person may exist without ever being a candidate.

**Election** identifies a particular electoral contest, with election date, office, jurisdiction and relevant electoral cycle metadata.

**Candidacy** is the person's participation in one election. It links exactly one person to one election and stores candidate-specific facts such as party, ballot status, nomination status and result references. A person can have many candidacies; an election has many candidacies.

`person_id -> candidacy -> election_id`

Candidate dossiers should therefore not be the primary identity table.

## Offices, officeholdings and administrations

**Office** is the institutional position (for example, President of Nigeria), independent of its occupant.

**OfficeHolding** records one person's occupancy of an office over a defined interval, with start/end dates and evidence. It is the authoritative temporal relationship for questions such as who held an office on a given date.

**Administration** is an analytical/governance period, not a person. It may be associated with one or more officeholdings and has explicit start/end boundaries plus a methodology note explaining the boundary rule.

`person -> office_holding -> office`

`administration -> office_holding(s)`

Economic performance can be compared against an administration's defined period, but attribution must remain a separate analytical claim.

## Claims and evidence

A **Claim** is a proposition. It may be a factual proposition, allegation, statement, analysis, estimate, opinion or disputed proposition.

An **Evidence** record describes exactly how a source relates to a claim. Evidence has a typed relationship; `supports` alone is intentionally insufficient.

A **Source** is the bibliographic/provenance object. A source may contain multiple relevant evidence items and may relate to multiple claims.

## Quantitative layer

**Metric** defines what is being measured. **Observation** stores a value for a metric, period and scope. **Calculation** defines a reproducible transformation of observations. **Analysis** interprets calculations or observations. **Result** is a versioned derived output that records its dependencies.

## Versioning

Material domain records are immutable versions. A correction creates a new version linked to its predecessor. Git commits provide repository history; domain versions provide record-level history. Both are retained.

## Design rule

No entity should contain another entity's mutable history merely for convenience. Relationships should carry their own temporal/provenance semantics where appropriate.
