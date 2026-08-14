# entity-level 다수결 앙상블: test  (20260705_072942)

min_votes=1
data_dir=`/data/team/hwan/synthetic`
evaluated_labels=19: `PS_NAME, LC_ADDRESS, OG_WORKPLACE, OG_DEPARTMENT, CV_POSITION, OGG_EDUCATION, QT_MOBILE, QT_PHONE, QT_RESIDENT_NUMBER, QT_ALIEN_NUMBER, QT_DRIVER_NUMBER, QT_PLATE_NUMBER, QT_ACCOUNT_NUMBER, QT_CARD_NUMBER, TMI_EMAIL, QT_PASSPORT_NUMBER, QT_AGE, DT_BIRTH, FD_MAJOR`
excluded_labels=0: `-`
excluded_gold_entities=0  excluded_predicted_entities=0

| Entity Micro F1 | **0.9422** |
| Precision | 0.9834 |
| Recall | 0.9043 |
| TP | 1247 | FP | 21 | FN | 132 |

| 레이블 | F1 | P | R | TP | FP | FN |
|--------|-----|---|---|----|----|-----|
| QT_RESIDENT_NUMBER | 1.0000 | 1.0000 | 1.0000 | 15 | 0 | 0 |
| QT_DRIVER_NUMBER | 1.0000 | 1.0000 | 1.0000 | 3 | 0 | 0 |
| QT_MOBILE | 0.9960 | 0.9919 | 1.0000 | 123 | 1 | 0 |
| QT_PHONE | 0.9934 | 0.9868 | 1.0000 | 75 | 1 | 0 |
| QT_CARD_NUMBER | 0.9643 | 0.9310 | 1.0000 | 27 | 2 | 0 |
| PS_NAME | 0.9486 | 0.9967 | 0.9049 | 609 | 2 | 64 |
| QT_PLATE_NUMBER | 0.9412 | 0.8889 | 1.0000 | 8 | 1 | 0 |
| QT_PASSPORT_NUMBER | 0.9412 | 1.0000 | 0.8889 | 8 | 0 | 1 |
| TMI_EMAIL | 0.9313 | 1.0000 | 0.8714 | 122 | 0 | 18 |
| OG_WORKPLACE | 0.9231 | 0.9767 | 0.8750 | 42 | 1 | 6 |
| DT_BIRTH | 0.9167 | 1.0000 | 0.8462 | 55 | 0 | 10 |
| QT_ACCOUNT_NUMBER | 0.9038 | 1.0000 | 0.8246 | 47 | 0 | 10 |
| LC_ADDRESS | 0.9011 | 0.9762 | 0.8367 | 82 | 2 | 16 |
| OG_DEPARTMENT | 0.8727 | 0.8571 | 0.8889 | 24 | 4 | 3 |
| CV_POSITION | 0.6087 | 0.5833 | 0.6364 | 7 | 5 | 4 |
| OGG_EDUCATION | 0.0000 | 0.0000 | 0.0000 | 0 | 0 | 0 |
| QT_ALIEN_NUMBER | 0.0000 | 0.0000 | 0.0000 | 0 | 0 | 0 |
| QT_AGE | 0.0000 | 0.0000 | 0.0000 | 0 | 1 | 0 |
| FD_MAJOR | 0.0000 | 0.0000 | 0.0000 | 0 | 1 | 0 |