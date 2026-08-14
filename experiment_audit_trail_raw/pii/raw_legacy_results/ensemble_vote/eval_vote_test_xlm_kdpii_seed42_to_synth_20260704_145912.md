# entity-level 다수결 앙상블: test  (20260704_145912)

min_votes=1
data_dir=`/data/team/hwan/synthetic`
evaluated_labels=19: `PS_NAME, LC_ADDRESS, OG_WORKPLACE, OG_DEPARTMENT, CV_POSITION, OGG_EDUCATION, QT_MOBILE, QT_PHONE, QT_RESIDENT_NUMBER, QT_ALIEN_NUMBER, QT_DRIVER_NUMBER, QT_PLATE_NUMBER, QT_ACCOUNT_NUMBER, QT_CARD_NUMBER, TMI_EMAIL, QT_PASSPORT_NUMBER, QT_AGE, DT_BIRTH, FD_MAJOR`
excluded_labels=0: `-`
excluded_gold_entities=0  excluded_predicted_entities=0

| Entity Micro F1 | **0.8251** |
| Precision | 0.7786 |
| Recall | 0.8774 |
| TP | 1210 | FP | 344 | FN | 169 |

| 레이블 | F1 | P | R | TP | FP | FN |
|--------|-----|---|---|----|----|-----|
| QT_CARD_NUMBER | 1.0000 | 1.0000 | 1.0000 | 27 | 0 | 0 |
| QT_MOBILE | 0.9919 | 0.9840 | 1.0000 | 123 | 2 | 0 |
| QT_PLATE_NUMBER | 0.9412 | 0.8889 | 1.0000 | 8 | 1 | 0 |
| QT_PHONE | 0.9375 | 0.8824 | 1.0000 | 75 | 10 | 0 |
| TMI_EMAIL | 0.9105 | 1.0000 | 0.8357 | 117 | 0 | 23 |
| PS_NAME | 0.8691 | 0.8750 | 0.8633 | 581 | 83 | 92 |
| LC_ADDRESS | 0.8601 | 0.8737 | 0.8469 | 83 | 12 | 15 |
| QT_PASSPORT_NUMBER | 0.8571 | 0.7500 | 1.0000 | 9 | 3 | 0 |
| DT_BIRTH | 0.8438 | 0.8571 | 0.8308 | 54 | 9 | 11 |
| QT_ACCOUNT_NUMBER | 0.8302 | 0.8980 | 0.7719 | 44 | 5 | 13 |
| OG_WORKPLACE | 0.6614 | 0.5316 | 0.8750 | 42 | 37 | 6 |
| OG_DEPARTMENT | 0.6098 | 0.4545 | 0.9259 | 25 | 30 | 2 |
| QT_RESIDENT_NUMBER | 0.5556 | 0.3846 | 1.0000 | 15 | 24 | 0 |
| QT_DRIVER_NUMBER | 0.3000 | 0.1765 | 1.0000 | 3 | 14 | 0 |
| CV_POSITION | 0.0630 | 0.0345 | 0.3636 | 4 | 112 | 7 |
| OGG_EDUCATION | 0.0000 | 0.0000 | 0.0000 | 0 | 1 | 0 |
| QT_ALIEN_NUMBER | 0.0000 | 0.0000 | 0.0000 | 0 | 0 | 0 |
| QT_AGE | 0.0000 | 0.0000 | 0.0000 | 0 | 1 | 0 |
| FD_MAJOR | 0.0000 | 0.0000 | 0.0000 | 0 | 0 | 0 |