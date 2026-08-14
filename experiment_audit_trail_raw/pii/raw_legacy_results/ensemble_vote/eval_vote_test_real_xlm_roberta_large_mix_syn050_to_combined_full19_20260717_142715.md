# entity-level 다수결 앙상블: test  (20260717_142715)

min_votes=1
data_dir=`/data/team/hwan/real/data/test_sets/combined`
evaluated_labels=19: `PS_NAME, LC_ADDRESS, OG_WORKPLACE, OG_DEPARTMENT, CV_POSITION, OGG_EDUCATION, QT_MOBILE, QT_PHONE, QT_RESIDENT_NUMBER, QT_ALIEN_NUMBER, QT_DRIVER_NUMBER, QT_PLATE_NUMBER, QT_ACCOUNT_NUMBER, QT_CARD_NUMBER, TMI_EMAIL, QT_PASSPORT_NUMBER, QT_AGE, DT_BIRTH, FD_MAJOR`
excluded_labels=0: `-`
excluded_gold_entities=0  excluded_predicted_entities=0

| Entity Micro F1 | **0.9651** |
| Precision | 0.9862 |
| Recall | 0.9449 |
| TP | 7439 | FP | 104 | FN | 434 |

| 레이블 | F1 | P | R | TP | FP | FN |
|--------|-----|---|---|----|----|-----|
| QT_RESIDENT_NUMBER | 1.0000 | 1.0000 | 1.0000 | 203 | 0 | 0 |
| QT_ALIEN_NUMBER | 1.0000 | 1.0000 | 1.0000 | 9 | 0 | 0 |
| QT_DRIVER_NUMBER | 1.0000 | 1.0000 | 1.0000 | 24 | 0 | 0 |
| QT_PLATE_NUMBER | 1.0000 | 1.0000 | 1.0000 | 64 | 0 | 0 |
| QT_PASSPORT_NUMBER | 1.0000 | 1.0000 | 1.0000 | 20 | 0 | 0 |
| QT_MOBILE | 0.9988 | 1.0000 | 0.9977 | 431 | 0 | 1 |
| QT_CARD_NUMBER | 0.9971 | 0.9942 | 1.0000 | 171 | 1 | 0 |
| QT_PHONE | 0.9961 | 0.9922 | 1.0000 | 255 | 2 | 0 |
| OGG_EDUCATION | 0.9917 | 1.0000 | 0.9836 | 300 | 0 | 5 |
| QT_ACCOUNT_NUMBER | 0.9883 | 0.9961 | 0.9807 | 254 | 1 | 5 |
| DT_BIRTH | 0.9744 | 0.9775 | 0.9712 | 304 | 7 | 9 |
| PS_NAME | 0.9621 | 0.9933 | 0.9327 | 3284 | 22 | 237 |
| FD_MAJOR | 0.9620 | 0.9568 | 0.9672 | 177 | 8 | 6 |
| LC_ADDRESS | 0.9559 | 0.9728 | 0.9396 | 358 | 10 | 23 |
| TMI_EMAIL | 0.9489 | 1.0000 | 0.9028 | 325 | 0 | 35 |
| OG_WORKPLACE | 0.9464 | 0.9801 | 0.9150 | 592 | 12 | 55 |
| OG_DEPARTMENT | 0.9461 | 0.9791 | 0.9153 | 281 | 6 | 26 |
| QT_AGE | 0.9384 | 0.9143 | 0.9639 | 160 | 15 | 6 |
| CV_POSITION | 0.9080 | 0.9190 | 0.8972 | 227 | 20 | 26 |