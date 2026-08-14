# entity-level 다수결 앙상블: test  (20260704_141006)

min_votes=1
data_dir=`/data/team/hwan/data`
evaluated_labels=15: `PS_NAME, LC_ADDRESS, OG_WORKPLACE, OG_DEPARTMENT, CV_POSITION, QT_MOBILE, QT_PHONE, QT_RESIDENT_NUMBER, QT_DRIVER_NUMBER, QT_PLATE_NUMBER, QT_ACCOUNT_NUMBER, QT_CARD_NUMBER, TMI_EMAIL, QT_PASSPORT_NUMBER, DT_BIRTH`
excluded_labels=4: `OGG_EDUCATION, QT_ALIEN_NUMBER, QT_AGE, FD_MAJOR`
excluded_gold_entities=219  excluded_predicted_entities=9

| Entity Micro F1 | **0.6610** |
| Precision | 0.6418 |
| Recall | 0.6815 |
| TP | 783 | FP | 437 | FN | 366 |

| 레이블 | F1 | P | R | TP | FP | FN |
|--------|-----|---|---|----|----|-----|
| QT_MOBILE | 0.9910 | 0.9821 | 1.0000 | 55 | 1 | 0 |
| QT_PASSPORT_NUMBER | 0.9474 | 0.9000 | 1.0000 | 18 | 2 | 0 |
| QT_CARD_NUMBER | 0.8652 | 0.9683 | 0.7821 | 61 | 2 | 17 |
| TMI_EMAIL | 0.8437 | 0.7297 | 1.0000 | 81 | 30 | 0 |
| DT_BIRTH | 0.8435 | 0.8052 | 0.8857 | 62 | 15 | 8 |
| QT_ACCOUNT_NUMBER | 0.8182 | 0.7273 | 0.9351 | 72 | 27 | 5 |
| QT_PHONE | 0.7746 | 0.6442 | 0.9710 | 67 | 37 | 2 |
| PS_NAME | 0.7232 | 0.5978 | 0.9153 | 162 | 109 | 15 |
| QT_DRIVER_NUMBER | 0.6429 | 0.8182 | 0.5294 | 9 | 2 | 8 |
| QT_RESIDENT_NUMBER | 0.6316 | 0.4615 | 1.0000 | 18 | 21 | 0 |
| CV_POSITION | 0.6207 | 0.7975 | 0.5081 | 63 | 16 | 61 |
| OG_WORKPLACE | 0.5638 | 0.4541 | 0.7434 | 84 | 101 | 29 |
| OG_DEPARTMENT | 0.2694 | 0.2766 | 0.2626 | 26 | 68 | 73 |
| LC_ADDRESS | 0.0741 | 0.5714 | 0.0396 | 4 | 3 | 97 |
| QT_PLATE_NUMBER | 0.0357 | 0.2500 | 0.0192 | 1 | 3 | 51 |