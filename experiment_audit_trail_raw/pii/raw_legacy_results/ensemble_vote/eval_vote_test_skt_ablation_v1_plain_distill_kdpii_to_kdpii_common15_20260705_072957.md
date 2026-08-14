# entity-level 다수결 앙상블: test  (20260705_072957)

min_votes=1
data_dir=`/data/team/hwan/data`
evaluated_labels=15: `PS_NAME, LC_ADDRESS, OG_WORKPLACE, OG_DEPARTMENT, CV_POSITION, QT_MOBILE, QT_PHONE, QT_RESIDENT_NUMBER, QT_DRIVER_NUMBER, QT_PLATE_NUMBER, QT_ACCOUNT_NUMBER, QT_CARD_NUMBER, TMI_EMAIL, QT_PASSPORT_NUMBER, DT_BIRTH`
excluded_labels=4: `OGG_EDUCATION, QT_ALIEN_NUMBER, QT_AGE, FD_MAJOR`
excluded_gold_entities=219  excluded_predicted_entities=212

| Entity Micro F1 | **0.9258** |
| Precision | 0.9513 |
| Recall | 0.9017 |
| TP | 1036 | FP | 53 | FN | 113 |

| 레이블 | F1 | P | R | TP | FP | FN |
|--------|-----|---|---|----|----|-----|
| QT_MOBILE | 1.0000 | 1.0000 | 1.0000 | 55 | 0 | 0 |
| QT_PHONE | 1.0000 | 1.0000 | 1.0000 | 69 | 0 | 0 |
| QT_RESIDENT_NUMBER | 1.0000 | 1.0000 | 1.0000 | 18 | 0 | 0 |
| TMI_EMAIL | 1.0000 | 1.0000 | 1.0000 | 81 | 0 | 0 |
| QT_PASSPORT_NUMBER | 1.0000 | 1.0000 | 1.0000 | 18 | 0 | 0 |
| QT_CARD_NUMBER | 0.9936 | 0.9873 | 1.0000 | 78 | 1 | 0 |
| QT_PLATE_NUMBER | 0.9804 | 1.0000 | 0.9615 | 50 | 0 | 2 |
| DT_BIRTH | 0.9787 | 0.9718 | 0.9857 | 69 | 2 | 1 |
| QT_ACCOUNT_NUMBER | 0.9682 | 0.9500 | 0.9870 | 76 | 4 | 1 |
| OG_DEPARTMENT | 0.9592 | 0.9691 | 0.9495 | 94 | 3 | 5 |
| QT_DRIVER_NUMBER | 0.9375 | 1.0000 | 0.8824 | 15 | 0 | 2 |
| LC_ADDRESS | 0.8980 | 0.9263 | 0.8713 | 88 | 7 | 13 |
| PS_NAME | 0.8696 | 0.8929 | 0.8475 | 150 | 18 | 27 |
| CV_POSITION | 0.8584 | 0.9174 | 0.8065 | 100 | 9 | 24 |
| OG_WORKPLACE | 0.7614 | 0.8929 | 0.6637 | 75 | 9 | 38 |