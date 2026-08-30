# Round 5 Threat Model

## Accidental corruption

Examples: malformed import, wrong version number, duplicate identity, bad interval, accidental delete.
Controls: JSON Schema, foreign keys, unique/check constraints, exclusion constraints, append-only triggers, CI fixtures.

## Malicious tampering

Examples: direct database UPDATE/DELETE, dependency substitution, historical answer mutation.
Controls: database immutability triggers, least-privilege roles in deployment, immutable provenance, Git history, audit findings. Authentication/authorization hardening is not fully implemented in the reference build.

## Source error

Examples: publisher revises a statistic, methodology changes, document disappears.
Controls: dataset versions, observation versions, retrieval events, hashes, corrections, stale propagation; historical source records remain retained.

## Researcher error

Examples: wrong source relationship, incompatible geography comparison, invalid status transition.
Controls: typed evidence relationships, database/API validation, review workflow, CI fixtures.

## Model error

Examples: wrong formula, incomplete dependency graph, stale answer presented as current.
Controls: exact methodology references, calculation lineage, AI dependency graph, stale propagation, reproducibility tests.

## Pipeline error

Examples: partial ingestion, skipped version, broken reference, graph traversal failure.
Controls: FK closure, version-chain checks, property tests, non-zero CI failures, machine-readable integrity findings.

## Out of scope for Round 5

Network perimeter security, credential management, production role design, encrypted backups, disaster recovery, hostile GitHub-account compromise, and external archive availability are not solved here. They require later operational/security reviews.
