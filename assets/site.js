(function(){
  // mobile menu
  var btn=document.querySelector('.menu-btn'),nav=document.querySelector('.nav');
  if(btn&&nav){btn.addEventListener('click',function(){var o=nav.classList.toggle('open');btn.setAttribute('aria-expanded',o)})}
  // Amazon store switcher: links with data-asin get the reader's own store
  var stores={'com':'amazon.com','de':'amazon.de','co.uk':'amazon.co.uk','in':'amazon.in','ca':'amazon.ca','com.au':'amazon.com.au','fr':'amazon.fr','it':'amazon.it','es':'amazon.es','nl':'amazon.nl'};
  var noPrint={'in':1}; // KDP paperbacks are not sold on amazon.in
  function guess(){var l=(navigator.language||'en-US').toLowerCase();
    if(/-in$/.test(l))return 'in';if(/^de|-de$|-at$|-ch$/.test(l))return 'de';if(/-gb$|-ie$/.test(l))return 'co.uk';
    if(/-ca$/.test(l))return 'ca';if(/-au$|-nz$/.test(l))return 'com.au';if(/^fr/.test(l))return 'fr';if(/^it/.test(l))return 'it';if(/^es-es/.test(l))return 'es';if(/^nl/.test(l))return 'nl';return 'com'}
  var cur;try{cur=localStorage.getItem('store')}catch(e){}
  if(!stores[cur])cur=guess();
  function apply(s){document.querySelectorAll('a[data-asin]').forEach(function(a){
      var st=(a.dataset.fmt==='paperback'&&noPrint[s])?'com':s;
      a.href='https://www.'+stores[st]+'/dp/'+a.dataset.asin;a.rel='noopener';a.target='_blank'});
    document.querySelectorAll('.store select').forEach(function(sel){sel.value=s});}
  document.querySelectorAll('.store select').forEach(function(sel){sel.addEventListener('change',function(){cur=sel.value;try{localStorage.setItem('store',cur)}catch(e){}apply(cur)})});
  apply(cur);
  // Promotion bar: shows only while a deal is live (times in UTC = Amazon Pacific time)
  var DEALS=[
   {s:'2026-11-04T08:00Z',e:'2026-11-06T07:59Z',st:'*',asin:'B0HPMHCHT3',t:'Deutsch B1 Pflege is <b>FREE on Kindle</b> for a short time'},
   {s:'2026-11-27T08:00Z',e:'2026-11-29T07:59Z',st:'*',asin:'B0HPMHCHT3',t:'Deutsch B1 Pflege is <b>FREE on Kindle</b> this weekend'},
   {s:'2026-11-12T16:00Z',e:'2026-11-19T16:00Z',st:'com',asin:'B0HMS37QX6',t:'Kindle deal: <b>Deutsch A2</b> at a reduced price'},
   {s:'2026-11-14T08:00Z',e:'2026-11-21T08:00Z',st:'co.uk',asin:'B0HMS37QX6',t:'Kindle deal: <b>Deutsch A2</b> at a reduced price'},
   {s:'2026-11-12T16:00Z',e:'2026-11-19T16:00Z',st:'com',asin:'B0HMVZ28R4',t:'Kindle deal: <b>Deutsch B1</b> at a reduced price'},
   {s:'2026-11-21T08:00Z',e:'2026-11-28T08:00Z',st:'co.uk',asin:'B0HMVZ28R4',t:'Kindle deal: <b>Deutsch B1</b> at a reduced price'},
   {s:'2026-11-13T16:00Z',e:'2026-11-20T16:00Z',st:'com',asin:'B0HKZPM3NJ',t:'Kindle deal: <b>Deutsch B2</b> at a reduced price'},
   {s:'2026-11-16T08:00Z',e:'2026-11-23T08:00Z',st:'co.uk',asin:'B0HKZPM3NJ',t:'Kindle deal: <b>Deutsch B2</b> at a reduced price'}];
  function promo(s){var bar=document.getElementById('promo');if(!bar)return;var now=Date.now();
    var d=DEALS.filter(function(x){return (x.st==='*'||x.st===s)&&now>=Date.parse(x.s)&&now<Date.parse(x.e)});
    if(!d.length){bar.hidden=true;return}
    var x=d[0],end=new Date(x.e),left=Math.max(1,Math.ceil((Date.parse(x.e)-now)/36e5));
    bar.innerHTML='<div class="wrap"><span class="promo-dot"></span><span>'+x.t+' &middot; ends in '+(left>48?Math.ceil(left/24)+' days':left+' h')+'</span><a data-asin="'+x.asin+'" data-fmt="kindle" href="https://www.'+stores[s]+'/dp/'+x.asin+'" target="_blank" rel="noopener">Get it on Amazon &rarr;</a></div>';
    bar.hidden=false}
  promo(cur);
  document.querySelectorAll('.store select').forEach(function(sel){sel.addEventListener('change',function(){promo(sel.value)})});
  var y=document.getElementById('year');if(y)y.textContent=new Date().getFullYear();
})();
