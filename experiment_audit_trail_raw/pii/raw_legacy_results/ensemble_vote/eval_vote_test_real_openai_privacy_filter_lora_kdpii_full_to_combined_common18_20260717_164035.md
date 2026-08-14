# entity-level 다수결 앙상블: test  (20260717_164035)

min_votes=1
data_dir=`/data/team/hwan/real/data/test_sets/combined`
evaluated_labels=18: `PS_NAME, LC_ADDRESS, OG_WORKPLACE, OG_DEPARTMENT, CV_POSITION, OGG_EDUCATION, QT_MOBILE, QT_PHONE, QT_RESIDENT_NUMBER, QT_DRIVER_NUMBER, QT_PLATE_NUMBER, QT_ACCOUNT_NUMBER, QT_CARD_NUMBER, TMI_EMAIL, QT_PASSPORT_NUMBER, QT_AGE, DT_BIRTH, FD_MAJOR`
excluded_labels=1: `QT_ALIEN_NUMBER`
excluded_gold_entities=9  excluded_predicted_entities=17

| Entity Micro F1 | **0.4622** |
| Precision | 0.8599 |
| Recall | 0.3160 |
| TP | 2485 | FP | 405 | FN | 5379 |

| 레이블 | F1 | P | R | TP | FP | FN |
|--------|-----|---|---|----|----|-----|
| QT_MOBILE | 0.9988 | 0.9977 | 1.0000 | 432 | 1 | 0 |
| QT_RESIDENT_NUMBER | 0.9927 | 0.9854 | 1.0000 | 203 | 3 | 0 |
| QT_PHONE | 0.9789 | 0.9586 | 1.0000 | 255 | 11 | 0 |
| QT_CARD_NUMBER | 0.9507 | 0.9425 | 0.9591 | 164 | 10 | 7 |
| QT_ACCOUNT_NUMBER | 0.8940 | 0.9685 | 0.8301 | 215 | 7 | 44 |
| QT_PLATE_NUMBER | 0.8905 | 0.8356 | 0.9531 | 61 | 12 | 3 |
| DT_BIRTH | 0.7316 | 0.6284 | 0.8754 | 274 | 162 | 39 |
| QT_DRIVER_NUMBER | 0.6667 | 0.7143 | 0.6250 | 15 | 6 | 9 |
| QT_AGE | 0.6204 | 0.7870 | 0.5120 | 85 | 23 | 81 |
| PS_NAME | 0.3091 | 0.9421 | 0.1849 | 651 | 40 | 2870 |
| TMI_EMAIL | 0.1818 | 1.0000 | 0.1000 | 36 | 0 | 324 |
| CV_POSITION | 0.1560 | 0.7586 | 0.0870 | 22 | 7 | 231 |
| OGG_EDUCATION | 0.1535 | 0.3488 | 0.0984 | 30 | 56 | 275 |
| LC_ADDRESS | 0.1119 | 0.7667 | 0.0604 | 23 | 7 | 358 |
| QT_PASSPORT_NUMBER | 0.0909 | 0.5000 | 0.0500 | 1 | 1 | 19 |
| OG_DEPARTMENT | 0.0612 | 0.5000 | 0.0326 | 10 | 10 | 297 |
| FD_MAJOR | 0.0300 | 0.1765 | 0.0164 | 3 | 14 | 180 |
| OG_WORKPLACE | 0.0146 | 0.1250 | 0.0077 | 5 | 35 | 642 |