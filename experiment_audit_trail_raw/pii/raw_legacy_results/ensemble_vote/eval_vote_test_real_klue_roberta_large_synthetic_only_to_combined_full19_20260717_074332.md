# entity-level 다수결 앙상블: test  (20260717_074332)

min_votes=1
data_dir=`/data/team/hwan/real/data/test_sets/combined`
evaluated_labels=19: `PS_NAME, LC_ADDRESS, OG_WORKPLACE, OG_DEPARTMENT, CV_POSITION, OGG_EDUCATION, QT_MOBILE, QT_PHONE, QT_RESIDENT_NUMBER, QT_ALIEN_NUMBER, QT_DRIVER_NUMBER, QT_PLATE_NUMBER, QT_ACCOUNT_NUMBER, QT_CARD_NUMBER, TMI_EMAIL, QT_PASSPORT_NUMBER, QT_AGE, DT_BIRTH, FD_MAJOR`
excluded_labels=0: `-`
excluded_gold_entities=0  excluded_predicted_entities=0

| Entity Micro F1 | **0.9209** |
| Precision | 0.9505 |
| Recall | 0.8931 |
| TP | 7031 | FP | 366 | FN | 842 |

| 레이블 | F1 | P | R | TP | FP | FN |
|--------|-----|---|---|----|----|-----|
| QT_MOBILE | 1.0000 | 1.0000 | 1.0000 | 432 | 0 | 0 |
| QT_ALIEN_NUMBER | 1.0000 | 1.0000 | 1.0000 | 9 | 0 | 0 |
| QT_PASSPORT_NUMBER | 1.0000 | 1.0000 | 1.0000 | 20 | 0 | 0 |
| QT_RESIDENT_NUMBER | 0.9975 | 0.9951 | 1.0000 | 203 | 1 | 0 |
| QT_PHONE | 0.9806 | 0.9693 | 0.9922 | 253 | 8 | 2 |
| PS_NAME | 0.9603 | 0.9793 | 0.9421 | 3317 | 70 | 204 |
| QT_ACCOUNT_NUMBER | 0.9304 | 0.8850 | 0.9807 | 254 | 33 | 5 |
| OGG_EDUCATION | 0.9244 | 0.9962 | 0.8623 | 263 | 1 | 42 |
| DT_BIRTH | 0.9173 | 0.8963 | 0.9393 | 294 | 34 | 19 |
| QT_CARD_NUMBER | 0.9143 | 1.0000 | 0.8421 | 144 | 0 | 27 |
| TMI_EMAIL | 0.9113 | 0.8828 | 0.9417 | 339 | 45 | 21 |
| QT_DRIVER_NUMBER | 0.8936 | 0.9130 | 0.8750 | 21 | 2 | 3 |
| OG_WORKPLACE | 0.8927 | 0.8920 | 0.8934 | 578 | 70 | 69 |
| LC_ADDRESS | 0.8331 | 0.9527 | 0.7402 | 282 | 14 | 99 |
| OG_DEPARTMENT | 0.8287 | 0.9534 | 0.7329 | 225 | 11 | 82 |
| FD_MAJOR | 0.7803 | 0.9754 | 0.6503 | 119 | 3 | 64 |
| CV_POSITION | 0.7182 | 0.9730 | 0.5692 | 144 | 4 | 109 |
| QT_AGE | 0.6817 | 0.6402 | 0.7289 | 121 | 68 | 45 |
| QT_PLATE_NUMBER | 0.3291 | 0.8667 | 0.2031 | 13 | 2 | 51 |