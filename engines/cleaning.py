"""Data hygiene for the ingredient set.

FlavorGraph nodes include a few non-ingredients (cleaning chemicals, a stray colour
word). We exclude them from the served graph. The list is deliberately CONSERVATIVE
and curated by hand — we do NOT exclude by `is_hub` (hubs are the best ingredients:
almond, garlic, strawberry...) and we keep legitimate one-word foods (salt, water,
orange-the-fruit). This stoplist is the seed of a larger curation pass in Phase 1.
"""

# Confirmed non-ingredient nodes present in FlavorGraph:
EXCLUDE = {
    "green",            # standalone colour word, not an ingredient (orange/red kept where they're foods)
    "bleach", "borax", "alum", "lye",   # cleaning / non-food chemicals
    "casing",           # sausage casing — not a pairable flavour entity
}


def is_excluded(name: str) -> bool:
    return name in EXCLUDE


def display_name(name: str) -> str:
    """Canonical snake_case -> human label, e.g. 'dark_chocolate' -> 'Dark Chocolate'."""
    return name.replace("_", " ").strip().title()
