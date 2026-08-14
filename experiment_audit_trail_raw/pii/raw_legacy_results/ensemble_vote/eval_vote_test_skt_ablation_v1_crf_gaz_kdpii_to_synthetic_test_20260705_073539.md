# entity-level 다수결 앙상블: test  (20260705_073539)

min_votes=1
data_dir=`/data/team/hwan/synthetic`
evaluated_labels=19: `PS_NAME, LC_ADDRESS, OG_WORKPLACE, OG_DEPARTMENT, CV_POSITION, OGG_EDUCATION, QT_MOBILE, QT_PHONE, QT_RESIDENT_NUMBER, QT_ALIEN_NUMBER, QT_DRIVER_NUMBER, QT_PLATE_NUMBER, QT_ACCOUNT_NUMBER, QT_CARD_NUMBER, TMI_EMAIL, QT_PASSPORT_NUMBER, QT_AGE, DT_BIRTH, FD_MAJOR`
excluded_labels=0: `-`
excluded_gold_entities=0  excluded_predicted_entities=0

| Entity Micro F1 | **0.8356** |
| Precision | 0.7963 |
| Recall | 0.8789 |
| TP | 1212 | FP | 310 | FN | 167 |

| 레이블 | F1 | P | R | TP | FP | FN |
|--------|-----|---|---|----|----|-----|
| QT_CARD_NUMBER | 1.0000 | 1.0000 | 1.0000 | 27 | 0 | 0 |
| QT_MOBILE | 0.9960 | 0.9919 | 1.0000 | 123 | 1 | 0 |
| QT_PASSPORT_NUMBER | 0.9474 | 0.9000 | 1.0000 | 9 | 1 | 0 |
| QT_PLATE_NUMBER | 0.9412 | 0.8889 | 1.0000 | 8 | 1 | 0 |
| QT_PHONE | 0.9375 | 0.8824 | 1.0000 | 75 | 10 | 0 |
| TMI_EMAIL | 0.9313 | 1.0000 | 0.8714 | 122 | 0 | 18 |
| QT_ACCOUNT_NUMBER | 0.9245 | 1.0000 | 0.8596 | 49 | 0 | 8 |
| QT_RESIDENT_NUMBER | 0.9091 | 0.8333 | 1.0000 | 15 | 3 | 0 |
| PS_NAME | 0.8643 | 0.8624 | 0.8663 | 583 | 93 | 90 |
| LC_ADDRESS | 0.8218 | 0.7981 | 0.8469 | 83 | 21 | 15 |
| OG_WORKPLACE | 0.7800 | 0.7500 | 0.8125 | 39 | 13 | 9 |
| OG_DEPARTMENT | 0.6173 | 0.4630 | 0.9259 | 25 | 29 | 2 |
| DT_BIRTH | 0.6065 | 0.5222 | 0.7231 | 47 | 43 | 18 |
| QT_DRIVER_NUMBER | 0.2143 | 0.1200 | 1.0000 | 3 | 22 | 0 |
| CV_POSITION | 0.0941 | 0.0541 | 0.3636 | 4 | 70 | 7 |
| OGG_EDUCATION | 0.0000 | 0.0000 | 0.0000 | 0 | 0 | 0 |
| QT_ALIEN_NUMBER | 0.0000 | 0.0000 | 0.0000 | 0 | 0 | 0 |
| QT_AGE | 0.0000 | 0.0000 | 0.0000 | 0 | 1 | 0 |
| FD_MAJOR | 0.0000 | 0.0000 | 0.0000 | 0 | 2 | 0 |