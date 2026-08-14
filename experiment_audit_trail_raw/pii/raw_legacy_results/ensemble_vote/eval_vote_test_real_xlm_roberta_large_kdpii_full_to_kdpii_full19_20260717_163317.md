# entity-level 다수결 앙상블: test  (20260717_163317)

min_votes=1
data_dir=`/data/team/hwan/real/data/test_sets/kdpii`
evaluated_labels=19: `PS_NAME, LC_ADDRESS, OG_WORKPLACE, OG_DEPARTMENT, CV_POSITION, OGG_EDUCATION, QT_MOBILE, QT_PHONE, QT_RESIDENT_NUMBER, QT_ALIEN_NUMBER, QT_DRIVER_NUMBER, QT_PLATE_NUMBER, QT_ACCOUNT_NUMBER, QT_CARD_NUMBER, TMI_EMAIL, QT_PASSPORT_NUMBER, QT_AGE, DT_BIRTH, FD_MAJOR`
excluded_labels=0: `-`
excluded_gold_entities=0  excluded_predicted_entities=0

| Entity Micro F1 | **0.9571** |
| Precision | 0.9596 |
| Recall | 0.9547 |
| TP | 1306 | FP | 55 | FN | 62 |

| 레이블 | F1 | P | R | TP | FP | FN |
|--------|-----|---|---|----|----|-----|
| QT_PHONE | 1.0000 | 1.0000 | 1.0000 | 69 | 0 | 0 |
| QT_RESIDENT_NUMBER | 1.0000 | 1.0000 | 1.0000 | 18 | 0 | 0 |
| QT_ALIEN_NUMBER | 1.0000 | 1.0000 | 1.0000 | 9 | 0 | 0 |
| QT_PLATE_NUMBER | 1.0000 | 1.0000 | 1.0000 | 52 | 0 | 0 |
| QT_CARD_NUMBER | 1.0000 | 1.0000 | 1.0000 | 78 | 0 | 0 |
| TMI_EMAIL | 1.0000 | 1.0000 | 1.0000 | 81 | 0 | 0 |
| QT_PASSPORT_NUMBER | 1.0000 | 1.0000 | 1.0000 | 18 | 0 | 0 |
| OG_DEPARTMENT | 0.9950 | 0.9900 | 1.0000 | 99 | 1 | 0 |
| QT_ACCOUNT_NUMBER | 0.9935 | 0.9872 | 1.0000 | 77 | 1 | 0 |
| DT_BIRTH | 0.9929 | 0.9859 | 1.0000 | 70 | 1 | 0 |
| QT_MOBILE | 0.9908 | 1.0000 | 0.9818 | 54 | 0 | 1 |
| QT_AGE | 0.9735 | 0.9649 | 0.9821 | 55 | 2 | 1 |
| OGG_EDUCATION | 0.9721 | 0.9667 | 0.9775 | 87 | 3 | 2 |
| QT_DRIVER_NUMBER | 0.9714 | 0.9444 | 1.0000 | 17 | 1 | 0 |
| FD_MAJOR | 0.9474 | 0.9265 | 0.9692 | 63 | 5 | 2 |
| PS_NAME | 0.9275 | 0.9524 | 0.9040 | 160 | 8 | 17 |
| LC_ADDRESS | 0.9109 | 0.9109 | 0.9109 | 92 | 9 | 9 |
| CV_POSITION | 0.8871 | 0.8871 | 0.8871 | 110 | 14 | 14 |
| OG_WORKPLACE | 0.8818 | 0.9065 | 0.8584 | 97 | 10 | 16 |