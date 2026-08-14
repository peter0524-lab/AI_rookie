# entity-level 다수결 앙상블: test  (20260717_205942)

min_votes=1
data_dir=`/data/team/hwan/real/data/test_sets/combined`
evaluated_labels=19: `PS_NAME, LC_ADDRESS, OG_WORKPLACE, OG_DEPARTMENT, CV_POSITION, OGG_EDUCATION, QT_MOBILE, QT_PHONE, QT_RESIDENT_NUMBER, QT_ALIEN_NUMBER, QT_DRIVER_NUMBER, QT_PLATE_NUMBER, QT_ACCOUNT_NUMBER, QT_CARD_NUMBER, TMI_EMAIL, QT_PASSPORT_NUMBER, QT_AGE, DT_BIRTH, FD_MAJOR`
excluded_labels=0: `-`
excluded_gold_entities=0  excluded_predicted_entities=0

| Entity Micro F1 | **0.5597** |
| Precision | 0.9478 |
| Recall | 0.3971 |
| TP | 3126 | FP | 172 | FN | 4747 |

| 레이블 | F1 | P | R | TP | FP | FN |
|--------|-----|---|---|----|----|-----|
| QT_MOBILE | 1.0000 | 1.0000 | 1.0000 | 432 | 0 | 0 |
| QT_ALIEN_NUMBER | 1.0000 | 1.0000 | 1.0000 | 9 | 0 | 0 |
| QT_PHONE | 0.9942 | 0.9884 | 1.0000 | 255 | 3 | 0 |
| QT_RESIDENT_NUMBER | 0.9831 | 0.9667 | 1.0000 | 203 | 7 | 0 |
| QT_CARD_NUMBER | 0.9515 | 0.9874 | 0.9181 | 157 | 2 | 14 |
| QT_ACCOUNT_NUMBER | 0.9361 | 0.9121 | 0.9614 | 249 | 24 | 10 |
| DT_BIRTH | 0.9116 | 0.9745 | 0.8562 | 268 | 7 | 45 |
| QT_AGE | 0.7361 | 0.8689 | 0.6386 | 106 | 16 | 60 |
| QT_DRIVER_NUMBER | 0.6792 | 0.6207 | 0.7500 | 18 | 11 | 6 |
| PS_NAME | 0.5425 | 0.9516 | 0.3794 | 1336 | 68 | 2185 |
| QT_PLATE_NUMBER | 0.3951 | 0.9412 | 0.2500 | 16 | 1 | 48 |
| TMI_EMAIL | 0.1633 | 1.0000 | 0.0889 | 32 | 0 | 328 |
| OGG_EDUCATION | 0.1450 | 0.9231 | 0.0787 | 24 | 2 | 281 |
| FD_MAJOR | 0.0529 | 0.8333 | 0.0273 | 5 | 1 | 178 |
| LC_ADDRESS | 0.0512 | 1.0000 | 0.0262 | 10 | 0 | 371 |
| OG_DEPARTMENT | 0.0129 | 0.6667 | 0.0065 | 2 | 1 | 305 |
| OG_WORKPLACE | 0.0118 | 0.1250 | 0.0062 | 4 | 28 | 643 |
| CV_POSITION | 0.0000 | 0.0000 | 0.0000 | 0 | 1 | 253 |
| QT_PASSPORT_NUMBER | 0.0000 | 0.0000 | 0.0000 | 0 | 0 | 20 |