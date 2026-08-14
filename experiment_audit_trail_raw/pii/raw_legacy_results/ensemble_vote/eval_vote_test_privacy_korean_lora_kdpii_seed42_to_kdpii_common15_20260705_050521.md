# entity-level 다수결 앙상블: test  (20260705_050521)

min_votes=1
data_dir=`/data/team/hwan/data`
evaluated_labels=15: `PS_NAME, LC_ADDRESS, OG_WORKPLACE, OG_DEPARTMENT, CV_POSITION, QT_MOBILE, QT_PHONE, QT_RESIDENT_NUMBER, QT_DRIVER_NUMBER, QT_PLATE_NUMBER, QT_ACCOUNT_NUMBER, QT_CARD_NUMBER, TMI_EMAIL, QT_PASSPORT_NUMBER, DT_BIRTH`
excluded_labels=4: `OGG_EDUCATION, QT_ALIEN_NUMBER, QT_AGE, FD_MAJOR`
excluded_gold_entities=219  excluded_predicted_entities=60

| Entity Micro F1 | **0.6120** |
| Precision | 0.9228 |
| Recall | 0.4578 |
| TP | 526 | FP | 44 | FN | 623 |

| 레이블 | F1 | P | R | TP | FP | FN |
|--------|-----|---|---|----|----|-----|
| QT_MOBILE | 1.0000 | 1.0000 | 1.0000 | 55 | 0 | 0 |
| QT_RESIDENT_NUMBER | 1.0000 | 1.0000 | 1.0000 | 18 | 0 | 0 |
| QT_PHONE | 0.9928 | 0.9857 | 1.0000 | 69 | 1 | 0 |
| DT_BIRTH | 0.9857 | 0.9857 | 0.9857 | 69 | 1 | 1 |
| QT_PLATE_NUMBER | 0.9703 | 1.0000 | 0.9423 | 49 | 0 | 3 |
| QT_CARD_NUMBER | 0.9530 | 1.0000 | 0.9103 | 71 | 0 | 7 |
| QT_ACCOUNT_NUMBER | 0.9014 | 0.9846 | 0.8312 | 64 | 1 | 13 |
| QT_DRIVER_NUMBER | 0.6400 | 1.0000 | 0.4706 | 8 | 0 | 9 |
| TMI_EMAIL | 0.5000 | 1.0000 | 0.3333 | 27 | 0 | 54 |
| PS_NAME | 0.3760 | 0.6438 | 0.2655 | 47 | 26 | 130 |
| CV_POSITION | 0.2895 | 0.7857 | 0.1774 | 22 | 6 | 102 |
| LC_ADDRESS | 0.2373 | 0.8235 | 0.1386 | 14 | 3 | 87 |
| OG_DEPARTMENT | 0.1481 | 0.8889 | 0.0808 | 8 | 1 | 91 |
| QT_PASSPORT_NUMBER | 0.1053 | 1.0000 | 0.0556 | 1 | 0 | 17 |
| OG_WORKPLACE | 0.0656 | 0.4444 | 0.0354 | 4 | 5 | 109 |