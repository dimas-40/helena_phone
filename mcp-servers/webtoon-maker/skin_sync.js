/* 스킨 싱크 v2 — PC 스킨(/4)과 모바일 스킨(/m/4)이 같은 숫자를 내게 만든다.
   (2026-09-18 박씨: "모바일 조건으로 똑같이 나올 수 있게 싱크해라")
   ★ v2 (2026-09-18 박씨: "PC 전체화면이랑 PC 브라우저에서 모바일로 보기, 이게
   깨져 있어"): 싱크는 **한 번 재고 끝나는 계산이 아니다.** 스킨은 모드를 바꾼다
   — 박씨가 스킨 상단에 만들어 둔 [모바일] 버튼이 body.s21-mobile 을 토글한다.
   v1 은 (1) 문서 로드 때 한 번만 돌았고 (2) 모드 판정에 그 클래스가 없었고
   (3) 한 번 흡수한 여백(0)을 되돌리는 길이 없었다. 그래서 토글을 켜면 스킨은
   기둥을 1430 전폭으로 넓히는데 우리 스트립만 720 으로 가운데 떠서 좌변이
   115 vs 355 = 240px 어긋났다(실측) — 폰 미리보기로 안 읽히고 깨진 화면이 된다.
   v2 는 만진 것을 전부 기록해 **되돌리고**, body.s21-mobile 을 모드로 읽고,
   데스크톱+모바일 모드에서 **기둥 자체를 폰 폭(430)으로** 좁혀 제목·머리말·
   스트립을 같은 기둥에 세우고, body class 변경·리사이즈에서 다시 돈다. */
