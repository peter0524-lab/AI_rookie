# entity-level 다수결 앙상블: test  (20260705_073117)

min_votes=1
data_dir=`/data/team/hwan/synthetic`
evaluated_labels=19: `PS_NAME, LC_ADDRESS, OG_WORKPLACE, OG_DEPARTMENT, CV_POSITION, OGG_EDUCATION, QT_MOBILE, QT_PHONE, QT_RESIDENT_NUMBER, QT_ALIEN_NUMBER, QT_DRIVER_NUMBER, QT_PLATE_NUMBER, QT_ACCOUNT_NUMBER, QT_CARD_NUMBER, TMI_EMAIL, QT_PASSPORT_NUMBER, QT_AGE, DT_BIRTH, FD_MAJOR`
excluded_labels=0: `-`
excluded_gold_entities=0  excluded_predicted_entities=0

| Entity Micro F1 | **0.8496** |
| Precision | 0.8153 |
| Recall | 0.8869 |
| TP | 1223 | FP | 277 | FN | 156 |

| 레이블 | F1 | P | R | TP | FP | FN |
|--------|-----|---|---|----|----|-----|
| QT_PLATE_NUMBER | 1.0000 | 1.0000 | 1.0000 | 8 | 0 | 0 |
| QT_MOBILE | 0.9960 | 0.9919 | 1.0000 | 123 | 1 | 0 |
| QT_PHONE | 0.9868 | 0.9740 | 1.0000 | 75 | 2 | 0 |
| QT_PASSPORT_NUMBER | 0.9474 | 0.9000 | 1.0000 | 9 | 1 | 0 |
| TMI_EMAIL | 0.9313 | 1.0000 | 0.8714 | 122 | 0 | 18 |
| QT_ACCOUNT_NUMBER | 0.9159 | 0.9800 | 0.8596 | 49 | 1 | 8 |
| QT_CARD_NUMBER | 0.8710 | 0.7714 | 1.0000 | 27 | 8 | 0 |
| PS_NAME | 0.8592 | 0.8397 | 0.8796 | 592 | 113 | 81 |
| LC_ADDRESS | 0.8513 | 0.8557 | 0.8469 | 83 | 14 | 15 |
| OG_WORKPLACE | 0.7193 | 0.6212 | 0.8542 | 41 | 25 | 7 |
| DT_BIRTH | 0.6528 | 0.5949 | 0.7231 | 47 | 32 | 18 |
| QT_RESIDENT_NUMBER | 0.6250 | 0.4545 | 1.0000 | 15 | 18 | 0 |
| OG_DEPARTMENT | 0.6173 | 0.4630 | 0.9259 | 25 | 29 | 2 |
| QT_DRIVER_NUMBER | 0.3750 | 0.2308 | 1.0000 | 3 | 10 | 0 |
| CV_POSITION | 0.2222 | 0.1600 | 0.3636 | 4 | 21 | 7 |
| OGG_EDUCATION | 0.0000 | 0.0000 | 0.0000 | 0 | 0 | 0 |
| QT_ALIEN_NUMBER | 0.0000 | 0.0000 | 0.0000 | 0 | 0 | 0 |
| QT_AGE | 0.0000 | 0.0000 | 0.0000 | 0 | 1 | 0 |
| FD_MAJOR | 0.0000 | 0.0000 | 0.0000 | 0 | 1 | 0 |