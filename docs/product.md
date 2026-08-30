# Evidence Product

## Purpose

The product turns the validated evidence infrastructure into a simple research experience:

**QUESTION → RETRIEVAL → ANSWER → EVIDENCE → PROVENANCE → QUALIFICATIONS → REVIEW**

Its governing question is:

> **WHAT DOES THE EVIDENCE ACTUALLY ESTABLISH?**

It is not a chatbot, campaign biography, ranking engine, propaganda system, or substitute for primary sources.

## Current scope

The product is deliberately limited to the three validated dossiers: Bola Ahmed Tinubu, Peter Gregory Obi and Atiku Abubakar. Candidate 4 remains blocked.

The deterministic query layer is the source of factual truth. No LLM is required to produce an answer.

## User surface

Run:

```bash
python tools/evidence_product.py --port 8080
```

Then open the local product URL. The interface exposes candidate scope, an optional `as_of` date, a question field, answer status, evidence, qualifications, review state, limitations and expandable technical provenance.

The current demonstration accepts the controlled golden-question templates. This is intentional: the first product layer proves safe evidence presentation before adding open-ended natural-language planning.

## What it does not do

- It does not rank candidates.
- It does not infer causality from temporal sequence.
- It does not turn UNKNOWN, UNVERIFIED or DISPUTED into FALSE.
- It does not treat candidate statements as independent proof.
- It does not overwrite historical evidence.
- It does not silently replace historical `as_of` state with current state.
- It does not manufacture missing evidence.
