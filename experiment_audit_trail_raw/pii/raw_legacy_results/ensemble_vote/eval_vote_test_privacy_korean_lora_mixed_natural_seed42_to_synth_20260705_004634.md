# entity-level 다수결 앙상블: test  (20260705_004634)

min_votes=1
data_dir=`/data/team/hwan/synthetic`
evaluated_labels=19: `PS_NAME, LC_ADDRESS, OG_WORKPLACE, OG_DEPARTMENT, CV_POSITION, OGG_EDUCATION, QT_MOBILE, QT_PHONE, QT_RESIDENT_NUMBER, QT_ALIEN_NUMBER, QT_DRIVER_NUMBER, QT_PLATE_NUMBER, QT_ACCOUNT_NUMBER, QT_CARD_NUMBER, TMI_EMAIL, QT_PASSPORT_NUMBER, QT_AGE, DT_BIRTH, FD_MAJOR`
excluded_labels=0: `-`
excluded_gold_entities=0  excluded_predicted_entities=0

| Entity Micro F1 | **0.5166** |
| Precision | 0.9897 |
| Recall | 0.3495 |
| TP | 482 | FP | 5 | FN | 897 |

| 레이블 | F1 | P | R | TP | FP | FN |
|--------|-----|---|---|----|----|-----|
| QT_MOBILE | 1.0000 | 1.0000 | 1.0000 | 123 | 0 | 0 |
| QT_RESIDENT_NUMBER | 1.0000 | 1.0000 | 1.0000 | 15 | 0 | 0 |
| QT_DRIVER_NUMBER | 1.0000 | 1.0000 | 1.0000 | 3 | 0 | 0 |
| QT_PLATE_NUMBER | 1.0000 | 1.0000 | 1.0000 | 8 | 0 | 0 |
| QT_PHONE | 0.9934 | 0.9868 | 1.0000 | 75 | 1 | 0 |
| QT_CARD_NUMBER | 0.9818 | 0.9643 | 1.0000 | 27 | 1 | 0 |
| DT_BIRTH | 0.9268 | 0.9828 | 0.8769 | 57 | 1 | 8 |
| QT_ACCOUNT_NUMBER | 0.9143 | 1.0000 | 0.8421 | 48 | 0 | 9 |
| PS_NAME | 0.3087 | 0.9919 | 0.1828 | 123 | 1 | 550 |
| OG_WORKPLACE | 0.1176 | 1.0000 | 0.0625 | 3 | 0 | 45 |
| LC_ADDRESS | 0.0000 | 0.0000 | 0.0000 | 0 | 0 | 98 |
| OG_DEPARTMENT | 0.0000 | 0.0000 | 0.0000 | 0 | 1 | 27 |
| CV_POSITION | 0.0000 | 0.0000 | 0.0000 | 0 | 0 | 11 |
| OGG_EDUCATION | 0.0000 | 0.0000 | 0.0000 | 0 | 0 | 0 |
| QT_ALIEN_NUMBER | 0.0000 | 0.0000 | 0.0000 | 0 | 0 | 0 |
| TMI_EMAIL | 0.0000 | 0.0000 | 0.0000 | 0 | 0 | 140 |
| QT_PASSPORT_NUMBER | 0.0000 | 0.0000 | 0.0000 | 0 | 0 | 9 |
| QT_AGE | 0.0000 | 0.0000 | 0.0000 | 0 | 0 | 0 |
| FD_MAJOR | 0.0000 | 0.0000 | 0.0000 | 0 | 0 | 0 |