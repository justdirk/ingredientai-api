"""IngredientAI API — FastAPI entrypoint. Serves the interactive pairing-graph
explorer at / plus the /v1 endpoints (Supabase-backed in production)."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse

from settings import settings
from routes import pairing

app = FastAPI(title="IngredientAI API", version="0.2.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in settings.cors_origins.split(",")],
    allow_methods=["*"], allow_headers=["*"],
)
app.include_router(pairing.router)


@app.get("/health")
def health():
    return {"status": "ok", "environment": settings.environment, "version": "0.2.0"}


@app.get("/", response_class=HTMLResponse)
def home():
    return INDEX_HTML


INDEX_HTML = """<!doctype html><html lang=en><head><meta charset=utf-8>
<meta name=viewport content="width=device-width,initial-scale=1"><title>IngredientAI</title>
<script src="https://cdnjs.cloudflare.com/ajax/libs/vis-network/9.1.9/standalone/umd/vis-network.min.js"></script>
<style>
:root{--bg:#faf9f6;--card:#fff;--line:#e7e4dc;--ink:#22201b;--mut:#6f6b61;--accent:#1d9e75}
*{box-sizing:border-box}html,body{margin:0;height:100%}
body{background:var(--bg);color:var(--ink);font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;display:flex;flex-direction:column;height:100vh}
header{padding:10px 16px;border-bottom:1px solid var(--line);display:flex;gap:8px;align-items:center;flex-wrap:wrap}
h1{font-size:17px;font-weight:600;margin:0 14px 0 0}
input,select{border:1px solid var(--line);border-radius:9px;padding:8px 10px;font-size:14px;background:#fff}
input{min-width:180px}
.toggle{display:inline-flex;border:1px solid var(--line);border-radius:9px;overflow:hidden}
.toggle button{border:0;background:#fff;padding:8px 12px;font-size:12.5px;cursor:pointer}.toggle button.on{background:var(--accent);color:#fff}
button.go{border:1px solid var(--line);background:#fff;border-radius:9px;padding:8px 13px;font-size:13px;cursor:pointer}
.main{flex:1;display:flex;min-height:0}
#graph{flex:1;min-width:0}
.side{width:300px;border-left:1px solid var(--line);padding:14px;overflow:auto;background:#fff}
.h{font-size:12px;font-weight:600;color:var(--mut);text-transform:uppercase;letter-spacing:.05em;margin:14px 0 7px}
.notes{font-size:13px}.notes b{color:var(--accent)}
.chips{display:flex;flex-wrap:wrap;gap:6px}
.chip{border:1px solid var(--line);border-radius:999px;padding:4px 10px;font-size:12px;background:#f3f6f4;cursor:pointer}
.chip.add{background:var(--accent);color:#fff;border-color:var(--accent)}
.rip{font-size:13.5px;line-height:1.5;margin-top:8px;background:#f7f6f2;border:1px solid var(--line);border-radius:10px;padding:10px}
.muted{color:var(--mut);font-size:12px}
.hint{font-size:12px;color:var(--mut);padding:6px 16px;border-top:1px solid var(--line)}
</style></head><body>
<header>
  <h1>IngredientAI</h1>
  <input id=q placeholder="Start with an ingredient…" value="garlic" onkeydown="if(event.key==='Enter')start()">
  <button class=go onclick=start()>Explore</button>
  <div class=toggle><button data-m=safe onclick="setMode('safe')">Safe</button><button data-m=balanced class=on onclick="setMode('balanced')">Balanced</button><button data-m=experimental onclick="setMode('experimental')">Experimental</button></div>
  <span class=muted>click a node to expand · double-click to add to your recipe</span>
</header>
<div class=main>
  <div id=graph></div>
  <div class=side>
    <div class=h>Focused</div>
    <div id=focus class=muted>Click a node to see its flavour notes.</div>
    <div class=h>Your recipe</div>
    <div id=basket class=chips><span class=muted>double-click nodes to add</span></div>
    <div class=h>Make it a…</div>
    <select id=rtype><option>salad</option><option>pasta sauce</option><option>main dish</option><option>marinade</option><option>dessert</option><option>cocktail</option><option>soup</option><option>dressing</option></select>
    <button class=go style="margin-top:8px" onclick=build()>Build it</button>
    <div id=recipe></div>
  </div>
</div>
<div class=hint>Graph: FlavorGraph2Vec similarity + shared flavour molecules. Notes from FlavorDB (non-commercial). Edges show the strongest shared note.</div>
<script>
let mode='balanced', net, nodes, edges, expanded=new Set(), basket=[];
const CAT={Fruit:'#e57',Spice:'#d83',Dairy:'#5ad','Plant/Vegetable':'#3a6','Meat/Animal Product':'#c55',Seafood:'#39c','Nut/Seed':'#b84','Beverage Alcoholic':'#a6c','Herb':'#3a6',Flower:'#d6a',Fungus:'#987'};
const disp=s=>s.replace(/_/g,' ').replace(/\\b\\w/g,c=>c.toUpperCase());
function color(cat){return CAT[cat]||'#8a9'}
function setMode(m){mode=m;document.querySelectorAll('.toggle button').forEach(b=>b.className=b.dataset.m===m?'on':'');}
function ensure(){
  if(net)return;
  nodes=new vis.DataSet([]); edges=new vis.DataSet([]);
  net=new vis.Network(document.getElementById('graph'),{nodes,edges},{
    nodes:{shape:'dot',size:14,font:{size:14,color:'#22201b'},borderWidth:0},
    edges:{color:{color:'#cfcabd',highlight:'#1d9e75'},font:{size:10,color:'#6f6b61',strokeWidth:3,strokeColor:'#faf9f6'},smooth:{type:'continuous'}},
    physics:{barnesHut:{springLength:130,gravitationalConstant:-4000},stabilization:{iterations:120}},
    interaction:{hover:true}
  });
  net.on('click',p=>{if(p.nodes.length)focus(p.nodes[0]);});
  net.on('doubleClick',p=>{if(p.nodes.length)addBasket(p.nodes[0]);});
}
function addNode(key,cat){ if(!nodes.get(key)) nodes.add({id:key,label:disp(key),color:color(cat)}); }
async function expand(key){
  if(expanded.has(key+mode))return; expanded.add(key+mode);
  let d; try{ d=await (await fetch(`/v1/pair/${encodeURIComponent(key)}?mode=${mode}&limit=7`)).json(); }catch(e){return;}
  if(!d.pairings)return;
  d.pairings.forEach(p=>{ addNode(p.ingredient,p.category);
    const id=key+'|'+p.ingredient;
    if(!edges.get(id)) edges.add({id,from:key,to:p.ingredient,label:(p.explanation.shared_notes||[])[0]||''});
  });
}
async function focus(key){
  const el=document.getElementById('focus');
  el.innerHTML=`<b style="font-size:15px">${disp(key)}</b> <button class=go style="padding:3px 8px;font-size:11px" onclick="addBasket('${key}')">+ recipe</button><div style="margin-top:6px"></div>`;
  await expand(key);
  // show this node's notes via a pair lookup (its strongest shared notes with neighbours)
  try{ const d=await (await fetch(`/v1/ingredient/${encodeURIComponent(key)}`)).json();
    const n=d.nutrition&&d.nutrition.per_100g; if(n) el.innerHTML+=`<div class=muted>${n.kcal} kcal · ${n.protein_g}g protein · ${n.fat_g}g fat</div>`;
  }catch(e){}
}
function addBasket(key){ if(!basket.includes(key)){basket.push(key);renderBasket();} }
function renderBasket(){
  const b=document.getElementById('basket');
  b.innerHTML=basket.length?basket.map(k=>`<span class="chip add" onclick="rmBasket('${k}')">${disp(k)} ✕</span>`).join(''):'<span class=muted>double-click nodes to add</span>';
}
function rmBasket(k){basket=basket.filter(x=>x!==k);renderBasket();}
async function build(){
  const out=document.getElementById('recipe');
  if(basket.length<2){out.innerHTML='<div class=muted style="margin-top:8px">Add at least two ingredients.</div>';return;}
  out.innerHTML='<div class=muted style="margin-top:8px">Thinking…</div>';
  const type=document.getElementById('rtype').value;
  try{
    const r=await (await fetch('/v1/recipe',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({ingredients:basket,type})})).json();
    out.innerHTML=`<div class=rip><b>${r.suggestion}</b>${r.shared_theme&&r.shared_theme.length?`<div class=muted style="margin-top:6px">flavour bridge: ${r.shared_theme.slice(0,6).join(', ')}</div>`:''}</div>`;
  }catch(e){ out.innerHTML='<div class=muted>Could not build.</div>'; }
}
function start(){ ensure(); nodes.clear(); edges.clear(); expanded.clear();
  const k=document.getElementById('q').value.trim().toLowerCase().replace(/ /g,'_');
  addNode(k,null); focus(k);
}
window.addEventListener('load',start);
</script></body></html>"""
