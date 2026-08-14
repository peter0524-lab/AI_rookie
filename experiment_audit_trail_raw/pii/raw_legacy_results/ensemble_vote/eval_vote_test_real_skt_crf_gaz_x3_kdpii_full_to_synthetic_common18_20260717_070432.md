# entity-level 다수결 앙상블: test  (20260717_070432)

min_votes=2
data_dir=`/data/team/hwan/real/data/test_sets/synthetic`
evaluated_labels=18: `PS_NAME, LC_ADDRESS, OG_WORKPLACE, OG_DEPARTMENT, CV_POSITION, OGG_EDUCATION, QT_MOBILE, QT_PHONE, QT_RESIDENT_NUMBER, QT_DRIVER_NUMBER, QT_PLATE_NUMBER, QT_ACCOUNT_NUMBER, QT_CARD_NUMBER, TMI_EMAIL, QT_PASSPORT_NUMBER, QT_AGE, DT_BIRTH, FD_MAJOR`
excluded_labels=1: `QT_ALIEN_NUMBER`
excluded_gold_entities=0  excluded_predicted_entities=0

| Entity Micro F1 | **0.9073** |
| Precision | 0.9117 |
| Recall | 0.9030 |
| TP | 5874 | FP | 569 | FN | 631 |

| 레이블 | F1 | P | R | TP | FP | FN |
|--------|-----|---|---|----|----|-----|
| QT_PLATE_NUMBER | 1.0000 | 1.0000 | 1.0000 | 12 | 0 | 0 |
| QT_PASSPORT_NUMBER | 1.0000 | 1.0000 | 1.0000 | 2 | 0 | 0 |
| QT_MOBILE | 0.9987 | 0.9974 | 1.0000 | 377 | 1 | 0 |
| OGG_EDUCATION | 0.9953 | 1.0000 | 0.9907 | 214 | 0 | 2 |
| QT_RESIDENT_NUMBER | 0.9946 | 0.9893 | 1.0000 | 185 | 2 | 0 |
| QT_CARD_NUMBER | 0.9738 | 0.9490 | 1.0000 | 93 | 5 | 0 |
| QT_ACCOUNT_NUMBER | 0.9695 | 0.9777 | 0.9615 | 175 | 4 | 7 |
| TMI_EMAIL | 0.9590 | 1.0000 | 0.9211 | 257 | 0 | 22 |
| LC_ADDRESS | 0.9541 | 0.9441 | 0.9643 | 270 | 16 | 10 |
| PS_NAME | 0.9471 | 0.9870 | 0.9103 | 3044 | 40 | 300 |
| QT_PHONE | 0.9466 | 0.8986 | 1.0000 | 186 | 21 | 0 |
| QT_AGE | 0.8230 | 0.8017 | 0.8455 | 93 | 23 | 17 |
| OG_WORKPLACE | 0.7874 | 0.7389 | 0.8427 | 450 | 159 | 84 |
| DT_BIRTH | 0.7854 | 0.7348 | 0.8436 | 205 | 74 | 38 |
| OG_DEPARTMENT | 0.6393 | 0.5804 | 0.7115 | 148 | 107 | 60 |
| FD_MAJOR | 0.6300 | 0.5548 | 0.7288 | 86 | 69 | 32 |
| CV_POSITION | 0.5957 | 0.6604 | 0.5426 | 70 | 36 | 59 |
| QT_DRIVER_NUMBER | 0.5385 | 0.3684 | 1.0000 | 7 | 12 | 0 |