# entity-level 다수결 앙상블: test  (20260716_132300)

min_votes=2
data_dir=`/data/team/hwan/real/data/test_sets/combined`
evaluated_labels=18: `PS_NAME, LC_ADDRESS, OG_WORKPLACE, OG_DEPARTMENT, CV_POSITION, OGG_EDUCATION, QT_MOBILE, QT_PHONE, QT_RESIDENT_NUMBER, QT_DRIVER_NUMBER, QT_PLATE_NUMBER, QT_ACCOUNT_NUMBER, QT_CARD_NUMBER, TMI_EMAIL, QT_PASSPORT_NUMBER, QT_AGE, DT_BIRTH, FD_MAJOR`
excluded_labels=1: `QT_ALIEN_NUMBER`
excluded_gold_entities=9  excluded_predicted_entities=9

| Entity Micro F1 | **0.9736** |
| Precision | 0.9903 |
| Recall | 0.9575 |
| TP | 7530 | FP | 74 | FN | 334 |

| 레이블 | F1 | P | R | TP | FP | FN |
|--------|-----|---|---|----|----|-----|
| QT_MOBILE | 1.0000 | 1.0000 | 1.0000 | 432 | 0 | 0 |
| QT_RESIDENT_NUMBER | 1.0000 | 1.0000 | 1.0000 | 203 | 0 | 0 |
| QT_DRIVER_NUMBER | 1.0000 | 1.0000 | 1.0000 | 24 | 0 | 0 |
| QT_PASSPORT_NUMBER | 1.0000 | 1.0000 | 1.0000 | 20 | 0 | 0 |
| QT_PHONE | 0.9980 | 0.9961 | 1.0000 | 255 | 1 | 0 |
| QT_CARD_NUMBER | 0.9971 | 1.0000 | 0.9942 | 170 | 0 | 1 |
| OGG_EDUCATION | 0.9951 | 0.9967 | 0.9934 | 303 | 1 | 2 |
| QT_ACCOUNT_NUMBER | 0.9942 | 1.0000 | 0.9884 | 256 | 0 | 3 |
| QT_PLATE_NUMBER | 0.9922 | 0.9846 | 1.0000 | 64 | 1 | 0 |
| FD_MAJOR | 0.9891 | 0.9838 | 0.9945 | 182 | 3 | 1 |
| DT_BIRTH | 0.9776 | 0.9807 | 0.9744 | 305 | 6 | 8 |
| PS_NAME | 0.9707 | 0.9958 | 0.9469 | 3334 | 14 | 187 |
| OG_DEPARTMENT | 0.9703 | 0.9833 | 0.9577 | 294 | 5 | 13 |
| TMI_EMAIL | 0.9685 | 1.0000 | 0.9389 | 338 | 0 | 22 |
| LC_ADDRESS | 0.9680 | 0.9837 | 0.9528 | 363 | 6 | 18 |
| OG_WORKPLACE | 0.9536 | 0.9884 | 0.9212 | 596 | 7 | 51 |
| QT_AGE | 0.9440 | 0.9249 | 0.9639 | 160 | 13 | 6 |
| CV_POSITION | 0.9222 | 0.9315 | 0.9130 | 231 | 17 | 22 |