# Result mapping

## PII

- Main result family: `SKT A.X + CRF+Gaz`.
- Test regimes: KPII test, Synthetic test, Combined test.
- Key reported Combined-test F1: **97.5** for SKT A.X + CRF+Gaz with Mix-all training.
- Detailed CSV/JSON results are under `pii/real/results` and `pii/results`.

## Injection

- Baseline/regularized MLP experiments are under `injection/alignsentinel_replicate`.
- Final Camp hybrid release is under `injection/camp_hybrid_exaone`.
- Key reported pooled result for EXAONE-4.0-1.2B-Camp: Acc 0.992 and weighted risk about 0.006.
