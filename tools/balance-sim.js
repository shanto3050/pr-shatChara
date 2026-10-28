// Balance simulator: plays headless matches of index.html with a scripted player.
// Usage: node tools/balance-sim.js [matchesPerSetting]
// Optional: PATCH='SK.normal.react=.8' node tools/balance-sim.js 100   (try a tweak without editing the game)
const fs=require('fs');
const html=fs.readFileSync(require('path').join(__dirname,'..','index.html'),'utf8');
let src=html.slice(html.indexOf('<script>')+8,html.lastIndexOf('</script>')).replace(/try\{window\.claude[\s\S]*$/,'');
const noop=()=>{};
const ctxP=new Proxy({},{get:(t,k)=>k==='measureText'?()=>({width:10}):(k in t?t[k]:noop),set:(t,k,v)=>{t[k]=v;return true}});
const el=()=>({hidden:false,disabled:false,textContent:'',innerHTML:'',style:{},dataset:{},addEventListener:noop,setAttribute:noop,getContext:()=>ctxP,getBoundingClientRect:()=>({left:0,top:0,width:600,height:800}),clientWidth:600,clientHeight:800,setPointerCapture:noop});
global.document={querySelector:el,querySelectorAll:()=>[],createElement:el};
global.matchMedia=()=>({matches:false});global.addEventListener=noop;global.window=global;global.navigator={};
global.performance={now:()=>0};global.requestAnimationFrame=noop;global.ResizeObserver=class{observe(){}};
const mk=()=>new Function(src+`
;const stats_={rounds:[],hits:0,defThrows:0};
const _e=endRound;endRound=function(w,sw,t,big){if(G.phase!=='roundover'&&G.phase!=='over')stats_.rounds.push({att:G.attacking,w,t,stacked:G.stacked,rebuild:45-G.timer});return _e(w,sw,t,big)};
const _h=hitOut;hitOut=function(p){stats_.hits++;return _h(p)};
const _tb=throwBall;throwBall=function(p,a,s){if(G.phase==='rebuild'&&p.team!==G.attacking&&s>400)stats_.defThrows++;return _tb(p,a,s)};
;${process.env.PATCH||""};return {G,setupRound,update,human,throwBall,st:stats_};`)();
const N=+process.argv[2]||10;
// "average human" bot: decent aim when attacking, decent aim when defending, moves toward next stone when rebuilding
function bot(S){
  const h=S.human(),b=S.G.ball,G=S.G;if(!h)return;
  if(b.state==='held'&&b.holder===h){
    h._t=(h._t||0)+1/60;
    if(G.phase==='throw'&&h._t>1){h._t=0;S.throwBall(h,Math.atan2(330-h.y,300-h.x)+(Math.random()-.5)*.16,560+Math.random()*120);}
    else if(G.phase==='rebuild'&&h._t>.8){
      const ts=G.players.filter(q=>q.alive&&q.team!==h.team).sort((a,c)=>Math.hypot(a.x-h.x,a.y-h.y)-Math.hypot(c.x-h.x,c.y-h.y));
      if(ts[0]){h._t=0;S.throwBall(h,Math.atan2(ts[0].y-h.y,ts[0].x-h.x)+(Math.random()-.5)*.2,560);}
    }
  }
}
const out=[];
for(const mode of ['classic','village'])for(const diff of ['easy','normal','hard']){
  const a={ourAtt:0,ourAttW:0,rivAtt:0,rivAttW:0,rounds:0,attW:0,youPts:0,rivPts:0,youWins:0,len:0,reb:[],hitsPerRebuild:0,rebuilds:0,noTopple:0,timeUp:0,defThrows:0};
  for(let m=0;m<N;m++){
    const S=mk();S.G.diff=diff;S.G.mode=mode;S.G.attacking=0;S.setupRound();
    for(let i=0;i<60*900;i++){bot(S);S.update(1/60);if(Math.max(...S.G.score)>=5&&S.G.phase!=='roundover')break;if(Math.max(...S.G.score)>=5&&S.G.roundT<0.1)break;}
    a.youPts+=S.G.score[0];a.rivPts+=S.G.score[1];if(S.G.score[0]>S.G.score[1])a.youWins++;a.len+=S.G.t;
    for(const r of S.st.rounds){a.rounds++;if(r.att===0){a.ourAtt++;if(r.w===0)a.ourAttW++;}else{a.rivAtt++;if(r.w===1)a.rivAttW++;}if(r.w===r.att)a.attW++;if(r.t.startsWith('No hit')||r.t.startsWith('Caught'))a.noTopple++;else{a.rebuilds++;a.reb.push(r.rebuild);}if(r.t.startsWith("Time"))a.timeUp++;}
    a.hitsPerRebuild+=S.st.hits;a.defThrows+=S.st.defThrows;
  }
  const med=a.reb.sort((x,y)=>x-y)[a.reb.length>>1]||0;
  out.push(`${mode.padEnd(8)}${diff.padEnd(7)} youWin ${(a.youWins/N*100).toFixed(0).padStart(3)}%  pts ${a.youPts}-${a.rivPts}  ourAtt ${(a.ourAttW/a.ourAtt*100).toFixed(0)}% rivAtt ${(a.rivAttW/a.rivAtt*100).toFixed(0)}%  noTopple ${(a.noTopple/a.rounds*100).toFixed(0)}%  medRebuild ${med.toFixed(1)}s  hits/rebuild ${(a.hitsPerRebuild/a.rebuilds).toFixed(2)}  hit% ${(a.hitsPerRebuild/a.defThrows*100).toFixed(0)}  timeUp ${a.timeUp}  match ${(a.len/N).toFixed(0)}s`);
}
console.log(out.join('\n'));
