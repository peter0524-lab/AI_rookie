# Public release policy

This repository is a review/public release. It intentionally includes a raw experiment audit trail so reviewers can inspect evidence that the experiments were run.

## Included

- Source code and experiment scripts.
- Aggregate metrics and table-ready result files.
- Raw experiment audit artifacts under `experiment_audit_trail_raw/`.
- Run manifests, status markers, retained logs, and SHA256 checksums.

## Excluded

- Real operational secrets such as access tokens, API keys, server passwords, and private server IPs.
- Hugging Face/pretrained model caches.
- Full fine-tuned checkpoint directories and large model bundles.
- Large tensor/attention/hidden-state feature dumps that can be regenerated.
- Private server command notes and local environment files.

The datasets and traces included for review are treated as public/synthetic for this release. The complete internal preservation archive remains local only under `backups/campfire_essential_backup_*.tar.zst`.
