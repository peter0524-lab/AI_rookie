# entity-level 다수결 앙상블: test  (20260718_051339)

min_votes=1
data_dir=`/data/team/hwan/real/data/test_sets/kdpii`
evaluated_labels=19: `PS_NAME, LC_ADDRESS, OG_WORKPLACE, OG_DEPARTMENT, CV_POSITION, OGG_EDUCATION, QT_MOBILE, QT_PHONE, QT_RESIDENT_NUMBER, QT_ALIEN_NUMBER, QT_DRIVER_NUMBER, QT_PLATE_NUMBER, QT_ACCOUNT_NUMBER, QT_CARD_NUMBER, TMI_EMAIL, QT_PASSPORT_NUMBER, QT_AGE, DT_BIRTH, FD_MAJOR`
excluded_labels=0: `-`
excluded_gold_entities=0  excluded_predicted_entities=0

| Entity Micro F1 | **0.5803** |
| Precision | 0.9192 |
| Recall | 0.4240 |
| TP | 580 | FP | 51 | FN | 788 |

| 레이블 | F1 | P | R | TP | FP | FN |
|--------|-----|---|---|----|----|-----|
| QT_MOBILE | 1.0000 | 1.0000 | 1.0000 | 55 | 0 | 0 |
| QT_PHONE | 1.0000 | 1.0000 | 1.0000 | 69 | 0 | 0 |
| QT_RESIDENT_NUMBER | 1.0000 | 1.0000 | 1.0000 | 18 | 0 | 0 |
| QT_ALIEN_NUMBER | 1.0000 | 1.0000 | 1.0000 | 9 | 0 | 0 |
| DT_BIRTH | 0.9859 | 0.9722 | 1.0000 | 70 | 2 | 0 |
| QT_PLATE_NUMBER | 0.9703 | 1.0000 | 0.9423 | 49 | 0 | 3 |
| QT_CARD_NUMBER | 0.9530 | 1.0000 | 0.9103 | 71 | 0 | 7 |
| QT_ACCOUNT_NUMBER | 0.9000 | 1.0000 | 0.8182 | 63 | 0 | 14 |
| QT_AGE | 0.6596 | 0.8158 | 0.5536 | 31 | 7 | 25 |
| QT_DRIVER_NUMBER | 0.6400 | 1.0000 | 0.4706 | 8 | 0 | 9 |
| TMI_EMAIL | 0.5000 | 1.0000 | 0.3333 | 27 | 0 | 54 |
| PS_NAME | 0.4130 | 0.7286 | 0.2881 | 51 | 19 | 126 |
| CV_POSITION | 0.2819 | 0.8400 | 0.1694 | 21 | 4 | 103 |
| LC_ADDRESS | 0.2124 | 1.0000 | 0.1188 | 12 | 0 | 89 |
| OG_DEPARTMENT | 0.1930 | 0.7333 | 0.1111 | 11 | 4 | 88 |
| OGG_EDUCATION | 0.1212 | 0.6000 | 0.0674 | 6 | 4 | 83 |
| FD_MAJOR | 0.1127 | 0.6667 | 0.0615 | 4 | 2 | 61 |
| QT_PASSPORT_NUMBER | 0.1053 | 1.0000 | 0.0556 | 1 | 0 | 17 |
| OG_WORKPLACE | 0.0635 | 0.3077 | 0.0354 | 4 | 9 | 109 |