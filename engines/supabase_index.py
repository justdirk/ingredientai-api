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
    # pair_rich = pgvector neighbours + shared flavour molecules, explained by the
    # most DISTINCTIVE shared flavour notes (IDF-weighted). Falls back to pair_ingredient.
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
        "explanation": {
            "embedding_cosine": r["embedding_cosine"],
            "shared_compounds": r["shared_compounds"],
            "shared_notes": r.get("shared_notes") or [],
        },
    } for r in rows]


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
