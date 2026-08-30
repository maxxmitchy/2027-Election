# Gate 4 — Scale-Up Review

**Pilot basis:** Bola Ahmed Tinubu Gate 4 pilot

**Decision:** READY FOR CONTROLLED SCALE-UP

## 1. Purpose

This review converts the empirical lessons of the completed Tinubu pilot into operating standards for the next phase. It does not redesign the architecture and does not populate additional candidates.

The pilot demonstrated that the existing evidence model can survive a real political dossier, but also exposed recurring operational work: primary-source verification, source-version capture, historical chronology reconstruction, social-media semantics, economic dataset definition, legal-record classification, contradiction review, correction lineage, and answer-dependency maintenance.

## 2. Pilot lessons

### Researcher workflow

The work is safest when researchers move in a fixed sequence: identify the durable person; establish elections, offices and party intervals; collect source material; decompose material assertions into claims; attach evidence and retrieval events; add quantitative observations; record contradictions and corrections; create reviewed public answers; execute validation.

Researchers should not write narrative first and retrofit provenance later. Every material assertion should acquire provenance at ingestion time.

### Source discovery

Search is useful for discovery but is not itself sufficient evidence. Researchers should record the discovered source, then seek the strongest available primary or institutional source before accepting the assertion.

### Primary-source verification

The pilot confirms that primary anchors should be prioritized for election results, official appointments/office status, statistical observations, institutional policy announcements and court records. When no primary source is located, the record should preserve the secondary status rather than silently upgrading it.

### Secondary-source handling

Secondary sources remain useful for historical context and for locating events whose primary records are difficult to retrieve. Their evidentiary status must remain explicit. A secondary account can contextualize or corroborate without becoming an authoritative anchor by default.

### Social-media/X evidence

Do not build a generic social-media archive. Use a **RELATED PUBLIC CONVERSATION** evidence/context model. An artifact records that an account made a statement or that a public conversation occurred. It does not establish the truth of the proposition contained in the artifact.

### Contradictory evidence

Contradictions should be preserved as typed relationships such as `CONTRADICTS`, `QUALIFIES`, `CONTEXTUALIZES`, or `CORRECTS`. Researchers should document the review assessment rather than selecting a preferred narrative and deleting the alternative.

### Corrections

Corrections should be versioned. The preferred pattern is `CLAIM v1 → CORRECTION → CLAIM v2`, with the predecessor remaining reconstructable. Downstream calculations and answers should reference the version on which they were generated.

### Economic-data ingestion

Economic observations require substantially more metadata than a displayed number. Definition, unit, geography, period, dataset, dataset version, observation version and methodology version should be captured at ingestion. Comparisons must distinguish percentage change from percentage-point change and temporal association from causal attribution.

### Legal-record ingestion

Legal records require explicit separation of allegation, court finding and procedural outcome. The existence of litigation is not evidence that an allegation is true.

### Review workload

Human review is concentrated around identity resolution, source authority, ambiguous chronology, legal classification, contradictory evidence, corrections, causal language and public-answer completeness. Mechanical checks can detect missing links and invalid structures, but they cannot reliably determine evidentiary sufficiency in every case.

### Human-readable consistency

Every candidate dossier should use the same section order and terminology. Narrative variation is acceptable inside sections, but researchers should not invent different dossier structures.

### Machine-readable consistency

Use controlled identifiers, relationship types, version fields and required provenance fields. Repeated manual construction of structurally similar records is a major source of avoidable errors and should be template-driven.

## 3. Minimum standard dossier template

Every future candidate dossier should contain:

1. Candidate Profile / Identity
2. Political History
3. Party History
4. Office History
5. Election History
6. Public Statements / Related Public Conversation
7. Major Documented Actions and Policies
8. Economic Record
9. Legal Record
10. Contested / Contradictory Claims
11. Corrections
12. Uncertainty
13. Sources
14. Reviews

Each material assertion should be represented as an auditable claim where appropriate and traceable through:

`CLAIM → EVIDENCE → SOURCE → SOURCE VERSION → RETRIEVAL EVENT`

Quantitative material should additionally trace through:

`OBSERVATION → CALCULATION → ANALYSIS → RESULT`

Public answers should trace through:

`ANSWER → DEPENDENCIES → CLAIMS / OBSERVATIONS / SOURCES → AS_OF → GENERATION VERSION`

## 4. RELATED PUBLIC CONVERSATION standard

For future dossiers, public social-media artifacts should be classified as **RELATED PUBLIC CONVERSATION**, not as a generic archive.

Supported evidence/context relationships include:

- `support_context`
- `contradict`
- `clarify`
- `correct`
- `provide_primary_source`
- `provide_data`
- `quote`
- `respond_to`
- `contextualize`
- `report_event`

Required provenance should include, where available:

- account identity
- original URL
- publication timestamp
- retrieval event
- source version/hash
- archive/reference
- deletion or availability state
- post type
- relationship to the proposition or event

The rule is explicit: **ACCOUNT MADE STATEMENT X** is distinct from **X IS FACTUALLY TRUE**.

## 5. Economic-data standard

The eventual administration-comparison framework is:

`ADMINISTRATION → TIME PERIOD → METRIC → OBSERVATION → CALCULATION → ANALYSIS → RESULT`

Every observation should preserve:

