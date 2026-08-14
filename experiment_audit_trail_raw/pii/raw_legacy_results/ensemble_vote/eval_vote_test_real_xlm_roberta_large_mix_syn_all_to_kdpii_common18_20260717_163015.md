# entity-level 다수결 앙상블: test  (20260717_163015)

min_votes=1
data_dir=`/data/team/hwan/real/data/test_sets/kdpii`
evaluated_labels=18: `PS_NAME, LC_ADDRESS, OG_WORKPLACE, OG_DEPARTMENT, CV_POSITION, OGG_EDUCATION, QT_MOBILE, QT_PHONE, QT_RESIDENT_NUMBER, QT_DRIVER_NUMBER, QT_PLATE_NUMBER, QT_ACCOUNT_NUMBER, QT_CARD_NUMBER, TMI_EMAIL, QT_PASSPORT_NUMBER, QT_AGE, DT_BIRTH, FD_MAJOR`
excluded_labels=1: `QT_ALIEN_NUMBER`
excluded_gold_entities=9  excluded_predicted_entities=9

| Entity Micro F1 | **0.9503** |
| Precision | 0.9651 |
| Recall | 0.9360 |
| TP | 1272 | FP | 46 | FN | 87 |

| 레이블 | F1 | P | R | TP | FP | FN |
|--------|-----|---|---|----|----|-----|
| QT_PHONE | 1.0000 | 1.0000 | 1.0000 | 69 | 0 | 0 |
| QT_RESIDENT_NUMBER | 1.0000 | 1.0000 | 1.0000 | 18 | 0 | 0 |
| QT_DRIVER_NUMBER | 1.0000 | 1.0000 | 1.0000 | 17 | 0 | 0 |
| QT_PLATE_NUMBER | 1.0000 | 1.0000 | 1.0000 | 52 | 0 | 0 |
| QT_ACCOUNT_NUMBER | 1.0000 | 1.0000 | 1.0000 | 77 | 0 | 0 |
| QT_CARD_NUMBER | 1.0000 | 1.0000 | 1.0000 | 78 | 0 | 0 |
| TMI_EMAIL | 1.0000 | 1.0000 | 1.0000 | 81 | 0 | 0 |
| QT_PASSPORT_NUMBER | 1.0000 | 1.0000 | 1.0000 | 18 | 0 | 0 |
| QT_MOBILE | 0.9908 | 1.0000 | 0.9818 | 54 | 0 | 1 |
| OG_DEPARTMENT | 0.9848 | 0.9898 | 0.9798 | 97 | 1 | 2 |
| DT_BIRTH | 0.9784 | 0.9855 | 0.9714 | 68 | 1 | 2 |
| OGG_EDUCATION | 0.9659 | 0.9770 | 0.9551 | 85 | 2 | 4 |
| QT_AGE | 0.9655 | 0.9333 | 1.0000 | 56 | 4 | 0 |
| FD_MAJOR | 0.9466 | 0.9394 | 0.9538 | 62 | 4 | 3 |
| PS_NAME | 0.9209 | 0.9209 | 0.9209 | 163 | 14 | 14 |
| LC_ADDRESS | 0.9128 | 0.9468 | 0.8812 | 89 | 5 | 12 |
| CV_POSITION | 0.8571 | 0.8947 | 0.8226 | 102 | 12 | 22 |
| OG_WORKPLACE | 0.8515 | 0.9663 | 0.7611 | 86 | 3 | 27 |