"""Supabase-backed engine: calls the SQL RPCs (pgvector kNN + shared-compound blend)
via PostgREST with the anon key. Used in production (Railway); the local index is the
fallback for the firewalled sandbox.
"""
import httpx
from settings import settings
from engines import cleaning


def available() -> bool:
    return bool(settings.supabase_url and settings.supabase_anon_key)


def _rpc(fn: str, payload: dict):
    url = f"{settings.supabase_url}/rest/v1/rpc/{fn}"
    headers = {
        "apikey": settings.supabase_anon_key,
        "Authorization": f"Bearer {settings.supabase_anon_key}",
        "Content-Type": "application/json",
    }
    r = httpx.post(url, json=payload, headers=headers, timeout=30)
    r.raise_for_status()
    return r.json()


def pair(ingredient: str, mode: str = "balanced", limit: int = 20) -> list[dict]:
    # pair_rich = co-occurrence consensus + embedding + most DISTINCTIVE shared notes
    # (IDF-weighted), with a Bible-style strength tier. Falls back to pair_ingredient.
    rows = _rpc("pair_rich", {"p_name": ingredient, "p_mode": mode, "p_limit": limit})
    if not rows:
        rows = _rpc("pair_ingredient", {"p_name": ingredient, "p_mode": mode, "p_limit": limit})
        if not rows:
            raise KeyError(f"unknown ingredient: {ingredient!r}")
    return [{
        "ingredient": r["ingredient"],
        "display": cleaning.display_name(r["ingredient"]),
        "category": r.get("category"),
        "score": r["score"],
        "tier": r.get("tier"),
        "explanation": {
            "embedding_cosine": r["embedding_cosine"],
            "shared_compounds": r["shared_compounds"],
            "shared_notes": r.get("shared_notes") or [],
        },
    } for r in rows]


def trio(ingredient: str, limit: int = 8) -> list[dict]:
    """Affinities-in-threes: anchor + two partners that all mutually co-occur."""
    rows = _rpc("pair_trio", {"p_name": ingredient, "p_limit": limit})
    return [{
        "a": r["partner_a"], "a_display": cleaning.display_name(r["partner_a"]),
        "b": r["partner_b"], "b_display": cleaning.display_name(r["partner_b"]),
        "score": r["score"], "why": r.get("why"),
    } for r in rows]


def bridge(a: str, c: str, limit: int = 8) -> list[dict]:
    """Flavour-bridging (Simas et al.): an intermediate linking two ingredients that
    don't directly pair — via real recipes first, else shared aroma notes."""
    rows = _rpc("flavor_bridge", {"p_a": a, "p_c": c, "p_limit": limit})
    return [{
        "bridge": r["bridge"], "display": cleaning.display_name(r["bridge"]),
        "category": r.get("category"), "score": r["score"],
        "a_link": r.get("a_link"), "c_link": r.get("c_link"),
        "direct_link": r.get("direct_link"), "via": r.get("via"),
    } for r in rows]


def i18n_bundle(lang: str) -> dict:
    """Localized display dictionaries: {lang, names:{canonical:localized}, notes:{en:localized}}."""
    return _rpc("i18n_bundle", {"p_lang": lang})


def substitute(ingredient: str, limit: int = 10, same_category_only: bool = False) -> list[dict]:
    rows = _rpc("substitute_ingredient",
                {"p_name": ingredient, "p_limit": limit, "p_same_category_only": same_category_only})
    if not rows:
        raise KeyError(f"unknown ingredient: {ingredient!r}")
    return [{
        "ingredient": r["ingredient"],
        "display": cleaning.display_name(r["ingredient"]),
        "category": r["category"],
        "score": r["score"],
        "explanation": {"similarity": r["similarity"], "shared_compounds": r["shared_compounds"],
                        "same_category": r["same_category"]},
    } for r in rows]


def common_notes(names: list[str]) -> list[str]:
    rows = _rpc("common_notes", {"p_names": names})
    return [r["note"] for r in rows]


def detail(ingredient: str) -> dict:
    d = _rpc("ingredient_detail", {"p_name": ingredient})
    if not d or d.get("category") is None and d.get("nutrition") is None and not d.get("top_pairings"):
        # still return; unknown ingredient yields mostly-null object
        pass
    d["display"] = cleaning.display_name(ingredient)
    return d
