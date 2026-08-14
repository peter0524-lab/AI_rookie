# entity-level 다수결 앙상블: test  (20260717_111059)

min_votes=1
data_dir=`/data/team/hwan/real/data/test_sets/synthetic`
evaluated_labels=18: `PS_NAME, LC_ADDRESS, OG_WORKPLACE, OG_DEPARTMENT, CV_POSITION, OGG_EDUCATION, QT_MOBILE, QT_PHONE, QT_RESIDENT_NUMBER, QT_DRIVER_NUMBER, QT_PLATE_NUMBER, QT_ACCOUNT_NUMBER, QT_CARD_NUMBER, TMI_EMAIL, QT_PASSPORT_NUMBER, QT_AGE, DT_BIRTH, FD_MAJOR`
excluded_labels=1: `QT_ALIEN_NUMBER`
excluded_gold_entities=0  excluded_predicted_entities=0

| Entity Micro F1 | **0.9749** |
| Precision | 0.9925 |
| Recall | 0.9579 |
| TP | 6231 | FP | 47 | FN | 274 |

| 레이블 | F1 | P | R | TP | FP | FN |
|--------|-----|---|---|----|----|-----|
| OGG_EDUCATION | 1.0000 | 1.0000 | 1.0000 | 216 | 0 | 0 |
| QT_MOBILE | 1.0000 | 1.0000 | 1.0000 | 377 | 0 | 0 |
| QT_DRIVER_NUMBER | 1.0000 | 1.0000 | 1.0000 | 7 | 0 | 0 |
| QT_PLATE_NUMBER | 1.0000 | 1.0000 | 1.0000 | 12 | 0 | 0 |
| QT_CARD_NUMBER | 1.0000 | 1.0000 | 1.0000 | 93 | 0 | 0 |
| QT_PASSPORT_NUMBER | 1.0000 | 1.0000 | 1.0000 | 2 | 0 | 0 |
| QT_PHONE | 0.9973 | 0.9947 | 1.0000 | 186 | 1 | 0 |
| QT_RESIDENT_NUMBER | 0.9946 | 0.9893 | 1.0000 | 185 | 2 | 0 |
| QT_ACCOUNT_NUMBER | 0.9917 | 1.0000 | 0.9835 | 179 | 0 | 3 |
| FD_MAJOR | 0.9832 | 0.9750 | 0.9915 | 117 | 3 | 1 |
| LC_ADDRESS | 0.9783 | 0.9926 | 0.9643 | 270 | 2 | 10 |
| DT_BIRTH | 0.9769 | 0.9957 | 0.9588 | 233 | 1 | 10 |
| PS_NAME | 0.9733 | 0.9991 | 0.9489 | 3173 | 3 | 171 |
| OG_WORKPLACE | 0.9712 | 0.9961 | 0.9476 | 506 | 2 | 28 |
| TMI_EMAIL | 0.9609 | 1.0000 | 0.9247 | 258 | 0 | 21 |
| CV_POSITION | 0.9389 | 0.9248 | 0.9535 | 123 | 10 | 6 |
| OG_DEPARTMENT | 0.9303 | 0.9639 | 0.8990 | 187 | 7 | 21 |
| QT_AGE | 0.9185 | 0.8699 | 0.9727 | 107 | 16 | 3 |