# entity-level 다수결 앙상블: test  (20260717_111325)

min_votes=1
data_dir=`/data/team/hwan/real/data/test_sets/synthetic`
evaluated_labels=19: `PS_NAME, LC_ADDRESS, OG_WORKPLACE, OG_DEPARTMENT, CV_POSITION, OGG_EDUCATION, QT_MOBILE, QT_PHONE, QT_RESIDENT_NUMBER, QT_ALIEN_NUMBER, QT_DRIVER_NUMBER, QT_PLATE_NUMBER, QT_ACCOUNT_NUMBER, QT_CARD_NUMBER, TMI_EMAIL, QT_PASSPORT_NUMBER, QT_AGE, DT_BIRTH, FD_MAJOR`
excluded_labels=0: `-`
excluded_gold_entities=0  excluded_predicted_entities=0

| Entity Micro F1 | **0.9120** |
| Precision | 0.9059 |
| Recall | 0.9181 |
| TP | 5972 | FP | 620 | FN | 533 |

| 레이블 | F1 | P | R | TP | FP | FN |
|--------|-----|---|---|----|----|-----|
| QT_DRIVER_NUMBER | 1.0000 | 1.0000 | 1.0000 | 7 | 0 | 0 |
| QT_PASSPORT_NUMBER | 1.0000 | 1.0000 | 1.0000 | 2 | 0 | 0 |
| QT_MOBILE | 0.9974 | 0.9947 | 1.0000 | 377 | 2 | 0 |
| QT_CARD_NUMBER | 0.9841 | 0.9688 | 1.0000 | 93 | 3 | 0 |
| QT_RESIDENT_NUMBER | 0.9840 | 0.9686 | 1.0000 | 185 | 6 | 0 |
| OGG_EDUCATION | 0.9811 | 1.0000 | 0.9630 | 208 | 0 | 8 |
| QT_PLATE_NUMBER | 0.9600 | 0.9231 | 1.0000 | 12 | 1 | 0 |
| TMI_EMAIL | 0.9591 | 0.9961 | 0.9247 | 258 | 1 | 21 |
| QT_PHONE | 0.9563 | 0.9163 | 1.0000 | 186 | 17 | 0 |
| PS_NAME | 0.9479 | 0.9817 | 0.9163 | 3064 | 57 | 280 |
| LC_ADDRESS | 0.9457 | 0.9278 | 0.9643 | 270 | 21 | 10 |
| QT_ACCOUNT_NUMBER | 0.8974 | 0.8413 | 0.9615 | 175 | 33 | 7 |
| FD_MAJOR | 0.8504 | 0.7941 | 0.9153 | 108 | 28 | 10 |
| OG_WORKPLACE | 0.8305 | 0.7523 | 0.9270 | 495 | 163 | 39 |
| QT_AGE | 0.8304 | 0.8158 | 0.8455 | 93 | 21 | 17 |
| DT_BIRTH | 0.7670 | 0.6921 | 0.8601 | 209 | 93 | 34 |
| OG_DEPARTMENT | 0.6303 | 0.5436 | 0.7500 | 156 | 131 | 52 |
| CV_POSITION | 0.6066 | 0.6435 | 0.5736 | 74 | 41 | 55 |
| QT_ALIEN_NUMBER | 0.0000 | 0.0000 | 0.0000 | 0 | 2 | 0 |