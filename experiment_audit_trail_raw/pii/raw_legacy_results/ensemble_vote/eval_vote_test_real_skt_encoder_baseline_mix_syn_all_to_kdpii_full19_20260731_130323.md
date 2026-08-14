# entity-level 다수결 앙상블: test  (20260731_130323)

min_votes=1
data_dir=`/data/team/hwan/real/data/test_sets/kdpii`
evaluated_labels=19: `PS_NAME, LC_ADDRESS, OG_WORKPLACE, OG_DEPARTMENT, CV_POSITION, OGG_EDUCATION, QT_MOBILE, QT_PHONE, QT_RESIDENT_NUMBER, QT_ALIEN_NUMBER, QT_DRIVER_NUMBER, QT_PLATE_NUMBER, QT_ACCOUNT_NUMBER, QT_CARD_NUMBER, TMI_EMAIL, QT_PASSPORT_NUMBER, QT_AGE, DT_BIRTH, FD_MAJOR`
excluded_labels=0: `-`
excluded_gold_entities=0  excluded_predicted_entities=0

| Entity Micro F1 | **0.9231** |
| Precision | 0.9428 |
| Recall | 0.9042 |
| TP | 1237 | FP | 75 | FN | 131 |

| 레이블 | F1 | P | R | TP | FP | FN |
|--------|-----|---|---|----|----|-----|
| QT_MOBILE | 1.0000 | 1.0000 | 1.0000 | 55 | 0 | 0 |
| QT_PHONE | 1.0000 | 1.0000 | 1.0000 | 69 | 0 | 0 |
| QT_RESIDENT_NUMBER | 1.0000 | 1.0000 | 1.0000 | 18 | 0 | 0 |
| QT_ALIEN_NUMBER | 1.0000 | 1.0000 | 1.0000 | 9 | 0 | 0 |
| QT_DRIVER_NUMBER | 1.0000 | 1.0000 | 1.0000 | 17 | 0 | 0 |
| TMI_EMAIL | 1.0000 | 1.0000 | 1.0000 | 81 | 0 | 0 |
| QT_PASSPORT_NUMBER | 1.0000 | 1.0000 | 1.0000 | 18 | 0 | 0 |
| QT_CARD_NUMBER | 0.9936 | 0.9873 | 1.0000 | 78 | 1 | 0 |
| DT_BIRTH | 0.9857 | 0.9857 | 0.9857 | 69 | 1 | 1 |
| QT_ACCOUNT_NUMBER | 0.9744 | 0.9620 | 0.9870 | 76 | 3 | 1 |
| QT_PLATE_NUMBER | 0.9608 | 0.9800 | 0.9423 | 49 | 1 | 3 |
| OGG_EDUCATION | 0.9425 | 0.9647 | 0.9213 | 82 | 3 | 7 |
| FD_MAJOR | 0.9355 | 0.9831 | 0.8923 | 58 | 1 | 7 |
| OG_DEPARTMENT | 0.9263 | 0.9670 | 0.8889 | 88 | 3 | 11 |
| QT_AGE | 0.9204 | 0.9123 | 0.9286 | 52 | 5 | 4 |
| PS_NAME | 0.8750 | 0.8800 | 0.8701 | 154 | 21 | 23 |
| LC_ADDRESS | 0.8673 | 0.8947 | 0.8416 | 85 | 10 | 16 |
| CV_POSITION | 0.8560 | 0.8739 | 0.8387 | 104 | 15 | 20 |
| OG_WORKPLACE | 0.7538 | 0.8721 | 0.6637 | 75 | 11 | 38 |