# entity-level 다수결 앙상블: test  (20260717_074440)

min_votes=1
data_dir=`/data/team/hwan/real/data/test_sets/kdpii`
evaluated_labels=18: `PS_NAME, LC_ADDRESS, OG_WORKPLACE, OG_DEPARTMENT, CV_POSITION, OGG_EDUCATION, QT_MOBILE, QT_PHONE, QT_RESIDENT_NUMBER, QT_DRIVER_NUMBER, QT_PLATE_NUMBER, QT_ACCOUNT_NUMBER, QT_CARD_NUMBER, TMI_EMAIL, QT_PASSPORT_NUMBER, QT_AGE, DT_BIRTH, FD_MAJOR`
excluded_labels=1: `QT_ALIEN_NUMBER`
excluded_gold_entities=9  excluded_predicted_entities=9

| Entity Micro F1 | **0.6367** |
| Precision | 0.7071 |
| Recall | 0.5791 |
| TP | 787 | FP | 326 | FN | 572 |

| 레이블 | F1 | P | R | TP | FP | FN |
|--------|-----|---|---|----|----|-----|
| QT_MOBILE | 1.0000 | 1.0000 | 1.0000 | 55 | 0 | 0 |
| QT_RESIDENT_NUMBER | 1.0000 | 1.0000 | 1.0000 | 18 | 0 | 0 |
| QT_PASSPORT_NUMBER | 1.0000 | 1.0000 | 1.0000 | 18 | 0 | 0 |
| QT_PHONE | 0.9371 | 0.9054 | 0.9710 | 67 | 7 | 2 |
| QT_DRIVER_NUMBER | 0.8485 | 0.8750 | 0.8235 | 14 | 2 | 3 |
| QT_ACCOUNT_NUMBER | 0.8108 | 0.6944 | 0.9740 | 75 | 33 | 2 |
| QT_CARD_NUMBER | 0.7907 | 1.0000 | 0.6538 | 51 | 0 | 27 |
| TMI_EMAIL | 0.7826 | 0.6429 | 1.0000 | 81 | 45 | 0 |
| PS_NAME | 0.7619 | 0.6847 | 0.8588 | 152 | 70 | 25 |
| DT_BIRTH | 0.7250 | 0.6444 | 0.8286 | 58 | 32 | 12 |
| OGG_EDUCATION | 0.6861 | 0.9792 | 0.5281 | 47 | 1 | 42 |
| OG_WORKPLACE | 0.5600 | 0.5109 | 0.6195 | 70 | 67 | 43 |
| OG_DEPARTMENT | 0.4308 | 0.9032 | 0.2828 | 28 | 3 | 71 |
| CV_POSITION | 0.3221 | 0.9600 | 0.1935 | 24 | 1 | 100 |
| QT_AGE | 0.2295 | 0.2121 | 0.2500 | 14 | 52 | 42 |
| LC_ADDRESS | 0.1951 | 0.5455 | 0.1188 | 12 | 10 | 89 |
| FD_MAJOR | 0.0588 | 0.6667 | 0.0308 | 2 | 1 | 63 |
| QT_PLATE_NUMBER | 0.0364 | 0.3333 | 0.0192 | 1 | 2 | 51 |