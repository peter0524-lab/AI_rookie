# Threshold 스윕: reg

| 방식 | valid F1 | test F1 | test P | test R |
|------|----------|---------|--------|--------|
| argmax | 0.0642 | 0.0678 | 0.0351 | 0.9839 |
| 전역 τ=0.55 | 0.9492 | 0.9563 | 0.9692 | 0.9437 |
| 라벨별 τ | 0.9538 | 0.9530 | 0.9733 | 0.9335 |

## 라벨별 최적 τ

| 라벨 | τ |
|------|---|
| PS_NAME | 0.75 |
| LC_ADDRESS | 0.55 |
| OG_WORKPLACE | 0.8 |
| OG_DEPARTMENT | 0.9 |
| CV_POSITION | 0.8 |
| OGG_EDUCATION | 0.05 |
| QT_MOBILE | 0.55 |
| QT_PHONE | 0.55 |
| QT_RESIDENT_NUMBER | 0.55 |
| QT_ALIEN_NUMBER | 0.55 |
| QT_DRIVER_NUMBER | 0.55 |
| QT_PLATE_NUMBER | 0.55 |
| QT_ACCOUNT_NUMBER | 0.55 |
| QT_CARD_NUMBER | 0.65 |
| TMI_EMAIL | 0.55 |
| QT_PASSPORT_NUMBER | 0.55 |
| QT_AGE | 0.1 |
| DT_BIRTH | 0.6 |
| FD_MAJOR | 0.1 |