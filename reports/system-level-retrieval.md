# System-Level Cross-Candidate Retrieval

## Purpose

This round tests whether the validated evidence infrastructure can answer comparative questions from stored records while preserving exact, machine-reconstructable provenance. It does not conduct new candidate research and includes only the three validated candidates: Tinubu, Peter Obi and Atiku Abubakar.

## Boundary

The retrieval prototype reads only the existing `pilot-record.json` fixtures. It does not call web search, use unstored political facts, or infer missing records. `NOT_FOUND_IN_CURRENT_DATASET` is kept distinct from `DID_NOT_OCCUR`.

## Retrieval path

`QUESTION -> DETERMINISTIC RETRIEVAL -> STRUCTURED RECORDS -> DERIVED ANSWER -> DEPENDENCY VALIDATION`

The existing methodology already requires answers to reference immutable claim/evidence/source and calculation/observation dependencies, database snapshot and generation timestamp. filecite references are documentation-only here; repository records remain the source of truth.

## Golden questions

| ID | Question | Expected scope |
|---|---|---|
| Q1 | Compare Tinubu, Obi and Atiku in the 2023 presidential election. | exactly 3 candidates; stored votes/rank/party/source fields; missing fields explicit |
| Q2 | Show the documented presidential election history currently represented for each candidate. | all presidential candidacy records present in the three fixtures; missing result records remain NOT_FOUND_IN_CURRENT_DATASET |
| Q3 | Show selected economic claims associated with each candidate and the evidence status. | stored economic/calculated/causal/assessment claims only; no ranking |
| Q4 | Which claims in the three dossiers are disputed or insufficiently evidenced? | explicit DISPUTED/INSUFFICIENT_EVIDENCE/UNVERIFIED/UNKNOWN records only |
| Q5 | Show all correction lineages currently represented for the three candidates. | stored correction records only; NO_MATCH is valid |
| Q6 | Show examples of RELATED PUBLIC CONVERSATION and distinguish statements from facts. | stored public/social records only; statement occurrence is not truth |
| Q7 | What did the database know about these candidates as of a controlled historical date? | transaction-time snapshot semantics; no post-cutoff dependencies |
| Q8 | Show the complete evidence lineage for one quantitative answer. | result -> analysis -> calculation -> observation -> dataset/source versions where those records exist |

## Safety and integrity tests

The prototype tests candidate identity isolation, provenance dependency resolution, quantitative compatibility (period/geography/metric/unit/dataset version), explicit failure states, answer immutability/versioning, and controlled mutations. A candidate-specific claim cannot be accepted merely because its text appears in another candidate's answer.

## What this demonstrates beyond an ordinary search/LLM response

Search engines and general-purpose LLMs may provide some of these capabilities, but this architecture makes them explicit, queryable and auditable as first-class records: exact dependency lineage, historical `as_of` reconstruction, correction history, contradiction preservation, negative knowledge, source/evidence separation, candidate-identity integrity, reproducibility, review history, answer versioning and machine-readable provenance.

This is not a claim that Google or ChatGPT cannot perform any of these functions. The distinction is that the project stores the necessary state and relationships so a result can be reconstructed deterministically from an identified snapshot rather than relying on an opaque response-generation event.

## Validation rule

No system-level PASS is declared until the dedicated CI workflow executes on the implementation commit and records test counts plus the evidence artifact and SHA-256 digest. Candidate 4 remains blocked regardless of this round's outcome.
