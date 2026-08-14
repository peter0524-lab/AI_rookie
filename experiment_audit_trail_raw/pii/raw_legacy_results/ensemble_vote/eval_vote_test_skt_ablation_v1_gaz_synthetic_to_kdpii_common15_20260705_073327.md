# entity-level 다수결 앙상블: test  (20260705_073327)

min_votes=1
data_dir=`/data/team/hwan/data`
evaluated_labels=15: `PS_NAME, LC_ADDRESS, OG_WORKPLACE, OG_DEPARTMENT, CV_POSITION, QT_MOBILE, QT_PHONE, QT_RESIDENT_NUMBER, QT_DRIVER_NUMBER, QT_PLATE_NUMBER, QT_ACCOUNT_NUMBER, QT_CARD_NUMBER, TMI_EMAIL, QT_PASSPORT_NUMBER, DT_BIRTH`
excluded_labels=4: `OGG_EDUCATION, QT_ALIEN_NUMBER, QT_AGE, FD_MAJOR`
excluded_gold_entities=219  excluded_predicted_entities=9

| Entity Micro F1 | **0.6335** |
| Precision | 0.7285 |
| Recall | 0.5605 |
| TP | 644 | FP | 240 | FN | 505 |

| 레이블 | F1 | P | R | TP | FP | FN |
|--------|-----|---|---|----|----|-----|
| QT_MOBILE | 1.0000 | 1.0000 | 1.0000 | 55 | 0 | 0 |
| QT_RESIDENT_NUMBER | 1.0000 | 1.0000 | 1.0000 | 18 | 0 | 0 |
| QT_PASSPORT_NUMBER | 1.0000 | 1.0000 | 1.0000 | 18 | 0 | 0 |
| QT_PHONE | 0.9784 | 0.9714 | 0.9855 | 68 | 2 | 1 |
| TMI_EMAIL | 0.8852 | 0.7941 | 1.0000 | 81 | 21 | 0 |
| QT_CARD_NUMBER | 0.7846 | 0.9808 | 0.6538 | 51 | 1 | 27 |
| QT_ACCOUNT_NUMBER | 0.7831 | 0.6607 | 0.9610 | 74 | 38 | 3 |
| PS_NAME | 0.7293 | 0.7135 | 0.7458 | 132 | 53 | 45 |
| QT_DRIVER_NUMBER | 0.6400 | 1.0000 | 0.4706 | 8 | 0 | 9 |
| DT_BIRTH | 0.5208 | 0.9615 | 0.3571 | 25 | 1 | 45 |
| OG_WORKPLACE | 0.4286 | 0.3593 | 0.5310 | 60 | 107 | 53 |
| CV_POSITION | 0.3949 | 0.9394 | 0.2500 | 31 | 2 | 93 |
| OG_DEPARTMENT | 0.2712 | 0.8421 | 0.1616 | 16 | 3 | 83 |
| LC_ADDRESS | 0.0926 | 0.7143 | 0.0495 | 5 | 2 | 96 |
| QT_PLATE_NUMBER | 0.0625 | 0.1667 | 0.0385 | 2 | 10 | 50 |