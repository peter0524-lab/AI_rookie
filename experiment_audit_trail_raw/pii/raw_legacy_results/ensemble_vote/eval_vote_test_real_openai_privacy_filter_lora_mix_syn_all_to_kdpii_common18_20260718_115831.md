# entity-level 다수결 앙상블: test  (20260718_115831)

min_votes=1
data_dir=`/data/team/hwan/real/data/test_sets/kdpii`
evaluated_labels=18: `PS_NAME, LC_ADDRESS, OG_WORKPLACE, OG_DEPARTMENT, CV_POSITION, OGG_EDUCATION, QT_MOBILE, QT_PHONE, QT_RESIDENT_NUMBER, QT_DRIVER_NUMBER, QT_PLATE_NUMBER, QT_ACCOUNT_NUMBER, QT_CARD_NUMBER, TMI_EMAIL, QT_PASSPORT_NUMBER, QT_AGE, DT_BIRTH, FD_MAJOR`
excluded_labels=1: `QT_ALIEN_NUMBER`
excluded_gold_entities=9  excluded_predicted_entities=9

| Entity Micro F1 | **0.5639** |
| Precision | 0.9337 |
| Recall | 0.4040 |
| TP | 549 | FP | 39 | FN | 810 |

| 레이블 | F1 | P | R | TP | FP | FN |
|--------|-----|---|---|----|----|-----|
| QT_MOBILE | 1.0000 | 1.0000 | 1.0000 | 55 | 0 | 0 |
| QT_PHONE | 1.0000 | 1.0000 | 1.0000 | 69 | 0 | 0 |
| QT_RESIDENT_NUMBER | 1.0000 | 1.0000 | 1.0000 | 18 | 0 | 0 |
| DT_BIRTH | 0.9784 | 0.9855 | 0.9714 | 68 | 1 | 2 |
| QT_CARD_NUMBER | 0.9530 | 1.0000 | 0.9103 | 71 | 0 | 7 |
| QT_PLATE_NUMBER | 0.9505 | 0.9796 | 0.9231 | 48 | 1 | 4 |
| QT_ACCOUNT_NUMBER | 0.9078 | 1.0000 | 0.8312 | 64 | 0 | 13 |
| QT_DRIVER_NUMBER | 0.7407 | 1.0000 | 0.5882 | 10 | 0 | 7 |
| QT_AGE | 0.6118 | 0.8966 | 0.4643 | 26 | 3 | 30 |
| TMI_EMAIL | 0.5000 | 1.0000 | 0.3333 | 27 | 0 | 54 |
| PS_NAME | 0.3559 | 0.7119 | 0.2373 | 42 | 17 | 135 |
| CV_POSITION | 0.2800 | 0.8077 | 0.1694 | 21 | 5 | 103 |
| LC_ADDRESS | 0.2353 | 0.7778 | 0.1386 | 14 | 4 | 87 |
| OG_DEPARTMENT | 0.1667 | 1.0000 | 0.0909 | 9 | 0 | 90 |
| QT_PASSPORT_NUMBER | 0.1053 | 1.0000 | 0.0556 | 1 | 0 | 17 |
| FD_MAJOR | 0.0597 | 1.0000 | 0.0308 | 2 | 0 | 63 |
| OGG_EDUCATION | 0.0417 | 0.2857 | 0.0225 | 2 | 5 | 87 |
| OG_WORKPLACE | 0.0339 | 0.4000 | 0.0177 | 2 | 3 | 111 |