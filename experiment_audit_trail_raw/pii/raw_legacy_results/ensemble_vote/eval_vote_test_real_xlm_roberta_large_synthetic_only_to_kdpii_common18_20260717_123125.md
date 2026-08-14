# entity-level 다수결 앙상블: test  (20260717_123125)

min_votes=1
data_dir=`/data/team/hwan/real/data/test_sets/kdpii`
evaluated_labels=18: `PS_NAME, LC_ADDRESS, OG_WORKPLACE, OG_DEPARTMENT, CV_POSITION, OGG_EDUCATION, QT_MOBILE, QT_PHONE, QT_RESIDENT_NUMBER, QT_DRIVER_NUMBER, QT_PLATE_NUMBER, QT_ACCOUNT_NUMBER, QT_CARD_NUMBER, TMI_EMAIL, QT_PASSPORT_NUMBER, QT_AGE, DT_BIRTH, FD_MAJOR`
excluded_labels=1: `QT_ALIEN_NUMBER`
excluded_gold_entities=9  excluded_predicted_entities=9

| Entity Micro F1 | **0.6627** |
| Precision | 0.7104 |
| Recall | 0.6210 |
| TP | 844 | FP | 344 | FN | 515 |

| 레이블 | F1 | P | R | TP | FP | FN |
|--------|-----|---|---|----|----|-----|
| QT_MOBILE | 0.9558 | 0.9310 | 0.9818 | 54 | 4 | 1 |
| QT_PHONE | 0.9128 | 0.8500 | 0.9855 | 68 | 12 | 1 |
| QT_CARD_NUMBER | 0.9128 | 0.9577 | 0.8718 | 68 | 3 | 10 |
| QT_PLATE_NUMBER | 0.8571 | 1.0000 | 0.7500 | 39 | 0 | 13 |
| DT_BIRTH | 0.8320 | 0.9455 | 0.7429 | 52 | 3 | 18 |
| QT_ACCOUNT_NUMBER | 0.8197 | 0.7075 | 0.9740 | 75 | 31 | 2 |
| QT_PASSPORT_NUMBER | 0.8000 | 1.0000 | 0.6667 | 12 | 0 | 6 |
| OGG_EDUCATION | 0.7651 | 0.9500 | 0.6404 | 57 | 3 | 32 |
| TMI_EMAIL | 0.7431 | 0.5912 | 1.0000 | 81 | 56 | 0 |
| QT_DRIVER_NUMBER | 0.7429 | 0.7222 | 0.7647 | 13 | 5 | 4 |
| PS_NAME | 0.7259 | 0.6447 | 0.8305 | 147 | 81 | 30 |
| QT_RESIDENT_NUMBER | 0.6207 | 0.4500 | 1.0000 | 18 | 22 | 0 |
| OG_WORKPLACE | 0.5603 | 0.4675 | 0.6991 | 79 | 90 | 34 |
| OG_DEPARTMENT | 0.4296 | 0.8056 | 0.2929 | 29 | 7 | 70 |
| CV_POSITION | 0.3500 | 0.7778 | 0.2258 | 28 | 8 | 96 |
| QT_AGE | 0.3000 | 0.5000 | 0.2143 | 12 | 12 | 44 |
| LC_ADDRESS | 0.1404 | 0.6154 | 0.0792 | 8 | 5 | 93 |
| FD_MAJOR | 0.1127 | 0.6667 | 0.0615 | 4 | 2 | 61 |