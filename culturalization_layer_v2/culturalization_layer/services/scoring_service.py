"""
services/scoring_service.py
Weighted scoring engine for the Culturalization Layer.

WEIGHTED FORMULA:
  weighted_score = w1*cultural_match + w2*age_match + w3*context_match + w4*pref_match

WEIGHTS (all sum to 1.0):
  w1 = 0.35  cultural_match  — Primary purpose of the layer; highest priority
  w2 = 0.30  age_match       — Safety-critical; kid/elderly protection is non-negotiable
  w3 = 0.20  context_match   — Scene naturalness; improves relevance but not safety
  w4 = 0.15  pref_match      — Personalisation; nice-to-have, must not override safety
"""

from typing import List
from models.models import Product, UserCategory, ScoredProduct, DetectionInput
from data.seed_data import CULTURAL_MAPPING, FORMAL_SCENES, FOREIGN_TO_LOCAL, BRAND_TO_CATEGORY

WEIGHTS = {"cultural": 0.35, "age": 0.30, "context": 0.20, "pref": 0.15}

AGE_MODE_TAG_MAP = {
    "kid":     {"kid_friendly", "age_safe"},
    "adult":   {"adult_only", "sports", "gaming"},
    "elderly": {"comfort_food", "nostalgic", "devotional", "elderly_comfort"},
}

FOREIGN_BRANDS = {
    "unknown", "pepsi", "coca-cola", "coke", "budweiser", "heineken",
    "budlight", "corona", "mcdonalds", "mcdonald's", "kfc", "subway",
    "doritos", "pringles", "red bull", "monster", "starbucks",
    "nescafe", "nike", "adidas", "tropicana", "minute maid",
}


def _score_age_match(product: Product, user: UserCategory) -> float:
    bonus_tags = AGE_MODE_TAG_MAP.get(user.mode, set())
    bonus = 0.30 if any(tag in product.tags for tag in bonus_tags) else 0.0
    return round(0.70 + bonus, 4)


def _is_preferred_local_replacement(product: Product, detected_brand: str) -> bool:
    brand_lower = detected_brand.lower()
    if brand_lower not in BRAND_TO_CATEGORY:
        return False
    category = BRAND_TO_CATEGORY[brand_lower]
    return product.name in FOREIGN_TO_LOCAL.get(category, [])


def _score_cultural_match(product: Product, user: UserCategory, detected_brand: str) -> float:
    is_region_specific = (
        user.region in product.region_relevance and "Global" not in product.region_relevance
    )
    is_global_available = "Global" in product.region_relevance

    base = 0.50 if is_region_specific else (0.25 if is_global_available else 0.0)
    local_bonus = 0.25 if _is_preferred_local_replacement(product, detected_brand) else 0.0
    localization_bonus = 0.10 if (detected_brand.lower() in FOREIGN_BRANDS and is_region_specific) else 0.0

    return min(round(base + local_bonus + localization_bonus, 4), 1.0)


def _score_context_match(product: Product, user: UserCategory, detection: DetectionInput) -> float:
    score = 0.0
    scene = detection.scene_type.lower()
    mapping = CULTURAL_MAPPING.get(detection.object_type, {}).get(user.region, {})
    if product.product_id in mapping.get("scene_boost", {}).get(scene, []):
        score += 0.50
    if user.mode == "elderly" and product.comfort_score >= 7:
        score += 0.30
    if scene in FORMAL_SCENES and "casual_only" in product.tags:
        score -= 0.40
    return round(min(max(score, 0.0), 1.0), 4)


def _score_pref_match(product: Product, user: UserCategory) -> float:
    pref_set = set(p.lower() for p in user.preferences)
    tag_set = set(t.lower() for t in product.tags)
    overlap = len(pref_set & tag_set)
    return 0.60 if overlap >= 2 else (0.30 if overlap == 1 else 0.0)


def score_products(
    products: List[Product],
    user: UserCategory,
    detection: DetectionInput,
) -> List[ScoredProduct]:
    """
    Scores every product across all four dimensions, applies weights, and
    returns a list sorted by weighted_score descending.

    Tiebreak order (equal weighted_score):
      1. comfort_score (higher is better)
      2. Region specificity (India-specific > Global)
      3. Product name alphabetically (deterministic)
    """
    scored = []
    for product in products:
        sp = ScoredProduct(product=product)
        sp.age_match      = _score_age_match(product, user)
        sp.cultural_match = _score_cultural_match(product, user, detection.detected_brand)
        sp.context_match  = _score_context_match(product, user, detection)
        sp.pref_match     = _score_pref_match(product, user)
        sp.weighted_score = round(
            WEIGHTS["cultural"] * sp.cultural_match
            + WEIGHTS["age"]    * sp.age_match
            + WEIGHTS["context"]* sp.context_match
            + WEIGHTS["pref"]   * sp.pref_match,
            4,
        )
        scored.append(sp)

    scored.sort(
        key=lambda x: (
            x.weighted_score,
            x.product.comfort_score,
            1 if user.region in x.product.region_relevance else 0,
            [-ord(c) for c in x.product.name],   # reverse-alphabetical secondary
        ),
        reverse=True,
    )
    return scored


def build_score_explanation(sp: ScoredProduct, detected_brand: str, user_mode: str) -> str:
    """
    Natural-language explanation of why this product was selected.
    Only mentions factors that meaningfully contributed.
    """
    parts = []
    if sp.cultural_match >= 0.60:
        parts.append("strong cultural fit for India")
    elif sp.cultural_match >= 0.35:
        parts.append("good regional availability")

    if _is_preferred_local_replacement(sp.product, detected_brand):
        parts.append(f"localizes '{detected_brand}' to an Indian brand")

    if sp.age_match >= 0.90:
        parts.append(f"explicitly optimised for {user_mode} mode")
    elif sp.age_match >= 0.70:
        parts.append(f"age-safe for {user_mode}")

    if sp.context_match >= 0.50:
        parts.append("scene context match")

    if sp.pref_match >= 0.30:
        parts.append("matches user preferences")

    reason_body = ", ".join(parts) if parts else "best available match"
    return f"Selected {sp.product.name}: {reason_body}."
