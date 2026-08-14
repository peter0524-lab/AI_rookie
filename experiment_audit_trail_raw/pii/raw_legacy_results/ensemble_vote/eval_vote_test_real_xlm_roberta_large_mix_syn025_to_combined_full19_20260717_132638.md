# entity-level 다수결 앙상블: test  (20260717_132638)

min_votes=1
data_dir=`/data/team/hwan/real/data/test_sets/combined`
evaluated_labels=19: `PS_NAME, LC_ADDRESS, OG_WORKPLACE, OG_DEPARTMENT, CV_POSITION, OGG_EDUCATION, QT_MOBILE, QT_PHONE, QT_RESIDENT_NUMBER, QT_ALIEN_NUMBER, QT_DRIVER_NUMBER, QT_PLATE_NUMBER, QT_ACCOUNT_NUMBER, QT_CARD_NUMBER, TMI_EMAIL, QT_PASSPORT_NUMBER, QT_AGE, DT_BIRTH, FD_MAJOR`
excluded_labels=0: `-`
excluded_gold_entities=0  excluded_predicted_entities=0

| Entity Micro F1 | **0.9630** |
| Precision | 0.9871 |
| Recall | 0.9402 |
| TP | 7402 | FP | 97 | FN | 471 |

| 레이블 | F1 | P | R | TP | FP | FN |
|--------|-----|---|---|----|----|-----|
| QT_ALIEN_NUMBER | 1.0000 | 1.0000 | 1.0000 | 9 | 0 | 0 |
| QT_PLATE_NUMBER | 1.0000 | 1.0000 | 1.0000 | 64 | 0 | 0 |
| QT_PASSPORT_NUMBER | 1.0000 | 1.0000 | 1.0000 | 20 | 0 | 0 |
| QT_MOBILE | 0.9977 | 0.9977 | 0.9977 | 431 | 1 | 1 |
| QT_PHONE | 0.9961 | 0.9922 | 1.0000 | 255 | 2 | 0 |
| QT_RESIDENT_NUMBER | 0.9951 | 0.9902 | 1.0000 | 203 | 2 | 0 |
| QT_CARD_NUMBER | 0.9942 | 0.9884 | 1.0000 | 171 | 2 | 0 |
| OGG_EDUCATION | 0.9902 | 0.9902 | 0.9902 | 302 | 3 | 3 |
| QT_ACCOUNT_NUMBER | 0.9865 | 0.9884 | 0.9846 | 255 | 3 | 4 |
| QT_DRIVER_NUMBER | 0.9796 | 0.9600 | 1.0000 | 24 | 1 | 0 |
| DT_BIRTH | 0.9694 | 0.9773 | 0.9617 | 301 | 7 | 12 |
| FD_MAJOR | 0.9674 | 0.9622 | 0.9727 | 178 | 7 | 5 |
| PS_NAME | 0.9623 | 0.9991 | 0.9281 | 3268 | 3 | 253 |
| LC_ADDRESS | 0.9507 | 0.9649 | 0.9370 | 357 | 13 | 24 |
| TMI_EMAIL | 0.9489 | 1.0000 | 0.9028 | 325 | 0 | 35 |
| OG_WORKPLACE | 0.9479 | 0.9850 | 0.9134 | 591 | 9 | 56 |
| OG_DEPARTMENT | 0.9283 | 0.9749 | 0.8860 | 272 | 7 | 35 |
| QT_AGE | 0.9271 | 0.8983 | 0.9578 | 159 | 18 | 7 |
| CV_POSITION | 0.8875 | 0.9195 | 0.8577 | 217 | 19 | 36 |