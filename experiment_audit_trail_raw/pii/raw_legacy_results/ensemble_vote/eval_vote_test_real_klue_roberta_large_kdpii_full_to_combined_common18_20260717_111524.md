# entity-level 다수결 앙상블: test  (20260717_111524)

min_votes=1
data_dir=`/data/team/hwan/real/data/test_sets/combined`
evaluated_labels=18: `PS_NAME, LC_ADDRESS, OG_WORKPLACE, OG_DEPARTMENT, CV_POSITION, OGG_EDUCATION, QT_MOBILE, QT_PHONE, QT_RESIDENT_NUMBER, QT_DRIVER_NUMBER, QT_PLATE_NUMBER, QT_ACCOUNT_NUMBER, QT_CARD_NUMBER, TMI_EMAIL, QT_PASSPORT_NUMBER, QT_AGE, DT_BIRTH, FD_MAJOR`
excluded_labels=1: `QT_ALIEN_NUMBER`
excluded_gold_entities=9  excluded_predicted_entities=12

| Entity Micro F1 | **0.9217** |
| Precision | 0.9168 |
| Recall | 0.9266 |
| TP | 7287 | FP | 661 | FN | 577 |

| 레이블 | F1 | P | R | TP | FP | FN |
|--------|-----|---|---|----|----|-----|
| QT_DRIVER_NUMBER | 1.0000 | 1.0000 | 1.0000 | 24 | 0 | 0 |
| QT_PASSPORT_NUMBER | 1.0000 | 1.0000 | 1.0000 | 20 | 0 | 0 |
| QT_MOBILE | 0.9977 | 0.9954 | 1.0000 | 432 | 2 | 0 |
| QT_PLATE_NUMBER | 0.9922 | 0.9846 | 1.0000 | 64 | 1 | 0 |
| QT_CARD_NUMBER | 0.9913 | 0.9828 | 1.0000 | 171 | 3 | 0 |
| QT_RESIDENT_NUMBER | 0.9854 | 0.9713 | 1.0000 | 203 | 6 | 0 |
| OGG_EDUCATION | 0.9801 | 0.9933 | 0.9672 | 295 | 2 | 10 |
| TMI_EMAIL | 0.9686 | 0.9971 | 0.9417 | 339 | 1 | 21 |
| QT_PHONE | 0.9677 | 0.9375 | 1.0000 | 255 | 17 | 0 |
| PS_NAME | 0.9486 | 0.9797 | 0.9193 | 3237 | 67 | 284 |
| LC_ADDRESS | 0.9419 | 0.9264 | 0.9580 | 365 | 29 | 16 |
| QT_ACCOUNT_NUMBER | 0.9265 | 0.8842 | 0.9730 | 252 | 33 | 7 |
| FD_MAJOR | 0.8935 | 0.8515 | 0.9399 | 172 | 30 | 11 |
| QT_AGE | 0.8724 | 0.8596 | 0.8855 | 147 | 24 | 19 |
| OG_WORKPLACE | 0.8415 | 0.7789 | 0.9150 | 592 | 168 | 55 |
| DT_BIRTH | 0.8134 | 0.7480 | 0.8914 | 279 | 94 | 34 |
| CV_POSITION | 0.7576 | 0.7815 | 0.7352 | 186 | 52 | 67 |
| OG_DEPARTMENT | 0.7330 | 0.6580 | 0.8274 | 254 | 132 | 53 |