(function(){
var root=document.getElementById('parksy-webtoon');if(!root)return;

/* ⓪ 우리가 조상에 만진 것을 전부 기록한다 — 모드가 바뀌면 **되돌리고** 다시
      흡수한다. 기록 없이 덧칠하면 PC 모드에서 0 으로 깎은 여백이 그대로 남는다. */
var TOUCH=[];
function _set(el,prop,val){
  var seen=false;
  for(var i=0;i<TOUCH.length;i++){if(TOUCH[i][0]===el&&TOUCH[i][1]===prop)seen=true;}
  if(!seen)TOUCH.push([el,prop,el.style.getPropertyValue(prop),
                       el.style.getPropertyPriority(prop)]);
  el.style.setProperty(prop,val,'important');
}
function _undo(){
  for(var i=0;i<TOUCH.length;i++){
    var el=TOUCH[i][0],prop=TOUCH[i][1],old=TOUCH[i][2],pri=TOUCH[i][3];
    if(old)el.style.setProperty(prop,old,pri);else el.style.removeProperty(prop);
  }
  TOUCH=[];
  var st=document.getElementById('parksy-skin-sync');
  if(st&&st.parentNode)st.parentNode.removeChild(st);
}

/* ① 모드 판정 — ★ body.s21-mobile(박씨가 스킨 상단에 만들어 둔 [모바일] 토글)을
      포함한다. v1 은 이걸 몰라서 토글을 켜도 'PC' 로 판정했다. */
function _mode(){
  var dt=(document.body.getAttribute('data-agent-type')||'');
  var cls=' '+(document.body.className||'')+' ';
  return /web_mobile|mobile/.test(dt)||/^\/m\//.test(location.pathname)
      ||/ s21-mobile /.test(cls)
      ||!!document.querySelector('article#mainContent,.blogview_content');
}


function sync(){
  _undo();
  var mob=_mode(), vw=window.innerWidth;
  /* 데스크톱 화면 + 모바일 모드 = 스킨의 '모바일 보기'.
     ★ 여기서 **기둥을 폰 폭으로 좁히면 안 된다.** 초판이 그렇게 했다가 박씨가
     바로 잡았다: "모바일로 보기 하니까 이게 더 작아졌어." 좁히는 게 아니라
     **스킨이 그 모드에서 쓰는 기사 폭에 맞추는** 것이다. 스킨은 s21-mobile 에서
     기둥을 1430 전폭으로 넓히고 제목 상자를 1200 으로 잡는다(실측 115..1315).
     우리 스트립만 720 가운데 떠서 좌변이 240px 어긋났던 것을, 제목 상자와
     **같은 폭·같은 좌표**로 세워 맞춘다(작아지지도, 어긋나지도 않는다).
     (390 실기기 모드는 vw<900 이라 이 분기를 타지 않는다 — 기존 패리티 보존) */
  var alignCol=mob&&vw>900;
  document.documentElement.setAttribute('data-parksy-skin',mob?'mobile':'pc');
  root.setAttribute('data-parksy-mode',(mob?'mobile':'pc')+(alignCol?'-align':''));
  root.setAttribute('data-parksy-absorbed','');

  /* ② 호스트 체인의 좌우 여백을 우리가 흡수한다.
        고정 조상(#wrap)은 사이드바 자리라 건드리지 않는다.
        outermost = 가장 바깥의 비고정 조상 = 이 스킨의 '본문 기둥'. */
  var e=root.parentElement, absorbed=[], outermost=null;
  while(e&&e.tagName!=='HTML'){
    var cs=getComputedStyle(e);
    if(cs.position!=='fixed'){
      /* ★ outermost = 가장 **바깥**의 비고정 조상. 위로 올라가며 매번 덮어쓴다
         (v2 초판은 '첫 번째'를 잡아 가장 안쪽 조상(contents_style)을 기둥으로
         삼았다 — 그래서 스트립만 430 으로 접히고 스킨 제목은 1200 고정폭으로
         기둥 밖에 남았다. 기둥은 제목과 스트립을 **함께** 담는 조상이어야 한다.) */
      if(e!==document.body)outermost=e;   /* body 는 기둥이 아니다 — 문서 판이다 */
      var pl=parseFloat(cs.paddingLeft)||0, pr=parseFloat(cs.paddingRight)||0;
      var ml=parseFloat(cs.marginLeft)||0, mr=parseFloat(cs.marginRight)||0;
      if(pl||pr){_set(e,'padding-left','0');_set(e,'padding-right','0');
                 absorbed.push(pl+pr);}
      if(ml||mr){_set(e,'margin-left','0');_set(e,'margin-right','0');}
      /* 폭을 스스로 깎는 조상(max-width·스크롤바 거터)을 펴준다.
         PC 체인의 .container 만 390 안에서 380 이었다 — 그 10px 이 패널 폭
         차이(348 vs 358)로 남았다. 양쪽 폭을 부모 폭에 그대로 붙인다. */
      if(cs.maxWidth!=='none'||e.clientWidth<e.parentElement.clientWidth-1){
        _set(e,'max-width','none');_set(e,'width','auto');
      }
      /* ②-b **칠해진 조상**을 벗긴다 — 모바일 스킨은 글 본문 상자를 흰색
         (article#mainContent rgb(255,255,255))과 옅은 회색(.main-content
         rgb(247,247,247))으로 칠한다. 그래서 먹색 스트립이 **흰 종이 위에 뜬
         카드**로 보였다. 바탕은 body 하나만 칠하게 한다.
         ★ html·body 는 벗기지 않는다 — 그 둘이 바탕(먹색 + 오라)을 칠하는
         판이다. 벗기면 바탕이 캔버스까지 내려가 흰 종이가 드러난다. */
      var bg=cs.backgroundColor;
      if(bg&&bg!=='rgba(0, 0, 0, 0)'&&bg!=='transparent'
         &&e!==document.body&&e!==document.documentElement){
        _set(e,'background-color','transparent');_set(e,'background-image','none');
      }
    }
    e=e.parentElement;
  }
  /* ②-c 스킨의 '모바일 보기' 기사 폭 = 제목 상자(own-text·20px↑·상단)의 폭.
        그 폭에 스트립을 맞춘다 — 좁히지 않는다. 없으면 0(뷰포트 기본값). */
  var colW=0;
  if(alignCol){
    var cd=document.querySelectorAll('body *');
    for(var ci=0;ci<cd.length;ci++){
      var el2=cd[ci];
      if(root.contains(el2))continue;
      var own2=false,ch2=el2.childNodes;
      for(var k2=0;k2<ch2.length;k2++){
        if(ch2[k2].nodeType===3&&ch2[k2].textContent.trim())own2=true;}
      if(!own2)continue;
      var s2=getComputedStyle(el2);
      if(s2.display==='none'||s2.visibility==='hidden')continue;
      if((parseFloat(s2.fontSize)||0)<20)continue;
      var r2=el2.getBoundingClientRect();
      if(r2.top>600||r2.width<40)continue;
      if(r2.width>colW)colW=Math.round(r2.width);
    }
    root.setAttribute('data-parksy-colw',colW+'');
  }

  /* ★ 폭 = min(설계폭, 뷰포트, 호스트 기사 기둥).
       · 설계폭: 기본 720. 스킨의 '모바일 보기'에서는 **제목 상자 폭**(실측 1200)
         — 작아지지도 어긋나지도 않게 그 모드의 기사 폭에 맞춘다.
       · 100vw - 44px: 390 실기기 실측값. 모바일 스킨과의 패리티가 이 값으로
         맞춰져 있다(호스트 체인에서 유도하면 PC 만 스크롤바 거터 10px 만큼
         좁아져 패리티가 깨진다 — 그게 v1 의 원인이었다).
       · 100%: 호스트 기사 기둥. 1024 화면에서 스트립이 기둥(700) 밖으로
         20px 삐져나온 것을 막는 상한이다(실측: 298..1018 vs 298..998). */
  var designW=(alignCol&&colW>=200)?Math.max(720,colW):720;
  /* 정렬 모드(스킨의 모바일 보기)에서는 44px 여백 상한을 **빼야** 한다 —
     1024 실측: 제목 상자가 1014 인데 상한이 스트립을 980 으로 깎아 34px 작아졌다
     (박씨 법칙: 모바일 보기에서 작아지면 결함이다). 제목 상자와 정확히 같은 폭. */
  var stripW=alignCol?'min('+designW+'px,100%)'
                     :'min('+designW+'px,calc(100vw - 44px),100%)';
  var CSS=[
   /* 바탕 — 모바일 스킨은 흰 바탕이라 스트립이 흰 여백에 떠 보였다 */
   'html,body{background:#08090a !important}',
   /* 오라 — PC 스킨은 #wrap 이 자기 방식으로 그리고, 모바일 스킨은 아예 없다.
      그래서 **양쪽 모두 우리가 html/body 에 같은 규칙으로** 깐다. */
   'html,body{background-image:radial-gradient(1200px 720px at 16% -8%, rgba(96,70,180,.52), rgba(0,0,0,0) 58%),radial-gradient(1000px 620px at 96% 10%, rgba(45,212,191,.44), rgba(0,0,0,0) 55%),radial-gradient(880px 560px at 6% 102%, rgba(240,180,41,.3), rgba(0,0,0,0) 55%),radial-gradient(820px 520px at 60% 108%, rgba(232,180,90,.16), rgba(0,0,0,0) 55%) !important;'
   +'background-attachment:fixed !important;background-repeat:no-repeat !important}',
   /* PC 스킨의 #wrap 은 뷰포트를 덮는 고정 판이라, 자기가 그린 바탕이 우리
      html/body 의 오라를 **가린다**. 판을 비운다 — 바탕을 그리는 자리는
      html/body 하나뿐이어야 두 스킨이 같은 픽셀을 낸다. */
   '#wrap{background-image:none !important;background-color:transparent !important}',
   '#parksy-webtoon,#parksy-webtoon *{box-sizing:border-box !important}',
   '#parksy-webtoon{width:'+stripW+' !important;'
   +'max-width:none !important;margin:0 auto !important;'
   +'padding:20px 16px 80px !important;background:#0c1710 !important;color:#e9e5cf !important}',
   /* 그림이 카드보다 넓어 필름 퍼포레이션이 잘렸다 */
   '#parksy-webtoon .panel,#parksy-webtoon .cut{width:100% !important;max-width:100% !important}',
   '#parksy-webtoon .cut img{width:100% !important;height:auto !important;'
   +'max-width:100% !important;display:block !important}',
   /* 모바일 스킨이 !important 로 이기던 것들 — px 로 못 박는다 */
   '#parksy-webtoon .cap{font-size:14px !important;line-height:26.6px !important;'
   +'word-break:keep-all !important;overflow-wrap:break-word !important;'
   +'text-align:left !important;margin:0 !important}',
   '#parksy-webtoon .wt-line,#parksy-webtoon .wt-char{line-height:26.6px !important;'
   +'word-break:keep-all !important;overflow-wrap:break-word !important}',
   '#parksy-webtoon .mast h1{font-size:26px !important;line-height:1.2 !important;'
   +'letter-spacing:normal !important;word-break:keep-all !important;'
   +'overflow-wrap:break-word !important}',
   /* ★ 탭 판(12.5px)의 행간 — 모바일 스킨의 **투명 패턴 규칙**을 이긴다:
      `.blogview_content [style*=font-size]{line-height:1.5em!important}`
      (티스토리 모바일 index.css 실측, 2026-09-18). 인라인에 font-size 가 있으면
      그 규칙에 걸려 행간이 1.5em(=18.75px)로 눌린다 — 인라인 line-height 는
      !important 가 없으면 진다. 발행 검수가 정확히 이 3개 노드에서 걸렸다. */
   '#parksy-webtoon [data-panel]{line-height:20.25px !important}',
   /* ★ 실측(1559개 노드 전수 대조) — 스킨이 **상속으로** 갈라놓는 것들.
      PC 스킨은 390 화면에서 기준 17px·행간 1.75·word-break:break-word, 모바일
      스킨은 16px·1.5·break-all 이다. 우리가 px 로 못 박지 않은 상속 노드
      101개(크기)·175개(행간)·208개(어절)가 갈라졌다. */
   '#parksy-webtoon{font-size:16px !important;line-height:1.5 !important;'
   +'word-break:keep-all !important;overflow-wrap:break-word !important;'
   +'text-align:left !important}'
  ];
  var st=document.createElement('style');st.id='parksy-skin-sync';
  st.textContent=CSS.join('\n');
  (document.head||document.documentElement).appendChild(st);

  /* ④ 스티키 레일 — 조상에 overflow:hidden 이 있으면 sticky 가 죽는다.
        모바일 스킨은 article 계열에 overflow:hidden 을 자주 건다. */
  var p=root.parentElement;
  while(p&&p.tagName!=='HTML'){
    var o=getComputedStyle(p);
    if(o.position!=='fixed'&&/(hidden|auto|scroll)/.test(o.overflowY||'')
       &&!/(hidden|auto|scroll)/.test(o.overflowX||'')){
      _set(p,'overflow-y','visible');
    }
    p=p.parentElement;
  }
  root.setAttribute('data-parksy-absorbed',absorbed.join(','));
  if(window.__parksyLift)window.__parksyLift();   /* 가독성 재채점 */
}

/* ⑤ 가독성 — 박씨: "왜 글씨가 안 보이냐, 헤더 제목이 안 보이잖아."
      원인은 우리가 바탕을 먹색으로 **소유**했기 때문이다. 남의 스킨은 제목
      (#222)·머리말·태그를 **흰 바탕 전제**로 설계했다. 바탕만 검게 바꾸면
      검은 글자가 검은 판 위에 얹혀 대비 1.25 = 안 보인다(실측).
      바탕을 소유하면 그 바탕 위에 얹히는 남의 글자도 우리 책임이다.
      WCAG AA(본문 4.5 · 큰글자 3.0)로 **재서** 못 미치는 것만 종이색으로 올린다. */
function _lum(c){function f(v){v/=255;return v<=0.03928?v/12.92:Math.pow((v+0.055)/1.055,2.4);}
  return 0.2126*f(c[0])+0.7152*f(c[1])+0.0722*f(c[2]);}
function _parse(s){var m=(s||'').match(/[\d.]+/g);if(!m)return null;
  return [+m[0],+m[1],+m[2],m[3]===undefined?1:+m[3]];}
function _effBg(el){                      /* 조상 바탕을 알파 합성 — 캔버스까지 */
  var e=el,stack=[],c;
  while(e&&e.tagName!=='HTML'){c=_parse(getComputedStyle(e).backgroundColor);
    if(c&&c[3]>0)stack.push(c);e=e.parentElement;}
  c=_parse(getComputedStyle(document.documentElement).backgroundColor);
  if(c&&c[3]>0)stack.push(c);
  var acc=[255,255,255];
  for(var i=stack.length-1;i>=0;i--){var q=stack[i];
    acc=[q[0]*q[3]+acc[0]*(1-q[3]),q[1]*q[3]+acc[1]*(1-q[3]),q[2]*q[3]+acc[2]*(1-q[3])];}
  return acc;}
function _ratio(a,b){var l1=_lum(a),l2=_lum(b);
  return (Math.max(l1,l2)+0.05)/(Math.min(l1,l2)+0.05);}
var PAPER='#e9e5cf';
/* ★ 한 번 재고 끝내면 안 된다 — 스킨의 늦은 스크립트가 우리 뒤에 버튼·툴바를
   만들거나 색을 다시 칠한다(PC 스킨의 공감/공유/태그가 그랬다: 우리가 잰 시각엔
   display:none 이었고, 9초 뒤 발행 검수에서 1.58 로 걸렸다). 그래서 여러 번 돈다. */
function liftPass(){
  var lifted=0,worst=99,all=document.querySelectorAll('body *');
  for(var n=0;n<all.length;n++){
    var el=all[n];
    if(el.closest('#parksy-webtoon'))continue;      /* 스트립 안은 우리 팔레트가 잡았다 */
    var own=false,ch=el.childNodes;
    for(var k=0;k<ch.length;k++){if(ch[k].nodeType===3&&ch[k].textContent.trim())own=true;}
    if(!own)continue;
    var r0=el.getBoundingClientRect();if(r0.width<2||r0.height<2)continue;
    var cs2=getComputedStyle(el);
    if(cs2.visibility==='hidden'||cs2.display==='none'||(+cs2.opacity||0)<0.15)continue;
    /* ★ 전이(transition) 중에는 **재지 않는다**. 스킨의 [📱 모바일] 토글은 배경과
       글자색을 함께 0.16s 로 바꾼다(teal 판 + #0a0c10 글자). 그 창에서 재면
       배경 알파가 반쯤만 올라온 **가짜 어두운 판**이 잡히고(실측 대비 1.4),
       거기서 종이색을 못 박으면 전이가 끝난 뒤에도 인라인 !important 라
       **teal 판 위 종이색 = 1.47** 로 굳는다. 2026-09-18 hitop /4 발행 검수가
       정확히 이것이었다(토글 켠 뒤 150ms 회차에서 못 박힘).
       전이 중이면 이번 회차는 건너뛴다 — 전이가 끝난 다음 회차가 제대로 잰다. */
    if(el.getAnimations&&el.getAnimations().length)continue;
    /* ★ 스스로 판을 칠하는 **컨트롤은 남의 것**이다. 스킨 툴바 버튼은 자기 배경
       (그라디언트 → 켜지면 teal)을 스스로 갖고, 그 판 위 대비도 스킨이 이미
       보장한다(#s21-top-actions button.on{color:#0a0c10}). 남의 컨트롤을 우리
       팔레트로 칠하면 스킨이 맞춰 둔 대비를 **우리가 깬다**. */
    if(el.closest('#s21-top-actions'))continue;
    var bg=_effBg(el),bl=_lum(bg);                   /* 바탕이 어두운가 = 우리 판인가 */
    /* ★ 어두운 판(휘도<0.2)일 때만 올린다. 남의 밝은 판(흰 바탕 위 옅은 회색 글씨,
       #888 on #f7f7f7 = 3.31)은 **플랫폼 자체 디자인**이다 — 우리가 손대면
       종이색 글자가 흰 판 위에 얹혀 1.18 로 **우리가 새로 안 보이게 만든다**. */
    if(el.__parksyOrig!==undefined && bl>=0.2){      /* 판이 나중에 밝아졌다 → 되돌린다 */
      el.style.setProperty('color',el.__parksyOrig,'important');
      delete el.__parksyOrig;
    }
    var fg=_parse(cs2.color);if(!fg)continue;
    var fa=(fg[3]===undefined?1:fg[3]);          /* 글자 알파도 바탕과 섞어서 잰다 */
    var fgx=[fg[0]*fa+bg[0]*(1-fa),fg[1]*fa+bg[1]*(1-fa),fg[2]*fa+bg[2]*(1-fa)];
    var fs=parseFloat(cs2.fontSize)||16,bold=(parseInt(cs2.fontWeight)||400)>=700;
    var need=(fs>=24||(fs>=18.66&&bold))?3.0:4.5;
    var cr=_ratio(fgx,bg);
    if(bl<0.2&&cr<worst)worst=cr;
    if(bl<0.2&&cr<need){
      if(el.__parksyOrig===undefined)el.__parksyOrig=cs2.color;
      el.style.setProperty('color',PAPER,'important');lifted++;
    }
  }
  var prev=parseInt(root.getAttribute('data-parksy-lifted')||'0',10)||0;
  root.setAttribute('data-parksy-lifted',
    Math.max(prev,lifted)+'/'+(worst===99?'-':Math.round(worst*100)/100));
  root.setAttribute('data-parksy-lift-runs',
    (parseInt(root.getAttribute('data-parksy-lift-runs')||'0',10)+1)+'');
}
window.__parksyLift=liftPass;                  /* 검수기가 필요하면 직접 부른다 */

sync();                                        /* 즉시 */
window.__parksySync=sync;                      /* 검수기가 모드를 강제하고 다시 부른다 */
window.addEventListener('load',sync);          /* 스킨 자원까지 다 온 뒤 */
var _RT=0;window.addEventListener('resize',function(){clearTimeout(_RT);_RT=setTimeout(sync,200);});
var _T=[900,2500,6000];                        /* 스킨의 늦은 스크립트 대비 */
for(var t=0;t<_T.length;t++)setTimeout(sync,_T[t]);
/* ★ 모드 전환(박씨의 [모바일] 토글 = body class 변경)에서 **다시 돈다**.
   v1 은 로드 때 한 번만 돌아서 토글을 켜도 PC 배치가 그대로 남았다.
   ★ 2026-09-18: 한 번만 돌면 **전이(0.16s) 중간을 재서** 가짜 판에 종이색을
   못 박는다(위 liftPass 주석). 그래서 전이가 끝난 뒤에도 두 번 더 돈다 —
   재채점은 멱등이고, 판이 밝아진 요소는 되돌리는 분기가 있다. */
if(window.MutationObserver){
  var _MT=0;
  new MutationObserver(function(){clearTimeout(_MT);
      setTimeout(sync,150);setTimeout(sync,500);setTimeout(sync,1200);})
    .observe(document.body,{attributes:true,attributeFilter:['class']});
}
})();
