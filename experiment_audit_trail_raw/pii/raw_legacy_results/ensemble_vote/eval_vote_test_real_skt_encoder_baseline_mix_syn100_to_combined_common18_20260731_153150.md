# entity-level 다수결 앙상블: test  (20260731_153150)

min_votes=1
data_dir=`/data/team/hwan/real/data/test_sets/combined`
evaluated_labels=18: `PS_NAME, LC_ADDRESS, OG_WORKPLACE, OG_DEPARTMENT, CV_POSITION, OGG_EDUCATION, QT_MOBILE, QT_PHONE, QT_RESIDENT_NUMBER, QT_DRIVER_NUMBER, QT_PLATE_NUMBER, QT_ACCOUNT_NUMBER, QT_CARD_NUMBER, TMI_EMAIL, QT_PASSPORT_NUMBER, QT_AGE, DT_BIRTH, FD_MAJOR`
excluded_labels=1: `QT_ALIEN_NUMBER`
excluded_gold_entities=9  excluded_predicted_entities=9

| Entity Micro F1 | **0.9626** |
| Precision | 0.9823 |
| Recall | 0.9438 |
| TP | 7422 | FP | 134 | FN | 442 |

| 레이블 | F1 | P | R | TP | FP | FN |
|--------|-----|---|---|----|----|-----|
| QT_MOBILE | 1.0000 | 1.0000 | 1.0000 | 432 | 0 | 0 |
| QT_RESIDENT_NUMBER | 1.0000 | 1.0000 | 1.0000 | 203 | 0 | 0 |
| QT_DRIVER_NUMBER | 1.0000 | 1.0000 | 1.0000 | 24 | 0 | 0 |
| QT_PASSPORT_NUMBER | 1.0000 | 1.0000 | 1.0000 | 20 | 0 | 0 |
| QT_PHONE | 0.9961 | 0.9922 | 1.0000 | 255 | 2 | 0 |
| QT_CARD_NUMBER | 0.9913 | 0.9828 | 1.0000 | 171 | 3 | 0 |
| QT_ACCOUNT_NUMBER | 0.9883 | 0.9961 | 0.9807 | 254 | 1 | 5 |
| OGG_EDUCATION | 0.9868 | 0.9934 | 0.9803 | 299 | 2 | 6 |
| DT_BIRTH | 0.9726 | 0.9805 | 0.9649 | 302 | 6 | 11 |
| TMI_EMAIL | 0.9685 | 1.0000 | 0.9389 | 338 | 0 | 22 |
| PS_NAME | 0.9675 | 0.9937 | 0.9426 | 3319 | 21 | 202 |
| QT_PLATE_NUMBER | 0.9600 | 0.9836 | 0.9375 | 60 | 1 | 4 |
| FD_MAJOR | 0.9596 | 0.9468 | 0.9727 | 178 | 10 | 5 |
| LC_ADDRESS | 0.9483 | 0.9572 | 0.9396 | 358 | 16 | 23 |
| OG_WORKPLACE | 0.9295 | 0.9651 | 0.8964 | 580 | 21 | 67 |
| QT_AGE | 0.9204 | 0.9017 | 0.9398 | 156 | 17 | 10 |
| OG_DEPARTMENT | 0.8900 | 0.9418 | 0.8436 | 259 | 16 | 48 |
| CV_POSITION | 0.8825 | 0.9224 | 0.8458 | 214 | 18 | 39 |