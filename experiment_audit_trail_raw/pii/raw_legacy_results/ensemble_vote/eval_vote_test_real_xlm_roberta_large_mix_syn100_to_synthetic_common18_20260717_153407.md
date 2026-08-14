# entity-level 다수결 앙상블: test  (20260717_153407)

min_votes=1
data_dir=`/data/team/hwan/real/data/test_sets/synthetic`
evaluated_labels=18: `PS_NAME, LC_ADDRESS, OG_WORKPLACE, OG_DEPARTMENT, CV_POSITION, OGG_EDUCATION, QT_MOBILE, QT_PHONE, QT_RESIDENT_NUMBER, QT_DRIVER_NUMBER, QT_PLATE_NUMBER, QT_ACCOUNT_NUMBER, QT_CARD_NUMBER, TMI_EMAIL, QT_PASSPORT_NUMBER, QT_AGE, DT_BIRTH, FD_MAJOR`
excluded_labels=1: `QT_ALIEN_NUMBER`
excluded_gold_entities=0  excluded_predicted_entities=0

| Entity Micro F1 | **0.9680** |
| Precision | 0.9934 |
| Recall | 0.9439 |
| TP | 6140 | FP | 41 | FN | 365 |

| 레이블 | F1 | P | R | TP | FP | FN |
|--------|-----|---|---|----|----|-----|
| QT_MOBILE | 1.0000 | 1.0000 | 1.0000 | 377 | 0 | 0 |
| QT_RESIDENT_NUMBER | 1.0000 | 1.0000 | 1.0000 | 185 | 0 | 0 |
| QT_DRIVER_NUMBER | 1.0000 | 1.0000 | 1.0000 | 7 | 0 | 0 |
| QT_PLATE_NUMBER | 1.0000 | 1.0000 | 1.0000 | 12 | 0 | 0 |
| QT_PASSPORT_NUMBER | 1.0000 | 1.0000 | 1.0000 | 2 | 0 | 0 |
| OGG_EDUCATION | 0.9977 | 1.0000 | 0.9954 | 215 | 0 | 1 |
| QT_PHONE | 0.9973 | 0.9947 | 1.0000 | 186 | 1 | 0 |
| QT_CARD_NUMBER | 0.9947 | 0.9894 | 1.0000 | 93 | 1 | 0 |
| QT_ACCOUNT_NUMBER | 0.9889 | 1.0000 | 0.9780 | 178 | 0 | 4 |
| FD_MAJOR | 0.9873 | 0.9832 | 0.9915 | 117 | 2 | 1 |
| DT_BIRTH | 0.9689 | 0.9750 | 0.9630 | 234 | 6 | 9 |
| LC_ADDRESS | 0.9689 | 0.9925 | 0.9464 | 265 | 2 | 15 |
| PS_NAME | 0.9646 | 0.9994 | 0.9321 | 3117 | 2 | 227 |
| OG_WORKPLACE | 0.9643 | 0.9940 | 0.9363 | 500 | 3 | 34 |
| QT_AGE | 0.9474 | 0.9153 | 0.9818 | 108 | 10 | 2 |
| TMI_EMAIL | 0.9331 | 1.0000 | 0.8746 | 244 | 0 | 35 |
| OG_DEPARTMENT | 0.9246 | 0.9684 | 0.8846 | 184 | 6 | 24 |
| CV_POSITION | 0.9170 | 0.9355 | 0.8992 | 116 | 8 | 13 |