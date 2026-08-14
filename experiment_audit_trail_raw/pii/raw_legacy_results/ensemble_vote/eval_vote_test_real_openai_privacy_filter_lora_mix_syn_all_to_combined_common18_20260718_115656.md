# entity-level 다수결 앙상블: test  (20260718_115656)

min_votes=1
data_dir=`/data/team/hwan/real/data/test_sets/combined`
evaluated_labels=18: `PS_NAME, LC_ADDRESS, OG_WORKPLACE, OG_DEPARTMENT, CV_POSITION, OGG_EDUCATION, QT_MOBILE, QT_PHONE, QT_RESIDENT_NUMBER, QT_DRIVER_NUMBER, QT_PLATE_NUMBER, QT_ACCOUNT_NUMBER, QT_CARD_NUMBER, TMI_EMAIL, QT_PASSPORT_NUMBER, QT_AGE, DT_BIRTH, FD_MAJOR`
excluded_labels=1: `QT_ALIEN_NUMBER`
excluded_gold_entities=9  excluded_predicted_entities=9

| Entity Micro F1 | **0.5826** |
| Precision | 0.9775 |
| Recall | 0.4149 |
| TP | 3263 | FP | 75 | FN | 4601 |

| 레이블 | F1 | P | R | TP | FP | FN |
|--------|-----|---|---|----|----|-----|
| QT_MOBILE | 0.9988 | 0.9977 | 1.0000 | 432 | 1 | 0 |
| QT_PHONE | 0.9980 | 0.9961 | 1.0000 | 255 | 1 | 0 |
| QT_RESIDENT_NUMBER | 0.9975 | 0.9951 | 1.0000 | 203 | 1 | 0 |
| QT_CARD_NUMBER | 0.9791 | 1.0000 | 0.9591 | 164 | 0 | 7 |
| DT_BIRTH | 0.9726 | 0.9805 | 0.9649 | 302 | 6 | 11 |
| QT_ACCOUNT_NUMBER | 0.9640 | 1.0000 | 0.9305 | 241 | 0 | 18 |
| QT_PLATE_NUMBER | 0.9600 | 0.9836 | 0.9375 | 60 | 1 | 4 |
| QT_AGE | 0.8355 | 0.9203 | 0.7651 | 127 | 11 | 39 |
| QT_DRIVER_NUMBER | 0.8293 | 1.0000 | 0.7083 | 17 | 0 | 7 |
| PS_NAME | 0.5467 | 0.9795 | 0.3792 | 1335 | 28 | 2186 |
| OGG_EDUCATION | 0.2011 | 0.8140 | 0.1148 | 35 | 8 | 270 |
| TMI_EMAIL | 0.1818 | 1.0000 | 0.1000 | 36 | 0 | 324 |
| CV_POSITION | 0.1495 | 0.7500 | 0.0830 | 21 | 7 | 232 |
| QT_PASSPORT_NUMBER | 0.0952 | 1.0000 | 0.0500 | 1 | 0 | 19 |
| LC_ADDRESS | 0.0748 | 0.7500 | 0.0394 | 15 | 5 | 366 |
| OG_DEPARTMENT | 0.0692 | 1.0000 | 0.0358 | 11 | 0 | 296 |
| FD_MAJOR | 0.0628 | 0.7500 | 0.0328 | 6 | 2 | 177 |
| OG_WORKPLACE | 0.0061 | 0.3333 | 0.0031 | 2 | 4 | 645 |