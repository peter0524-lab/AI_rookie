# entity-level 다수결 앙상블: test  (20260704_153200)

min_votes=1
data_dir=`/data/team/hwan/data`
evaluated_labels=15: `PS_NAME, LC_ADDRESS, OG_WORKPLACE, OG_DEPARTMENT, CV_POSITION, QT_MOBILE, QT_PHONE, QT_RESIDENT_NUMBER, QT_DRIVER_NUMBER, QT_PLATE_NUMBER, QT_ACCOUNT_NUMBER, QT_CARD_NUMBER, TMI_EMAIL, QT_PASSPORT_NUMBER, DT_BIRTH`
excluded_labels=4: `OGG_EDUCATION, QT_ALIEN_NUMBER, QT_AGE, FD_MAJOR`
excluded_gold_entities=219  excluded_predicted_entities=9

| Entity Micro F1 | **0.7009** |
| Precision | 0.7639 |
| Recall | 0.6475 |
| TP | 744 | FP | 230 | FN | 405 |

| 레이블 | F1 | P | R | TP | FP | FN |
|--------|-----|---|---|----|----|-----|
| QT_PASSPORT_NUMBER | 1.0000 | 1.0000 | 1.0000 | 18 | 0 | 0 |
| QT_CARD_NUMBER | 0.9427 | 0.9367 | 0.9487 | 74 | 5 | 4 |
| QT_MOBILE | 0.9138 | 0.8689 | 0.9636 | 53 | 8 | 2 |
| QT_PHONE | 0.9128 | 0.8500 | 0.9855 | 68 | 12 | 1 |
| QT_RESIDENT_NUMBER | 0.8780 | 0.7826 | 1.0000 | 18 | 5 | 0 |
| QT_ACCOUNT_NUMBER | 0.8242 | 0.7143 | 0.9740 | 75 | 30 | 2 |
| TMI_EMAIL | 0.8061 | 0.6870 | 0.9753 | 79 | 36 | 2 |
| PS_NAME | 0.7747 | 0.7540 | 0.7966 | 141 | 46 | 36 |
| QT_DRIVER_NUMBER | 0.7333 | 0.8462 | 0.6471 | 11 | 2 | 6 |
| DT_BIRTH | 0.7193 | 0.9318 | 0.5857 | 41 | 3 | 29 |
| QT_PLATE_NUMBER | 0.6585 | 0.9000 | 0.5192 | 27 | 3 | 25 |
| OG_WORKPLACE | 0.5812 | 0.5620 | 0.6018 | 68 | 53 | 45 |
| CV_POSITION | 0.4074 | 0.8684 | 0.2661 | 33 | 5 | 91 |
| OG_DEPARTMENT | 0.3885 | 0.6750 | 0.2727 | 27 | 13 | 72 |
| LC_ADDRESS | 0.1818 | 0.5500 | 0.1089 | 11 | 9 | 90 |