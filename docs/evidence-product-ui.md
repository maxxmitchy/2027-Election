# Evidence Product UI

## Architecture

The browser is a presentation layer only. The request path is:

`natural language -> query_interpreter.py -> deterministic template/retrieval -> system_demo.py -> structured answer -> browser`

The UI does not contain candidate facts, calculations, provenance decisions, or an LLM fallback. Candidate data remains in the validated dossier files used by the existing deterministic engine.

## API

`POST /api/ask`

```json
{"question":"...","candidate_ids":["bola-ahmed-tinubu"],"as_of":"2026-05-01"}
```

The adapter validates candidate IDs server-side, rejects Candidate 4, invokes the existing deterministic interpreter and answer machinery, and exposes the structured answer with interpretation, evidence status, provenance, limitations, and performance metadata.

## UI

`product/index.html` is a responsive, keyboard-usable, semantic HTML interface. The hierarchy is question -> answer -> evidence -> provenance -> limitations. Empty sections are omitted.

## Candidate scope

Only `bola-ahmed-tinubu`, `peter-gregory-obi`, and `atiku-abubakar` are permitted. Candidate 4 is not present in the UI and is rejected by the API.

## Local setup

```bash
python -m pip install -r requirements-dev.txt
python tools/evidence_product.py --host 127.0.0.1 --port 8080
```

Open `http://127.0.0.1:8080`.

Run acceptance tests:

```bash
python -m pytest -q tests/test_evidence_product_ui.py
```

Run the genuine mutation suite:

```bash
python tests/run_evidence_product_ui_mutations.py
```

## Deployment

The prototype is packaged as a single Python web service and can be deployed on Render's current free web-service tier. Render currently documents free Python web services, 750 free instance hours per workspace per month, and idle spin-down after 15 minutes; the free tier is explicitly positioned for testing/hobby use rather than production.

The repository includes `render.yaml` as the reproducible deployment descriptor. No database credentials are stored in the repository. The current deterministic engine reads the validated dossier snapshot; PostgreSQL remains the reference runtime used by the existing CI/regression architecture rather than being duplicated in browser code.

## Security

User input is treated as untrusted. The API is read-only, validates candidate IDs, never accepts SQL/Python, does not mutate evidence, and returns controlled errors rather than stack traces. No LLM is used as a factual engine.

## Testing and limitations

The UI/API acceptance suite covers factual, quantitative, historical/as_of, cross-candidate, incomparable, causal, public-conversation, contradiction, correction, research-gap/negative-knowledge, provenance, unsupported, candidate isolation, Candidate 4 rejection, and no-LLM behavior. The mutation suite actually modifies the adapter source in temporary copies and runs an independent oracle; survivors cause CI failure.

This phase prepares the product for human testing. It does not fabricate participants or human-testing findings.
