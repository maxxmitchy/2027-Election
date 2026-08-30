# Temporal and Version Semantics

## Temporal validity

A record may have both **valid time** (when the represented fact was true/applicable) and **transaction time** (when the repository/database recorded the version). They are not interchangeable.

Use `valid_from` and nullable `valid_until` for open-ended intervals. A claim may have multiple validity intervals when the same proposition becomes true, false, and true again. Each interval is represented explicitly or through separate versioned validity records; do not encode repeated intervals as one ambiguous range.

## Example

For office occupancy, `OfficeHolding.valid_from` and `valid_until` answer who held an office on a date. Corrections to those dates create a new record version while preserving the prior version and its transaction history.

## Version identity

Every material record version has a stable `version_id`, `entity_id`, integer sequence, predecessor reference, creation timestamp, actor, reason and Git commit reference when applicable.

## Historical reconstruction

An `as_of` query resolves the latest valid **record version known by the requested transaction time**, while a valid-time query asks whether the represented fact applied during a requested real-world interval. A robust API should permit both dimensions where needed.

## No destructive updates

Replacing a record's current value does not erase the predecessor. Corrections, supersession and invalidation are new events/versions.
