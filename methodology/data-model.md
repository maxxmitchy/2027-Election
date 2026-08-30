# Information Architecture and Core Data Model

## Design principle

Separate entities, claims, evidence, sources, observations, analyses, reviews and versions. Prose is a presentation layer, not the canonical knowledge model.

## Core entities

- **Person/Candidate** — identity and candidate-specific attributes.
- **Administration** — office holder with explicit start/end dates.
- **Office/Party** — reusable political entities.
- **Event** — dated historical event with participants and evidence.
- **Claim** — proposition whose status can be evaluated.
- **Source** — bibliographic/provenance record for an external source.
- **Evidence** — specific support or contradiction relationship between a source and claim.
- **Economic Observation** — measured value for a defined metric and period.
- **Analysis** — reproducible transformation or comparison of observations.
- **Review** — public/internal assessment of a claim, answer or evidence record.
- **Version** — immutable domain-level state transition.

## Relationships

`subject -> claim -> evidence -> source`

`metric -> observation -> source`

`analysis -> observations -> calculation -> result`

`record -> version -> predecessor/successor`

`answer -> claims/observations -> sources -> database version`

## Separation of concerns

A source is not itself a claim. Evidence describes what a source contributes to a claim. A statement by a candidate is evidence that the candidate made the statement; it does not automatically validate the statement's underlying content. A review is feedback about a record and does not become evidence merely because it exists.
