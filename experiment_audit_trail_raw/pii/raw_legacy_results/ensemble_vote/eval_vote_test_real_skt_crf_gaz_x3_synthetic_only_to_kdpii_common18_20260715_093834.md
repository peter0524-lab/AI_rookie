# entity-level 다수결 앙상블: test  (20260715_093834)

min_votes=2
data_dir=`/data/team/hwan/real/data/test_sets/kdpii`
evaluated_labels=18: `PS_NAME, LC_ADDRESS, OG_WORKPLACE, OG_DEPARTMENT, CV_POSITION, OGG_EDUCATION, QT_MOBILE, QT_PHONE, QT_RESIDENT_NUMBER, QT_DRIVER_NUMBER, QT_PLATE_NUMBER, QT_ACCOUNT_NUMBER, QT_CARD_NUMBER, TMI_EMAIL, QT_PASSPORT_NUMBER, QT_AGE, DT_BIRTH, FD_MAJOR`
excluded_labels=1: `QT_ALIEN_NUMBER`
excluded_gold_entities=9  excluded_predicted_entities=9

| Entity Micro F1 | **0.6620** |
| Precision | 0.8205 |
| Recall | 0.5548 |
| TP | 754 | FP | 165 | FN | 605 |

| 레이블 | F1 | P | R | TP | FP | FN |
|--------|-----|---|---|----|----|-----|
| QT_MOBILE | 1.0000 | 1.0000 | 1.0000 | 55 | 0 | 0 |
| QT_DRIVER_NUMBER | 1.0000 | 1.0000 | 1.0000 | 17 | 0 | 0 |
| TMI_EMAIL | 1.0000 | 1.0000 | 1.0000 | 81 | 0 | 0 |
| QT_PASSPORT_NUMBER | 1.0000 | 1.0000 | 1.0000 | 18 | 0 | 0 |
| QT_PHONE | 0.9853 | 1.0000 | 0.9710 | 67 | 0 | 2 |
| QT_RESIDENT_NUMBER | 0.9000 | 0.8182 | 1.0000 | 18 | 4 | 0 |
| DT_BIRTH | 0.8346 | 0.9298 | 0.7571 | 53 | 4 | 17 |
| QT_ACCOUNT_NUMBER | 0.8092 | 0.7292 | 0.9091 | 70 | 26 | 7 |
| QT_CARD_NUMBER | 0.7907 | 1.0000 | 0.6538 | 51 | 0 | 27 |
| PS_NAME | 0.6950 | 0.6550 | 0.7401 | 131 | 69 | 46 |
| OGG_EDUCATION | 0.6569 | 0.9375 | 0.5056 | 45 | 3 | 44 |
| OG_WORKPLACE | 0.5479 | 0.5660 | 0.5310 | 60 | 46 | 53 |
| QT_AGE | 0.5111 | 0.6765 | 0.4107 | 23 | 11 | 33 |
| OG_DEPARTMENT | 0.4032 | 1.0000 | 0.2525 | 25 | 0 | 74 |
| QT_PLATE_NUMBER | 0.2951 | 1.0000 | 0.1731 | 9 | 0 | 43 |
| LC_ADDRESS | 0.2564 | 0.9375 | 0.1485 | 15 | 1 | 86 |
| CV_POSITION | 0.2270 | 0.9412 | 0.1290 | 16 | 1 | 108 |
| FD_MAJOR | 0.0000 | 0.0000 | 0.0000 | 0 | 0 | 65 |