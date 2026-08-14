# entity-level 다수결 앙상블: test  (20260717_163216)

min_votes=1
data_dir=`/data/team/hwan/real/data/test_sets/combined`
evaluated_labels=19: `PS_NAME, LC_ADDRESS, OG_WORKPLACE, OG_DEPARTMENT, CV_POSITION, OGG_EDUCATION, QT_MOBILE, QT_PHONE, QT_RESIDENT_NUMBER, QT_ALIEN_NUMBER, QT_DRIVER_NUMBER, QT_PLATE_NUMBER, QT_ACCOUNT_NUMBER, QT_CARD_NUMBER, TMI_EMAIL, QT_PASSPORT_NUMBER, QT_AGE, DT_BIRTH, FD_MAJOR`
excluded_labels=0: `-`
excluded_gold_entities=0  excluded_predicted_entities=0

| Entity Micro F1 | **0.9046** |
| Precision | 0.8929 |
| Recall | 0.9167 |
| TP | 7217 | FP | 866 | FN | 656 |

| 레이블 | F1 | P | R | TP | FP | FN |
|--------|-----|---|---|----|----|-----|
| QT_ALIEN_NUMBER | 1.0000 | 1.0000 | 1.0000 | 9 | 0 | 0 |
| QT_PLATE_NUMBER | 1.0000 | 1.0000 | 1.0000 | 64 | 0 | 0 |
| QT_MOBILE | 0.9931 | 0.9885 | 0.9977 | 431 | 5 | 1 |
| QT_CARD_NUMBER | 0.9913 | 0.9828 | 1.0000 | 171 | 3 | 0 |
| QT_PHONE | 0.9808 | 0.9623 | 1.0000 | 255 | 10 | 0 |
| OGG_EDUCATION | 0.9803 | 0.9803 | 0.9803 | 299 | 6 | 6 |
| QT_RESIDENT_NUMBER | 0.9644 | 0.9312 | 1.0000 | 203 | 15 | 0 |
| TMI_EMAIL | 0.9381 | 1.0000 | 0.8833 | 318 | 0 | 42 |
| PS_NAME | 0.9368 | 0.9751 | 0.9014 | 3174 | 81 | 347 |
| LC_ADDRESS | 0.9352 | 0.9233 | 0.9475 | 361 | 30 | 20 |
| QT_ACCOUNT_NUMBER | 0.9211 | 0.8776 | 0.9691 | 251 | 35 | 8 |
| QT_PASSPORT_NUMBER | 0.9091 | 0.8333 | 1.0000 | 20 | 4 | 0 |
| QT_AGE | 0.9064 | 0.8807 | 0.9337 | 155 | 21 | 11 |
| DT_BIRTH | 0.8508 | 0.7912 | 0.9201 | 288 | 76 | 25 |
| OG_WORKPLACE | 0.8395 | 0.7857 | 0.9011 | 583 | 159 | 64 |
| FD_MAJOR | 0.7765 | 0.6615 | 0.9399 | 172 | 88 | 11 |
| QT_DRIVER_NUMBER | 0.7385 | 0.5854 | 1.0000 | 24 | 17 | 0 |
| OG_DEPARTMENT | 0.7210 | 0.6259 | 0.8502 | 261 | 156 | 46 |
| CV_POSITION | 0.6024 | 0.5266 | 0.7036 | 178 | 160 | 75 |