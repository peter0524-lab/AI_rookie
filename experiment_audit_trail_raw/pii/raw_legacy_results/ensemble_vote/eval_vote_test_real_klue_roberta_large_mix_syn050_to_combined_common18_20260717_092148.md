# entity-level 다수결 앙상블: test  (20260717_092148)

min_votes=1
data_dir=`/data/team/hwan/real/data/test_sets/combined`
evaluated_labels=18: `PS_NAME, LC_ADDRESS, OG_WORKPLACE, OG_DEPARTMENT, CV_POSITION, OGG_EDUCATION, QT_MOBILE, QT_PHONE, QT_RESIDENT_NUMBER, QT_DRIVER_NUMBER, QT_PLATE_NUMBER, QT_ACCOUNT_NUMBER, QT_CARD_NUMBER, TMI_EMAIL, QT_PASSPORT_NUMBER, QT_AGE, DT_BIRTH, FD_MAJOR`
excluded_labels=1: `QT_ALIEN_NUMBER`
excluded_gold_entities=9  excluded_predicted_entities=9

| Entity Micro F1 | **0.9699** |
| Precision | 0.9885 |
| Recall | 0.9519 |
| TP | 7486 | FP | 87 | FN | 378 |

| 레이블 | F1 | P | R | TP | FP | FN |
|--------|-----|---|---|----|----|-----|
| QT_MOBILE | 1.0000 | 1.0000 | 1.0000 | 432 | 0 | 0 |
| QT_RESIDENT_NUMBER | 1.0000 | 1.0000 | 1.0000 | 203 | 0 | 0 |
| QT_DRIVER_NUMBER | 1.0000 | 1.0000 | 1.0000 | 24 | 0 | 0 |
| QT_PLATE_NUMBER | 1.0000 | 1.0000 | 1.0000 | 64 | 0 | 0 |
| QT_CARD_NUMBER | 1.0000 | 1.0000 | 1.0000 | 171 | 0 | 0 |
| QT_PASSPORT_NUMBER | 1.0000 | 1.0000 | 1.0000 | 20 | 0 | 0 |
| QT_PHONE | 0.9961 | 0.9922 | 1.0000 | 255 | 2 | 0 |
| QT_ACCOUNT_NUMBER | 0.9922 | 1.0000 | 0.9846 | 255 | 0 | 4 |
| OGG_EDUCATION | 0.9901 | 0.9934 | 0.9869 | 301 | 2 | 4 |
| DT_BIRTH | 0.9759 | 0.9806 | 0.9712 | 304 | 6 | 9 |
| PS_NAME | 0.9704 | 0.9961 | 0.9460 | 3331 | 13 | 190 |
| TMI_EMAIL | 0.9700 | 1.0000 | 0.9417 | 339 | 0 | 21 |
| LC_ADDRESS | 0.9670 | 0.9734 | 0.9606 | 366 | 10 | 15 |
| FD_MAJOR | 0.9476 | 0.9095 | 0.9891 | 181 | 18 | 2 |
| OG_WORKPLACE | 0.9464 | 0.9966 | 0.9011 | 583 | 2 | 64 |
| QT_AGE | 0.9377 | 0.9240 | 0.9518 | 158 | 13 | 8 |
| OG_DEPARTMENT | 0.9333 | 0.9820 | 0.8893 | 273 | 5 | 34 |
| CV_POSITION | 0.9131 | 0.9339 | 0.8933 | 226 | 16 | 27 |