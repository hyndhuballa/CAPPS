"""
data/seed_data.py
Realistic dummy datasets for the Culturalization Layer (India-focused MVP).
"""

from datetime import date

# ---------------------------------------------------------------------------
# USERS
# ---------------------------------------------------------------------------
USERS = [
    {
        "user_id": "u001",
        "name": "Riya Sharma",
        "dob": date(2010, 6, 15),        # age ~15 → kid
        "region": "India",
        "preferences": ["animation", "sports"],
        "cultural_layer_enabled": True,
        "parent_id": "u005",
    },
    {
        "user_id": "u002",
        "name": "Arjun Mehta",
        "dob": date(1992, 3, 20),        # age ~33 → adult
        "region": "India",
        "preferences": ["cricket", "tech"],
        "cultural_layer_enabled": True,
        "parent_id": None,
    },
    {
        "user_id": "u003",
        "name": "Sunita Devi",
        "dob": date(1958, 11, 2),        # age ~66 → elderly
        "region": "India",
        "preferences": ["devotional", "cooking"],
        "cultural_layer_enabled": True,
        "parent_id": None,
    },
    {
        "user_id": "u004",
        "name": "Karan Patel",
        "dob": date(2000, 8, 10),        # age ~25 → adult
        "region": "India",
        "preferences": ["gaming", "fitness"],
        "cultural_layer_enabled": False,  # layer OFF — should always return no-replace
        "parent_id": None,
    },
    {
        "user_id": "u005",
        "name": "Priya Sharma",           # Parent of Riya
        "dob": date(1982, 4, 18),        # age ~43 → adult
        "region": "India",
        "preferences": ["bollywood", "travel"],
        "cultural_layer_enabled": True,
        "parent_id": None,
    },
]

# ---------------------------------------------------------------------------
# PRODUCTS
# ---------------------------------------------------------------------------
PRODUCTS = [
    # --- Beverages ---
    {
        "product_id": "p001",
        "name": "Frooti",
        "brand": "Frooti",
        "category": "bottle",
        "region_relevance": ["India"],
        "age_suitability": {"min_age": 0, "max_age": 99, "modes_allowed": ["kid", "adult", "elderly"]},
        "tags": ["beverage", "mango", "kid_friendly", "popular_india", "casual"],
        "comfort_score": 8,
    },
    {
        "product_id": "p002",
        "name": "Thums Up",
        "brand": "Thums Up",
        "category": "bottle",
        "region_relevance": ["India"],
        "age_suitability": {"min_age": 13, "max_age": 99, "modes_allowed": ["adult", "elderly", "kid"]},
        "tags": ["beverage", "cola", "popular_india", "sports", "casual"],
        "comfort_score": 7,
    },
    {
        "product_id": "p003",
        "name": "Sprite",
        "brand": "Sprite",
        "category": "bottle",
        "region_relevance": ["India", "Global"],
        "age_suitability": {"min_age": 0, "max_age": 99, "modes_allowed": ["kid", "adult", "elderly"]},
        "tags": ["beverage", "lemon", "kid_friendly", "casual", "age_safe"],
        "comfort_score": 8,
    },
    {
        "product_id": "p004",
        "name": "Maaza",
        "brand": "Maaza",
        "category": "bottle",
        "region_relevance": ["India"],
        "age_suitability": {"min_age": 0, "max_age": 99, "modes_allowed": ["kid", "adult", "elderly"]},
        "tags": ["beverage", "mango", "kid_friendly", "popular_india", "casual"],
        "comfort_score": 9,
    },
    {
        "product_id": "p005",
        "name": "Kingfisher Beer",
        "brand": "Kingfisher",
        "category": "bottle",
        "region_relevance": ["India"],
        "age_suitability": {"min_age": 21, "max_age": 99, "modes_allowed": ["adult"]},
        "tags": ["beverage", "alcohol", "adult_only", "casual"],
        "comfort_score": 4,
    },
    {
        "product_id": "p006",
        "name": "Sting Energy",
        "brand": "Sting",
        "category": "bottle",
        "region_relevance": ["India", "Global"],
        "age_suitability": {"min_age": 16, "max_age": 55, "modes_allowed": ["adult"]},
        "tags": ["beverage", "energy", "sports", "gaming", "casual"],
        "comfort_score": 5,
    },
    # --- Food Packages ---
    {
        "product_id": "p007",
        "name": "Haldiram's Namkeen",
        "brand": "Haldiram's",
        "category": "food_package",
        "region_relevance": ["India"],
        "age_suitability": {"min_age": 0, "max_age": 99, "modes_allowed": ["kid", "adult", "elderly"]},
        "tags": ["snack", "popular_india", "casual", "kid_friendly", "comfort_food"],
        "comfort_score": 9,
    },
    {
        "product_id": "p008",
        "name": "Lays India Magic Masala",
        "brand": "Lays",
        "category": "food_package",
        "region_relevance": ["India", "Global"],
        "age_suitability": {"min_age": 5, "max_age": 99, "modes_allowed": ["kid", "adult", "elderly"]},
        "tags": ["snack", "casual", "kid_friendly", "popular_india"],
        "comfort_score": 7,
    },
    # --- Posters / Background Ads ---
    {
        "product_id": "p009",
        "name": "Fevicol",
        "brand": "Fevicol",
        "category": "poster",
        "region_relevance": ["India"],
        "age_suitability": {"min_age": 0, "max_age": 99, "modes_allowed": ["kid", "adult", "elderly"]},
        "tags": ["home", "popular_india", "casual", "kid_friendly", "nostalgic"],
        "comfort_score": 8,
    },
    {
        "product_id": "p010",
        "name": "Amul Butter",
        "brand": "Amul",
        "category": "poster",
        "region_relevance": ["India"],
        "age_suitability": {"min_age": 0, "max_age": 99, "modes_allowed": ["kid", "adult", "elderly"]},
        "tags": ["food", "popular_india", "casual", "kid_friendly", "nostalgic", "comfort_food"],
        "comfort_score": 10,
    },
    {
        "product_id": "p011",
        "name": "Tanishq Jewellery",
        "brand": "Tanishq",
        "category": "poster",
        "region_relevance": ["India"],
        "age_suitability": {"min_age": 18, "max_age": 99, "modes_allowed": ["adult", "elderly"]},
        "tags": ["luxury", "jewellery", "formal", "popular_india", "wedding"],
        "comfort_score": 7,
    },
]

