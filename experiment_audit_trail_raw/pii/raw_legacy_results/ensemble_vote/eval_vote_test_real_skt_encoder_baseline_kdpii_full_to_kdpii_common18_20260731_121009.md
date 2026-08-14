# entity-level 다수결 앙상블: test  (20260731_121009)

min_votes=1
data_dir=`/data/team/hwan/real/data/test_sets/kdpii`
evaluated_labels=18: `PS_NAME, LC_ADDRESS, OG_WORKPLACE, OG_DEPARTMENT, CV_POSITION, OGG_EDUCATION, QT_MOBILE, QT_PHONE, QT_RESIDENT_NUMBER, QT_DRIVER_NUMBER, QT_PLATE_NUMBER, QT_ACCOUNT_NUMBER, QT_CARD_NUMBER, TMI_EMAIL, QT_PASSPORT_NUMBER, QT_AGE, DT_BIRTH, FD_MAJOR`
excluded_labels=1: `QT_ALIEN_NUMBER`
excluded_gold_entities=9  excluded_predicted_entities=9

| Entity Micro F1 | **0.9357** |
| Precision | 0.9506 |
| Recall | 0.9213 |
| TP | 1252 | FP | 65 | FN | 107 |

| 레이블 | F1 | P | R | TP | FP | FN |
|--------|-----|---|---|----|----|-----|
| QT_MOBILE | 1.0000 | 1.0000 | 1.0000 | 55 | 0 | 0 |
| QT_PHONE | 1.0000 | 1.0000 | 1.0000 | 69 | 0 | 0 |
| QT_RESIDENT_NUMBER | 1.0000 | 1.0000 | 1.0000 | 18 | 0 | 0 |
| TMI_EMAIL | 1.0000 | 1.0000 | 1.0000 | 81 | 0 | 0 |
| QT_PASSPORT_NUMBER | 1.0000 | 1.0000 | 1.0000 | 18 | 0 | 0 |
| QT_CARD_NUMBER | 0.9936 | 0.9873 | 1.0000 | 78 | 1 | 0 |
| QT_ACCOUNT_NUMBER | 0.9868 | 1.0000 | 0.9740 | 75 | 0 | 2 |
| QT_DRIVER_NUMBER | 0.9714 | 0.9444 | 1.0000 | 17 | 1 | 0 |
| QT_PLATE_NUMBER | 0.9709 | 0.9804 | 0.9615 | 50 | 1 | 2 |
| OG_DEPARTMENT | 0.9694 | 0.9794 | 0.9596 | 95 | 2 | 4 |
| DT_BIRTH | 0.9565 | 0.9706 | 0.9429 | 66 | 2 | 4 |
| FD_MAJOR | 0.9516 | 1.0000 | 0.9077 | 59 | 0 | 6 |
| OGG_EDUCATION | 0.9302 | 0.9639 | 0.8989 | 80 | 3 | 9 |
| QT_AGE | 0.9286 | 0.9286 | 0.9286 | 52 | 4 | 4 |
| LC_ADDRESS | 0.9208 | 0.9208 | 0.9208 | 93 | 8 | 8 |
| PS_NAME | 0.9045 | 0.8994 | 0.9096 | 161 | 18 | 16 |
| CV_POSITION | 0.8390 | 0.8839 | 0.7984 | 99 | 13 | 25 |
| OG_WORKPLACE | 0.8152 | 0.8776 | 0.7611 | 86 | 12 | 27 |