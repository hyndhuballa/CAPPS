"""
main.py
Entry point for the Culturalization Layer.

Two modes:
  1. Run as demo:  python main.py
  2. Import recommend_product in your pipeline code

In production, wrap with FastAPI (see example at bottom of file).
"""

import json
from datetime import date
from models.models import DetectionInput, UserInput
from services.recommendation_engine import recommend_product


# ---------------------------------------------------------------------------
# DEMO TEST CASES  — covers all pipeline paths and edge cases
# ---------------------------------------------------------------------------

TEST_CASES = [
    # ── Standard replacements ──────────────────────────────────────────────
    {
        "label": "Kid (15y) + casual bottle + unknown brand",
        "detection": {"object_type": "bottle", "detected_brand": "unknown",   "scene_type": "casual",   "object_focus": 0.5},
        "user":      {"user_id": "u001", "dob": date(2010, 6, 15), "region": "India", "preferences": ["animation","sports"], "cultural_layer_enabled": True},
    },
    {
        "label": "Adult (33y) + sports scene + Pepsi bottle",
        "detection": {"object_type": "bottle", "detected_brand": "Pepsi",     "scene_type": "sports",   "object_focus": 0.5},
        "user":      {"user_id": "u002", "dob": date(1992, 3, 20), "region": "India", "preferences": ["cricket","tech"],    "cultural_layer_enabled": True},
    },
    {
        "label": "Elderly (75y) + casual bottle + Coca-Cola",
        "detection": {"object_type": "bottle", "detected_brand": "Coca-Cola", "scene_type": "casual",   "object_focus": 0.5},
        "user":      {"user_id": "u003", "dob": date(1950, 11, 2), "region": "India", "preferences": ["devotional","cooking"], "cultural_layer_enabled": True},
    },
    # ── Gate checks ────────────────────────────────────────────────────────
    {
        "label": "Adult + cultural layer OFF",
        "detection": {"object_type": "bottle", "detected_brand": "unknown",   "scene_type": "casual",   "object_focus": 0.5},
        "user":      {"user_id": "u004", "dob": date(2000, 8, 10), "region": "India", "preferences": ["gaming"],   "cultural_layer_enabled": False},
    },
    {
        "label": "Adult + funeral scene (emotional protection)",
        "detection": {"object_type": "bottle", "detected_brand": "unknown",   "scene_type": "funeral",  "object_focus": 0.5},
        "user":      {"user_id": "u002", "dob": date(1992, 3, 20), "region": "India", "preferences": [],           "cultural_layer_enabled": True},
    },
    # ── Object importance ──────────────────────────────────────────────────
    {
        "label": "High-importance object: bottle in wedding (focus=0.9) → blocked",
        "detection": {"object_type": "bottle", "detected_brand": "Pepsi",     "scene_type": "wedding_ceremony", "object_focus": 0.9},
        "user":      {"user_id": "u002", "dob": date(1992, 3, 20), "region": "India", "preferences": [],           "cultural_layer_enabled": True},
    },
    {
        "label": "Low-importance object: bottle in sports (focus=0.2) → replaced",
        "detection": {"object_type": "bottle", "detected_brand": "Pepsi",     "scene_type": "sports",   "object_focus": 0.2},
        "user":      {"user_id": "u002", "dob": date(1992, 3, 20), "region": "India", "preferences": ["cricket"],  "cultural_layer_enabled": True},
    },
    # ── Poster and food_package ────────────────────────────────────────────
    {
        "label": "Kid (13y) + poster + casual",
        "detection": {"object_type": "poster",  "detected_brand": "unknown",  "scene_type": "casual",   "object_focus": 0.5},
        "user":      {"user_id": "u001", "dob": date(2012, 6, 1),  "region": "India", "preferences": ["animation"],"cultural_layer_enabled": True},
    },
    {
        "label": "Elderly (70y) + poster + casual",
        "detection": {"object_type": "poster",  "detected_brand": "unknown",  "scene_type": "casual",   "object_focus": 0.5},
        "user":      {"user_id": "u003", "dob": date(1955, 11, 2), "region": "India", "preferences": ["cooking"],  "cultural_layer_enabled": True},
    },
    # ── Edge cases ─────────────────────────────────────────────────────────
    {
        "label": "Unknown object type → no mapping",
        "detection": {"object_type": "alien_gadget", "detected_brand": "unknown", "scene_type": "casual", "object_focus": 0.5},
        "user":      {"user_id": "u002", "dob": date(1992, 3, 20), "region": "India", "preferences": [],  "cultural_layer_enabled": True},
    },
    {
        "label": "Unsupported region (Brazil) → region error",
        "detection": {"object_type": "bottle", "detected_brand": "unknown",   "scene_type": "casual",   "object_focus": 0.5},
        "user":      {"user_id": "u002", "dob": date(1992, 3, 20), "region": "Brazil","preferences": [],  "cultural_layer_enabled": True},
    },
    {
        "label": "Kid + Budweiser bottle → safe replacement (equal score tie handled)",
        "detection": {"object_type": "bottle", "detected_brand": "Budweiser", "scene_type": "casual",   "object_focus": 0.5},
        "user":      {"user_id": "u001", "dob": date(2010, 6, 15), "region": "India", "preferences": [],           "cultural_layer_enabled": True},
    },
]


def run_demo():
    sep = "=" * 72
    print(f"\n{sep}")
    print("  CULTURALIZATION LAYER — DEMO OUTPUT  (v2 — 8 improvements active)")
    print(sep)

    for i, case in enumerate(TEST_CASES, start=1):
        detection  = DetectionInput(**case["detection"])
        user_input = UserInput(**case["user"])
        result     = recommend_product(detection, user_input)
        output     = result.to_dict()

        print(f"\nTest {i:02d}: {case['label']}")
        print(f"  Input  → object: {detection.object_type} | brand: {detection.detected_brand} "
              f"| scene: {detection.scene_type} | focus: {detection.object_focus}")
        print(f"  Output → replace: {output['replace']}")
        if output["replace"]:
            print(f"           brand:     {output['replacement_brand']}")
            print(f"           score:     {output['score']}")
            print(f"           reason:    {output['reason']}")
            print(f"           breakdown: {json.dumps(output['score_breakdown'])}")
        else:
            print(f"           reason:    {output['reason']}")

    print(f"\n{sep}\n")


# ---------------------------------------------------------------------------
# FASTAPI EXAMPLE (uncomment + pip install fastapi uvicorn to run as API)
# ---------------------------------------------------------------------------
# from fastapi import FastAPI
# from pydantic import BaseModel
# from typing import List, Optional
#
# app = FastAPI(title="Culturalization Layer API")
#
# class DetectionRequest(BaseModel):
#     object_type: str
#     detected_brand: str
#     scene_type: str
#     object_focus: float = 0.5
#
# class UserRequest(BaseModel):
#     user_id: str
#     dob: str          # "YYYY-MM-DD"
#     region: str
#     preferences: List[str] = []
#     cultural_layer_enabled: bool = True
#
# @app.post("/recommend")
# def api_recommend(detection: DetectionRequest, user: UserRequest):
#     from datetime import datetime
#     user_input = UserInput(
#         user_id=user.user_id,
#         dob=datetime.strptime(user.dob, "%Y-%m-%d").date(),
#         region=user.region,
#         preferences=user.preferences,
#         cultural_layer_enabled=user.cultural_layer_enabled,
#     )
#     det = DetectionInput(**detection.dict())
#     result = recommend_product(det, user_input)
#     return result.to_dict()


if __name__ == "__main__":
    run_demo()
