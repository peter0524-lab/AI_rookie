# entity-level 다수결 앙상블: test  (20260717_123053)

min_votes=1
data_dir=`/data/team/hwan/real/data/test_sets/combined`
evaluated_labels=18: `PS_NAME, LC_ADDRESS, OG_WORKPLACE, OG_DEPARTMENT, CV_POSITION, OGG_EDUCATION, QT_MOBILE, QT_PHONE, QT_RESIDENT_NUMBER, QT_DRIVER_NUMBER, QT_PLATE_NUMBER, QT_ACCOUNT_NUMBER, QT_CARD_NUMBER, TMI_EMAIL, QT_PASSPORT_NUMBER, QT_AGE, DT_BIRTH, FD_MAJOR`
excluded_labels=1: `QT_ALIEN_NUMBER`
excluded_gold_entities=9  excluded_predicted_entities=9

| Entity Micro F1 | **0.9177** |
| Precision | 0.9492 |
| Recall | 0.8882 |
| TP | 6985 | FP | 374 | FN | 879 |

| 레이블 | F1 | P | R | TP | FP | FN |
|--------|-----|---|---|----|----|-----|
| QT_MOBILE | 0.9942 | 0.9908 | 0.9977 | 431 | 4 | 1 |
| QT_PHONE | 0.9713 | 0.9478 | 0.9961 | 254 | 14 | 1 |
| QT_CARD_NUMBER | 0.9612 | 0.9817 | 0.9415 | 161 | 3 | 10 |
| PS_NAME | 0.9496 | 0.9754 | 0.9250 | 3257 | 82 | 264 |
| QT_RESIDENT_NUMBER | 0.9486 | 0.9022 | 1.0000 | 203 | 22 | 0 |
| DT_BIRTH | 0.9453 | 0.9828 | 0.9105 | 285 | 5 | 28 |
| OGG_EDUCATION | 0.9379 | 0.9891 | 0.8918 | 272 | 3 | 33 |
| QT_ACCOUNT_NUMBER | 0.9338 | 0.8912 | 0.9807 | 254 | 31 | 5 |
| QT_PLATE_NUMBER | 0.8870 | 1.0000 | 0.7969 | 51 | 0 | 13 |
| OG_WORKPLACE | 0.8775 | 0.8593 | 0.8964 | 580 | 95 | 67 |
| TMI_EMAIL | 0.8772 | 0.8530 | 0.9028 | 325 | 56 | 35 |
| LC_ADDRESS | 0.8248 | 0.9715 | 0.7165 | 273 | 8 | 108 |
| QT_PASSPORT_NUMBER | 0.8235 | 1.0000 | 0.7000 | 14 | 0 | 6 |
| QT_DRIVER_NUMBER | 0.8163 | 0.8000 | 0.8333 | 20 | 5 | 4 |
| OG_DEPARTMENT | 0.8090 | 0.9515 | 0.7036 | 216 | 11 | 91 |
| FD_MAJOR | 0.7948 | 0.9839 | 0.6667 | 122 | 2 | 61 |
| QT_AGE | 0.7829 | 0.8623 | 0.7169 | 119 | 19 | 47 |
| CV_POSITION | 0.7133 | 0.9136 | 0.5850 | 148 | 14 | 105 |