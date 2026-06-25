"""IngredientAI API — FastAPI entrypoint. Serves the interactive pairing-graph
explorer at / (desktop) and the native mobile card UI to phones, plus the /v1
endpoints (Supabase-backed in production). Override with ?view=graph|mobile."""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse

from settings import settings
from routes import pairing
from mobile import MOBILE_HTML

app = FastAPI(title="IngredientAI API", version="0.5.2")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in settings.cors_origins.split(",")],
    allow_methods=["*"], allow_headers=["*"],
)
app.include_router(pairing.router)


@app.get("/health")
def health():
    return {"status": "ok", "environment": settings.environment, "version": "0.5.2"}


def _is_phone(ua: str) -> bool:
    ua = ua.lower()
    if "ipad" in ua:  # tablets get the desktop graph
        return False
    return any(s in ua for s in ("iphone", "android", "ipod", "blackberry", "windows phone", "mobile"))


@app.get("/", response_class=HTMLResponse)
def home(request: Request, view: str = ""):
    if view == "graph":
        return INDEX_HTML
    if view == "mobile" or _is_phone(request.headers.get("user-agent", "")):
        return MOBILE_HTML
    return INDEX_HTML


INDEX_HTML = """<!doctype html><html lang=en><head><meta charset=utf-8>
<meta name=viewport content="width=device-width,initial-scale=1,maximum-scale=1,user-scalable=no"><title>IngredientAI</title>
<script src="https://cdnjs.cloudflare.com/ajax/libs/vis-network/9.1.9/standalone/umd/vis-network.min.js"></script>
<style>
:root{--bg:#faf9f6;--card:#fff;--line:#e7e4dc;--ink:#22201b;--mut:#6f6b61;--accent:#1d9e75}
*{box-sizing:border-box}html,body{margin:0;height:100%}
body{background:var(--bg);color:var(--ink);font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;display:flex;flex-direction:column;height:100vh;height:100dvh}
header{padding:10px 16px;border-bottom:1px solid var(--line);display:flex;gap:8px;align-items:center;flex-wrap:wrap}
h1{font-size:17px;font-weight:600;margin:0 14px 0 0}
input,select{border:1px solid var(--line);border-radius:9px;padding:8px 10px;font-size:14px;background:#fff}
input{min-width:160px}
.toggle{display:inline-flex;border:1px solid var(--line);border-radius:9px;overflow:hidden}
.toggle button{border:0;background:#fff;padding:8px 12px;font-size:12.5px;cursor:pointer}.toggle button.on{background:var(--accent);color:#fff}
button.go{border:1px solid var(--line);background:#fff;border-radius:9px;padding:8px 13px;font-size:13px;cursor:pointer}
a.go{text-decoration:none;color:var(--ink)}
.main{flex:1;display:flex;min-height:0}
#graph{flex:1;min-width:0}
.side{width:312px;border-left:1px solid var(--line);padding:14px;overflow:auto;background:#fff;-webkit-overflow-scrolling:touch}
.h{font-size:12px;font-weight:600;color:var(--mut);text-transform:uppercase;letter-spacing:.05em;margin:16px 0 7px}
.notes{font-size:13px}.notes b{color:var(--accent)}
.chips{display:flex;flex-wrap:wrap;gap:6px}
.chip{border:1px solid var(--line);border-radius:999px;padding:4px 10px;font-size:12px;background:#f3f6f4;cursor:pointer}
.chip.add{background:var(--accent);color:#fff;border-color:var(--accent)}
.tchip{border:1px solid var(--line);border-radius:9px;padding:8px 9px;font-size:12.5px;background:#f7f6f2;cursor:pointer;margin-bottom:6px;display:block}
.rip{font-size:13.5px;line-height:1.5;margin-top:8px;background:#f7f6f2;border:1px solid var(--line);border-radius:10px;padding:10px}
.muted{color:var(--mut);font-size:12px}
.hint{font-size:12px;color:var(--mut);padding:6px 16px;border-top:1px solid var(--line)}
.badge{display:inline-block;font-size:10px;font-weight:600;text-transform:uppercase;letter-spacing:.04em;padding:1px 6px;border-radius:6px;color:#fff;vertical-align:middle}
.b-classic{background:#1d9e75}.b-recommended{background:#4f9fd0}.b-interesting{background:#9a958b}.b-bold{background:#d9883b}
.b-recipe{background:#1d9e75}.b-aroma{background:#9b6fc0}
.legend{font-size:11px;color:var(--mut);display:flex;gap:8px;flex-wrap:wrap;align-items:center}
.row{display:flex;gap:6px}.row input{min-width:0;flex:1}
#tolist{display:none}
@media (max-width:760px){
  header{padding:8px 10px;gap:6px}
  h1{font-size:15px;margin:0;order:1}
  #tolist{display:inline-block;order:2}
  #lang{order:3;margin-left:auto}
  #q{order:4;flex:1 1 100%;min-width:0}
  #btnExplore{order:5}
  .toggle{order:6;flex:1 1 auto}
  .toggle button{flex:1}
  .legend{display:none}
  .main{flex-direction:column}
  #graph{height:46vh;flex:0 0 auto;border-bottom:1px solid var(--line)}
  .side{width:100%;border-left:0;flex:1 1 auto;min-height:0;padding:12px 14px 22px}
  .h{margin:13px 0 6px}
  .hint{display:none}
  input,select,button.go,.toggle button{font-size:16px}
  .tchip,.chip{padding:9px 11px;font-size:13px}
}
</style></head><body>
<header>
  <h1>IngredientAI</h1>
  <a href="/" id=tolist class=go>← Cards</a>
  <input id=q placeholder="Start with an ingredient…" value="garlic" onkeydown="if(event.key==='Enter')start()">
  <button id=btnExplore class=go onclick=start()>Explore</button>
  <div class=toggle><button data-m=safe onclick="setMode('safe')">Safe</button><button data-m=balanced class=on onclick="setMode('balanced')">Balanced</button><button data-m=experimental onclick="setMode('experimental')">Experimental</button></div>
  <select id=lang onchange="loadLang(this.value)"><option value=en>English</option><option value=pt>Português</option><option value=es>Español</option><option value=it>Italiano</option><option value=de>Deutsch</option><option value=fr>Français</option></select>
  <span class=legend><span class=badge style="background:#1d9e75">classic</span><span class=badge style="background:#4f9fd0">recommended</span><span class=badge style="background:#9a958b">interesting</span><span class=badge style="background:#d9883b">bold</span></span>
</header>
<div class=main>
  <div id=graph></div>
  <div class=side>
    <div class=h id=focusH>Focused</div>
    <div id=focus class=muted></div>
    <div class=h id=triosH>Flavour trios</div>
    <div id=trios class=muted></div>
    <div class=h id=bridgeH>Bridge two ingredients</div>
    <div class=row><input id=ba placeholder="strawberry"><input id=bc placeholder="basil"></div>
    <button id=bridgeBtn class=go style="margin-top:6px" onclick=doBridge()>Find the bridge</button>
    <div id=bridgeout></div>
    <div class=h id=recipeH>Your recipe</div>
    <div id=basket class=chips></div>
    <div class=h id=makeitH>Make it a…</div>
    <select id=rtype><option value=salad>salad</option><option value="pasta sauce">pasta sauce</option><option value="main dish">main dish</option><option value=marinade>marinade</option><option value=dessert>dessert</option><option value=cocktail>cocktail</option><option value=soup>soup</option><option value=dressing>dressing</option></select>
    <button id=buildBtn class=go style="margin-top:8px" onclick=build()>Build it</button>
    <div id=recipe></div>
  </div>
</div>
<div class=hint id=foot></div>
<script>
let mode='balanced', net, nodes, edges, expanded=new Set(), basket=[];
let lang='en', NAMES={}, NOTES={};
const isMobile=()=>window.matchMedia('(max-width:760px)').matches;
const I18N={
 en:{ph_start:"Start with an ingredient…",explore:"Explore",m_safe:"Safe",m_balanced:"Balanced",m_experimental:"Experimental",t_classic:"classic",t_recommended:"recommended",t_interesting:"interesting",t_bold:"bold",focused:"Focused",focus_hint:"Click a node to expand it · double-click to add to recipe.",trios:"Flavour trios",trios_hint:"Affinities-in-threes appear here.",trios_finding:"finding trios…",trios_none:"No strong trios found.",trios_err:"Trios unavailable.",bridge_h:"Bridge two ingredients",bridge_btn:"Find the bridge",bridging:"Bridging…",bridge_enter:"Enter two ingredients.",bridge_none:"No bridge found between these two.",bridge_err:"Bridge unavailable.",recipe_h:"Your recipe",recipe_hint:"double-click nodes to add",makeit:"Make it a…",buildit:"Build it",thinking:"Thinking…",need2:"Add at least two ingredients.",build_fail:"Could not build.",flav_bridge:"flavour bridge",addrecipe:"+ recipe",protein:"protein",fat:"fat",nodirect:"%a and %c don't pair directly — try bridging through:",connectors:"Connectors between %a and %c:",foot:"Pairings ranked by recipe co-occurrence + flavour notes. Tiers reflect affinity strength. Click any node to grow the web. Trios = affinities-in-threes; Bridge links ingredients that don't directly pair."},
 pt:{ph_start:"Comece com um ingrediente…",explore:"Explorar",m_safe:"Seguro",m_balanced:"Equilibrado",m_experimental:"Experimental",t_classic:"clássico",t_recommended:"recomendado",t_interesting:"interessante",t_bold:"ousado",focused:"Em foco",focus_hint:"Clique num nó para expandir · clique duplo para adicionar à receita.",trios:"Trios de sabor",trios_hint:"As afinidades em trio aparecem aqui.",trios_finding:"buscando trios…",trios_none:"Nenhum trio forte encontrado.",trios_err:"Trios indisponíveis.",bridge_h:"Conectar dois ingredientes",bridge_btn:"Encontrar a ponte",bridging:"Conectando…",bridge_enter:"Digite dois ingredientes.",bridge_none:"Nenhuma ponte encontrada entre os dois.",bridge_err:"Ponte indisponível.",recipe_h:"Sua receita",recipe_hint:"clique duplo nos nós para adicionar",makeit:"Transforme em…",buildit:"Criar",thinking:"Pensando…",need2:"Adicione pelo menos dois ingredientes.",build_fail:"Não foi possível criar.",flav_bridge:"ponte de sabor",addrecipe:"+ receita",protein:"proteína",fat:"gordura",nodirect:"%a e %c não combinam diretamente — tente conectar através de:",connectors:"Conectores entre %a e %c:",foot:"Combinações ordenadas por coocorrência em receitas + notas de sabor. Os níveis refletem a força da afinidade. Clique em qualquer nó para expandir. Trios = afinidades em três; a Ponte liga ingredientes que não combinam diretamente."},
 es:{ph_start:"Empieza con un ingrediente…",explore:"Explorar",m_safe:"Seguro",m_balanced:"Equilibrado",m_experimental:"Experimental",t_classic:"clásico",t_recommended:"recomendado",t_interesting:"interesante",t_bold:"atrevido",focused:"Enfocado",focus_hint:"Haz clic en un nodo para expandir · doble clic para añadir a la receta.",trios:"Tríos de sabor",trios_hint:"Las afinidades en trío aparecen aquí.",trios_finding:"buscando tríos…",trios_none:"No se encontraron tríos fuertes.",trios_err:"Tríos no disponibles.",bridge_h:"Conectar dos ingredientes",bridge_btn:"Encontrar el puente",bridging:"Conectando…",bridge_enter:"Introduce dos ingredientes.",bridge_none:"No se encontró puente entre estos dos.",bridge_err:"Puente no disponible.",recipe_h:"Tu receta",recipe_hint:"doble clic en los nodos para añadir",makeit:"Conviértelo en…",buildit:"Crear",thinking:"Pensando…",need2:"Añade al menos dos ingredientes.",build_fail:"No se pudo crear.",flav_bridge:"puente de sabor",addrecipe:"+ receta",protein:"proteína",fat:"grasa",nodirect:"%a y %c no combinan directamente — prueba a conectar mediante:",connectors:"Conectores entre %a y %c:",foot:"Maridajes ordenados por coaparición en recetas + notas de sabor. Los niveles reflejan la fuerza de la afinidad. Haz clic en cualquier nodo para expandir. Tríos = afinidades de tres; el Puente une ingredientes que no combinan directamente."},
 it:{ph_start:"Inizia con un ingrediente…",explore:"Esplora",m_safe:"Sicuro",m_balanced:"Bilanciato",m_experimental:"Sperimentale",t_classic:"classico",t_recommended:"consigliato",t_interesting:"interessante",t_bold:"audace",focused:"In evidenza",focus_hint:"Clicca un nodo per espandere · doppio clic per aggiungere alla ricetta.",trios:"Trii di sapore",trios_hint:"Le affinità a tre appaiono qui.",trios_finding:"ricerca trii…",trios_none:"Nessun trio forte trovato.",trios_err:"Trii non disponibili.",bridge_h:"Collega due ingredienti",bridge_btn:"Trova il ponte",bridging:"Collegamento…",bridge_enter:"Inserisci due ingredienti.",bridge_none:"Nessun ponte trovato tra i due.",bridge_err:"Ponte non disponibile.",recipe_h:"La tua ricetta",recipe_hint:"doppio clic sui nodi per aggiungere",makeit:"Trasformalo in…",buildit:"Crea",thinking:"Sto pensando…",need2:"Aggiungi almeno due ingredienti.",build_fail:"Impossibile creare.",flav_bridge:"ponte di sapore",addrecipe:"+ ricetta",protein:"proteine",fat:"grassi",nodirect:"%a e %c non si abbinano direttamente — prova a collegarli tramite:",connectors:"Connettori tra %a e %c:",foot:"Abbinamenti ordinati per co-occorrenza nelle ricette + note aromatiche. I livelli riflettono la forza dell'affinità. Clicca un nodo per espandere. Trii = affinità a tre; il Ponte collega ingredienti che non si abbinano direttamente."},
 de:{ph_start:"Mit einer Zutat beginnen…",explore:"Entdecken",m_safe:"Sicher",m_balanced:"Ausgewogen",m_experimental:"Experimentell",t_classic:"klassisch",t_recommended:"empfohlen",t_interesting:"interessant",t_bold:"gewagt",focused:"Fokus",focus_hint:"Knoten anklicken zum Erweitern · Doppelklick zum Hinzufügen zum Rezept.",trios:"Geschmackstrios",trios_hint:"Dreier-Affinitäten erscheinen hier.",trios_finding:"suche Trios…",trios_none:"Keine starken Trios gefunden.",trios_err:"Trios nicht verfügbar.",bridge_h:"Zwei Zutaten verbinden",bridge_btn:"Brücke finden",bridging:"Verbinde…",bridge_enter:"Zwei Zutaten eingeben.",bridge_none:"Keine Brücke zwischen beiden gefunden.",bridge_err:"Brücke nicht verfügbar.",recipe_h:"Dein Rezept",recipe_hint:"Doppelklick auf Knoten zum Hinzufügen",makeit:"Mach daraus…",buildit:"Erstellen",thinking:"Denke nach…",need2:"Mindestens zwei Zutaten hinzufügen.",build_fail:"Erstellen fehlgeschlagen.",flav_bridge:"Geschmacksbrücke",addrecipe:"+ Rezept",protein:"Eiweiß",fat:"Fett",nodirect:"%a und %c passen nicht direkt zusammen — versuche eine Brücke über:",connectors:"Verbindungen zwischen %a und %c:",foot:"Kombinationen nach Rezept-Kookkurrenz + Aromanoten sortiert. Stufen zeigen die Stärke der Affinität. Klicke einen Knoten zum Erweitern. Trios = Dreier-Affinitäten; die Brücke verbindet Zutaten, die nicht direkt zusammenpassen."},
 fr:{ph_start:"Commencez par un ingrédient…",explore:"Explorer",m_safe:"Sûr",m_balanced:"Équilibré",m_experimental:"Expérimental",t_classic:"classique",t_recommended:"recommandé",t_interesting:"intéressant",t_bold:"audacieux",focused:"Sélection",focus_hint:"Cliquez sur un nœud pour développer · double-clic pour ajouter à la recette.",trios:"Trios de saveurs",trios_hint:"Les affinités à trois apparaissent ici.",trios_finding:"recherche de trios…",trios_none:"Aucun trio fort trouvé.",trios_err:"Trios indisponibles.",bridge_h:"Relier deux ingrédients",bridge_btn:"Trouver le pont",bridging:"Liaison…",bridge_enter:"Saisissez deux ingrédients.",bridge_none:"Aucun pont trouvé entre les deux.",bridge_err:"Pont indisponible.",recipe_h:"Votre recette",recipe_hint:"double-cliquez sur les nœuds pour ajouter",makeit:"Transformer en…",buildit:"Créer",thinking:"Réflexion…",need2:"Ajoutez au moins deux ingrédients.",build_fail:"Création impossible.",flav_bridge:"pont de saveurs",addrecipe:"+ recette",protein:"protéines",fat:"lipides",nodirect:"%a et %c ne s'accordent pas directement — essayez un pont via :",connectors:"Connecteurs entre %a et %c :",foot:"Accords classés par co-occurrence dans les recettes + notes aromatiques. Les niveaux reflètent la force de l'affinité. Cliquez sur un nœud pour développer. Trios = affinités à trois ; le Pont relie des ingrédients qui ne s'accordent pas directement."}
};
const RT={en:["salad","pasta sauce","main dish","marinade","dessert","cocktail","soup","dressing"],
 pt:["salada","molho de massa","prato principal","marinada","sobremesa","coquetel","sopa","molho"],
 es:["ensalada","salsa para pasta","plato principal","adobo","postre","cóctel","sopa","aliño"],
 it:["insalata","sugo per pasta","piatto principale","marinata","dessert","cocktail","zuppa","condimento"],
 de:["Salat","Pastasauce","Hauptgericht","Marinade","Dessert","Cocktail","Suppe","Dressing"],
 fr:["salade","sauce pour pâtes","plat principal","marinade","dessert","cocktail","soupe","vinaigrette"]};
const TIER={classic:'#1d9e75',recommended:'#4f9fd0',interesting:'#9a958b',bold:'#d9883b'};
const TW={classic:3,recommended:2.1,interesting:1.3,bold:1.7};
function t(k){ return (I18N[lang]&&I18N[lang][k])||I18N.en[k]||k; }
const cap=s=>s?s.charAt(0).toUpperCase()+s.slice(1):s;
function disp(key){ if(lang!=='en'&&NAMES[key]) return cap(NAMES[key]); return key.replace(/_/g,' ').replace(/\\b\\w/g,c=>c.toUpperCase()); }
function dnote(n){ return (lang!=='en'&&NOTES[n])?NOTES[n]:n; }
const CAT={Fruit:'#e07a5f',Spice:'#d9883b',Dairy:'#4f9fd0','Plant/Vegetable':'#3a9d5d','Vegetable':'#3a9d5d','Meat':'#c1554f','Meat/Animal Product':'#c1554f',Seafood:'#3a8fc4','Nut/Seed':'#b07a3c','Beverage Alcoholic':'#9b6fc0','Beverage':'#7a9bd0',Flower:'#d07aa8',Fungus:'#8a7d6b','Condiment':'#a89a6a','Bakery/Dessert':'#caa06a','Bakery/Dessert/Snack':'#caa06a'};
function color(cat){return CAT[cat]||'#8a9a8e'}
function setMode(m){mode=m;document.querySelectorAll('.toggle button').forEach(b=>b.className=b.dataset.m===m?'on':'');}
function applyStatic(){
  document.getElementById('q').placeholder=t('ph_start');
  document.getElementById('btnExplore').textContent=t('explore');
  document.querySelector('[data-m=safe]').textContent=t('m_safe');
  document.querySelector('[data-m=balanced]').textContent=t('m_balanced');
  document.querySelector('[data-m=experimental]').textContent=t('m_experimental');
  const lg=document.querySelectorAll('.legend .badge');
  lg[0].textContent=t('t_classic');lg[1].textContent=t('t_recommended');lg[2].textContent=t('t_interesting');lg[3].textContent=t('t_bold');
  document.getElementById('focusH').textContent=t('focused');
  document.getElementById('triosH').textContent=t('trios');
  document.getElementById('bridgeH').textContent=t('bridge_h');
  document.getElementById('bridgeBtn').textContent=t('bridge_btn');
  document.getElementById('recipeH').textContent=t('recipe_h');
  document.getElementById('makeitH').textContent=t('makeit');
  document.getElementById('buildBtn').textContent=t('buildit');
  document.getElementById('foot').textContent=t('foot');
  const rt=RT[lang]||RT.en, sel=document.getElementById('rtype');
  [].forEach.call(sel.options,(o,i)=>{ o.textContent=rt[i]; });
}
async function loadLang(l){
  lang=l; document.getElementById('lang').value=l;
  if(l==='en'){ NAMES={}; NOTES={}; }
  else{ try{ const d=await (await fetch(`/v1/i18n/${l}`)).json(); NAMES=d.names||{}; NOTES=d.notes||{}; }catch(e){ NAMES={};NOTES={}; } }
  applyStatic(); start();
}
function ensure(){
  if(net)return;
  nodes=new vis.DataSet([]); edges=new vis.DataSet([]);
  window.nodes=nodes; window.edges=edges; window.expand=expand;
  const mob=isMobile();
  net=new vis.Network(document.getElementById('graph'),{nodes,edges},{
    physics:false,
    nodes:{shape:'dot',size:mob?20:15,borderWidth:2,color:{border:'#fff'},font:{size:mob?16:14,color:'#22201b'}},
    edges:{color:{color:'#d8d3c8',highlight:'#1d9e75',hover:'#1d9e75'},width:1.5,
      font:{size:mob?12:10,color:'#6f6b61',strokeWidth:4,strokeColor:'#faf9f6',align:'middle'},
      smooth:{type:'curvedCW',roundness:0.12}},
    interaction:{hover:true,dragNodes:true,dragView:true,zoomView:true,tooltipDelay:120}
  });
  net.on('click',p=>{ if(p.nodes.length){ showFocus(p.nodes[0]); expand(p.nodes[0]); }});
  net.on('doubleClick',p=>{ if(p.nodes.length) addBasket(p.nodes[0]); });
}
function pos(id){ try{ return net.getPositions([id])[id]; }catch(e){ return {x:0,y:0}; } }
function nodeCat(key){ const n=nodes.get(key); return n?n.cat:null; }
function addNodeAt(key,cat,x,y){ if(nodes.get(key)) return false; nodes.add({id:key,label:disp(key),cat,color:color(cat),x,y}); return true; }
async function expand(key,lim){
  lim=lim||10;
  if(expanded.has(key+'|'+mode)) return []; expanded.add(key+'|'+mode);
  nodes.update({id:key,borderWidth:4,color:{border:'#1d9e75',background:color(nodeCat(key))}});
  let d; try{ d=await (await fetch(`/v1/pair/${encodeURIComponent(key)}?mode=${mode}&limit=${lim}`)).json(); }catch(e){ return []; }
  if(!d.pairings||!d.pairings.length) return [];
  const pp=pos(key), n=d.pairings.length, R=isMobile()?130:200, base=(key.length%6);
  d.pairings.forEach((p,i)=>{
    const a=base+(i/n)*2*Math.PI;
    addNodeAt(p.ingredient,p.category, pp.x+R*Math.cos(a)+(Math.random()*30-15), pp.y+R*Math.sin(a)+(Math.random()*30-15));
    const eid=key+'|'+p.ingredient;
    const notes=(p.explanation.shared_notes||[]).map(dnote); const tier=p.tier||'';
    if(!edges.get(eid)&&!edges.get(p.ingredient+'|'+key))
      edges.add({id:eid,from:key,to:p.ingredient,label:notes[0]||'',
        title:(tier?t('t_'+tier).toUpperCase()+' · ':'')+(notes.join(', ')||''),
        width:TW[tier]||1.5, color:{color:(TIER[tier]||'#d8d3c8'),highlight:TIER[tier]||'#1d9e75'}});
  });
  return d.pairings.map(p=>p.ingredient);
}
async function showFocus(key){
  const el=document.getElementById('focus');
  el.innerHTML=`<b style="font-size:15px">${disp(key)}</b> <button class=go style="padding:3px 8px;font-size:11px" onclick="addBasket('${key}')">${t('addrecipe')}</button>`;
  try{ const d=await (await fetch(`/v1/ingredient/${encodeURIComponent(key)}`)).json();
    const n=d.nutrition&&d.nutrition.per_100g; if(n) el.innerHTML+=`<div class=muted style="margin-top:5px">${n.kcal} kcal · ${n.protein_g}g ${t('protein')} · ${n.fat_g}g ${t('fat')}</div>`;
  }catch(e){}
  document.getElementById('ba').value=disp(key);
  loadTrios(key);
}
async function loadTrios(key){
  const tt=document.getElementById('trios'); tt.innerHTML=`<span class=muted>${t('trios_finding')}</span>`;
  try{
    const d=await (await fetch(`/v1/trio/${encodeURIComponent(key)}?limit=6`)).json();
    if(!d.trios||!d.trios.length){ tt.innerHTML=`<span class=muted>${t('trios_none')}</span>`; return; }
    tt.innerHTML=d.trios.map(x=>`<span class=tchip onclick="addBasket('${key}');addBasket('${x.a}');addBasket('${x.b}')">${disp(key)} + <b>${disp(x.a)}</b> + <b>${disp(x.b)}</b></span>`).join('');
  }catch(e){ tt.innerHTML=`<span class=muted>${t('trios_err')}</span>`; }
}
async function doBridge(){
  const a=document.getElementById('ba').value.trim().toLowerCase().replace(/ /g,'_');
  const c=document.getElementById('bc').value.trim().toLowerCase().replace(/ /g,'_');
  const out=document.getElementById('bridgeout');
  if(!a||!c){ out.innerHTML=`<div class=muted style="margin-top:6px">${t('bridge_enter')}</div>`; return; }
  out.innerHTML=`<div class=muted style="margin-top:6px">${t('bridging')}</div>`;
  try{
    const d=await (await fetch(`/v1/bridge?a=${encodeURIComponent(a)}&c=${encodeURIComponent(c)}&limit=6`)).json();
    if(!d.bridges||!d.bridges.length){ out.innerHTML=`<div class=muted style="margin-top:6px">${t('bridge_none')}</div>`; return; }
    const direct=d.bridges[0].direct_link;
    const tmpl=(direct!=null&&direct<=0)?t('nodirect'):t('connectors');
    const head=`<div class=muted style="margin-top:6px">${tmpl.replace('%a',disp(a)).replace('%c',disp(c))}</div>`;
    out.innerHTML=head+'<div style="margin-top:6px">'+d.bridges.map(b=>`<span class=tchip onclick="addBasket('${a}');addBasket('${b.bridge}');addBasket('${c}')"><b>${disp(b.bridge)}</b> <span class="badge b-${b.via}">${b.via}</span></span>`).join('')+'</div>';
  }catch(e){ out.innerHTML=`<div class=muted style="margin-top:6px">${t('bridge_err')}</div>`; }
}
function addBasket(key){ if(!basket.includes(key)){basket.push(key);renderBasket();} }
function renderBasket(){
  const b=document.getElementById('basket');
  b.innerHTML=basket.length?basket.map(k=>`<span class="chip add" onclick="rmBasket('${k}')">${disp(k)} ✕</span>`).join(''):`<span class=muted>${t('recipe_hint')}</span>`;
}
function rmBasket(k){basket=basket.filter(x=>x!==k);renderBasket();}
async function build(){
  const out=document.getElementById('recipe');
  if(basket.length<2){out.innerHTML=`<div class=muted style="margin-top:8px">${t('need2')}</div>`;return;}
  out.innerHTML=`<div class=muted style="margin-top:8px">${t('thinking')}</div>`;
  const type=document.getElementById('rtype').value;
  try{
    const r=await (await fetch('/v1/recipe',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({ingredients:basket,type})})).json();
    const theme=(r.shared_theme||[]).map(dnote).slice(0,6);
    out.innerHTML=`<div class=rip><b>${r.suggestion}</b>${theme.length?`<div class=muted style="margin-top:6px">${t('flav_bridge')}: ${theme.join(', ')}</div>`:''}</div>`;
  }catch(e){ out.innerHTML=`<div class=muted>${t('build_fail')}</div>`; }
}
async function start(){ ensure(); nodes.clear(); edges.clear(); expanded.clear(); renderBasket();
  const raw=document.getElementById('q').value.trim().toLowerCase();
  const k=raw.replace(/ /g,'_');
  addNodeAt(k,null,0,0); net.moveTo({position:{x:0,y:0},scale:0.85}); showFocus(k);
  const firsts=await expand(k, 26);
  const topN=isMobile()?3:6;
  for(let i=0;i<Math.min(topN, firsts.length); i++){ await expand(firsts[i], 7); }
  try{ net.fit({animation:{duration:550}}); }catch(e){}
}
function init(){
  const nav=(navigator.language||'en').slice(0,2).toLowerCase();
  const start_lang=['pt','es','it','de','fr'].includes(nav)?nav:'en';
  loadLang(start_lang);
}
window.addEventListener('load',init);
</script></body></html>"""
