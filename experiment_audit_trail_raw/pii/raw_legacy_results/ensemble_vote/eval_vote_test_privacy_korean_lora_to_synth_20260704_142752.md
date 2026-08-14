# entity-level 다수결 앙상블: test  (20260704_142752)

min_votes=1
data_dir=`/data/team/hwan/synthetic`
evaluated_labels=19: `PS_NAME, LC_ADDRESS, OG_WORKPLACE, OG_DEPARTMENT, CV_POSITION, OGG_EDUCATION, QT_MOBILE, QT_PHONE, QT_RESIDENT_NUMBER, QT_ALIEN_NUMBER, QT_DRIVER_NUMBER, QT_PLATE_NUMBER, QT_ACCOUNT_NUMBER, QT_CARD_NUMBER, TMI_EMAIL, QT_PASSPORT_NUMBER, QT_AGE, DT_BIRTH, FD_MAJOR`
excluded_labels=0: `-`
excluded_gold_entities=0  excluded_predicted_entities=0

| Entity Micro F1 | **0.4013** |
| Precision | 0.7596 |
| Recall | 0.2727 |
| TP | 376 | FP | 119 | FN | 1003 |

| 레이블 | F1 | P | R | TP | FP | FN |
|--------|-----|---|---|----|----|-----|
| QT_MOBILE | 1.0000 | 1.0000 | 1.0000 | 123 | 0 | 0 |
| QT_DRIVER_NUMBER | 1.0000 | 1.0000 | 1.0000 | 3 | 0 | 0 |
| QT_PHONE | 0.9868 | 0.9740 | 1.0000 | 75 | 2 | 0 |
| QT_RESIDENT_NUMBER | 0.9677 | 0.9375 | 1.0000 | 15 | 1 | 0 |
| QT_CARD_NUMBER | 0.9310 | 0.8710 | 1.0000 | 27 | 4 | 0 |
| QT_ACCOUNT_NUMBER | 0.8485 | 1.0000 | 0.7368 | 42 | 0 | 15 |
| QT_PLATE_NUMBER | 0.8421 | 0.7273 | 1.0000 | 8 | 3 | 0 |
| DT_BIRTH | 0.4851 | 0.3577 | 0.7538 | 49 | 88 | 16 |
| PS_NAME | 0.0907 | 0.9697 | 0.0475 | 32 | 1 | 641 |
| OG_WORKPLACE | 0.0370 | 0.1667 | 0.0208 | 1 | 5 | 47 |
| LC_ADDRESS | 0.0200 | 0.5000 | 0.0102 | 1 | 1 | 97 |
| OG_DEPARTMENT | 0.0000 | 0.0000 | 0.0000 | 0 | 1 | 27 |
| CV_POSITION | 0.0000 | 0.0000 | 0.0000 | 0 | 0 | 11 |
| OGG_EDUCATION | 0.0000 | 0.0000 | 0.0000 | 0 | 6 | 0 |
| QT_ALIEN_NUMBER | 0.0000 | 0.0000 | 0.0000 | 0 | 2 | 0 |
| TMI_EMAIL | 0.0000 | 0.0000 | 0.0000 | 0 | 0 | 140 |
| QT_PASSPORT_NUMBER | 0.0000 | 0.0000 | 0.0000 | 0 | 1 | 9 |
| QT_AGE | 0.0000 | 0.0000 | 0.0000 | 0 | 3 | 0 |
| FD_MAJOR | 0.0000 | 0.0000 | 0.0000 | 0 | 1 | 0 |