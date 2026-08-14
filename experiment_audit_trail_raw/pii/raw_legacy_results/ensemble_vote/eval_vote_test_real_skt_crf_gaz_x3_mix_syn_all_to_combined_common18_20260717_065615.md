# entity-level 다수결 앙상블: test  (20260717_065615)

min_votes=2
data_dir=`/data/team/hwan/real/data/test_sets/combined`
evaluated_labels=18: `PS_NAME, LC_ADDRESS, OG_WORKPLACE, OG_DEPARTMENT, CV_POSITION, OGG_EDUCATION, QT_MOBILE, QT_PHONE, QT_RESIDENT_NUMBER, QT_DRIVER_NUMBER, QT_PLATE_NUMBER, QT_ACCOUNT_NUMBER, QT_CARD_NUMBER, TMI_EMAIL, QT_PASSPORT_NUMBER, QT_AGE, DT_BIRTH, FD_MAJOR`
excluded_labels=1: `QT_ALIEN_NUMBER`
excluded_gold_entities=9  excluded_predicted_entities=9

| Entity Micro F1 | **0.9744** |
| Precision | 0.9921 |
| Recall | 0.9574 |
| TP | 7529 | FP | 60 | FN | 335 |

| 레이블 | F1 | P | R | TP | FP | FN |
|--------|-----|---|---|----|----|-----|
| QT_MOBILE | 1.0000 | 1.0000 | 1.0000 | 432 | 0 | 0 |
| QT_RESIDENT_NUMBER | 1.0000 | 1.0000 | 1.0000 | 203 | 0 | 0 |
| QT_DRIVER_NUMBER | 1.0000 | 1.0000 | 1.0000 | 24 | 0 | 0 |
| QT_PLATE_NUMBER | 1.0000 | 1.0000 | 1.0000 | 64 | 0 | 0 |
| QT_CARD_NUMBER | 1.0000 | 1.0000 | 1.0000 | 171 | 0 | 0 |
| QT_PASSPORT_NUMBER | 1.0000 | 1.0000 | 1.0000 | 20 | 0 | 0 |
| QT_PHONE | 0.9980 | 0.9961 | 1.0000 | 255 | 1 | 0 |
| QT_ACCOUNT_NUMBER | 0.9942 | 1.0000 | 0.9884 | 256 | 0 | 3 |
| OGG_EDUCATION | 0.9934 | 0.9967 | 0.9902 | 302 | 1 | 3 |
| FD_MAJOR | 0.9918 | 0.9891 | 0.9945 | 182 | 2 | 1 |
| DT_BIRTH | 0.9791 | 0.9839 | 0.9744 | 305 | 5 | 8 |
| OG_DEPARTMENT | 0.9718 | 0.9899 | 0.9544 | 293 | 3 | 14 |
| PS_NAME | 0.9713 | 0.9973 | 0.9466 | 3333 | 9 | 188 |
| TMI_EMAIL | 0.9685 | 1.0000 | 0.9389 | 338 | 0 | 22 |
| LC_ADDRESS | 0.9680 | 0.9837 | 0.9528 | 363 | 6 | 18 |
| OG_WORKPLACE | 0.9502 | 0.9899 | 0.9134 | 591 | 6 | 56 |
| QT_AGE | 0.9501 | 0.9257 | 0.9759 | 162 | 13 | 4 |
| CV_POSITION | 0.9363 | 0.9438 | 0.9289 | 235 | 14 | 18 |