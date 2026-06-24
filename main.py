"""IngredientAI API — FastAPI entrypoint. Serves a small test UI at / plus the
/v1 pairing endpoints (Supabase-backed in production)."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse

from settings import settings
from routes import pairing

app = FastAPI(title="IngredientAI API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in settings.cors_origins.split(",")],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(pairing.router)


@app.get("/health")
def health():
    return {"status": "ok", "environment": settings.environment, "version": "0.1.0"}


@app.get("/", response_class=HTMLResponse)
def home():
    return INDEX_HTML


INDEX_HTML = """<!doctype html><html lang=en><head><meta charset=utf-8>
<meta name=viewport content="width=device-width,initial-scale=1"><title>IngredientAI</title>
<style>
:root{--bg:#faf9f6;--card:#fff;--line:#e7e4dc;--ink:#22201b;--mut:#6f6b61;--accent:#1d9e75}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;line-height:1.5}
.wrap{max-width:860px;margin:0 auto;padding:26px 18px 60px}
h1{font-size:22px;font-weight:600;margin:0 0 2px}.sub{color:var(--mut);font-size:14px;margin:0 0 18px}
.row{display:flex;gap:8px;flex-wrap:wrap;align-items:center;margin-bottom:14px}
input{border:1px solid var(--line);border-radius:10px;padding:10px 12px;font-size:15px;background:#fff;min-width:220px;flex:1}
.toggle{display:inline-flex;border:1px solid var(--line);border-radius:10px;overflow:hidden}
.toggle button{border:0;background:#fff;padding:9px 15px;font-size:13px;cursor:pointer}.toggle button.on{background:var(--accent);color:#fff}
button.go{border:1px solid var(--line);background:#fff;border-radius:10px;padding:10px 16px;font-size:14px;cursor:pointer}
.chips{display:flex;gap:6px;flex-wrap:wrap;margin:2px 0 16px}.chip{border:1px solid var(--line);background:#fff;border-radius:999px;padding:5px 11px;font-size:12px;cursor:pointer}
.head{display:flex;align-items:baseline;gap:10px;margin:10px 0 4px}.head h2{font-size:20px;font-weight:600;margin:0}.cat{color:var(--mut);font-size:13px}
.nut{display:flex;gap:8px;flex-wrap:wrap;margin:10px 0 18px}.stat{background:#fff;border:1px solid var(--line);border-radius:10px;padding:7px 11px;min-width:70px}.stat .v{font-size:17px;font-weight:600}.stat .k{font-size:10px;color:var(--mut);text-transform:uppercase;letter-spacing:.04em}
.sec{font-size:12px;font-weight:600;color:var(--mut);text-transform:uppercase;letter-spacing:.05em;margin:18px 0 9px}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(210px,1fr));gap:9px}
.pc{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:11px 13px}
.pc .n{font-weight:600;font-size:15px;margin-bottom:7px;display:flex;justify-content:space-between;align-items:center}
.badge{font-size:10px;font-weight:600;padding:2px 7px;border-radius:999px;background:#eef6f1;color:#0f6e56}
.bar{height:6px;border-radius:6px;background:#eee;overflow:hidden;margin:5px 0}.bar>span{display:block;height:100%;background:var(--accent)}
.why{font-size:12px;color:var(--mut)}.why b{color:var(--ink);font-weight:600}.err{color:#a32d2d;font-size:14px}
.foot{margin-top:30px;font-size:12px;color:var(--mut);border-top:1px solid var(--line);padding-top:12px}
</style></head><body><div class=wrap>
<h1>IngredientAI</h1><p class=sub>Explainable flavour pairing over 6,629 ingredients - every suggestion shows why.</p>
<div class=row>
  <input id=q placeholder="Type an ingredient, e.g. basil" value="basil" onkeydown="if(event.key==='Enter')load()">
  <div class=toggle><button id=m-safe class=on onclick="setMode('safe')">Safe</button><button id=m-exp onclick="setMode('experimental')">Experimental</button></div>
  <button class=go onclick=load()>Go</button>
</div>
<div class=chips id=chips></div>
<div id=panel></div>
<div class=foot>Engine: pgvector nearest-neighbour (FlavorGraph, Apache-2.0) + shared flavour-compound overlap; nutrition from USDA. Served by FastAPI on Railway, data in Supabase.</div>
</div><script>
let mode='safe';
const chips=['basil','strawberry','tomato','garlic','dark_chocolate','coffee','salmon','lemon','mushroom','ginger'];
document.getElementById('chips').innerHTML=chips.map(c=>`<span class=chip onclick="pick('${c}')">${c.replace(/_/g,' ')}</span>`).join('');
function pick(c){document.getElementById('q').value=c;load();}
function setMode(m){mode=m;document.getElementById('m-safe').className=m==='safe'?'on':'';document.getElementById('m-exp').className=m==='experimental'?'on':'';load();}
function disp(s){return s.replace(/_/g,' ').replace(/\\b\\w/g,c=>c.toUpperCase());}
async function jget(u){const r=await fetch(u);if(!r.ok)throw new Error(r.status);return r.json();}
async function load(){
  const name=document.getElementById('q').value.trim().toLowerCase().replace(/ /g,'_');
  const panel=document.getElementById('panel');panel.innerHTML='Loading...';
  try{
    const [pair,sub,det]=await Promise.all([
      jget(`/v1/pair/${encodeURIComponent(name)}?mode=${mode}&limit=8`),
      jget(`/v1/substitute/${encodeURIComponent(name)}?limit=6`),
      jget(`/v1/ingredient/${encodeURIComponent(name)}`).catch(()=>null)
    ]);
    let h=`<div class=head><h2>${disp(name)}</h2></div>`;
    const nut=det&&det.nutrition;
    if(nut){h+='<div class=nut>'+Object.entries(nut).map(([k,v])=>`<div class=stat><div class=v>${v.value??v}</div><div class=k>${k.replace('_g','').replace('_',' ')}</div></div>`).join('')+'</div>';}
    h+=`<div class=sec>Pairs well with - ${mode==='safe'?'consensus':'experimental'}</div><div class=grid>`;
    h+=pair.pairings.map(p=>`<div class=pc><div class=n>${p.display||disp(p.ingredient)}</div><div class=bar><span style="width:${Math.round(p.explanation.embedding_cosine*100)}%"></span></div><div class=why>similarity <b>${p.explanation.embedding_cosine.toFixed(2)}</b> &middot; <b>${p.explanation.shared_compounds}</b> shared compounds</div></div>`).join('');
    h+='</div><div class=sec>Can be substituted by</div><div class=grid>';
    h+=sub.substitutes.map(s=>`<div class=pc><div class=n>${s.display||disp(s.ingredient)}${s.explanation.same_category?'<span class=badge>same type</span>':''}</div><div class=bar><span style="width:${Math.round(s.explanation.similarity*100)}%"></span></div><div class=why>similarity <b>${s.explanation.similarity.toFixed(2)}</b> &middot; <b>${s.explanation.shared_compounds}</b> shared${s.category?' &middot; '+s.category:''}</div></div>`).join('');
    h+='</div>';panel.innerHTML=h;
  }catch(e){panel.innerHTML=`<p class=err>No data for "${disp(name)}". Try another ingredient (e.g. basil, tomato, garlic).</p>`;}
}
load();
</script></body></html>"""
