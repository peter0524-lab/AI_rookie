# entity-level 다수결 앙상블: test  (20260717_091948)

min_votes=1
data_dir=`/data/team/hwan/real/data/test_sets/synthetic`
evaluated_labels=19: `PS_NAME, LC_ADDRESS, OG_WORKPLACE, OG_DEPARTMENT, CV_POSITION, OGG_EDUCATION, QT_MOBILE, QT_PHONE, QT_RESIDENT_NUMBER, QT_ALIEN_NUMBER, QT_DRIVER_NUMBER, QT_PLATE_NUMBER, QT_ACCOUNT_NUMBER, QT_CARD_NUMBER, TMI_EMAIL, QT_PASSPORT_NUMBER, QT_AGE, DT_BIRTH, FD_MAJOR`
excluded_labels=0: `-`
excluded_gold_entities=0  excluded_predicted_entities=0

| Entity Micro F1 | **0.9719** |
| Precision | 0.9915 |
| Recall | 0.9531 |
| TP | 6200 | FP | 53 | FN | 305 |

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
| QT_ACCOUNT_NUMBER | 0.9917 | 1.0000 | 0.9835 | 179 | 0 | 3 |
| DT_BIRTH | 0.9751 | 0.9833 | 0.9671 | 235 | 4 | 8 |
| LC_ADDRESS | 0.9747 | 0.9854 | 0.9643 | 270 | 4 | 10 |
| PS_NAME | 0.9714 | 0.9994 | 0.9450 | 3160 | 2 | 184 |
| OG_WORKPLACE | 0.9682 | 0.9960 | 0.9419 | 503 | 2 | 31 |
| TMI_EMAIL | 0.9609 | 1.0000 | 0.9247 | 258 | 0 | 21 |
| CV_POSITION | 0.9375 | 0.9449 | 0.9302 | 120 | 7 | 9 |
| FD_MAJOR | 0.9286 | 0.8731 | 0.9915 | 117 | 17 | 1 |
| QT_AGE | 0.9244 | 0.9043 | 0.9455 | 104 | 11 | 6 |
| OG_DEPARTMENT | 0.9072 | 0.9778 | 0.8462 | 176 | 4 | 32 |
| QT_ALIEN_NUMBER | 0.0000 | 0.0000 | 0.0000 | 0 | 0 | 0 |