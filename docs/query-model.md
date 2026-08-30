# Query Model

The product reuses the validated `system_demo.answer_question()` retrieval/answer contract rather than replacing it.

1. Resolve the question against a controlled template.
2. Resolve candidate scope using stable candidate IDs.
3. Retrieve only the dossier(s) in that scope.
4. Select the record type appropriate to the question: officeholding, party membership, candidacy/election result, observation, causal analysis, contradiction, correction or public conversation.
5. Assemble the answer from retrieved records.
6. Attach provenance and limitations.

A query that cannot be mapped to a controlled template returns `NO_MATCH`; it is not answered by guesswork.

Cross-candidate queries explicitly carry multiple candidate IDs. Single-candidate queries cannot inherit records from another dossier.
