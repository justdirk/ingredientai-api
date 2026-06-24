"""IngredientAI API — FastAPI entrypoint. Serves the interactive pairing-graph
explorer at / plus the /v1 endpoints (Supabase-backed in production)."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse

from settings import settings
from routes import pairing

app = FastAPI(title="IngredientAI API", version="0.3.1")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in settings.cors_origins.split(",")],
    allow_methods=["*"], allow_headers=["*"],
)
app.include_router(pairing.router)


@app.get("/health")
def health():
    return {"status": "ok", "environment": settings.environment, "version": "0.3.1"}


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
input{min-width:160px}
.toggle{display:inline-flex;border:1px solid var(--line);border-radius:9px;overflow:hidden}
.toggle button{border:0;background:#fff;padding:8px 12px;font-size:12.5px;cursor:pointer}.toggle button.on{background:var(--accent);color:#fff}
button.go{border:1px solid var(--line);background:#fff;border-radius:9px;padding:8px 13px;font-size:13px;cursor:pointer}
.main{flex:1;display:flex;min-height:0}
#graph{flex:1;min-width:0}
.side{width:312px;border-left:1px solid var(--line);padding:14px;overflow:auto;background:#fff}
.h{font-size:12px;font-weight:600;color:var(--mut);text-transform:uppercase;letter-spacing:.05em;margin:16px 0 7px}
.notes{font-size:13px}.notes b{color:var(--accent)}
.chips{display:flex;flex-wrap:wrap;gap:6px}
.chip{border:1px solid var(--line);border-radius:999px;padding:4px 10px;font-size:12px;background:#f3f6f4;cursor:pointer}
.chip.add{background:var(--accent);color:#fff;border-color:var(--accent)}
.tchip{border:1px solid var(--line);border-radius:9px;padding:6px 9px;font-size:12.5px;background:#f7f6f2;cursor:pointer;margin-bottom:6px;display:block}
.rip{font-size:13.5px;line-height:1.5;margin-top:8px;background:#f7f6f2;border:1px solid var(--line);border-radius:10px;padding:10px}
.muted{color:var(--mut);font-size:12px}
.hint{font-size:12px;color:var(--mut);padding:6px 16px;border-top:1px solid var(--line)}
.badge{display:inline-block;font-size:10px;font-weight:600;text-transform:uppercase;letter-spacing:.04em;padding:1px 6px;border-radius:6px;color:#fff;vertical-align:middle}
.b-classic{background:#1d9e75}.b-recommended{background:#4f9fd0}.b-interesting{background:#9a958b}.b-bold{background:#d9883b}
.b-recipe{background:#1d9e75}.b-aroma{background:#9b6fc0}
.legend{font-size:11px;color:var(--mut);display:flex;gap:8px;flex-wrap:wrap;align-items:center}
.row{display:flex;gap:6px}.row input{min-width:0;flex:1}
</style></head><body>
<header>
  <h1>IngredientAI</h1>
  <input id=q placeholder="Start with an ingredient…" value="garlic" onkeydown="if(event.key==='Enter')start()">
  <button class=go onclick=start()>Explore</button>
  <div class=toggle><button data-m=safe onclick="setMode('safe')">Safe</button><button data-m=balanced class=on onclick="setMode('balanced')">Balanced</button><button data-m=experimental onclick="setMode('experimental')">Experimental</button></div>
  <span class=legend><span class=badge style="background:#1d9e75">classic</span><span class=badge style="background:#4f9fd0">recommended</span><span class=badge style="background:#9a958b">interesting</span><span class=badge style="background:#d9883b">bold</span></span>
</header>
<div class=main>
  <div id=graph></div>
  <div class=side>
    <div class=h>Focused</div>
    <div id=focus class=muted>Click a node to expand it · double-click to add to recipe.</div>
    <div class=h>Flavour trios</div>
    <div id=trios class=muted>Affinities-in-threes appear here.</div>
    <div class=h>Bridge two ingredients</div>
    <div class=row><input id=ba placeholder="strawberry"><input id=bc placeholder="basil"></div>
    <button class=go style="margin-top:6px" onclick=doBridge()>Find the bridge</button>
    <div id=bridgeout></div>
    <div class=h>Your recipe</div>
    <div id=basket class=chips><span class=muted>double-click nodes to add</span></div>
    <div class=h>Make it a…</div>
    <select id=rtype><option>salad</option><option>pasta sauce</option><option>main dish</option><option>marinade</option><option>dessert</option><option>cocktail</option><option>soup</option><option>dressing</option></select>
    <button class=go style="margin-top:8px" onclick=build()>Build it</button>
    <div id=recipe></div>
  </div>
</div>
<div class=hint>Pairings ranked by recipe co-occurrence + FlavorGraph2Vec + shared flavour notes. Tiers reflect affinity strength. Click any node to grow the web from it. Trios = affinities-in-threes; Bridge links ingredients that don't directly pair.</div>
<script>
let mode='balanced', net, nodes, edges, expanded=new Set(), basket=[], booted=false;
const CAT={Fruit:'#e07a5f',Spice:'#d9883b',Dairy:'#4f9fd0','Plant/Vegetable':'#3a9d5d','Vegetable':'#3a9d5d','Meat':'#c1554f','Meat/Animal Product':'#c1554f',Seafood:'#3a8fc4','Nut/Seed':'#b07a3c','Beverage Alcoholic':'#9b6fc0','Beverage':'#7a9bd0',Flower:'#d07aa8',Fungus:'#8a7d6b','Condiment':'#a89a6a','Bakery/Dessert':'#caa06a','Bakery/Dessert/Snack':'#caa06a'};
const TIER={classic:'#1d9e75',recommended:'#4f9fd0',interesting:'#9a958b',bold:'#d9883b'};
const TW={classic:3,recommended:2.1,interesting:1.3,bold:1.7};
const disp=s=>s.replace(/_/g,' ').replace(/\\b\\w/g,c=>c.toUpperCase());
function color(cat){return CAT[cat]||'#8a9a8e'}
function setMode(m){mode=m;document.querySelectorAll('.toggle button').forEach(b=>b.className=b.dataset.m===m?'on':'');}
function ensure(){
  if(net)return;
  nodes=new vis.DataSet([]); edges=new vis.DataSet([]);
  window.nodes=nodes; window.edges=edges; window.expand=expand;
  net=new vis.Network(document.getElementById('graph'),{nodes,edges},{
    physics:false,
    nodes:{shape:'dot',size:15,borderWidth:2,color:{border:'#fff'},font:{size:14,color:'#22201b'}},
    edges:{color:{color:'#d8d3c8',highlight:'#1d9e75',hover:'#1d9e75'},width:1.5,
      font:{size:10,color:'#6f6b61',strokeWidth:4,strokeColor:'#faf9f6',align:'middle'},
      smooth:{type:'curvedCW',roundness:0.12}},
    interaction:{hover:true,dragNodes:true,dragView:true,zoomView:true,tooltipDelay:120}
  });
  net.on('click',p=>{ if(p.nodes.length){ showFocus(p.nodes[0]); expand(p.nodes[0]); }});
  net.on('doubleClick',p=>{ if(p.nodes.length) addBasket(p.nodes[0]); });
}
function pos(id){ try{ return net.getPositions([id])[id]; }catch(e){ return {x:0,y:0}; } }
function nodeCat(key){ const n=nodes.get(key); return n?n.cat:null; }
function addNodeAt(key,cat,x,y){ if(nodes.get(key)) return false; nodes.add({id:key,label:disp(key),cat,color:color(cat),x,y}); return true; }
async function expand(key){
  if(expanded.has(key+'|'+mode)) return; expanded.add(key+'|'+mode);
  nodes.update({id:key,borderWidth:4,color:{border:'#1d9e75',background:color(nodeCat(key))}});
  let d; try{ d=await (await fetch(`/v1/pair/${encodeURIComponent(key)}?mode=${mode}&limit=8`)).json(); }catch(e){ return; }
  if(!d.pairings||!d.pairings.length) return;
  const pp=pos(key), n=d.pairings.length, R=175, base=(key.length%6);
  let added=0;
  d.pairings.forEach((p,i)=>{
    const a=base+(i/n)*2*Math.PI;
    if(addNodeAt(p.ingredient,p.category, pp.x+R*Math.cos(a)+(Math.random()*24-12), pp.y+R*Math.sin(a)+(Math.random()*24-12))) added++;
    const eid=key+'|'+p.ingredient;
    const notes=(p.explanation.shared_notes||[]); const tier=p.tier||'';
    if(!edges.get(eid)&&!edges.get(p.ingredient+'|'+key))
      edges.add({id:eid,from:key,to:p.ingredient,label:notes[0]||'',
        title:(tier?tier.toUpperCase()+' · ':'')+(notes.join(', ')||'similar profile'),
        width:TW[tier]||1.5, color:{color:(TIER[tier]||'#d8d3c8'),highlight:TIER[tier]||'#1d9e75'}});
  });
  // Only frame the very first expansion. Afterwards the web grows in place so a
  // click connects new pairings to the node you clicked without moving your view.
  if(!booted){ booted=true; try{ net.fit({animation:{duration:450}}); }catch(e){} }
}
async function showFocus(key){
  const el=document.getElementById('focus');
  el.innerHTML=`<b style="font-size:15px">${disp(key)}</b> <button class=go style="padding:3px 8px;font-size:11px" onclick="addBasket('${key}')">+ recipe</button>`;
  try{ const d=await (await fetch(`/v1/ingredient/${encodeURIComponent(key)}`)).json();
    const n=d.nutrition&&d.nutrition.per_100g; if(n) el.innerHTML+=`<div class=muted style="margin-top:5px">${n.kcal} kcal · ${n.protein_g}g protein · ${n.fat_g}g fat</div>`;
  }catch(e){}
  document.getElementById('ba').value=key.replace(/_/g,' ');
  loadTrios(key);
}
async function loadTrios(key){
  const t=document.getElementById('trios'); t.innerHTML='<span class=muted>finding trios…</span>';
  try{
    const d=await (await fetch(`/v1/trio/${encodeURIComponent(key)}?limit=6`)).json();
    if(!d.trios||!d.trios.length){ t.innerHTML='<span class=muted>No strong trios found.</span>'; return; }
    t.innerHTML=d.trios.map(x=>`<span class=tchip onclick="addBasket('${key}');addBasket('${x.a}');addBasket('${x.b}')">${disp(key)} + <b>${disp(x.a)}</b> + <b>${disp(x.b)}</b></span>`).join('');
  }catch(e){ t.innerHTML='<span class=muted>Trios unavailable.</span>'; }
}
async function doBridge(){
  const a=document.getElementById('ba').value.trim().toLowerCase().replace(/ /g,'_');
  const c=document.getElementById('bc').value.trim().toLowerCase().replace(/ /g,'_');
  const out=document.getElementById('bridgeout');
  if(!a||!c){ out.innerHTML='<div class=muted style="margin-top:6px">Enter two ingredients.</div>'; return; }
  out.innerHTML='<div class=muted style="margin-top:6px">Bridging…</div>';
  try{
    const d=await (await fetch(`/v1/bridge?a=${encodeURIComponent(a)}&c=${encodeURIComponent(c)}&limit=6`)).json();
    if(!d.bridges||!d.bridges.length){ out.innerHTML='<div class=muted style="margin-top:6px">No bridge found between these two.</div>'; return; }
    const direct=d.bridges[0].direct_link;
    const head=(direct!=null&&direct<=0)?`<div class=muted style="margin-top:6px">${disp(a)} and ${disp(c)} don't pair directly — try bridging through:</div>`:`<div class=muted style="margin-top:6px">Connectors between ${disp(a)} and ${disp(c)}:</div>`;
    out.innerHTML=head+'<div style="margin-top:6px">'+d.bridges.map(b=>`<span class=tchip onclick="addBasket('${a}');addBasket('${b.bridge}');addBasket('${c}')"><b>${disp(b.bridge)}</b> <span class="badge b-${b.via}">${b.via}</span></span>`).join('')+'</div>';
  }catch(e){ out.innerHTML='<div class=muted style="margin-top:6px">Bridge unavailable.</div>'; }
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
function start(){ ensure(); nodes.clear(); edges.clear(); expanded.clear(); booted=false;
  const k=document.getElementById('q').value.trim().toLowerCase().replace(/ /g,'_');
  addNodeAt(k,null,0,0); net.moveTo({position:{x:0,y:0},scale:0.9}); showFocus(k); expand(k);
}
window.addEventListener('load',start);
</script></body></html>"""
