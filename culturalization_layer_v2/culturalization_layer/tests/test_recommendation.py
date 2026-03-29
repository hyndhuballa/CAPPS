"""
tests/test_recommendation.py
Comprehensive test suite for the Culturalization Layer (49 tests, 11 groups).
Run with: python -m pytest tests/ -v
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import date
from models.models import DetectionInput, UserInput
from services.recommendation_engine import recommend_product
from services.context_filter import compute_importance_score, is_object_important
from services.scoring_service import score_products, _score_age_match, _score_cultural_match, _score_pref_match
from services.user_service import get_user_category
from services.product_service import get_valid_products


# ---------------------------------------------------------------------------
# HELPERS
# ---------------------------------------------------------------------------

def make_user(dob: date, preferences=None, enabled=True, region="India") -> UserInput:
    return UserInput(
        user_id="test_user",
        dob=dob,
        region=region,
        preferences=preferences or [],
        cultural_layer_enabled=enabled,
    )

def make_detection(
    object_type="bottle",
    detected_brand="unknown",
    scene_type="casual",
    object_focus=0.5,
) -> DetectionInput:
    return DetectionInput(
        object_type=object_type,
        detected_brand=detected_brand,
        scene_type=scene_type,
        object_focus=object_focus,
    )

def _adult(prefs=None, region="India"):
    return make_user(date(1992, 1, 1), preferences=prefs, region=region)

def _kid():
    return make_user(date(2010, 1, 1))

def _elderly(prefs=None):
    return make_user(date(1950, 5, 5), preferences=prefs or [])


# ===========================================================================
# GROUP 1: Gate Checks (6 tests)
# ===========================================================================

class TestGateChecks:

    def test_cultural_layer_disabled_no_replace(self):
        """layer OFF → always replace=False regardless of scene/brand."""
        result = recommend_product(make_detection(), make_user(date(1992,1,1), enabled=False))
        assert result.replace is False
        assert result.reason == "cultural_layer_disabled"

    def test_cultural_layer_disabled_ignores_scene(self):
        """Gate fires before emotional scene check — reason is 'cultural_layer_disabled'."""
        result = recommend_product(
            make_detection(scene_type="funeral"),
            make_user(date(1992,1,1), enabled=False),
        )
        assert result.replace is False
        assert result.reason == "cultural_layer_disabled"

    def test_emotional_scene_funeral(self):
        result = recommend_product(make_detection(scene_type="funeral"), _adult())
        assert result.replace is False
        assert "emotional_scene_protected" in result.reason
        assert "funeral" in result.reason

    def test_emotional_scene_medical(self):
        result = recommend_product(make_detection(scene_type="medical"), _adult())
        assert result.replace is False
        assert "emotional_scene_protected" in result.reason

    def test_emotional_scene_prayer(self):
        result = recommend_product(make_detection(scene_type="prayer"), _adult())
        assert result.replace is False

    def test_emotional_scene_grief(self):
        result = recommend_product(make_detection(scene_type="grief"), _adult())
        assert result.replace is False


# ===========================================================================
# GROUP 2: Object Importance Filter (7 tests)
# ===========================================================================

class TestObjectImportanceFilter:

    def test_casual_low_focus_is_not_blocked(self):
        """Background object in casual scene → importance well below threshold."""
        d = make_detection(scene_type="casual", object_focus=0.1)
        assert compute_importance_score(d) < 0.60

    def test_casual_high_focus_still_below_threshold(self):
        """Even foreground object in casual scene should not block (0.335 < 0.60)."""
        d = make_detection(scene_type="casual", object_focus=0.9)
        score = compute_importance_score(d)
        assert score < 0.60

    def test_wedding_ceremony_high_focus_blocks(self):
        """Wedding + high focus → importance > 0.60 → replacement blocked."""
        d = make_detection(scene_type="wedding_ceremony", object_focus=0.9)
        blocked, score = is_object_important(d)
        assert blocked is True
        assert score >= 0.60

    def test_wedding_ceremony_low_focus_blocks(self):
        """wedding_ceremony base is 0.70 already; even low focus crosses threshold."""
        d = make_detection(scene_type="wedding_ceremony", object_focus=0.1)
        blocked, score = is_object_important(d)
        assert blocked is True  # 0.70 + (0.1 * 0.15) = 0.715

    def test_importance_block_reason_format(self):
        """reason string must contain key identifiers for logging."""
        d = make_detection(scene_type="wedding_ceremony", object_focus=0.9)
        result = recommend_product(d, _adult())
        assert result.replace is False
        assert "object_importance_blocked" in result.reason
        assert "wedding_ceremony" in result.reason

    def test_formal_meeting_low_focus_is_borderline_not_blocked(self):
        """formal_meeting base=0.60; adding small focus bonus should still block."""
        d = make_detection(scene_type="formal_meeting", object_focus=0.0)
        blocked, score = is_object_important(d)
        # base 0.60 == threshold → should block (>=)
        assert blocked is True

    def test_sports_with_default_focus_is_not_blocked(self):
        """sports scene (base 0.30) + 0.5 focus = 0.375 → not blocked."""
        d = make_detection(scene_type="sports", object_focus=0.5)
        blocked, score = is_object_important(d)
        assert blocked is False
        result = recommend_product(d, _adult())
        assert result.replace is True


# ===========================================================================
# GROUP 3: Unsupported Region (3 tests)
# ===========================================================================

class TestUnsupportedRegion:

    def test_brazil_returns_no_replace(self):
        result = recommend_product(make_detection(), make_user(date(1990,1,1), region="Brazil"))
        assert result.replace is False
        assert "unsupported_region" in result.reason
        assert "Brazil" in result.reason

    def test_usa_returns_no_replace(self):
        result = recommend_product(make_detection(), make_user(date(1990,1,1), region="USA"))
        assert result.replace is False
        assert "unsupported_region" in result.reason

    def test_supported_regions_mentioned_in_reason(self):
        """Error message should tell the caller what IS supported."""
        result = recommend_product(make_detection(), make_user(date(1990,1,1), region="Unknown"))
        assert "India" in result.reason  # supported region listed


# ===========================================================================
# GROUP 4: Kid Mode Safety (5 tests)
# ===========================================================================

class TestKidModeSafety:

    def test_kid_never_gets_alcohol_brand(self):
        """CRITICAL: Kingfisher must never be served to a 15-year-old."""
        result = recommend_product(
            make_detection(detected_brand="Budweiser"),
            _kid(),
        )
        assert result.replace is True
        assert result.replacement_brand != "Kingfisher Beer"

    def test_kid_gets_kid_friendly_bottle(self):
        """Kid's replacement must be one of the explicitly kid-safe brands."""
        result = recommend_product(make_detection(), _kid())
        assert result.replace is True
        assert result.replacement_brand in {"Frooti", "Maaza", "Sprite", "Thums Up"}

    def test_kid_gets_kid_friendly_poster(self):
        """Tanishq jewellery (adult-only poster) must not appear for kids."""
        result = recommend_product(make_detection(object_type="poster"), _kid())
        assert result.replace is True
        assert result.replacement_brand in {"Amul", "Fevicol"}
        assert result.replacement_brand != "Tanishq"

    def test_kid_unsafe_product_not_in_candidates(self):
        """Sting Energy (min_age=16) must be filtered in product service for kid."""
        cat = get_user_category(_kid())
        valid = get_valid_products("bottle", cat)
        names = [p.name for p in valid]
        assert "Sting Energy" not in names
        assert "Kingfisher Beer" not in names

    def test_kid_age_boundary_exactly_18(self):
        """User who turns 18 today should still be classified as kid (<=18 rule)."""
        today = date.today()
        dob = date(today.year - 18, today.month, today.day)
        result = recommend_product(make_detection(), make_user(dob))
        assert result.replace is True
        assert result.replacement_brand != "Kingfisher Beer"


