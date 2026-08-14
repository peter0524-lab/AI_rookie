# entity-level 다수결 앙상블: test  (20260731_153050)

min_votes=1
data_dir=`/data/team/hwan/real/data/test_sets/kdpii`
evaluated_labels=18: `PS_NAME, LC_ADDRESS, OG_WORKPLACE, OG_DEPARTMENT, CV_POSITION, OGG_EDUCATION, QT_MOBILE, QT_PHONE, QT_RESIDENT_NUMBER, QT_DRIVER_NUMBER, QT_PLATE_NUMBER, QT_ACCOUNT_NUMBER, QT_CARD_NUMBER, TMI_EMAIL, QT_PASSPORT_NUMBER, QT_AGE, DT_BIRTH, FD_MAJOR`
excluded_labels=1: `QT_ALIEN_NUMBER`
excluded_gold_entities=9  excluded_predicted_entities=9

| Entity Micro F1 | **0.9319** |
| Precision | 0.9538 |
| Recall | 0.9110 |
| TP | 1238 | FP | 60 | FN | 121 |

| 레이블 | F1 | P | R | TP | FP | FN |
|--------|-----|---|---|----|----|-----|
| QT_MOBILE | 1.0000 | 1.0000 | 1.0000 | 55 | 0 | 0 |
| QT_PHONE | 1.0000 | 1.0000 | 1.0000 | 69 | 0 | 0 |
| QT_RESIDENT_NUMBER | 1.0000 | 1.0000 | 1.0000 | 18 | 0 | 0 |
| QT_DRIVER_NUMBER | 1.0000 | 1.0000 | 1.0000 | 17 | 0 | 0 |
| TMI_EMAIL | 1.0000 | 1.0000 | 1.0000 | 81 | 0 | 0 |
| QT_PASSPORT_NUMBER | 1.0000 | 1.0000 | 1.0000 | 18 | 0 | 0 |
| QT_CARD_NUMBER | 0.9873 | 0.9750 | 1.0000 | 78 | 2 | 0 |
| QT_ACCOUNT_NUMBER | 0.9804 | 0.9868 | 0.9740 | 75 | 1 | 2 |
| DT_BIRTH | 0.9710 | 0.9853 | 0.9571 | 67 | 1 | 3 |
| QT_PLATE_NUMBER | 0.9600 | 1.0000 | 0.9231 | 48 | 0 | 4 |
| OGG_EDUCATION | 0.9540 | 0.9765 | 0.9326 | 83 | 2 | 6 |
| OG_DEPARTMENT | 0.9529 | 0.9891 | 0.9192 | 91 | 1 | 8 |
| FD_MAJOR | 0.9524 | 0.9836 | 0.9231 | 60 | 1 | 5 |
| QT_AGE | 0.9369 | 0.9455 | 0.9286 | 52 | 3 | 4 |
| PS_NAME | 0.8940 | 0.9070 | 0.8814 | 156 | 16 | 21 |
| LC_ADDRESS | 0.8713 | 0.8713 | 0.8713 | 88 | 13 | 13 |
| CV_POSITION | 0.8584 | 0.9174 | 0.8065 | 100 | 9 | 24 |
| OG_WORKPLACE | 0.7961 | 0.8817 | 0.7257 | 82 | 11 | 31 |