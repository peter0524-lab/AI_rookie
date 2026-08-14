# entity-level 다수결 앙상블: test  (20260717_142551)

min_votes=1
data_dir=`/data/team/hwan/real/data/test_sets/synthetic`
evaluated_labels=19: `PS_NAME, LC_ADDRESS, OG_WORKPLACE, OG_DEPARTMENT, CV_POSITION, OGG_EDUCATION, QT_MOBILE, QT_PHONE, QT_RESIDENT_NUMBER, QT_ALIEN_NUMBER, QT_DRIVER_NUMBER, QT_PLATE_NUMBER, QT_ACCOUNT_NUMBER, QT_CARD_NUMBER, TMI_EMAIL, QT_PASSPORT_NUMBER, QT_AGE, DT_BIRTH, FD_MAJOR`
excluded_labels=0: `-`
excluded_gold_entities=0  excluded_predicted_entities=0

| Entity Micro F1 | **0.9663** |
| Precision | 0.9914 |
| Recall | 0.9425 |
| TP | 6131 | FP | 53 | FN | 374 |

| 레이블 | F1 | P | R | TP | FP | FN |
|--------|-----|---|---|----|----|-----|
| QT_MOBILE | 1.0000 | 1.0000 | 1.0000 | 377 | 0 | 0 |
| QT_RESIDENT_NUMBER | 1.0000 | 1.0000 | 1.0000 | 185 | 0 | 0 |
| QT_DRIVER_NUMBER | 1.0000 | 1.0000 | 1.0000 | 7 | 0 | 0 |
| QT_PLATE_NUMBER | 1.0000 | 1.0000 | 1.0000 | 12 | 0 | 0 |
| QT_PASSPORT_NUMBER | 1.0000 | 1.0000 | 1.0000 | 2 | 0 | 0 |
| OGG_EDUCATION | 0.9977 | 1.0000 | 0.9954 | 215 | 0 | 1 |
| QT_PHONE | 0.9947 | 0.9894 | 1.0000 | 186 | 2 | 0 |
| QT_CARD_NUMBER | 0.9947 | 0.9894 | 1.0000 | 93 | 1 | 0 |
| QT_ACCOUNT_NUMBER | 0.9861 | 1.0000 | 0.9725 | 177 | 0 | 5 |
| FD_MAJOR | 0.9748 | 0.9667 | 0.9831 | 116 | 4 | 2 |
| DT_BIRTH | 0.9710 | 0.9791 | 0.9630 | 234 | 5 | 9 |
| LC_ADDRESS | 0.9654 | 0.9851 | 0.9464 | 265 | 4 | 15 |
| PS_NAME | 0.9638 | 0.9981 | 0.9318 | 3116 | 6 | 228 |
| OG_WORKPLACE | 0.9612 | 0.9960 | 0.9288 | 496 | 2 | 38 |
| TMI_EMAIL | 0.9331 | 1.0000 | 0.8746 | 244 | 0 | 35 |
| OG_DEPARTMENT | 0.9242 | 0.9734 | 0.8798 | 183 | 5 | 25 |
| QT_AGE | 0.9211 | 0.8898 | 0.9545 | 105 | 13 | 5 |
| CV_POSITION | 0.9147 | 0.9147 | 0.9147 | 118 | 11 | 11 |
| QT_ALIEN_NUMBER | 0.0000 | 0.0000 | 0.0000 | 0 | 0 | 0 |