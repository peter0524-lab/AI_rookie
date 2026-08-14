# entity-level 다수결 앙상블: test  (20260705_073025)

min_votes=1
data_dir=`/data/team/hwan/data`
evaluated_labels=19: `PS_NAME, LC_ADDRESS, OG_WORKPLACE, OG_DEPARTMENT, CV_POSITION, OGG_EDUCATION, QT_MOBILE, QT_PHONE, QT_RESIDENT_NUMBER, QT_ALIEN_NUMBER, QT_DRIVER_NUMBER, QT_PLATE_NUMBER, QT_ACCOUNT_NUMBER, QT_CARD_NUMBER, TMI_EMAIL, QT_PASSPORT_NUMBER, QT_AGE, DT_BIRTH, FD_MAJOR`
excluded_labels=0: `-`
excluded_gold_entities=0  excluded_predicted_entities=0

| Entity Micro F1 | **0.9255** |
| Precision | 0.9542 |
| Recall | 0.8984 |
| TP | 1229 | FP | 59 | FN | 139 |

| 레이블 | F1 | P | R | TP | FP | FN |
|--------|-----|---|---|----|----|-----|
| QT_MOBILE | 1.0000 | 1.0000 | 1.0000 | 55 | 0 | 0 |
| QT_PHONE | 1.0000 | 1.0000 | 1.0000 | 69 | 0 | 0 |
| QT_RESIDENT_NUMBER | 1.0000 | 1.0000 | 1.0000 | 18 | 0 | 0 |
| QT_ALIEN_NUMBER | 1.0000 | 1.0000 | 1.0000 | 9 | 0 | 0 |
| TMI_EMAIL | 1.0000 | 1.0000 | 1.0000 | 81 | 0 | 0 |
| QT_PASSPORT_NUMBER | 1.0000 | 1.0000 | 1.0000 | 18 | 0 | 0 |
| QT_CARD_NUMBER | 0.9936 | 0.9873 | 1.0000 | 78 | 1 | 0 |
| DT_BIRTH | 0.9857 | 0.9857 | 0.9857 | 69 | 1 | 1 |
| QT_ACCOUNT_NUMBER | 0.9804 | 0.9868 | 0.9740 | 75 | 1 | 2 |
| QT_PLATE_NUMBER | 0.9709 | 0.9804 | 0.9615 | 50 | 1 | 2 |
| QT_DRIVER_NUMBER | 0.9697 | 1.0000 | 0.9412 | 16 | 0 | 1 |
| FD_MAJOR | 0.9516 | 1.0000 | 0.9077 | 59 | 0 | 6 |
| OGG_EDUCATION | 0.9419 | 0.9759 | 0.9101 | 81 | 2 | 8 |
| QT_AGE | 0.9189 | 0.9273 | 0.9107 | 51 | 4 | 5 |
| OG_DEPARTMENT | 0.9158 | 0.9560 | 0.8788 | 87 | 4 | 12 |
| PS_NAME | 0.8902 | 0.9112 | 0.8701 | 154 | 15 | 23 |
| LC_ADDRESS | 0.8629 | 0.8854 | 0.8416 | 85 | 11 | 16 |
| CV_POSITION | 0.8522 | 0.9245 | 0.7903 | 98 | 8 | 26 |
| OG_WORKPLACE | 0.7600 | 0.8736 | 0.6726 | 76 | 11 | 37 |