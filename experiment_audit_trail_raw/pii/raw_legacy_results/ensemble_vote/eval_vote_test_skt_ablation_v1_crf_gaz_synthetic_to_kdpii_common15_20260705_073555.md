# entity-level 다수결 앙상블: test  (20260705_073555)

min_votes=1
data_dir=`/data/team/hwan/data`
evaluated_labels=15: `PS_NAME, LC_ADDRESS, OG_WORKPLACE, OG_DEPARTMENT, CV_POSITION, QT_MOBILE, QT_PHONE, QT_RESIDENT_NUMBER, QT_DRIVER_NUMBER, QT_PLATE_NUMBER, QT_ACCOUNT_NUMBER, QT_CARD_NUMBER, TMI_EMAIL, QT_PASSPORT_NUMBER, DT_BIRTH`
excluded_labels=4: `OGG_EDUCATION, QT_ALIEN_NUMBER, QT_AGE, FD_MAJOR`
excluded_gold_entities=219  excluded_predicted_entities=9

| Entity Micro F1 | **0.6431** |
| Precision | 0.6799 |
| Recall | 0.6101 |
| TP | 701 | FP | 330 | FN | 448 |

| 레이블 | F1 | P | R | TP | FP | FN |
|--------|-----|---|---|----|----|-----|
| QT_MOBILE | 1.0000 | 1.0000 | 1.0000 | 55 | 0 | 0 |
| QT_PASSPORT_NUMBER | 1.0000 | 1.0000 | 1.0000 | 18 | 0 | 0 |
| QT_PHONE | 0.9640 | 0.9571 | 0.9710 | 67 | 3 | 2 |
| TMI_EMAIL | 0.9364 | 0.8804 | 1.0000 | 81 | 11 | 0 |
| QT_RESIDENT_NUMBER | 0.9231 | 0.8571 | 1.0000 | 18 | 3 | 0 |
| QT_CARD_NUMBER | 0.8000 | 1.0000 | 0.6667 | 52 | 0 | 26 |
| QT_DRIVER_NUMBER | 0.7879 | 0.8125 | 0.7647 | 13 | 3 | 4 |
| QT_ACCOUNT_NUMBER | 0.7821 | 0.7722 | 0.7922 | 61 | 18 | 16 |
| PS_NAME | 0.7662 | 0.6844 | 0.8701 | 154 | 71 | 23 |
| DT_BIRTH | 0.6727 | 0.9250 | 0.5286 | 37 | 3 | 33 |
| CV_POSITION | 0.4578 | 0.9048 | 0.3065 | 38 | 4 | 86 |
| OG_WORKPLACE | 0.4167 | 0.3266 | 0.5752 | 65 | 134 | 48 |
| OG_DEPARTMENT | 0.2880 | 0.6923 | 0.1818 | 18 | 8 | 81 |
| LC_ADDRESS | 0.2124 | 1.0000 | 0.1188 | 12 | 0 | 89 |
| QT_PLATE_NUMBER | 0.1765 | 0.1429 | 0.2308 | 12 | 72 | 40 |