# entity-level 다수결 앙상블: test  (20260731_123122)

min_votes=1
data_dir=`/data/team/hwan/real/data/test_sets/combined`
evaluated_labels=19: `PS_NAME, LC_ADDRESS, OG_WORKPLACE, OG_DEPARTMENT, CV_POSITION, OGG_EDUCATION, QT_MOBILE, QT_PHONE, QT_RESIDENT_NUMBER, QT_ALIEN_NUMBER, QT_DRIVER_NUMBER, QT_PLATE_NUMBER, QT_ACCOUNT_NUMBER, QT_CARD_NUMBER, TMI_EMAIL, QT_PASSPORT_NUMBER, QT_AGE, DT_BIRTH, FD_MAJOR`
excluded_labels=0: `-`
excluded_gold_entities=0  excluded_predicted_entities=0

| Entity Micro F1 | **0.9032** |
| Precision | 0.9333 |
| Recall | 0.8750 |
| TP | 6889 | FP | 492 | FN | 984 |

| 레이블 | F1 | P | R | TP | FP | FN |
|--------|-----|---|---|----|----|-----|
| QT_MOBILE | 1.0000 | 1.0000 | 1.0000 | 432 | 0 | 0 |
| QT_ALIEN_NUMBER | 1.0000 | 1.0000 | 1.0000 | 9 | 0 | 0 |
| QT_RESIDENT_NUMBER | 0.9951 | 0.9902 | 1.0000 | 203 | 2 | 0 |
| QT_PHONE | 0.9806 | 0.9693 | 0.9922 | 253 | 8 | 2 |
| PS_NAME | 0.9541 | 0.9668 | 0.9418 | 3316 | 114 | 205 |
| QT_ACCOUNT_NUMBER | 0.9209 | 0.9701 | 0.8764 | 227 | 7 | 32 |
| TMI_EMAIL | 0.9162 | 0.9213 | 0.9111 | 328 | 28 | 32 |
| QT_CARD_NUMBER | 0.9143 | 1.0000 | 0.8421 | 144 | 0 | 27 |
| OGG_EDUCATION | 0.9039 | 0.9883 | 0.8328 | 254 | 3 | 51 |
| DT_BIRTH | 0.8998 | 0.9601 | 0.8466 | 265 | 11 | 48 |
| OG_WORKPLACE | 0.8453 | 0.8111 | 0.8825 | 571 | 133 | 76 |
| QT_PASSPORT_NUMBER | 0.8333 | 0.9375 | 0.7500 | 15 | 1 | 5 |
| QT_DRIVER_NUMBER | 0.8293 | 1.0000 | 0.7083 | 17 | 0 | 7 |
| LC_ADDRESS | 0.8207 | 0.9747 | 0.7087 | 270 | 7 | 111 |
| FD_MAJOR | 0.7638 | 0.9365 | 0.6448 | 118 | 8 | 65 |
| OG_DEPARTMENT | 0.7237 | 0.8986 | 0.6059 | 186 | 21 | 121 |
| QT_AGE | 0.7143 | 0.8203 | 0.6325 | 105 | 23 | 61 |
| CV_POSITION | 0.6515 | 0.9021 | 0.5099 | 129 | 14 | 124 |
| QT_PLATE_NUMBER | 0.4215 | 0.2956 | 0.7344 | 47 | 112 | 17 |