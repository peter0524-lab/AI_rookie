# entity-level 다수결 앙상블: test  (20260705_073129)

min_votes=1
data_dir=`/data/team/hwan/data`
evaluated_labels=15: `PS_NAME, LC_ADDRESS, OG_WORKPLACE, OG_DEPARTMENT, CV_POSITION, QT_MOBILE, QT_PHONE, QT_RESIDENT_NUMBER, QT_DRIVER_NUMBER, QT_PLATE_NUMBER, QT_ACCOUNT_NUMBER, QT_CARD_NUMBER, TMI_EMAIL, QT_PASSPORT_NUMBER, DT_BIRTH`
excluded_labels=4: `OGG_EDUCATION, QT_ALIEN_NUMBER, QT_AGE, FD_MAJOR`
excluded_gold_entities=219  excluded_predicted_entities=9

| Entity Micro F1 | **0.6622** |
| Precision | 0.7341 |
| Recall | 0.6031 |
| TP | 693 | FP | 251 | FN | 456 |

| 레이블 | F1 | P | R | TP | FP | FN |
|--------|-----|---|---|----|----|-----|
| QT_MOBILE | 1.0000 | 1.0000 | 1.0000 | 55 | 0 | 0 |
| QT_RESIDENT_NUMBER | 1.0000 | 1.0000 | 1.0000 | 18 | 0 | 0 |
| QT_PASSPORT_NUMBER | 1.0000 | 1.0000 | 1.0000 | 18 | 0 | 0 |
| QT_PHONE | 0.9855 | 0.9855 | 0.9855 | 68 | 1 | 1 |
| TMI_EMAIL | 0.9818 | 0.9643 | 1.0000 | 81 | 3 | 0 |
| QT_CARD_NUMBER | 0.8000 | 1.0000 | 0.6667 | 52 | 0 | 26 |
| QT_ACCOUNT_NUMBER | 0.7978 | 0.6887 | 0.9481 | 73 | 33 | 4 |
| PS_NAME | 0.7676 | 0.7136 | 0.8305 | 147 | 59 | 30 |
| QT_DRIVER_NUMBER | 0.7143 | 0.9091 | 0.5882 | 10 | 1 | 7 |
| DT_BIRTH | 0.6095 | 0.9143 | 0.4571 | 32 | 3 | 38 |
| CV_POSITION | 0.4643 | 0.8864 | 0.3145 | 39 | 5 | 85 |
| OG_WORKPLACE | 0.3669 | 0.3091 | 0.4513 | 51 | 114 | 62 |
| LC_ADDRESS | 0.3387 | 0.9130 | 0.2079 | 21 | 2 | 80 |
| OG_DEPARTMENT | 0.2923 | 0.6129 | 0.1919 | 19 | 12 | 80 |
| QT_PLATE_NUMBER | 0.2278 | 0.3333 | 0.1731 | 9 | 18 | 43 |