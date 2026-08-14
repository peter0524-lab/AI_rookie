"""R-Drop + FGM — CRF/gazetteer 모델용 정규화."""

import torch
import torch.nn.functional as F
from transformers import Trainer


class FGM:
    def __init__(self, model, epsilon: float = 1.0):
        self.model = model
        self.epsilon = epsilon
        self.backup = None

    def _emb_weight(self) -> torch.nn.Parameter:
        return self.model.get_input_embeddings().weight

    def attack(self):
        w = self._emb_weight()
        if w.grad is None:
            return
        self.backup = w.data.clone()
        norm = torch.norm(w.grad)
        if norm != 0 and not torch.isnan(norm):
            w.data.add_(self.epsilon * w.grad / norm)

    def restore(self):
        if self.backup is not None:
            self._emb_weight().data = self.backup
            self.backup = None


def rdrop_kl_loss(
    logits1: torch.Tensor, logits2: torch.Tensor, label_mask: torch.Tensor
) -> torch.Tensor:
    log_p = F.log_softmax(logits1, dim=-1)
    log_q = F.log_softmax(logits2, dim=-1)
    p = log_p.exp()
    q = log_q.exp()
    kl_pq = F.kl_div(log_p, q, reduction="none").sum(-1)
    kl_qp = F.kl_div(log_q, p, reduction="none").sum(-1)
    kl = (kl_pq + kl_qp) / 2.0
    mask = label_mask.float()
    return (kl * mask).sum() / mask.sum().clamp(min=1.0)


class PiiTrainer(Trainer):
    def __init__(
        self,
        *args,
        use_rdrop: bool = False,
        rdrop_alpha: float = 4.0,
        use_fgm: bool = False,
        fgm_epsilon: float = 1.0,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.use_rdrop = use_rdrop
        self.rdrop_alpha = rdrop_alpha
        self.use_fgm = use_fgm
        self._fgm = FGM(self.model, epsilon=fgm_epsilon) if use_fgm else None

    def compute_loss(self, model, inputs, return_outputs=False, **kwargs):
        if self.use_rdrop:
            loss, outputs = self._rdrop_forward(model, inputs)
        else:
            outputs = model(**inputs)
            loss = outputs["loss"] if isinstance(outputs, dict) else outputs[0]
        return (loss, outputs) if return_outputs else loss

    def _rdrop_forward(self, model, inputs):
        outputs1 = model(**inputs)
        outputs2 = model(**inputs)
        loss1 = outputs1["loss"] if isinstance(outputs1, dict) else outputs1[0]
        loss2 = outputs2["loss"] if isinstance(outputs2, dict) else outputs2[0]
        logits1 = outputs1["logits"] if isinstance(outputs1, dict) else outputs1[1]
        logits2 = outputs2["logits"] if isinstance(outputs2, dict) else outputs2[1]
        label_mask = inputs["labels"] != -100
        kl = rdrop_kl_loss(logits1, logits2, label_mask)
        loss = 0.5 * (loss1 + loss2) + self.rdrop_alpha * kl
        return loss, outputs1

    def training_step(self, model, inputs, num_items_in_batch=None):
        model.train()
        inputs = self._prepare_inputs(inputs)
        loss = self.compute_loss(model, inputs)
        if self.args.n_gpu > 1:
            loss = loss.mean()
        self._backward(loss)
        if self.use_fgm:
            self._fgm.attack()
            loss_adv = self.compute_loss(model, inputs)
            if self.args.n_gpu > 1:
                loss_adv = loss_adv.mean()
            self._backward(loss_adv)
            self._fgm.restore()
        return loss.detach() / max(self.args.gradient_accumulation_steps, 1)

    def _backward(self, loss):
        scaled = loss / max(self.args.gradient_accumulation_steps, 1)
        accelerator = getattr(self, "accelerator", None)
        if accelerator is not None:
            accelerator.backward(scaled)
        else:
            scaled.backward()
