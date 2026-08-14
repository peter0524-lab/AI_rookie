# entity-level 다수결 앙상블: test  (20260731_153118)

min_votes=1
data_dir=`/data/team/hwan/real/data/test_sets/synthetic`
evaluated_labels=18: `PS_NAME, LC_ADDRESS, OG_WORKPLACE, OG_DEPARTMENT, CV_POSITION, OGG_EDUCATION, QT_MOBILE, QT_PHONE, QT_RESIDENT_NUMBER, QT_DRIVER_NUMBER, QT_PLATE_NUMBER, QT_ACCOUNT_NUMBER, QT_CARD_NUMBER, TMI_EMAIL, QT_PASSPORT_NUMBER, QT_AGE, DT_BIRTH, FD_MAJOR`
excluded_labels=1: `QT_ALIEN_NUMBER`
excluded_gold_entities=0  excluded_predicted_entities=0

| Entity Micro F1 | **0.9691** |
| Precision | 0.9882 |
| Recall | 0.9507 |
| TP | 6184 | FP | 74 | FN | 321 |

| 레이블 | F1 | P | R | TP | FP | FN |
|--------|-----|---|---|----|----|-----|
| OGG_EDUCATION | 1.0000 | 1.0000 | 1.0000 | 216 | 0 | 0 |
| QT_MOBILE | 1.0000 | 1.0000 | 1.0000 | 377 | 0 | 0 |
| QT_RESIDENT_NUMBER | 1.0000 | 1.0000 | 1.0000 | 185 | 0 | 0 |
| QT_DRIVER_NUMBER | 1.0000 | 1.0000 | 1.0000 | 7 | 0 | 0 |
| QT_PASSPORT_NUMBER | 1.0000 | 1.0000 | 1.0000 | 2 | 0 | 0 |
| QT_PHONE | 0.9947 | 0.9894 | 1.0000 | 186 | 2 | 0 |
| QT_CARD_NUMBER | 0.9947 | 0.9894 | 1.0000 | 93 | 1 | 0 |
| QT_ACCOUNT_NUMBER | 0.9917 | 1.0000 | 0.9835 | 179 | 0 | 3 |
| LC_ADDRESS | 0.9765 | 0.9890 | 0.9643 | 270 | 3 | 10 |
| DT_BIRTH | 0.9731 | 0.9792 | 0.9671 | 235 | 5 | 8 |
| PS_NAME | 0.9714 | 0.9984 | 0.9459 | 3163 | 5 | 181 |
| FD_MAJOR | 0.9633 | 0.9291 | 1.0000 | 118 | 9 | 0 |
| QT_PLATE_NUMBER | 0.9600 | 0.9231 | 1.0000 | 12 | 1 | 0 |
| TMI_EMAIL | 0.9590 | 1.0000 | 0.9211 | 257 | 0 | 22 |
| OG_WORKPLACE | 0.9559 | 0.9803 | 0.9326 | 498 | 10 | 36 |
| QT_AGE | 0.9123 | 0.8814 | 0.9455 | 104 | 14 | 6 |
| CV_POSITION | 0.9048 | 0.9268 | 0.8837 | 114 | 9 | 15 |
| OG_DEPARTMENT | 0.8593 | 0.9180 | 0.8077 | 168 | 15 | 40 |