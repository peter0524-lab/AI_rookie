# Raw Experiment Audit Trail

This folder contains raw experiment evidence for the Campfire PII and prompt-injection experiments.

## Purpose

The public repository keeps the main README and source tree compact, while this folder exposes the underlying result artifacts used to verify that the experiments were actually run.

## Contents

- `pii/raw_real_results/`: raw PII metric JSON/CSV/TSV result tables from the real experiment protocol.
- `pii/raw_legacy_results/`: earlier PII baseline and ablation result artifacts.
- `pii/run_status/`: training/evaluation completion markers.
- `pii/run_manifests/`: run manifests and protocol metadata.
- `pii/raw_logs/`: raw PII experiment logs retained in the public release.
- `injection/alignsentinel_*`: AlignSentinel-style backend LLM experiment logs/results.
- `injection/camp_hybrid_*`: Camp EXAONE hybrid detector logs/results.
- `checksums/RAW_AUDIT_SHA256.tsv`: SHA256 checksums for every copied audit artifact.

## Disclosure Note

The included datasets and result traces are treated as public/synthetic for this review release. Operational secrets such as real access tokens, server passwords, and private server IPs are still excluded from the repository.

Generated at: 2026-08-14T10:57:53
