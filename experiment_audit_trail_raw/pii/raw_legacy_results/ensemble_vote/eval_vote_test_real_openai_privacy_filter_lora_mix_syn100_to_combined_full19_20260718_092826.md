# entity-level 다수결 앙상블: test  (20260718_092826)

min_votes=1
data_dir=`/data/team/hwan/real/data/test_sets/combined`
evaluated_labels=19: `PS_NAME, LC_ADDRESS, OG_WORKPLACE, OG_DEPARTMENT, CV_POSITION, OGG_EDUCATION, QT_MOBILE, QT_PHONE, QT_RESIDENT_NUMBER, QT_ALIEN_NUMBER, QT_DRIVER_NUMBER, QT_PLATE_NUMBER, QT_ACCOUNT_NUMBER, QT_CARD_NUMBER, TMI_EMAIL, QT_PASSPORT_NUMBER, QT_AGE, DT_BIRTH, FD_MAJOR`
excluded_labels=0: `-`
excluded_gold_entities=0  excluded_predicted_entities=0

| Entity Micro F1 | **0.5883** |
| Precision | 0.9725 |
| Recall | 0.4217 |
| TP | 3320 | FP | 94 | FN | 4553 |

| 레이블 | F1 | P | R | TP | FP | FN |
|--------|-----|---|---|----|----|-----|
| QT_MOBILE | 1.0000 | 1.0000 | 1.0000 | 432 | 0 | 0 |
| QT_RESIDENT_NUMBER | 1.0000 | 1.0000 | 1.0000 | 203 | 0 | 0 |
| QT_ALIEN_NUMBER | 1.0000 | 1.0000 | 1.0000 | 9 | 0 | 0 |
| QT_PHONE | 0.9961 | 0.9922 | 1.0000 | 255 | 2 | 0 |
| QT_CARD_NUMBER | 0.9760 | 1.0000 | 0.9532 | 163 | 0 | 8 |
| DT_BIRTH | 0.9712 | 0.9712 | 0.9712 | 304 | 9 | 9 |
| QT_PLATE_NUMBER | 0.9683 | 0.9839 | 0.9531 | 61 | 1 | 3 |
| QT_ACCOUNT_NUMBER | 0.9640 | 1.0000 | 0.9305 | 241 | 0 | 18 |
| QT_AGE | 0.8428 | 0.8816 | 0.8072 | 134 | 18 | 32 |
| QT_DRIVER_NUMBER | 0.7692 | 1.0000 | 0.6250 | 15 | 0 | 9 |
| PS_NAME | 0.5552 | 0.9723 | 0.3885 | 1368 | 39 | 2153 |
| OGG_EDUCATION | 0.2159 | 0.8085 | 0.1246 | 38 | 9 | 267 |
| TMI_EMAIL | 0.1818 | 1.0000 | 0.1000 | 36 | 0 | 324 |
| CV_POSITION | 0.1377 | 0.8261 | 0.0751 | 19 | 4 | 234 |
| QT_PASSPORT_NUMBER | 0.0952 | 1.0000 | 0.0500 | 1 | 0 | 19 |
| LC_ADDRESS | 0.0804 | 0.9412 | 0.0420 | 16 | 1 | 365 |
| FD_MAJOR | 0.0733 | 0.8750 | 0.0383 | 7 | 1 | 176 |
| OG_DEPARTMENT | 0.0566 | 0.8182 | 0.0293 | 9 | 2 | 298 |
| OG_WORKPLACE | 0.0271 | 0.5294 | 0.0139 | 9 | 8 | 638 |