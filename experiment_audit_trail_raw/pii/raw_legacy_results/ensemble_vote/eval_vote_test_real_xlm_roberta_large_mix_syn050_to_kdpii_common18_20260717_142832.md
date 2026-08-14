# entity-level 다수결 앙상블: test  (20260717_142832)

min_votes=1
data_dir=`/data/team/hwan/real/data/test_sets/kdpii`
evaluated_labels=18: `PS_NAME, LC_ADDRESS, OG_WORKPLACE, OG_DEPARTMENT, CV_POSITION, OGG_EDUCATION, QT_MOBILE, QT_PHONE, QT_RESIDENT_NUMBER, QT_DRIVER_NUMBER, QT_PLATE_NUMBER, QT_ACCOUNT_NUMBER, QT_CARD_NUMBER, TMI_EMAIL, QT_PASSPORT_NUMBER, QT_AGE, DT_BIRTH, FD_MAJOR`
excluded_labels=1: `QT_ALIEN_NUMBER`
excluded_gold_entities=9  excluded_predicted_entities=9

| Entity Micro F1 | **0.9590** |
| Precision | 0.9622 |
| Recall | 0.9558 |
| TP | 1299 | FP | 51 | FN | 60 |

| 레이블 | F1 | P | R | TP | FP | FN |
|--------|-----|---|---|----|----|-----|
| QT_PHONE | 1.0000 | 1.0000 | 1.0000 | 69 | 0 | 0 |
| QT_RESIDENT_NUMBER | 1.0000 | 1.0000 | 1.0000 | 18 | 0 | 0 |
| QT_DRIVER_NUMBER | 1.0000 | 1.0000 | 1.0000 | 17 | 0 | 0 |
| QT_PLATE_NUMBER | 1.0000 | 1.0000 | 1.0000 | 52 | 0 | 0 |
| QT_CARD_NUMBER | 1.0000 | 1.0000 | 1.0000 | 78 | 0 | 0 |
| TMI_EMAIL | 1.0000 | 1.0000 | 1.0000 | 81 | 0 | 0 |
| QT_PASSPORT_NUMBER | 1.0000 | 1.0000 | 1.0000 | 18 | 0 | 0 |
| QT_ACCOUNT_NUMBER | 0.9935 | 0.9872 | 1.0000 | 77 | 1 | 0 |
| QT_MOBILE | 0.9908 | 1.0000 | 0.9818 | 54 | 0 | 1 |
| OG_DEPARTMENT | 0.9899 | 0.9899 | 0.9899 | 98 | 1 | 1 |
| DT_BIRTH | 0.9859 | 0.9722 | 1.0000 | 70 | 2 | 0 |
| OGG_EDUCATION | 0.9770 | 1.0000 | 0.9551 | 85 | 0 | 4 |
| QT_AGE | 0.9735 | 0.9649 | 0.9821 | 55 | 2 | 1 |
| FD_MAJOR | 0.9385 | 0.9385 | 0.9385 | 61 | 4 | 4 |
| PS_NAME | 0.9307 | 0.9130 | 0.9492 | 168 | 16 | 9 |
| LC_ADDRESS | 0.9300 | 0.9394 | 0.9208 | 93 | 6 | 8 |
| CV_POSITION | 0.9008 | 0.9237 | 0.8790 | 109 | 9 | 15 |
| OG_WORKPLACE | 0.8767 | 0.9057 | 0.8496 | 96 | 10 | 17 |