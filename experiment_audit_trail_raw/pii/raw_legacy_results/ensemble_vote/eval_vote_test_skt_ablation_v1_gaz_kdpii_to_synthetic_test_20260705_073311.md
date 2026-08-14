# entity-level 다수결 앙상블: test  (20260705_073311)

min_votes=1
data_dir=`/data/team/hwan/synthetic`
evaluated_labels=19: `PS_NAME, LC_ADDRESS, OG_WORKPLACE, OG_DEPARTMENT, CV_POSITION, OGG_EDUCATION, QT_MOBILE, QT_PHONE, QT_RESIDENT_NUMBER, QT_ALIEN_NUMBER, QT_DRIVER_NUMBER, QT_PLATE_NUMBER, QT_ACCOUNT_NUMBER, QT_CARD_NUMBER, TMI_EMAIL, QT_PASSPORT_NUMBER, QT_AGE, DT_BIRTH, FD_MAJOR`
excluded_labels=0: `-`
excluded_gold_entities=0  excluded_predicted_entities=0

| Entity Micro F1 | **0.8649** |
| Precision | 0.8338 |
| Recall | 0.8985 |
| TP | 1239 | FP | 247 | FN | 140 |

| 레이블 | F1 | P | R | TP | FP | FN |
|--------|-----|---|---|----|----|-----|
| QT_CARD_NUMBER | 1.0000 | 1.0000 | 1.0000 | 27 | 0 | 0 |
| QT_MOBILE | 0.9960 | 0.9919 | 1.0000 | 123 | 1 | 0 |
| QT_PHONE | 0.9934 | 0.9868 | 1.0000 | 75 | 1 | 0 |
| QT_PASSPORT_NUMBER | 0.9474 | 0.9000 | 1.0000 | 9 | 1 | 0 |
| TMI_EMAIL | 0.9313 | 1.0000 | 0.8714 | 122 | 0 | 18 |
| LC_ADDRESS | 0.8783 | 0.9121 | 0.8469 | 83 | 8 | 15 |
| PS_NAME | 0.8764 | 0.8631 | 0.8900 | 599 | 95 | 74 |
| QT_ACCOUNT_NUMBER | 0.8673 | 0.8750 | 0.8596 | 49 | 7 | 8 |
| QT_PLATE_NUMBER | 0.8421 | 0.7273 | 1.0000 | 8 | 3 | 0 |
| DT_BIRTH | 0.7639 | 0.6962 | 0.8462 | 55 | 24 | 10 |
| OG_WORKPLACE | 0.7455 | 0.6613 | 0.8542 | 41 | 21 | 7 |
| QT_RESIDENT_NUMBER | 0.6667 | 0.5000 | 1.0000 | 15 | 15 | 0 |
| OG_DEPARTMENT | 0.6098 | 0.4545 | 0.9259 | 25 | 30 | 2 |
| QT_DRIVER_NUMBER | 0.5455 | 0.3750 | 1.0000 | 3 | 5 | 0 |
| CV_POSITION | 0.2000 | 0.1282 | 0.4545 | 5 | 34 | 6 |
| OGG_EDUCATION | 0.0000 | 0.0000 | 0.0000 | 0 | 0 | 0 |
| QT_ALIEN_NUMBER | 0.0000 | 0.0000 | 0.0000 | 0 | 0 | 0 |
| QT_AGE | 0.0000 | 0.0000 | 0.0000 | 0 | 1 | 0 |
| FD_MAJOR | 0.0000 | 0.0000 | 0.0000 | 0 | 1 | 0 |