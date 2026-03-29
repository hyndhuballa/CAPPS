# Culturalization Layer

Rule-based cultural recommendation engine for a video processing pipeline.
Replaces detected objects/brands in video with age-safe, culturally relevant alternatives.

## Quick Start

```bash
# Run demo
python main.py

# Run tests
python -m pytest tests/ -v
# or without pytest:
python -m unittest discover -s tests
```

## Folder Structure

```
culturalization_layer/
├── main.py                        # Entry point + FastAPI example
├── models/
│   └── models.py                  # Typed dataclasses (input/output/internal)
├── services/
│   ├── user_service.py            # Age calc + user classification
│   ├── product_service.py         # Product loading + hard filters
│   ├── scoring_service.py         # 3-dimension scoring engine
│   └── recommendation_engine.py  # Main orchestrator (call this)
├── data/
│   └── seed_data.py               # Users, products, cultural mappings
└── tests/
    └── test_recommendation.py     # Full test suite
```

## How to Call the Layer

```python
from models.models import DetectionInput, UserInput
from services.recommendation_engine import recommend_product
from datetime import date

detection = DetectionInput(
    object_type="bottle",
    detected_brand="unknown",
    scene_type="casual"
)

user = UserInput(
    user_id="u001",
    dob=date(2010, 6, 15),
    region="India",
    preferences=["cricket"],
    cultural_layer_enabled=True
)

result = recommend_product(detection, user)
print(result.to_dict())
# → { replace: True, replacement_brand: "Frooti", score: 33, reason: "..." }
```

## Scoring Formula

```
total_score = age_match + cultural_match + context_match

age_match      (max 15): base 10 + 5 bonus for age-mode tagged product
cultural_match (max 18): +10 region-specific, +5 pref alignment, +3 localization bonus
context_match  (max 11): +5 scene boost, +3 elderly comfort, -5 formal scene penalty
```