- metric definition
- value
- unit
- geography
- period start
- period end
- dataset
- dataset version
- observation version
- methodology version
- source
- retrieval event

Calculations must label the correct change type:

- **percentage-point change:** subtraction of two percentages
- **percentage change:** change divided by the comparison baseline

The system must not infer causation from chronology. Causal classifications remain explicit, such as `TEMPORAL_ASSOCIATION`, `DOCUMENTED_ATTRIBUTION`, `SUPPORTED_CAUSAL_INFERENCE`, `CONTESTED_ATTRIBUTION`, and `INSUFFICIENT_EVIDENCE`.

## 6. Review standard

Material records should be reviewed separately for:

- evidence quality
- factual accuracy
- calculation accuracy
- context completeness
- source quality
- reviewer confidence

Review is an assessment layer, not evidence itself. No popularity or consensus score should substitute for evidentiary review.

## 7. Automation opportunities

The following should become increasingly automated without removing human review:

- dossier scaffolding and required-section checks
- identifier generation and relationship validation
- provenance completeness checks
- duplicate-source and duplicate-claim detection
- source/version/hash capture where technically available
- retrieval-event creation
- schema validation
- temporal interval validation
- election/result foreign-key and relationship checks
- economic unit/geography/period consistency checks
- percentage-point versus percentage-change calculation validation
- stale dependency detection after corrections
- public-answer dependency completeness
- CI execution and evidence artifact generation
- report generation

## 8. Human-review requirements

Human researchers must retain responsibility for:

- resolving real-world identity ambiguity
- deciding whether a source is genuinely primary or authoritative for the proposition
- interpreting historical party and office chronology
- deciding whether evidence supports, contradicts, qualifies or merely contextualizes a claim
- distinguishing allegation from finding in legal records
- assessing contradictory accounts
- approving corrections
- evaluating causal attribution
- determining whether context is materially incomplete
- approving public-facing answers for evidentiary fidelity

Automation may flag these decisions but should not silently make them.

## 9. Repeated primary-evidence gaps

The Tinubu pilot showed recurring situations where primary evidence was unavailable, difficult to retrieve, or less direct than desired. These included older historical electoral records, some historical political chronology, reproduced legal material where a court-hosted copy was not located, and public social-media material whose availability can change.

These should be handled operationally, not by lowering the truth standard. The record should say `UNKNOWN`, `UNVERIFIED`, `INCOMPLETE`, `UNAVAILABLE`, or `RETRIEVAL_FAILURE` where appropriate.

**Absence of evidence ≠ evidence of absence.**

## 10. Unnecessarily difficult pilot tasks

The most avoidable difficulty was not database representation. It was repeated manual provenance work: locating authoritative versions, capturing retrieval metadata, normalizing historical intervals, preserving competing accounts, and keeping narrative answers synchronized with corrected machine-readable records.

The scale-up response should therefore be standardized ingestion templates, source/retrieval capture helpers, controlled vocabularies, automated validation and dependency checks—not architectural expansion.

## 11. Research discipline

The following principles are mandatory operating rules:

> The database records what the evidence establishes. It does not record what the researcher wishes the evidence established.

Also:

- absence of evidence ≠ evidence of absence
- unverified ≠ false
- disputed ≠ false
- source authority ≠ automatic truth
- temporal association ≠ causation
- candidate statement ≠ factual proof
- review ≠ evidence
- AI answer ≠ source of truth

## 12. Remaining operational risks

1. Primary-source availability varies sharply by historical period.
2. Social-media content can be deleted, edited, restricted or become inaccessible.
3. Historical party and office records may require reconciliation across multiple sources.
4. Statistical datasets can be revised; dataset and methodology versions therefore matter.
5. Legal reporting can compress allegations and judicial findings into misleading summaries.
6. Contradictory sources may disagree because of scope, definitions or time periods rather than because one is simply false.
7. Corrections can make previously generated answers stale unless dependency checks run automatically.
8. Researcher workload will rise quickly if every source decision remains entirely manual.
9. Current-status assertions require a fresh verification cutoff; historical dossier content should not be mistaken for continuously current data.
10. Public answers can introduce unsupported synthesis even when their underlying records are sound; answer-level review remains necessary.

## 13. Scale-up gate

**SPECIFIED:** Controlled future-candidate workflow, standard dossier, public-conversation standard, economic standard, review standard and operating principles.

**IMPLEMENTED:** The Tinubu pilot already demonstrates the core record, provenance, review, correction, contradiction, economic and answer-dependency patterns.

**EXECUTED:** The Tinubu Gate 4 acceptance workflow executed against commit `4ee713dd1c50829ff11742a31dbc56b7a5953dc0`, with 15 tests passing and 0 failing.

**PASS:** Gate 4 pilot acceptance.

**PARTIAL:** Operational standardization for repeated candidate ingestion; this review defines the standard but does not populate additional candidates.

**UNTESTED:** Full-scale throughput, multi-researcher consistency and sustained ingestion volume across the remaining presidential field.

## 14. Recommendation

### READY FOR CONTROLLED SCALE-UP

The pilot provides sufficient empirical evidence to proceed to a controlled next phase. The next phase should begin with the standardized dossier template, controlled vocabularies, source/retrieval discipline, human review requirements and automated validation defined here.

This review does **not** authorize or initiate mass candidate ingestion. Additional candidates should be populated only under a separately approved controlled-ingestion phase.
