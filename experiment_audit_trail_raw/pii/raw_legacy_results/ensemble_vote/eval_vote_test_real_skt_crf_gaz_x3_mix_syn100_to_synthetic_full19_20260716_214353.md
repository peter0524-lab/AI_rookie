# entity-level 다수결 앙상블: test  (20260716_214353)

min_votes=2
data_dir=`/data/team/hwan/real/data/test_sets/synthetic`
evaluated_labels=19: `PS_NAME, LC_ADDRESS, OG_WORKPLACE, OG_DEPARTMENT, CV_POSITION, OGG_EDUCATION, QT_MOBILE, QT_PHONE, QT_RESIDENT_NUMBER, QT_ALIEN_NUMBER, QT_DRIVER_NUMBER, QT_PLATE_NUMBER, QT_ACCOUNT_NUMBER, QT_CARD_NUMBER, TMI_EMAIL, QT_PASSPORT_NUMBER, QT_AGE, DT_BIRTH, FD_MAJOR`
excluded_labels=0: `-`
excluded_gold_entities=0  excluded_predicted_entities=0

| Entity Micro F1 | **0.9764** |
| Precision | 0.9957 |
| Recall | 0.9579 |
| TP | 6231 | FP | 27 | FN | 274 |

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
| FD_MAJOR | 0.9916 | 0.9833 | 1.0000 | 118 | 2 | 0 |
| LC_ADDRESS | 0.9800 | 0.9963 | 0.9643 | 270 | 1 | 10 |
| DT_BIRTH | 0.9793 | 0.9874 | 0.9712 | 236 | 3 | 7 |
| PS_NAME | 0.9725 | 0.9997 | 0.9468 | 3166 | 1 | 178 |
| OG_WORKPLACE | 0.9692 | 0.9960 | 0.9438 | 504 | 2 | 30 |
| OG_DEPARTMENT | 0.9682 | 0.9851 | 0.9519 | 198 | 3 | 10 |
| TMI_EMAIL | 0.9590 | 1.0000 | 0.9211 | 257 | 0 | 22 |
| CV_POSITION | 0.9444 | 0.9675 | 0.9225 | 119 | 4 | 10 |
| QT_AGE | 0.9381 | 0.9138 | 0.9636 | 106 | 10 | 4 |
| QT_ALIEN_NUMBER | 0.0000 | 0.0000 | 0.0000 | 0 | 0 | 0 |