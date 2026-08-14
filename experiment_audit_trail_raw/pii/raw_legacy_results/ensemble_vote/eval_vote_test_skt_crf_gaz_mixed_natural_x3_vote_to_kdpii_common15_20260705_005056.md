# entity-level 다수결 앙상블: test  (20260705_005056)

min_votes=2
data_dir=`/data/team/hwan/data`
evaluated_labels=15: `PS_NAME, LC_ADDRESS, OG_WORKPLACE, OG_DEPARTMENT, CV_POSITION, QT_MOBILE, QT_PHONE, QT_RESIDENT_NUMBER, QT_DRIVER_NUMBER, QT_PLATE_NUMBER, QT_ACCOUNT_NUMBER, QT_CARD_NUMBER, TMI_EMAIL, QT_PASSPORT_NUMBER, DT_BIRTH`
excluded_labels=4: `OGG_EDUCATION, QT_ALIEN_NUMBER, QT_AGE, FD_MAJOR`
excluded_gold_entities=219  excluded_predicted_entities=219

| Entity Micro F1 | **0.9657** |
| Precision | 0.9760 |
| Recall | 0.9556 |
| TP | 1098 | FP | 27 | FN | 51 |

| 레이블 | F1 | P | R | TP | FP | FN |
|--------|-----|---|---|----|----|-----|
| OG_DEPARTMENT | 1.0000 | 1.0000 | 1.0000 | 99 | 0 | 0 |
| QT_MOBILE | 1.0000 | 1.0000 | 1.0000 | 55 | 0 | 0 |
| QT_PHONE | 1.0000 | 1.0000 | 1.0000 | 69 | 0 | 0 |
| QT_RESIDENT_NUMBER | 1.0000 | 1.0000 | 1.0000 | 18 | 0 | 0 |
| QT_DRIVER_NUMBER | 1.0000 | 1.0000 | 1.0000 | 17 | 0 | 0 |
| QT_PLATE_NUMBER | 1.0000 | 1.0000 | 1.0000 | 52 | 0 | 0 |
| QT_ACCOUNT_NUMBER | 1.0000 | 1.0000 | 1.0000 | 77 | 0 | 0 |
| TMI_EMAIL | 1.0000 | 1.0000 | 1.0000 | 81 | 0 | 0 |
| QT_PASSPORT_NUMBER | 1.0000 | 1.0000 | 1.0000 | 18 | 0 | 0 |
| QT_CARD_NUMBER | 0.9935 | 1.0000 | 0.9872 | 77 | 0 | 1 |
| DT_BIRTH | 0.9857 | 0.9857 | 0.9857 | 69 | 1 | 1 |
| PS_NAME | 0.9577 | 0.9551 | 0.9605 | 170 | 8 | 7 |
| LC_ADDRESS | 0.9254 | 0.9300 | 0.9208 | 93 | 7 | 8 |
| CV_POSITION | 0.9218 | 0.9412 | 0.9032 | 112 | 7 | 12 |
| OG_WORKPLACE | 0.8750 | 0.9579 | 0.8053 | 91 | 4 | 22 |