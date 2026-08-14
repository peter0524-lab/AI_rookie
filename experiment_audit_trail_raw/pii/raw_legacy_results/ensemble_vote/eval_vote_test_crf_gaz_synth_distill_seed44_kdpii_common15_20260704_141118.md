# entity-level 다수결 앙상블: test  (20260704_141118)

min_votes=1
data_dir=`/data/team/hwan/data`
evaluated_labels=15: `PS_NAME, LC_ADDRESS, OG_WORKPLACE, OG_DEPARTMENT, CV_POSITION, QT_MOBILE, QT_PHONE, QT_RESIDENT_NUMBER, QT_DRIVER_NUMBER, QT_PLATE_NUMBER, QT_ACCOUNT_NUMBER, QT_CARD_NUMBER, TMI_EMAIL, QT_PASSPORT_NUMBER, DT_BIRTH`
excluded_labels=4: `OGG_EDUCATION, QT_ALIEN_NUMBER, QT_AGE, FD_MAJOR`
excluded_gold_entities=219  excluded_predicted_entities=9

| Entity Micro F1 | **0.6647** |
| Precision | 0.7443 |
| Recall | 0.6005 |
| TP | 690 | FP | 237 | FN | 459 |

| 레이블 | F1 | P | R | TP | FP | FN |
|--------|-----|---|---|----|----|-----|
| QT_MOBILE | 1.0000 | 1.0000 | 1.0000 | 55 | 0 | 0 |
| QT_PASSPORT_NUMBER | 1.0000 | 1.0000 | 1.0000 | 18 | 0 | 0 |
| QT_PHONE | 0.9718 | 0.9452 | 1.0000 | 69 | 4 | 0 |
| QT_DRIVER_NUMBER | 0.9697 | 1.0000 | 0.9412 | 16 | 0 | 1 |
| QT_RESIDENT_NUMBER | 0.9000 | 0.8182 | 1.0000 | 18 | 4 | 0 |
| TMI_EMAIL | 0.8394 | 0.7232 | 1.0000 | 81 | 31 | 0 |
| QT_ACCOUNT_NUMBER | 0.8229 | 0.7347 | 0.9351 | 72 | 26 | 5 |
| QT_CARD_NUMBER | 0.7907 | 1.0000 | 0.6538 | 51 | 0 | 27 |
| PS_NAME | 0.7189 | 0.6070 | 0.8814 | 156 | 101 | 21 |
| OG_WORKPLACE | 0.5299 | 0.5124 | 0.5487 | 62 | 59 | 51 |
| CV_POSITION | 0.4578 | 0.9048 | 0.3065 | 38 | 4 | 86 |
| LC_ADDRESS | 0.3443 | 1.0000 | 0.2079 | 21 | 0 | 80 |
| OG_DEPARTMENT | 0.2951 | 0.7826 | 0.1818 | 18 | 5 | 81 |
| DT_BIRTH | 0.2469 | 0.9091 | 0.1429 | 10 | 1 | 60 |
| QT_PLATE_NUMBER | 0.1695 | 0.7143 | 0.0962 | 5 | 2 | 47 |