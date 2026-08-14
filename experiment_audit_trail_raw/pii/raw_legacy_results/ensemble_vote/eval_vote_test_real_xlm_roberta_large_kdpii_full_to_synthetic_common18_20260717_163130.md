# entity-level 다수결 앙상블: test  (20260717_163130)

min_votes=1
data_dir=`/data/team/hwan/real/data/test_sets/synthetic`
evaluated_labels=18: `PS_NAME, LC_ADDRESS, OG_WORKPLACE, OG_DEPARTMENT, CV_POSITION, OGG_EDUCATION, QT_MOBILE, QT_PHONE, QT_RESIDENT_NUMBER, QT_DRIVER_NUMBER, QT_PLATE_NUMBER, QT_ACCOUNT_NUMBER, QT_CARD_NUMBER, TMI_EMAIL, QT_PASSPORT_NUMBER, QT_AGE, DT_BIRTH, FD_MAJOR`
excluded_labels=1: `QT_ALIEN_NUMBER`
excluded_gold_entities=0  excluded_predicted_entities=0

| Entity Micro F1 | **0.8938** |
| Precision | 0.8794 |
| Recall | 0.9087 |
| TP | 5911 | FP | 811 | FN | 594 |

| 레이블 | F1 | P | R | TP | FP | FN |
|--------|-----|---|---|----|----|-----|
| QT_PLATE_NUMBER | 1.0000 | 1.0000 | 1.0000 | 12 | 0 | 0 |
| QT_MOBILE | 0.9934 | 0.9869 | 1.0000 | 377 | 5 | 0 |
| QT_CARD_NUMBER | 0.9841 | 0.9688 | 1.0000 | 93 | 3 | 0 |
| OGG_EDUCATION | 0.9838 | 0.9860 | 0.9815 | 212 | 3 | 4 |
| QT_PHONE | 0.9738 | 0.9490 | 1.0000 | 186 | 10 | 0 |
| QT_RESIDENT_NUMBER | 0.9610 | 0.9250 | 1.0000 | 185 | 15 | 0 |
| LC_ADDRESS | 0.9439 | 0.9276 | 0.9607 | 269 | 21 | 11 |
| PS_NAME | 0.9373 | 0.9764 | 0.9013 | 3014 | 73 | 330 |
| TMI_EMAIL | 0.9186 | 1.0000 | 0.8495 | 237 | 0 | 42 |
| QT_ACCOUNT_NUMBER | 0.8923 | 0.8365 | 0.9560 | 174 | 34 | 8 |
| QT_AGE | 0.8734 | 0.8403 | 0.9091 | 100 | 19 | 10 |
| OG_WORKPLACE | 0.8315 | 0.7654 | 0.9101 | 486 | 149 | 48 |
| DT_BIRTH | 0.8134 | 0.7440 | 0.8971 | 218 | 75 | 25 |
| FD_MAJOR | 0.7032 | 0.5677 | 0.9237 | 109 | 83 | 9 |
| OG_DEPARTMENT | 0.6171 | 0.5110 | 0.7788 | 162 | 155 | 46 |
| QT_PASSPORT_NUMBER | 0.5000 | 0.3333 | 1.0000 | 2 | 4 | 0 |
| QT_DRIVER_NUMBER | 0.4667 | 0.3043 | 1.0000 | 7 | 16 | 0 |
| CV_POSITION | 0.3965 | 0.3178 | 0.5271 | 68 | 146 | 61 |