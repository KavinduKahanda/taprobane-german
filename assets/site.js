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
  var y=document.getElementById('year');if(y)y.textContent=new Date().getFullYear();
})();
