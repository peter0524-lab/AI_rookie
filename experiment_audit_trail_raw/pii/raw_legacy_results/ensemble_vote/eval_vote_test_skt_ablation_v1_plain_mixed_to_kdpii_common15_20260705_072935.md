# entity-level 다수결 앙상블: test  (20260705_072935)

min_votes=1
data_dir=`/data/team/hwan/data`
evaluated_labels=15: `PS_NAME, LC_ADDRESS, OG_WORKPLACE, OG_DEPARTMENT, CV_POSITION, QT_MOBILE, QT_PHONE, QT_RESIDENT_NUMBER, QT_DRIVER_NUMBER, QT_PLATE_NUMBER, QT_ACCOUNT_NUMBER, QT_CARD_NUMBER, TMI_EMAIL, QT_PASSPORT_NUMBER, DT_BIRTH`
excluded_labels=4: `OGG_EDUCATION, QT_ALIEN_NUMBER, QT_AGE, FD_MAJOR`
excluded_gold_entities=219  excluded_predicted_entities=208

| Entity Micro F1 | **0.9216** |
| Precision | 0.9435 |
| Recall | 0.9008 |
| TP | 1035 | FP | 62 | FN | 114 |

| 레이블 | F1 | P | R | TP | FP | FN |
|--------|-----|---|---|----|----|-----|
| QT_MOBILE | 1.0000 | 1.0000 | 1.0000 | 55 | 0 | 0 |
| QT_PHONE | 1.0000 | 1.0000 | 1.0000 | 69 | 0 | 0 |
| QT_DRIVER_NUMBER | 1.0000 | 1.0000 | 1.0000 | 17 | 0 | 0 |
| TMI_EMAIL | 1.0000 | 1.0000 | 1.0000 | 81 | 0 | 0 |
| QT_PASSPORT_NUMBER | 1.0000 | 1.0000 | 1.0000 | 18 | 0 | 0 |
| QT_PLATE_NUMBER | 0.9903 | 1.0000 | 0.9808 | 51 | 0 | 1 |
| QT_CARD_NUMBER | 0.9873 | 0.9750 | 1.0000 | 78 | 2 | 0 |
| DT_BIRTH | 0.9784 | 0.9855 | 0.9714 | 68 | 1 | 2 |
| QT_ACCOUNT_NUMBER | 0.9737 | 0.9867 | 0.9610 | 74 | 1 | 3 |
| QT_RESIDENT_NUMBER | 0.9730 | 0.9474 | 1.0000 | 18 | 1 | 0 |
| OG_DEPARTMENT | 0.9231 | 0.9375 | 0.9091 | 90 | 6 | 9 |
| PS_NAME | 0.8711 | 0.8837 | 0.8588 | 152 | 20 | 25 |
| LC_ADDRESS | 0.8700 | 0.8788 | 0.8614 | 87 | 12 | 14 |
| CV_POSITION | 0.8426 | 0.8919 | 0.7984 | 99 | 12 | 25 |
| OG_WORKPLACE | 0.7879 | 0.9176 | 0.6903 | 78 | 7 | 35 |