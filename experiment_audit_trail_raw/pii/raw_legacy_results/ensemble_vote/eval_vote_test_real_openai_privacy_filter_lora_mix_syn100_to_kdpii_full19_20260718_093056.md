# entity-level 다수결 앙상블: test  (20260718_093056)

min_votes=1
data_dir=`/data/team/hwan/real/data/test_sets/kdpii`
evaluated_labels=19: `PS_NAME, LC_ADDRESS, OG_WORKPLACE, OG_DEPARTMENT, CV_POSITION, OGG_EDUCATION, QT_MOBILE, QT_PHONE, QT_RESIDENT_NUMBER, QT_ALIEN_NUMBER, QT_DRIVER_NUMBER, QT_PLATE_NUMBER, QT_ACCOUNT_NUMBER, QT_CARD_NUMBER, TMI_EMAIL, QT_PASSPORT_NUMBER, QT_AGE, DT_BIRTH, FD_MAJOR`
excluded_labels=0: `-`
excluded_gold_entities=0  excluded_predicted_entities=0

| Entity Micro F1 | **0.5710** |
| Precision | 0.9104 |
| Recall | 0.4159 |
| TP | 569 | FP | 56 | FN | 799 |

| 레이블 | F1 | P | R | TP | FP | FN |
|--------|-----|---|---|----|----|-----|
| QT_MOBILE | 1.0000 | 1.0000 | 1.0000 | 55 | 0 | 0 |
| QT_RESIDENT_NUMBER | 1.0000 | 1.0000 | 1.0000 | 18 | 0 | 0 |
| QT_ALIEN_NUMBER | 1.0000 | 1.0000 | 1.0000 | 9 | 0 | 0 |
| QT_PHONE | 0.9928 | 0.9857 | 1.0000 | 69 | 1 | 0 |
| DT_BIRTH | 0.9714 | 0.9714 | 0.9714 | 68 | 2 | 2 |
| QT_PLATE_NUMBER | 0.9703 | 1.0000 | 0.9423 | 49 | 0 | 3 |
| QT_CARD_NUMBER | 0.9459 | 1.0000 | 0.8974 | 70 | 0 | 8 |
| QT_ACCOUNT_NUMBER | 0.9000 | 1.0000 | 0.8182 | 63 | 0 | 14 |
| QT_AGE | 0.6875 | 0.8250 | 0.5893 | 33 | 7 | 23 |
| QT_DRIVER_NUMBER | 0.6400 | 1.0000 | 0.4706 | 8 | 0 | 9 |
| TMI_EMAIL | 0.5000 | 1.0000 | 0.3333 | 27 | 0 | 54 |
| PS_NAME | 0.3780 | 0.6234 | 0.2712 | 48 | 29 | 129 |
| CV_POSITION | 0.2585 | 0.8261 | 0.1532 | 19 | 4 | 105 |
| LC_ADDRESS | 0.2261 | 0.9286 | 0.1287 | 13 | 1 | 88 |
| OGG_EDUCATION | 0.1176 | 0.4615 | 0.0674 | 6 | 7 | 83 |
| OG_DEPARTMENT | 0.1143 | 1.0000 | 0.0606 | 6 | 0 | 93 |
| QT_PASSPORT_NUMBER | 0.1053 | 1.0000 | 0.0556 | 1 | 0 | 17 |
| FD_MAJOR | 0.0870 | 0.7500 | 0.0462 | 3 | 1 | 62 |
| OG_WORKPLACE | 0.0661 | 0.5000 | 0.0354 | 4 | 4 | 109 |