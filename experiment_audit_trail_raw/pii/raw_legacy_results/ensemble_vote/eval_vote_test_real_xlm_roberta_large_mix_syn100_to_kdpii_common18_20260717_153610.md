# entity-level 다수결 앙상블: test  (20260717_153610)

min_votes=1
data_dir=`/data/team/hwan/real/data/test_sets/kdpii`
evaluated_labels=18: `PS_NAME, LC_ADDRESS, OG_WORKPLACE, OG_DEPARTMENT, CV_POSITION, OGG_EDUCATION, QT_MOBILE, QT_PHONE, QT_RESIDENT_NUMBER, QT_DRIVER_NUMBER, QT_PLATE_NUMBER, QT_ACCOUNT_NUMBER, QT_CARD_NUMBER, TMI_EMAIL, QT_PASSPORT_NUMBER, QT_AGE, DT_BIRTH, FD_MAJOR`
excluded_labels=1: `QT_ALIEN_NUMBER`
excluded_gold_entities=9  excluded_predicted_entities=9

| Entity Micro F1 | **0.9593** |
| Precision | 0.9636 |
| Recall | 0.9551 |
| TP | 1298 | FP | 49 | FN | 61 |

| 레이블 | F1 | P | R | TP | FP | FN |
|--------|-----|---|---|----|----|-----|
| QT_PHONE | 1.0000 | 1.0000 | 1.0000 | 69 | 0 | 0 |
| QT_RESIDENT_NUMBER | 1.0000 | 1.0000 | 1.0000 | 18 | 0 | 0 |
| QT_DRIVER_NUMBER | 1.0000 | 1.0000 | 1.0000 | 17 | 0 | 0 |
| QT_CARD_NUMBER | 1.0000 | 1.0000 | 1.0000 | 78 | 0 | 0 |
| TMI_EMAIL | 1.0000 | 1.0000 | 1.0000 | 81 | 0 | 0 |
| QT_PASSPORT_NUMBER | 1.0000 | 1.0000 | 1.0000 | 18 | 0 | 0 |
| QT_ACCOUNT_NUMBER | 0.9935 | 0.9872 | 1.0000 | 77 | 1 | 0 |
| QT_MOBILE | 0.9908 | 1.0000 | 0.9818 | 54 | 0 | 1 |
| QT_PLATE_NUMBER | 0.9905 | 0.9811 | 1.0000 | 52 | 1 | 0 |
| OGG_EDUCATION | 0.9770 | 1.0000 | 0.9551 | 85 | 0 | 4 |
| OG_DEPARTMENT | 0.9751 | 0.9608 | 0.9899 | 98 | 4 | 1 |
| DT_BIRTH | 0.9722 | 0.9459 | 1.0000 | 70 | 4 | 0 |
| FD_MAJOR | 0.9618 | 0.9545 | 0.9692 | 63 | 3 | 2 |
| QT_AGE | 0.9565 | 0.9322 | 0.9821 | 55 | 4 | 1 |
| PS_NAME | 0.9435 | 0.9435 | 0.9435 | 167 | 10 | 10 |
| LC_ADDRESS | 0.9388 | 0.9684 | 0.9109 | 92 | 3 | 9 |
| CV_POSITION | 0.8988 | 0.9024 | 0.8952 | 111 | 12 | 13 |
| OG_WORKPLACE | 0.8732 | 0.9300 | 0.8230 | 93 | 7 | 20 |