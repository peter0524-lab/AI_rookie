# entity-level 다수결 앙상블: test  (20260731_123106)

min_votes=1
data_dir=`/data/team/hwan/real/data/test_sets/synthetic`
evaluated_labels=18: `PS_NAME, LC_ADDRESS, OG_WORKPLACE, OG_DEPARTMENT, CV_POSITION, OGG_EDUCATION, QT_MOBILE, QT_PHONE, QT_RESIDENT_NUMBER, QT_DRIVER_NUMBER, QT_PLATE_NUMBER, QT_ACCOUNT_NUMBER, QT_CARD_NUMBER, TMI_EMAIL, QT_PASSPORT_NUMBER, QT_AGE, DT_BIRTH, FD_MAJOR`
excluded_labels=1: `QT_ALIEN_NUMBER`
excluded_gold_entities=0  excluded_predicted_entities=0

| Entity Micro F1 | **0.9706** |
| Precision | 0.9904 |
| Recall | 0.9516 |
| TP | 6190 | FP | 60 | FN | 315 |

| 레이블 | F1 | P | R | TP | FP | FN |
|--------|-----|---|---|----|----|-----|
| OGG_EDUCATION | 1.0000 | 1.0000 | 1.0000 | 216 | 0 | 0 |
| QT_MOBILE | 1.0000 | 1.0000 | 1.0000 | 377 | 0 | 0 |
| QT_RESIDENT_NUMBER | 1.0000 | 1.0000 | 1.0000 | 185 | 0 | 0 |
| QT_DRIVER_NUMBER | 1.0000 | 1.0000 | 1.0000 | 7 | 0 | 0 |
| QT_CARD_NUMBER | 1.0000 | 1.0000 | 1.0000 | 93 | 0 | 0 |
| QT_PASSPORT_NUMBER | 1.0000 | 1.0000 | 1.0000 | 2 | 0 | 0 |
| QT_PHONE | 0.9973 | 0.9947 | 1.0000 | 186 | 1 | 0 |
| QT_ACCOUNT_NUMBER | 0.9890 | 0.9944 | 0.9835 | 179 | 1 | 3 |
| LC_ADDRESS | 0.9818 | 1.0000 | 0.9643 | 270 | 0 | 10 |
| PS_NAME | 0.9733 | 0.9997 | 0.9483 | 3171 | 1 | 173 |
| DT_BIRTH | 0.9731 | 0.9792 | 0.9671 | 235 | 5 | 8 |
| FD_MAJOR | 0.9712 | 0.9440 | 1.0000 | 118 | 7 | 0 |
| QT_PLATE_NUMBER | 0.9600 | 0.9231 | 1.0000 | 12 | 1 | 0 |
| TMI_EMAIL | 0.9590 | 1.0000 | 0.9211 | 257 | 0 | 22 |
| OG_WORKPLACE | 0.9563 | 0.9710 | 0.9419 | 503 | 15 | 31 |
| QT_AGE | 0.9321 | 0.9279 | 0.9364 | 103 | 8 | 7 |
| CV_POSITION | 0.8949 | 0.8984 | 0.8915 | 115 | 13 | 14 |
| OG_DEPARTMENT | 0.8541 | 0.9527 | 0.7740 | 161 | 8 | 47 |