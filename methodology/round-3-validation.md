# Round 3 — Formal Model Validation

This document validates the canonical model against adversarial historical, evidentiary, temporal, revision and retrieval scenarios. These are hypothetical fixtures only; no political research data is introduced.

## Validation result

**PASS WITH REQUIRED ENFORCEMENT:** the normalized model represents all 18 scenarios after the Round 3 schema additions. JSON Schema validates record shape; cross-record integrity, temporal exclusion, dependency propagation and immutable history require API/database/workflow enforcement.

## 1. Multiple candidacies

Records: `PERSON:P-001`; `ELECTION:E-2019`, `ELECTION:E-2023`; `CANDIDACY:C-2019-P001`, `CANDIDACY:C-2023-P001`.

Both candidacies reference the same `P-001`. Election-specific party/status/result data belongs to each candidacy. The person ID never changes or duplicates. Valid time is the candidacy interval; transaction time is the creation/version timestamp.

**Query:** all candidacies for `P-001`, ordered by election date. **Pass.**

## 2. Party changes

Records: `PARTY:PA`, `PARTY:PB`; `PARTY_AFFILIATION:AFF-001`, `AFF-002`.

`P-001` belongs to PA from 2018-01-01 through 2022-06-30 and PB from 2022-07-01 onward. Membership is not a property of Person. Each affiliation has its own valid interval and version history.

**Pass.**

## 3. Multiple officeholdings

Records: `OFFICE:PRES`, `OFFICE:GOV`; `OFFICEHOLDING:OH-001`, `OH-002`.

One person may hold sequential or genuinely overlapping offices. Each holding has its own interval, appointment/election basis and evidence. API rules must reject overlapping holdings where the office is defined as single-occupancy unless a documented exception exists.

**Pass with database/API temporal constraint.**

## 4. Administration transitions

`OFFICEHOLDING:OH-A` covers 2019-05-29 to 2023-05-29; `OH-B` covers 2023-05-29 onward. `ADMIN:A-2019` and `ADMIN:A-2023` are analytical periods, not persons.

**Who held office on 2022-01-01?** Resolve the office holding whose valid interval contains the date.

**What did the database believe on transaction date 2021-01-01?** Select the latest version created no later than that transaction timestamp, then evaluate its valid-time interval.

**Pass.**

## 5. Historical statistical revision

`OBS:OBS-123:v1 = 20.0`; later `OBS-123:v2 = 21.0`, same metric/period/scope but corrected source data.

Existing `CALC-1:v1` references `OBS-123:v1`; `ANALYSIS-1:v1` references `CALC-1:v1`; `RESULT-1:v1` references the analysis; `ANSWER-1:v1` references the result.

The correction creates `OBS-123:v2`. Reverse dependency traversal marks the v1 calculation, analysis, result and answer stale/invalid according to policy. New v2 calculation → analysis → result → answer records reference the corrected observation version.

**Pass.**

## 6. Reverse dependency query

Given `OBS-123:v2`, dependency edges are traversed downstream by `upstream_ref`. The graph returns all directly and transitively dependent calculations, analyses, results and answers without scanning unrelated records.

**Pass.**

## 7. Contradictory sources

`SOURCE:S-A` reports 100; `SOURCE:S-B` reports 110. Separate evidence records attach each source to the relevant claim/observation with typed semantics and independence metadata. Neither source is deleted or automatically selected as truth.

A result may state that credible sources disagree, identify each value and explain the reconciliation policy (or explicitly decline to reconcile).

**Pass.**

## 8. Political statement vs fact

Create `CLAIM:C-STMT` = "Candidate P said inflation fell by 20%" with `claim_type=statement`. Evidence uses `is_subject_statement` against the candidate's source.

Separately create underlying inflation observations, `CALC:CALC-20`, `ANALYSIS:AN-20`, and `RESULT:R-20` testing the claimed change. The result can conclude supported, partially supported, unsupported or indeterminate without altering the statement record.

**Pass.**

## 9. Deleted social-media post

