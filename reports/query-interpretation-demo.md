# Natural-Language Query Interpretation Demonstration

## 1. Factual
USER QUESTION: How many votes did Tinubu get in 2023?
SYSTEM INTERPRETATION: Tinubu; election; presidential vote count; COUNT; Nigeria; 2023.
STRUCTURED QUERY: `candidate_scope=[bola-ahmed-tinubu], operation=COUNT, entity=presidential_vote_count, geography=Nigeria, time=2023`.
EVIDENCE RETRIEVAL: deterministic election-result records.
ANSWER: Determined by existing evidence retrieval; interpretation does not supply the vote value.
STATUS: INTERPRETED.
PROVENANCE: query hash + methodology version.
LIMITATION: no inference about voter motivation.

## 2. Factual
USER QUESTION: What offices has Tinubu held?
INTERPRETATION: Tinubu; office history; FACTUAL_LOOKUP.
RETRIEVAL: existing officeholding records.
STATUS: INTERPRETED.

## 3. Factual
USER QUESTION: What political parties has Peter Obi belonged to?
INTERPRETATION: Peter Obi; party history; FACTUAL_LOOKUP.
STATUS: INTERPRETED.

## 4. Quantitative
USER QUESTION: How much did inflation increase between 2022 and 2023?
INTERPRETATION: economy; headline inflation; CHANGE; Nigeria; 2022→2023.
STATUS: INTERPRETED.

## 5. Quantitative
USER QUESTION: What's Tinubu's 2023 vote total?
INTERPRETATION: same structured scope as the first vote-count query.
STATUS: INTERPRETED.

## 6. Causal
USER QUESTION: Did Tinubu cause inflation to rise?
INTERPRETATION: Tinubu; economy; headline inflation; CAUSAL_ATTRIBUTION.
STATUS: INTERPRETED.
ANSWER GENERATION: causal evidence is evaluated downstream; language does not establish causation.

## 7. Causal
USER QUESTION: Was Obi responsible for Anambra's debt?
INTERPRETATION: Peter Obi; Anambra debt; CAUSAL_ATTRIBUTION.
STATUS: INTERPRETED.

## 8. Causal
USER QUESTION: Did Atiku personally cause the outcomes of the NCP?
INTERPRETATION: Atiku; NCP; CAUSAL_ATTRIBUTION.
STATUS: INTERPRETED.

## 9. Contradiction
USER QUESTION: What conflicting evidence exists about Anambra's debt during Obi's tenure?
INTERPRETATION: Peter Obi; Anambra debt; CONTRADICTION; administrative/temporal scope.
STATUS: INTERPRETED.

## 10. Contradiction
USER QUESTION: What evidence disputes the recorded account?
INTERPRETATION: contradiction request; insufficient entity scope unless a concrete record is named.
STATUS: PARTIALLY_INTERPRETED where the referenced record is unavailable.

## 11. Public conversation
USER QUESTION: What did Atiku say about ADC in 2026?
INTERPRETATION: Atiku; ADC; PUBLIC_CONVERSATION; 2026.
STATUS: INTERPRETED.

## 12. Public conversation / assessment distinction
USER QUESTION: Was what Atiku said about ADC true?
INTERPRETATION: assessment of a public statement, not merely a statement lookup.
STATUS: requires evidence assessment rather than treating the statement as proof.

## 13. As-of
USER QUESTION: What was ADC's legal status as of June 2026?
INTERPRETATION: legal; ADC status; AS_OF; June 2026.
STATUS: INTERPRETED when an exact historical boundary can be resolved; otherwise clarification is required.

## 14. Ambiguous
USER QUESTION: What did Tinubu do about the economy?
INTERPRETATION: Tinubu + economy; requested scope remains broad.
STATUS: PARTIALLY_INTERPRETED.
LIMITATION: no arbitrary definition of “economy” is manufactured.

## 15. Subjective
USER QUESTION: Who was the best candidate?
INTERPRETATION: subjective ranking.
STATUS: UNSUPPORTED.
LIMITATION: no validated ranking methodology exists.

## 16. Incomparable
USER QUESTION: Compare Anambra debt with Nigeria inflation.
INTERPRETATION: comparison request with incompatible metric/geography semantics.
STATUS: INCOMPARABLE_COMPARISON after compatibility validation; the interpreter does not declare the metrics substantively comparable.

The examples demonstrate the central boundary: natural language interprets; evidence decides.
