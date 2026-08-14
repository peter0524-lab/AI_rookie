# entity-level 다수결 앙상블: test  (20260705_050728)

min_votes=2
data_dir=`/data/team/hwan/data`
evaluated_labels=19: `PS_NAME, LC_ADDRESS, OG_WORKPLACE, OG_DEPARTMENT, CV_POSITION, OGG_EDUCATION, QT_MOBILE, QT_PHONE, QT_RESIDENT_NUMBER, QT_ALIEN_NUMBER, QT_DRIVER_NUMBER, QT_PLATE_NUMBER, QT_ACCOUNT_NUMBER, QT_CARD_NUMBER, TMI_EMAIL, QT_PASSPORT_NUMBER, QT_AGE, DT_BIRTH, FD_MAJOR`
excluded_labels=0: `-`
excluded_gold_entities=0  excluded_predicted_entities=0

| Entity Micro F1 | **0.9667** |
| Precision | 0.9685 |
| Recall | 0.9649 |
| TP | 1320 | FP | 43 | FN | 48 |

| 레이블 | F1 | P | R | TP | FP | FN |
|--------|-----|---|---|----|----|-----|
| OG_DEPARTMENT | 1.0000 | 1.0000 | 1.0000 | 99 | 0 | 0 |
| QT_MOBILE | 1.0000 | 1.0000 | 1.0000 | 55 | 0 | 0 |
| QT_RESIDENT_NUMBER | 1.0000 | 1.0000 | 1.0000 | 18 | 0 | 0 |
| QT_ALIEN_NUMBER | 1.0000 | 1.0000 | 1.0000 | 9 | 0 | 0 |
| QT_DRIVER_NUMBER | 1.0000 | 1.0000 | 1.0000 | 17 | 0 | 0 |
| QT_PLATE_NUMBER | 1.0000 | 1.0000 | 1.0000 | 52 | 0 | 0 |
| QT_ACCOUNT_NUMBER | 1.0000 | 1.0000 | 1.0000 | 77 | 0 | 0 |
| QT_CARD_NUMBER | 1.0000 | 1.0000 | 1.0000 | 78 | 0 | 0 |
| TMI_EMAIL | 1.0000 | 1.0000 | 1.0000 | 81 | 0 | 0 |
| QT_PASSPORT_NUMBER | 1.0000 | 1.0000 | 1.0000 | 18 | 0 | 0 |
| DT_BIRTH | 0.9929 | 0.9859 | 1.0000 | 70 | 1 | 0 |
| QT_PHONE | 0.9928 | 0.9857 | 1.0000 | 69 | 1 | 0 |
| OGG_EDUCATION | 0.9829 | 1.0000 | 0.9663 | 86 | 0 | 3 |
| QT_AGE | 0.9825 | 0.9655 | 1.0000 | 56 | 2 | 0 |
| FD_MAJOR | 0.9771 | 0.9697 | 0.9846 | 64 | 2 | 1 |
| PS_NAME | 0.9521 | 0.9494 | 0.9548 | 169 | 9 | 8 |
| LC_ADDRESS | 0.9458 | 0.9412 | 0.9505 | 96 | 6 | 5 |
| CV_POSITION | 0.8933 | 0.8760 | 0.9113 | 113 | 16 | 11 |
| OG_WORKPLACE | 0.8774 | 0.9394 | 0.8230 | 93 | 6 | 20 |