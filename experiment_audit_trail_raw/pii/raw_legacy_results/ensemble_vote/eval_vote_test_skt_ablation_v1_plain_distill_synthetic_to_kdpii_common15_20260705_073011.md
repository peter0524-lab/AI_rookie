# entity-level 다수결 앙상블: test  (20260705_073011)

min_votes=1
data_dir=`/data/team/hwan/data`
evaluated_labels=15: `PS_NAME, LC_ADDRESS, OG_WORKPLACE, OG_DEPARTMENT, CV_POSITION, QT_MOBILE, QT_PHONE, QT_RESIDENT_NUMBER, QT_DRIVER_NUMBER, QT_PLATE_NUMBER, QT_ACCOUNT_NUMBER, QT_CARD_NUMBER, TMI_EMAIL, QT_PASSPORT_NUMBER, DT_BIRTH`
excluded_labels=4: `OGG_EDUCATION, QT_ALIEN_NUMBER, QT_AGE, FD_MAJOR`
excluded_gold_entities=219  excluded_predicted_entities=9

| Entity Micro F1 | **0.5394** |
| Precision | 0.6106 |
| Recall | 0.4830 |
| TP | 555 | FP | 354 | FN | 594 |

| 레이블 | F1 | P | R | TP | FP | FN |
|--------|-----|---|---|----|----|-----|
| QT_MOBILE | 1.0000 | 1.0000 | 1.0000 | 55 | 0 | 0 |
| QT_RESIDENT_NUMBER | 1.0000 | 1.0000 | 1.0000 | 18 | 0 | 0 |
| QT_PHONE | 0.9710 | 0.9710 | 0.9710 | 67 | 2 | 2 |
| QT_CARD_NUMBER | 0.7907 | 1.0000 | 0.6538 | 51 | 0 | 27 |
| QT_ACCOUNT_NUMBER | 0.7766 | 0.6577 | 0.9481 | 73 | 38 | 4 |
| TMI_EMAIL | 0.7030 | 0.6905 | 0.7160 | 58 | 26 | 23 |
| PS_NAME | 0.5813 | 0.4393 | 0.8588 | 152 | 194 | 25 |
| DT_BIRTH | 0.4615 | 1.0000 | 0.3000 | 21 | 0 | 49 |
| QT_DRIVER_NUMBER | 0.4545 | 1.0000 | 0.2941 | 5 | 0 | 12 |
| OG_WORKPLACE | 0.3874 | 0.3500 | 0.4336 | 49 | 91 | 64 |
| LC_ADDRESS | 0.0571 | 0.7500 | 0.0297 | 3 | 1 | 98 |
| CV_POSITION | 0.0317 | 1.0000 | 0.0161 | 2 | 0 | 122 |
| OG_DEPARTMENT | 0.0196 | 0.3333 | 0.0101 | 1 | 2 | 98 |
| QT_PLATE_NUMBER | 0.0000 | 0.0000 | 0.0000 | 0 | 0 | 52 |
| QT_PASSPORT_NUMBER | 0.0000 | 0.0000 | 0.0000 | 0 | 0 | 18 |