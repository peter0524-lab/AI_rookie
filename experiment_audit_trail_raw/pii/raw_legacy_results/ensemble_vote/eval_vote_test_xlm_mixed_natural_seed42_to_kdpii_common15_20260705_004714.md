# entity-level 다수결 앙상블: test  (20260705_004714)

min_votes=1
data_dir=`/data/team/hwan/data`
evaluated_labels=15: `PS_NAME, LC_ADDRESS, OG_WORKPLACE, OG_DEPARTMENT, CV_POSITION, QT_MOBILE, QT_PHONE, QT_RESIDENT_NUMBER, QT_DRIVER_NUMBER, QT_PLATE_NUMBER, QT_ACCOUNT_NUMBER, QT_CARD_NUMBER, TMI_EMAIL, QT_PASSPORT_NUMBER, DT_BIRTH`
excluded_labels=4: `OGG_EDUCATION, QT_ALIEN_NUMBER, QT_AGE, FD_MAJOR`
excluded_gold_entities=219  excluded_predicted_entities=223

| Entity Micro F1 | **0.9531** |
| Precision | 0.9594 |
| Recall | 0.9469 |
| TP | 1088 | FP | 46 | FN | 61 |

| 레이블 | F1 | P | R | TP | FP | FN |
|--------|-----|---|---|----|----|-----|
| QT_PHONE | 1.0000 | 1.0000 | 1.0000 | 69 | 0 | 0 |
| QT_RESIDENT_NUMBER | 1.0000 | 1.0000 | 1.0000 | 18 | 0 | 0 |
| QT_PLATE_NUMBER | 1.0000 | 1.0000 | 1.0000 | 52 | 0 | 0 |
| QT_ACCOUNT_NUMBER | 1.0000 | 1.0000 | 1.0000 | 77 | 0 | 0 |
| QT_CARD_NUMBER | 1.0000 | 1.0000 | 1.0000 | 78 | 0 | 0 |
| TMI_EMAIL | 1.0000 | 1.0000 | 1.0000 | 81 | 0 | 0 |
| QT_PASSPORT_NUMBER | 1.0000 | 1.0000 | 1.0000 | 18 | 0 | 0 |
| QT_MOBILE | 0.9908 | 1.0000 | 0.9818 | 54 | 0 | 1 |
| DT_BIRTH | 0.9857 | 0.9857 | 0.9857 | 69 | 1 | 1 |
| OG_DEPARTMENT | 0.9849 | 0.9800 | 0.9899 | 98 | 2 | 1 |
| QT_DRIVER_NUMBER | 0.9714 | 0.9444 | 1.0000 | 17 | 1 | 0 |
| PS_NAME | 0.9348 | 0.9375 | 0.9322 | 165 | 11 | 12 |
| LC_ADDRESS | 0.8900 | 0.8990 | 0.8812 | 89 | 10 | 12 |
| CV_POSITION | 0.8852 | 0.9000 | 0.8710 | 108 | 12 | 16 |
| OG_WORKPLACE | 0.8756 | 0.9135 | 0.8407 | 95 | 9 | 18 |