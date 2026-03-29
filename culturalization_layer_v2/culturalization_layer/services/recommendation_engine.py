"""
services/recommendation_engine.py
Top-level orchestrator of the Culturalization Layer — SINGLE ENTRY POINT.

6-Step Pipeline:
  1. Gate checks       (toggle, emotional scene)
  2. Object importance (block high-importance objects)
  3. Region validation (unsupported regions get a clear error)
  4. User + products   (classify user, filter valid candidates)
  5. Weighted scoring  (4-dimension score + tiebreaking)
  6. Winner + output   (structured result with full explainability)
"""

from models.models import DetectionInput, UserInput, RecommendationOutput
from services.user_service import get_user_category
from services.product_service import get_valid_products
from services.scoring_service import score_products, build_score_explanation
from services.context_filter import is_object_important, object_importance_reason
from data.seed_data import EMOTIONAL_SCENES, SUPPORTED_REGIONS


def recommend_product(
    detection: DetectionInput,
    user_input: UserInput,
) -> RecommendationOutput:
    """
    Main pipeline function.

    Args:
        detection:  DetectionInput from the upstream Detection Layer.
        user_input: UserInput with DOB, region, preferences.

    Returns:
        RecommendationOutput — replace=True/False + full supporting info.
    """

    # ------------------------------------------------------------------
    # STEP 1a: GATE — Cultural layer toggled off
    # ------------------------------------------------------------------
    if not user_input.cultural_layer_enabled:
        return RecommendationOutput(
            replace=False,
            reason="cultural_layer_disabled",
        )

    # ------------------------------------------------------------------
    # STEP 1b: GATE — Emotional scene (narrative integrity)
    # ------------------------------------------------------------------
    if detection.scene_type.lower() in EMOTIONAL_SCENES:
        return RecommendationOutput(
            replace=False,
            reason=(
                f"emotional_scene_protected: '{detection.scene_type}' scene "
                "preserves narrative integrity"
            ),
        )

    # ------------------------------------------------------------------
    # STEP 2: OBJECT IMPORTANCE FILTER
    # ------------------------------------------------------------------
    blocked, importance_score = is_object_important(detection)
    if blocked:
        return RecommendationOutput(
            replace=False,
            reason=object_importance_reason(importance_score, detection.scene_type),
        )

    # ------------------------------------------------------------------
    # STEP 3: REGION VALIDATION
    # ------------------------------------------------------------------
    if user_input.region not in SUPPORTED_REGIONS:
        return RecommendationOutput(
            replace=False,
            reason=(
                f"unsupported_region: '{user_input.region}' has no cultural "
                "mapping yet. Supported regions: "
                + ", ".join(sorted(SUPPORTED_REGIONS))
            ),
        )

    # ------------------------------------------------------------------
    # STEP 4: USER CLASSIFICATION + PRODUCT FILTERING
    # ------------------------------------------------------------------
    user_category = get_user_category(user_input)

    valid_products = get_valid_products(
        object_type=detection.object_type,
        user=user_category,
    )

    if not valid_products:
        return RecommendationOutput(
            replace=False,
            reason=(
                f"no_safe_product_found: no products match "
                f"object_type='{detection.object_type}' for "
                f"mode='{user_category.mode}' in region='{user_input.region}'"
            ),
        )

    # ------------------------------------------------------------------
    # STEP 5: WEIGHTED SCORING (tiebreaking included inside score_products)
    # ------------------------------------------------------------------
    scored_products = score_products(valid_products, user_category, detection)
    winner = scored_products[0]

    # ------------------------------------------------------------------
    # STEP 6: PACKAGE RESULT WITH EXPLAINABILITY
    # ------------------------------------------------------------------
    reason = build_score_explanation(
        sp=winner,
        detected_brand=detection.detected_brand,
        user_mode=user_category.mode,
    )

    return RecommendationOutput(
        replace=True,
        replacement_brand=winner.product.brand,
        product_id=winner.product.product_id,
        score=winner.weighted_score,
        reason=reason,
        score_breakdown=winner.score_breakdown(),
    )
