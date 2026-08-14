# entity-level 다수결 앙상블: test  (20260705_073424)

min_votes=1
data_dir=`/data/team/hwan/data`
evaluated_labels=15: `PS_NAME, LC_ADDRESS, OG_WORKPLACE, OG_DEPARTMENT, CV_POSITION, QT_MOBILE, QT_PHONE, QT_RESIDENT_NUMBER, QT_DRIVER_NUMBER, QT_PLATE_NUMBER, QT_ACCOUNT_NUMBER, QT_CARD_NUMBER, TMI_EMAIL, QT_PASSPORT_NUMBER, DT_BIRTH`
excluded_labels=4: `OGG_EDUCATION, QT_ALIEN_NUMBER, QT_AGE, FD_MAJOR`
excluded_gold_entities=219  excluded_predicted_entities=217

| Entity Micro F1 | **0.9604** |
| Precision | 0.9723 |
| Recall | 0.9487 |
| TP | 1090 | FP | 31 | FN | 59 |

| 레이블 | F1 | P | R | TP | FP | FN |
|--------|-----|---|---|----|----|-----|
| QT_MOBILE | 1.0000 | 1.0000 | 1.0000 | 55 | 0 | 0 |
| QT_PHONE | 1.0000 | 1.0000 | 1.0000 | 69 | 0 | 0 |
| QT_RESIDENT_NUMBER | 1.0000 | 1.0000 | 1.0000 | 18 | 0 | 0 |
| QT_DRIVER_NUMBER | 1.0000 | 1.0000 | 1.0000 | 17 | 0 | 0 |
| QT_CARD_NUMBER | 1.0000 | 1.0000 | 1.0000 | 78 | 0 | 0 |
| TMI_EMAIL | 1.0000 | 1.0000 | 1.0000 | 81 | 0 | 0 |
| QT_PASSPORT_NUMBER | 1.0000 | 1.0000 | 1.0000 | 18 | 0 | 0 |
| QT_ACCOUNT_NUMBER | 0.9935 | 1.0000 | 0.9870 | 76 | 0 | 1 |
| DT_BIRTH | 0.9929 | 0.9859 | 1.0000 | 70 | 1 | 0 |
| QT_PLATE_NUMBER | 0.9905 | 0.9811 | 1.0000 | 52 | 1 | 0 |
| OG_DEPARTMENT | 0.9900 | 0.9802 | 1.0000 | 99 | 2 | 0 |
| PS_NAME | 0.9398 | 0.9535 | 0.9266 | 164 | 8 | 13 |
| LC_ADDRESS | 0.9246 | 0.9388 | 0.9109 | 92 | 6 | 9 |
| CV_POSITION | 0.9129 | 0.9402 | 0.8871 | 110 | 7 | 14 |
| OG_WORKPLACE | 0.8667 | 0.9381 | 0.8053 | 91 | 6 | 22 |