# entity-level 다수결 앙상블: test  (20260717_122844)

min_votes=1
data_dir=`/data/team/hwan/real/data/test_sets/synthetic`
evaluated_labels=19: `PS_NAME, LC_ADDRESS, OG_WORKPLACE, OG_DEPARTMENT, CV_POSITION, OGG_EDUCATION, QT_MOBILE, QT_PHONE, QT_RESIDENT_NUMBER, QT_ALIEN_NUMBER, QT_DRIVER_NUMBER, QT_PLATE_NUMBER, QT_ACCOUNT_NUMBER, QT_CARD_NUMBER, TMI_EMAIL, QT_PASSPORT_NUMBER, QT_AGE, DT_BIRTH, FD_MAJOR`
excluded_labels=0: `-`
excluded_gold_entities=0  excluded_predicted_entities=0

| Entity Micro F1 | **0.9689** |
| Precision | 0.9951 |
| Recall | 0.9440 |
| TP | 6141 | FP | 30 | FN | 364 |

| 레이블 | F1 | P | R | TP | FP | FN |
|--------|-----|---|---|----|----|-----|
| QT_MOBILE | 1.0000 | 1.0000 | 1.0000 | 377 | 0 | 0 |
| QT_RESIDENT_NUMBER | 1.0000 | 1.0000 | 1.0000 | 185 | 0 | 0 |
| QT_DRIVER_NUMBER | 1.0000 | 1.0000 | 1.0000 | 7 | 0 | 0 |
| QT_PLATE_NUMBER | 1.0000 | 1.0000 | 1.0000 | 12 | 0 | 0 |
| QT_CARD_NUMBER | 1.0000 | 1.0000 | 1.0000 | 93 | 0 | 0 |
| QT_PASSPORT_NUMBER | 1.0000 | 1.0000 | 1.0000 | 2 | 0 | 0 |
| FD_MAJOR | 1.0000 | 1.0000 | 1.0000 | 118 | 0 | 0 |
| OGG_EDUCATION | 0.9977 | 1.0000 | 0.9954 | 215 | 0 | 1 |
| QT_PHONE | 0.9947 | 0.9894 | 1.0000 | 186 | 2 | 0 |
| QT_ACCOUNT_NUMBER | 0.9917 | 1.0000 | 0.9835 | 179 | 0 | 3 |
| DT_BIRTH | 0.9749 | 0.9915 | 0.9588 | 233 | 2 | 10 |
| LC_ADDRESS | 0.9672 | 0.9888 | 0.9464 | 265 | 3 | 15 |
| PS_NAME | 0.9636 | 0.9997 | 0.9300 | 3110 | 1 | 234 |
| OG_WORKPLACE | 0.9635 | 0.9901 | 0.9382 | 501 | 5 | 33 |
| QT_AGE | 0.9554 | 0.9386 | 0.9727 | 107 | 7 | 3 |
| CV_POSITION | 0.9412 | 0.9524 | 0.9302 | 120 | 6 | 9 |
| OG_DEPARTMENT | 0.9373 | 0.9791 | 0.8990 | 187 | 4 | 21 |
| TMI_EMAIL | 0.9331 | 1.0000 | 0.8746 | 244 | 0 | 35 |
| QT_ALIEN_NUMBER | 0.0000 | 0.0000 | 0.0000 | 0 | 0 | 0 |