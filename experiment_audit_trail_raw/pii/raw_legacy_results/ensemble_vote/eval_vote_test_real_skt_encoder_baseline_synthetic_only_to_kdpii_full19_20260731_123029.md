# entity-level 다수결 앙상블: test  (20260731_123029)

min_votes=1
data_dir=`/data/team/hwan/real/data/test_sets/kdpii`
evaluated_labels=19: `PS_NAME, LC_ADDRESS, OG_WORKPLACE, OG_DEPARTMENT, CV_POSITION, OGG_EDUCATION, QT_MOBILE, QT_PHONE, QT_RESIDENT_NUMBER, QT_ALIEN_NUMBER, QT_DRIVER_NUMBER, QT_PLATE_NUMBER, QT_ACCOUNT_NUMBER, QT_CARD_NUMBER, TMI_EMAIL, QT_PASSPORT_NUMBER, QT_AGE, DT_BIRTH, FD_MAJOR`
excluded_labels=0: `-`
excluded_gold_entities=0  excluded_predicted_entities=0

| Entity Micro F1 | **0.5594** |
| Precision | 0.6180 |
| Recall | 0.5110 |
| TP | 699 | FP | 432 | FN | 669 |

| 레이블 | F1 | P | R | TP | FP | FN |
|--------|-----|---|---|----|----|-----|
| QT_MOBILE | 1.0000 | 1.0000 | 1.0000 | 55 | 0 | 0 |
| QT_ALIEN_NUMBER | 1.0000 | 1.0000 | 1.0000 | 9 | 0 | 0 |
| QT_RESIDENT_NUMBER | 0.9474 | 0.9000 | 1.0000 | 18 | 2 | 0 |
| QT_PHONE | 0.9371 | 0.9054 | 0.9710 | 67 | 7 | 2 |
| QT_PASSPORT_NUMBER | 0.8125 | 0.9286 | 0.7222 | 13 | 1 | 5 |
| QT_CARD_NUMBER | 0.7907 | 1.0000 | 0.6538 | 51 | 0 | 27 |
| TMI_EMAIL | 0.7889 | 0.7172 | 0.8765 | 71 | 28 | 10 |
| QT_DRIVER_NUMBER | 0.7407 | 1.0000 | 0.5882 | 10 | 0 | 7 |
| QT_ACCOUNT_NUMBER | 0.7328 | 0.8889 | 0.6234 | 48 | 6 | 29 |
| PS_NAME | 0.6667 | 0.5620 | 0.8192 | 145 | 113 | 32 |
| OGG_EDUCATION | 0.5846 | 0.9268 | 0.4270 | 38 | 3 | 51 |
| DT_BIRTH | 0.5660 | 0.8333 | 0.4286 | 30 | 6 | 40 |
| OG_WORKPLACE | 0.4548 | 0.3656 | 0.6018 | 68 | 118 | 45 |
| OG_DEPARTMENT | 0.3650 | 0.6579 | 0.2525 | 25 | 13 | 74 |
| QT_PLATE_NUMBER | 0.3535 | 0.2397 | 0.6731 | 35 | 111 | 17 |
| CV_POSITION | 0.2014 | 0.9333 | 0.1129 | 14 | 1 | 110 |
| QT_AGE | 0.0548 | 0.1176 | 0.0357 | 2 | 15 | 54 |
| LC_ADDRESS | 0.0000 | 0.0000 | 0.0000 | 0 | 7 | 101 |
| FD_MAJOR | 0.0000 | 0.0000 | 0.0000 | 0 | 1 | 65 |