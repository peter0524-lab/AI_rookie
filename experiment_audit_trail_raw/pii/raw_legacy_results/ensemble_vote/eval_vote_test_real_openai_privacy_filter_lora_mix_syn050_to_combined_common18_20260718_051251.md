# entity-level 다수결 앙상블: test  (20260718_051251)

min_votes=1
data_dir=`/data/team/hwan/real/data/test_sets/combined`
evaluated_labels=18: `PS_NAME, LC_ADDRESS, OG_WORKPLACE, OG_DEPARTMENT, CV_POSITION, OGG_EDUCATION, QT_MOBILE, QT_PHONE, QT_RESIDENT_NUMBER, QT_DRIVER_NUMBER, QT_PLATE_NUMBER, QT_ACCOUNT_NUMBER, QT_CARD_NUMBER, TMI_EMAIL, QT_PASSPORT_NUMBER, QT_AGE, DT_BIRTH, FD_MAJOR`
excluded_labels=1: `QT_ALIEN_NUMBER`
excluded_gold_entities=9  excluded_predicted_entities=10

| Entity Micro F1 | **0.5786** |
| Precision | 0.9681 |
| Recall | 0.4126 |
| TP | 3245 | FP | 107 | FN | 4619 |

| 레이블 | F1 | P | R | TP | FP | FN |
|--------|-----|---|---|----|----|-----|
| QT_MOBILE | 1.0000 | 1.0000 | 1.0000 | 432 | 0 | 0 |
| QT_RESIDENT_NUMBER | 1.0000 | 1.0000 | 1.0000 | 203 | 0 | 0 |
| QT_PHONE | 0.9980 | 0.9961 | 1.0000 | 255 | 1 | 0 |
| QT_CARD_NUMBER | 0.9791 | 1.0000 | 0.9591 | 164 | 0 | 7 |
| QT_PLATE_NUMBER | 0.9760 | 1.0000 | 0.9531 | 61 | 0 | 3 |
| DT_BIRTH | 0.9744 | 0.9775 | 0.9712 | 304 | 7 | 9 |
| QT_ACCOUNT_NUMBER | 0.9619 | 1.0000 | 0.9266 | 240 | 0 | 19 |
| QT_AGE | 0.8051 | 0.8571 | 0.7590 | 126 | 21 | 40 |
| QT_DRIVER_NUMBER | 0.7692 | 1.0000 | 0.6250 | 15 | 0 | 9 |
| PS_NAME | 0.5403 | 0.9705 | 0.3743 | 1318 | 40 | 2203 |
| OGG_EDUCATION | 0.1871 | 0.8649 | 0.1049 | 32 | 5 | 273 |
| TMI_EMAIL | 0.1772 | 1.0000 | 0.0972 | 35 | 0 | 325 |
| CV_POSITION | 0.1500 | 0.7778 | 0.0830 | 21 | 6 | 232 |
| QT_PASSPORT_NUMBER | 0.0952 | 1.0000 | 0.0500 | 1 | 0 | 19 |
| OG_DEPARTMENT | 0.0800 | 0.7222 | 0.0423 | 13 | 5 | 294 |
| FD_MAJOR | 0.0722 | 0.6364 | 0.0383 | 7 | 4 | 176 |
| LC_ADDRESS | 0.0608 | 0.8571 | 0.0315 | 12 | 2 | 369 |
| OG_WORKPLACE | 0.0179 | 0.2727 | 0.0093 | 6 | 16 | 641 |