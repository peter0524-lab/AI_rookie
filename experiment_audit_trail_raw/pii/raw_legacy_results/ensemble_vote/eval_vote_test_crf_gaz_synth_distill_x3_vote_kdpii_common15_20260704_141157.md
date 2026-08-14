# entity-level 다수결 앙상블: test  (20260704_141157)

min_votes=2
data_dir=`/data/team/hwan/data`
evaluated_labels=15: `PS_NAME, LC_ADDRESS, OG_WORKPLACE, OG_DEPARTMENT, CV_POSITION, QT_MOBILE, QT_PHONE, QT_RESIDENT_NUMBER, QT_DRIVER_NUMBER, QT_PLATE_NUMBER, QT_ACCOUNT_NUMBER, QT_CARD_NUMBER, TMI_EMAIL, QT_PASSPORT_NUMBER, DT_BIRTH`
excluded_labels=4: `OGG_EDUCATION, QT_ALIEN_NUMBER, QT_AGE, FD_MAJOR`
excluded_gold_entities=219  excluded_predicted_entities=9

| Entity Micro F1 | **0.6774** |
| Precision | 0.6795 |
| Recall | 0.6754 |
| TP | 776 | FP | 366 | FN | 373 |

| 레이블 | F1 | P | R | TP | FP | FN |
|--------|-----|---|---|----|----|-----|
| QT_MOBILE | 1.0000 | 1.0000 | 1.0000 | 55 | 0 | 0 |
| QT_RESIDENT_NUMBER | 1.0000 | 1.0000 | 1.0000 | 18 | 0 | 0 |
| QT_PASSPORT_NUMBER | 1.0000 | 1.0000 | 1.0000 | 18 | 0 | 0 |
| QT_PHONE | 0.9718 | 0.9452 | 1.0000 | 69 | 4 | 0 |
| QT_DRIVER_NUMBER | 0.9697 | 1.0000 | 0.9412 | 16 | 0 | 1 |
| DT_BIRTH | 0.9343 | 0.9552 | 0.9143 | 64 | 3 | 6 |
| TMI_EMAIL | 0.8182 | 0.6923 | 1.0000 | 81 | 36 | 0 |
| QT_ACCOUNT_NUMBER | 0.8161 | 0.7320 | 0.9221 | 71 | 26 | 6 |
| QT_CARD_NUMBER | 0.7907 | 1.0000 | 0.6538 | 51 | 0 | 27 |
| PS_NAME | 0.7082 | 0.5846 | 0.8983 | 159 | 113 | 18 |
| LC_ADDRESS | 0.5000 | 0.9714 | 0.3366 | 34 | 1 | 67 |
| CV_POSITION | 0.4472 | 0.9730 | 0.2903 | 36 | 1 | 88 |
| OG_WORKPLACE | 0.4324 | 0.3113 | 0.7080 | 80 | 177 | 33 |
| OG_DEPARTMENT | 0.3279 | 0.8696 | 0.2020 | 20 | 3 | 79 |
| QT_PLATE_NUMBER | 0.1379 | 0.6667 | 0.0769 | 4 | 2 | 48 |