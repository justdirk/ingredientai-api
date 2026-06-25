"""Mobile-first card UI served to phones (desktop keeps the graph explorer).
Search-first selection model: search and add ingredients to a selection, then act
on it via Explore / Trios / Bridge / Recipe. Talks to the same /v1 endpoints and
loads the localized name/note dictionaries."""

MOBILE_HTML = """<!doctype html><html lang=en><head><meta charset=utf-8>
<meta name=viewport content="width=device-width,initial-scale=1,maximum-scale=1,user-scalable=no"><title>IngredientAI</title>
<link href="https://cdnjs.cloudflare.com/ajax/libs/tabler-icons/3.30.0/tabler-icons.min.css" rel=stylesheet>
<style>
:root{--bg:#faf9f6;--card:#fff;--line:#e9e6df;--ink:#22201b;--mut:#6f6b61;--accent:#1d9e75}
*{box-sizing:border-box;-webkit-tap-highlight-color:transparent}
html,body{margin:0;height:100%}
body{background:var(--bg);color:var(--ink);font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;display:flex;flex-direction:column;height:100vh;height:100dvh}
.util{display:flex;align-items:center;gap:10px;padding:9px 16px;border-bottom:1px solid var(--line)}
.util .brand{font-weight:600;font-size:15px;flex:1}
.iconbtn{border:0;background:transparent;color:var(--mut);font-size:21px;padding:4px;line-height:1}
select{border:1px solid var(--line);border-radius:9px;padding:6px 8px;font-size:14px;background:#fff;color:var(--ink)}
.searchbar{padding:11px 16px 9px;border-bottom:1px solid var(--line);position:relative}
.searchbar input{width:100%;border:1px solid var(--line);border-radius:12px;padding:11px 13px;font-size:16px;background:#fff;color:var(--ink)}
.suggest{position:absolute;left:16px;right:16px;top:54px;background:#fff;border:1px solid var(--line);border-radius:12px;box-shadow:0 6px 22px rgba(0,0,0,.10);max-height:50vh;overflow:auto;z-index:30}
.sug{padding:12px 14px;font-size:15px;border-bottom:1px solid var(--line)}
.sug:last-child{border-bottom:0}
.selbar{display:flex;flex-wrap:wrap;gap:7px;padding:11px 16px;border-bottom:1px solid var(--line);min-height:48px;align-items:center}
.schip{display:inline-flex;align-items:center;gap:6px;background:var(--accent);color:#fff;border-radius:999px;padding:7px 8px 7px 12px;font-size:13.5px;font-weight:600}
.schip.foc{box-shadow:0 0 0 2px rgba(29,158,117,.35)}
.schip .x{font-size:15px;opacity:.85}
.selhint{color:#a7a399;font-size:13.5px}
.seg{display:flex;background:#efece4;border-radius:11px;padding:3px;gap:3px;margin:11px 16px 0}
.seg button{flex:1;border:0;background:transparent;border-radius:8px;padding:9px 0;font-size:13.5px;color:var(--mut)}
.seg button.on{background:#fff;color:var(--ink);font-weight:600}
#body{flex:1;overflow:auto;padding:14px 16px 20px;-webkit-overflow-scrolling:touch}
.exhead{font-size:13px;color:var(--mut);margin-bottom:10px}
.exhead b{color:var(--ink);font-weight:600}
.pcard{display:flex;align-items:center;gap:11px;padding:13px 14px;border:1px solid var(--line);border-radius:14px;background:#fff;margin-bottom:9px}
.pcard .nm{font-size:16px;font-weight:600;margin-bottom:2px}
.pcard .nt{font-size:13px;color:var(--mut)}
.tier{font-size:11px;font-weight:600;padding:3px 9px;border-radius:999px;white-space:nowrap}
.addb{width:32px;height:32px;border-radius:50%;border:1px solid var(--line);background:#fff;color:var(--mut);font-size:18px;flex:none}
.addb.on{background:var(--accent);color:#fff;border-color:var(--accent)}
.chev{color:#c3bfb4;font-size:19px}
.tabbar{display:flex;border-top:1px solid var(--line);background:#fff;padding-bottom:env(safe-area-inset-bottom)}
.tab{flex:1;display:flex;flex-direction:column;align-items:center;gap:2px;border:0;background:transparent;padding:9px 0 8px;font-size:11px;color:#a7a399}
.tab.on{color:var(--accent)}
.tab i{font-size:22px}
.sub{font-size:13px;color:var(--mut);margin-bottom:12px;line-height:1.5}
.bigbtn{width:100%;border:1px solid var(--line);background:#fff;border-radius:12px;padding:13px;font-size:15px;font-weight:600;color:var(--ink)}
.bigbtn.prim{background:var(--accent);color:#fff;border-color:var(--accent)}
.tin{flex:1;min-width:0;border:1px solid var(--line);border-radius:11px;padding:11px;font-size:15px;text-align:center;background:#fff;color:var(--ink)}
.empty{text-align:center;color:#a7a399;font-size:14px;padding:40px 12px}
.empty i{font-size:34px;display:block;margin-bottom:10px}
</style></head><body>
<div class=util>
  <span class=brand>IngredientAI</span>
  <a class=iconbtn href="?view=graph" aria-label="Graph view"><i class="ti ti-affiliate"></i></a>
  <select id=lang onchange="setLang(this.value)"><option value=en>EN</option><option value=pt>PT</option><option value=es>ES</option><option value=it>IT</option><option value=de>DE</option><option value=fr>FR</option></select>
</div>
<div class=searchbar>
  <input id=searchin placeholder="Search an ingredient" autocomplete=off>
  <div id=suggest class=suggest style="display:none"></div>
</div>
<div id=selbar class=selbar></div>
<div class=seg id=seg><button data-m=safe>Safe</button><button data-m=balanced class=on>Balanced</button><button data-m=surprising>Surprising</button></div>
<div id=body></div>
<div class=tabbar id=tabbar>
  <button class="tab on" data-t=explore><i class="ti ti-grain"></i><span data-k=tExplore>Explore</span></button>
  <button class=tab data-t=trios><i class="ti ti-triangle"></i><span data-k=tTrios>Trios</span></button>
  <button class=tab data-t=bridge><i class="ti ti-arrows-left-right"></i><span data-k=tBridge>Bridge</span></button>
  <button class=tab data-t=recipe><i class="ti ti-basket"></i><span data-k=tRecipe>Recipe</span></button>
</div>
<script>
var TB={classic:['#E1F5EE','#0F6E56'],recommended:['#E6F1FB','#185FA5'],interesting:['#F1EFE8','#5F5E5A'],bold:['#FAEEDA','#854F0B']};
var CATC={'Fruit':'#e07a5f','Spice':'#d9883b','Dairy':'#4f9fd0','Plant/Vegetable':'#3a9d5d','Vegetable':'#3a9d5d','Meat':'#c1554f','Meat/Animal Product':'#c1554f','Seafood':'#3a8fc4','Nut/Seed':'#b07a3c','Beverage Alcoholic':'#9b6fc0','Beverage':'#7a9bd0','Flower':'#d07aa8','Fungus':'#8a7d6b','Condiment':'#a89a6a','Bakery/Dessert':'#caa06a'};
var M={
 en:{safe:'Safe',balanced:'Balanced',surprising:'Surprising',tExplore:'Explore',tTrios:'Trios',tBridge:'Bridge',tRecipe:'Recipe',searchph:'Search an ingredient',start:'Search and add an ingredient to begin.',exploring:'Pairings for',addhint:'Tap + to add to your selection',selempty:'No ingredients yet — search above',needone:'Add an ingredient to your selection first.',tap:'Tap a card to explore it further',triosub:'Three-way affinities with',bridgesub:"What links two ingredients that don't pair directly.",findbridge:'Find the bridge',nobridge:'No bridge found between these two.',nopair:'No pairings found.',makeit:'Make it a',build:'Build it',need2:'Add at least two ingredients to your selection.',buildfail:'Could not build.',flav:'flavour bridge',directno:"%a and %c don't pair directly — bridge through:",connect:'Connectors between %a and %c:',enter2:'Pick two ingredients.',thinking:'Thinking…',via_recipe:'recipe',via_aroma:'aroma'},
 pt:{safe:'Seguro',balanced:'Equilibrado',surprising:'Surpreendente',tExplore:'Explorar',tTrios:'Trios',tBridge:'Ponte',tRecipe:'Receita',searchph:'Buscar um ingrediente',start:'Busque e adicione um ingrediente para começar.',exploring:'Combinações de',addhint:'Toque em + para adicionar à seleção',selempty:'Nenhum ingrediente ainda — busque acima',needone:'Adicione um ingrediente à seleção primeiro.',tap:'Toque num cartão para explorar',triosub:'Afinidades em três com',bridgesub:'O que liga dois ingredientes que não combinam diretamente.',findbridge:'Encontrar a ponte',nobridge:'Nenhuma ponte encontrada entre os dois.',nopair:'Nenhuma combinação encontrada.',makeit:'Transforme em',build:'Criar',need2:'Adicione pelo menos dois ingredientes à seleção.',buildfail:'Não foi possível criar.',flav:'ponte de sabor',directno:'%a e %c não combinam diretamente — conecte através de:',connect:'Conectores entre %a e %c:',enter2:'Escolha dois ingredientes.',thinking:'Pensando…',via_recipe:'receita',via_aroma:'aroma'},
 es:{safe:'Seguro',balanced:'Equilibrado',surprising:'Sorprendente',tExplore:'Explorar',tTrios:'Tríos',tBridge:'Puente',tRecipe:'Receta',searchph:'Buscar un ingrediente',start:'Busca y añade un ingrediente para empezar.',exploring:'Maridajes de',addhint:'Toca + para añadir a tu selección',selempty:'Aún no hay ingredientes — busca arriba',needone:'Añade un ingrediente a tu selección primero.',tap:'Toca una tarjeta para explorar',triosub:'Afinidades de tres con',bridgesub:'Qué une dos ingredientes que no combinan directamente.',findbridge:'Encontrar el puente',nobridge:'No se encontró puente entre estos dos.',nopair:'No se encontraron maridajes.',makeit:'Conviértelo en',build:'Crear',need2:'Añade al menos dos ingredientes a tu selección.',buildfail:'No se pudo crear.',flav:'puente de sabor',directno:'%a y %c no combinan directamente — conecta mediante:',connect:'Conectores entre %a y %c:',enter2:'Elige dos ingredientes.',thinking:'Pensando…',via_recipe:'receta',via_aroma:'aroma'},
 it:{safe:'Sicuro',balanced:'Bilanciato',surprising:'Sorprendente',tExplore:'Esplora',tTrios:'Trii',tBridge:'Ponte',tRecipe:'Ricetta',searchph:'Cerca un ingrediente',start:'Cerca e aggiungi un ingrediente per iniziare.',exploring:'Abbinamenti di',addhint:'Tocca + per aggiungere alla selezione',selempty:'Ancora nessun ingrediente — cerca sopra',needone:'Aggiungi prima un ingrediente alla selezione.',tap:'Tocca una scheda per esplorare',triosub:'Affinità a tre con',bridgesub:'Cosa collega due ingredienti che non si abbinano direttamente.',findbridge:'Trova il ponte',nobridge:'Nessun ponte trovato tra i due.',nopair:'Nessun abbinamento trovato.',makeit:'Trasformalo in',build:'Crea',need2:'Aggiungi almeno due ingredienti alla selezione.',buildfail:'Impossibile creare.',flav:'ponte di sapore',directno:'%a e %c non si abbinano direttamente — collega tramite:',connect:'Connettori tra %a e %c:',enter2:'Scegli due ingredienti.',thinking:'Sto pensando…',via_recipe:'ricetta',via_aroma:'aroma'},
 de:{safe:'Sicher',balanced:'Ausgewogen',surprising:'Überraschend',tExplore:'Entdecken',tTrios:'Trios',tBridge:'Brücke',tRecipe:'Rezept',searchph:'Zutat suchen',start:'Suche und füge eine Zutat hinzu, um zu beginnen.',exploring:'Kombinationen für',addhint:'Tippe +, um zur Auswahl hinzuzufügen',selempty:'Noch keine Zutaten — oben suchen',needone:'Füge zuerst eine Zutat zur Auswahl hinzu.',tap:'Tippe eine Karte zum Erkunden',triosub:'Dreier-Affinitäten mit',bridgesub:'Was zwei Zutaten verbindet, die nicht direkt zusammenpassen.',findbridge:'Brücke finden',nobridge:'Keine Brücke zwischen beiden gefunden.',nopair:'Keine Kombinationen gefunden.',makeit:'Mach daraus',build:'Erstellen',need2:'Füge mindestens zwei Zutaten zur Auswahl hinzu.',buildfail:'Erstellen fehlgeschlagen.',flav:'Geschmacksbrücke',directno:'%a und %c passen nicht direkt zusammen — Brücke über:',connect:'Verbindungen zwischen %a und %c:',enter2:'Wähle zwei Zutaten.',thinking:'Denke nach…',via_recipe:'Rezept',via_aroma:'Aroma'},
 fr:{safe:'Sûr',balanced:'Équilibré',surprising:'Surprenant',tExplore:'Explorer',tTrios:'Trios',tBridge:'Pont',tRecipe:'Recette',searchph:'Chercher un ingrédient',start:'Cherchez et ajoutez un ingrédient pour commencer.',exploring:'Accords de',addhint:'Touchez + pour ajouter à votre sélection',selempty:'Aucun ingrédient — cherchez ci-dessus',needone:"Ajoutez d'abord un ingrédient à votre sélection.",tap:'Touchez une carte pour explorer',triosub:'Affinités à trois avec',bridgesub:"Ce qui relie deux ingrédients qui ne s'accordent pas directement.",findbridge:'Trouver le pont',nobridge:'Aucun pont trouvé entre les deux.',nopair:'Aucun accord trouvé.',makeit:'Transformer en',build:'Créer',need2:'Ajoutez au moins deux ingrédients à votre sélection.',buildfail:'Création impossible.',flav:'pont de saveurs',directno:"%a et %c ne s'accordent pas directement — pont via :",connect:'Connecteurs entre %a et %c :',enter2:'Choisissez deux ingrédients.',thinking:'Réflexion…',via_recipe:'recette',via_aroma:'arôme'}};
var RT={en:['salad','pasta sauce','main dish','marinade','dessert','cocktail','soup','dressing'],
 pt:['salada','molho de massa','prato principal','marinada','sobremesa','coquetel','sopa','molho'],
 es:['ensalada','salsa para pasta','plato principal','adobo','postre','cóctel','sopa','aliño'],
 it:['insalata','sugo per pasta','piatto principale','marinata','dessert','cocktail','zuppa','condimento'],
 de:['Salat','Pastasauce','Hauptgericht','Marinade','Dessert','Cocktail','Suppe','Dressing'],
 fr:['salade','sauce pour pâtes','plat principal','marinade','dessert','cocktail','soupe','vinaigrette']};
var RTV=['salad','pasta sauce','main dish','marinade','dessert','cocktail','soup','dressing'];
var st={selection:[],focus:null,mode:'balanced',tab:'explore',lang:'en',NAMES:{},NOTES:{},REV:{},ALL:[]};
function t(k){return (M[st.lang]&&M[st.lang][k])||M.en[k]||k}
function cap(s){return s?s.charAt(0).toUpperCase()+s.slice(1):s}
function disp(key){ if(st.lang!=='en'&&st.NAMES[key]) return cap(st.NAMES[key]); return cap((key||'').replace(/_/g,' ')); }
function dnote(n){ return (st.lang!=='en'&&st.NOTES[n])?st.NOTES[n]:n; }
function canon(text){ var x=(text||'').trim().toLowerCase(); if(st.REV[x])return st.REV[x]; return x.replace(/ /g,'_'); }
function $(i){return document.getElementById(i)}
function apiMode(){return st.mode==='surprising'?'experimental':st.mode}
function inSel(k){return st.selection.indexOf(k)>=0}
async function loadNames(){ try{ st.ALL=await (await fetch('/v1/names')).json(); }catch(e){ st.ALL=[]; } }
async function setLang(l){
  st.lang=l; $('lang').value=l;
  if(l==='en'){ st.NAMES={};st.NOTES={};st.REV={}; }
  else{ try{ var d=await (await fetch('/v1/i18n/'+l)).json(); st.NAMES=d.names||{}; st.NOTES=d.notes||{}; st.REV={}; for(var k in st.NAMES){ st.REV[(''+st.NAMES[k]).toLowerCase()]=k; } }catch(e){ st.NAMES={};st.NOTES={};st.REV={}; } }
  document.querySelectorAll('[data-k]').forEach(function(el){ el.textContent=t(el.dataset.k); });
  document.querySelectorAll('#seg button').forEach(function(b){ b.textContent=t(b.dataset.m); });
  $('searchin').placeholder=t('searchph');
  render();
}
function doSearch(q){
  var box=$('suggest'); q=(q||'').trim().toLowerCase();
  if(!q){ box.style.display='none'; return; }
  var out=[], seen={};
  for(var i=0;i<st.ALL.length && out.length<14;i++){
    var k=st.ALL[i]; var label=disp(k).toLowerCase(); var loc=(st.NAMES[k]||'').toLowerCase();
    if((label.indexOf(q)>=0 || loc.indexOf(q)>=0 || k.indexOf(q)>=0) && !seen[k] && !inSel(k)){ seen[k]=1; out.push(k); }
  }
  if(!out.length){ box.style.display='none'; return; }
  box.innerHTML=out.map(function(k){return '<div class=sug data-pick="'+k+'">'+disp(k)+'</div>'}).join('');
  box.style.display='block';
}
function addSel(k){ if(!inSel(k)){ st.selection.push(k); } selbar(); }
function pickSel(k){ if(!inSel(k)){ st.selection.push(k); } st.focus=k; st.tab='explore'; $('searchin').value=''; $('suggest').style.display='none'; render(); }
function removeSel(k){ st.selection=st.selection.filter(function(x){return x!==k}); if(st.focus===k) st.focus=st.selection[st.selection.length-1]||null; render(); }
function selbar(){
  var el=$('selbar');
  if(!st.selection.length){ el.innerHTML='<span class=selhint>'+t('selempty')+'</span>'; return; }
  el.innerHTML=st.selection.map(function(k){
    return '<span class="schip'+(k===st.focus?' foc':'')+'" data-foc="'+k+'">'+disp(k)+'<span class=x data-rm="'+k+'">×</span></span>';
  }).join('');
}
function pcard(nm,tier,notes,cat){
  var c=TB[tier]||TB.interesting;
  return '<div class=pcard data-go="'+nm+'"><span class=tier style="background:'+c[0]+';color:'+c[1]+'">'+tier+'</span>'+
    '<div style="flex:1;min-width:0"><div class=nm>'+disp(nm)+'</div><div class=nt>'+(notes||'')+'</div></div>'+
    '<button class="addb'+(inSel(nm)?' on':'')+'" data-add="'+nm+'" aria-label="add">'+(inSel(nm)?'✓':'+')+'</button>'+
    '<i class="ti ti-chevron-right chev"></i></div>';
}
function shell(){
  $('seg').style.display=st.tab==='explore'?'flex':'none';
  document.querySelectorAll('.tab').forEach(function(b){b.className='tab'+(b.dataset.t===st.tab?' on':'')});
  document.querySelectorAll('#seg button').forEach(function(b){b.className=(b.dataset.m===st.mode?'on':'')});
  selbar();
}
async function render(){
  shell();
  var b=$('body');
  if(st.tab==='explore'){
    if(!st.focus){ b.innerHTML='<div class=empty><i class="ti ti-search"></i>'+t('start')+'</div>'; return; }
    b.innerHTML='<div class=exhead>'+t('exploring')+' <b>'+disp(st.focus)+'</b> · '+t('addhint')+'</div><div class=empty><i class="ti ti-loader-2"></i></div>';
    try{
      var d=await (await fetch('/v1/pair/'+encodeURIComponent(st.focus)+'?mode='+apiMode()+'&limit=18')).json();
      var ps=d.pairings||[];
      var head='<div class=exhead>'+t('exploring')+' <b>'+disp(st.focus)+'</b> · '+t('addhint')+'</div>';
      if(!ps.length){ b.innerHTML=head+'<div class=empty>'+t('nopair')+'</div>'; return; }
      b.innerHTML=head+ps.map(function(p){
        var notes=(p.explanation.shared_notes||[]).slice(0,3).map(dnote).join(' · ');
        return pcard(p.ingredient,p.tier||'interesting',notes,p.category);
      }).join('');
    }catch(e){ b.innerHTML='<div class=empty>'+t('nopair')+'</div>'; }
  } else if(st.tab==='trios'){
    var anc=st.focus||st.selection[0];
    if(!anc){ b.innerHTML='<div class=empty><i class="ti ti-triangle"></i>'+t('needone')+'</div>'; return; }
    b.innerHTML='<div class=sub>'+t('triosub')+' '+disp(anc)+'</div><div class=empty><i class="ti ti-loader-2"></i></div>';
    try{
      var d=await (await fetch('/v1/trio/'+encodeURIComponent(anc)+'?limit=8')).json();
      var tr=d.trios||[]; var html='<div class=sub>'+t('triosub')+' '+disp(anc)+'</div>';
      if(!tr.length){ html+='<div class=empty>'+t('nopair')+'</div>'; }
      else html+=tr.map(function(x){return '<div class=pcard style="gap:8px"><div style="flex:1;font-size:15px"><b style="font-weight:600">'+disp(anc)+'</b> + '+disp(x.a)+' + '+disp(x.b)+'</div><button class=addb data-trio="'+x.a+'|'+x.b+'" aria-label="add">+</button></div>'}).join('');
      b.innerHTML=html;
    }catch(e){ b.innerHTML='<div class=empty>'+t('nopair')+'</div>'; }
  } else if(st.tab==='bridge'){
    var a0=st.selection[0]?disp(st.selection[0]):'', c0=st.selection[1]?disp(st.selection[1]):'';
    b.innerHTML='<div class=sub>'+t('bridgesub')+'</div>'+
      '<div style="display:flex;gap:8px;margin-bottom:10px"><input class=tin id=bA placeholder="…" value="'+a0+'"><input class=tin id=bB placeholder="…" value="'+c0+'"></div>'+
      '<button class=bigbtn id=bgo>'+t('findbridge')+'</button><div id=bout style="margin-top:12px"></div>';
    $('bgo').onclick=doBridge;
  } else {
    if(st.selection.length<2){ b.innerHTML='<div class=empty><i class="ti ti-basket"></i>'+t('need2')+'</div>'; return; }
    var opts=(RT[st.lang]||RT.en).map(function(n,i){return '<option value="'+RTV[i]+'">'+t('makeit')+' '+n+'</option>'}).join('');
    b.innerHTML='<select id=rtype style="width:100%;margin-bottom:12px">'+opts+'</select>'+
      '<button class="bigbtn prim" id=bld>'+t('build')+'</button><div id=rout style="margin-top:14px"></div>';
    $('bld').onclick=buildRecipe;
  }
}
async function doBridge(){
  var a=canon($('bA').value), c=canon($('bB').value), out=$('bout');
  if(!a||!c){ out.innerHTML='<div class=sub>'+t('enter2')+'</div>'; return; }
  out.innerHTML='<div class=empty><i class="ti ti-loader-2"></i></div>';
  try{
    var d=await (await fetch('/v1/bridge?a='+encodeURIComponent(a)+'&c='+encodeURIComponent(c)+'&limit=6')).json();
    var bs=d.bridges||[];
    if(!bs.length){ out.innerHTML='<div class=sub>'+t('nobridge')+'</div>'; return; }
    var direct=bs[0].direct_link;
    var head=((direct!=null&&direct<=0)?t('directno'):t('connect')).replace('%a',disp(a)).replace('%c',disp(c));
    out.innerHTML='<div class=sub>'+head+'</div>'+bs.map(function(x){
      var vc=x.via==='recipe'?['#E1F5EE','#0F6E56']:['#EEEDFE','#3C3489'];
      return '<div class=pcard><span class=tier style="background:'+vc[0]+';color:'+vc[1]+'">'+t('via_'+x.via)+'</span><div style="flex:1"><div class=nm>'+disp(x.bridge)+'</div></div><button class="addb'+(inSel(x.bridge)?' on':'')+'" data-add="'+x.bridge+'" aria-label="add">'+(inSel(x.bridge)?'✓':'+')+'</button></div>';
    }).join('');
  }catch(e){ out.innerHTML='<div class=sub>'+t('nobridge')+'</div>'; }
}
async function buildRecipe(){
  var out=$('rout'); out.innerHTML='<div class=sub>'+t('thinking')+'</div>';
  var type=$('rtype').value;
  try{
    var r=await (await fetch('/v1/recipe',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({ingredients:st.selection,type:type})})).json();
    var theme=(r.shared_theme||[]).slice(0,6).map(dnote);
    out.innerHTML='<div style="background:#f7f6f2;border:1px solid var(--line);border-radius:12px;padding:13px;font-size:14px;line-height:1.5"><b>'+r.suggestion+'</b>'+(theme.length?'<div class=sub style="margin:6px 0 0">'+t('flav')+': '+theme.join(', ')+'</div>':'')+'</div>';
  }catch(e){ out.innerHTML='<div class=sub>'+t('buildfail')+'</div>'; }
}
$('searchin').addEventListener('input',function(){ doSearch(this.value); });
$('searchin').addEventListener('keydown',function(e){ if(e.key==='Enter'){ var k=canon(this.value); if(k){ pickSel(k); } } });
document.body.addEventListener('click',function(e){
  var pick=e.target.closest('[data-pick]'), add=e.target.closest('[data-add]'), trio=e.target.closest('[data-trio]'),
      go=e.target.closest('[data-go]'), rm=e.target.closest('[data-rm]'), foc=e.target.closest('[data-foc]'),
      tab=e.target.closest('[data-t]'), mode=e.target.closest('[data-m]');
  if(pick){ pickSel(pick.dataset.pick); return; }
  if(rm){ e.stopPropagation(); removeSel(rm.dataset.rm); return; }
  if(add){ e.stopPropagation(); addSel(add.dataset.add); add.className='addb on'; add.textContent='✓'; return; }
  if(trio){ e.stopPropagation(); var p=trio.dataset.trio.split('|'); addSel(p[0]); addSel(p[1]); trio.textContent='✓'; setTimeout(function(){trio.textContent='+'},800); return; }
  if(foc){ st.focus=foc.dataset.foc; st.tab='explore'; render(); return; }
  if(tab){ st.tab=tab.dataset.t; render(); return; }
  if(mode){ st.mode=mode.dataset.m; render(); return; }
  if(go){ st.focus=go.dataset.go; render(); return; }
});
document.addEventListener('click',function(e){ if(!e.target.closest('.searchbar')) $('suggest').style.display='none'; });
async function init(){
  await loadNames();
  var nav=(navigator.language||'en').slice(0,2).toLowerCase();
  await setLang(['pt','es','it','de','fr'].indexOf(nav)>=0?nav:'en');
}
window.addEventListener('load',init);
</script></body></html>"""
