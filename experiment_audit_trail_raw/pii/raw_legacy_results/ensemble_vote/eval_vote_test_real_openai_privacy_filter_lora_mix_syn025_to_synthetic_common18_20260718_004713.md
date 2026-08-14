# entity-level 다수결 앙상블: test  (20260718_004713)

min_votes=1
data_dir=`/data/team/hwan/real/data/test_sets/synthetic`
evaluated_labels=18: `PS_NAME, LC_ADDRESS, OG_WORKPLACE, OG_DEPARTMENT, CV_POSITION, OGG_EDUCATION, QT_MOBILE, QT_PHONE, QT_RESIDENT_NUMBER, QT_DRIVER_NUMBER, QT_PLATE_NUMBER, QT_ACCOUNT_NUMBER, QT_CARD_NUMBER, TMI_EMAIL, QT_PASSPORT_NUMBER, QT_AGE, DT_BIRTH, FD_MAJOR`
excluded_labels=1: `QT_ALIEN_NUMBER`
excluded_gold_entities=0  excluded_predicted_entities=0

| Entity Micro F1 | **0.5775** |
| Precision | 0.9780 |
| Recall | 0.4097 |
| TP | 2665 | FP | 60 | FN | 3840 |

| 레이블 | F1 | P | R | TP | FP | FN |
|--------|-----|---|---|----|----|-----|
| QT_MOBILE | 1.0000 | 1.0000 | 1.0000 | 377 | 0 | 0 |
| QT_RESIDENT_NUMBER | 1.0000 | 1.0000 | 1.0000 | 185 | 0 | 0 |
| QT_DRIVER_NUMBER | 1.0000 | 1.0000 | 1.0000 | 7 | 0 | 0 |
| QT_PLATE_NUMBER | 1.0000 | 1.0000 | 1.0000 | 12 | 0 | 0 |
| QT_CARD_NUMBER | 1.0000 | 1.0000 | 1.0000 | 93 | 0 | 0 |
| QT_PHONE | 0.9973 | 0.9947 | 1.0000 | 186 | 1 | 0 |
| QT_ACCOUNT_NUMBER | 0.9861 | 1.0000 | 0.9725 | 177 | 0 | 5 |
| DT_BIRTH | 0.9751 | 0.9833 | 0.9671 | 235 | 4 | 8 |
| QT_AGE | 0.9067 | 0.8870 | 0.9273 | 102 | 13 | 8 |
| PS_NAME | 0.5397 | 0.9888 | 0.3711 | 1241 | 14 | 2103 |
| OGG_EDUCATION | 0.2460 | 0.8611 | 0.1435 | 31 | 5 | 185 |
| TMI_EMAIL | 0.0557 | 1.0000 | 0.0287 | 8 | 0 | 271 |
| FD_MAJOR | 0.0476 | 0.3750 | 0.0254 | 3 | 5 | 115 |
| OG_DEPARTMENT | 0.0283 | 0.7500 | 0.0144 | 3 | 1 | 205 |
| CV_POSITION | 0.0152 | 0.3333 | 0.0078 | 1 | 2 | 128 |
| LC_ADDRESS | 0.0140 | 0.4000 | 0.0071 | 2 | 3 | 278 |
| OG_WORKPLACE | 0.0073 | 0.1429 | 0.0037 | 2 | 12 | 532 |
| QT_PASSPORT_NUMBER | 0.0000 | 0.0000 | 0.0000 | 0 | 0 | 2 |