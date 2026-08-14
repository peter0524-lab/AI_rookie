# entity-level 다수결 앙상블: test  (20260716_131222)

min_votes=2
data_dir=`/data/team/hwan/real/data/test_sets/synthetic`
evaluated_labels=18: `PS_NAME, LC_ADDRESS, OG_WORKPLACE, OG_DEPARTMENT, CV_POSITION, OGG_EDUCATION, QT_MOBILE, QT_PHONE, QT_RESIDENT_NUMBER, QT_DRIVER_NUMBER, QT_PLATE_NUMBER, QT_ACCOUNT_NUMBER, QT_CARD_NUMBER, TMI_EMAIL, QT_PASSPORT_NUMBER, QT_AGE, DT_BIRTH, FD_MAJOR`
excluded_labels=1: `QT_ALIEN_NUMBER`
excluded_gold_entities=0  excluded_predicted_entities=0

| Entity Micro F1 | **0.9753** |
| Precision | 0.9943 |
| Recall | 0.9571 |
| TP | 6226 | FP | 36 | FN | 279 |

| 레이블 | F1 | P | R | TP | FP | FN |
|--------|-----|---|---|----|----|-----|
| OGG_EDUCATION | 1.0000 | 1.0000 | 1.0000 | 216 | 0 | 0 |
| QT_MOBILE | 1.0000 | 1.0000 | 1.0000 | 377 | 0 | 0 |
| QT_RESIDENT_NUMBER | 1.0000 | 1.0000 | 1.0000 | 185 | 0 | 0 |
| QT_DRIVER_NUMBER | 1.0000 | 1.0000 | 1.0000 | 7 | 0 | 0 |
| QT_CARD_NUMBER | 1.0000 | 1.0000 | 1.0000 | 93 | 0 | 0 |
| QT_PASSPORT_NUMBER | 1.0000 | 1.0000 | 1.0000 | 2 | 0 | 0 |
| QT_PHONE | 0.9973 | 0.9947 | 1.0000 | 186 | 1 | 0 |
| QT_ACCOUNT_NUMBER | 0.9917 | 1.0000 | 0.9835 | 179 | 0 | 3 |
| FD_MAJOR | 0.9915 | 0.9915 | 0.9915 | 117 | 1 | 1 |
| LC_ADDRESS | 0.9783 | 0.9926 | 0.9643 | 270 | 2 | 10 |
| DT_BIRTH | 0.9752 | 0.9793 | 0.9712 | 236 | 5 | 7 |
| PS_NAME | 0.9722 | 0.9997 | 0.9462 | 3164 | 1 | 180 |
| OG_WORKPLACE | 0.9683 | 0.9941 | 0.9438 | 504 | 3 | 30 |
| QT_PLATE_NUMBER | 0.9600 | 0.9231 | 1.0000 | 12 | 1 | 0 |
| TMI_EMAIL | 0.9590 | 1.0000 | 0.9211 | 257 | 0 | 22 |
| OG_DEPARTMENT | 0.9584 | 0.9751 | 0.9423 | 196 | 5 | 12 |
| CV_POSITION | 0.9375 | 0.9449 | 0.9302 | 120 | 7 | 9 |
| QT_AGE | 0.9333 | 0.9130 | 0.9545 | 105 | 10 | 5 |