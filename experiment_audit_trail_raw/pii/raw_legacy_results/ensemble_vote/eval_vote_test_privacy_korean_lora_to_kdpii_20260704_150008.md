# entity-level 다수결 앙상블: test  (20260704_150008)

min_votes=1
data_dir=`/data/team/hwan/data`
evaluated_labels=19: `PS_NAME, LC_ADDRESS, OG_WORKPLACE, OG_DEPARTMENT, CV_POSITION, OGG_EDUCATION, QT_MOBILE, QT_PHONE, QT_RESIDENT_NUMBER, QT_ALIEN_NUMBER, QT_DRIVER_NUMBER, QT_PLATE_NUMBER, QT_ACCOUNT_NUMBER, QT_CARD_NUMBER, TMI_EMAIL, QT_PASSPORT_NUMBER, QT_AGE, DT_BIRTH, FD_MAJOR`
excluded_labels=0: `-`
excluded_gold_entities=0  excluded_predicted_entities=0

| Entity Micro F1 | **0.5756** |
| Precision | 0.9127 |
| Recall | 0.4203 |
| TP | 575 | FP | 55 | FN | 793 |

| 레이블 | F1 | P | R | TP | FP | FN |
|--------|-----|---|---|----|----|-----|
| QT_MOBILE | 1.0000 | 1.0000 | 1.0000 | 55 | 0 | 0 |
| QT_RESIDENT_NUMBER | 1.0000 | 1.0000 | 1.0000 | 18 | 0 | 0 |
| QT_ALIEN_NUMBER | 1.0000 | 1.0000 | 1.0000 | 9 | 0 | 0 |
| QT_PHONE | 0.9928 | 0.9857 | 1.0000 | 69 | 1 | 0 |
| DT_BIRTH | 0.9857 | 0.9857 | 0.9857 | 69 | 1 | 1 |
| QT_PLATE_NUMBER | 0.9703 | 1.0000 | 0.9423 | 49 | 0 | 3 |
| QT_CARD_NUMBER | 0.9530 | 1.0000 | 0.9103 | 71 | 0 | 7 |
| QT_ACCOUNT_NUMBER | 0.9014 | 0.9846 | 0.8312 | 64 | 1 | 13 |
| QT_AGE | 0.6957 | 0.8889 | 0.5714 | 32 | 4 | 24 |
| QT_DRIVER_NUMBER | 0.6400 | 1.0000 | 0.4706 | 8 | 0 | 9 |
| TMI_EMAIL | 0.5000 | 1.0000 | 0.3333 | 27 | 0 | 54 |
| PS_NAME | 0.3760 | 0.6438 | 0.2655 | 47 | 26 | 130 |
| CV_POSITION | 0.2895 | 0.7857 | 0.1774 | 22 | 6 | 102 |
| LC_ADDRESS | 0.2373 | 0.8235 | 0.1386 | 14 | 3 | 87 |
| OG_DEPARTMENT | 0.1481 | 0.8889 | 0.0808 | 8 | 1 | 91 |
| QT_PASSPORT_NUMBER | 0.1053 | 1.0000 | 0.0556 | 1 | 0 | 17 |
| OGG_EDUCATION | 0.1000 | 0.4545 | 0.0562 | 5 | 6 | 84 |
| FD_MAJOR | 0.0870 | 0.7500 | 0.0462 | 3 | 1 | 62 |
| OG_WORKPLACE | 0.0656 | 0.4444 | 0.0354 | 4 | 5 | 109 |