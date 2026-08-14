# entity-level 다수결 앙상블: test  (20260717_070743)

min_votes=2
data_dir=`/data/team/hwan/real/data/test_sets/combined`
evaluated_labels=19: `PS_NAME, LC_ADDRESS, OG_WORKPLACE, OG_DEPARTMENT, CV_POSITION, OGG_EDUCATION, QT_MOBILE, QT_PHONE, QT_RESIDENT_NUMBER, QT_ALIEN_NUMBER, QT_DRIVER_NUMBER, QT_PLATE_NUMBER, QT_ACCOUNT_NUMBER, QT_CARD_NUMBER, TMI_EMAIL, QT_PASSPORT_NUMBER, QT_AGE, DT_BIRTH, FD_MAJOR`
excluded_labels=0: `-`
excluded_gold_entities=0  excluded_predicted_entities=0

| Entity Micro F1 | **0.9179** |
| Precision | 0.9231 |
| Recall | 0.9129 |
| TP | 7187 | FP | 599 | FN | 686 |

| 레이블 | F1 | P | R | TP | FP | FN |
|--------|-----|---|---|----|----|-----|
| QT_ALIEN_NUMBER | 1.0000 | 1.0000 | 1.0000 | 9 | 0 | 0 |
| QT_PLATE_NUMBER | 1.0000 | 1.0000 | 1.0000 | 64 | 0 | 0 |
| QT_PASSPORT_NUMBER | 1.0000 | 1.0000 | 1.0000 | 20 | 0 | 0 |
| QT_MOBILE | 0.9988 | 0.9977 | 1.0000 | 432 | 1 | 0 |
| QT_RESIDENT_NUMBER | 0.9951 | 0.9902 | 1.0000 | 203 | 2 | 0 |
| OGG_EDUCATION | 0.9917 | 1.0000 | 0.9836 | 300 | 0 | 5 |
| QT_CARD_NUMBER | 0.9856 | 0.9716 | 1.0000 | 171 | 5 | 0 |
| QT_ACCOUNT_NUMBER | 0.9786 | 0.9844 | 0.9730 | 252 | 4 | 7 |
| TMI_EMAIL | 0.9685 | 1.0000 | 0.9389 | 338 | 0 | 22 |
| QT_PHONE | 0.9605 | 0.9239 | 1.0000 | 255 | 21 | 0 |
| LC_ADDRESS | 0.9518 | 0.9456 | 0.9580 | 365 | 21 | 16 |
| PS_NAME | 0.9478 | 0.9859 | 0.9125 | 3213 | 46 | 308 |
| QT_AGE | 0.8706 | 0.8506 | 0.8916 | 148 | 26 | 18 |
| DT_BIRTH | 0.8296 | 0.7857 | 0.8786 | 275 | 75 | 38 |
| QT_DRIVER_NUMBER | 0.8000 | 0.6667 | 1.0000 | 24 | 12 | 0 |
| OG_WORKPLACE | 0.7994 | 0.7670 | 0.8346 | 540 | 164 | 107 |
| CV_POSITION | 0.7573 | 0.8044 | 0.7154 | 181 | 44 | 72 |
| OG_DEPARTMENT | 0.7474 | 0.6977 | 0.8046 | 247 | 107 | 60 |
| FD_MAJOR | 0.7426 | 0.6787 | 0.8197 | 150 | 71 | 33 |