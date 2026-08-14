# entity-level 다수결 앙상블: test  (20260731_121023)

min_votes=1
data_dir=`/data/team/hwan/real/data/test_sets/synthetic`
evaluated_labels=19: `PS_NAME, LC_ADDRESS, OG_WORKPLACE, OG_DEPARTMENT, CV_POSITION, OGG_EDUCATION, QT_MOBILE, QT_PHONE, QT_RESIDENT_NUMBER, QT_ALIEN_NUMBER, QT_DRIVER_NUMBER, QT_PLATE_NUMBER, QT_ACCOUNT_NUMBER, QT_CARD_NUMBER, TMI_EMAIL, QT_PASSPORT_NUMBER, QT_AGE, DT_BIRTH, FD_MAJOR`
excluded_labels=0: `-`
excluded_gold_entities=0  excluded_predicted_entities=0

| Entity Micro F1 | **0.8510** |
| Precision | 0.8164 |
| Recall | 0.8887 |
| TP | 5781 | FP | 1300 | FN | 724 |

| 레이블 | F1 | P | R | TP | FP | FN |
|--------|-----|---|---|----|----|-----|
| QT_MOBILE | 0.9974 | 0.9947 | 1.0000 | 377 | 2 | 0 |
| QT_RESIDENT_NUMBER | 0.9814 | 0.9635 | 1.0000 | 185 | 7 | 0 |
| QT_PHONE | 0.9588 | 0.9208 | 1.0000 | 186 | 16 | 0 |
| QT_CARD_NUMBER | 0.9588 | 0.9208 | 1.0000 | 93 | 8 | 0 |
| LC_ADDRESS | 0.9343 | 0.9060 | 0.9643 | 270 | 28 | 10 |
| TMI_EMAIL | 0.9298 | 0.9879 | 0.8781 | 245 | 3 | 34 |
| PS_NAME | 0.9145 | 0.9066 | 0.9225 | 3085 | 318 | 259 |
| QT_ACCOUNT_NUMBER | 0.8895 | 0.8535 | 0.9286 | 169 | 29 | 13 |
| QT_PASSPORT_NUMBER | 0.8000 | 0.6667 | 1.0000 | 2 | 1 | 0 |
| QT_DRIVER_NUMBER | 0.7778 | 0.6364 | 1.0000 | 7 | 4 | 0 |
| OGG_EDUCATION | 0.7027 | 1.0000 | 0.5417 | 117 | 0 | 99 |
| OG_WORKPLACE | 0.6900 | 0.5815 | 0.8483 | 453 | 326 | 81 |
| DT_BIRTH | 0.6667 | 0.5661 | 0.8107 | 197 | 151 | 46 |
| FD_MAJOR | 0.6457 | 0.6029 | 0.6949 | 82 | 54 | 36 |
| QT_AGE | 0.5930 | 0.6629 | 0.5364 | 59 | 30 | 51 |
| OG_DEPARTMENT | 0.5816 | 0.4607 | 0.7885 | 164 | 192 | 44 |
| CV_POSITION | 0.5799 | 0.5571 | 0.6047 | 78 | 62 | 51 |
| QT_PLATE_NUMBER | 0.2857 | 0.1667 | 1.0000 | 12 | 60 | 0 |
| QT_ALIEN_NUMBER | 0.0000 | 0.0000 | 0.0000 | 0 | 9 | 0 |