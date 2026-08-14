# entity-level 다수결 앙상블: test  (20260717_102027)

min_votes=1
data_dir=`/data/team/hwan/real/data/test_sets/combined`
evaluated_labels=19: `PS_NAME, LC_ADDRESS, OG_WORKPLACE, OG_DEPARTMENT, CV_POSITION, OGG_EDUCATION, QT_MOBILE, QT_PHONE, QT_RESIDENT_NUMBER, QT_ALIEN_NUMBER, QT_DRIVER_NUMBER, QT_PLATE_NUMBER, QT_ACCOUNT_NUMBER, QT_CARD_NUMBER, TMI_EMAIL, QT_PASSPORT_NUMBER, QT_AGE, DT_BIRTH, FD_MAJOR`
excluded_labels=0: `-`
excluded_gold_entities=0  excluded_predicted_entities=0

| Entity Micro F1 | **0.9721** |
| Precision | 0.9856 |
| Recall | 0.9590 |
| TP | 7550 | FP | 110 | FN | 323 |

| 레이블 | F1 | P | R | TP | FP | FN |
|--------|-----|---|---|----|----|-----|
| QT_MOBILE | 1.0000 | 1.0000 | 1.0000 | 432 | 0 | 0 |
| QT_ALIEN_NUMBER | 1.0000 | 1.0000 | 1.0000 | 9 | 0 | 0 |
| QT_DRIVER_NUMBER | 1.0000 | 1.0000 | 1.0000 | 24 | 0 | 0 |
| QT_PLATE_NUMBER | 1.0000 | 1.0000 | 1.0000 | 64 | 0 | 0 |
| QT_CARD_NUMBER | 1.0000 | 1.0000 | 1.0000 | 171 | 0 | 0 |
| QT_PASSPORT_NUMBER | 1.0000 | 1.0000 | 1.0000 | 20 | 0 | 0 |
| QT_PHONE | 0.9980 | 0.9961 | 1.0000 | 255 | 1 | 0 |
| QT_RESIDENT_NUMBER | 0.9975 | 0.9951 | 1.0000 | 203 | 1 | 0 |
| QT_ACCOUNT_NUMBER | 0.9942 | 1.0000 | 0.9884 | 256 | 0 | 3 |
| OGG_EDUCATION | 0.9934 | 0.9934 | 0.9934 | 303 | 2 | 2 |
| DT_BIRTH | 0.9775 | 0.9838 | 0.9712 | 304 | 5 | 9 |
| FD_MAJOR | 0.9730 | 0.9626 | 0.9836 | 180 | 7 | 3 |
| LC_ADDRESS | 0.9706 | 0.9891 | 0.9528 | 363 | 4 | 18 |
| PS_NAME | 0.9705 | 0.9946 | 0.9475 | 3336 | 18 | 185 |
| TMI_EMAIL | 0.9700 | 1.0000 | 0.9417 | 339 | 0 | 21 |
| OG_WORKPLACE | 0.9596 | 0.9838 | 0.9366 | 606 | 10 | 41 |
| OG_DEPARTMENT | 0.9446 | 0.9446 | 0.9446 | 290 | 17 | 17 |
| QT_AGE | 0.9443 | 0.9200 | 0.9699 | 161 | 14 | 5 |
| CV_POSITION | 0.9035 | 0.8830 | 0.9249 | 234 | 31 | 19 |