# ---------------------------------------------------------------------------
# CULTURAL MAPPING
# object_type + region → candidate product_ids, with kid exclusions
# ---------------------------------------------------------------------------
CULTURAL_MAPPING = {
    "bottle": {
        "India": {
            "candidates": ["p001", "p002", "p003", "p004", "p005", "p006"],
            "kid_excluded": ["p005"],        # alcohol
            "elderly_preferred": ["p001", "p003", "p004"],  # lighter, comfort drinks
            "scene_boost": {
                "sports": ["p002", "p006"],
                "casual": ["p001", "p003", "p004"],
                "party":  ["p002", "p005"],
            },
        }
    },
    "food_package": {
        "India": {
            "candidates": ["p007", "p008"],
            "kid_excluded": [],
            "elderly_preferred": ["p007"],
            "scene_boost": {
                "casual": ["p007", "p008"],
                "sports": ["p008"],
            },
        }
    },
    "poster": {
        "India": {
            "candidates": ["p009", "p010", "p011"],
            "kid_excluded": ["p011"],        # jewellery ad not for kids
            "elderly_preferred": ["p009", "p010"],
            "scene_boost": {
                "formal": ["p011"],
                "casual": ["p009", "p010"],
                "wedding": ["p011"],
            },
        }
    },
}

# ---------------------------------------------------------------------------
# SCENE CATEGORIES
# Scenes where replacement should NEVER happen (emotional integrity)
# ---------------------------------------------------------------------------
EMOTIONAL_SCENES = {"funeral", "grief", "medical", "hospital", "prayer", "accident"}

# Scenes considered formal (affects scoring negatively for casual-only products)
FORMAL_SCENES = {"wedding_ceremony", "court", "formal_meeting", "graduation"}

# ---------------------------------------------------------------------------
# SUPPORTED REGIONS
# Used to validate incoming region and return clear error for unsupported ones.
# ---------------------------------------------------------------------------
SUPPORTED_REGIONS = {"India"}

# ---------------------------------------------------------------------------
# FOREIGN → LOCAL BRAND MAPPING
# category → ordered list of preferred Indian replacements (deterministic).
# First entry is always the primary recommendation for that category.
# ---------------------------------------------------------------------------
FOREIGN_TO_LOCAL = {
    "cola":       ["Thums Up", "Maaza", "Frooti"],
    "alcohol":    ["Kingfisher Beer"],          # adult-only; gating applied separately
    "chips":      ["Kurkure", "Haldiram's", "Bingo Mad Angles"],
    "fast_food":  ["Wow! Momo", "Haldiram's Namkeen"],
    "energy":     ["Sting Energy"],
    "coffee":     ["Bru", "Tata Tea"],
    "sportswear": ["Wildcraft"],
    "juice":      ["Real Juice", "Frooti", "Maaza"],
}

# Maps a detected brand name (lowercase) to its category for FOREIGN_TO_LOCAL lookup.
BRAND_TO_CATEGORY = {
    "pepsi":        "cola",
    "coca-cola":    "cola",
    "coke":         "cola",
    "budweiser":    "alcohol",
    "heineken":     "alcohol",
    "corona":       "alcohol",
    "budlight":     "alcohol",
    "doritos":      "chips",
    "pringles":     "chips",
    "lays":         "chips",
    "mcdonalds":    "fast_food",
    "mcdonald's":   "fast_food",
    "kfc":          "fast_food",
    "subway":       "fast_food",
    "red bull":     "energy",
    "monster":      "energy",
    "starbucks":    "coffee",
    "nescafe":      "coffee",
    "nike":         "sportswear",
    "adidas":       "sportswear",
    "tropicana":    "juice",
    "minute maid":  "juice",
}

# ---------------------------------------------------------------------------
# OBJECT IMPORTANCE CONFIG
# Controls whether a detected object is important enough to block replacement.
# importance_score = base(scene_type) + focus_bonus * object_focus
# If importance_score >= threshold → DO NOT replace (preserve narrative integrity).
# ---------------------------------------------------------------------------
OBJECT_IMPORTANCE_CONFIG = {
    "threshold": 0.60,          # Minimum importance to block replacement
    "focus_weight": 0.15,       # Multiplied by object_focus (0.0–1.0 field)
    "scene_base_scores": {
        # High narrative value — object is often a story prop
        "wedding_ceremony": 0.70,
        "funeral":          0.90,   # always blocked via emotional gate first
        "medical":          0.85,
        "court":            0.75,
        "formal_meeting":   0.60,
        "graduation":       0.65,
        # Low narrative value — object is background, safe to replace
        "casual":           0.20,
        "sports":           0.30,
        "party":            0.25,
        "outdoor":          0.25,
    },
    "default_base_score": 0.35,  # For unmapped scene types
}