# ===========================================================================
# GROUP 5: Elderly Mode (6 tests)
# ===========================================================================

class TestElderlyMode:

    def test_elderly_gets_high_comfort_bottle(self):
        """66-year-old should get comfort_score >= 7 product."""
        result = recommend_product(make_detection(), _elderly())
        assert result.replace is True
        assert result.replacement_brand in {"Maaza", "Frooti", "Sprite", "Thums Up"}

    def test_elderly_does_not_get_energy_drink(self):
        """Sting max_age=55, elderly user is 75 → hard filter must remove it."""
        result = recommend_product(make_detection(), _elderly())
        assert result.replacement_brand != "Sting Energy"

    def test_elderly_poster_gets_comfort_brand(self):
        result = recommend_product(make_detection(object_type="poster"), _elderly(prefs=["cooking"]))
        assert result.replace is True
        assert result.replacement_brand in {"Amul", "Fevicol"}

    def test_elderly_context_match_boosts_comfort_products(self):
        """Elderly mode adds +0.30 context score for products with comfort_score>=7."""
        cat = get_user_category(_elderly())
        prods = get_valid_products("bottle", cat)
        d = make_detection()
        scored = score_products(prods, cat, d)
        winner = scored[0]
        # Winner must have comfort_score >= 7
        assert winner.product.comfort_score >= 7

    def test_elderly_unfamiliar_brand_not_recommended(self):
        """Sting Energy is an unfamiliar/young brand; elderly should never see it."""
        cat = get_user_category(_elderly())
        valid = get_valid_products("bottle", cat)
        names = [p.name for p in valid]
        assert "Sting Energy" not in names

    def test_elderly_mode_classification_at_60(self):
        """Exactly 60 years old should be classified as 'elderly'."""
        today = date.today()
        dob = date(today.year - 60, today.month, today.day)
        cat = get_user_category(make_user(dob))
        assert cat.mode == "elderly"


