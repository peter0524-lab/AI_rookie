# entity-level 다수결 앙상블: test  (20260705_042221)

min_votes=2
data_dir=`/data/team/hwan/synthetic`
evaluated_labels=19: `PS_NAME, LC_ADDRESS, OG_WORKPLACE, OG_DEPARTMENT, CV_POSITION, OGG_EDUCATION, QT_MOBILE, QT_PHONE, QT_RESIDENT_NUMBER, QT_ALIEN_NUMBER, QT_DRIVER_NUMBER, QT_PLATE_NUMBER, QT_ACCOUNT_NUMBER, QT_CARD_NUMBER, TMI_EMAIL, QT_PASSPORT_NUMBER, QT_AGE, DT_BIRTH, FD_MAJOR`
excluded_labels=0: `-`
excluded_gold_entities=0  excluded_predicted_entities=0

| Entity Micro F1 | **0.8593** |
| Precision | 0.8466 |
| Recall | 0.8724 |
| TP | 1203 | FP | 218 | FN | 176 |

| 레이블 | F1 | P | R | TP | FP | FN |
|--------|-----|---|---|----|----|-----|
| QT_PLATE_NUMBER | 1.0000 | 1.0000 | 1.0000 | 8 | 0 | 0 |
| QT_MOBILE | 0.9960 | 0.9919 | 1.0000 | 123 | 1 | 0 |
| QT_RESIDENT_NUMBER | 0.9677 | 0.9375 | 1.0000 | 15 | 1 | 0 |
| QT_CARD_NUMBER | 0.9643 | 0.9310 | 1.0000 | 27 | 2 | 0 |
| QT_PHONE | 0.9615 | 0.9259 | 1.0000 | 75 | 6 | 0 |
| QT_PASSPORT_NUMBER | 0.9474 | 0.9000 | 1.0000 | 9 | 1 | 0 |
| TMI_EMAIL | 0.9313 | 1.0000 | 0.8714 | 122 | 0 | 18 |
| QT_ACCOUNT_NUMBER | 0.9074 | 0.9608 | 0.8596 | 49 | 2 | 8 |
| PS_NAME | 0.8855 | 0.9172 | 0.8559 | 576 | 52 | 97 |
| LC_ADDRESS | 0.7477 | 0.6694 | 0.8469 | 83 | 41 | 15 |
| OG_WORKPLACE | 0.7379 | 0.6909 | 0.7917 | 38 | 17 | 10 |
| DT_BIRTH | 0.6571 | 0.6133 | 0.7077 | 46 | 29 | 19 |
| OG_DEPARTMENT | 0.6329 | 0.4808 | 0.9259 | 25 | 27 | 2 |
| CV_POSITION | 0.2500 | 0.1905 | 0.3636 | 4 | 17 | 7 |
| QT_DRIVER_NUMBER | 0.2222 | 0.1250 | 1.0000 | 3 | 21 | 0 |
| OGG_EDUCATION | 0.0000 | 0.0000 | 0.0000 | 0 | 0 | 0 |
| QT_ALIEN_NUMBER | 0.0000 | 0.0000 | 0.0000 | 0 | 0 | 0 |
| QT_AGE | 0.0000 | 0.0000 | 0.0000 | 0 | 1 | 0 |
| FD_MAJOR | 0.0000 | 0.0000 | 0.0000 | 0 | 0 | 0 |