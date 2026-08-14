# entity-level 다수결 앙상블: test  (20260717_111537)

min_votes=1
data_dir=`/data/team/hwan/real/data/test_sets/kdpii`
evaluated_labels=19: `PS_NAME, LC_ADDRESS, OG_WORKPLACE, OG_DEPARTMENT, CV_POSITION, OGG_EDUCATION, QT_MOBILE, QT_PHONE, QT_RESIDENT_NUMBER, QT_ALIEN_NUMBER, QT_DRIVER_NUMBER, QT_PLATE_NUMBER, QT_ACCOUNT_NUMBER, QT_CARD_NUMBER, TMI_EMAIL, QT_PASSPORT_NUMBER, QT_AGE, DT_BIRTH, FD_MAJOR`
excluded_labels=0: `-`
excluded_gold_entities=0  excluded_predicted_entities=0

| Entity Micro F1 | **0.9678** |
| Precision | 0.9678 |
| Recall | 0.9678 |
| TP | 1324 | FP | 44 | FN | 44 |

| 레이블 | F1 | P | R | TP | FP | FN |
|--------|-----|---|---|----|----|-----|
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
| OG_DEPARTMENT | 0.9899 | 0.9899 | 0.9899 | 98 | 1 | 1 |
| OGG_EDUCATION | 0.9775 | 0.9775 | 0.9775 | 87 | 2 | 2 |
| FD_MAJOR | 0.9771 | 0.9697 | 0.9846 | 64 | 2 | 1 |
| PS_NAME | 0.9611 | 0.9454 | 0.9774 | 173 | 10 | 4 |
| QT_AGE | 0.9558 | 0.9474 | 0.9643 | 54 | 3 | 2 |
| QT_ALIEN_NUMBER | 0.9474 | 0.9000 | 1.0000 | 9 | 1 | 0 |
| LC_ADDRESS | 0.9314 | 0.9223 | 0.9406 | 95 | 8 | 6 |
| CV_POSITION | 0.9069 | 0.9106 | 0.9032 | 112 | 11 | 12 |
| OG_WORKPLACE | 0.9023 | 0.9510 | 0.8584 | 97 | 5 | 16 |