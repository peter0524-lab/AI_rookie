# entity-level 다수결 앙상블: test  (20260716_220222)

min_votes=2
data_dir=`/data/team/hwan/real/data/test_sets/combined`
evaluated_labels=18: `PS_NAME, LC_ADDRESS, OG_WORKPLACE, OG_DEPARTMENT, CV_POSITION, OGG_EDUCATION, QT_MOBILE, QT_PHONE, QT_RESIDENT_NUMBER, QT_DRIVER_NUMBER, QT_PLATE_NUMBER, QT_ACCOUNT_NUMBER, QT_CARD_NUMBER, TMI_EMAIL, QT_PASSPORT_NUMBER, QT_AGE, DT_BIRTH, FD_MAJOR`
excluded_labels=1: `QT_ALIEN_NUMBER`
excluded_gold_entities=9  excluded_predicted_entities=9

| Entity Micro F1 | **0.9735** |
| Precision | 0.9913 |
| Recall | 0.9563 |
| TP | 7520 | FP | 66 | FN | 344 |

| 레이블 | F1 | P | R | TP | FP | FN |
|--------|-----|---|---|----|----|-----|
| QT_MOBILE | 1.0000 | 1.0000 | 1.0000 | 432 | 0 | 0 |
| QT_RESIDENT_NUMBER | 1.0000 | 1.0000 | 1.0000 | 203 | 0 | 0 |
| QT_DRIVER_NUMBER | 1.0000 | 1.0000 | 1.0000 | 24 | 0 | 0 |
| QT_PLATE_NUMBER | 1.0000 | 1.0000 | 1.0000 | 64 | 0 | 0 |
| QT_CARD_NUMBER | 1.0000 | 1.0000 | 1.0000 | 171 | 0 | 0 |
| QT_PASSPORT_NUMBER | 1.0000 | 1.0000 | 1.0000 | 20 | 0 | 0 |
| QT_PHONE | 0.9980 | 0.9961 | 1.0000 | 255 | 1 | 0 |
| OGG_EDUCATION | 0.9951 | 1.0000 | 0.9902 | 302 | 0 | 3 |
| QT_ACCOUNT_NUMBER | 0.9942 | 1.0000 | 0.9884 | 256 | 0 | 3 |
| FD_MAJOR | 0.9864 | 0.9785 | 0.9945 | 182 | 4 | 1 |
| DT_BIRTH | 0.9791 | 0.9870 | 0.9712 | 304 | 4 | 9 |
| OG_DEPARTMENT | 0.9770 | 0.9867 | 0.9674 | 297 | 4 | 10 |
| PS_NAME | 0.9700 | 0.9961 | 0.9452 | 3328 | 13 | 193 |
| TMI_EMAIL | 0.9685 | 1.0000 | 0.9389 | 338 | 0 | 22 |
| LC_ADDRESS | 0.9666 | 0.9837 | 0.9501 | 362 | 6 | 19 |
| OG_WORKPLACE | 0.9486 | 0.9866 | 0.9134 | 591 | 8 | 56 |
| QT_AGE | 0.9471 | 0.9253 | 0.9699 | 161 | 13 | 5 |
| CV_POSITION | 0.9274 | 0.9465 | 0.9091 | 230 | 13 | 23 |