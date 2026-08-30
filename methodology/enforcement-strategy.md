# Schema, API, Database and Workflow Enforcement

JSON Schema is the structural contract. It should not be expected to enforce cross-record facts such as foreign-key existence, interval overlap or dependency invalidation. JSON Schema 2020-12 supports structural assertions and conditional schemas, while cross-record semantics belong in the application/database layer. See the official specification: https://json-schema.org/specification.

## JSON Schema

Enforce required fields, types, enums, ranges, array cardinality, URI/date syntax and local conditional structure.

## API/application

Enforce foreign-reference existence, immutable version creation, predecessor correctness, bitemporal query semantics, candidacy status transitions, dependency propagation, geographic compatibility, calculation input resolution and AI-answer dependency completeness.

## Database

Use primary keys, unique constraints, foreign keys, check constraints, exclusion/range constraints where supported, indexes for dependency traversal and transactional controls preventing destructive updates. Version rows should be append-only from the application's perspective.

## Workflow/review

Use review gates for source quality, evidence semantics, corrections, methodology changes, disputed claims and publication of AI answers. A workflow decision is never itself evidence of factual truth.

## CI

Before production population, repository CI should validate every schema against the JSON Schema 2020-12 meta-schema, validate fixture records, detect broken local `$ref` targets, and run domain-level invariant tests. Production ingestion should fail closed when required provenance or dependency references cannot be resolved.
