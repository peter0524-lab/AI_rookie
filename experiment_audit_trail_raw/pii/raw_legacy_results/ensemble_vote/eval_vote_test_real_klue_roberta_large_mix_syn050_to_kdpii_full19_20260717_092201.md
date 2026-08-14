# entity-level 다수결 앙상블: test  (20260717_092201)

min_votes=1
data_dir=`/data/team/hwan/real/data/test_sets/kdpii`
evaluated_labels=19: `PS_NAME, LC_ADDRESS, OG_WORKPLACE, OG_DEPARTMENT, CV_POSITION, OGG_EDUCATION, QT_MOBILE, QT_PHONE, QT_RESIDENT_NUMBER, QT_ALIEN_NUMBER, QT_DRIVER_NUMBER, QT_PLATE_NUMBER, QT_ACCOUNT_NUMBER, QT_CARD_NUMBER, TMI_EMAIL, QT_PASSPORT_NUMBER, QT_AGE, DT_BIRTH, FD_MAJOR`
excluded_labels=0: `-`
excluded_gold_entities=0  excluded_predicted_entities=0

| Entity Micro F1 | **0.9603** |
| Precision | 0.9744 |
| Recall | 0.9466 |
| TP | 1295 | FP | 34 | FN | 73 |

| 레이블 | F1 | P | R | TP | FP | FN |
|--------|-----|---|---|----|----|-----|
| QT_MOBILE | 1.0000 | 1.0000 | 1.0000 | 55 | 0 | 0 |
| QT_PHONE | 1.0000 | 1.0000 | 1.0000 | 69 | 0 | 0 |
| QT_RESIDENT_NUMBER | 1.0000 | 1.0000 | 1.0000 | 18 | 0 | 0 |
| QT_ALIEN_NUMBER | 1.0000 | 1.0000 | 1.0000 | 9 | 0 | 0 |
| QT_DRIVER_NUMBER | 1.0000 | 1.0000 | 1.0000 | 17 | 0 | 0 |
| QT_PLATE_NUMBER | 1.0000 | 1.0000 | 1.0000 | 52 | 0 | 0 |
| QT_CARD_NUMBER | 1.0000 | 1.0000 | 1.0000 | 78 | 0 | 0 |
| TMI_EMAIL | 1.0000 | 1.0000 | 1.0000 | 81 | 0 | 0 |
| QT_PASSPORT_NUMBER | 1.0000 | 1.0000 | 1.0000 | 18 | 0 | 0 |
| QT_ACCOUNT_NUMBER | 0.9935 | 1.0000 | 0.9870 | 76 | 0 | 1 |
| OG_DEPARTMENT | 0.9848 | 0.9898 | 0.9798 | 97 | 1 | 2 |
| FD_MAJOR | 0.9846 | 0.9846 | 0.9846 | 64 | 1 | 1 |
| DT_BIRTH | 0.9787 | 0.9718 | 0.9857 | 69 | 2 | 1 |
| OGG_EDUCATION | 0.9659 | 0.9770 | 0.9551 | 85 | 2 | 4 |
| QT_AGE | 0.9643 | 0.9643 | 0.9643 | 54 | 2 | 2 |
| PS_NAME | 0.9526 | 0.9396 | 0.9661 | 171 | 11 | 6 |
| LC_ADDRESS | 0.9458 | 0.9412 | 0.9505 | 96 | 6 | 5 |
| CV_POSITION | 0.8870 | 0.9217 | 0.8548 | 106 | 9 | 18 |
| OG_WORKPLACE | 0.8290 | 1.0000 | 0.7080 | 80 | 0 | 33 |