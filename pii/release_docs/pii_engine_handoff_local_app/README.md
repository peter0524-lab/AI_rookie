# PII Engine Handoff: SKT + Gazetteer + CRF Single Model

For local-app deployment, prefer `LOCAL_APP_HANDOFF.md` and
`package_pii_local_app_bundle.sh`. This file is the older research/server-style
handoff note.

## What to hand off

Give the developer a single tarball that contains one trained checkpoint, not the 3-seed ensemble.

Use the latest single model trained on mixed data:

```bash
models/skt_encoder_crf_gaz_mixed_natural/seed44
```

If the final selected seed is different, replace `seed44` with that exact seed directory. Do not give the `x3` voting result as the engine model; `x3` is an evaluation-time ensemble.

## Required files inside the model directory

The model directory must include:

```text
config.json
model.safetensors or pytorch_model.bin
tokenizer.json / tokenizer_config.json / special_tokens_map.json
label_map.json
gazetteer.json
```

This model is not a plain Hugging Face token-classification model. It uses:

```text
pii_model.py      # custom SKT backbone + optional gazetteer + optional CRF wrapper
crf_bio.py        # CRF decoding and BIO transition constraints
gazetteer.py      # gazetteer feature construction during inference
```

## Server-side packaging command

Run from the project root on the GPU server:

```bash
cd /data/team/hwan/alignsentinel_replicate
bash /path/to/package_pii_single_model.sh \
  models/skt_encoder_crf_gaz_mixed_natural/seed44 \
  pii_skt_crf_gaz_mixed_single_seed44.tar.gz
```

Then give the developer:

```text
pii_skt_crf_gaz_mixed_single_seed44.tar.gz
```

## Integration notes for the developer

The engine should load the model with `trust_remote_code=True`, load the tokenizer, load `gazetteer.json`, build gazetteer token features for each request, and decode with CRF through `model.predict_tags(...)`.

Minimum runtime dependencies:

```text
python >= 3.10
torch
transformers
numpy
```

Expected output format should be span-based PII entities:

```json
[
  {
    "label": "PHONE_NUMBER",
    "form": "[PHONE_PLACEHOLDER]",
    "begin": 12,
    "end": 25
  }
]
```

## Smoke test before handoff

Before sending the tarball, run one short inference/eval to confirm the bundle loads:

```bash
python3 eval_crf_gaz.py \
  --model_dir models/skt_encoder_crf_gaz_mixed_natural/seed44 \
  --data-dir data \
  --split test \
  --batch_size 16 \
  --max_length 256
```

If this loads and prints metrics, the developer can integrate the same model path logic into the engine.