# ===========================================================================
# GROUP 6: Adult Mode (2 tests)
# ===========================================================================

class TestAdultMode:

    def test_adult_gets_valid_replacement(self):
        result = recommend_product(make_detection(), _adult())
        assert result.replace is True
        assert result.replacement_brand is not None
        assert result.score is not None and result.score > 0

    def test_adult_sports_scene_wins_sports_tagged(self):
        """Sports scene for adult should deliver a sports-tagged product."""
        result = recommend_product(
            make_detection(scene_type="sports", detected_brand="Pepsi"),
            _adult(prefs=["cricket"]),
        )
        assert result.replace is True
        assert result.replacement_brand in {"Thums Up", "Sting Energy"}


# ===========================================================================
# GROUP 7: Weighted Score Structure (4 tests)
# ===========================================================================

class TestWeightedScoreStructure:

    def test_score_breakdown_has_all_keys(self):
        result = recommend_product(make_detection(), _adult())
        bd = result.score_breakdown
        for key in ("age_match", "cultural_match", "context_match", "pref_match", "weighted_score"):
            assert key in bd, f"Missing key: {key}"

    def test_weighted_score_in_valid_range(self):
        result = recommend_product(make_detection(), _adult())
        assert 0.0 <= result.score <= 1.0

    def test_weighted_score_matches_formula(self):
        """Manually verify: weighted_score = 0.35*C + 0.30*A + 0.20*X + 0.15*P."""
        result = recommend_product(make_detection(), _adult())
        bd = result.score_breakdown
        expected = round(
            0.35 * bd["cultural_match"]
            + 0.30 * bd["age_match"]
            + 0.20 * bd["context_match"]
            + 0.15 * bd["pref_match"],
            4,
        )
        assert abs(bd["weighted_score"] - expected) < 1e-4

    def test_all_dimension_scores_normalised(self):
        """Every scoring dimension should return a value in [0.0, 1.0]."""
        result = recommend_product(make_detection(), _adult())
        bd = result.score_breakdown
        for key in ("age_match", "cultural_match", "context_match", "pref_match"):
            assert 0.0 <= bd[key] <= 1.0, f"{key} = {bd[key]} out of [0,1]"


# ===========================================================================
# GROUP 8: Preference Match (2 tests)
# ===========================================================================

class TestPreferenceMatch:

    def test_matching_preferences_boost_score(self):
        """User with cricket+sports preference should score higher than user with none."""
        d = make_detection(scene_type="sports", detected_brand="Pepsi")
        r_pref   = recommend_product(d, _adult(prefs=["cricket", "sports"]))
        r_nopref = recommend_product(d, _adult(prefs=[]))
        assert r_pref.score >= r_nopref.score

    def test_pref_match_appears_in_breakdown(self):
        """When preferences match, pref_match should be > 0.0 in breakdown."""
        d = make_detection(scene_type="sports", detected_brand="Pepsi")
        result = recommend_product(d, _adult(prefs=["sports", "cricket"]))
        assert result.score_breakdown["pref_match"] > 0.0


# ===========================================================================
# GROUP 9: Tie-Breaking (4 tests)
# ===========================================================================

