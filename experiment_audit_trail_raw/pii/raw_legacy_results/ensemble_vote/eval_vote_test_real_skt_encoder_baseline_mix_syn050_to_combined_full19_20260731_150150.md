# entity-level 다수결 앙상블: test  (20260731_150150)

min_votes=1
data_dir=`/data/team/hwan/real/data/test_sets/combined`
evaluated_labels=19: `PS_NAME, LC_ADDRESS, OG_WORKPLACE, OG_DEPARTMENT, CV_POSITION, OGG_EDUCATION, QT_MOBILE, QT_PHONE, QT_RESIDENT_NUMBER, QT_ALIEN_NUMBER, QT_DRIVER_NUMBER, QT_PLATE_NUMBER, QT_ACCOUNT_NUMBER, QT_CARD_NUMBER, TMI_EMAIL, QT_PASSPORT_NUMBER, QT_AGE, DT_BIRTH, FD_MAJOR`
excluded_labels=0: `-`
excluded_gold_entities=0  excluded_predicted_entities=0

| Entity Micro F1 | **0.9600** |
| Precision | 0.9803 |
| Recall | 0.9406 |
| TP | 7405 | FP | 149 | FN | 468 |

| 레이블 | F1 | P | R | TP | FP | FN |
|--------|-----|---|---|----|----|-----|
| QT_MOBILE | 1.0000 | 1.0000 | 1.0000 | 432 | 0 | 0 |
| QT_RESIDENT_NUMBER | 1.0000 | 1.0000 | 1.0000 | 203 | 0 | 0 |
| QT_ALIEN_NUMBER | 1.0000 | 1.0000 | 1.0000 | 9 | 0 | 0 |
| QT_DRIVER_NUMBER | 1.0000 | 1.0000 | 1.0000 | 24 | 0 | 0 |
| QT_CARD_NUMBER | 1.0000 | 1.0000 | 1.0000 | 171 | 0 | 0 |
| QT_PASSPORT_NUMBER | 1.0000 | 1.0000 | 1.0000 | 20 | 0 | 0 |
| QT_ACCOUNT_NUMBER | 0.9942 | 1.0000 | 0.9884 | 256 | 0 | 3 |
| QT_PHONE | 0.9941 | 0.9922 | 0.9961 | 254 | 2 | 1 |
| OGG_EDUCATION | 0.9851 | 0.9933 | 0.9770 | 298 | 2 | 7 |
| DT_BIRTH | 0.9776 | 0.9807 | 0.9744 | 305 | 6 | 8 |
| QT_PLATE_NUMBER | 0.9771 | 0.9552 | 1.0000 | 64 | 3 | 0 |
| TMI_EMAIL | 0.9700 | 1.0000 | 0.9417 | 339 | 0 | 21 |
| PS_NAME | 0.9635 | 0.9904 | 0.9381 | 3303 | 32 | 218 |
| LC_ADDRESS | 0.9585 | 0.9781 | 0.9396 | 358 | 8 | 23 |
| FD_MAJOR | 0.9428 | 0.9402 | 0.9454 | 173 | 11 | 10 |
| OG_WORKPLACE | 0.9173 | 0.9548 | 0.8825 | 571 | 27 | 76 |
| OG_DEPARTMENT | 0.9029 | 0.9464 | 0.8632 | 265 | 15 | 42 |
| QT_AGE | 0.9003 | 0.9030 | 0.8976 | 149 | 16 | 17 |
| CV_POSITION | 0.8595 | 0.8866 | 0.8340 | 211 | 27 | 42 |