# entity-level 다수결 앙상블: test  (20260705_050637)

min_votes=2
data_dir=`/data/team/hwan/synthetic`
evaluated_labels=19: `PS_NAME, LC_ADDRESS, OG_WORKPLACE, OG_DEPARTMENT, CV_POSITION, OGG_EDUCATION, QT_MOBILE, QT_PHONE, QT_RESIDENT_NUMBER, QT_ALIEN_NUMBER, QT_DRIVER_NUMBER, QT_PLATE_NUMBER, QT_ACCOUNT_NUMBER, QT_CARD_NUMBER, TMI_EMAIL, QT_PASSPORT_NUMBER, QT_AGE, DT_BIRTH, FD_MAJOR`
excluded_labels=0: `-`
excluded_gold_entities=0  excluded_predicted_entities=0

| Entity Micro F1 | **0.8569** |
| Precision | 0.8475 |
| Recall | 0.8666 |
| TP | 1195 | FP | 215 | FN | 184 |

| 레이블 | F1 | P | R | TP | FP | FN |
|--------|-----|---|---|----|----|-----|
| QT_PLATE_NUMBER | 1.0000 | 1.0000 | 1.0000 | 8 | 0 | 0 |
| QT_MOBILE | 0.9960 | 0.9919 | 1.0000 | 123 | 1 | 0 |
| QT_CARD_NUMBER | 0.9643 | 0.9310 | 1.0000 | 27 | 2 | 0 |
| QT_PHONE | 0.9554 | 0.9146 | 1.0000 | 75 | 7 | 0 |
| QT_PASSPORT_NUMBER | 0.9474 | 0.9000 | 1.0000 | 9 | 1 | 0 |
| TMI_EMAIL | 0.9313 | 1.0000 | 0.8714 | 122 | 0 | 18 |
| QT_ACCOUNT_NUMBER | 0.9074 | 0.9608 | 0.8596 | 49 | 2 | 8 |
| PS_NAME | 0.8979 | 0.9610 | 0.8425 | 567 | 23 | 106 |
| QT_RESIDENT_NUMBER | 0.7500 | 0.6000 | 1.0000 | 15 | 10 | 0 |
| LC_ADDRESS | 0.7249 | 0.6336 | 0.8469 | 83 | 48 | 15 |
| OG_WORKPLACE | 0.7170 | 0.6552 | 0.7917 | 38 | 20 | 10 |
| OG_DEPARTMENT | 0.6250 | 0.4717 | 0.9259 | 25 | 28 | 2 |
| DT_BIRTH | 0.6144 | 0.5341 | 0.7231 | 47 | 41 | 18 |
| QT_DRIVER_NUMBER | 0.2857 | 0.1667 | 1.0000 | 3 | 15 | 0 |
| CV_POSITION | 0.2581 | 0.2000 | 0.3636 | 4 | 16 | 7 |
| OGG_EDUCATION | 0.0000 | 0.0000 | 0.0000 | 0 | 0 | 0 |
| QT_ALIEN_NUMBER | 0.0000 | 0.0000 | 0.0000 | 0 | 0 | 0 |
| QT_AGE | 0.0000 | 0.0000 | 0.0000 | 0 | 1 | 0 |
| FD_MAJOR | 0.0000 | 0.0000 | 0.0000 | 0 | 0 | 0 |