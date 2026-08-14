# entity-level 다수결 앙상블: test  (20260718_115225)

min_votes=1
data_dir=`/data/team/hwan/real/data/test_sets/synthetic`
evaluated_labels=19: `PS_NAME, LC_ADDRESS, OG_WORKPLACE, OG_DEPARTMENT, CV_POSITION, OGG_EDUCATION, QT_MOBILE, QT_PHONE, QT_RESIDENT_NUMBER, QT_ALIEN_NUMBER, QT_DRIVER_NUMBER, QT_PLATE_NUMBER, QT_ACCOUNT_NUMBER, QT_CARD_NUMBER, TMI_EMAIL, QT_PASSPORT_NUMBER, QT_AGE, DT_BIRTH, FD_MAJOR`
excluded_labels=0: `-`
excluded_gold_entities=0  excluded_predicted_entities=0

| Entity Micro F1 | **0.5864** |
| Precision | 0.9873 |
| Recall | 0.4171 |
| TP | 2713 | FP | 35 | FN | 3792 |

| 레이블 | F1 | P | R | TP | FP | FN |
|--------|-----|---|---|----|----|-----|
| QT_DRIVER_NUMBER | 1.0000 | 1.0000 | 1.0000 | 7 | 0 | 0 |
| QT_PLATE_NUMBER | 1.0000 | 1.0000 | 1.0000 | 12 | 0 | 0 |
| QT_CARD_NUMBER | 1.0000 | 1.0000 | 1.0000 | 93 | 0 | 0 |
| QT_MOBILE | 0.9987 | 0.9974 | 1.0000 | 377 | 1 | 0 |
| QT_PHONE | 0.9973 | 0.9947 | 1.0000 | 186 | 1 | 0 |
| QT_RESIDENT_NUMBER | 0.9973 | 0.9946 | 1.0000 | 185 | 1 | 0 |
| QT_ACCOUNT_NUMBER | 0.9861 | 1.0000 | 0.9725 | 177 | 0 | 5 |
| DT_BIRTH | 0.9710 | 0.9791 | 0.9630 | 234 | 5 | 9 |
| QT_AGE | 0.9224 | 0.9266 | 0.9182 | 101 | 8 | 9 |
| PS_NAME | 0.5562 | 0.9923 | 0.3864 | 1292 | 10 | 2052 |
| OGG_EDUCATION | 0.2619 | 0.9167 | 0.1528 | 33 | 3 | 183 |
| FD_MAJOR | 0.0645 | 0.6667 | 0.0339 | 4 | 2 | 114 |
| TMI_EMAIL | 0.0625 | 1.0000 | 0.0323 | 9 | 0 | 270 |
| OG_DEPARTMENT | 0.0190 | 1.0000 | 0.0096 | 2 | 0 | 206 |
| LC_ADDRESS | 0.0071 | 0.5000 | 0.0036 | 1 | 1 | 279 |
| OG_WORKPLACE | 0.0000 | 0.0000 | 0.0000 | 0 | 1 | 534 |
| CV_POSITION | 0.0000 | 0.0000 | 0.0000 | 0 | 2 | 129 |
| QT_ALIEN_NUMBER | 0.0000 | 0.0000 | 0.0000 | 0 | 0 | 0 |
| QT_PASSPORT_NUMBER | 0.0000 | 0.0000 | 0.0000 | 0 | 0 | 2 |