# Campfire AI Security

This repository is the GitHub-clean research package for Campfire, a lightweight local AI input-security gateway.

It contains reproducible code, experiment scripts, selected result artifacts, and release documentation for two detectors:

- **Korean PII detection**: SKT A.X encoder variants with CRF and gazetteer features, evaluated on KPII, synthetic, and combined test sets.
- **Prompt-injection detection**: AlignSentinel-style attention-map regularized MLP baselines and a Camp EXAONE-4.0-1.2B hybrid detector.

Large raw datasets, Hugging Face caches, full pretrained checkpoints, and regenerable attention/hidden-state dumps are intentionally excluded. See `docs/release_and_backup_policy.md`.


## Public-safe release note

Detailed logs, raw examples, full PII evaluation traces, and files containing PII-like synthetic examples are excluded from this public repository. Aggregate metrics, source code, reproducibility scripts, and release documentation are retained.
