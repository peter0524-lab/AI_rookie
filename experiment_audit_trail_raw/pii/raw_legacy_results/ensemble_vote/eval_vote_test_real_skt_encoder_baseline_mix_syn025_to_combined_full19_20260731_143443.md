# entity-level 다수결 앙상블: test  (20260731_143443)

min_votes=1
data_dir=`/data/team/hwan/real/data/test_sets/combined`
evaluated_labels=19: `PS_NAME, LC_ADDRESS, OG_WORKPLACE, OG_DEPARTMENT, CV_POSITION, OGG_EDUCATION, QT_MOBILE, QT_PHONE, QT_RESIDENT_NUMBER, QT_ALIEN_NUMBER, QT_DRIVER_NUMBER, QT_PLATE_NUMBER, QT_ACCOUNT_NUMBER, QT_CARD_NUMBER, TMI_EMAIL, QT_PASSPORT_NUMBER, QT_AGE, DT_BIRTH, FD_MAJOR`
excluded_labels=0: `-`
excluded_gold_entities=0  excluded_predicted_entities=0

| Entity Micro F1 | **0.9561** |
| Precision | 0.9774 |
| Recall | 0.9356 |
| TP | 7366 | FP | 170 | FN | 507 |

| 레이블 | F1 | P | R | TP | FP | FN |
|--------|-----|---|---|----|----|-----|
| QT_MOBILE | 1.0000 | 1.0000 | 1.0000 | 432 | 0 | 0 |
| QT_RESIDENT_NUMBER | 1.0000 | 1.0000 | 1.0000 | 203 | 0 | 0 |
| QT_ALIEN_NUMBER | 1.0000 | 1.0000 | 1.0000 | 9 | 0 | 0 |
| QT_DRIVER_NUMBER | 1.0000 | 1.0000 | 1.0000 | 24 | 0 | 0 |
| QT_PASSPORT_NUMBER | 1.0000 | 1.0000 | 1.0000 | 20 | 0 | 0 |
| QT_PHONE | 0.9961 | 0.9922 | 1.0000 | 255 | 2 | 0 |
| QT_CARD_NUMBER | 0.9942 | 0.9884 | 1.0000 | 171 | 2 | 0 |
| QT_ACCOUNT_NUMBER | 0.9844 | 0.9922 | 0.9768 | 253 | 2 | 6 |
| OGG_EDUCATION | 0.9818 | 0.9933 | 0.9705 | 296 | 2 | 9 |
| DT_BIRTH | 0.9759 | 0.9806 | 0.9712 | 304 | 6 | 9 |
| TMI_EMAIL | 0.9670 | 1.0000 | 0.9361 | 337 | 0 | 23 |
| PS_NAME | 0.9639 | 0.9916 | 0.9378 | 3302 | 28 | 219 |
| FD_MAJOR | 0.9537 | 0.9511 | 0.9563 | 175 | 9 | 8 |
| LC_ADDRESS | 0.9534 | 0.9676 | 0.9396 | 358 | 12 | 23 |
| QT_PLATE_NUMBER | 0.9531 | 0.9531 | 0.9531 | 61 | 3 | 3 |
| OG_WORKPLACE | 0.9076 | 0.9360 | 0.8810 | 570 | 39 | 77 |
| QT_AGE | 0.9015 | 0.8935 | 0.9096 | 151 | 18 | 15 |
| OG_DEPARTMENT | 0.8612 | 0.9351 | 0.7980 | 245 | 17 | 62 |
| CV_POSITION | 0.8282 | 0.8696 | 0.7905 | 200 | 30 | 53 |