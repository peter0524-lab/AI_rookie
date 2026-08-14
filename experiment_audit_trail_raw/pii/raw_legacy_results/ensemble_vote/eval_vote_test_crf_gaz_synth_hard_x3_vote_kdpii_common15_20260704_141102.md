# entity-level 다수결 앙상블: test  (20260704_141102)

min_votes=2
data_dir=`/data/team/hwan/data`
evaluated_labels=15: `PS_NAME, LC_ADDRESS, OG_WORKPLACE, OG_DEPARTMENT, CV_POSITION, QT_MOBILE, QT_PHONE, QT_RESIDENT_NUMBER, QT_DRIVER_NUMBER, QT_PLATE_NUMBER, QT_ACCOUNT_NUMBER, QT_CARD_NUMBER, TMI_EMAIL, QT_PASSPORT_NUMBER, DT_BIRTH`
excluded_labels=4: `OGG_EDUCATION, QT_ALIEN_NUMBER, QT_AGE, FD_MAJOR`
excluded_gold_entities=219  excluded_predicted_entities=9

| Entity Micro F1 | **0.6920** |
| Precision | 0.7309 |
| Recall | 0.6571 |
| TP | 755 | FP | 278 | FN | 394 |

| 레이블 | F1 | P | R | TP | FP | FN |
|--------|-----|---|---|----|----|-----|
| QT_MOBILE | 1.0000 | 1.0000 | 1.0000 | 55 | 0 | 0 |
| QT_PASSPORT_NUMBER | 1.0000 | 1.0000 | 1.0000 | 18 | 0 | 0 |
| QT_RESIDENT_NUMBER | 0.9474 | 0.9000 | 1.0000 | 18 | 2 | 0 |
| QT_PHONE | 0.9324 | 0.8734 | 1.0000 | 69 | 10 | 0 |
| QT_DRIVER_NUMBER | 0.9032 | 1.0000 | 0.8235 | 14 | 0 | 3 |
| QT_ACCOUNT_NUMBER | 0.8475 | 0.7500 | 0.9740 | 75 | 25 | 2 |
| TMI_EMAIL | 0.8351 | 0.7168 | 1.0000 | 81 | 32 | 0 |
| DT_BIRTH | 0.8281 | 0.9138 | 0.7571 | 53 | 5 | 17 |
| QT_CARD_NUMBER | 0.8092 | 1.0000 | 0.6795 | 53 | 0 | 25 |
| PS_NAME | 0.7684 | 0.6991 | 0.8531 | 151 | 65 | 26 |
| CV_POSITION | 0.5116 | 0.9167 | 0.3548 | 44 | 4 | 80 |
| OG_WORKPLACE | 0.4795 | 0.3725 | 0.6726 | 76 | 128 | 37 |
| OG_DEPARTMENT | 0.3817 | 0.7812 | 0.2525 | 25 | 7 | 74 |
| QT_PLATE_NUMBER | 0.2667 | 1.0000 | 0.1538 | 8 | 0 | 44 |
| LC_ADDRESS | 0.2586 | 1.0000 | 0.1485 | 15 | 0 | 86 |