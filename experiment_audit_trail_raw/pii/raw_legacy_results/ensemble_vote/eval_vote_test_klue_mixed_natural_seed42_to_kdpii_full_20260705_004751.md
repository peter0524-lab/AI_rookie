# entity-level 다수결 앙상블: test  (20260705_004751)

min_votes=1
data_dir=`/data/team/hwan/data`
evaluated_labels=19: `PS_NAME, LC_ADDRESS, OG_WORKPLACE, OG_DEPARTMENT, CV_POSITION, OGG_EDUCATION, QT_MOBILE, QT_PHONE, QT_RESIDENT_NUMBER, QT_ALIEN_NUMBER, QT_DRIVER_NUMBER, QT_PLATE_NUMBER, QT_ACCOUNT_NUMBER, QT_CARD_NUMBER, TMI_EMAIL, QT_PASSPORT_NUMBER, QT_AGE, DT_BIRTH, FD_MAJOR`
excluded_labels=0: `-`
excluded_gold_entities=0  excluded_predicted_entities=0

| Entity Micro F1 | **0.9705** |
| Precision | 0.9660 |
| Recall | 0.9751 |
| TP | 1334 | FP | 47 | FN | 34 |

| 레이블 | F1 | P | R | TP | FP | FN |
|--------|-----|---|---|----|----|-----|
| OG_DEPARTMENT | 1.0000 | 1.0000 | 1.0000 | 99 | 0 | 0 |
| QT_MOBILE | 1.0000 | 1.0000 | 1.0000 | 55 | 0 | 0 |
| QT_PHONE | 1.0000 | 1.0000 | 1.0000 | 69 | 0 | 0 |
| QT_RESIDENT_NUMBER | 1.0000 | 1.0000 | 1.0000 | 18 | 0 | 0 |
| QT_ALIEN_NUMBER | 1.0000 | 1.0000 | 1.0000 | 9 | 0 | 0 |
| QT_DRIVER_NUMBER | 1.0000 | 1.0000 | 1.0000 | 17 | 0 | 0 |
| QT_ACCOUNT_NUMBER | 1.0000 | 1.0000 | 1.0000 | 77 | 0 | 0 |
| QT_CARD_NUMBER | 1.0000 | 1.0000 | 1.0000 | 78 | 0 | 0 |
| TMI_EMAIL | 1.0000 | 1.0000 | 1.0000 | 81 | 0 | 0 |
| QT_PASSPORT_NUMBER | 1.0000 | 1.0000 | 1.0000 | 18 | 0 | 0 |
| QT_PLATE_NUMBER | 0.9905 | 0.9811 | 1.0000 | 52 | 1 | 0 |
| OGG_EDUCATION | 0.9886 | 1.0000 | 0.9775 | 87 | 0 | 2 |
| DT_BIRTH | 0.9857 | 0.9857 | 0.9857 | 69 | 1 | 1 |
| FD_MAJOR | 0.9697 | 0.9552 | 0.9846 | 64 | 3 | 1 |
| PS_NAME | 0.9695 | 0.9511 | 0.9887 | 175 | 9 | 2 |
| QT_AGE | 0.9655 | 0.9333 | 1.0000 | 56 | 4 | 0 |
| LC_ADDRESS | 0.9515 | 0.9333 | 0.9703 | 98 | 7 | 3 |
| OG_WORKPLACE | 0.9067 | 0.9107 | 0.9027 | 102 | 10 | 11 |
| CV_POSITION | 0.8943 | 0.9016 | 0.8871 | 110 | 12 | 14 |