"""Engine facade — picks the Supabase backend when configured and reachable,
otherwise the local FlavorGraph index. Identical response shape either way, so the
REST routes and the MCP server don't care which is active.
"""
import httpx


def _supabase_ok() -> bool:
    from engines import supabase_index
    return supabase_index.available()


def _local_ok() -> bool:
    from engines import local_index
    return local_index.available()


def pair(ingredient: str, mode: str = "balanced", limit: int = 20) -> list[dict]:
    from engines import supabase_index, local_index
    if _supabase_ok():
        try:
            return supabase_index.pair(ingredient, mode=mode, limit=limit)
        except (httpx.HTTPError, OSError):
            pass  # fall back (e.g. firewalled local dev)
    if _local_ok():
        return local_index.pair(ingredient, mode=mode, limit=limit)
    raise NotImplementedError("No data source. Configure Supabase or set FLAVORGRAPH_DIR.")


def trio(ingredient: str, limit: int = 8) -> list[dict]:
    """Affinities-in-threes (Supabase only)."""
    from engines import supabase_index
    if _supabase_ok():
        try:
            return supabase_index.trio(ingredient, limit=limit)
        except (httpx.HTTPError, OSError):
            pass
    raise NotImplementedError("Trios require the Supabase backend.")


def bridge(a: str, c: str, limit: int = 8) -> list[dict]:
    """Flavour-bridging between two ingredients (Supabase only)."""
    from engines import supabase_index
    if _supabase_ok():
        try:
            return supabase_index.bridge(a, c, limit=limit)
        except (httpx.HTTPError, OSError):
            pass
    raise NotImplementedError("Bridging requires the Supabase backend.")


def substitute(ingredient: str, limit: int = 10, same_category_only: bool = False) -> list[dict]:
    from engines import supabase_index, local_index
    if _supabase_ok():
        try:
            return supabase_index.substitute(ingredient, limit=limit, same_category_only=same_category_only)
        except (httpx.HTTPError, OSError):
            pass
    if _local_ok():
        return local_index.substitute(ingredient, limit=limit, same_category_only=same_category_only)
    raise NotImplementedError("No data source.")


def detail(ingredient: str) -> dict:
    from engines import supabase_index, local_index, cleaning
    if _supabase_ok():
        try:
            return supabase_index.detail(ingredient)
        except (httpx.HTTPError, OSError):
            pass
    # local assembly
    import sys, os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "data", "ingest"))
    import usda
    top = local_index.pair(ingredient, mode="balanced", limit=3)
    return {"ingredient": ingredient, "display": cleaning.display_name(ingredient),
            "nutrition": usda.get_nutrition(ingredient), "top_pairings": top}
