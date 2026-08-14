# entity-level 다수결 앙상블: test  (20260717_065935)

min_votes=2
data_dir=`/data/team/hwan/real/data/test_sets/kdpii`
evaluated_labels=18: `PS_NAME, LC_ADDRESS, OG_WORKPLACE, OG_DEPARTMENT, CV_POSITION, OGG_EDUCATION, QT_MOBILE, QT_PHONE, QT_RESIDENT_NUMBER, QT_DRIVER_NUMBER, QT_PLATE_NUMBER, QT_ACCOUNT_NUMBER, QT_CARD_NUMBER, TMI_EMAIL, QT_PASSPORT_NUMBER, QT_AGE, DT_BIRTH, FD_MAJOR`
excluded_labels=1: `QT_ALIEN_NUMBER`
excluded_gold_entities=9  excluded_predicted_entities=9

| Entity Micro F1 | **0.9635** |
| Precision | 0.9744 |
| Recall | 0.9529 |
| TP | 1295 | FP | 34 | FN | 64 |

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
| OG_DEPARTMENT | 0.9898 | 1.0000 | 0.9798 | 97 | 0 | 2 |
| DT_BIRTH | 0.9857 | 0.9857 | 0.9857 | 69 | 1 | 1 |
| OGG_EDUCATION | 0.9773 | 0.9885 | 0.9663 | 86 | 1 | 3 |
| FD_MAJOR | 0.9771 | 0.9697 | 0.9846 | 64 | 2 | 1 |
| QT_AGE | 0.9739 | 0.9492 | 1.0000 | 56 | 3 | 0 |
| PS_NAME | 0.9459 | 0.9540 | 0.9379 | 166 | 8 | 11 |
| LC_ADDRESS | 0.9300 | 0.9394 | 0.9208 | 93 | 6 | 8 |
| CV_POSITION | 0.9143 | 0.9256 | 0.9032 | 112 | 9 | 12 |
| OG_WORKPLACE | 0.8529 | 0.9560 | 0.7699 | 87 | 4 | 26 |