# entity-level 다수결 앙상블: test  (20260715_092004)

min_votes=2
data_dir=`/data/team/hwan/real/data/test_sets/synthetic`
evaluated_labels=19: `PS_NAME, LC_ADDRESS, OG_WORKPLACE, OG_DEPARTMENT, CV_POSITION, OGG_EDUCATION, QT_MOBILE, QT_PHONE, QT_RESIDENT_NUMBER, QT_ALIEN_NUMBER, QT_DRIVER_NUMBER, QT_PLATE_NUMBER, QT_ACCOUNT_NUMBER, QT_CARD_NUMBER, TMI_EMAIL, QT_PASSPORT_NUMBER, QT_AGE, DT_BIRTH, FD_MAJOR`
excluded_labels=0: `-`
excluded_gold_entities=0  excluded_predicted_entities=0

| Entity Micro F1 | **0.9783** |
| Precision | 0.9963 |
| Recall | 0.9610 |
| TP | 6251 | FP | 23 | FN | 254 |

| 레이블 | F1 | P | R | TP | FP | FN |
|--------|-----|---|---|----|----|-----|
| OGG_EDUCATION | 1.0000 | 1.0000 | 1.0000 | 216 | 0 | 0 |
| QT_MOBILE | 1.0000 | 1.0000 | 1.0000 | 377 | 0 | 0 |
| QT_RESIDENT_NUMBER | 1.0000 | 1.0000 | 1.0000 | 185 | 0 | 0 |
| QT_DRIVER_NUMBER | 1.0000 | 1.0000 | 1.0000 | 7 | 0 | 0 |
| QT_PLATE_NUMBER | 1.0000 | 1.0000 | 1.0000 | 12 | 0 | 0 |
| QT_CARD_NUMBER | 1.0000 | 1.0000 | 1.0000 | 93 | 0 | 0 |
| QT_PASSPORT_NUMBER | 1.0000 | 1.0000 | 1.0000 | 2 | 0 | 0 |
| FD_MAJOR | 1.0000 | 1.0000 | 1.0000 | 118 | 0 | 0 |
| QT_PHONE | 0.9973 | 0.9947 | 1.0000 | 186 | 1 | 0 |
| QT_ACCOUNT_NUMBER | 0.9917 | 1.0000 | 0.9835 | 179 | 0 | 3 |
| LC_ADDRESS | 0.9800 | 1.0000 | 0.9607 | 269 | 0 | 11 |
| DT_BIRTH | 0.9793 | 0.9874 | 0.9712 | 236 | 3 | 7 |
| OG_DEPARTMENT | 0.9756 | 0.9901 | 0.9615 | 200 | 2 | 8 |
| PS_NAME | 0.9746 | 0.9997 | 0.9507 | 3179 | 1 | 165 |
| OG_WORKPLACE | 0.9712 | 0.9961 | 0.9476 | 506 | 2 | 28 |
| TMI_EMAIL | 0.9609 | 1.0000 | 0.9247 | 258 | 0 | 21 |
| CV_POSITION | 0.9528 | 0.9680 | 0.9380 | 121 | 4 | 8 |
| QT_AGE | 0.9427 | 0.9145 | 0.9727 | 107 | 10 | 3 |
| QT_ALIEN_NUMBER | 0.0000 | 0.0000 | 0.0000 | 0 | 0 | 0 |