# entity-level 다수결 앙상블: test  (20260731_130432)

min_votes=1
data_dir=`/data/team/hwan/real/data/test_sets/combined`
evaluated_labels=18: `PS_NAME, LC_ADDRESS, OG_WORKPLACE, OG_DEPARTMENT, CV_POSITION, OGG_EDUCATION, QT_MOBILE, QT_PHONE, QT_RESIDENT_NUMBER, QT_DRIVER_NUMBER, QT_PLATE_NUMBER, QT_ACCOUNT_NUMBER, QT_CARD_NUMBER, TMI_EMAIL, QT_PASSPORT_NUMBER, QT_AGE, DT_BIRTH, FD_MAJOR`
excluded_labels=1: `QT_ALIEN_NUMBER`
excluded_gold_entities=9  excluded_predicted_entities=9

| Entity Micro F1 | **0.9597** |
| Precision | 0.9799 |
| Recall | 0.9404 |
| TP | 7395 | FP | 152 | FN | 469 |

| 레이블 | F1 | P | R | TP | FP | FN |
|--------|-----|---|---|----|----|-----|
| QT_MOBILE | 1.0000 | 1.0000 | 1.0000 | 432 | 0 | 0 |
| QT_RESIDENT_NUMBER | 1.0000 | 1.0000 | 1.0000 | 203 | 0 | 0 |
| QT_DRIVER_NUMBER | 1.0000 | 1.0000 | 1.0000 | 24 | 0 | 0 |
| QT_PASSPORT_NUMBER | 1.0000 | 1.0000 | 1.0000 | 20 | 0 | 0 |
| QT_CARD_NUMBER | 0.9971 | 0.9942 | 1.0000 | 171 | 1 | 0 |
| QT_PHONE | 0.9961 | 0.9922 | 1.0000 | 255 | 2 | 0 |
| OGG_EDUCATION | 0.9835 | 0.9900 | 0.9770 | 298 | 3 | 7 |
| QT_ACCOUNT_NUMBER | 0.9807 | 0.9807 | 0.9807 | 254 | 5 | 5 |
| DT_BIRTH | 0.9743 | 0.9806 | 0.9681 | 303 | 6 | 10 |
| QT_PLATE_NUMBER | 0.9683 | 0.9839 | 0.9531 | 61 | 1 | 3 |
| TMI_EMAIL | 0.9670 | 1.0000 | 0.9361 | 337 | 0 | 23 |
| PS_NAME | 0.9666 | 0.9922 | 0.9423 | 3318 | 26 | 203 |
| FD_MAJOR | 0.9565 | 0.9514 | 0.9617 | 176 | 9 | 7 |
| LC_ADDRESS | 0.9479 | 0.9647 | 0.9318 | 355 | 13 | 26 |
| OG_WORKPLACE | 0.9188 | 0.9675 | 0.8748 | 566 | 19 | 81 |
| QT_AGE | 0.9145 | 0.8960 | 0.9337 | 155 | 18 | 11 |
| OG_DEPARTMENT | 0.8789 | 0.9373 | 0.8274 | 254 | 17 | 53 |
| CV_POSITION | 0.8554 | 0.8694 | 0.8419 | 213 | 32 | 40 |