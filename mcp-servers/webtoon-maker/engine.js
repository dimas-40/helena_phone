/* (0) 티스토리 스킨이 html/body에 박은 overscroll-behavior-y:contain 을 걷어낸다.
   ★ 2026-09-15 실기기 확정: 이 값 때문에 손가락 터치 스와이프(스크롤)가 0%로 죽는다.
   auto 로 바꾸면 터치 스크롤이 살아난다. 연출보다 이게 먼저다. */
(function(){var _h=document.documentElement,_b=document.body;if(_h)_h.style.setProperty('overscroll-behavior-y','auto','important');if(_b)_b.style.setProperty('overscroll-behavior-y','auto','important');})();

/* 연출 엔진(SPEC v1) — [data-tl] 타임라인 재생. s/r/x/y=transform, o=opacity, blur/bright/contr/sat/hue/gray/sepia/invert=filter, clip, mask */
(function(){var els=document.querySelectorAll('[data-tl]');if(!els.length)return;
function lerp(a,b,t){return a+(b-a)*t;}
function at(tl,k){if(k<=tl[0].p)return tl[0];for(var i=0;i<tl.length-1;i++){var a=tl[i],b=tl[i+1];if(k>=a.p&&k<=b.p){var t=(k-a.p)/(b.p-a.p),o={};for(var key in a){if(key==='p')continue;o[key]=(typeof a[key]==='number'&&typeof b[key]==='number')?lerp(a[key],b[key],t):b[key];}return o;}}return tl[tl.length-1];}
function apply(el,st){el.style.transform='scale('+(st.s||1)+') rotate('+(st.r||0)+'deg) translate('+(st.x||0)+'px,'+(st.y||0)+'px)';if(st.o!=null)el.style.opacity=st.o;var f=[];if(st.blur!=null)f.push('blur('+st.blur+'px)');if(st.bright!=null)f.push('brightness('+st.bright+')');if(st.contr!=null)f.push('contrast('+st.contr+')');if(st.sat!=null)f.push('saturate('+st.sat+')');if(st.hue!=null)f.push('hue-rotate('+st.hue+'deg)');if(st.gray!=null)f.push('grayscale('+st.gray+')');if(st.sepia!=null)f.push('sepia('+st.sepia+')');if(st.invert!=null)f.push('invert('+st.invert+')');if(f.length)el.style.filter=f.join(' ');if(st.reveal!=null)el.style.clipPath='inset(0 0 '+((1-st.reveal)*100).toFixed(1)+'% 0)';else if(st.clip)el.style.clipPath=st.clip;if(st.mask)el.style.webkitMaskImage=el.style.maskImage=st.mask;}
function tick(){var vh=innerHeight;for(var i=0;i<els.length;i++){var el=els[i],tgt=el.querySelector('img')||el;var r=el.getBoundingClientRect();var k=Math.max(0,Math.min(1,(vh-r.top)/(vh*0.8)));var tl;try{tl=JSON.parse(el.getAttribute('data-tl'));}catch(e){continue;}apply(tgt,at(tl,k));}requestAnimationFrame(tick);}
requestAnimationFrame(tick);})();

(function(){document.documentElement.classList.add('wt-js');var bs=document.querySelectorAll('.wt-bubble');if(!bs.length)return;for(var i=0;i<bs.length;i++){var b=bs[i];var t=b.textContent;b.innerHTML=t.split('').map(function(c,j){return '<span class="wt-char" style="animation-delay:'+(j*0.04).toFixed(3)+'s">'+(c===' '?'&nbsp;':c)+'</span>';}).join('');}var shakes={};for(var k=0;k<bs.length;k++){(function(el){el.addEventListener('click',function(){shakes[el]=Date.now()+450;});})(bs[k]);}if('IntersectionObserver'in window){var io=new IntersectionObserver(function(es){for(var j=0;j<es.length;j++){if(es[j].isIntersecting)es[j].target.classList.add('wt-in');else es[j].target.classList.remove('wt-in');}},{threshold:0.3});for(var l=0;l<bs.length;l++)io.observe(bs[l]);}else{for(var m=0;m<bs.length;m++)bs[m].classList.add('wt-in');}function tick(){var now=Date.now(),vh=innerHeight;for(var j=0;j<bs.length;j++){var b=bs[j];if(!b.classList.contains('wt-in'))continue;var r=b.getBoundingClientRect(),c=r.top+r.height/2,d=Math.abs(c-vh/2);var kk=Math.max(0,1-d/(vh/2)),s=0.95+kk*0.13;var sway=Math.sin(now/800+j*1.3)*5;var sh=0;if(shakes[b]&&now<shakes[b]){var tt=(shakes[b]-now)/450;sh=Math.sin(now/40)*9*tt;}b.style.transform='scale('+s.toFixed(3)+') translateX('+(sway+sh).toFixed(1)+'px)';}requestAnimationFrame(tick);}requestAnimationFrame(tick);})();

/* INFO 객체 연출 — 카운트업 + 막대성장 + 탭 버튼 (SPEC v1: info object) */
(function(){
function ease(p){return p<.5?2*p*p:-1+(4-2*p)*p;}
var ioN=null,ioB=null;
if('IntersectionObserver'in window){
  ioN=new IntersectionObserver(function(es){es.forEach(function(e){if(e.isIntersecting){var el=e.target,t=parseInt(el.getAttribute('data-count'),10),s=el.getAttribute('data-suffix')||'',d=1200,t0=null;function st(ts){if(!t0)t0=ts;var p=Math.min(1,(ts-t0)/d);el.textContent=Math.round(t*ease(p))+s;if(p<1)requestAnimationFrame(st);}requestAnimationFrame(st);ioN.unobserve(el);}});},{threshold:0.5});
  ioB=new IntersectionObserver(function(es){es.forEach(function(e){if(e.isIntersecting){e.target.style.width=e.target.getAttribute('data-bar')+'%';ioB.unobserve(e.target);}});},{threshold:0.5});
}
var nums=document.querySelectorAll('[data-count]');nums.forEach(function(n){if(ioN)ioN.observe(n);else n.textContent=n.getAttribute('data-count')+(n.getAttribute('data-suffix')||'');});
var bars=document.querySelectorAll('[data-bar]');bars.forEach(function(b){if(ioB)ioB.observe(b);else b.style.width=b.getAttribute('data-bar')+'%';});
var tabs=document.querySelectorAll('[data-tab]');tabs.forEach(function(t){t.addEventListener('click',function(){var g=t.getAttribute('data-group')||'g';document.querySelectorAll('[data-tab][data-group="'+g+'"]').forEach(function(x){x.style.background='rgba(160,138,76,.15)';x.style.color='#e9e5cf';});t.style.background='#a08a4c';t.style.color='#0c1710';document.querySelectorAll('[data-panel="'+g+'"]').forEach(function(p){p.style.display='none';});var tgt=document.querySelector('[data-panel="'+g+'"][data-pane="'+t.getAttribute('data-pane')+'"]');if(tgt)tgt.style.display='block';});});
})();
