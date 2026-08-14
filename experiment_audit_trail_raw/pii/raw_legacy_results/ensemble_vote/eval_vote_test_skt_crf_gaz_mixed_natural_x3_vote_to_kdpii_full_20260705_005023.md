# entity-level 다수결 앙상블: test  (20260705_005023)

min_votes=2
data_dir=`/data/team/hwan/data`
evaluated_labels=19: `PS_NAME, LC_ADDRESS, OG_WORKPLACE, OG_DEPARTMENT, CV_POSITION, OGG_EDUCATION, QT_MOBILE, QT_PHONE, QT_RESIDENT_NUMBER, QT_ALIEN_NUMBER, QT_DRIVER_NUMBER, QT_PLATE_NUMBER, QT_ACCOUNT_NUMBER, QT_CARD_NUMBER, TMI_EMAIL, QT_PASSPORT_NUMBER, QT_AGE, DT_BIRTH, FD_MAJOR`
excluded_labels=0: `-`
excluded_gold_entities=0  excluded_predicted_entities=0

| Entity Micro F1 | **0.9676** |
| Precision | 0.9762 |
| Recall | 0.9591 |
| TP | 1312 | FP | 32 | FN | 56 |

| 레이블 | F1 | P | R | TP | FP | FN |
|--------|-----|---|---|----|----|-----|
| OG_DEPARTMENT | 1.0000 | 1.0000 | 1.0000 | 99 | 0 | 0 |
| QT_MOBILE | 1.0000 | 1.0000 | 1.0000 | 55 | 0 | 0 |
| QT_PHONE | 1.0000 | 1.0000 | 1.0000 | 69 | 0 | 0 |
| QT_RESIDENT_NUMBER | 1.0000 | 1.0000 | 1.0000 | 18 | 0 | 0 |
| QT_ALIEN_NUMBER | 1.0000 | 1.0000 | 1.0000 | 9 | 0 | 0 |
| QT_DRIVER_NUMBER | 1.0000 | 1.0000 | 1.0000 | 17 | 0 | 0 |
| QT_PLATE_NUMBER | 1.0000 | 1.0000 | 1.0000 | 52 | 0 | 0 |
| QT_ACCOUNT_NUMBER | 1.0000 | 1.0000 | 1.0000 | 77 | 0 | 0 |
| TMI_EMAIL | 1.0000 | 1.0000 | 1.0000 | 81 | 0 | 0 |
| QT_PASSPORT_NUMBER | 1.0000 | 1.0000 | 1.0000 | 18 | 0 | 0 |
| QT_CARD_NUMBER | 0.9935 | 1.0000 | 0.9872 | 77 | 0 | 1 |
| OGG_EDUCATION | 0.9886 | 1.0000 | 0.9775 | 87 | 0 | 2 |
| DT_BIRTH | 0.9857 | 0.9857 | 0.9857 | 69 | 1 | 1 |
| FD_MAJOR | 0.9692 | 0.9692 | 0.9692 | 63 | 2 | 2 |
| QT_AGE | 0.9649 | 0.9483 | 0.9821 | 55 | 3 | 1 |
| PS_NAME | 0.9577 | 0.9551 | 0.9605 | 170 | 8 | 7 |
| LC_ADDRESS | 0.9254 | 0.9300 | 0.9208 | 93 | 7 | 8 |
| CV_POSITION | 0.9218 | 0.9412 | 0.9032 | 112 | 7 | 12 |
| OG_WORKPLACE | 0.8750 | 0.9579 | 0.8053 | 91 | 4 | 22 |