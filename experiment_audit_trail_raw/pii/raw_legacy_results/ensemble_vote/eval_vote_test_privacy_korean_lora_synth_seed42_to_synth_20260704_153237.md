# entity-level 다수결 앙상블: test  (20260704_153237)

min_votes=1
data_dir=`/data/team/hwan/synthetic`
evaluated_labels=19: `PS_NAME, LC_ADDRESS, OG_WORKPLACE, OG_DEPARTMENT, CV_POSITION, OGG_EDUCATION, QT_MOBILE, QT_PHONE, QT_RESIDENT_NUMBER, QT_ALIEN_NUMBER, QT_DRIVER_NUMBER, QT_PLATE_NUMBER, QT_ACCOUNT_NUMBER, QT_CARD_NUMBER, TMI_EMAIL, QT_PASSPORT_NUMBER, QT_AGE, DT_BIRTH, FD_MAJOR`
excluded_labels=0: `-`
excluded_gold_entities=0  excluded_predicted_entities=0

| Entity Micro F1 | **0.5195** |
| Precision | 0.9819 |
| Recall | 0.3532 |
| TP | 487 | FP | 9 | FN | 892 |

| 레이블 | F1 | P | R | TP | FP | FN |
|--------|-----|---|---|----|----|-----|
| QT_PLATE_NUMBER | 1.0000 | 1.0000 | 1.0000 | 8 | 0 | 0 |
| QT_CARD_NUMBER | 1.0000 | 1.0000 | 1.0000 | 27 | 0 | 0 |
| QT_MOBILE | 0.9960 | 0.9919 | 1.0000 | 123 | 1 | 0 |
| QT_PHONE | 0.9934 | 0.9868 | 1.0000 | 75 | 1 | 0 |
| QT_RESIDENT_NUMBER | 0.9677 | 0.9375 | 1.0000 | 15 | 1 | 0 |
| DT_BIRTH | 0.9344 | 1.0000 | 0.8769 | 57 | 0 | 8 |
| QT_ACCOUNT_NUMBER | 0.9038 | 1.0000 | 0.8246 | 47 | 0 | 10 |
| QT_DRIVER_NUMBER | 0.8571 | 0.7500 | 1.0000 | 3 | 1 | 0 |
| PS_NAME | 0.3239 | 0.9632 | 0.1947 | 131 | 5 | 542 |
| TMI_EMAIL | 0.0142 | 1.0000 | 0.0071 | 1 | 0 | 139 |
| LC_ADDRESS | 0.0000 | 0.0000 | 0.0000 | 0 | 0 | 98 |
| OG_WORKPLACE | 0.0000 | 0.0000 | 0.0000 | 0 | 0 | 48 |
| OG_DEPARTMENT | 0.0000 | 0.0000 | 0.0000 | 0 | 0 | 27 |
| CV_POSITION | 0.0000 | 0.0000 | 0.0000 | 0 | 0 | 11 |
| OGG_EDUCATION | 0.0000 | 0.0000 | 0.0000 | 0 | 0 | 0 |
| QT_ALIEN_NUMBER | 0.0000 | 0.0000 | 0.0000 | 0 | 0 | 0 |
| QT_PASSPORT_NUMBER | 0.0000 | 0.0000 | 0.0000 | 0 | 0 | 9 |
| QT_AGE | 0.0000 | 0.0000 | 0.0000 | 0 | 0 | 0 |
| FD_MAJOR | 0.0000 | 0.0000 | 0.0000 | 0 | 0 | 0 |