`SOC:S-001` records the original-post reference, archive capture, screenshot, capture hash, account authenticity, date certainty and deletion state. The screenshot and archive are distinct records and are not equivalent to an original platform record.

Evidence A: `is_subject_statement` establishes evidence about what the person said, subject to provenance confidence. A separate claim about the truth of the underlying proposition requires independent evidence.

**Pass.**

## 10. Source disappears

`SOURCE:S-100:v1` retains its original URL, retrieval timestamp, publisher/title and archival reference. Extracted evidence remains linked to the source version. If the live URL later becomes unavailable, the source status changes; the historical source and evidence records remain immutable.

**Pass.**

## 11. Methodology change

The same observation versions feed `CALC:v1` using methodology `M-1` / Formula A and `CALC:v2` using `M-2` / Formula B. Each produces its own analysis/result versions. The v1 AI answer retains `M-1` and its exact inputs, so it remains reproducible.

**Pass.**

## 12. Geographic normalization

Create `GEO:NG` (Nigeria), `GEO:NG-LA` (Lagos State), `GEO:NG-LA-METRO` (Lagos metropolitan area), and another explicitly defined geographic unit. Observations reference a normalized geography ID rather than free-text geography alone.

Comparisons require compatible metric definition, unit, time basis and geographic scope. The API must reject or flag incompatible scopes rather than silently aggregating them.

**Pass with database/API compatibility enforcement.**

## 13. Election result normalization

`PERSON:P-001 → CANDIDACY:C-2023-P001 → ELECTION:E-2023 → RESULT:ER-001`.

Election result stores votes, vote share, rank, electoral scope, result status, source reference and certification status. Result is not a property of Person.

**Pass.**

## 14. Claim relationships

Required typed claim relations are: `qualifies`, `contradicts`, `supersedes`, `depends_on`, `entails`, `retracts`, `corrects`. They are represented as separate versioned relation records, not overloaded fields on Claim.

`contradicts` is evidentiary/logical relationship between propositions; `supersedes` replaces an earlier claim version; `retracts` withdraws a prior assertion; `corrects` identifies a factual correction; `depends_on` expresses prerequisite proposition; `entails` expresses logical implication; `qualifies` narrows a proposition.

**Pass.**

## 15. AS_OF resolution

There are two independent axes:

- **Valid time:** when the fact applied.
- **Transaction time:** when our system recorded the version.

For "Who held office on 2022-01-01?" query versions representing the officeholding and select the valid interval containing 2022-01-01.

For "What did the database know on 2022-06-01?" select the latest version whose `transaction_from <= 2022-06-01`, without allowing later corrections to leak backward into that historical snapshot.

For a bitemporal query, first establish the transaction snapshot, then evaluate valid time within that snapshot. This makes resolution deterministic.

**Pass after explicit transaction interval fields are added to Version.**

## 16. Candidate status

Status belongs to Candidacy, not Person. A candidacy may transition through potential, declared, nominated, registered, withdrawn, disqualified and elected states. Each state transition is time-stamped and versioned. A person can simultaneously have different candidacy statuses in different elections.

**Pass.**

## 17. Data correction

`OBS-77:v1` is entered incorrectly. A `CORRECTION:CR-77` identifies the affected version, reason, evidence, proposer, reviewer and proposed action. Review approves the correction. `OBS-77:v2` is created; v1 remains immutable. Dependency traversal invalidates/stales downstream v1 calculations/results/answers. Recalculation creates new versions.

**Pass.**

## 18. AI answer reproducibility

Example dependency:

`ANSWER:A-1:v1`
→ `CLAIM:C-1:v3`
→ `EVIDENCE:E-1:v2`
→ `SOURCE:S-1:v4`

For quantitative output:

`ANSWER:A-1:v1`
→ `RESULT:R-1:v2`
→ `ANALYSIS:AN-1:v2`
→ `CALCULATION:CAL-1:v2`
→ `OBSERVATION:OBS-1:v4`
→ `DATASET:DS-1:v3` / source versions
→ `METHODOLOGY:M-1:v2`

