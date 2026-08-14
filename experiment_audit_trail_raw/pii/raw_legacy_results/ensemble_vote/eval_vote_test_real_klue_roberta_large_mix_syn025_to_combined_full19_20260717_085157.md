# entity-level 다수결 앙상블: test  (20260717_085157)

min_votes=1
data_dir=`/data/team/hwan/real/data/test_sets/combined`
evaluated_labels=19: `PS_NAME, LC_ADDRESS, OG_WORKPLACE, OG_DEPARTMENT, CV_POSITION, OGG_EDUCATION, QT_MOBILE, QT_PHONE, QT_RESIDENT_NUMBER, QT_ALIEN_NUMBER, QT_DRIVER_NUMBER, QT_PLATE_NUMBER, QT_ACCOUNT_NUMBER, QT_CARD_NUMBER, TMI_EMAIL, QT_PASSPORT_NUMBER, QT_AGE, DT_BIRTH, FD_MAJOR`
excluded_labels=0: `-`
excluded_gold_entities=0  excluded_predicted_entities=0

| Entity Micro F1 | **0.9699** |
| Precision | 0.9856 |
| Recall | 0.9547 |
| TP | 7516 | FP | 110 | FN | 357 |

| 레이블 | F1 | P | R | TP | FP | FN |
|--------|-----|---|---|----|----|-----|
| QT_MOBILE | 1.0000 | 1.0000 | 1.0000 | 432 | 0 | 0 |
| QT_RESIDENT_NUMBER | 1.0000 | 1.0000 | 1.0000 | 203 | 0 | 0 |
| QT_DRIVER_NUMBER | 1.0000 | 1.0000 | 1.0000 | 24 | 0 | 0 |
| QT_PLATE_NUMBER | 1.0000 | 1.0000 | 1.0000 | 64 | 0 | 0 |
| QT_CARD_NUMBER | 1.0000 | 1.0000 | 1.0000 | 171 | 0 | 0 |
| QT_PASSPORT_NUMBER | 1.0000 | 1.0000 | 1.0000 | 20 | 0 | 0 |
| QT_PHONE | 0.9980 | 0.9961 | 1.0000 | 255 | 1 | 0 |
| QT_ACCOUNT_NUMBER | 0.9942 | 1.0000 | 0.9884 | 256 | 0 | 3 |
| OGG_EDUCATION | 0.9934 | 0.9967 | 0.9902 | 302 | 1 | 3 |
| DT_BIRTH | 0.9774 | 0.9870 | 0.9681 | 303 | 4 | 10 |
| FD_MAJOR | 0.9731 | 0.9577 | 0.9891 | 181 | 8 | 2 |
| TMI_EMAIL | 0.9700 | 1.0000 | 0.9417 | 339 | 0 | 21 |
| PS_NAME | 0.9691 | 0.9946 | 0.9449 | 3327 | 18 | 194 |
| LC_ADDRESS | 0.9644 | 0.9683 | 0.9606 | 366 | 12 | 15 |
| OG_WORKPLACE | 0.9545 | 0.9868 | 0.9243 | 598 | 8 | 49 |
| QT_ALIEN_NUMBER | 0.9474 | 0.9000 | 1.0000 | 9 | 1 | 0 |
| OG_DEPARTMENT | 0.9362 | 0.9654 | 0.9088 | 279 | 10 | 28 |
| QT_AGE | 0.9157 | 0.8579 | 0.9819 | 163 | 27 | 3 |
| CV_POSITION | 0.9014 | 0.9180 | 0.8854 | 224 | 20 | 29 |