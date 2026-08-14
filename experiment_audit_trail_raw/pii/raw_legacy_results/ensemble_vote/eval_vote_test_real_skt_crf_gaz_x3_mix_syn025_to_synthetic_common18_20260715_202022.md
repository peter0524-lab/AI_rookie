# entity-level 다수결 앙상블: test  (20260715_202022)

min_votes=2
data_dir=`/data/team/hwan/real/data/test_sets/synthetic`
evaluated_labels=18: `PS_NAME, LC_ADDRESS, OG_WORKPLACE, OG_DEPARTMENT, CV_POSITION, OGG_EDUCATION, QT_MOBILE, QT_PHONE, QT_RESIDENT_NUMBER, QT_DRIVER_NUMBER, QT_PLATE_NUMBER, QT_ACCOUNT_NUMBER, QT_CARD_NUMBER, TMI_EMAIL, QT_PASSPORT_NUMBER, QT_AGE, DT_BIRTH, FD_MAJOR`
excluded_labels=1: `QT_ALIEN_NUMBER`
excluded_gold_entities=0  excluded_predicted_entities=0

| Entity Micro F1 | **0.9732** |
| Precision | 0.9942 |
| Recall | 0.9530 |
| TP | 6199 | FP | 36 | FN | 306 |

| 레이블 | F1 | P | R | TP | FP | FN |
|--------|-----|---|---|----|----|-----|
| OGG_EDUCATION | 1.0000 | 1.0000 | 1.0000 | 216 | 0 | 0 |
| QT_MOBILE | 1.0000 | 1.0000 | 1.0000 | 377 | 0 | 0 |
| QT_RESIDENT_NUMBER | 1.0000 | 1.0000 | 1.0000 | 185 | 0 | 0 |
| QT_DRIVER_NUMBER | 1.0000 | 1.0000 | 1.0000 | 7 | 0 | 0 |
| QT_PLATE_NUMBER | 1.0000 | 1.0000 | 1.0000 | 12 | 0 | 0 |
| QT_CARD_NUMBER | 1.0000 | 1.0000 | 1.0000 | 93 | 0 | 0 |
| QT_PASSPORT_NUMBER | 1.0000 | 1.0000 | 1.0000 | 2 | 0 | 0 |
| QT_PHONE | 0.9947 | 0.9894 | 1.0000 | 186 | 2 | 0 |
| QT_ACCOUNT_NUMBER | 0.9917 | 1.0000 | 0.9835 | 179 | 0 | 3 |
| FD_MAJOR | 0.9915 | 1.0000 | 0.9831 | 116 | 0 | 2 |
| LC_ADDRESS | 0.9764 | 0.9926 | 0.9607 | 269 | 2 | 11 |
| DT_BIRTH | 0.9752 | 0.9793 | 0.9712 | 236 | 5 | 7 |
| PS_NAME | 0.9709 | 0.9991 | 0.9444 | 3158 | 3 | 186 |
| OG_WORKPLACE | 0.9671 | 1.0000 | 0.9363 | 500 | 0 | 34 |
| TMI_EMAIL | 0.9590 | 1.0000 | 0.9211 | 257 | 0 | 22 |
| CV_POSITION | 0.9323 | 0.9590 | 0.9070 | 117 | 5 | 12 |
| OG_DEPARTMENT | 0.9266 | 0.9786 | 0.8798 | 183 | 4 | 25 |
| QT_AGE | 0.9177 | 0.8760 | 0.9636 | 106 | 15 | 4 |