# entity-level 다수결 앙상블: test  (20260731_130346)

min_votes=1
data_dir=`/data/team/hwan/real/data/test_sets/synthetic`
evaluated_labels=19: `PS_NAME, LC_ADDRESS, OG_WORKPLACE, OG_DEPARTMENT, CV_POSITION, OGG_EDUCATION, QT_MOBILE, QT_PHONE, QT_RESIDENT_NUMBER, QT_ALIEN_NUMBER, QT_DRIVER_NUMBER, QT_PLATE_NUMBER, QT_ACCOUNT_NUMBER, QT_CARD_NUMBER, TMI_EMAIL, QT_PASSPORT_NUMBER, QT_AGE, DT_BIRTH, FD_MAJOR`
excluded_labels=0: `-`
excluded_gold_entities=0  excluded_predicted_entities=0

| Entity Micro F1 | **0.9674** |
| Precision | 0.9877 |
| Recall | 0.9480 |
| TP | 6167 | FP | 77 | FN | 338 |

| 레이블 | F1 | P | R | TP | FP | FN |
|--------|-----|---|---|----|----|-----|
| OGG_EDUCATION | 1.0000 | 1.0000 | 1.0000 | 216 | 0 | 0 |
| QT_MOBILE | 1.0000 | 1.0000 | 1.0000 | 377 | 0 | 0 |
| QT_RESIDENT_NUMBER | 1.0000 | 1.0000 | 1.0000 | 185 | 0 | 0 |
| QT_DRIVER_NUMBER | 1.0000 | 1.0000 | 1.0000 | 7 | 0 | 0 |
| QT_PLATE_NUMBER | 1.0000 | 1.0000 | 1.0000 | 12 | 0 | 0 |
| QT_CARD_NUMBER | 1.0000 | 1.0000 | 1.0000 | 93 | 0 | 0 |
| QT_PASSPORT_NUMBER | 1.0000 | 1.0000 | 1.0000 | 2 | 0 | 0 |
| QT_PHONE | 0.9947 | 0.9894 | 1.0000 | 186 | 2 | 0 |
| QT_ACCOUNT_NUMBER | 0.9834 | 0.9889 | 0.9780 | 178 | 2 | 4 |
| LC_ADDRESS | 0.9765 | 0.9890 | 0.9643 | 270 | 3 | 10 |
| PS_NAME | 0.9716 | 0.9984 | 0.9462 | 3164 | 5 | 180 |
| DT_BIRTH | 0.9710 | 0.9791 | 0.9630 | 234 | 5 | 9 |
| FD_MAJOR | 0.9672 | 0.9365 | 1.0000 | 118 | 8 | 0 |
| TMI_EMAIL | 0.9570 | 1.0000 | 0.9176 | 256 | 0 | 23 |
| OG_WORKPLACE | 0.9506 | 0.9840 | 0.9195 | 491 | 8 | 43 |
| QT_AGE | 0.9115 | 0.8879 | 0.9364 | 103 | 13 | 7 |
| OG_DEPARTMENT | 0.8557 | 0.9222 | 0.7981 | 166 | 14 | 42 |
| CV_POSITION | 0.8549 | 0.8651 | 0.8450 | 109 | 17 | 20 |
| QT_ALIEN_NUMBER | 0.0000 | 0.0000 | 0.0000 | 0 | 0 | 0 |