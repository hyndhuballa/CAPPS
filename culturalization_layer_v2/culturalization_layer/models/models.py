"""
models/models.py
Typed data models for the Culturalization Layer.
Uses Python dataclasses — lightweight, no ORM dependency needed for MVP.
"""

from dataclasses import dataclass, field
from datetime import date
from typing import List, Optional, Dict


# ---------------------------------------------------------------------------
# INPUT MODELS
# ---------------------------------------------------------------------------

@dataclass
class DetectionInput:
    """
    Represents a single detected object from the video pipeline.
    Produced by the upstream Detection Layer.
    """
    object_type: str          # e.g., "bottle", "poster", "food_package"
    detected_brand: str       # e.g., "unknown", "Pepsi", "Budweiser"
    scene_type: str           # e.g., "casual", "sports", "formal", "wedding"
    object_focus: float = 0.5  # 0.0 (background) → 1.0 (hero/foreground)


@dataclass
class UserInput:
    """
    Represents the user context passed to the Culturalization Layer.
    Age is calculated from DOB at request time.
    """
    user_id: str
    dob: date
    region: str                          # "India" for MVP
    preferences: List[str] = field(default_factory=list)
    cultural_layer_enabled: bool = True
    parent_id: Optional[str] = None


# ---------------------------------------------------------------------------
# INTERNAL MODELS
# ---------------------------------------------------------------------------

@dataclass
class UserCategory:
    """
    Derived from UserInput — computed classification used throughout the layer.
    """
    user_id: str
    age: int
    mode: str        # "kid" | "adult" | "elderly"
    region: str
    preferences: List[str]


@dataclass
class ProductAgeSuitability:
    min_age: int
    max_age: int
    modes_allowed: List[str]   # ["kid", "adult", "elderly"]


@dataclass
class Product:
    """
    Internal product representation loaded from seed data.
    """
    product_id: str
    name: str
    brand: str
    category: str                      # "bottle", "poster", "food_package"
    region_relevance: List[str]
    age_suitability: ProductAgeSuitability
    tags: List[str]
    comfort_score: int                 # 1–10, used for elderly scoring


@dataclass
class ScoredProduct:
    """
    A Product enriched with scoring breakdown — used internally before selecting winner.
    """
    product: Product
    age_match: float = 0.0
    cultural_match: float = 0.0
    context_match: float = 0.0
    pref_match: float = 0.0
    weighted_score: float = 0.0   # final weighted composite (set by scoring_service)

    @property
    def total_score(self) -> float:
        return self.weighted_score

    def score_breakdown(self) -> Dict[str, float]:
        return {
            "age_match": round(self.age_match, 4),
            "cultural_match": round(self.cultural_match, 4),
            "context_match": round(self.context_match, 4),
            "pref_match": round(self.pref_match, 4),
            "weighted_score": round(self.weighted_score, 4),
        }


# ---------------------------------------------------------------------------
# OUTPUT MODEL
# ---------------------------------------------------------------------------

@dataclass
class RecommendationOutput:
    """
    The final output of the Culturalization Layer.
    Sent downstream to the Replacement Layer.
    """
    replace: bool
    replacement_brand: Optional[str] = None
    product_id: Optional[str] = None
    score: Optional[float] = None
    reason: str = ""
    score_breakdown: Optional[Dict[str, int]] = None

    def to_dict(self) -> dict:
        return {
            "replace": self.replace,
            "replacement_brand": self.replacement_brand,
            "product_id": self.product_id,
            "score": self.score,
            "reason": self.reason,
            "score_breakdown": self.score_breakdown,
        }
