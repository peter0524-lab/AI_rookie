# entity-level 다수결 앙상블: test  (20260705_073633)

min_votes=1
data_dir=`/data/team/hwan/data`
evaluated_labels=19: `PS_NAME, LC_ADDRESS, OG_WORKPLACE, OG_DEPARTMENT, CV_POSITION, OGG_EDUCATION, QT_MOBILE, QT_PHONE, QT_RESIDENT_NUMBER, QT_ALIEN_NUMBER, QT_DRIVER_NUMBER, QT_PLATE_NUMBER, QT_ACCOUNT_NUMBER, QT_CARD_NUMBER, TMI_EMAIL, QT_PASSPORT_NUMBER, QT_AGE, DT_BIRTH, FD_MAJOR`
excluded_labels=0: `-`
excluded_gold_entities=0  excluded_predicted_entities=0

| Entity Micro F1 | **0.9581** |
| Precision | 0.9722 |
| Recall | 0.9444 |
| TP | 1292 | FP | 37 | FN | 76 |

| 레이블 | F1 | P | R | TP | FP | FN |
|--------|-----|---|---|----|----|-----|
| QT_MOBILE | 1.0000 | 1.0000 | 1.0000 | 55 | 0 | 0 |
| QT_PHONE | 1.0000 | 1.0000 | 1.0000 | 69 | 0 | 0 |
| QT_RESIDENT_NUMBER | 1.0000 | 1.0000 | 1.0000 | 18 | 0 | 0 |
| QT_ALIEN_NUMBER | 1.0000 | 1.0000 | 1.0000 | 9 | 0 | 0 |
| QT_DRIVER_NUMBER | 1.0000 | 1.0000 | 1.0000 | 17 | 0 | 0 |
| QT_PLATE_NUMBER | 1.0000 | 1.0000 | 1.0000 | 52 | 0 | 0 |
| QT_ACCOUNT_NUMBER | 1.0000 | 1.0000 | 1.0000 | 77 | 0 | 0 |
| QT_CARD_NUMBER | 1.0000 | 1.0000 | 1.0000 | 78 | 0 | 0 |
| TMI_EMAIL | 1.0000 | 1.0000 | 1.0000 | 81 | 0 | 0 |
| QT_PASSPORT_NUMBER | 1.0000 | 1.0000 | 1.0000 | 18 | 0 | 0 |
| OG_DEPARTMENT | 0.9949 | 1.0000 | 0.9899 | 98 | 0 | 1 |
| DT_BIRTH | 0.9857 | 0.9857 | 0.9857 | 69 | 1 | 1 |
| FD_MAJOR | 0.9771 | 0.9697 | 0.9846 | 64 | 2 | 1 |
| OGG_EDUCATION | 0.9711 | 1.0000 | 0.9438 | 84 | 0 | 5 |
| QT_AGE | 0.9474 | 0.9310 | 0.9643 | 54 | 4 | 2 |
| LC_ADDRESS | 0.9347 | 0.9490 | 0.9208 | 93 | 5 | 8 |
| PS_NAME | 0.9235 | 0.9261 | 0.9209 | 163 | 13 | 14 |
| CV_POSITION | 0.9167 | 0.9483 | 0.8871 | 110 | 6 | 14 |
| OG_WORKPLACE | 0.8218 | 0.9326 | 0.7345 | 83 | 6 | 30 |