# entity-level 다수결 앙상블: test  (20260718_050919)

min_votes=1
data_dir=`/data/team/hwan/real/data/test_sets/synthetic`
evaluated_labels=18: `PS_NAME, LC_ADDRESS, OG_WORKPLACE, OG_DEPARTMENT, CV_POSITION, OGG_EDUCATION, QT_MOBILE, QT_PHONE, QT_RESIDENT_NUMBER, QT_DRIVER_NUMBER, QT_PLATE_NUMBER, QT_ACCOUNT_NUMBER, QT_CARD_NUMBER, TMI_EMAIL, QT_PASSPORT_NUMBER, QT_AGE, DT_BIRTH, FD_MAJOR`
excluded_labels=1: `QT_ALIEN_NUMBER`
excluded_gold_entities=0  excluded_predicted_entities=1

| Entity Micro F1 | **0.5796** |
| Precision | 0.9799 |
| Recall | 0.4115 |
| TP | 2677 | FP | 55 | FN | 3828 |

| 레이블 | F1 | P | R | TP | FP | FN |
|--------|-----|---|---|----|----|-----|
| QT_MOBILE | 1.0000 | 1.0000 | 1.0000 | 377 | 0 | 0 |
| QT_RESIDENT_NUMBER | 1.0000 | 1.0000 | 1.0000 | 185 | 0 | 0 |
| QT_DRIVER_NUMBER | 1.0000 | 1.0000 | 1.0000 | 7 | 0 | 0 |
| QT_PLATE_NUMBER | 1.0000 | 1.0000 | 1.0000 | 12 | 0 | 0 |
| QT_CARD_NUMBER | 1.0000 | 1.0000 | 1.0000 | 93 | 0 | 0 |
| QT_PHONE | 0.9973 | 0.9947 | 1.0000 | 186 | 1 | 0 |
| QT_ACCOUNT_NUMBER | 0.9861 | 1.0000 | 0.9725 | 177 | 0 | 5 |
| DT_BIRTH | 0.9710 | 0.9791 | 0.9630 | 234 | 5 | 9 |
| QT_AGE | 0.8676 | 0.8716 | 0.8636 | 95 | 14 | 15 |
| PS_NAME | 0.5479 | 0.9830 | 0.3798 | 1270 | 22 | 2074 |
| OGG_EDUCATION | 0.2140 | 0.9630 | 0.1204 | 26 | 1 | 190 |
| TMI_EMAIL | 0.0557 | 1.0000 | 0.0287 | 8 | 0 | 271 |
| FD_MAJOR | 0.0496 | 1.0000 | 0.0254 | 3 | 0 | 115 |
| OG_DEPARTMENT | 0.0189 | 0.5000 | 0.0096 | 2 | 2 | 206 |
| OG_WORKPLACE | 0.0074 | 0.2222 | 0.0037 | 2 | 7 | 532 |
| LC_ADDRESS | 0.0000 | 0.0000 | 0.0000 | 0 | 2 | 280 |
| CV_POSITION | 0.0000 | 0.0000 | 0.0000 | 0 | 1 | 129 |
| QT_PASSPORT_NUMBER | 0.0000 | 0.0000 | 0.0000 | 0 | 0 | 2 |