"""
services/product_service.py
Responsible for:
  - Loading products from seed data into typed Product objects
  - Fetching culturally mapped candidate products for an object type + region
  - Applying hard-rule filters (age, mode, region)
"""

from typing import List, Optional
from models.models import Product, ProductAgeSuitability, UserCategory
from data.seed_data import PRODUCTS, CULTURAL_MAPPING


# ---------------------------------------------------------------------------
# PRODUCT LOADER
# ---------------------------------------------------------------------------

def load_all_products() -> dict:
    """
    Loads seed product data into a dict keyed by product_id.
    In production, this would be a DB query or cache read.

    Returns:
        Dict[str, Product]: product_id → Product
    """
    product_map = {}
    for raw in PRODUCTS:
        suitability = ProductAgeSuitability(
            min_age=raw["age_suitability"]["min_age"],
            max_age=raw["age_suitability"]["max_age"],
            modes_allowed=raw["age_suitability"]["modes_allowed"],
        )
        product = Product(
            product_id=raw["product_id"],
            name=raw["name"],
            brand=raw["brand"],
            category=raw["category"],
            region_relevance=raw["region_relevance"],
            age_suitability=suitability,
            tags=raw["tags"],
            comfort_score=raw["comfort_score"],
        )
        product_map[product.product_id] = product
    return product_map


# Singleton-style cache — loaded once at import time
_PRODUCT_CACHE: Optional[dict] = None

def get_product_cache() -> dict:
    global _PRODUCT_CACHE
    if _PRODUCT_CACHE is None:
        _PRODUCT_CACHE = load_all_products()
    return _PRODUCT_CACHE


# ---------------------------------------------------------------------------
# CULTURAL MAPPING LOOKUP
# ---------------------------------------------------------------------------

def get_candidate_product_ids(object_type: str, region: str) -> List[str]:
    """
    Returns the list of candidate product_ids from the cultural mapping
    for a given object_type and region.

    Returns empty list if no mapping exists (triggers no-replace).
    """
    mapping = CULTURAL_MAPPING.get(object_type, {}).get(region, {})
    return mapping.get("candidates", [])


# ---------------------------------------------------------------------------
# HARD FILTERS
# ---------------------------------------------------------------------------

def is_age_safe(product: Product, user: UserCategory) -> bool:
    """
    Hard rule: checks both age range AND mode allowlist.
    A product must pass BOTH checks to be considered.

    Examples:
      - Kingfisher (min_age=21, modes=["adult"]) → fails for kid mode
      - Sprite (min_age=0, modes=["kid","adult","elderly"]) → passes for all
    """
    suitability = product.age_suitability
    age_ok = suitability.min_age <= user.age <= suitability.max_age
    mode_ok = user.mode in suitability.modes_allowed
    return age_ok and mode_ok


def is_region_relevant(product: Product, region: str) -> bool:
    """
    Hard rule: product must be relevant to user's region OR be globally available.
    'Global' tag means the product is universally applicable.
    """
    return region in product.region_relevance or "Global" in product.region_relevance


def get_valid_products(
    object_type: str,
    user: UserCategory,
) -> List[Product]:
    """
    Main filtering function. Steps:
      1. Get candidate product IDs from cultural mapping
      2. Load full product objects
      3. Apply hard filters: age safety + region relevance

    Args:
        object_type: The detected object type (e.g., "bottle")
        user: The classified UserCategory

    Returns:
        List of Product objects that passed all hard filters.
        Empty list = no safe replacement exists.
    """
    candidate_ids = get_candidate_product_ids(object_type, user.region)
    product_cache = get_product_cache()

    valid = []
    for pid in candidate_ids:
        product = product_cache.get(pid)
        if product is None:
            continue  # Skip unknown product IDs gracefully

        if not is_age_safe(product, user):
            continue

        if not is_region_relevant(product, user.region):
            continue

        valid.append(product)

    return valid
