# entity-level 다수결 앙상블: test  (20260704_153256)

min_votes=1
data_dir=`/data/team/hwan/data`
evaluated_labels=15: `PS_NAME, LC_ADDRESS, OG_WORKPLACE, OG_DEPARTMENT, CV_POSITION, QT_MOBILE, QT_PHONE, QT_RESIDENT_NUMBER, QT_DRIVER_NUMBER, QT_PLATE_NUMBER, QT_ACCOUNT_NUMBER, QT_CARD_NUMBER, TMI_EMAIL, QT_PASSPORT_NUMBER, DT_BIRTH`
excluded_labels=4: `OGG_EDUCATION, QT_ALIEN_NUMBER, QT_AGE, FD_MAJOR`
excluded_gold_entities=219  excluded_predicted_entities=9

| Entity Micro F1 | **0.4542** |
| Precision | 0.7167 |
| Recall | 0.3325 |
| TP | 382 | FP | 151 | FN | 767 |

| 레이블 | F1 | P | R | TP | FP | FN |
|--------|-----|---|---|----|----|-----|
| QT_MOBILE | 1.0000 | 1.0000 | 1.0000 | 55 | 0 | 0 |
| QT_PHONE | 0.9650 | 0.9324 | 1.0000 | 69 | 5 | 0 |
| QT_CARD_NUMBER | 0.8406 | 0.9667 | 0.7436 | 58 | 2 | 20 |
| DT_BIRTH | 0.8293 | 0.9623 | 0.7286 | 51 | 2 | 19 |
| QT_ACCOUNT_NUMBER | 0.8129 | 0.8077 | 0.8182 | 63 | 15 | 14 |
| QT_RESIDENT_NUMBER | 0.8000 | 0.6667 | 1.0000 | 18 | 9 | 0 |
| TMI_EMAIL | 0.4272 | 1.0000 | 0.2716 | 22 | 0 | 59 |
| QT_DRIVER_NUMBER | 0.3182 | 0.2593 | 0.4118 | 7 | 20 | 10 |
| PS_NAME | 0.2475 | 0.3033 | 0.2090 | 37 | 85 | 140 |
| QT_PLATE_NUMBER | 0.0377 | 1.0000 | 0.0192 | 1 | 0 | 51 |
| OG_WORKPLACE | 0.0157 | 0.0714 | 0.0088 | 1 | 13 | 112 |
| LC_ADDRESS | 0.0000 | 0.0000 | 0.0000 | 0 | 0 | 101 |
| OG_DEPARTMENT | 0.0000 | 0.0000 | 0.0000 | 0 | 0 | 99 |
| CV_POSITION | 0.0000 | 0.0000 | 0.0000 | 0 | 0 | 124 |
| QT_PASSPORT_NUMBER | 0.0000 | 0.0000 | 0.0000 | 0 | 0 | 18 |