# entity-level 다수결 앙상블: test  (20260717_111142)

min_votes=1
data_dir=`/data/team/hwan/real/data/test_sets/combined`
evaluated_labels=19: `PS_NAME, LC_ADDRESS, OG_WORKPLACE, OG_DEPARTMENT, CV_POSITION, OGG_EDUCATION, QT_MOBILE, QT_PHONE, QT_RESIDENT_NUMBER, QT_ALIEN_NUMBER, QT_DRIVER_NUMBER, QT_PLATE_NUMBER, QT_ACCOUNT_NUMBER, QT_CARD_NUMBER, TMI_EMAIL, QT_PASSPORT_NUMBER, QT_AGE, DT_BIRTH, FD_MAJOR`
excluded_labels=0: `-`
excluded_gold_entities=0  excluded_predicted_entities=0

| Entity Micro F1 | **0.9726** |
| Precision | 0.9882 |
| Recall | 0.9576 |
| TP | 7539 | FP | 90 | FN | 334 |

| 레이블 | F1 | P | R | TP | FP | FN |
|--------|-----|---|---|----|----|-----|
| QT_MOBILE | 1.0000 | 1.0000 | 1.0000 | 432 | 0 | 0 |
| QT_ALIEN_NUMBER | 1.0000 | 1.0000 | 1.0000 | 9 | 0 | 0 |
| QT_DRIVER_NUMBER | 1.0000 | 1.0000 | 1.0000 | 24 | 0 | 0 |
| QT_PLATE_NUMBER | 1.0000 | 1.0000 | 1.0000 | 64 | 0 | 0 |
| QT_CARD_NUMBER | 1.0000 | 1.0000 | 1.0000 | 171 | 0 | 0 |
| QT_PASSPORT_NUMBER | 1.0000 | 1.0000 | 1.0000 | 20 | 0 | 0 |
| QT_PHONE | 0.9980 | 0.9961 | 1.0000 | 255 | 1 | 0 |
| QT_ACCOUNT_NUMBER | 0.9942 | 1.0000 | 0.9884 | 256 | 0 | 3 |
| QT_RESIDENT_NUMBER | 0.9927 | 0.9854 | 1.0000 | 203 | 3 | 0 |
| OGG_EDUCATION | 0.9837 | 0.9805 | 0.9869 | 301 | 6 | 4 |
| DT_BIRTH | 0.9789 | 0.9934 | 0.9649 | 302 | 2 | 11 |
| FD_MAJOR | 0.9753 | 0.9780 | 0.9727 | 178 | 4 | 5 |
| PS_NAME | 0.9728 | 0.9970 | 0.9497 | 3344 | 10 | 177 |
| LC_ADDRESS | 0.9706 | 0.9891 | 0.9528 | 363 | 4 | 18 |
| TMI_EMAIL | 0.9700 | 1.0000 | 0.9417 | 339 | 0 | 21 |
| OG_WORKPLACE | 0.9553 | 0.9884 | 0.9243 | 598 | 7 | 49 |
| OG_DEPARTMENT | 0.9388 | 0.9530 | 0.9251 | 284 | 14 | 23 |
| QT_AGE | 0.9368 | 0.8956 | 0.9819 | 163 | 19 | 3 |
| CV_POSITION | 0.9209 | 0.9209 | 0.9209 | 233 | 20 | 20 |