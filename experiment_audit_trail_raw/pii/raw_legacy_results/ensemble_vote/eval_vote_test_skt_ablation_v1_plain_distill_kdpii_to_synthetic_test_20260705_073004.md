# entity-level 다수결 앙상블: test  (20260705_073004)

min_votes=1
data_dir=`/data/team/hwan/synthetic`
evaluated_labels=19: `PS_NAME, LC_ADDRESS, OG_WORKPLACE, OG_DEPARTMENT, CV_POSITION, OGG_EDUCATION, QT_MOBILE, QT_PHONE, QT_RESIDENT_NUMBER, QT_ALIEN_NUMBER, QT_DRIVER_NUMBER, QT_PLATE_NUMBER, QT_ACCOUNT_NUMBER, QT_CARD_NUMBER, TMI_EMAIL, QT_PASSPORT_NUMBER, QT_AGE, DT_BIRTH, FD_MAJOR`
excluded_labels=0: `-`
excluded_gold_entities=0  excluded_predicted_entities=0

| Entity Micro F1 | **0.8030** |
| Precision | 0.7367 |
| Recall | 0.8825 |
| TP | 1217 | FP | 435 | FN | 162 |

| 레이블 | F1 | P | R | TP | FP | FN |
|--------|-----|---|---|----|----|-----|
| QT_RESIDENT_NUMBER | 1.0000 | 1.0000 | 1.0000 | 15 | 0 | 0 |
| QT_MOBILE | 0.9960 | 0.9919 | 1.0000 | 123 | 1 | 0 |
| QT_PHONE | 0.9934 | 0.9868 | 1.0000 | 75 | 1 | 0 |
| QT_ACCOUNT_NUMBER | 0.8972 | 0.9600 | 0.8421 | 48 | 2 | 9 |
| TMI_EMAIL | 0.8931 | 0.9590 | 0.8357 | 117 | 5 | 23 |
| QT_PASSPORT_NUMBER | 0.8889 | 0.8889 | 0.8889 | 8 | 1 | 1 |
| QT_CARD_NUMBER | 0.8852 | 0.7941 | 1.0000 | 27 | 7 | 0 |
| QT_DRIVER_NUMBER | 0.8571 | 0.7500 | 1.0000 | 3 | 1 | 0 |
| LC_ADDRESS | 0.8342 | 0.8218 | 0.8469 | 83 | 18 | 15 |
| QT_PLATE_NUMBER | 0.8000 | 0.6667 | 1.0000 | 8 | 4 | 0 |
| PS_NAME | 0.7818 | 0.7026 | 0.8811 | 593 | 251 | 80 |
| OG_WORKPLACE | 0.7477 | 0.6780 | 0.8333 | 40 | 19 | 8 |
| OG_DEPARTMENT | 0.5747 | 0.4167 | 0.9259 | 25 | 35 | 2 |
| DT_BIRTH | 0.5158 | 0.3920 | 0.7538 | 49 | 76 | 16 |
| CV_POSITION | 0.2308 | 0.2000 | 0.2727 | 3 | 12 | 8 |
| OGG_EDUCATION | 0.0000 | 0.0000 | 0.0000 | 0 | 1 | 0 |
| QT_ALIEN_NUMBER | 0.0000 | 0.0000 | 0.0000 | 0 | 0 | 0 |
| QT_AGE | 0.0000 | 0.0000 | 0.0000 | 0 | 1 | 0 |
| FD_MAJOR | 0.0000 | 0.0000 | 0.0000 | 0 | 0 | 0 |