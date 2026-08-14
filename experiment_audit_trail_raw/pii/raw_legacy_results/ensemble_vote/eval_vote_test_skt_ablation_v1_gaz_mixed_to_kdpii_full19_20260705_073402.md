# entity-level 다수결 앙상블: test  (20260705_073402)

min_votes=1
data_dir=`/data/team/hwan/data`
evaluated_labels=19: `PS_NAME, LC_ADDRESS, OG_WORKPLACE, OG_DEPARTMENT, CV_POSITION, OGG_EDUCATION, QT_MOBILE, QT_PHONE, QT_RESIDENT_NUMBER, QT_ALIEN_NUMBER, QT_DRIVER_NUMBER, QT_PLATE_NUMBER, QT_ACCOUNT_NUMBER, QT_CARD_NUMBER, TMI_EMAIL, QT_PASSPORT_NUMBER, QT_AGE, DT_BIRTH, FD_MAJOR`
excluded_labels=0: `-`
excluded_gold_entities=0  excluded_predicted_entities=0

| Entity Micro F1 | **0.9623** |
| Precision | 0.9731 |
| Recall | 0.9518 |
| TP | 1302 | FP | 36 | FN | 66 |

| 레이블 | F1 | P | R | TP | FP | FN |
|--------|-----|---|---|----|----|-----|
| QT_MOBILE | 1.0000 | 1.0000 | 1.0000 | 55 | 0 | 0 |
| QT_PHONE | 1.0000 | 1.0000 | 1.0000 | 69 | 0 | 0 |
| QT_RESIDENT_NUMBER | 1.0000 | 1.0000 | 1.0000 | 18 | 0 | 0 |
| QT_ALIEN_NUMBER | 1.0000 | 1.0000 | 1.0000 | 9 | 0 | 0 |
| QT_DRIVER_NUMBER | 1.0000 | 1.0000 | 1.0000 | 17 | 0 | 0 |
| QT_CARD_NUMBER | 1.0000 | 1.0000 | 1.0000 | 78 | 0 | 0 |
| TMI_EMAIL | 1.0000 | 1.0000 | 1.0000 | 81 | 0 | 0 |
| QT_PASSPORT_NUMBER | 1.0000 | 1.0000 | 1.0000 | 18 | 0 | 0 |
| QT_ACCOUNT_NUMBER | 0.9935 | 1.0000 | 0.9870 | 76 | 0 | 1 |
| DT_BIRTH | 0.9929 | 0.9859 | 1.0000 | 70 | 1 | 0 |
| QT_PLATE_NUMBER | 0.9905 | 0.9811 | 1.0000 | 52 | 1 | 0 |
| OG_DEPARTMENT | 0.9900 | 0.9802 | 1.0000 | 99 | 2 | 0 |
| OGG_EDUCATION | 0.9770 | 1.0000 | 0.9551 | 85 | 0 | 4 |
| FD_MAJOR | 0.9767 | 0.9844 | 0.9692 | 63 | 1 | 2 |
| QT_AGE | 0.9565 | 0.9322 | 0.9821 | 55 | 4 | 1 |
| PS_NAME | 0.9398 | 0.9535 | 0.9266 | 164 | 8 | 13 |
| LC_ADDRESS | 0.9246 | 0.9388 | 0.9109 | 92 | 6 | 9 |
| CV_POSITION | 0.9129 | 0.9402 | 0.8871 | 110 | 7 | 14 |
| OG_WORKPLACE | 0.8667 | 0.9381 | 0.8053 | 91 | 6 | 22 |