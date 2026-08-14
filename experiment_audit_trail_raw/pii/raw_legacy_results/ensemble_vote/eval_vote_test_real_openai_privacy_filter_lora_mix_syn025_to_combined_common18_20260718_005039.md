# entity-level 다수결 앙상블: test  (20260718_005039)

min_votes=1
data_dir=`/data/team/hwan/real/data/test_sets/combined`
evaluated_labels=18: `PS_NAME, LC_ADDRESS, OG_WORKPLACE, OG_DEPARTMENT, CV_POSITION, OGG_EDUCATION, QT_MOBILE, QT_PHONE, QT_RESIDENT_NUMBER, QT_DRIVER_NUMBER, QT_PLATE_NUMBER, QT_ACCOUNT_NUMBER, QT_CARD_NUMBER, TMI_EMAIL, QT_PASSPORT_NUMBER, QT_AGE, DT_BIRTH, FD_MAJOR`
excluded_labels=1: `QT_ALIEN_NUMBER`
excluded_gold_entities=9  excluded_predicted_entities=9

| Entity Micro F1 | **0.5760** |
| Precision | 0.9636 |
| Recall | 0.4107 |
| TP | 3230 | FP | 122 | FN | 4634 |

| 레이블 | F1 | P | R | TP | FP | FN |
|--------|-----|---|---|----|----|-----|
| QT_MOBILE | 1.0000 | 1.0000 | 1.0000 | 432 | 0 | 0 |
| QT_RESIDENT_NUMBER | 1.0000 | 1.0000 | 1.0000 | 203 | 0 | 0 |
| QT_PHONE | 0.9980 | 0.9961 | 1.0000 | 255 | 1 | 0 |
| QT_CARD_NUMBER | 0.9791 | 1.0000 | 0.9591 | 164 | 0 | 7 |
| DT_BIRTH | 0.9759 | 0.9806 | 0.9712 | 304 | 6 | 9 |
| QT_PLATE_NUMBER | 0.9677 | 1.0000 | 0.9375 | 60 | 0 | 4 |
| QT_ACCOUNT_NUMBER | 0.9619 | 1.0000 | 0.9266 | 240 | 0 | 19 |
| QT_AGE | 0.8328 | 0.8742 | 0.7952 | 132 | 19 | 34 |
| QT_DRIVER_NUMBER | 0.8000 | 1.0000 | 0.6667 | 16 | 0 | 8 |
| PS_NAME | 0.5316 | 0.9743 | 0.3655 | 1287 | 34 | 2234 |
| OGG_EDUCATION | 0.2079 | 0.7255 | 0.1213 | 37 | 14 | 268 |
| TMI_EMAIL | 0.1772 | 1.0000 | 0.0972 | 35 | 0 | 325 |
| CV_POSITION | 0.1631 | 0.7931 | 0.0909 | 23 | 6 | 230 |
| QT_PASSPORT_NUMBER | 0.0952 | 1.0000 | 0.0500 | 1 | 0 | 19 |
| OG_DEPARTMENT | 0.0800 | 0.7222 | 0.0423 | 13 | 5 | 294 |
| LC_ADDRESS | 0.0796 | 0.7619 | 0.0420 | 16 | 5 | 365 |
| FD_MAJOR | 0.0609 | 0.4286 | 0.0328 | 6 | 8 | 177 |
| OG_WORKPLACE | 0.0177 | 0.2000 | 0.0093 | 6 | 24 | 641 |