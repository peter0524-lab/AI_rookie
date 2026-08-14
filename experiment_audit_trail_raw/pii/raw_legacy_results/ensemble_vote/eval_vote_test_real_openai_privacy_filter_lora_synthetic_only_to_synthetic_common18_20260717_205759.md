# entity-level 다수결 앙상블: test  (20260717_205759)

min_votes=1
data_dir=`/data/team/hwan/real/data/test_sets/synthetic`
evaluated_labels=18: `PS_NAME, LC_ADDRESS, OG_WORKPLACE, OG_DEPARTMENT, CV_POSITION, OGG_EDUCATION, QT_MOBILE, QT_PHONE, QT_RESIDENT_NUMBER, QT_DRIVER_NUMBER, QT_PLATE_NUMBER, QT_ACCOUNT_NUMBER, QT_CARD_NUMBER, TMI_EMAIL, QT_PASSPORT_NUMBER, QT_AGE, DT_BIRTH, FD_MAJOR`
excluded_labels=1: `QT_ALIEN_NUMBER`
excluded_gold_entities=0  excluded_predicted_entities=0

| Entity Micro F1 | **0.5875** |
| Precision | 0.9866 |
| Recall | 0.4183 |
| TP | 2721 | FP | 37 | FN | 3784 |

| 레이블 | F1 | P | R | TP | FP | FN |
|--------|-----|---|---|----|----|-----|
| QT_MOBILE | 1.0000 | 1.0000 | 1.0000 | 377 | 0 | 0 |
| QT_RESIDENT_NUMBER | 1.0000 | 1.0000 | 1.0000 | 185 | 0 | 0 |
| QT_DRIVER_NUMBER | 1.0000 | 1.0000 | 1.0000 | 7 | 0 | 0 |
| QT_PLATE_NUMBER | 1.0000 | 1.0000 | 1.0000 | 12 | 0 | 0 |
| QT_CARD_NUMBER | 1.0000 | 1.0000 | 1.0000 | 93 | 0 | 0 |
| QT_PHONE | 0.9973 | 0.9947 | 1.0000 | 186 | 1 | 0 |
| QT_ACCOUNT_NUMBER | 0.9889 | 1.0000 | 0.9780 | 178 | 0 | 4 |
| DT_BIRTH | 0.9751 | 0.9833 | 0.9671 | 235 | 4 | 8 |
| QT_AGE | 0.9412 | 0.9369 | 0.9455 | 104 | 7 | 6 |
| PS_NAME | 0.5576 | 0.9856 | 0.3888 | 1300 | 19 | 2044 |
| OGG_EDUCATION | 0.2000 | 1.0000 | 0.1111 | 24 | 0 | 192 |
| FD_MAJOR | 0.0813 | 1.0000 | 0.0424 | 5 | 0 | 113 |
| TMI_EMAIL | 0.0625 | 1.0000 | 0.0323 | 9 | 0 | 270 |
| OG_DEPARTMENT | 0.0190 | 0.6667 | 0.0096 | 2 | 1 | 206 |
| OG_WORKPLACE | 0.0111 | 0.4286 | 0.0056 | 3 | 4 | 531 |
| LC_ADDRESS | 0.0071 | 1.0000 | 0.0036 | 1 | 0 | 279 |
| CV_POSITION | 0.0000 | 0.0000 | 0.0000 | 0 | 1 | 129 |
| QT_PASSPORT_NUMBER | 0.0000 | 0.0000 | 0.0000 | 0 | 0 | 2 |