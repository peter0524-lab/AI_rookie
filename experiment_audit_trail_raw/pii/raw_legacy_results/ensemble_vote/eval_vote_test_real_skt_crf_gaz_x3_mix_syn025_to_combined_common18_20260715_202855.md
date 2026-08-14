# entity-level 다수결 앙상블: test  (20260715_202855)

min_votes=2
data_dir=`/data/team/hwan/real/data/test_sets/combined`
evaluated_labels=18: `PS_NAME, LC_ADDRESS, OG_WORKPLACE, OG_DEPARTMENT, CV_POSITION, OGG_EDUCATION, QT_MOBILE, QT_PHONE, QT_RESIDENT_NUMBER, QT_DRIVER_NUMBER, QT_PLATE_NUMBER, QT_ACCOUNT_NUMBER, QT_CARD_NUMBER, TMI_EMAIL, QT_PASSPORT_NUMBER, QT_AGE, DT_BIRTH, FD_MAJOR`
excluded_labels=1: `QT_ALIEN_NUMBER`
excluded_gold_entities=9  excluded_predicted_entities=9

| Entity Micro F1 | **0.9720** |
| Precision | 0.9911 |
| Recall | 0.9536 |
| TP | 7499 | FP | 67 | FN | 365 |

| 레이블 | F1 | P | R | TP | FP | FN |
|--------|-----|---|---|----|----|-----|
| QT_MOBILE | 1.0000 | 1.0000 | 1.0000 | 432 | 0 | 0 |
| QT_RESIDENT_NUMBER | 1.0000 | 1.0000 | 1.0000 | 203 | 0 | 0 |
| QT_DRIVER_NUMBER | 1.0000 | 1.0000 | 1.0000 | 24 | 0 | 0 |
| QT_PLATE_NUMBER | 1.0000 | 1.0000 | 1.0000 | 64 | 0 | 0 |
| QT_CARD_NUMBER | 1.0000 | 1.0000 | 1.0000 | 171 | 0 | 0 |
| QT_PASSPORT_NUMBER | 1.0000 | 1.0000 | 1.0000 | 20 | 0 | 0 |
| QT_PHONE | 0.9961 | 0.9922 | 1.0000 | 255 | 2 | 0 |
| OGG_EDUCATION | 0.9951 | 0.9967 | 0.9934 | 303 | 1 | 2 |
| QT_ACCOUNT_NUMBER | 0.9942 | 1.0000 | 0.9884 | 256 | 0 | 3 |
| FD_MAJOR | 0.9863 | 0.9890 | 0.9836 | 180 | 2 | 3 |
| DT_BIRTH | 0.9776 | 0.9807 | 0.9744 | 305 | 6 | 8 |
| PS_NAME | 0.9695 | 0.9964 | 0.9440 | 3324 | 12 | 197 |
| LC_ADDRESS | 0.9693 | 0.9864 | 0.9528 | 363 | 5 | 18 |
| TMI_EMAIL | 0.9685 | 1.0000 | 0.9389 | 338 | 0 | 22 |
| OG_WORKPLACE | 0.9509 | 0.9916 | 0.9134 | 591 | 5 | 56 |
| OG_DEPARTMENT | 0.9475 | 0.9859 | 0.9121 | 280 | 4 | 27 |
| QT_AGE | 0.9360 | 0.9045 | 0.9699 | 161 | 17 | 5 |
| CV_POSITION | 0.9253 | 0.9463 | 0.9051 | 229 | 13 | 24 |