# entity-level 다수결 앙상블: test  (20260731_150057)

min_votes=1
data_dir=`/data/team/hwan/real/data/test_sets/kdpii`
evaluated_labels=19: `PS_NAME, LC_ADDRESS, OG_WORKPLACE, OG_DEPARTMENT, CV_POSITION, OGG_EDUCATION, QT_MOBILE, QT_PHONE, QT_RESIDENT_NUMBER, QT_ALIEN_NUMBER, QT_DRIVER_NUMBER, QT_PLATE_NUMBER, QT_ACCOUNT_NUMBER, QT_CARD_NUMBER, TMI_EMAIL, QT_PASSPORT_NUMBER, QT_AGE, DT_BIRTH, FD_MAJOR`
excluded_labels=0: `-`
excluded_gold_entities=0  excluded_predicted_entities=0

| Entity Micro F1 | **0.9259** |
| Precision | 0.9486 |
| Recall | 0.9042 |
| TP | 1237 | FP | 67 | FN | 131 |

| 레이블 | F1 | P | R | TP | FP | FN |
|--------|-----|---|---|----|----|-----|
| QT_MOBILE | 1.0000 | 1.0000 | 1.0000 | 55 | 0 | 0 |
| QT_RESIDENT_NUMBER | 1.0000 | 1.0000 | 1.0000 | 18 | 0 | 0 |
| QT_ALIEN_NUMBER | 1.0000 | 1.0000 | 1.0000 | 9 | 0 | 0 |
| QT_DRIVER_NUMBER | 1.0000 | 1.0000 | 1.0000 | 17 | 0 | 0 |
| QT_ACCOUNT_NUMBER | 1.0000 | 1.0000 | 1.0000 | 77 | 0 | 0 |
| QT_CARD_NUMBER | 1.0000 | 1.0000 | 1.0000 | 78 | 0 | 0 |
| TMI_EMAIL | 1.0000 | 1.0000 | 1.0000 | 81 | 0 | 0 |
| QT_PASSPORT_NUMBER | 1.0000 | 1.0000 | 1.0000 | 18 | 0 | 0 |
| DT_BIRTH | 0.9929 | 0.9859 | 1.0000 | 70 | 1 | 0 |
| QT_PHONE | 0.9927 | 1.0000 | 0.9855 | 68 | 0 | 1 |
| QT_PLATE_NUMBER | 0.9811 | 0.9630 | 1.0000 | 52 | 2 | 0 |
| OG_DEPARTMENT | 0.9583 | 0.9892 | 0.9293 | 92 | 1 | 7 |
| OGG_EDUCATION | 0.9480 | 0.9762 | 0.9213 | 82 | 2 | 7 |
| FD_MAJOR | 0.9431 | 1.0000 | 0.8923 | 58 | 0 | 7 |
| QT_AGE | 0.9259 | 0.9615 | 0.8929 | 50 | 2 | 6 |
| LC_ADDRESS | 0.9026 | 0.9362 | 0.8713 | 88 | 6 | 13 |
| PS_NAME | 0.8514 | 0.8613 | 0.8418 | 149 | 24 | 28 |
| CV_POSITION | 0.8439 | 0.8850 | 0.8065 | 100 | 13 | 24 |
| OG_WORKPLACE | 0.7353 | 0.8242 | 0.6637 | 75 | 16 | 38 |