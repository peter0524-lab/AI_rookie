# entity-level 다수결 앙상블: test  (20260717_153452)

min_votes=1
data_dir=`/data/team/hwan/real/data/test_sets/combined`
evaluated_labels=19: `PS_NAME, LC_ADDRESS, OG_WORKPLACE, OG_DEPARTMENT, CV_POSITION, OGG_EDUCATION, QT_MOBILE, QT_PHONE, QT_RESIDENT_NUMBER, QT_ALIEN_NUMBER, QT_DRIVER_NUMBER, QT_PLATE_NUMBER, QT_ACCOUNT_NUMBER, QT_CARD_NUMBER, TMI_EMAIL, QT_PASSPORT_NUMBER, QT_AGE, DT_BIRTH, FD_MAJOR`
excluded_labels=0: `-`
excluded_gold_entities=0  excluded_predicted_entities=0

| Entity Micro F1 | **0.9665** |
| Precision | 0.9881 |
| Recall | 0.9459 |
| TP | 7447 | FP | 90 | FN | 426 |

| 레이블 | F1 | P | R | TP | FP | FN |
|--------|-----|---|---|----|----|-----|
| QT_RESIDENT_NUMBER | 1.0000 | 1.0000 | 1.0000 | 203 | 0 | 0 |
| QT_ALIEN_NUMBER | 1.0000 | 1.0000 | 1.0000 | 9 | 0 | 0 |
| QT_DRIVER_NUMBER | 1.0000 | 1.0000 | 1.0000 | 24 | 0 | 0 |
| QT_PASSPORT_NUMBER | 1.0000 | 1.0000 | 1.0000 | 20 | 0 | 0 |
| QT_MOBILE | 0.9988 | 1.0000 | 0.9977 | 431 | 0 | 1 |
| QT_PHONE | 0.9980 | 0.9961 | 1.0000 | 255 | 1 | 0 |
| QT_CARD_NUMBER | 0.9971 | 0.9942 | 1.0000 | 171 | 1 | 0 |
| QT_PLATE_NUMBER | 0.9922 | 0.9846 | 1.0000 | 64 | 1 | 0 |
| OGG_EDUCATION | 0.9917 | 1.0000 | 0.9836 | 300 | 0 | 5 |
| QT_ACCOUNT_NUMBER | 0.9903 | 0.9961 | 0.9846 | 255 | 1 | 4 |
| FD_MAJOR | 0.9783 | 0.9730 | 0.9836 | 180 | 5 | 3 |
| DT_BIRTH | 0.9697 | 0.9682 | 0.9712 | 304 | 10 | 9 |
| PS_NAME | 0.9635 | 0.9964 | 0.9327 | 3284 | 12 | 237 |
| LC_ADDRESS | 0.9610 | 0.9862 | 0.9370 | 357 | 5 | 24 |
| QT_AGE | 0.9504 | 0.9209 | 0.9819 | 163 | 14 | 3 |
| TMI_EMAIL | 0.9489 | 1.0000 | 0.9028 | 325 | 0 | 35 |
| OG_WORKPLACE | 0.9488 | 0.9834 | 0.9165 | 593 | 10 | 54 |
| OG_DEPARTMENT | 0.9416 | 0.9658 | 0.9186 | 282 | 10 | 25 |
| CV_POSITION | 0.9080 | 0.9190 | 0.8972 | 227 | 20 | 26 |