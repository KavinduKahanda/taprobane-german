(function(){
  // mobile menu
  var btn=document.querySelector('.menu-btn'),nav=document.querySelector('.nav');
  if(btn&&nav){btn.addEventListener('click',function(){var o=nav.classList.toggle('open');btn.setAttribute('aria-expanded',o)});
    document.addEventListener('keydown',function(e){if(e.key==='Escape'&&nav.classList.contains('open')){nav.classList.remove('open');btn.setAttribute('aria-expanded','false');btn.focus()}})}
  // Amazon store switcher: links with data-asin go to the reader's own store
  var stores={'com':'amazon.com','de':'amazon.de','co.uk':'amazon.co.uk','in':'amazon.in','ca':'amazon.ca','com.au':'amazon.com.au','fr':'amazon.fr','it':'amazon.it','es':'amazon.es','nl':'amazon.nl'};
  var noPrint={'in':1}; // KDP paperbacks are not sold on amazon.in
  function guess(){var l=(navigator.language||'en-US').toLowerCase();
    if(/-in$/.test(l))return 'in';if(/^de|-de$|-at$|-ch$/.test(l))return 'de';if(/-gb$|-ie$/.test(l))return 'co.uk';
    if(/-ca$/.test(l))return 'ca';if(/-au$|-nz$/.test(l))return 'com.au';if(/^fr/.test(l))return 'fr';if(/^it/.test(l))return 'it';if(/^es-es/.test(l))return 'es';if(/^nl/.test(l))return 'nl';return 'com'}
  var cur;try{cur=localStorage.getItem('store')}catch(e){}
  if(!stores[cur])cur=guess();
  function links(s){document.querySelectorAll('a[data-asin]').forEach(function(a){
      var st=(a.dataset.fmt==='paperback'&&noPrint[s])?'com':s;
      a.href='https://www.'+stores[st]+'/dp/'+a.dataset.asin;a.rel='noopener';a.target='_blank'});
    document.querySelectorAll('.store select').forEach(function(sel){sel.value=s});}
  // "New" tags expire on their own (data-until = last day shown)
  var today=new Date().toISOString().slice(0,10);
  document.querySelectorAll('.new-tag[data-until]').forEach(function(n){if(n.dataset.until<today)n.remove()});
  // Promotions (window.DEALS comes from assets/deals.js, built from _src/data/promos.json).
  // Shows ONE live deal for the visitor's store (the one ending soonest) and marks that book.
  function promo(s){var bar=document.getElementById('promo');var now=Date.now();
    var live=(window.DEALS||[]).filter(function(x){return (x.st==='*'||x.st===s)&&now>=Date.parse(x.s)&&now<Date.parse(x.e)})
      .sort(function(a,b){return Date.parse(a.e)-Date.parse(b.e)});
    document.querySelectorAll('[data-book].on-deal').forEach(function(el){el.classList.remove('on-deal');el.removeAttribute('data-deal')});
    if(!bar)return;
    if(!live.length){bar.hidden=true;bar.innerHTML='';return}
    var x=live[0],left=Math.max(1,Math.ceil((Date.parse(x.e)-now)/36e5));
    var label=x.kind==='free'?'Free on Kindle':'Kindle deal';
    document.querySelectorAll('[data-book="'+x.book+'"]').forEach(function(el){el.classList.add('on-deal');el.setAttribute('data-deal',label)});
    bar.innerHTML='<div class="wrap"><span class="promo-tag">'+label+'</span><span>'+x.t+' · ends in '+(left>48?Math.ceil(left/24)+' days':left+' h')+'</span><a data-asin="'+x.asin+'" data-fmt="kindle" href="https://www.'+stores[s]+'/dp/'+x.asin+'">Get it on Amazon →</a></div>';
    bar.hidden=false;links(s)}
  function apply(s){links(s);promo(s)}
  document.querySelectorAll('.store select').forEach(function(sel){sel.addEventListener('change',function(){cur=sel.value;try{localStorage.setItem('store',cur)}catch(e){}apply(cur)})});
  apply(cur);
  // Inquiry form (only present once a form service endpoint is set in _src/build.py)
  var f=document.getElementById('inquiry');
  if(f){f.addEventListener('submit',function(e){e.preventDefault();var st=f.querySelector('.form-status'),b=f.querySelector('button');
    if(!f.checkValidity()){st.className='form-status err';st.textContent='Please choose a topic, add your e-mail and write a message.';f.reportValidity();return}
    b.disabled=true;st.className='form-status';st.textContent='Sending…';
    fetch(f.action,{method:'POST',body:new FormData(f),headers:{'Accept':'application/json'}}).then(function(r){
      if(!r.ok)throw 0;f.reset();st.className='form-status ok';st.textContent='Thank you — your message has been sent. We will reply by e-mail.'})
    .catch(function(){st.className='form-status err';st.textContent='Sorry, sending failed. Please message us on Instagram instead.'})
    .then(function(){b.disabled=false})})}
  var y=document.getElementById('year');if(y)y.textContent=new Date().getFullYear();
})();
