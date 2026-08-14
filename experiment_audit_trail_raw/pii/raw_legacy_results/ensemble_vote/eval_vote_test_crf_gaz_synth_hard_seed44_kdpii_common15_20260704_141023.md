# entity-level 다수결 앙상블: test  (20260704_141023)

min_votes=1
data_dir=`/data/team/hwan/data`
evaluated_labels=15: `PS_NAME, LC_ADDRESS, OG_WORKPLACE, OG_DEPARTMENT, CV_POSITION, QT_MOBILE, QT_PHONE, QT_RESIDENT_NUMBER, QT_DRIVER_NUMBER, QT_PLATE_NUMBER, QT_ACCOUNT_NUMBER, QT_CARD_NUMBER, TMI_EMAIL, QT_PASSPORT_NUMBER, DT_BIRTH`
excluded_labels=4: `OGG_EDUCATION, QT_ALIEN_NUMBER, QT_AGE, FD_MAJOR`
excluded_gold_entities=219  excluded_predicted_entities=9

| Entity Micro F1 | **0.6742** |
| Precision | 0.6970 |
| Recall | 0.6527 |
| TP | 750 | FP | 326 | FN | 399 |

| 레이블 | F1 | P | R | TP | FP | FN |
|--------|-----|---|---|----|----|-----|
| QT_MOBILE | 1.0000 | 1.0000 | 1.0000 | 55 | 0 | 0 |
| QT_PASSPORT_NUMBER | 1.0000 | 1.0000 | 1.0000 | 18 | 0 | 0 |
| QT_PHONE | 0.9020 | 0.8214 | 1.0000 | 69 | 15 | 0 |
| QT_RESIDENT_NUMBER | 0.9000 | 0.8182 | 1.0000 | 18 | 4 | 0 |
| DT_BIRTH | 0.8346 | 0.9298 | 0.7571 | 53 | 4 | 17 |
| TMI_EMAIL | 0.8223 | 0.6983 | 1.0000 | 81 | 35 | 0 |
| QT_DRIVER_NUMBER | 0.8125 | 0.8667 | 0.7647 | 13 | 2 | 4 |
| QT_CARD_NUMBER | 0.8092 | 1.0000 | 0.6795 | 53 | 0 | 25 |
| QT_ACCOUNT_NUMBER | 0.8022 | 0.6952 | 0.9481 | 73 | 32 | 4 |
| PS_NAME | 0.7340 | 0.6935 | 0.7797 | 138 | 61 | 39 |
| CV_POSITION | 0.5202 | 0.9184 | 0.3629 | 45 | 4 | 79 |
| OG_WORKPLACE | 0.4489 | 0.3305 | 0.6991 | 79 | 160 | 34 |
| LC_ADDRESS | 0.3840 | 1.0000 | 0.2376 | 24 | 0 | 77 |
| OG_DEPARTMENT | 0.3788 | 0.7576 | 0.2525 | 25 | 8 | 74 |
| QT_PLATE_NUMBER | 0.2034 | 0.8571 | 0.1154 | 6 | 1 | 46 |