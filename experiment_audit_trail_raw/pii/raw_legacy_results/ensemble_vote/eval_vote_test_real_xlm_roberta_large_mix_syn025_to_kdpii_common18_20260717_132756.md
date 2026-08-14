# entity-level 다수결 앙상블: test  (20260717_132756)

min_votes=1
data_dir=`/data/team/hwan/real/data/test_sets/kdpii`
evaluated_labels=18: `PS_NAME, LC_ADDRESS, OG_WORKPLACE, OG_DEPARTMENT, CV_POSITION, OGG_EDUCATION, QT_MOBILE, QT_PHONE, QT_RESIDENT_NUMBER, QT_DRIVER_NUMBER, QT_PLATE_NUMBER, QT_ACCOUNT_NUMBER, QT_CARD_NUMBER, TMI_EMAIL, QT_PASSPORT_NUMBER, QT_AGE, DT_BIRTH, FD_MAJOR`
excluded_labels=1: `QT_ALIEN_NUMBER`
excluded_gold_entities=9  excluded_predicted_entities=9

| Entity Micro F1 | **0.9587** |
| Precision | 0.9699 |
| Recall | 0.9478 |
| TP | 1288 | FP | 40 | FN | 71 |

| 레이블 | F1 | P | R | TP | FP | FN |
|--------|-----|---|---|----|----|-----|
| QT_PHONE | 1.0000 | 1.0000 | 1.0000 | 69 | 0 | 0 |
| QT_RESIDENT_NUMBER | 1.0000 | 1.0000 | 1.0000 | 18 | 0 | 0 |
| QT_PLATE_NUMBER | 1.0000 | 1.0000 | 1.0000 | 52 | 0 | 0 |
| QT_CARD_NUMBER | 1.0000 | 1.0000 | 1.0000 | 78 | 0 | 0 |
| TMI_EMAIL | 1.0000 | 1.0000 | 1.0000 | 81 | 0 | 0 |
| QT_PASSPORT_NUMBER | 1.0000 | 1.0000 | 1.0000 | 18 | 0 | 0 |
| QT_ACCOUNT_NUMBER | 0.9935 | 0.9872 | 1.0000 | 77 | 1 | 0 |
| QT_MOBILE | 0.9908 | 1.0000 | 0.9818 | 54 | 0 | 1 |
| OG_DEPARTMENT | 0.9899 | 0.9899 | 0.9899 | 98 | 1 | 1 |
| DT_BIRTH | 0.9857 | 0.9857 | 0.9857 | 69 | 1 | 1 |
| QT_AGE | 0.9825 | 0.9655 | 1.0000 | 56 | 2 | 0 |
| OGG_EDUCATION | 0.9721 | 0.9667 | 0.9775 | 87 | 3 | 2 |
| QT_DRIVER_NUMBER | 0.9714 | 0.9444 | 1.0000 | 17 | 1 | 0 |
| PS_NAME | 0.9595 | 0.9822 | 0.9379 | 166 | 3 | 11 |
| FD_MAJOR | 0.9457 | 0.9531 | 0.9385 | 61 | 3 | 4 |
| LC_ADDRESS | 0.9020 | 0.8932 | 0.9109 | 92 | 11 | 9 |
| OG_WORKPLACE | 0.8750 | 0.9579 | 0.8053 | 91 | 4 | 22 |
| CV_POSITION | 0.8739 | 0.9123 | 0.8387 | 104 | 10 | 20 |