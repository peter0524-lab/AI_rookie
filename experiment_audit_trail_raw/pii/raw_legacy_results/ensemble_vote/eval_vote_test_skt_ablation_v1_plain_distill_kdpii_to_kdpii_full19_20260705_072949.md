# entity-level 다수결 앙상블: test  (20260705_072949)

min_votes=1
data_dir=`/data/team/hwan/data`
evaluated_labels=19: `PS_NAME, LC_ADDRESS, OG_WORKPLACE, OG_DEPARTMENT, CV_POSITION, OGG_EDUCATION, QT_MOBILE, QT_PHONE, QT_RESIDENT_NUMBER, QT_ALIEN_NUMBER, QT_DRIVER_NUMBER, QT_PLATE_NUMBER, QT_ACCOUNT_NUMBER, QT_CARD_NUMBER, TMI_EMAIL, QT_PASSPORT_NUMBER, QT_AGE, DT_BIRTH, FD_MAJOR`
excluded_labels=0: `-`
excluded_gold_entities=0  excluded_predicted_entities=0

| Entity Micro F1 | **0.9283** |
| Precision | 0.9537 |
| Recall | 0.9042 |
| TP | 1237 | FP | 60 | FN | 131 |

| 레이블 | F1 | P | R | TP | FP | FN |
|--------|-----|---|---|----|----|-----|
| QT_MOBILE | 1.0000 | 1.0000 | 1.0000 | 55 | 0 | 0 |
| QT_PHONE | 1.0000 | 1.0000 | 1.0000 | 69 | 0 | 0 |
| QT_RESIDENT_NUMBER | 1.0000 | 1.0000 | 1.0000 | 18 | 0 | 0 |
| QT_ALIEN_NUMBER | 1.0000 | 1.0000 | 1.0000 | 9 | 0 | 0 |
| TMI_EMAIL | 1.0000 | 1.0000 | 1.0000 | 81 | 0 | 0 |
| QT_PASSPORT_NUMBER | 1.0000 | 1.0000 | 1.0000 | 18 | 0 | 0 |
| QT_CARD_NUMBER | 0.9936 | 0.9873 | 1.0000 | 78 | 1 | 0 |
| QT_PLATE_NUMBER | 0.9804 | 1.0000 | 0.9615 | 50 | 0 | 2 |
| DT_BIRTH | 0.9787 | 0.9718 | 0.9857 | 69 | 2 | 1 |
| QT_ACCOUNT_NUMBER | 0.9682 | 0.9500 | 0.9870 | 76 | 4 | 1 |
| OG_DEPARTMENT | 0.9592 | 0.9691 | 0.9495 | 94 | 3 | 5 |
| FD_MAJOR | 0.9524 | 0.9836 | 0.9231 | 60 | 1 | 5 |
| QT_DRIVER_NUMBER | 0.9375 | 1.0000 | 0.8824 | 15 | 0 | 2 |
| OGG_EDUCATION | 0.9364 | 0.9643 | 0.9101 | 81 | 3 | 8 |
| QT_AGE | 0.9273 | 0.9444 | 0.9107 | 51 | 3 | 5 |
| LC_ADDRESS | 0.8980 | 0.9263 | 0.8713 | 88 | 7 | 13 |
| PS_NAME | 0.8696 | 0.8929 | 0.8475 | 150 | 18 | 27 |
| CV_POSITION | 0.8584 | 0.9174 | 0.8065 | 100 | 9 | 24 |
| OG_WORKPLACE | 0.7614 | 0.8929 | 0.6637 | 75 | 9 | 38 |