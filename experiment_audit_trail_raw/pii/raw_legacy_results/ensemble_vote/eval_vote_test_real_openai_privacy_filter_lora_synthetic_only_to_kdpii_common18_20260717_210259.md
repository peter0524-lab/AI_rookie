# entity-level 다수결 앙상블: test  (20260717_210259)

min_votes=1
data_dir=`/data/team/hwan/real/data/test_sets/kdpii`
evaluated_labels=18: `PS_NAME, LC_ADDRESS, OG_WORKPLACE, OG_DEPARTMENT, CV_POSITION, OGG_EDUCATION, QT_MOBILE, QT_PHONE, QT_RESIDENT_NUMBER, QT_DRIVER_NUMBER, QT_PLATE_NUMBER, QT_ACCOUNT_NUMBER, QT_CARD_NUMBER, TMI_EMAIL, QT_PASSPORT_NUMBER, QT_AGE, DT_BIRTH, FD_MAJOR`
excluded_labels=1: `QT_ALIEN_NUMBER`
excluded_gold_entities=9  excluded_predicted_entities=9

| Entity Micro F1 | **0.4190** |
| Precision | 0.7458 |
| Recall | 0.2914 |
| TP | 396 | FP | 135 | FN | 963 |

| 레이블 | F1 | P | R | TP | FP | FN |
|--------|-----|---|---|----|----|-----|
| QT_MOBILE | 1.0000 | 1.0000 | 1.0000 | 55 | 0 | 0 |
| QT_PHONE | 0.9857 | 0.9718 | 1.0000 | 69 | 2 | 0 |
| QT_CARD_NUMBER | 0.8889 | 0.9697 | 0.8205 | 64 | 2 | 14 |
| QT_RESIDENT_NUMBER | 0.8372 | 0.7200 | 1.0000 | 18 | 7 | 0 |
| QT_ACCOUNT_NUMBER | 0.8256 | 0.7474 | 0.9221 | 71 | 24 | 6 |
| DT_BIRTH | 0.6226 | 0.9167 | 0.4714 | 33 | 3 | 37 |
| QT_DRIVER_NUMBER | 0.5641 | 0.5000 | 0.6471 | 11 | 11 | 6 |
| TMI_EMAIL | 0.4423 | 1.0000 | 0.2840 | 23 | 0 | 58 |
| PS_NAME | 0.2748 | 0.4235 | 0.2034 | 36 | 49 | 141 |
| LC_ADDRESS | 0.1636 | 1.0000 | 0.0891 | 9 | 0 | 92 |
| QT_PLATE_NUMBER | 0.1404 | 0.8000 | 0.0769 | 4 | 1 | 48 |
| QT_AGE | 0.0597 | 0.1818 | 0.0357 | 2 | 9 | 54 |
| OG_WORKPLACE | 0.0145 | 0.0400 | 0.0088 | 1 | 24 | 112 |
| OG_DEPARTMENT | 0.0000 | 0.0000 | 0.0000 | 0 | 0 | 99 |
| CV_POSITION | 0.0000 | 0.0000 | 0.0000 | 0 | 0 | 124 |
| OGG_EDUCATION | 0.0000 | 0.0000 | 0.0000 | 0 | 2 | 89 |
| QT_PASSPORT_NUMBER | 0.0000 | 0.0000 | 0.0000 | 0 | 0 | 18 |
| FD_MAJOR | 0.0000 | 0.0000 | 0.0000 | 0 | 1 | 65 |