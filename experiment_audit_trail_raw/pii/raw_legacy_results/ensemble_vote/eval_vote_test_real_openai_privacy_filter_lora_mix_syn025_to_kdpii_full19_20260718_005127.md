# entity-level 다수결 앙상블: test  (20260718_005127)

min_votes=1
data_dir=`/data/team/hwan/real/data/test_sets/kdpii`
evaluated_labels=19: `PS_NAME, LC_ADDRESS, OG_WORKPLACE, OG_DEPARTMENT, CV_POSITION, OGG_EDUCATION, QT_MOBILE, QT_PHONE, QT_RESIDENT_NUMBER, QT_ALIEN_NUMBER, QT_DRIVER_NUMBER, QT_PLATE_NUMBER, QT_ACCOUNT_NUMBER, QT_CARD_NUMBER, TMI_EMAIL, QT_PASSPORT_NUMBER, QT_AGE, DT_BIRTH, FD_MAJOR`
excluded_labels=0: `-`
excluded_gold_entities=0  excluded_predicted_entities=0

| Entity Micro F1 | **0.5758** |
| Precision | 0.9072 |
| Recall | 0.4218 |
| TP | 577 | FP | 59 | FN | 791 |

| 레이블 | F1 | P | R | TP | FP | FN |
|--------|-----|---|---|----|----|-----|
| QT_MOBILE | 1.0000 | 1.0000 | 1.0000 | 55 | 0 | 0 |
| QT_PHONE | 1.0000 | 1.0000 | 1.0000 | 69 | 0 | 0 |
| QT_RESIDENT_NUMBER | 1.0000 | 1.0000 | 1.0000 | 18 | 0 | 0 |
| QT_ALIEN_NUMBER | 1.0000 | 1.0000 | 1.0000 | 9 | 0 | 0 |
| DT_BIRTH | 0.9787 | 0.9718 | 0.9857 | 69 | 2 | 1 |
| QT_PLATE_NUMBER | 0.9600 | 1.0000 | 0.9231 | 48 | 0 | 4 |
| QT_CARD_NUMBER | 0.9530 | 1.0000 | 0.9103 | 71 | 0 | 7 |
| QT_ACCOUNT_NUMBER | 0.9000 | 1.0000 | 0.8182 | 63 | 0 | 14 |
| QT_DRIVER_NUMBER | 0.6923 | 1.0000 | 0.5294 | 9 | 0 | 8 |
| QT_AGE | 0.6739 | 0.8611 | 0.5536 | 31 | 5 | 25 |
| TMI_EMAIL | 0.5000 | 1.0000 | 0.3333 | 27 | 0 | 54 |
| PS_NAME | 0.3934 | 0.7164 | 0.2712 | 48 | 19 | 129 |
| CV_POSITION | 0.2933 | 0.8462 | 0.1774 | 22 | 4 | 102 |
| LC_ADDRESS | 0.2393 | 0.8750 | 0.1386 | 14 | 2 | 87 |
| OG_DEPARTMENT | 0.1770 | 0.7143 | 0.1010 | 10 | 4 | 89 |
| OGG_EDUCATION | 0.1154 | 0.4000 | 0.0674 | 6 | 9 | 83 |
| QT_PASSPORT_NUMBER | 0.1053 | 1.0000 | 0.0556 | 1 | 0 | 17 |
| FD_MAJOR | 0.0857 | 0.6000 | 0.0462 | 3 | 2 | 62 |
| OG_WORKPLACE | 0.0620 | 0.2500 | 0.0354 | 4 | 12 | 109 |