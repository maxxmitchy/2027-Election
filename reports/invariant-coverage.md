# Round 7 — 34-Invariant Coverage Matrix

Status vocabulary: SPECIFIED, IMPLEMENTED, EXECUTED, PASS, FAIL, PARTIAL, UNTESTED.

| ID | Description | Enforcement | Implementation | Test ID | Executed? | Result | Evidence | Remaining gap |
|---|---|---|---|---|---|---|---|---|
| I01 | Stable version ID unique | DATABASE | PK record_version | test_unique_entity_version | YES | PASS | PostgreSQL unique/PK enforcement | none |
| I02 | Entity/version number unique | DATABASE | UNIQUE(entity_id,version_number) | test_unique_entity_version | YES | PASS | duplicate rejected | none |
| I03 | Version 1 has no predecessor | DATABASE | version-chain trigger | test_predecessor_validation | YES | PASS | trigger | add dedicated v1-predecessor fixture |
| I04 | Later version requires predecessor | DATABASE | version-chain trigger | test_predecessor_validation | YES | PASS | trigger | none |
| I05 | Predecessor is immediate same entity | DATABASE | version-chain trigger | test_predecessor_validation | YES | PASS | trigger | none |
| I06 | Transaction timestamp ordering | DATABASE | transaction_from + uniqueness trigger | test_bitemporal_view_snapshot | YES | PASS | snapshot selection | boundary suite expanded |
| I07 | Historical version UPDATE denied | DATABASE | append-only trigger | test_historical_immutability | YES | PASS | DB rejection | none |
| I08 | Historical version DELETE denied | DATABASE | append-only trigger | test_historical_immutability | YES | PASS | DB rejection | none |
| I09 | Office validity interval coherent | DATABASE | CHECK | test_office_overlap_rejected | YES | PASS | schema constraint | dedicated invalid interval fixture |
| I10 | Single-office occupancy non-overlap | DATABASE | GiST exclusion | test_office_overlap_rejected | YES | PASS | exclusion rejection | none |
| I11 | Election references existing office | DATABASE | FK | test_round7.py | YES | PASS | FK exercised by fixture | dedicated negative FK test |
| I12 | Candidacy references person/election | DATABASE | FK | test_round7.py | YES | PASS | FK-backed fixture | dedicated negative FK test |
| I13 | Election result references candidacy/election pair | DATABASE | composite FK | test_round7.py | YES | PASS | invalid pair rejected in prior suite | dedicated Round 7 named test |
| I14 | Geography comparison types compatible | DATABASE | trigger | test_round7.py | YES | PASS | incompatible types rejected in prior suite | dedicated Round 7 named test |
| I15 | Candidacy status transitions constrained | DATABASE | trigger | test_round7.py | YES | PASS | invalid transition rejected in prior suite | dedicated Round 7 named test |
| I16 | Dependency self-edge forbidden | DATABASE | CHECK | test_round7.py | PARTIAL | PARTIAL | control exists | dedicated negative fixture |
| I17 | Dependency edges immutable | DATABASE | trigger | test_round7.py | PARTIAL | PARTIAL | control exists | dedicated mutation test |
| I18 | Dependency cycles rejected | DATABASE | trigger | test_dependency_reverse_closure | YES | PASS | cycle guard exercised by prior suite | dedicated named cycle test |
| I19 | Reverse dependency closure exact | DATABASE | recursive function | test_dependency_reverse_closure | YES | PASS | exact closure asserted | shared/unrelated branch fixture |
| I20 | Dependency traversal terminates | DATABASE | recursive function + visited semantics | test_dependency_reverse_closure | PARTIAL | PARTIAL | finite DAG executed | explicit duplicate/shared-path test |
| I21 | Derived records reference exact input versions | DATABASE | FK/dependency lineage | test_ai_full_reconstruction_and_completeness | YES | PASS | dependency IDs exact | typed lineage validation |
| I22 | Published AI answer content immutable | DATABASE | trigger | test_ai_full_reconstruction_and_completeness | YES | PASS | stale transition preserves content | direct UPDATE negative test |
| I23 | Published AI dependency set immutable | DATABASE | trigger | test_ai_full_reconstruction_and_completeness | YES | PASS | dependency set retained | direct DELETE negative test |
| I24 | Published AI dependency completeness | DATABASE | publish trigger | test_ai_full_reconstruction_and_completeness | YES | PASS | incomplete publication rejected | none |
| I25 | Historical answer remains reconstructable | MULTI_LAYER | immutable answer + dependencies | test_ai_full_reconstruction_and_completeness | YES | PASS | v1 retained after stale | full current-answer selector |
| I26 | Bitemporal transaction snapshot is causal-safe | DATABASE | version_bitemporal + query rule | test_bitemporal_view_snapshot | YES | PASS | 2025→V1, 2026→V2 | full edge matrix |
| I27 | Half-open temporal boundaries | DATABASE | tstzrange/query convention | test_bitemporal_edge_cases | YES | PASS | exact boundary fixture | invalid overlap fixture |
| I28 | Open-ended validity supported | DATABASE | nullable end/query rule | test_bitemporal_edge_cases | YES | PASS | open interval fixture | none |
| I29 | Dataset stable identity preserved | DATABASE | dataset stable_identity_key | test_dataset_revision_matrix | YES | PASS | same observation identity | added/removed cases |
| I30 | Revised observation creates new version | DATABASE | observation_version FK/UNIQUE | test_dataset_revision_matrix | YES | PASS | OV1→OV2 | removed-observation semantics |
| I31 | Methodology versions immutable | DATABASE | trigger | test_round7.py | PARTIAL | PARTIAL | implementation exists | dedicated negative test |
| I32 | Retrieval content hash verifiable | API/MULTI_LAYER | retrieval_event + SHA-256 | test_provenance_hash_match_and_mismatch | YES | PASS | MATCH/MISMATCH hashes | artifact bytes externalized |
| I33 | JSON Schema references resolve | WORKFLOW | schema CI resolver | test_schema_validation_and_ref_resolution | YES | PASS | all discovered refs resolve | full jsonschema RefResolver execution |
| I34 | Failure evidence survives test failure | WORKFLOW | pytest session hook + artifact upload | Round 7 workflow | EXECUTED | PENDING | unconditional report hook implemented | deliberate red CI run |

## Coverage rule

No row is promoted to PASS solely because code exists. PASS requires actual execution and an expected result. PARTIAL indicates execution evidence is incomplete for the invariant's full requirement. UNTESTED means no execution evidence exists.
