# entity-level 다수결 앙상블: test  (20260731_143351)

min_votes=1
data_dir=`/data/team/hwan/real/data/test_sets/kdpii`
evaluated_labels=19: `PS_NAME, LC_ADDRESS, OG_WORKPLACE, OG_DEPARTMENT, CV_POSITION, OGG_EDUCATION, QT_MOBILE, QT_PHONE, QT_RESIDENT_NUMBER, QT_ALIEN_NUMBER, QT_DRIVER_NUMBER, QT_PLATE_NUMBER, QT_ACCOUNT_NUMBER, QT_CARD_NUMBER, TMI_EMAIL, QT_PASSPORT_NUMBER, QT_AGE, DT_BIRTH, FD_MAJOR`
excluded_labels=0: `-`
excluded_gold_entities=0  excluded_predicted_entities=0

| Entity Micro F1 | **0.9348** |
| Precision | 0.9481 |
| Recall | 0.9218 |
| TP | 1261 | FP | 69 | FN | 107 |

| 레이블 | F1 | P | R | TP | FP | FN |
|--------|-----|---|---|----|----|-----|
| QT_MOBILE | 1.0000 | 1.0000 | 1.0000 | 55 | 0 | 0 |
| QT_PHONE | 1.0000 | 1.0000 | 1.0000 | 69 | 0 | 0 |
| QT_RESIDENT_NUMBER | 1.0000 | 1.0000 | 1.0000 | 18 | 0 | 0 |
| QT_ALIEN_NUMBER | 1.0000 | 1.0000 | 1.0000 | 9 | 0 | 0 |
| QT_DRIVER_NUMBER | 1.0000 | 1.0000 | 1.0000 | 17 | 0 | 0 |
| TMI_EMAIL | 1.0000 | 1.0000 | 1.0000 | 81 | 0 | 0 |
| QT_PASSPORT_NUMBER | 1.0000 | 1.0000 | 1.0000 | 18 | 0 | 0 |
| QT_CARD_NUMBER | 0.9873 | 0.9750 | 1.0000 | 78 | 2 | 0 |
| DT_BIRTH | 0.9857 | 0.9857 | 0.9857 | 69 | 1 | 1 |
| QT_ACCOUNT_NUMBER | 0.9804 | 0.9868 | 0.9740 | 75 | 1 | 2 |
| OG_DEPARTMENT | 0.9746 | 0.9796 | 0.9697 | 96 | 2 | 3 |
| QT_PLATE_NUMBER | 0.9608 | 0.9800 | 0.9423 | 49 | 1 | 3 |
| FD_MAJOR | 0.9440 | 0.9833 | 0.9077 | 59 | 1 | 6 |
| QT_AGE | 0.9369 | 0.9455 | 0.9286 | 52 | 3 | 4 |
| OGG_EDUCATION | 0.9357 | 0.9756 | 0.8989 | 80 | 2 | 9 |
| PS_NAME | 0.9050 | 0.8950 | 0.9153 | 162 | 19 | 15 |
| LC_ADDRESS | 0.8900 | 0.8990 | 0.8812 | 89 | 10 | 12 |
| CV_POSITION | 0.8632 | 0.9182 | 0.8145 | 101 | 9 | 23 |
| OG_WORKPLACE | 0.7814 | 0.8235 | 0.7434 | 84 | 18 | 29 |