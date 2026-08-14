# entity-level 다수결 앙상블: test  (20260717_102123)

min_votes=1
data_dir=`/data/team/hwan/real/data/test_sets/kdpii`
evaluated_labels=19: `PS_NAME, LC_ADDRESS, OG_WORKPLACE, OG_DEPARTMENT, CV_POSITION, OGG_EDUCATION, QT_MOBILE, QT_PHONE, QT_RESIDENT_NUMBER, QT_ALIEN_NUMBER, QT_DRIVER_NUMBER, QT_PLATE_NUMBER, QT_ACCOUNT_NUMBER, QT_CARD_NUMBER, TMI_EMAIL, QT_PASSPORT_NUMBER, QT_AGE, DT_BIRTH, FD_MAJOR`
excluded_labels=0: `-`
excluded_gold_entities=0  excluded_predicted_entities=0

| Entity Micro F1 | **0.9584** |
| Precision | 0.9491 |
| Recall | 0.9678 |
| TP | 1324 | FP | 71 | FN | 44 |

| 레이블 | F1 | P | R | TP | FP | FN |
|--------|-----|---|---|----|----|-----|
| QT_MOBILE | 1.0000 | 1.0000 | 1.0000 | 55 | 0 | 0 |
| QT_PHONE | 1.0000 | 1.0000 | 1.0000 | 69 | 0 | 0 |
| QT_ALIEN_NUMBER | 1.0000 | 1.0000 | 1.0000 | 9 | 0 | 0 |
| QT_DRIVER_NUMBER | 1.0000 | 1.0000 | 1.0000 | 17 | 0 | 0 |
| QT_PLATE_NUMBER | 1.0000 | 1.0000 | 1.0000 | 52 | 0 | 0 |
| QT_ACCOUNT_NUMBER | 1.0000 | 1.0000 | 1.0000 | 77 | 0 | 0 |
| QT_CARD_NUMBER | 1.0000 | 1.0000 | 1.0000 | 78 | 0 | 0 |
| TMI_EMAIL | 1.0000 | 1.0000 | 1.0000 | 81 | 0 | 0 |
| QT_PASSPORT_NUMBER | 1.0000 | 1.0000 | 1.0000 | 18 | 0 | 0 |
| OGG_EDUCATION | 0.9775 | 0.9775 | 0.9775 | 87 | 2 | 2 |
| QT_AGE | 0.9739 | 0.9492 | 1.0000 | 56 | 3 | 0 |
| QT_RESIDENT_NUMBER | 0.9730 | 0.9474 | 1.0000 | 18 | 1 | 0 |
| DT_BIRTH | 0.9650 | 0.9452 | 0.9857 | 69 | 4 | 1 |
| FD_MAJOR | 0.9618 | 0.9545 | 0.9692 | 63 | 3 | 2 |
| OG_DEPARTMENT | 0.9557 | 0.9327 | 0.9798 | 97 | 7 | 2 |
| PS_NAME | 0.9428 | 0.9105 | 0.9774 | 173 | 17 | 4 |
| LC_ADDRESS | 0.9394 | 0.9588 | 0.9208 | 93 | 4 | 8 |
| OG_WORKPLACE | 0.9050 | 0.9259 | 0.8850 | 100 | 8 | 13 |
| CV_POSITION | 0.8682 | 0.8358 | 0.9032 | 112 | 22 | 12 |