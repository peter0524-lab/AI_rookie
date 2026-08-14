# entity-level 다수결 앙상블: test  (20260717_111237)

min_votes=1
data_dir=`/data/team/hwan/real/data/test_sets/kdpii`
evaluated_labels=19: `PS_NAME, LC_ADDRESS, OG_WORKPLACE, OG_DEPARTMENT, CV_POSITION, OGG_EDUCATION, QT_MOBILE, QT_PHONE, QT_RESIDENT_NUMBER, QT_ALIEN_NUMBER, QT_DRIVER_NUMBER, QT_PLATE_NUMBER, QT_ACCOUNT_NUMBER, QT_CARD_NUMBER, TMI_EMAIL, QT_PASSPORT_NUMBER, QT_AGE, DT_BIRTH, FD_MAJOR`
excluded_labels=0: `-`
excluded_gold_entities=0  excluded_predicted_entities=0

| Entity Micro F1 | **0.9621** |
| Precision | 0.9682 |
| Recall | 0.9561 |
| TP | 1308 | FP | 43 | FN | 60 |

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
| DT_BIRTH | 0.9857 | 0.9857 | 0.9857 | 69 | 1 | 1 |
| QT_AGE | 0.9739 | 0.9492 | 1.0000 | 56 | 3 | 0 |
| QT_RESIDENT_NUMBER | 0.9730 | 0.9474 | 1.0000 | 18 | 1 | 0 |
| PS_NAME | 0.9634 | 0.9607 | 0.9661 | 171 | 7 | 6 |
| FD_MAJOR | 0.9606 | 0.9839 | 0.9385 | 61 | 1 | 4 |
| OG_DEPARTMENT | 0.9557 | 0.9327 | 0.9798 | 97 | 7 | 2 |
| LC_ADDRESS | 0.9490 | 0.9789 | 0.9208 | 93 | 2 | 8 |
| OGG_EDUCATION | 0.9444 | 0.9341 | 0.9551 | 85 | 6 | 4 |
| CV_POSITION | 0.9016 | 0.9167 | 0.8871 | 110 | 10 | 14 |
| OG_WORKPLACE | 0.8762 | 0.9485 | 0.8142 | 92 | 5 | 21 |