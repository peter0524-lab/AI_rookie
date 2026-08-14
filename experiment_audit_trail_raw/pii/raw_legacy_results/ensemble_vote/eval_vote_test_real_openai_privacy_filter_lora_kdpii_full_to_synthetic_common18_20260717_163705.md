# entity-level 다수결 앙상블: test  (20260717_163705)

min_votes=1
data_dir=`/data/team/hwan/real/data/test_sets/synthetic`
evaluated_labels=18: `PS_NAME, LC_ADDRESS, OG_WORKPLACE, OG_DEPARTMENT, CV_POSITION, OGG_EDUCATION, QT_MOBILE, QT_PHONE, QT_RESIDENT_NUMBER, QT_DRIVER_NUMBER, QT_PLATE_NUMBER, QT_ACCOUNT_NUMBER, QT_CARD_NUMBER, TMI_EMAIL, QT_PASSPORT_NUMBER, QT_AGE, DT_BIRTH, FD_MAJOR`
excluded_labels=1: `QT_ALIEN_NUMBER`
excluded_gold_entities=0  excluded_predicted_entities=8

| Entity Micro F1 | **0.4366** |
| Precision | 0.8433 |
| Recall | 0.2945 |
| TP | 1916 | FP | 356 | FN | 4589 |

| 레이블 | F1 | P | R | TP | FP | FN |
|--------|-----|---|---|----|----|-----|
| QT_MOBILE | 0.9987 | 0.9974 | 1.0000 | 377 | 1 | 0 |
| QT_RESIDENT_NUMBER | 0.9920 | 0.9840 | 1.0000 | 185 | 3 | 0 |
| QT_PHONE | 0.9738 | 0.9490 | 1.0000 | 186 | 10 | 0 |
| QT_CARD_NUMBER | 0.9490 | 0.9029 | 1.0000 | 93 | 10 | 0 |
| QT_ACCOUNT_NUMBER | 0.8909 | 0.9618 | 0.8297 | 151 | 6 | 31 |
| QT_DRIVER_NUMBER | 0.7000 | 0.5385 | 1.0000 | 7 | 6 | 0 |
| DT_BIRTH | 0.6732 | 0.5583 | 0.8477 | 206 | 163 | 37 |
| QT_PLATE_NUMBER | 0.6486 | 0.4800 | 1.0000 | 12 | 13 | 0 |
| QT_AGE | 0.5714 | 0.7222 | 0.4727 | 52 | 20 | 58 |
| PS_NAME | 0.3037 | 0.9788 | 0.1797 | 601 | 13 | 2743 |
| OGG_EDUCATION | 0.1701 | 0.3205 | 0.1157 | 25 | 53 | 191 |
| TMI_EMAIL | 0.0625 | 1.0000 | 0.0323 | 9 | 0 | 270 |
| LC_ADDRESS | 0.0614 | 0.6923 | 0.0321 | 9 | 4 | 271 |
| OG_DEPARTMENT | 0.0183 | 0.2000 | 0.0096 | 2 | 8 | 206 |
| OG_WORKPLACE | 0.0035 | 0.0323 | 0.0019 | 1 | 30 | 533 |
| CV_POSITION | 0.0000 | 0.0000 | 0.0000 | 0 | 1 | 129 |
| QT_PASSPORT_NUMBER | 0.0000 | 0.0000 | 0.0000 | 0 | 1 | 2 |
| FD_MAJOR | 0.0000 | 0.0000 | 0.0000 | 0 | 14 | 118 |