The answer also records generation time, database snapshot/version, `as_of`, and exact dependency references. Missing in the earlier model were formal dataset-version and methodology identity contracts; these are now required by the architecture and must be added before production data ingestion.

**Pass after schema additions.**

# Formal invariants

1. Every Candidacy references exactly one Person and exactly one Election.
2. Person identity is independent of candidacy, party affiliation and officeholding.
3. Party affiliation is a temporal relationship, not a permanent Person property.
4. Every OfficeHolding references exactly one Person and one Office.
5. Administration and Office are distinct entities.
6. An Administration cannot be inferred solely from a person's identity.
7. Single-occupancy offices cannot have unexplained overlapping active holdings.
8. Every ElectionResult references exactly one Candidacy and one Election.
9. Every material record version has a unique immutable version ID.
10. The first version has no predecessor; every later version has exactly one predecessor.
11. Version transaction timestamps are monotonic for a record's version chain.
12. Valid-time intervals must be internally coherent and use explicit boundary semantics.
13. Valid time and transaction time are never treated as interchangeable.
14. Derived records reference exact input versions, not only stable entity IDs.
15. A dependency edge references identifiable upstream and downstream versions.
16. Corrections never mutate or delete historical versions.
17. A stale/invalid upstream version propagates stale/invalid status to affected downstream derivatives according to dependency policy.
18. Recalculation creates new derived versions.
19. A source-to-claim relationship must have a typed semantic relationship.
20. A subject statement does not by itself establish the truth of its proposition.
21. Contradictory evidence is retainable without forced automatic resolution.
22. Social-media authenticity and statement truth are separate assessments.
23. Screenshot evidence is not equivalent to original platform evidence.
24. Geographic scope is represented by normalized identifiers for comparable quantitative observations.
25. Quantitative comparison requires compatible metric definition, unit, period basis and geography.
26. Temporal change does not imply causal attribution.
27. Review records are not evidence merely because they exist.
28. Community agreement cannot raise evidentiary truth status by itself.
29. AI answers reference exact dependency versions and methodology versions.
30. An AI answer whose dependency is stale cannot remain silently represented as current.
31. An `as_of` transaction query cannot use versions created after its cutoff.
32. A valid-time query must evaluate the fact's validity within the selected transaction snapshot when bitemporal reconstruction is requested.
33. Claim relations are explicit, typed and versioned.
34. Candidate status is election/candidacy-specific.

# Enforcement matrix

| Invariant class | JSON Schema | API/application | Database | Workflow/review |
|---|---|---|---|---|
| Required IDs/types/enums | **Yes** | Yes | Yes | — |
| Foreign-key existence | No | **Yes** | **Yes** | — |
| Unique stable IDs | No | Yes | **Yes** | — |
| Version predecessor chain | Partial | **Yes** | **Yes** | Yes |
| Immutable historical versions | No | **Yes** | **Yes** | Yes |
| Valid-time interval coherence | Partial | **Yes** | **Yes** | Yes |
| No unexplained office overlap | No | **Yes** | **Yes** | Yes |
| Exact dependency versions | Partial | **Yes** | **Yes** | — |
| Reverse dependency invalidation | No | **Yes** | Support graph | — |
| Source/evidence semantic typing | **Yes** | Yes | Yes | **Yes** |
| Statement ≠ truth | No | **Yes** | Support | **Yes** |
| Geographic compatibility | No | **Yes** | Support | **Yes** |
| Calculation reproducibility | Partial | **Yes** | Support | **Yes** |
| Review ≠ evidence | Partial | **Yes** | Support | **Yes** |
| AI dependency completeness | Partial | **Yes** | **Yes** | **Yes** |
| Candidacy status transitions | Partial | **Yes** | **Yes** | Yes |

# Approval gate

All 18 adversarial cases are representable after the Round 3 additions. No candidate research data is used in these tests.

**Research gate: NOT YET OPEN.** The model should undergo one further independent review focused on implementation-level constraints, especially database exclusion constraints, transaction-time interval semantics, dependency invalidation algorithms, dataset identity/revision semantics and schema validation tooling before production population begins.
