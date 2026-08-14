# entity-level 다수결 앙상블: test  (20260731_121053)

min_votes=1
data_dir=`/data/team/hwan/real/data/test_sets/combined`
evaluated_labels=19: `PS_NAME, LC_ADDRESS, OG_WORKPLACE, OG_DEPARTMENT, CV_POSITION, OGG_EDUCATION, QT_MOBILE, QT_PHONE, QT_RESIDENT_NUMBER, QT_ALIEN_NUMBER, QT_DRIVER_NUMBER, QT_PLATE_NUMBER, QT_ACCOUNT_NUMBER, QT_CARD_NUMBER, TMI_EMAIL, QT_PASSPORT_NUMBER, QT_AGE, DT_BIRTH, FD_MAJOR`
excluded_labels=0: `-`
excluded_gold_entities=0  excluded_predicted_entities=0

| Entity Micro F1 | **0.8651** |
| Precision | 0.8376 |
| Recall | 0.8946 |
| TP | 7043 | FP | 1366 | FN | 830 |

| 레이블 | F1 | P | R | TP | FP | FN |
|--------|-----|---|---|----|----|-----|
| QT_MOBILE | 0.9977 | 0.9954 | 1.0000 | 432 | 2 | 0 |
| QT_RESIDENT_NUMBER | 0.9831 | 0.9667 | 1.0000 | 203 | 7 | 0 |
| QT_PASSPORT_NUMBER | 0.9756 | 0.9524 | 1.0000 | 20 | 1 | 0 |
| QT_CARD_NUMBER | 0.9744 | 0.9500 | 1.0000 | 171 | 9 | 0 |
| QT_PHONE | 0.9696 | 0.9410 | 1.0000 | 255 | 16 | 0 |
| TMI_EMAIL | 0.9463 | 0.9909 | 0.9056 | 326 | 3 | 34 |
| LC_ADDRESS | 0.9308 | 0.9098 | 0.9528 | 363 | 36 | 18 |
| QT_ACCOUNT_NUMBER | 0.9173 | 0.8938 | 0.9421 | 244 | 29 | 15 |
| PS_NAME | 0.9140 | 0.9062 | 0.9219 | 3246 | 336 | 275 |
| QT_DRIVER_NUMBER | 0.9057 | 0.8276 | 1.0000 | 24 | 5 | 0 |
| OGG_EDUCATION | 0.7826 | 0.9851 | 0.6492 | 198 | 3 | 107 |
| FD_MAJOR | 0.7460 | 0.7231 | 0.7705 | 141 | 54 | 42 |
| DT_BIRTH | 0.7205 | 0.6307 | 0.8403 | 263 | 154 | 50 |
| QT_AGE | 0.7138 | 0.7655 | 0.6687 | 111 | 34 | 55 |
| OG_WORKPLACE | 0.7078 | 0.6153 | 0.8331 | 539 | 337 | 108 |
| CV_POSITION | 0.6996 | 0.6996 | 0.6996 | 177 | 76 | 76 |
| OG_DEPARTMENT | 0.6816 | 0.5717 | 0.8436 | 259 | 194 | 48 |
| QT_ALIEN_NUMBER | 0.6667 | 0.5000 | 1.0000 | 9 | 9 | 0 |
| QT_PLATE_NUMBER | 0.6631 | 0.5041 | 0.9688 | 62 | 61 | 2 |