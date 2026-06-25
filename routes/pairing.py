"""Pairing API routes — same engine facade powers REST + MCP. Backend (Supabase or
local) is chosen in engines/pairing.py."""
from fastapi import APIRouter, HTTPException, Query

from pydantic import BaseModel

from engines import pairing as engine

router = APIRouter(prefix="/v1", tags=["pairing"])


class RecipeReq(BaseModel):
    ingredients: list[str]
    type: str = "dish"


@router.post("/recipe")
def recipe(req: RecipeReq):
    """Given selected ingredients + a recipe type, return the shared flavour theme
    (data-grounded) and a suggestion. Full recipe text would use an LLM."""
    from engines import supabase_index
    theme: list[str] = []
    if supabase_index.available():
        try:
            theme = supabase_index.common_notes(req.ingredients)
        except Exception:
            theme = []
    names = ", ".join(i.replace("_", " ") for i in req.ingredients)
    sugg = f"A {req.type} built around {names}"
    if theme:
        sugg += f" — united by {', '.join(theme[:4])} notes"
    return {"type": req.type, "ingredients": req.ingredients, "shared_theme": theme, "suggestion": sugg + "."}


@router.get("/pair/{ingredient}")
def pair(
    ingredient: str,
    mode: str = Query("balanced", pattern="^(safe|balanced|experimental)$"),
    limit: int = Query(20, ge=1, le=100),
):
    """Ranked, explained pairings for an ingredient (each carries a strength tier)."""
    try:
        results = engine.pair(ingredient, mode=mode, limit=limit)
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except NotImplementedError as e:
        raise HTTPException(status_code=501, detail=str(e))
    return {"ingredient": ingredient, "mode": mode, "pairings": results}


@router.get("/trio/{ingredient}")
def trio(ingredient: str, limit: int = Query(8, ge=1, le=30)):
    """Affinities-in-threes: anchor + two partners that all mutually pair."""
    try:
        results = engine.trio(ingredient, limit=limit)
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except NotImplementedError as e:
        raise HTTPException(status_code=501, detail=str(e))
    return {"ingredient": ingredient, "trios": results}


@router.get("/bridge")
def bridge(
    a: str = Query(..., description="first ingredient"),
    c: str = Query(..., description="second ingredient"),
    limit: int = Query(8, ge=1, le=30),
):
    """Flavour-bridging: intermediate ingredient(s) linking two that don't directly pair."""
    try:
        results = engine.bridge(a, c, limit=limit)
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except NotImplementedError as e:
        raise HTTPException(status_code=501, detail=str(e))
    return {"a": a, "c": c, "bridges": results}


@router.get("/i18n/{lang}")
def i18n(lang: str):
    """Localized display dictionaries for a language (names + flavour notes)."""
    from engines import supabase_index
    if lang == "en" or not supabase_index.available():
        return {"lang": "en", "names": {}, "notes": {}}
    try:
        return supabase_index.i18n_bundle(lang)
    except Exception:
        return {"lang": lang, "names": {}, "notes": {}}


@router.get("/substitute/{ingredient}")
def substitute(
    ingredient: str,
    limit: int = Query(10, ge=1, le=50),
    same_category_only: bool = Query(False),
):
    """Smart swaps that can replace an ingredient, with reasoning."""
    try:
        results = engine.substitute(ingredient, limit=limit, same_category_only=same_category_only)
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except NotImplementedError as e:
        raise HTTPException(status_code=501, detail=str(e))
    return {"ingredient": ingredient, "substitutes": results}


@router.get("/ingredient/{ingredient}")
def ingredient_detail(ingredient: str):
    """Display name + nutrition (with provenance) + top pairings."""
    try:
        return engine.detail(ingredient)
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except NotImplementedError as e:
        raise HTTPException(status_code=501, detail=str(e))
