# entity-level 다수결 앙상블: test  (20260717_162943)

min_votes=1
data_dir=`/data/team/hwan/real/data/test_sets/combined`
evaluated_labels=18: `PS_NAME, LC_ADDRESS, OG_WORKPLACE, OG_DEPARTMENT, CV_POSITION, OGG_EDUCATION, QT_MOBILE, QT_PHONE, QT_RESIDENT_NUMBER, QT_DRIVER_NUMBER, QT_PLATE_NUMBER, QT_ACCOUNT_NUMBER, QT_CARD_NUMBER, TMI_EMAIL, QT_PASSPORT_NUMBER, QT_AGE, DT_BIRTH, FD_MAJOR`
excluded_labels=1: `QT_ALIEN_NUMBER`
excluded_gold_entities=9  excluded_predicted_entities=9

| Entity Micro F1 | **0.9634** |
| Precision | 0.9889 |
| Recall | 0.9392 |
| TP | 7386 | FP | 83 | FN | 478 |

| 레이블 | F1 | P | R | TP | FP | FN |
|--------|-----|---|---|----|----|-----|
| QT_DRIVER_NUMBER | 1.0000 | 1.0000 | 1.0000 | 24 | 0 | 0 |
| QT_PLATE_NUMBER | 1.0000 | 1.0000 | 1.0000 | 64 | 0 | 0 |
| QT_CARD_NUMBER | 1.0000 | 1.0000 | 1.0000 | 171 | 0 | 0 |
| QT_PASSPORT_NUMBER | 1.0000 | 1.0000 | 1.0000 | 20 | 0 | 0 |
| QT_PHONE | 0.9980 | 0.9961 | 1.0000 | 255 | 1 | 0 |
| QT_MOBILE | 0.9977 | 0.9977 | 0.9977 | 431 | 1 | 1 |
| QT_RESIDENT_NUMBER | 0.9975 | 0.9951 | 1.0000 | 203 | 1 | 0 |
| QT_ACCOUNT_NUMBER | 0.9884 | 0.9922 | 0.9846 | 255 | 2 | 4 |
| OGG_EDUCATION | 0.9868 | 0.9901 | 0.9836 | 300 | 3 | 5 |
| DT_BIRTH | 0.9725 | 0.9837 | 0.9617 | 301 | 5 | 12 |
| FD_MAJOR | 0.9650 | 0.9521 | 0.9781 | 179 | 9 | 4 |
| PS_NAME | 0.9604 | 0.9957 | 0.9276 | 3266 | 14 | 255 |
| LC_ADDRESS | 0.9555 | 0.9833 | 0.9291 | 354 | 6 | 27 |
| QT_AGE | 0.9507 | 0.9162 | 0.9880 | 164 | 15 | 2 |
| TMI_EMAIL | 0.9489 | 1.0000 | 0.9028 | 325 | 0 | 35 |
| OG_WORKPLACE | 0.9466 | 0.9932 | 0.9042 | 585 | 4 | 62 |
| OG_DEPARTMENT | 0.9313 | 0.9855 | 0.8827 | 271 | 4 | 36 |
| CV_POSITION | 0.8916 | 0.9237 | 0.8617 | 218 | 18 | 35 |