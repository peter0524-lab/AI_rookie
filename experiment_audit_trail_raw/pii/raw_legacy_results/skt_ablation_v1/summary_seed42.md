# SKT Ablation v1 Summary

| variant | train | KDPII full-19 | KDPII common-15 | synthetic test |
|---|---|---:|---:|---:|
| plain | mixed | 0.9247 | 0.9216 | 0.9422 |
| plain_distill | kdpii | 0.9283 | 0.9258 | 0.8030 |
| plain_distill | synthetic | - | 0.5394 | 0.9337 |
| plain_distill | mixed | 0.9255 | 0.9225 | 0.9463 |
| crf | kdpii | 0.9606 | 0.9587 | 0.8496 |
| crf | synthetic | - | 0.6622 | 0.9522 |
| crf | mixed | 0.9599 | 0.9561 | 0.9511 |
| gaz | kdpii | 0.9647 | 0.9637 | 0.8649 |
| gaz | synthetic | - | 0.6335 | 0.9511 |
| gaz | mixed | 0.9623 | 0.9604 | 0.9492 |
| crf_gaz | kdpii | 0.9601 | 0.9576 | 0.8356 |
| crf_gaz | synthetic | - | 0.6431 | 0.9530 |
| crf_gaz | mixed | 0.9581 | 0.9562 | 0.9500 |
