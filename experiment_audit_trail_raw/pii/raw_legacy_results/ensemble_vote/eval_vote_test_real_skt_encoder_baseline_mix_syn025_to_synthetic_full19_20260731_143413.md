# entity-level 다수결 앙상블: test  (20260731_143413)

min_votes=1
data_dir=`/data/team/hwan/real/data/test_sets/synthetic`
evaluated_labels=19: `PS_NAME, LC_ADDRESS, OG_WORKPLACE, OG_DEPARTMENT, CV_POSITION, OGG_EDUCATION, QT_MOBILE, QT_PHONE, QT_RESIDENT_NUMBER, QT_ALIEN_NUMBER, QT_DRIVER_NUMBER, QT_PLATE_NUMBER, QT_ACCOUNT_NUMBER, QT_CARD_NUMBER, TMI_EMAIL, QT_PASSPORT_NUMBER, QT_AGE, DT_BIRTH, FD_MAJOR`
excluded_labels=0: `-`
excluded_gold_entities=0  excluded_predicted_entities=0

| Entity Micro F1 | **0.9606** |
| Precision | 0.9837 |
| Recall | 0.9385 |
| TP | 6105 | FP | 101 | FN | 400 |

| 레이블 | F1 | P | R | TP | FP | FN |
|--------|-----|---|---|----|----|-----|
| OGG_EDUCATION | 1.0000 | 1.0000 | 1.0000 | 216 | 0 | 0 |
| QT_MOBILE | 1.0000 | 1.0000 | 1.0000 | 377 | 0 | 0 |
| QT_RESIDENT_NUMBER | 1.0000 | 1.0000 | 1.0000 | 185 | 0 | 0 |
| QT_DRIVER_NUMBER | 1.0000 | 1.0000 | 1.0000 | 7 | 0 | 0 |
| QT_CARD_NUMBER | 1.0000 | 1.0000 | 1.0000 | 93 | 0 | 0 |
| QT_PASSPORT_NUMBER | 1.0000 | 1.0000 | 1.0000 | 2 | 0 | 0 |
| QT_PHONE | 0.9947 | 0.9894 | 1.0000 | 186 | 2 | 0 |
| QT_ACCOUNT_NUMBER | 0.9861 | 0.9944 | 0.9780 | 178 | 1 | 4 |
| LC_ADDRESS | 0.9764 | 0.9926 | 0.9607 | 269 | 2 | 11 |
| DT_BIRTH | 0.9731 | 0.9792 | 0.9671 | 235 | 5 | 8 |
| PS_NAME | 0.9672 | 0.9971 | 0.9390 | 3140 | 9 | 204 |
| FD_MAJOR | 0.9587 | 0.9355 | 0.9831 | 116 | 8 | 2 |
| TMI_EMAIL | 0.9570 | 1.0000 | 0.9176 | 256 | 0 | 23 |
| OG_WORKPLACE | 0.9337 | 0.9586 | 0.9101 | 486 | 21 | 48 |
| QT_PLATE_NUMBER | 0.9231 | 0.8571 | 1.0000 | 12 | 2 | 0 |
| QT_AGE | 0.8839 | 0.8684 | 0.9000 | 99 | 15 | 11 |
| OG_DEPARTMENT | 0.8011 | 0.9085 | 0.7163 | 149 | 15 | 59 |
| CV_POSITION | 0.7952 | 0.8250 | 0.7674 | 99 | 21 | 30 |
| QT_ALIEN_NUMBER | 0.0000 | 0.0000 | 0.0000 | 0 | 0 | 0 |