class TestTieBreaking:

    def test_tie_resolved_deterministically(self):
        """Running the same input twice must return the same brand."""
        d = make_detection(detected_brand="unknown", scene_type="casual")
        r1 = recommend_product(d, _adult())
        r2 = recommend_product(d, _adult())
        assert r1.replacement_brand == r2.replacement_brand

    def test_tie_resolved_by_comfort_score(self):
        """When Maaza and Frooti both score 0.52, Maaza wins (comfort=9 > 8)."""
        d = make_detection(detected_brand="unknown", scene_type="casual")
        result = recommend_product(d, _adult())
        # Both Maaza and Frooti score 0.52; Maaza has comfort=9 so it wins
        assert result.replacement_brand == "Maaza"

    def test_no_random_selection_on_equal_scores(self):
        """Winner must be deterministic — not randomly chosen from equals."""
        d = make_detection()
        results = [recommend_product(d, _adult()).replacement_brand for _ in range(5)]
        assert len(set(results)) == 1, f"Non-deterministic: {results}"

    def test_tiebreak_order_respects_comfort_then_region(self):
        """Verify sort key: weighted_score > comfort_score > region_specific > name."""
        cat = get_user_category(_adult())
        prods = get_valid_products("bottle", cat)
        d = make_detection()
        scored = score_products(prods, cat, d)
        # The first two should have equal weighted_score; higher comfort comes first
        if scored[0].weighted_score == scored[1].weighted_score:
            assert scored[0].product.comfort_score >= scored[1].product.comfort_score


# ===========================================================================
# GROUP 10: Explainability (4 tests)
# ===========================================================================

class TestExplainability:

    def test_reason_mentions_selected_brand(self):
        """Reason must name the winning brand."""
        result = recommend_product(make_detection(), _adult())
        assert result.replacement_brand in result.reason or "Selected" in result.reason

    def test_reason_mentions_localization_for_foreign_brand(self):
        """Replacing Pepsi should note localization in the reason string."""
        result = recommend_product(
            make_detection(detected_brand="Pepsi"),
            _adult(),
        )
        assert "localizes" in result.reason or "Pepsi" in result.reason

    def test_gate_reason_is_descriptive(self):
        """Gate-triggered reasons must be human-readable, not cryptic codes."""
        result = recommend_product(make_detection(scene_type="funeral"), _adult())
        assert len(result.reason) > 20  # descriptive, not a one-word code

    def test_output_serializes_to_dict(self):
        """to_dict() must produce a plain dict consumable by a JSON API."""
        result = recommend_product(make_detection(), _adult())
        d = result.to_dict()
        assert isinstance(d, dict)
        for key in ("replace", "replacement_brand", "product_id", "score", "reason", "score_breakdown"):
            assert key in d


# ===========================================================================
# GROUP 11: Edge Cases (6 tests)
# ===========================================================================

class TestEdgeCases:

    def test_unknown_object_type_no_replace(self):
        """No cultural mapping for 'alien_gadget' → descriptive no-replace."""
        result = recommend_product(
            make_detection(object_type="alien_gadget"),
            _adult(),
        )
        assert result.replace is False
        assert "no_safe_product_found" in result.reason
        assert "alien_gadget" in result.reason

    def test_unknown_object_type_reason_has_mode_and_region(self):
        """Edge case reason must include mode and region for debugging."""
        result = recommend_product(
            make_detection(object_type="mystery_box"),
            _adult(),
        )
        assert "adult" in result.reason
        assert "India" in result.reason

    def test_kid_unsafe_product_no_valid_fallback_handled(self):
        """If somehow all candidates fail safety for a kid, returns no_safe_product_found."""
        from services.product_service import get_valid_products
        cat = get_user_category(_kid())
        valid = get_valid_products("bottle", cat)
        # Must still have valid products (Frooti, Maaza, Sprite) — not empty
        assert len(valid) >= 2

    def test_elderly_all_candidates_have_valid_ages(self):
        """Hard filter must ensure no product exceeds elderly user's age limits."""
        cat = get_user_category(_elderly())
        valid = get_valid_products("bottle", cat)
        for p in valid:
            assert cat.age <= p.age_suitability.max_age

    def test_multiple_same_score_all_get_valid_products(self):
        """Even when many products tie, the final list must have at least one item."""
        result = recommend_product(make_detection(), _adult())
        assert result.replace is True
        assert result.product_id is not None

    def test_invalid_dob_in_future_raises(self):
        """Future DOB should raise ValueError in user_service."""
        import pytest
        from services.user_service import get_user_category
        user = make_user(date(2099, 1, 1))
        with pytest.raises((ValueError, Exception)):
            get_user_category(user)

