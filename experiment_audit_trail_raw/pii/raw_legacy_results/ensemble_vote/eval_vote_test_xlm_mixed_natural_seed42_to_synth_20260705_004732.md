# entity-level 다수결 앙상블: test  (20260705_004732)

min_votes=1
data_dir=`/data/team/hwan/synthetic`
evaluated_labels=19: `PS_NAME, LC_ADDRESS, OG_WORKPLACE, OG_DEPARTMENT, CV_POSITION, OGG_EDUCATION, QT_MOBILE, QT_PHONE, QT_RESIDENT_NUMBER, QT_ALIEN_NUMBER, QT_DRIVER_NUMBER, QT_PLATE_NUMBER, QT_ACCOUNT_NUMBER, QT_CARD_NUMBER, TMI_EMAIL, QT_PASSPORT_NUMBER, QT_AGE, DT_BIRTH, FD_MAJOR`
excluded_labels=0: `-`
excluded_gold_entities=0  excluded_predicted_entities=0

| Entity Micro F1 | **0.9429** |
| Precision | 0.9920 |
| Recall | 0.8985 |
| TP | 1239 | FP | 10 | FN | 140 |

| 레이블 | F1 | P | R | TP | FP | FN |
|--------|-----|---|---|----|----|-----|
| QT_RESIDENT_NUMBER | 1.0000 | 1.0000 | 1.0000 | 15 | 0 | 0 |
| QT_DRIVER_NUMBER | 1.0000 | 1.0000 | 1.0000 | 3 | 0 | 0 |
| QT_PLATE_NUMBER | 1.0000 | 1.0000 | 1.0000 | 8 | 0 | 0 |
| QT_PASSPORT_NUMBER | 1.0000 | 1.0000 | 1.0000 | 9 | 0 | 0 |
| QT_PHONE | 0.9934 | 0.9868 | 1.0000 | 75 | 1 | 0 |
| QT_MOBILE | 0.9880 | 0.9762 | 1.0000 | 123 | 3 | 0 |
| QT_CARD_NUMBER | 0.9818 | 0.9643 | 1.0000 | 27 | 1 | 0 |
| PS_NAME | 0.9427 | 1.0000 | 0.8915 | 600 | 0 | 73 |
| DT_BIRTH | 0.9344 | 1.0000 | 0.8769 | 57 | 0 | 8 |
| OG_WORKPLACE | 0.9247 | 0.9556 | 0.8958 | 43 | 2 | 5 |
| OG_DEPARTMENT | 0.9231 | 0.9600 | 0.8889 | 24 | 1 | 3 |
| QT_ACCOUNT_NUMBER | 0.9143 | 1.0000 | 0.8421 | 48 | 0 | 9 |
| TMI_EMAIL | 0.9105 | 1.0000 | 0.8357 | 117 | 0 | 23 |
| LC_ADDRESS | 0.9050 | 1.0000 | 0.8265 | 81 | 0 | 17 |
| CV_POSITION | 0.8571 | 0.9000 | 0.8182 | 9 | 1 | 2 |
| OGG_EDUCATION | 0.0000 | 0.0000 | 0.0000 | 0 | 0 | 0 |
| QT_ALIEN_NUMBER | 0.0000 | 0.0000 | 0.0000 | 0 | 0 | 0 |
| QT_AGE | 0.0000 | 0.0000 | 0.0000 | 0 | 1 | 0 |
| FD_MAJOR | 0.0000 | 0.0000 | 0.0000 | 0 | 0 | 0 |