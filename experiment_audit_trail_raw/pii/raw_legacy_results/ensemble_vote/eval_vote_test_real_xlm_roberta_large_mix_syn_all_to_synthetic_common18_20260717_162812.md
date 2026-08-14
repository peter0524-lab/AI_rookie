# entity-level 다수결 앙상블: test  (20260717_162812)

min_votes=1
data_dir=`/data/team/hwan/real/data/test_sets/synthetic`
evaluated_labels=18: `PS_NAME, LC_ADDRESS, OG_WORKPLACE, OG_DEPARTMENT, CV_POSITION, OGG_EDUCATION, QT_MOBILE, QT_PHONE, QT_RESIDENT_NUMBER, QT_DRIVER_NUMBER, QT_PLATE_NUMBER, QT_ACCOUNT_NUMBER, QT_CARD_NUMBER, TMI_EMAIL, QT_PASSPORT_NUMBER, QT_AGE, DT_BIRTH, FD_MAJOR`
excluded_labels=1: `QT_ALIEN_NUMBER`
excluded_gold_entities=0  excluded_predicted_entities=0

| Entity Micro F1 | **0.9662** |
| Precision | 0.9940 |
| Recall | 0.9399 |
| TP | 6114 | FP | 37 | FN | 391 |

| 레이블 | F1 | P | R | TP | FP | FN |
|--------|-----|---|---|----|----|-----|
| QT_DRIVER_NUMBER | 1.0000 | 1.0000 | 1.0000 | 7 | 0 | 0 |
| QT_PLATE_NUMBER | 1.0000 | 1.0000 | 1.0000 | 12 | 0 | 0 |
| QT_CARD_NUMBER | 1.0000 | 1.0000 | 1.0000 | 93 | 0 | 0 |
| QT_PASSPORT_NUMBER | 1.0000 | 1.0000 | 1.0000 | 2 | 0 | 0 |
| QT_MOBILE | 0.9987 | 0.9974 | 1.0000 | 377 | 1 | 0 |
| QT_PHONE | 0.9973 | 0.9947 | 1.0000 | 186 | 1 | 0 |
| QT_RESIDENT_NUMBER | 0.9973 | 0.9946 | 1.0000 | 185 | 1 | 0 |
| OGG_EDUCATION | 0.9954 | 0.9954 | 0.9954 | 215 | 1 | 1 |
| QT_ACCOUNT_NUMBER | 0.9834 | 0.9889 | 0.9780 | 178 | 2 | 4 |
| FD_MAJOR | 0.9750 | 0.9590 | 0.9915 | 117 | 5 | 1 |
| DT_BIRTH | 0.9708 | 0.9831 | 0.9588 | 233 | 4 | 10 |
| LC_ADDRESS | 0.9707 | 0.9962 | 0.9464 | 265 | 1 | 15 |
| OG_WORKPLACE | 0.9652 | 0.9980 | 0.9345 | 499 | 1 | 35 |
| PS_NAME | 0.9626 | 1.0000 | 0.9279 | 3103 | 0 | 241 |
| QT_AGE | 0.9432 | 0.9076 | 0.9818 | 108 | 11 | 2 |
| TMI_EMAIL | 0.9331 | 1.0000 | 0.8746 | 244 | 0 | 35 |
| CV_POSITION | 0.9243 | 0.9508 | 0.8992 | 116 | 6 | 13 |
| OG_DEPARTMENT | 0.9039 | 0.9831 | 0.8365 | 174 | 3 | 34 |