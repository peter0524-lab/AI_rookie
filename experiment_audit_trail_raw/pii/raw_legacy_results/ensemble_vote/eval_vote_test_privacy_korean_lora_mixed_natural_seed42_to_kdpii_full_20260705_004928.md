# entity-level 다수결 앙상블: test  (20260705_004928)

min_votes=1
data_dir=`/data/team/hwan/data`
evaluated_labels=19: `PS_NAME, LC_ADDRESS, OG_WORKPLACE, OG_DEPARTMENT, CV_POSITION, OGG_EDUCATION, QT_MOBILE, QT_PHONE, QT_RESIDENT_NUMBER, QT_ALIEN_NUMBER, QT_DRIVER_NUMBER, QT_PLATE_NUMBER, QT_ACCOUNT_NUMBER, QT_CARD_NUMBER, TMI_EMAIL, QT_PASSPORT_NUMBER, QT_AGE, DT_BIRTH, FD_MAJOR`
excluded_labels=0: `-`
excluded_gold_entities=0  excluded_predicted_entities=0

| Entity Micro F1 | **0.5700** |
| Precision | 0.9305 |
| Recall | 0.4108 |
| TP | 562 | FP | 42 | FN | 806 |

| 레이블 | F1 | P | R | TP | FP | FN |
|--------|-----|---|---|----|----|-----|
| QT_MOBILE | 1.0000 | 1.0000 | 1.0000 | 55 | 0 | 0 |
| QT_PHONE | 1.0000 | 1.0000 | 1.0000 | 69 | 0 | 0 |
| QT_RESIDENT_NUMBER | 1.0000 | 1.0000 | 1.0000 | 18 | 0 | 0 |
| QT_ALIEN_NUMBER | 1.0000 | 1.0000 | 1.0000 | 9 | 0 | 0 |
| DT_BIRTH | 0.9857 | 0.9857 | 0.9857 | 69 | 1 | 1 |
| QT_PLATE_NUMBER | 0.9600 | 1.0000 | 0.9231 | 48 | 0 | 4 |
| QT_CARD_NUMBER | 0.9388 | 1.0000 | 0.8846 | 69 | 0 | 9 |
| QT_ACCOUNT_NUMBER | 0.9000 | 1.0000 | 0.8182 | 63 | 0 | 14 |
| QT_DRIVER_NUMBER | 0.6923 | 1.0000 | 0.5294 | 9 | 0 | 8 |
| QT_AGE | 0.6889 | 0.9118 | 0.5536 | 31 | 3 | 25 |
| TMI_EMAIL | 0.5000 | 1.0000 | 0.3333 | 27 | 0 | 54 |
| PS_NAME | 0.3583 | 0.6825 | 0.2429 | 43 | 20 | 134 |
| CV_POSITION | 0.3067 | 0.8846 | 0.1855 | 23 | 3 | 101 |
| LC_ADDRESS | 0.2281 | 1.0000 | 0.1287 | 13 | 0 | 88 |
| OG_DEPARTMENT | 0.1308 | 0.8750 | 0.0707 | 7 | 1 | 92 |
| QT_PASSPORT_NUMBER | 0.1053 | 1.0000 | 0.0556 | 1 | 0 | 17 |
| FD_MAJOR | 0.0857 | 0.6000 | 0.0462 | 3 | 2 | 62 |
| OGG_EDUCATION | 0.0808 | 0.4000 | 0.0449 | 4 | 6 | 85 |
| OG_WORKPLACE | 0.0167 | 0.1429 | 0.0088 | 1 | 6 | 112 |