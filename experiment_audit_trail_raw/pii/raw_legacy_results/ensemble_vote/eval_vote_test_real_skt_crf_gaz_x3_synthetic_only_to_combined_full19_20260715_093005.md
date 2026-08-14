# entity-level 다수결 앙상블: test  (20260715_093005)

min_votes=2
data_dir=`/data/team/hwan/real/data/test_sets/combined`
evaluated_labels=19: `PS_NAME, LC_ADDRESS, OG_WORKPLACE, OG_DEPARTMENT, CV_POSITION, OGG_EDUCATION, QT_MOBILE, QT_PHONE, QT_RESIDENT_NUMBER, QT_ALIEN_NUMBER, QT_DRIVER_NUMBER, QT_PLATE_NUMBER, QT_ACCOUNT_NUMBER, QT_CARD_NUMBER, TMI_EMAIL, QT_PASSPORT_NUMBER, QT_AGE, DT_BIRTH, FD_MAJOR`
excluded_labels=0: `-`
excluded_gold_entities=0  excluded_predicted_entities=0

| Entity Micro F1 | **0.9305** |
| Precision | 0.9739 |
| Recall | 0.8909 |
| TP | 7014 | FP | 188 | FN | 859 |

| 레이블 | F1 | P | R | TP | FP | FN |
|--------|-----|---|---|----|----|-----|
| QT_MOBILE | 1.0000 | 1.0000 | 1.0000 | 432 | 0 | 0 |
| QT_ALIEN_NUMBER | 1.0000 | 1.0000 | 1.0000 | 9 | 0 | 0 |
| QT_DRIVER_NUMBER | 1.0000 | 1.0000 | 1.0000 | 24 | 0 | 0 |
| QT_PASSPORT_NUMBER | 1.0000 | 1.0000 | 1.0000 | 20 | 0 | 0 |
| QT_PHONE | 0.9941 | 0.9961 | 0.9922 | 253 | 1 | 2 |
| QT_RESIDENT_NUMBER | 0.9902 | 0.9807 | 1.0000 | 203 | 4 | 0 |
| TMI_EMAIL | 0.9700 | 1.0000 | 0.9417 | 339 | 0 | 21 |
| PS_NAME | 0.9593 | 0.9793 | 0.9401 | 3310 | 70 | 211 |
| DT_BIRTH | 0.9491 | 0.9764 | 0.9233 | 289 | 7 | 24 |
| QT_ACCOUNT_NUMBER | 0.9326 | 0.9055 | 0.9614 | 249 | 26 | 10 |
| OGG_EDUCATION | 0.9174 | 0.9886 | 0.8557 | 261 | 3 | 44 |
| QT_CARD_NUMBER | 0.9143 | 1.0000 | 0.8421 | 144 | 0 | 27 |
| OG_WORKPLACE | 0.8977 | 0.9218 | 0.8748 | 566 | 48 | 81 |
| LC_ADDRESS | 0.8529 | 0.9965 | 0.7454 | 284 | 1 | 97 |
| OG_DEPARTMENT | 0.8427 | 0.9912 | 0.7329 | 225 | 2 | 82 |
| QT_AGE | 0.8202 | 0.8609 | 0.7831 | 130 | 21 | 36 |
| FD_MAJOR | 0.7841 | 1.0000 | 0.6448 | 118 | 0 | 65 |
| CV_POSITION | 0.6937 | 0.9648 | 0.5415 | 137 | 5 | 116 |
| QT_PLATE_NUMBER | 0.4941 | 1.0000 | 0.3281 | 21 | 0 | 43 |