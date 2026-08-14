# entity-level 다수결 앙상블: test  (20260705_050443)

min_votes=1
data_dir=`/data/team/hwan/data`
evaluated_labels=15: `PS_NAME, LC_ADDRESS, OG_WORKPLACE, OG_DEPARTMENT, CV_POSITION, QT_MOBILE, QT_PHONE, QT_RESIDENT_NUMBER, QT_DRIVER_NUMBER, QT_PLATE_NUMBER, QT_ACCOUNT_NUMBER, QT_CARD_NUMBER, TMI_EMAIL, QT_PASSPORT_NUMBER, DT_BIRTH`
excluded_labels=4: `OGG_EDUCATION, QT_ALIEN_NUMBER, QT_AGE, FD_MAJOR`
excluded_gold_entities=219  excluded_predicted_entities=224

| Entity Micro F1 | **0.9554** |
| Precision | 0.9604 |
| Recall | 0.9504 |
| TP | 1092 | FP | 45 | FN | 57 |

| 레이블 | F1 | P | R | TP | FP | FN |
|--------|-----|---|---|----|----|-----|
| QT_PHONE | 1.0000 | 1.0000 | 1.0000 | 69 | 0 | 0 |
| QT_RESIDENT_NUMBER | 1.0000 | 1.0000 | 1.0000 | 18 | 0 | 0 |
| QT_PLATE_NUMBER | 1.0000 | 1.0000 | 1.0000 | 52 | 0 | 0 |
| QT_CARD_NUMBER | 1.0000 | 1.0000 | 1.0000 | 78 | 0 | 0 |
| TMI_EMAIL | 1.0000 | 1.0000 | 1.0000 | 81 | 0 | 0 |
| QT_PASSPORT_NUMBER | 1.0000 | 1.0000 | 1.0000 | 18 | 0 | 0 |
| OG_DEPARTMENT | 0.9950 | 0.9900 | 1.0000 | 99 | 1 | 0 |
| QT_ACCOUNT_NUMBER | 0.9935 | 0.9872 | 1.0000 | 77 | 1 | 0 |
| DT_BIRTH | 0.9929 | 0.9859 | 1.0000 | 70 | 1 | 0 |
| QT_MOBILE | 0.9908 | 1.0000 | 0.9818 | 54 | 0 | 1 |
| QT_DRIVER_NUMBER | 0.9714 | 0.9444 | 1.0000 | 17 | 1 | 0 |
| PS_NAME | 0.9275 | 0.9524 | 0.9040 | 160 | 8 | 17 |
| LC_ADDRESS | 0.9109 | 0.9109 | 0.9109 | 92 | 9 | 9 |
| CV_POSITION | 0.8871 | 0.8871 | 0.8871 | 110 | 14 | 14 |
| OG_WORKPLACE | 0.8818 | 0.9065 | 0.8584 | 97 | 10 | 16 |