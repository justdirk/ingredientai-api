"""Mobile-first card UI served to phones (desktop keeps the graph explorer).
Thumb-driven: focused ingredient feed, segmented modes, drill-down navigation,
and Explore / Trios / Bridge / Recipe tabs. Talks to the same /v1 endpoints and
loads the same localized name/note dictionaries."""

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
.hd{padding:12px 16px 12px;border-bottom:1px solid var(--line)}
.hrow{display:flex;align-items:center;gap:10px;margin-bottom:12px}
.crumb{font-size:12px;color:#9b978d;min-height:15px;text-transform:lowercase}
.title{font-size:22px;font-weight:600;line-height:1.1}
.dot{width:11px;height:11px;border-radius:50%;flex:none}
.seg{display:flex;background:#efece4;border-radius:11px;padding:3px;gap:3px}
.seg button{flex:1;border:0;background:transparent;border-radius:8px;padding:9px 0;font-size:13.5px;color:var(--mut)}
.seg button.on{background:#fff;color:var(--ink);font-weight:600}
#body{flex:1;overflow:auto;padding:14px 16px 20px;-webkit-overflow-scrolling:touch}
.pcard{display:flex;align-items:center;gap:11px;padding:13px 14px;border:1px solid var(--line);border-radius:14px;background:#fff;margin-bottom:9px}
.pcard .nm{font-size:16px;font-weight:600;margin-bottom:2px}
.pcard .nt{font-size:13px;color:var(--mut)}
.tier{font-size:11px;font-weight:600;padding:3px 9px;border-radius:999px;white-space:nowrap}
.addb{width:32px;height:32px;border-radius:50%;border:1px solid var(--line);background:#fff;color:var(--mut);font-size:18px;flex:none}
.chev{color:#c3bfb4;font-size:19px}
.tabbar{display:flex;border-top:1px solid var(--line);background:#fff;padding-bottom:env(safe-area-inset-bottom)}
.tab{flex:1;display:flex;flex-direction:column;align-items:center;gap:2px;border:0;background:transparent;padding:9px 0 8px;font-size:11px;color:#a7a399}
.tab.on{color:var(--accent)}
.tab i{font-size:22px}
.sub{font-size:13px;color:var(--mut);margin-bottom:12px;line-height:1.5}
.bchip{background:#efece4;border-radius:999px;padding:7px 13px;font-size:13.5px}
.bigbtn{width:100%;border:1px solid var(--line);background:#fff;border-radius:12px;padding:13px;font-size:15px;font-weight:600;color:var(--ink)}
.bigbtn.prim{background:var(--accent);color:#fff;border-color:var(--accent)}
.tin{flex:1;min-width:0;border:1px solid var(--line);border-radius:11px;padding:11px;font-size:15px;text-align:center;background:#fff;color:var(--ink)}
.searchwrap{flex:1}
.searchwrap input{width:100%;border:1px solid var(--line);border-radius:11px;padding:9px 12px;font-size:16px;background:#fff;color:var(--ink)}
.empty{text-align:center;color:#a7a399;font-size:14px;padding:34px 10px}
.empty i{font-size:32px;display:block;margin-bottom:8px}
.cnt{background:var(--accent);color:#fff;font-size:10px;font-weight:600;border-radius:999px;padding:0 5px;margin-left:3px}
</style></head><body>
<div class=util>
  <span class=brand>IngredientAI</span>
  <a class=iconbtn href="?view=graph" aria-label="Graph view"><i class="ti ti-affiliate"></i></a>
  <select id=lang onchange="setLang(this.value)"><option value=en>EN</option><option value=pt>PT</option><option value=es>ES</option><option value=it>IT</option><option value=de>DE</option><option value=fr>FR</option></select>
</div>
<div class=hd>
  <div class=hrow>
    <button id=back class=iconbtn style="display:none" aria-label="Back"><i class="ti ti-chevron-left"></i></button>
    <div style="flex:1;min-width:0" id=titlewrap>
      <div class=crumb id=crumb></div>
      <div style="display:flex;align-items:center;gap:8px"><span class=dot id=dot></span><span class=title id=focus>Garlic</span></div>
    </div>
    <div class=searchwrap id=searchwrap style="display:none"><input id=searchin placeholder="Search" autocomplete=off></div>
    <button id=searchbtn class=iconbtn aria-label="Search"><i class="ti ti-search"></i></button>
  </div>
  <div class=seg id=seg><button data-m=safe>Safe</button><button data-m=balanced class=on>Balanced</button><button data-m=surprising>Surprising</button></div>
</div>
<div id=body></div>
<div class=tabbar id=tabbar>
  <button class="tab on" data-t=explore><i class="ti ti-grain"></i><span data-k=tExplore>Explore</span></button>
  <button class=tab data-t=trios><i class="ti ti-triangle"></i><span data-k=tTrios>Trios</span></button>
  <button class=tab data-t=bridge><i class="ti ti-arrows-left-right"></i><span data-k=tBridge>Bridge</span></button>
  <button class=tab data-t=recipe><i class="ti ti-basket"></i><span data-k=tRecipe>Recipe</span><span class=cnt id=cnt style="display:none">0</span></button>
</div>
<script>
var TB={classic:['#E1F5EE','#0F6E56'],recommended:['#E6F1FB','#185FA5'],interesting:['#F1EFE8','#5F5E5A'],bold:['#FAEEDA','#854F0B']};
var CATC={Fruit:'#e07a5f',Spice:'#d9883b',Dairy:'#4f9fd0','Plant/Vegetable':'#3a9d5d',Vegetable:'#3a9d5d',Meat:'#c1554f','Meat/Animal Product':'#c1554f',Seafood:'#3a8fc4','Nut/Seed':'#b07a3c',Beverage Alcoholic:'#9b6fc0',Beverage:'#7a9bd0',Flower:'#d07aa8',Fungus:'#8a7d6b',Condiment:'#a89a6a','Bakery/Dessert':'#caa06a'};
var M={
 en:{safe:'Safe',balanced:'Balanced',surprising:'Surprising',tExplore:'Explore',tTrios:'Trios',tBridge:'Bridge',tRecipe:'Recipe',search:'Search an ingredient',empty:'Add ingredients with the + buttons',tap:'Tap a card to explore it further',triosub:'Three-way affinities with',bridgesub:"Find what links two ingredients that don't pair directly.",findbridge:'Find the bridge',nobridge:'No bridge found between these two.',nopair:'No pairings found.',makeit:'Make it a…',build:'Build it',buildfail:'Could not build.',flav:'flavour bridge',directno:"%a and %c don't pair directly — bridge through:",connect:'Connectors between %a and %c:',enter2:'Enter two ingredients.',thinking:'Thinking…',recipe_built:'shared notes',via_recipe:'recipe',via_aroma:'aroma'},
 pt:{safe:'Seguro',balanced:'Equilibrado',surprising:'Surpreendente',tExplore:'Explorar',tTrios:'Trios',tBridge:'Ponte',tRecipe:'Receita',search:'Buscar um ingrediente',empty:'Adicione ingredientes com os botões +',tap:'Toque num cartão para explorar',triosub:'Afinidades em três com',bridgesub:'Descubra o que liga dois ingredientes que não combinam diretamente.',findbridge:'Encontrar a ponte',nobridge:'Nenhuma ponte encontrada entre os dois.',nopair:'Nenhuma combinação encontrada.',makeit:'Transforme em…',build:'Criar',buildfail:'Não foi possível criar.',flav:'ponte de sabor',directno:'%a e %c não combinam diretamente — conecte através de:',connect:'Conectores entre %a e %c:',enter2:'Digite dois ingredientes.',thinking:'Pensando…',recipe_built:'notas em comum',via_recipe:'receita',via_aroma:'aroma'},
 es:{safe:'Seguro',balanced:'Equilibrado',surprising:'Sorprendente',tExplore:'Explorar',tTrios:'Tríos',tBridge:'Puente',tRecipe:'Receta',search:'Buscar un ingrediente',empty:'Añade ingredientes con los botones +',tap:'Toca una tarjeta para explorar',triosub:'Afinidades de tres con',bridgesub:'Descubre qué une dos ingredientes que no combinan directamente.',findbridge:'Encontrar el puente',nobridge:'No se encontró puente entre estos dos.',nopair:'No se encontraron maridajes.',makeit:'Conviértelo en…',build:'Crear',buildfail:'No se pudo crear.',flav:'puente de sabor',directno:'%a y %c no combinan directamente — conecta mediante:',connect:'Conectores entre %a y %c:',enter2:'Introduce dos ingredientes.',thinking:'Pensando…',recipe_built:'notas en común',via_recipe:'receta',via_aroma:'aroma'},
 it:{safe:'Sicuro',balanced:'Bilanciato',surprising:'Sorprendente',tExplore:'Esplora',tTrios:'Trii',tBridge:'Ponte',tRecipe:'Ricetta',search:'Cerca un ingrediente',empty:'Aggiungi ingredienti con i pulsanti +',tap:'Tocca una scheda per esplorare',triosub:'Affinità a tre con',bridgesub:'Scopri cosa collega due ingredienti che non si abbinano direttamente.',findbridge:'Trova il ponte',nobridge:'Nessun ponte trovato tra i due.',nopair:'Nessun abbinamento trovato.',makeit:'Trasformalo in…',build:'Crea',buildfail:'Impossibile creare.',flav:'ponte di sapore',directno:'%a e %c non si abbinano direttamente — collega tramite:',connect:'Connettori tra %a e %c:',enter2:'Inserisci due ingredienti.',thinking:'Sto pensando…',recipe_built:'note in comune',via_recipe:'ricetta',via_aroma:'aroma'},
 de:{safe:'Sicher',balanced:'Ausgewogen',surprising:'Überraschend',tExplore:'Entdecken',tTrios:'Trios',tBridge:'Brücke',tRecipe:'Rezept',search:'Zutat suchen',empty:'Zutaten mit den +-Tasten hinzufügen',tap:'Tippe eine Karte zum Erkunden',triosub:'Dreier-Affinitäten mit',bridgesub:'Finde, was zwei Zutaten verbindet, die nicht direkt zusammenpassen.',findbridge:'Brücke finden',nobridge:'Keine Brücke zwischen beiden gefunden.',nopair:'Keine Kombinationen gefunden.',makeit:'Mach daraus…',build:'Erstellen',buildfail:'Erstellen fehlgeschlagen.',flav:'Geschmacksbrücke',directno:'%a und %c passen nicht direkt zusammen — Brücke über:',connect:'Verbindungen zwischen %a und %c:',enter2:'Zwei Zutaten eingeben.',thinking:'Denke nach…',recipe_built:'gemeinsame Noten',via_recipe:'Rezept',via_aroma:'Aroma'},
 fr:{safe:'Sûr',balanced:'Équilibré',surprising:'Surprenant',tExplore:'Explorer',tTrios:'Trios',tBridge:'Pont',tRecipe:'Recette',search:'Chercher un ingrédient',empty:'Ajoutez des ingrédients avec les boutons +',tap:'Touchez une carte pour explorer',triosub:'Affinités à trois avec',bridgesub:"Trouvez ce qui relie deux ingrédients qui ne s'accordent pas directement.",findbridge:'Trouver le pont',nobridge:'Aucun pont trouvé entre les deux.',nopair:'Aucun accord trouvé.',makeit:'Transformer en…',build:'Créer',buildfail:'Création impossible.',flav:'pont de saveurs',directno:"%a et %c ne s'accordent pas directement — pont via :",connect:'Connecteurs entre %a et %c :',enter2:'Saisissez deux ingrédients.',thinking:'Réflexion…',recipe_built:'notes communes',via_recipe:'recette',via_aroma:'arôme'}};
var RT={en:['salad','pasta sauce','main dish','marinade','dessert','cocktail','soup','dressing'],
 pt:['salada','molho de massa','prato principal','marinada','sobremesa','coquetel','sopa','molho'],
 es:['ensalada','salsa para pasta','plato principal','adobo','postre','cóctel','sopa','aliño'],
 it:['insalata','sugo per pasta','piatto principale','marinata','dessert','cocktail','zuppa','condimento'],
 de:['Salat','Pastasauce','Hauptgericht','Marinade','Dessert','Cocktail','Suppe','Dressing'],
 fr:['salade','sauce pour pâtes','plat principal','marinade','dessert','cocktail','soupe','vinaigrette']};
var RTV=['salad','pasta sauce','main dish','marinade','dessert','cocktail','soup','dressing'];
var st={focus:'garlic',mode:'balanced',tab:'explore',stack:[],basket:[],lang:'en',NAMES:{},NOTES:{},REV:{}};
function t(k){return (M[st.lang]&&M[st.lang][k])||M.en[k]||k}
function cap(s){return s?s.charAt(0).toUpperCase()+s.slice(1):s}
function disp(key){ if(st.lang!=='en'&&st.NAMES[key]) return cap(st.NAMES[key]); return cap(key.replace(/_/g,' ')); }
function dnote(n){ return (st.lang!=='en'&&st.NOTES[n])?st.NOTES[n]:n; }
function canon(text){ var x=(text||'').trim().toLowerCase(); if(st.REV[x])return st.REV[x]; return x.replace(/ /g,'_'); }
function $(i){return document.getElementById(i)}
function apiMode(){return st.mode==='surprising'?'experimental':st.mode}
async function setLang(l){
  st.lang=l; $('lang').value=l;
  if(l==='en'){ st.NAMES={};st.NOTES={};st.REV={}; }
  else{ try{ var d=await (await fetch('/v1/i18n/'+l)).json(); st.NAMES=d.names||{}; st.NOTES=d.notes||{}; st.REV={}; for(var k in st.NAMES){ st.REV[(''+st.NAMES[k]).toLowerCase()]=k; } }catch(e){ st.NAMES={};st.NOTES={};st.REV={}; } }
  document.querySelectorAll('[data-k]').forEach(function(el){ el.textContent=t(el.dataset.k); });
  document.querySelectorAll('#seg button').forEach(function(b){ b.textContent=t(b.dataset.m); });
  $('searchin').placeholder=t('search');
  render();
}
function pcard(nm,tier,notes,cat,drill){
  var c=TB[tier]||TB.interesting;
  return '<div class=pcard data-go="'+(drill?nm:'')+'"><span class=dot style="background:'+(CATC[cat]||'#8a9a8e')+'"></span>'+
    '<div style="flex:1;min-width:0"><div class=nm>'+disp(nm)+'</div><div class=nt>'+(notes||'')+'</div></div>'+
    '<span class=tier style="background:'+c[0]+';color:'+c[1]+'">'+(tier)+'</span>'+
    '<button class=addb data-add="'+nm+'" aria-label="add">+</button>'+
    (drill?'<i class="ti ti-chevron-right chev"></i>':'')+'</div>';
}
function shell(){
  $('focus').textContent=disp(st.focus);
  $('crumb').textContent=st.stack.length?st.stack.map(function(x){return disp(x)}).join(' › '):t('tExplore');
  $('back').style.display=st.stack.length?'block':'none';
  $('seg').style.display=st.tab==='explore'?'flex':'none';
  document.querySelectorAll('.tab').forEach(function(b){b.className='tab'+(b.dataset.t===st.tab?' on':'')});
  document.querySelectorAll('#seg button').forEach(function(b){b.className=(b.dataset.m===st.mode?'on':'')});
  $('cnt').style.display=st.basket.length?'inline-block':'none'; $('cnt').textContent=st.basket.length;
}
async function render(){
  shell();
  var b=$('body');
  if(st.tab==='explore'){
    b.innerHTML='<div class=empty><i class="ti ti-loader-2"></i></div>';
    try{
      var d=await (await fetch('/v1/pair/'+encodeURIComponent(st.focus)+'?mode='+apiMode()+'&limit=18')).json();
      var ps=d.pairings||[];
      if(!ps.length){ b.innerHTML='<div class=empty>'+t('nopair')+'</div>'; return; }
      var dotcat=ps[0]?ps[0].category:null;
      $('dot').style.background=CATC[dotcat]||'#8a9a8e';
      b.innerHTML=ps.map(function(p){
        var notes=(p.explanation.shared_notes||[]).slice(0,3).map(dnote).join(' · ');
        return pcard(p.ingredient,p.tier||'interesting',notes,p.category,true);
      }).join('')+'<div style="font-size:12px;color:#b3afa5;text-align:center;margin-top:4px">'+t('tap')+'</div>';
    }catch(e){ b.innerHTML='<div class=empty>'+t('nopair')+'</div>'; }
  } else if(st.tab==='trios'){
    b.innerHTML='<div class=sub>'+t('triosub')+' '+disp(st.focus)+'</div><div class=empty><i class="ti ti-loader-2"></i></div>';
    try{
      var d=await (await fetch('/v1/trio/'+encodeURIComponent(st.focus)+'?limit=8')).json();
      var tr=d.trios||[];
      var html='<div class=sub>'+t('triosub')+' '+disp(st.focus)+'</div>';
      if(!tr.length){ html+='<div class=empty>'+t('nopair')+'</div>'; }
      else html+=tr.map(function(x){return '<div class=pcard style="gap:8px"><div style="flex:1;font-size:15px"><b style="font-weight:600">'+disp(st.focus)+'</b> + '+disp(x.a)+' + '+disp(x.b)+'</div><button class=addb data-trio="'+x.a+'|'+x.b+'" aria-label="add">+</button></div>'}).join('');
      b.innerHTML=html;
    }catch(e){ b.innerHTML='<div class=empty>'+t('nopair')+'</div>'; }
  } else if(st.tab==='bridge'){
    b.innerHTML='<div class=sub>'+t('bridgesub')+'</div>'+
      '<div style="display:flex;gap:8px;margin-bottom:10px"><input class=tin id=bA value="'+disp(st.focus)+'"><input class=tin id=bB placeholder="…"></div>'+
      '<button class=bigbtn id=bgo>'+t('findbridge')+'</button><div id=bout style="margin-top:12px"></div>';
    $('bgo').onclick=doBridge;
  } else {
    if(!st.basket.length){ b.innerHTML='<div class=empty><i class="ti ti-basket"></i>'+t('empty')+'</div>'; }
    else{
      var opts=(RT[st.lang]||RT.en).map(function(n,i){return '<option value="'+RTV[i]+'">'+t('makeit').replace('…','')+' '+n+'</option>'}).join('');
      b.innerHTML='<div style="display:flex;flex-wrap:wrap;gap:8px;margin-bottom:16px">'+st.basket.map(function(k){return '<span class=bchip data-rm="'+k+'">'+disp(k)+' ✕</span>'}).join('')+'</div>'+
        '<select id=rtype style="width:100%;margin-bottom:12px">'+opts+'</select>'+
        '<button class="bigbtn prim" id=bld>'+t('build')+'</button><div id=rout style="margin-top:14px"></div>';
      $('bld').onclick=buildRecipe;
    }
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
      return '<div class=pcard><div style="flex:1"><div class=nm>'+disp(x.bridge)+'</div></div><span class=tier style="background:'+vc[0]+';color:'+vc[1]+'">'+t('via_'+x.via)+'</span><button class=addb data-add="'+x.bridge+'" aria-label="add">+</button></div>';
    }).join('');
  }catch(e){ out.innerHTML='<div class=sub>'+t('nobridge')+'</div>'; }
}
async function buildRecipe(){
  var out=$('rout'); out.innerHTML='<div class=sub>'+t('thinking')+'</div>';
  var type=$('rtype').value;
  try{
    var r=await (await fetch('/v1/recipe',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({ingredients:st.basket,type:type})})).json();
    var theme=(r.shared_theme||[]).slice(0,6).map(dnote);
    out.innerHTML='<div style="background:#f7f6f2;border:1px solid var(--line);border-radius:12px;padding:13px;font-size:14px;line-height:1.5"><b>'+r.suggestion+'</b>'+(theme.length?'<div class=sub style="margin:6px 0 0">'+t('flav')+': '+theme.join(', ')+'</div>':'')+'</div>';
  }catch(e){ out.innerHTML='<div class=sub>'+t('buildfail')+'</div>'; }
}
function addBasket(k){ if(st.basket.indexOf(k)<0){st.basket.push(k);shell();} }
document.body.addEventListener('click',function(e){
  var go=e.target.closest('[data-go]'), add=e.target.closest('[data-add]'), trio=e.target.closest('[data-trio]'),
      tab=e.target.closest('[data-t]'), mode=e.target.closest('[data-m]'), rm=e.target.closest('[data-rm]');
  if(add){ e.stopPropagation(); addBasket(add.dataset.add); flash(add); return; }
  if(trio){ e.stopPropagation(); trio.dataset.trio.split('|').concat([st.focus]).forEach(addBasket); flash(trio); return; }
  if(rm){ st.basket=st.basket.filter(function(x){return x!==rm.dataset.rm}); render(); return; }
  if(e.target.closest('#back')){ st.focus=st.stack.pop()||'garlic'; render(); return; }
  if(tab){ st.tab=tab.dataset.t; render(); return; }
  if(mode){ st.mode=mode.dataset.m; render(); return; }
  if(go&&go.dataset.go){ st.stack.push(st.focus); st.focus=go.dataset.go; st.tab='explore'; render(); return; }
});
function flash(el){ el.textContent='✓'; setTimeout(function(){el.textContent='+'},700); }
$('searchbtn').onclick=function(){
  var sw=$('searchwrap'), tw=$('titlewrap');
  if(sw.style.display==='none'){ sw.style.display='block'; tw.style.display='none'; $('searchin').focus(); }
  else{ sw.style.display='none'; tw.style.display='block'; }
};
$('searchin').addEventListener('keydown',function(e){
  if(e.key==='Enter'){ var k=canon(this.value); if(k){ st.stack=[]; st.focus=k; st.tab='explore'; } this.value=''; $('searchbtn').onclick(); render(); }
});
function init(){
  var nav=(navigator.language||'en').slice(0,2).toLowerCase();
  setLang(['pt','es','it','de','fr'].indexOf(nav)>=0?nav:'en');
}
window.addEventListener('load',init);
</script></body></html>"""
