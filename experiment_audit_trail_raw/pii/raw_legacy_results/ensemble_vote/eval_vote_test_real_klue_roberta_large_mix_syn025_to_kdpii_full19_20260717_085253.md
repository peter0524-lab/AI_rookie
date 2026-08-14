# entity-level 다수결 앙상블: test  (20260717_085253)

min_votes=1
data_dir=`/data/team/hwan/real/data/test_sets/kdpii`
evaluated_labels=19: `PS_NAME, LC_ADDRESS, OG_WORKPLACE, OG_DEPARTMENT, CV_POSITION, OGG_EDUCATION, QT_MOBILE, QT_PHONE, QT_RESIDENT_NUMBER, QT_ALIEN_NUMBER, QT_DRIVER_NUMBER, QT_PLATE_NUMBER, QT_ACCOUNT_NUMBER, QT_CARD_NUMBER, TMI_EMAIL, QT_PASSPORT_NUMBER, QT_AGE, DT_BIRTH, FD_MAJOR`
excluded_labels=0: `-`
excluded_gold_entities=0  excluded_predicted_entities=0

| Entity Micro F1 | **0.9664** |
| Precision | 0.9657 |
| Recall | 0.9671 |
| TP | 1323 | FP | 47 | FN | 45 |

| 레이블 | F1 | P | R | TP | FP | FN |
|--------|-----|---|---|----|----|-----|
| OG_DEPARTMENT | 1.0000 | 1.0000 | 1.0000 | 99 | 0 | 0 |
| QT_MOBILE | 1.0000 | 1.0000 | 1.0000 | 55 | 0 | 0 |
| QT_PHONE | 1.0000 | 1.0000 | 1.0000 | 69 | 0 | 0 |
| QT_RESIDENT_NUMBER | 1.0000 | 1.0000 | 1.0000 | 18 | 0 | 0 |
| QT_DRIVER_NUMBER | 1.0000 | 1.0000 | 1.0000 | 17 | 0 | 0 |
| QT_PLATE_NUMBER | 1.0000 | 1.0000 | 1.0000 | 52 | 0 | 0 |
| QT_ACCOUNT_NUMBER | 1.0000 | 1.0000 | 1.0000 | 77 | 0 | 0 |
| QT_CARD_NUMBER | 1.0000 | 1.0000 | 1.0000 | 78 | 0 | 0 |
| TMI_EMAIL | 1.0000 | 1.0000 | 1.0000 | 81 | 0 | 0 |
| QT_PASSPORT_NUMBER | 1.0000 | 1.0000 | 1.0000 | 18 | 0 | 0 |
| DT_BIRTH | 0.9929 | 0.9859 | 1.0000 | 70 | 1 | 0 |
| OGG_EDUCATION | 0.9773 | 0.9885 | 0.9663 | 86 | 1 | 3 |
| FD_MAJOR | 0.9771 | 0.9697 | 0.9846 | 64 | 2 | 1 |
| QT_AGE | 0.9565 | 0.9322 | 0.9821 | 55 | 4 | 1 |
| QT_ALIEN_NUMBER | 0.9474 | 0.9000 | 1.0000 | 9 | 1 | 0 |
| LC_ADDRESS | 0.9458 | 0.9412 | 0.9505 | 96 | 6 | 5 |
| PS_NAME | 0.9448 | 0.9243 | 0.9661 | 171 | 14 | 6 |
| OG_WORKPLACE | 0.9032 | 0.9423 | 0.8673 | 98 | 6 | 15 |
| CV_POSITION | 0.8943 | 0.9016 | 0.8871 | 110 | 12 | 14 |