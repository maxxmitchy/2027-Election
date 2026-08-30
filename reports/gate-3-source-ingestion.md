# Gate 3 — Source Ingestion Controlled Experiment

## Purpose

This experiment tests whether the existing evidence architecture survives contact with real public information without collapsing provenance, temporal semantics, evidence relationships, version history or review state.

This is **not candidate research**. No candidate, administration, election result, party dossier or political claim has been populated.

## Sources inspected

| Source | Type | Tier | Role |
|---|---|---:|---|
| National Bureau of Statistics — July 2026 CPI report | Official statistical publication | 1 | Primary measurement |
| National Bureau of Statistics — CPI dataset catalog | Official statistical dataset/catalog | 1 | Dataset identity and release discovery |
| Reuters — cost-of-living report, 10 Aug 2026 | Reputable news report | 2 | Secondary contextual evidence |
| Proshare X post, 24 Mar 2026 | Social-media statement | 3 | Statement-vs-truth semantic test |
| Central Bank of Nigeria homepage snapshot | Official record/display | 1 | Contradiction/temporal-context test |
| Premium Times — July 2026 inflation report | Established journalism | 3 | Independent corroboration |

The public artifacts were inspected on 2026-08-30. Source URLs and retrieval metadata are preserved in `sources/gate3/`.

## Retrieval and hash semantics

Each source has a `RetrievalEvent` with URL, retrieval timestamp, media type, artifact identifier, hash algorithm and content hash. For web/PDF resources whose raw bytes were not directly persisted by this experiment, the recorded SHA-256 covers a **canonical captured representation** stored in the test fixture. The repository does not misrepresent this as a byte-for-byte hash of the remote artifact.

The NBS July direct-download endpoint timed out during inspection while the NBS catalog remained accessible. This is recorded as `availability_status=unknown` / retrieval failure, not as evidence that the source is false.

## Evidence semantics

The ingestion demonstrates typed relationships:

- NBS CPI report → `directly_establishes` July headline inflation.
- Premium Times → `reports_claim` the NBS figure.
- Proshare X post → `is_subject_statement`.
- CBN homepage snapshot → `directly_establishes` what the page displayed at retrieval.
- NBS July release → `contradicts_claim` an undated interpretation of the CBN 15.93% display.

The social-media test deliberately stores two separate propositions:

1. **Statement claim:** Proshare's account published a statement about February 2026 inflation.
2. **Fact claim:** February 2026 inflation was 15.06%.

The first does not automatically establish the second.

## Contradictory evidence

The CBN homepage snapshot displayed 15.93%, while the later NBS July release reported 15.43% year-on-year. Both records remain preserved. The apparent disagreement is treated as a temporal/context problem rather than silently selecting one value and deleting the other.

This is deliberately a controlled contradiction: the system is being tested on preservation and qualification, not asked to decide causation or political responsibility.

## Source revision

`source-version-fixtures.json` contains an explicitly labelled `simulated_revision` from V1 to V2. V1 remains reconstructable. The experiment does **not** claim that NBS actually revised the publication.

## Correction

A controlled ingestion error was introduced:

`15.43% month-on-month`

was corrected to:

`15.43% year-on-year; 1.57% month-on-month`.

V1 remains stored as `superseded`; V2 is the valid version. The downstream analysis fixture correspondingly changes from `superseded` to the corrected valid record.

## Review

Reviews are stored separately from source/evidence records. The correction review explicitly identifies the factual error and proposed action. The CBN dispute review identifies missing temporal context rather than declaring the source itself false.

## Execution

The executable validation suite is `tests/gate3_source_ingestion.py` and the CI workflow is `.github/workflows/gate3-source-ingestion.yml`.

The final execution evidence must identify the exact checked-out commit using `git rev-parse HEAD` and is uploaded as a CI artifact. No Gate 3 PASS is claimed merely because the workflow or fixtures exist.

## Acceptance status

At creation of this report, the controlled source records, retrieval events, evidence relationships, review records, correction fixtures, source-revision fixtures and executable validator are **IMPLEMENTED**. Gate 3 becomes **PASS** only after the corresponding CI execution is observed as successful for the tested commit.
