# entity-level 다수결 앙상블: test  (20260718_092541)

min_votes=1
data_dir=`/data/team/hwan/real/data/test_sets/synthetic`
evaluated_labels=19: `PS_NAME, LC_ADDRESS, OG_WORKPLACE, OG_DEPARTMENT, CV_POSITION, OGG_EDUCATION, QT_MOBILE, QT_PHONE, QT_RESIDENT_NUMBER, QT_ALIEN_NUMBER, QT_DRIVER_NUMBER, QT_PLATE_NUMBER, QT_ACCOUNT_NUMBER, QT_CARD_NUMBER, TMI_EMAIL, QT_PASSPORT_NUMBER, QT_AGE, DT_BIRTH, FD_MAJOR`
excluded_labels=0: `-`
excluded_gold_entities=0  excluded_predicted_entities=0

| Entity Micro F1 | **0.5920** |
| Precision | 0.9864 |
| Recall | 0.4229 |
| TP | 2751 | FP | 38 | FN | 3754 |

| 레이블 | F1 | P | R | TP | FP | FN |
|--------|-----|---|---|----|----|-----|
| QT_MOBILE | 1.0000 | 1.0000 | 1.0000 | 377 | 0 | 0 |
| QT_RESIDENT_NUMBER | 1.0000 | 1.0000 | 1.0000 | 185 | 0 | 0 |
| QT_DRIVER_NUMBER | 1.0000 | 1.0000 | 1.0000 | 7 | 0 | 0 |
| QT_CARD_NUMBER | 1.0000 | 1.0000 | 1.0000 | 93 | 0 | 0 |
| QT_PHONE | 0.9973 | 0.9947 | 1.0000 | 186 | 1 | 0 |
| QT_ACCOUNT_NUMBER | 0.9889 | 1.0000 | 0.9780 | 178 | 0 | 4 |
| DT_BIRTH | 0.9712 | 0.9712 | 0.9712 | 236 | 7 | 7 |
| QT_PLATE_NUMBER | 0.9600 | 0.9231 | 1.0000 | 12 | 1 | 0 |
| QT_AGE | 0.9099 | 0.9018 | 0.9182 | 101 | 11 | 9 |
| PS_NAME | 0.5648 | 0.9925 | 0.3947 | 1320 | 10 | 2024 |
| OGG_EDUCATION | 0.2560 | 0.9412 | 0.1481 | 32 | 2 | 184 |
| FD_MAJOR | 0.0656 | 1.0000 | 0.0339 | 4 | 0 | 114 |
| TMI_EMAIL | 0.0625 | 1.0000 | 0.0323 | 9 | 0 | 270 |
| OG_DEPARTMENT | 0.0282 | 0.6000 | 0.0144 | 3 | 2 | 205 |
| LC_ADDRESS | 0.0212 | 1.0000 | 0.0107 | 3 | 0 | 277 |
| OG_WORKPLACE | 0.0184 | 0.5556 | 0.0094 | 5 | 4 | 529 |
| CV_POSITION | 0.0000 | 0.0000 | 0.0000 | 0 | 0 | 129 |
| QT_ALIEN_NUMBER | 0.0000 | 0.0000 | 0.0000 | 0 | 0 | 0 |
| QT_PASSPORT_NUMBER | 0.0000 | 0.0000 | 0.0000 | 0 | 0 | 2 |