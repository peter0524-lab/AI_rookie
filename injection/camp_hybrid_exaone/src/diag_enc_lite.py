"""Enc-lite 검증 — g_mean(Avg-first류)이 아니라 encode-before-pool이면 attention 신호가 오르는가?

배경: injection_diag/diag_analyze.py의 g_mean은 head별로 tool-response 전체 토큰(위치 bin)
평균을 낸 뒤 분류기에 넣는다 — 이는 논문(AlignSentinel)의 Avg-first와 같은 계열이다(선형 평균 후 분류).
논문에서는 Avg-first(Acc~0.73-0.80)보다 Enc-first(각 토큰쌍을 먼저 비선형 인코딩한 뒤 pool,
Acc~0.92-0.96)가 확실히 우수했다. 즉 "평균 먼저 vs 인코딩 먼저"의 순서가 성능을 가른다.

재추출 없이 이미 만든 dump/*.npz의 g_prof(n, LH, bins) 로 같은 대비를 재현한다:
  - bin을 논문의 "토큰쌍"에 대응하는 단위로 보고, bin마다의 LH벡터를 작은 MLP(LH→128)로
    먼저 인코딩한 뒤 bin 축으로 mean-pool → Linear(128→3) 로 분류(=Enc-lite).
  - g_mean(먼저 bin 평균 → LH벡터 → 로지스틴 회귀)과 같은 프로토콜(in-domain CV, cross-domain LODO)로 비교.

bin(10개)은 논문의 실제 토큰쌍(수천 개)보다 훨씬 거친 근사이므로, 여기서 신호가 안 오르더라도
"진짜 Enc-first가 안 통한다"를 확정하진 못한다(스크리닝 용도). 반대로 여기서도 오르면
encode-before-pool 자체의 이득은 최소한 이 근사 수준에서도 존재한다는 뜻.

실행: python src/diag_enc_lite.py --dump dump --out results
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import torch
import torch.nn as nn

from diag_analyze import load_all, MIS  # 동일 로더 재사용


def parse_args():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--dump", default="dump")
    p.add_argument("--out", default="results")
    p.add_argument("--hidden-dim", type=int, default=128)
    p.add_argument("--epochs", type=int, default=200)
    p.add_argument("--lr", type=float, default=1e-2)
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--device", default="cuda" if torch.cuda.is_available() else "cpu")
    return p.parse_args()


class EncLite(nn.Module):
    """bin(LH벡터)을 128차원으로 인코딩 → bin 축 mean-pool → 3-class 분류. 논문 Enc-first 구조의 축소판."""

    def __init__(self, lh, hid):
        super().__init__()
        self.enc = nn.Sequential(nn.Linear(lh, hid), nn.ReLU())
        self.clf = nn.Sequential(nn.Linear(hid, hid), nn.ReLU(), nn.Linear(hid, 3))

    def forward(self, x):  # x: (B, bins, LH)
        z = self.enc(x)          # (B, bins, hid)
        pooled = z.mean(dim=1)   # (B, hid)  <- encode-before-pool
        return self.clf(pooled)


def train_eval(Xtr, ytr, Xte, yte, lh, hid, epochs, lr, seed, device):
    torch.manual_seed(seed)
    mu = Xtr.reshape(-1, lh).mean(0, keepdims=True)
    sd = Xtr.reshape(-1, lh).std(0, keepdims=True) + 1e-6

    def norm(x):
        return (x - mu) / sd

    Xtr_t = torch.tensor(norm(Xtr), dtype=torch.float32, device=device)
    ytr_t = torch.tensor(ytr, dtype=torch.long, device=device)
    Xte_t = torch.tensor(norm(Xte), dtype=torch.float32, device=device)

    model = EncLite(lh, hid).to(device)
    opt = torch.optim.Adam(model.parameters(), lr=lr)
    lossf = nn.CrossEntropyLoss()
    model.train()
    for _ in range(epochs):
        opt.zero_grad()
        out = model(Xtr_t)
        loss = lossf(out, ytr_t)
        loss.backward()
        opt.step()
    model.eval()
    with torch.no_grad():
        pred = model(Xte_t).argmax(1).cpu().numpy()
    return pred


def cv_enc_lite(Xg, y, lh, hid, epochs, lr, seed, device, k=5):
    from sklearn.model_selection import StratifiedKFold
    skf = StratifiedKFold(n_splits=k, shuffle=True, random_state=seed)
    yp = np.zeros_like(y)
    for tr, te in skf.split(Xg.reshape(len(y), -1), y):
        yp[te] = train_eval(Xg[tr], y[tr], Xg[te], y[te], lh, hid, epochs, lr, seed, device)
    return yp


def lodo_enc_lite(Xg, y, domain, lh, hid, epochs, lr, seed, device):
    f1s = []
    from sklearn.metrics import f1_score
    for d in np.unique(domain):
        tr, te = domain != d, domain == d
        if len(np.unique(y[tr])) < 2 or te.sum() == 0:
            continue
        pred = train_eval(Xg[tr], y[tr], Xg[te], y[te], lh, hid, epochs, lr, seed, device)
        f1s.append(f1_score(y[te], pred, average="macro"))
    return (float(np.mean(f1s)), float(np.min(f1s))) if f1s else (float("nan"), float("nan"))


def main():
    args = parse_args()
    dump, out = Path(args.dump), Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    meta, D = load_all(dump)
    y, dom = D["labels"], D["domain"]
    LH = meta["LH"]
    n = len(y)
    lines = []

    def w(s=""):
        lines.append(s)
        print(s)

    # g_prof: (n, LH, bins) -> (n, bins, LH)  bin을 "토큰쌍" 자리로
    Xg = D["g_prof"].transpose(0, 2, 1).astype(np.float32)
    bins = Xg.shape[1]

    w(f"# Enc-lite 검증 — encode-before-pool이 g_mean(Avg-style) 대비 오르는가  (model={meta['model_key']}, N={n})\n")
    w(f"- 입력: g_prof을 (bins={bins}, LH={LH})로 취급, bin마다 LH→{args.hidden_dim} MLP 인코딩 후 bin 축 mean-pool → Linear→3")
    w(f"- device={args.device}, epochs={args.epochs}, lr={args.lr}\n")

    from sklearn.metrics import f1_score, recall_score

    yp_cv = cv_enc_lite(Xg, y, LH, args.hidden_dim, args.epochs, args.lr, args.seed, args.device)
    acc = (yp_cv == y).mean()
    mf1 = f1_score(y, yp_cv, average="macro")
    mr = recall_score(y, yp_cv, labels=[MIS], average="macro")
    cmean, cworst = lodo_enc_lite(Xg, y, dom, LH, args.hidden_dim, args.epochs, args.lr, args.seed, args.device)

    w("| feature | in-domain acc | macroF1 | MIS recall | cross meanF1 | worstF1 |")
    w("|---|---|---|---|---|---|")
    w(f"| g_mean (Avg-style, 기존 diag①) | 0.775 | 0.775 | 0.740 | 0.738 | 0.674 |")
    w(f"| Enc-lite (encode-before-pool) | {acc:.3f} | {mf1:.3f} | {mr:.3f} | {cmean:.3f} | {cworst:.3f} |")
    w(f"| hidden-state 최고 (기존 diag③, L9_last) | 0.942 | 0.942 | 0.948 | 0.929 | 0.913 |")
    w("")

    delta = mf1 - 0.775
    w("## 판정 (자동)\n")
    w(f"- Δ macroF1 (Enc-lite − g_mean) = **{delta:+.3f}**")
    if delta > 0.05:
        w("→ encode-before-pool이 뚜렷하게 신호를 회복시킴. attention의 진짜 천장은 g_mean(0.775)보다 높다 "
          "→ 정통 Enc-first(전체 토큰쌍) 재현으로 hidden(0.94)과 정식 비교할 가치 있음.")
    elif delta > 0.02:
        w("→ 소폭 회복. bin 단위 근사로도 인코딩 이득이 있으나 hidden(0.94)과는 여전히 격차 큼 — "
          "정통 Enc-first가 이 격차를 메울지는 별도 확인 필요.")
    else:
        w("→ 거의 회복 안 됨. bin 단위로는 encode-before-pool의 이득이 안 보임 — "
          "다만 bin(10개)이 실제 토큰쌍(수천개)보다 훨씬 거친 근사라 이것만으로 "
          "'진짜 Enc-first도 안 통한다'를 확정할 수는 없음(스크리닝 한계).")
    w("\n---\n*참고: bins는 위치 프로파일 버킷(기본 10개)이며 논문의 실제 토큰쌍 수(샘플당 ~수천)보다 훨씬 성긴 근사다.*")

    report = out / "enc_lite_report.md"
    report.write_text("\n".join(lines), encoding="utf-8")
    print(f"\n리포트 → {report}")


if __name__ == "__main__":
    main()
