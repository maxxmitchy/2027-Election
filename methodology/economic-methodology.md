# Economic and Governance Methodology

## Objective

Create reproducible observations that allow comparisons across administrations without confusing temporal association with causal responsibility.

## Required observation fields

Every important metric should preserve its definition, unit, geography, observation period, source, publication date, original value and dataset/version. Where a comparison is made, preserve both values and the exact calculation.

## Comparability

Do not combine observations with incompatible definitions, geographic scopes, frequencies, base years or methodological regimes without documenting the difference. Statistical revisions should be retained and linked to the prior version.

## Before/during/after comparisons

Define administration start and end dates explicitly. State whether a comparison uses the nearest published observation, a monthly/quarterly/annual period, an average, an end-period value or another rule. Do not silently cherry-pick dates.

## Calculations

Calculations should be reproducible from stored source observations. Percentage change is `((comparison_value - original_value) / original_value) * 100`. Percentage-point changes subtract rates directly. Preserve rounding rules and original precision.

## Attribution

Temporal change answers what changed over a period. Causal attribution answers why it changed. Store these as different analytical objects and require an explicit causal methodology for attribution claims.

## Price and exchange-rate data

Record exact product/market definition, location, unit, currency, date and pricing basis. Do not mix official and parallel-market exchange rates without labeling them as different series.
