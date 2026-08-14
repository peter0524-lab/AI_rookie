# entity-level 다수결 앙상블: test  (20260717_085041)

min_votes=1
data_dir=`/data/team/hwan/real/data/test_sets/synthetic`
evaluated_labels=19: `PS_NAME, LC_ADDRESS, OG_WORKPLACE, OG_DEPARTMENT, CV_POSITION, OGG_EDUCATION, QT_MOBILE, QT_PHONE, QT_RESIDENT_NUMBER, QT_ALIEN_NUMBER, QT_DRIVER_NUMBER, QT_PLATE_NUMBER, QT_ACCOUNT_NUMBER, QT_CARD_NUMBER, TMI_EMAIL, QT_PASSPORT_NUMBER, QT_AGE, DT_BIRTH, FD_MAJOR`
excluded_labels=0: `-`
excluded_gold_entities=0  excluded_predicted_entities=0

| Entity Micro F1 | **0.9706** |
| Precision | 0.9899 |
| Recall | 0.9520 |
| TP | 6193 | FP | 63 | FN | 312 |

| 레이블 | F1 | P | R | TP | FP | FN |
|--------|-----|---|---|----|----|-----|
| OGG_EDUCATION | 1.0000 | 1.0000 | 1.0000 | 216 | 0 | 0 |
| QT_MOBILE | 1.0000 | 1.0000 | 1.0000 | 377 | 0 | 0 |
| QT_RESIDENT_NUMBER | 1.0000 | 1.0000 | 1.0000 | 185 | 0 | 0 |
| QT_DRIVER_NUMBER | 1.0000 | 1.0000 | 1.0000 | 7 | 0 | 0 |
| QT_PLATE_NUMBER | 1.0000 | 1.0000 | 1.0000 | 12 | 0 | 0 |
| QT_CARD_NUMBER | 1.0000 | 1.0000 | 1.0000 | 93 | 0 | 0 |
| QT_PASSPORT_NUMBER | 1.0000 | 1.0000 | 1.0000 | 2 | 0 | 0 |
| QT_PHONE | 0.9973 | 0.9947 | 1.0000 | 186 | 1 | 0 |
| QT_ACCOUNT_NUMBER | 0.9917 | 1.0000 | 0.9835 | 179 | 0 | 3 |
| DT_BIRTH | 0.9729 | 0.9873 | 0.9588 | 233 | 3 | 10 |
| LC_ADDRESS | 0.9712 | 0.9783 | 0.9643 | 270 | 6 | 10 |
| FD_MAJOR | 0.9710 | 0.9512 | 0.9915 | 117 | 6 | 1 |
| PS_NAME | 0.9705 | 0.9987 | 0.9438 | 3156 | 4 | 188 |
| OG_WORKPLACE | 0.9653 | 0.9960 | 0.9363 | 500 | 2 | 34 |
| TMI_EMAIL | 0.9609 | 1.0000 | 0.9247 | 258 | 0 | 21 |
| CV_POSITION | 0.9084 | 0.9344 | 0.8837 | 114 | 8 | 15 |
| OG_DEPARTMENT | 0.9045 | 0.9474 | 0.8654 | 180 | 10 | 28 |
| QT_AGE | 0.8963 | 0.8244 | 0.9818 | 108 | 23 | 2 |
| QT_ALIEN_NUMBER | 0.0000 | 0.0000 | 0.0000 | 0 | 0 | 0 |