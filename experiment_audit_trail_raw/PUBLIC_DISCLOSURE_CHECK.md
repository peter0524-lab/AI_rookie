# Public Disclosure Check

This file records the final local checks run before publishing the raw experiment
audit trail.

## Scope

- Directory checked: `experiment_audit_trail_raw/`
- Audit artifacts included: raw result tables, run manifests, status markers,
  logs, summaries, and SHA256 checksums for the PII and prompt-injection
  experiments.
- Public-release assumption from the project owner: datasets and exposed result
  traces are synthetic or public-data-derived and may be disclosed for the
  review period.

## Checks

- Operational secret scan: passed.
- Searched patterns:
  - Hugging Face tokens: `hf_[A-Za-z0-9]{20,}`
  - GitHub tokens: `gh[pousr]_[A-Za-z0-9_]{20,}`
  - AWS access keys: `AKIA[0-9A-Z]{16}`
  - OpenAI-style API keys: `sk-[A-Za-z0-9]{20,}`
  - SSH password helper environment variable names
  - known server password prefix
  - known private server IP
- Matching hits: `0`
- Files larger than 90 MB: `0`
- Raw audit files: `1,563`
- Raw audit directory size: `151M`

## Publication Boundary

The raw audit trail intentionally includes experiment evidence, including raw
logs and result files, so reviewers can inspect reproducibility traces. It does
not intentionally include operational credentials, private access tokens, model
cache blobs, virtual environments, or unrelated machine-local dumps.
