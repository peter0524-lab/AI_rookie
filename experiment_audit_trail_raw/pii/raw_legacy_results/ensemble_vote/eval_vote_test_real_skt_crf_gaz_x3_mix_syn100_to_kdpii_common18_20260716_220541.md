# entity-level 다수결 앙상블: test  (20260716_220541)

min_votes=2
data_dir=`/data/team/hwan/real/data/test_sets/kdpii`
evaluated_labels=18: `PS_NAME, LC_ADDRESS, OG_WORKPLACE, OG_DEPARTMENT, CV_POSITION, OGG_EDUCATION, QT_MOBILE, QT_PHONE, QT_RESIDENT_NUMBER, QT_DRIVER_NUMBER, QT_PLATE_NUMBER, QT_ACCOUNT_NUMBER, QT_CARD_NUMBER, TMI_EMAIL, QT_PASSPORT_NUMBER, QT_AGE, DT_BIRTH, FD_MAJOR`
excluded_labels=1: `QT_ALIEN_NUMBER`
excluded_gold_entities=9  excluded_predicted_entities=9

| Entity Micro F1 | **0.9594** |
| Precision | 0.9706 |
| Recall | 0.9485 |
| TP | 1289 | FP | 39 | FN | 70 |

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
| OG_DEPARTMENT | 0.9950 | 0.9900 | 1.0000 | 99 | 1 | 0 |
| OGG_EDUCATION | 0.9829 | 1.0000 | 0.9663 | 86 | 0 | 3 |
| DT_BIRTH | 0.9784 | 0.9855 | 0.9714 | 68 | 1 | 2 |
| FD_MAJOR | 0.9771 | 0.9697 | 0.9846 | 64 | 2 | 1 |
| QT_AGE | 0.9649 | 0.9483 | 0.9821 | 55 | 3 | 1 |
| LC_ADDRESS | 0.9293 | 0.9485 | 0.9109 | 92 | 5 | 9 |
| PS_NAME | 0.9231 | 0.9310 | 0.9153 | 162 | 12 | 15 |
| CV_POSITION | 0.9098 | 0.9250 | 0.8952 | 111 | 9 | 13 |
| OG_WORKPLACE | 0.8447 | 0.9355 | 0.7699 | 87 | 6 | 26 |