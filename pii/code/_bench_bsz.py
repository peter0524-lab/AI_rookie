import gc
import json
import time
from pathlib import Path

import torch
from peft import LoraConfig, TaskType, get_peft_model
from transformers import (
    AutoModelForTokenClassification,
    AutoTokenizer,
    DataCollatorForTokenClassification,
)

BASE = Path("/data/team/hwan")
path = str(BASE / "models/privacy_filter")
data = json.load(open(BASE / "data/train.json", encoding="utf-8"))
tok = AutoTokenizer.from_pretrained(path)

items = []
for item in data[:512]:
    enc = tok(item["sentence"], truncation=True, max_length=256, return_offsets_mapping=True)
    labels = []
    seen = set()
    char = item["labelling_seq"]
    for wid, (cs, ce) in zip(enc.word_ids(), enc["offset_mapping"]):
        if wid is None or ce == 0:
            labels.append(-100)
        elif wid in seen:
            labels.append(-100)
        else:
            seen.add(wid)
            labels.append(0)
    enc.pop("offset_mapping")
    enc["labels"] = labels
    items.append({k: torch.tensor(v) for k, v in enc.items()})

collator = DataCollatorForTokenClassification(tok, padding=True, label_pad_token_id=-100)

for bsz in [128, 192, 256, 320, 384, 448, 512, 640, 768, 896, 1024]:
    gc.collect()
    torch.cuda.empty_cache()
    model = base = opt = None
    try:
        base = AutoModelForTokenClassification.from_pretrained(
            path, num_labels=39, ignore_mismatched_sizes=True, dtype=torch.bfloat16
        )
        model = get_peft_model(
            base,
            LoraConfig(
                r=16,
                lora_alpha=32,
                target_modules=["q_proj", "k_proj", "v_proj", "o_proj"],
                modules_to_save=["score"],
                task_type=TaskType.TOKEN_CLS,
                bias="none",
            ),
        ).cuda().train()
        opt = torch.optim.AdamW([p for p in model.parameters() if p.requires_grad], lr=2e-4)
        batch = collator(items[:bsz])
        batch = {k: v.cuda() for k, v in batch.items()}
        torch.cuda.synchronize()
        t0 = time.time()
        opt.zero_grad(set_to_none=True)
        loss = model(**batch).loss
        loss.backward()
        opt.step()
        torch.cuda.synchronize()
        mem = torch.cuda.max_memory_allocated() / 1024**3
        steps_per_epoch = (40109 + bsz - 1) // bsz
        total_steps = steps_per_epoch * 20
        est_h = total_steps * (time.time() - t0) / 3600
        print(
            f"BSZ={bsz:4d}  {time.time()-t0:.2f}s/step  "
            f"peakVRAM={mem:.1f}GB  steps={total_steps}  est~{est_h:.1f}h  OK"
        )
    except Exception as e:
        print(f"BSZ={bsz:4d}  FAIL  {type(e).__name__}: {str(e)[:120]}")
    finally:
        del model, base, opt
        gc.collect()
        torch.cuda.empty_cache()
