# Release and backup policy

## Included in this GitHub-clean repository

- Source code and experiment scripts.
- Result CSV/JSON/PDF artifacts that are small enough for GitHub.
- Final Camp hybrid injection release files if each file is below 90 MB.
- README and developer handoff documentation.

## Excluded from GitHub

- Raw/private PII data.
- Hugging Face pretrained model caches.
- Full training checkpoint directories.
- Large intermediate attention/hidden-state feature dumps.
- Local command notes or files that may contain credentials.

The raw preservation archive is stored separately as `campfire_essential_backup_*.tar.zst` and includes more experiment context while still excluding very large re-downloadable or regenerable artifacts.
