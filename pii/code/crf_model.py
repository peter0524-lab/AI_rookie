"""
TokenClassification + CRF 래퍼

챔피언(distill_aug) 체크포인트 위에 CRF 전이행렬을 추가해 BIO 시퀀스 일관성을 학습.
저장: HuggingFace tc 가중치 + crf.pt
"""

from pathlib import Path

import torch
import torch.nn as nn
from torchcrf import CRF
from transformers import AutoModelForTokenClassification


class TokenClassifierCRF(nn.Module):
    def __init__(self, tc_model: AutoModelForTokenClassification):
        super().__init__()
        self.tc = tc_model
        n = tc_model.num_labels
        self.crf = CRF(n, batch_first=True)

    @property
    def num_labels(self):
        return self.tc.num_labels

    @property
    def config(self):
        return self.tc.config

    def emissions(self, input_ids, attention_mask):
        return self.tc(input_ids=input_ids, attention_mask=attention_mask).logits

    def forward(self, input_ids=None, attention_mask=None, labels=None, **kwargs):
        logits = self.emissions(input_ids, attention_mask)
        if labels is None:
            return {"logits": logits}

        crf_labels = labels.clone()
        crf_labels[labels == -100] = 0
        mask = attention_mask.bool()
        crf_loss = -self.crf(logits, crf_labels, mask=mask, reduction="mean")
        return {"loss": crf_loss, "logits": logits}

    def decode(self, input_ids, attention_mask):
        logits = self.emissions(input_ids, attention_mask)
        mask = attention_mask.bool()
        return self.crf.decode(logits, mask=mask)

    def save_pretrained(self, path: str | Path):
        path = Path(path)
        path.mkdir(parents=True, exist_ok=True)
        self.tc.save_pretrained(path)
        torch.save(self.crf.state_dict(), path / "crf.pt")

    @classmethod
    def from_pretrained_tc(cls, path: str | Path, trust_remote_code=True):
        tc = AutoModelForTokenClassification.from_pretrained(
            str(path), trust_remote_code=trust_remote_code)
        return cls(tc)

    @classmethod
    def load_pretrained(cls, path: str | Path, trust_remote_code=True):
        model = cls.from_pretrained_tc(path, trust_remote_code=trust_remote_code)
        crf_path = Path(path) / "crf.pt"
        if crf_path.exists():
            model.crf.load_state_dict(torch.load(crf_path, map_location="cpu", weights_only=True))
        return model
