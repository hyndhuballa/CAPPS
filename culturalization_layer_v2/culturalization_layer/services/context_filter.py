"""
services/context_filter.py
Object Importance / Context Filter — Step inserted BEFORE scoring.

Computes an importance_score for the detected object. If the score meets or
exceeds the configured threshold, the object is considered narratively
significant and should NOT be replaced (e.g., a wedding ring being proposed
with, a branded bottle used as a plot device).

Pipeline position:
  Detection → [Context Filter] → Recommendation

importance_score formula:
  base  = OBJECT_IMPORTANCE_CONFIG["scene_base_scores"].get(scene_type, default)
  bonus = object_focus × focus_weight
  importance_score = min(base + bonus, 1.0)

If importance_score >= threshold → block replacement.
"""

from models.models import DetectionInput
from data.seed_data import OBJECT_IMPORTANCE_CONFIG


def compute_importance_score(detection: DetectionInput) -> float:
    """
    Returns a float in [0.0, 1.0] representing how narratively important
    the detected object is.

    Args:
        detection: DetectionInput with scene_type and object_focus.

    Returns:
        importance_score between 0.0 and 1.0.
    """
    cfg = OBJECT_IMPORTANCE_CONFIG
    base = cfg["scene_base_scores"].get(
        detection.scene_type.lower(),
        cfg["default_base_score"],
    )
    bonus = detection.object_focus * cfg["focus_weight"]
    return min(base + bonus, 1.0)


def is_object_important(detection: DetectionInput) -> tuple[bool, float]:
    """
    Determines whether the detected object is too important to replace.

    Returns:
        (should_block: bool, importance_score: float)
        should_block=True means DO NOT replace — preserve narrative integrity.
    """
    score = compute_importance_score(detection)
    threshold = OBJECT_IMPORTANCE_CONFIG["threshold"]
    return score >= threshold, score


def object_importance_reason(importance_score: float, scene_type: str) -> str:
    """
    Builds a human-readable reason string when replacement is blocked by
    object importance.
    """
    return (
        f"object_importance_blocked: scene='{scene_type}' "
        f"importance={importance_score:.2f} >= threshold={OBJECT_IMPORTANCE_CONFIG['threshold']}"
    )
