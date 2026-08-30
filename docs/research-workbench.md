# Research Workbench

The Phase 5 workbench is deterministic and operates on the existing candidate dossier records.

```python
from pathlib import Path
from research_workbench import investigate, task_queue

root = Path('.')
investigation = investigate(
    root,
    "What evidence supports or contradicts claims about Peter Obi's Anambra debt record?",
    as_of="2026-08-30",
)
tasks = task_queue(investigation)
```

The investigation contains the interpreted question, candidate scope, decomposition, explicit evidence requirements, retrieved source metadata, research gaps, review boundary, answerability state, performance metadata and reproducibility metadata.

The workbench does not declare unsupported claims true or false. It creates an auditable plan for establishing them.

## Candidate scope

Only these IDs are accepted:

- `bola-ahmed-tinubu`
- `peter-gregory-obi`
- `atiku-abubakar`

`candidate-4` is rejected by the deterministic scope guard.

## Answerability

`ANSWERABLE` and `PARTIALLY_ANSWERABLE` describe documentary readiness, not probability of truth. Coverage is explicitly labelled `multidimensional-documentary-coverage-v1` and `is_truth_probability=false`.
