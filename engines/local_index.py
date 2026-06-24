"""Local, in-memory pairing index built from FlavorGraph (Apache-2.0).

Lets the engine return LIVE results with no cloud DB — the local stand-in for the
Supabase + pgvector path. In production the same `pair()` interface is backed by a
pgvector cosine query; here it's an in-memory numpy matrix.

Set FLAVORGRAPH_DIR to a clone of github.com/lamypark/FlavorGraph.
"""
from __future__ import annotations
import os, csv, pickle, functools
import numpy as np

FG = os.environ.get("FLAVORGRAPH_DIR", "/tmp/FlavorGraph")


@functools.lru_cache(maxsize=1)
def _index():
    """Build once: names, normalized embedding matrix, name->row, compound sets, categories."""
    import glob
    id2name, ntype = {}, {}
    with open(f"{FG}/input/nodes_191120.csv") as f:
        for row in csv.DictReader(f):
            nid = int(row["node_id"])
            id2name[nid] = row["name"]
            ntype[nid] = row["node_type"]
    name2id = {v: k for k, v in id2name.items()}

    # ingredient -> category (for substitution / display)
    category: dict[int, str] = {}
    cat_files = glob.glob(f"{FG}/input/dict_ingr2cate*")
    if cat_files:
        with open(cat_files[0]) as f:
            for row in csv.DictReader(f):
                nid = name2id.get(row["ingredient"])
                if nid is not None:
                    category[nid] = row["category"]

    # ingredient -> set(compound ids)  (shared-compound signal)
    compounds: dict[int, set] = {}
    with open(f"{FG}/input/edges_191120.csv") as f:
        for row in csv.DictReader(f):
            if row["edge_type"] in ("ingr-fcomp", "ingr-dcomp"):
                a, b = int(row["id_1"]), int(row["id_2"])
                ing, comp = (a, b) if ntype.get(a) == "ingredient" else (b, a)
                if ntype.get(ing) == "ingredient" and ntype.get(comp) == "compound":
                    compounds.setdefault(ing, set()).add(comp)

    # 300D embeddings, keyed by ingredient name (skip curated non-ingredient noise)
    from engines import cleaning
    emb = pickle.load(open(f"{FG}/output/kitchenette_embeddings.pkl", "rb"))
    ids, rows = [], []
    for name, vec in emb.items():
        nid = name2id.get(name)
        if nid is not None and ntype.get(nid) == "ingredient" and not cleaning.is_excluded(name):
            ids.append(nid)
            rows.append(np.asarray(vec, dtype=np.float32))
    M = np.vstack(rows)
    M /= (np.linalg.norm(M, axis=1, keepdims=True) + 1e-9)
    row_of = {nid: i for i, nid in enumerate(ids)}
    return dict(id2name=id2name, name2id=name2id, ids=ids, M=M,
                row_of=row_of, compounds=compounds, category=category)


def available() -> bool:
    return os.path.isdir(FG)


WEIGHTS = {"safe": (0.8, 0.2), "balanced": (0.6, 0.4), "experimental": (0.4, 0.6)}


def pair(ingredient: str, mode: str = "balanced", limit: int = 20) -> list[dict]:
    ix = _index()
    nid = ix["name2id"].get(ingredient)
    if nid is None or nid not in ix["row_of"]:
        raise KeyError(f"unknown ingredient: {ingredient!r}")
    k = ix["row_of"][nid]
    cos = ix["M"] @ ix["M"][k]
    w_emb, w_chem = WEIGHTS.get(mode, WEIGHTS["balanced"])
    my_comp = ix["compounds"].get(nid, set())

    out = []
    for j in np.argsort(-cos):
        oid = ix["ids"][j]
        if oid == nid:
            continue
        shared = len(my_comp & ix["compounds"].get(oid, set()))
        score = w_emb * float(cos[j]) + w_chem * min(shared / 20.0, 1.0)
        from engines import cleaning
        out.append({
            "ingredient": ix["id2name"][oid],
            "display": cleaning.display_name(ix["id2name"][oid]),
            "score": round(score, 4),
            "explanation": {
                "embedding_cosine": round(float(cos[j]), 4),
                "shared_compounds": int(shared),
                "note": "consensus" if cos[j] > 0.7 else ("novel" if mode == "experimental" else ""),
            },
        })
        if len(out) >= limit:
            break
    # experimental mode re-ranks by the blended score (rewards chemistry/novelty)
    out.sort(key=lambda r: r["score"], reverse=True)
    return out


def substitute(ingredient: str, limit: int = 10, same_category_only: bool = False) -> list[dict]:
    """Smart swaps: ingredients that can REPLACE this one (similarity-driven, category-aware)."""
    from engines import cleaning
    ix = _index()
    nid = ix["name2id"].get(ingredient)
    if nid is None or nid not in ix["row_of"]:
        raise KeyError(f"unknown ingredient: {ingredient!r}")
    k = ix["row_of"][nid]
    cos = ix["M"] @ ix["M"][k]
    my_cat = ix["category"].get(nid)
    my_comp = ix["compounds"].get(nid, set())

    out = []
    for j in np.argsort(-cos):
        oid = ix["ids"][j]
        if oid == nid:
            continue
        o_cat = ix["category"].get(oid)
        same_cat = my_cat is not None and o_cat == my_cat
        if same_category_only and not same_cat:
            continue
        shared = len(my_comp & ix["compounds"].get(oid, set()))
        # substitution is similarity-led, with a same-category boost
        sub_score = float(cos[j]) + (0.05 if same_cat else 0.0)
        out.append({
            "ingredient": ix["id2name"][oid],
            "display": cleaning.display_name(ix["id2name"][oid]),
            "category": o_cat,
            "score": round(sub_score, 4),
            "explanation": {
                "similarity": round(float(cos[j]), 4),
                "shared_compounds": int(shared),
                "same_category": bool(same_cat),
            },
        })
    out.sort(key=lambda r: r["score"], reverse=True)
    return out[:limit]
