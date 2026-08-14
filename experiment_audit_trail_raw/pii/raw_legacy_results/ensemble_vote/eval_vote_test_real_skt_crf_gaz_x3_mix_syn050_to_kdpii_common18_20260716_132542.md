# entity-level 다수결 앙상블: test  (20260716_132542)

min_votes=2
data_dir=`/data/team/hwan/real/data/test_sets/kdpii`
evaluated_labels=18: `PS_NAME, LC_ADDRESS, OG_WORKPLACE, OG_DEPARTMENT, CV_POSITION, OGG_EDUCATION, QT_MOBILE, QT_PHONE, QT_RESIDENT_NUMBER, QT_DRIVER_NUMBER, QT_PLATE_NUMBER, QT_ACCOUNT_NUMBER, QT_CARD_NUMBER, TMI_EMAIL, QT_PASSPORT_NUMBER, QT_AGE, DT_BIRTH, FD_MAJOR`
excluded_labels=1: `QT_ALIEN_NUMBER`
excluded_gold_entities=9  excluded_predicted_entities=9

| Entity Micro F1 | **0.9656** |
| Precision | 0.9717 |
| Recall | 0.9595 |
| TP | 1304 | FP | 38 | FN | 55 |

| 레이블 | F1 | P | R | TP | FP | FN |
|--------|-----|---|---|----|----|-----|
| QT_MOBILE | 1.0000 | 1.0000 | 1.0000 | 55 | 0 | 0 |
| QT_PHONE | 1.0000 | 1.0000 | 1.0000 | 69 | 0 | 0 |
| QT_RESIDENT_NUMBER | 1.0000 | 1.0000 | 1.0000 | 18 | 0 | 0 |
| QT_DRIVER_NUMBER | 1.0000 | 1.0000 | 1.0000 | 17 | 0 | 0 |
| QT_PLATE_NUMBER | 1.0000 | 1.0000 | 1.0000 | 52 | 0 | 0 |
| QT_ACCOUNT_NUMBER | 1.0000 | 1.0000 | 1.0000 | 77 | 0 | 0 |
| TMI_EMAIL | 1.0000 | 1.0000 | 1.0000 | 81 | 0 | 0 |
| QT_PASSPORT_NUMBER | 1.0000 | 1.0000 | 1.0000 | 18 | 0 | 0 |
| OG_DEPARTMENT | 0.9949 | 1.0000 | 0.9899 | 98 | 0 | 1 |
| QT_CARD_NUMBER | 0.9935 | 1.0000 | 0.9872 | 77 | 0 | 1 |
| DT_BIRTH | 0.9857 | 0.9857 | 0.9857 | 69 | 1 | 1 |
| FD_MAJOR | 0.9848 | 0.9701 | 1.0000 | 65 | 2 | 0 |
| OGG_EDUCATION | 0.9831 | 0.9886 | 0.9775 | 87 | 1 | 2 |
| QT_AGE | 0.9649 | 0.9483 | 0.9821 | 55 | 3 | 1 |
| PS_NAME | 0.9444 | 0.9290 | 0.9605 | 170 | 13 | 7 |
| LC_ADDRESS | 0.9394 | 0.9588 | 0.9208 | 93 | 4 | 8 |
| CV_POSITION | 0.9061 | 0.9174 | 0.8952 | 111 | 10 | 13 |
| OG_WORKPLACE | 0.8804 | 0.9583 | 0.8142 | 92 | 4 | 21 |