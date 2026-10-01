#!/usr/bin/env python3
# Card generator template. Schemas: intro-plane, iPhone reveal, dark WhatsApp chat+logo,
# template message, vertical flow, CRM 5, step-by-step compare, stat+graph, CTA.
import json, re, html, sys
# Usage: python gen.py <cut_transcript.json>  (run it from inside the project's cards/ folder)
# Logos go in cards/assets/logos/ and the screenshot in cards/assets/iphone_phone.png
# EDIT the BEATS list below with the reel's content (trigger = the word the card starts on).
# NOTE: the BEATS below are a worked example (English) — replace them with your own beats.
A="#2fe081"; AD="rgba(47,224,129,0.45)"; GL="rgba(47,224,129,0.16)"; RED="#ff5470"; REDD="rgba(255,84,112,0.45)"
WA="#25D366"; WAB="#005c4b"; WAIN="#1f2c33"
d=json.load(open(sys.argv[1] if len(sys.argv)>1 else "cut_transcript.json"))
WS=[w for w in d["words"] if w.get("type")!="spacing" and w.get("start") is not None]
TOTAL=round(WS[-1]["end"],2)+0.2
def norm(s): return re.sub(r"[^a-z0-9àèéìòù ]","",s.lower())
TOK=[norm(w["text"]) for w in WS]
def find(trig):
    tt=norm(trig).split()
    for i in range(len(TOK)-len(tt)+1):
        if TOK[i:i+len(tt)]==tt: return round(WS[i]["start"],2)
    for i,t in enumerate(TOK):
        if tt and t==tt[0]: return round(WS[i]["start"],2)
    return 0.0
def find_after(trig, after):
    # like find() but AFTER a given time: use it for words that also occur earlier (e.g. "these
    # four" in the hook and later) -> anchors the beat to the RIGHT occurrence, not the first.
    tt=norm(trig).split()
    for i in range(len(TOK)-len(tt)+1):
        if TOK[i:i+len(tt)]==tt and WS[i]["start"]>=after-0.01: return round(WS[i]["start"],2)
    return after
def esc(s): return html.escape(s)
def eb(e,red=False): return f'<div class="eyebrow{" red" if red else ""}"><span class="ebdot{" red" if red else ""}"></span>{esc(e)}</div>' if e else ""
def poly(dirn): return "0,150 110,120 220,135 330,95 440,105 550,55 600,40" if dirn=="up" else "0,40 110,60 220,52 330,95 440,90 550,140 600,150"

BEATS=[
 ("If you run a business","intro",{"t1":"SMALL","t2":"BUSINESSES"}),
 ("hundreds of old","statgraph",{"eyebrow":"IN YOUR CRM","count":340,"suffix":"+","unit":"LEADS & CLIENTS","dir":"down"}),
 ("worth thousands","summary",{"eyebrow":"WORTH","kw":"THOUSANDS"}),
 ("nobody is following","graph",{"eyebrow":"LOST REVENUE","dir":"down","color":RED}),
 ("You have hundreds of contacts","crm",{"eyebrow":"IDLE CONTACTS","rows":[("Sarah K.","asked for a quote"),("James P.","bought in 2024"),("Amina B.","trial never upgraded"),("Leo M.","demo, no reply"),("Nora T.","cart abandoned")]}),
 ("clients who already","listcheck",{"eyebrow":"SLEEPING IN HERE","rows":[("Already bought from you","clients who already"),("Quotes never closed","leads who asked")]}),
 ("Next month","calendar",{"eyebrow":"NEXT MONTH"}),
 ("follow up by hand","comstep",{"eyebrow":"FOLLOWING UP BY HAND","items":[("Hundreds of messages","hundreds of messages"),("One by one","one by one"),("At the right time","at the right time")],"stamp":("IMPOSSIBLE","impossible")}),
 ("Claude does it","iphone",{}),
 ("agent","wachat",{"msgs":[("in","Hi Sarah! You asked about a quote last month","agent"),("in","We have a slot this week, want me to send it again?","reopens the conversation")]}),
 ("starts from their","msgtpl",{"eyebrow":"EVERY MESSAGE IS A TEMPLATE"}),
 ("come back as clients","graph",{"eyebrow":"CLIENTS WHO COME BACK","dir":"up","color":A}),
 ("without you lifting","vflow",{"items":[("CONTACTS","already in your CRM","📇"),("AGENT","handles it","🤖"),("CLIENTS","who buy again","✅")]}),
 ("Comment GUIDE","cta",{"eyebrow":"COMMENT","kw":"GUIDE"}),
]
starts=[find(t) for t,_,_ in BEATS]; ends=[starts[i+1] for i in range(len(starts)-1)]+[TOTAL]

def inner(i,t,p):
    if t=="intro":
        return (f'<div class="introtxt"><div class="introeb">FOR</div><div class="introt1" id="it1{i}">{esc(p["t1"])}</div>'
                f'<div class="introt2" id="it2{i}">{esc(p["t2"])}</div></div>'
                f'<svg class="flightsvg" viewBox="0 0 960 620" preserveAspectRatio="none">'
                f'<path id="fp{i}" d="M 40 540 Q 480 120 920 300" fill="none" stroke="{A}" stroke-width="4" stroke-dasharray="14 16" opacity="0.85"/>'
                f'<circle cx="40" cy="540" r="12" fill="{A}"/><circle cx="920" cy="300" r="12" fill="{A}"/></svg>'
                f'<div class="plane" id="pl{i}">✈</div>')
    if t=="statgraph":
        return f'{eb(p["eyebrow"])}<div class="statrow"><div class="big" id="big{i}">0</div><div class="unit">{esc(p["unit"])}</div></div><svg class="spark" viewBox="0 0 600 150" preserveAspectRatio="none"><polyline id="sp{i}" points="{poly(p["dir"])}" style="stroke:{A}"/></svg>'
    if t=="summary":
        return f'{eb(p["eyebrow"])}<div class="kw" id="kw{i}">{esc(p["kw"])}</div>'
    if t=="graph":
        return f'{eb(p["eyebrow"])}<svg class="sparkbig" viewBox="0 0 600 170" preserveAspectRatio="none"><polyline id="sp{i}" points="{poly(p["dir"])}" style="stroke:{p["color"]}"/></svg>'
    if t=="crm":
        rows="".join(f'<div class="crow" id="b{i}c{j}"><span class="ava"></span><span class="cn">{esc(n)}</span><span class="cs">{esc(s)}</span><span class="cz">IDLE</span></div>' for j,(n,s) in enumerate(p["rows"]))
        return f'{eb(p["eyebrow"])}<div class="crm">{rows}</div>'
    if t=="listcheck":
        rows="".join(f'<div class="lrow" id="b{i}l{j}"><span class="lck">✓</span><span class="lt">{esc(x)}</span></div>' for j,(x,_) in enumerate(p["rows"]))
        return f'{eb(p["eyebrow"])}<div class="lc">{rows}</div>'
    if t=="calendar":
        cells="".join(f'<span class="cal {"hot" if k==18 else ""}">{(k+1) if k<30 else ""}</span>' for k in range(35))
        return f'{eb(p["eyebrow"])}<div class="calg" id="cg{i}">{cells}</div>'
    if t=="comstep":
        items="".join(f'<div class="cmi bad" id="b{i}s{j}">✕ {esc(x)}</div>' for j,(x,_) in enumerate(p["items"]))
        stamp=f'<div class="stamp" id="b{i}st">{esc(p["stamp"][0])}</div>'
        return f'{eb(p["eyebrow"],True)}<div class="comstep">{items}</div>{stamp}'
    if t=="iphone":
        logos="".join(f'<img src="assets/logos/{l}.svg" class="plogo"/>' for l in ["whatsapp","claude","openai","github"])
        return f'<div class="iphwrap"><img src="assets/iphone_phone.png" class="iph" id="iph{i}"/><div class="poweredby"><span>POWERED BY</span>{logos}</div></div>'
    if t=="wachat":
        b="".join(f'<div class="wbub {s}" id="b{i}m{j}">{esc(m)}<span class="wt">15:3{j} ✓✓</span></div>' for j,(s,m,_) in enumerate(p["msgs"]))
        return f'<div class="wahead"><img src="assets/logos/whatsapp.svg" class="walogo"/><div class="waname">Agent<span>online</span></div></div><div class="wabody">{b}</div>'
    if t=="msgtpl":
        return (f'{eb(p["eyebrow"])}<div class="wabody solo"><div class="wbub in" id="mt{i}">'
                f'Hi <span class="ph" id="mp1{i}">[Sarah]</span>! Last time you bought <span class="ph" id="mp2{i}">[the starter pack]</span> '
                f'- you might like <span class="ph" id="mp3{i}">[the new pro kit]</span> 🚀'
                f'<span class="wt">15:32 ✓✓</span></div></div>')
    if t=="vflow":
        parts=[]
        for j,(a1,a2,ic) in enumerate(p["items"]):
            parts.append(f'<div class="vbox" id="b{i}f{j}"><span class="vic">{ic}</span><span class="vt1">{esc(a1)}</span><span class="vt2">{esc(a2)}</span></div>')
            if j<len(p["items"])-1: parts.append(f'<div class="varrow" id="b{i}a{j}">↓</div>')
        return f'<div class="vflow">{"".join(parts)}</div>'
    if t=="cta":
        return f'{eb(p["eyebrow"])}<div class="kw">{esc(p["kw"])}</div><div class="meter"><span id="mt{i}"></span></div>'
    return ""

clips=[];tw=[]
for i,((trig,t,p),s,e) in enumerate(zip(BEATS,starts,ends)):
    dur=max(0.6,e-s)
    wrap="innerfull" if t in ("intro","iphone") else "inner"
    clips.append(f'<div class="beat" id="beat{i}" data-start="{s}" data-duration="{dur:.2f}" data-track-index="{i+2}"><div class="{wrap} {t}" id="in{i}">{inner(i,t,p)}</div></div>')
    js=[f'tl.fromTo("#beat{i}",{{opacity:0,y:30,scale:0.97}},{{opacity:1,y:0,scale:1,duration:0.2,ease:"power3.out"}},{s:.2f});']
    if t=="intro":
        js.append(f'tl.fromTo("#fp{i}",{{attr:{{"stroke-dashoffset":1200}}}},{{attr:{{"stroke-dashoffset":0}},duration:1.6,ease:"power1.inOut"}},{s+0.2:.2f});')
        js.append(f'tl.fromTo("#pl{i}",{{motionPath:{{path:"#fp{i}",align:"#fp{i}",alignOrigin:[0.5,0.5],autoRotate:true,start:0,end:0}}}},{{motionPath:{{path:"#fp{i}",align:"#fp{i}",alignOrigin:[0.5,0.5],autoRotate:true,start:0,end:1}},duration:1.8,ease:"power1.inOut"}},{s+0.2:.2f});')
        js.append(f'tl.fromTo("#it1{i}",{{opacity:0,y:40}},{{opacity:1,y:0,duration:0.5,ease:"power3.out"}},{s+0.6:.2f});')
        js.append(f'tl.fromTo("#it2{i}",{{opacity:0,y:40}},{{opacity:1,y:0,duration:0.5,ease:"power3.out"}},{s+0.9:.2f});')
    if t=="statgraph":
        js.append(f'tl.to({{v:0}},{{v:{p["count"]},duration:0.9,ease:"power2.out",onUpdate:function(){{document.getElementById("big{i}").textContent=Math.round(this.targets()[0].v)+"{p.get("suffix","")}";}}}},{s+0.15:.2f});')
        js.append(f'tl.fromTo("#sp{i}",{{attr:{{"stroke-dashoffset":760}}}},{{attr:{{"stroke-dashoffset":0}},duration:1.0,ease:"power2.out"}},{s+0.2:.2f});')
    if t=="graph":
        js.append(f'tl.fromTo("#sp{i}",{{attr:{{"stroke-dashoffset":760}}}},{{attr:{{"stroke-dashoffset":0}},duration:1.1,ease:"power2.out"}},{s+0.15:.2f});')
    if t=="crm":
        for j in range(len(p["rows"])): js.append(f'tl.fromTo("#b{i}c{j}",{{opacity:0,x:-50}},{{opacity:1,x:0,duration:0.26,ease:"power3.out"}},{s+0.15+j*0.32:.2f});')
    if t=="listcheck":
        for j,(_,rt) in enumerate(p["rows"]): js.append(f'tl.fromTo("#b{i}l{j}",{{opacity:0,x:-50}},{{opacity:1,x:0,duration:0.28,ease:"back.out(1.8)"}},{(find(rt) if rt else s+0.2):.2f});')
    if t=="comstep":
        for j,(_,it) in enumerate(p["items"]): js.append(f'tl.fromTo("#b{i}s{j}",{{opacity:0,x:-60}},{{opacity:1,x:0,duration:0.26,ease:"back.out(1.8)"}},{find(it):.2f});')
        js.append(f'tl.fromTo("#b{i}st",{{opacity:0,scale:1.6,rotate:-8}},{{opacity:1,scale:1,rotate:-6,duration:0.3,ease:"back.out(2)"}},{find(p["stamp"][1]):.2f});')
    if t=="iphone":
        js.append(f'tl.fromTo("#iph{i}",{{opacity:0,y:80,scale:0.9}},{{opacity:1,y:0,scale:1,duration:0.4,ease:"power3.out"}},{s:.2f});')
    if t=="wachat":
        for j,(_,_,mt) in enumerate(p["msgs"]): js.append(f'tl.fromTo("#b{i}m{j}",{{opacity:0,y:24,scale:0.85}},{{opacity:1,y:0,scale:1,duration:0.3,ease:"back.out(1.9)"}},{find(mt):.2f});')
    if t=="msgtpl":
        js.append(f'tl.fromTo("#mt{i}",{{opacity:0,y:24}},{{opacity:1,y:0,duration:0.3,ease:"power3.out"}},{s+0.1:.2f});')
        for k in range(1,4): js.append(f'tl.fromTo("#mp{k}{i}",{{backgroundColor:"rgba(47,224,129,0)",color:"#fff"}},{{backgroundColor:"rgba(47,224,129,0.28)",color:"{A}",duration:0.25,ease:"power2.out"}},{s+0.5+k*0.45:.2f});')
    if t=="vflow":
        for j in range(len(p["items"])): js.append(f'tl.fromTo("#b{i}f{j}",{{opacity:0,y:-40,scale:0.9}},{{opacity:1,y:0,scale:1,duration:0.26,ease:"back.out(1.9)"}},{s+0.15+j*0.4:.2f});')
        for j in range(len(p["items"])-1): js.append(f'tl.fromTo("#b{i}a{j}",{{opacity:0}},{{opacity:1,duration:0.2}},{s+0.35+j*0.4:.2f});')
    if t=="cta":
        js.append(f'tl.fromTo("#mt{i}",{{scaleX:0}},{{scaleX:1,duration:1.0,ease:"power2.out"}},{s+0.3:.2f});')
    js.append(f'tl.to("#beat{i}",{{opacity:0,duration:0.16,ease:"power2.in"}},{e-0.16:.2f});')
    tw.append("\n      ".join(js))

NP=22
parts_html="".join(f'<span class="pt" id="pt{k}" style="left:{(k*131+40)%1040}px;top:{(k*97+30)%760}px;width:{5+(k%3)*3}px;height:{5+(k%3)*3}px;opacity:{0.12+0.2*((k*7)%5)/5:.2f}"></span>' for k in range(NP))
streaks_html="".join(f'<span class="stk" id="stk{k}" style="top:{120+k*230}px"></span>' for k in range(3))
bg=['tl.to("#glow",{x:120,y:30,scale:1.15,duration:6,yoyo:true,repeat:9,ease:"sine.inOut"},0);',
    'tl.to("#grid",{backgroundPosition:"0px 110px",duration:6,ease:"none",repeat:9},0);']
for k in range(NP):
    dur=4+(k%5)
    bg.append(f'tl.to("#pt{k}",{{y:-{120+(k%4)*60},duration:{dur},ease:"none",repeat:{int(60/dur)+1}}},0);')
    bg.append(f'tl.to("#pt{k}",{{opacity:0,duration:{dur},yoyo:true,repeat:{int(60/dur)+1},ease:"sine.inOut"}},0);')
for k in range(3):
    bg.append(f'tl.fromTo("#stk{k}",{{x:-1200}},{{x:1200,duration:{5+k*2},ease:"none",repeat:9}},{k*1.5});')

HTML=f'''<!doctype html><html lang="it"><head><meta charset="UTF-8"/>
<meta name="viewport" content="width=1080, height=1920"/>
<script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/MotionPathPlugin.min.js"></script>
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
html,body{{width:1080px;height:1920px;overflow:hidden;background:#000;font-family:"Montserrat","Inter",sans-serif}}
#root{{position:relative;width:1080px;height:1920px}}
#bgz{{position:absolute;top:0;left:0;width:1080px;height:864px;overflow:hidden}}
#grid{{position:absolute;inset:-40px;background-image:linear-gradient(rgba(47,224,129,0.05) 1px,transparent 1px),linear-gradient(90deg,rgba(47,224,129,0.05) 1px,transparent 1px);background-size:110px 110px}}
#glow{{position:absolute;top:120px;left:280px;width:520px;height:520px;border-radius:50%;background:radial-gradient(circle,rgba(47,224,129,0.26),transparent 65%);filter:blur(22px)}}
.pt{{position:absolute;border-radius:50%;background:{A};box-shadow:0 0 12px {A}}}
.stk{{position:absolute;left:0;width:520px;height:2px;background:linear-gradient(90deg,transparent,{A},transparent);opacity:0.3}}
.beat{{position:absolute;top:0;left:0;width:1080px;height:864px}}
.inner{{position:absolute;top:55px;left:64px;right:64px;height:680px;display:flex;flex-direction:column;justify-content:center;gap:24px}}
.innerfull{{position:absolute;top:0;left:0;width:1080px;height:864px}}
.eyebrow{{color:{A};font-size:30px;font-weight:800;letter-spacing:6px;text-transform:uppercase;display:flex;align-items:center;gap:13px}}
.eyebrow.red{{color:{RED}}}
.ebdot{{width:14px;height:14px;border-radius:50%;background:{A};box-shadow:0 0 14px {A}}}.ebdot.red{{background:{RED};box-shadow:0 0 14px {RED}}}
.kw{{color:#fff;font-size:112px;font-weight:900;line-height:0.98;letter-spacing:-1px;text-shadow:0 0 30px {GL}}}
.statrow{{display:flex;align-items:flex-end;gap:26px}}
.big{{color:#fff;font-size:200px;font-weight:900;line-height:0.85;letter-spacing:-3px;text-shadow:0 0 36px {GL}}}
.unit{{color:{A};font-size:36px;font-weight:900;text-transform:uppercase;line-height:1.1;padding-bottom:18px}}
.spark{{width:100%;height:210px}} .sparkbig{{width:100%;height:320px}}
.spark polyline,.sparkbig polyline{{fill:none;stroke-width:8;stroke-linecap:round;stroke-linejoin:round;stroke-dasharray:760;filter:drop-shadow(0 0 12px currentColor)}}
/* intro */
.introtxt{{position:absolute;top:120px;left:64px;z-index:2}}
.introeb{{color:{A};font-size:32px;font-weight:800;letter-spacing:10px}}
.introt1{{color:#fff;font-size:120px;font-weight:900;line-height:0.9;letter-spacing:-2px;text-shadow:0 0 36px {GL}}}
.introt2{{color:{A};font-size:64px;font-weight:900;letter-spacing:-1px}}
.flightsvg{{position:absolute;top:120px;left:60px;width:960px;height:620px}}
.plane{{position:absolute;top:0;left:0;font-size:84px;color:#fff;filter:drop-shadow(0 0 16px {A})}}
/* crm */
.crm{{display:flex;flex-direction:column;gap:13px}}
.crow{{display:flex;align-items:center;gap:18px;background:rgba(14,18,16,0.8);border:1px solid rgba(255,255,255,0.07);border-radius:16px;padding:18px 24px}}
.ava{{width:40px;height:40px;border-radius:50%;background:linear-gradient(135deg,#2a322d,#1a201d);border:1px solid {AD};flex:none}}
.cn{{color:#fff;font-size:31px;font-weight:800}} .cs{{color:#8b938e;font-size:27px;font-weight:600;flex:1}}
.cz{{color:{RED};font-size:22px;font-weight:800;letter-spacing:1px;border:1px solid {REDD};border-radius:18px;padding:5px 14px}}
/* list */
.lc{{display:flex;flex-direction:column;gap:16px}}
.lrow{{display:flex;align-items:center;gap:20px;background:rgba(14,18,16,0.8);border:1px solid {AD};border-radius:18px;padding:26px 32px;box-shadow:0 0 20px {GL}}}
.lck{{color:{A};font-size:40px;font-weight:900}} .lt{{color:#fff;font-size:40px;font-weight:800;text-transform:uppercase}}
/* calendar */
.calg{{display:grid;grid-template-columns:repeat(7,1fr);gap:12px;background:rgba(14,18,16,0.8);border:1px solid {AD};border-radius:22px;padding:30px;box-shadow:0 0 26px {GL}}}
.cal{{aspect-ratio:1;display:flex;align-items:center;justify-content:center;color:#6f776f;font-size:34px;font-weight:700;border-radius:12px}}
.cal.hot{{background:{A};color:#06140d;font-weight:900;box-shadow:0 0 22px {A}}}
/* comstep */
.comstep{{display:flex;flex-direction:column;gap:18px}}
.cmi.bad{{color:#f1b8c2;font-size:48px;font-weight:800;text-decoration:line-through;text-decoration-color:{RED};text-decoration-thickness:5px}}
.stamp{{align-self:flex-start;margin-top:10px;color:{RED};font-size:86px;font-weight:900;border:5px solid {RED};border-radius:18px;padding:6px 30px;text-transform:uppercase;box-shadow:0 0 30px {REDD}}}
/* iphone */
.iphwrap{{position:absolute;inset:0;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:18px;padding-top:30px}}
.iph{{height:700px;border-radius:36px;box-shadow:0 0 60px rgba(47,224,129,0.25)}}
.poweredby{{display:flex;align-items:center;gap:18px;color:#7f877f;font-size:22px;font-weight:800;letter-spacing:2px}}
.plogo{{height:34px;width:34px;object-fit:contain;filter:drop-shadow(0 0 6px rgba(255,255,255,0.15))}}
/* whatsapp chat */
.wahead{{display:flex;align-items:center;gap:16px;background:{WAIN};border-radius:18px 18px 0 0;padding:22px 26px}}
.walogo{{height:46px;width:46px}}
.waname{{color:#fff;font-size:34px;font-weight:800;display:flex;flex-direction:column;line-height:1.1}}
.waname span{{color:{WA};font-size:24px;font-weight:600}}
.wabody{{display:flex;flex-direction:column;gap:14px;background:#0b141a;border-radius:0 0 18px 18px;padding:26px 24px}}
.wabody.solo{{border-radius:18px}}
.wbub{{position:relative;max-width:84%;font-size:33px;font-weight:500;line-height:1.3;padding:20px 26px 30px;border-radius:16px;color:#e9edef}}
.wbub.in{{align-self:flex-start;background:{WAIN};border-top-left-radius:4px}}
.wbub.out{{align-self:flex-end;background:{WAB};border-top-right-radius:4px}}
.wt{{position:absolute;right:16px;bottom:8px;font-size:20px;color:#8696a0}}
.ph{{border-radius:8px;padding:2px 10px;font-weight:800}}
/* vflow */
.vflow{{display:flex;flex-direction:column;align-items:center;gap:12px}}
.vbox{{width:80%;display:flex;align-items:center;gap:22px;background:rgba(14,18,16,0.82);border:1px solid {AD};border-radius:20px;padding:24px 30px;box-shadow:0 0 22px {GL}}}
.vic{{font-size:54px;line-height:1}} .vt1{{color:#fff;font-size:38px;font-weight:900;text-transform:uppercase}} .vt2{{color:#aeb6b1;font-size:26px;font-weight:600}}
.vbox .vt1,.vbox .vt2{{display:block}}
.vbox>div{{display:flex;flex-direction:column}}
.varrow{{color:{A};font-size:50px;font-weight:900;line-height:0.6}}
/* cta */
.meter{{width:100%;height:28px;background:rgba(255,255,255,0.08);border-radius:14px;overflow:hidden;border:1px solid {AD}}}
.meter span{{display:block;height:100%;width:100%;transform-origin:left;transform:scaleX(0);background:linear-gradient(90deg,{A},#7af0b0);box-shadow:0 0 18px {A}}}
.inner.cta{{background:rgba(14,18,16,0.9);border:2px solid {A};border-radius:26px;padding:42px;box-shadow:0 0 46px {GL}}}
</style></head><body>
<div id="root" data-composition-id="main" data-start="0" data-duration="{TOTAL:.2f}" data-width="1080" data-height="1920">
  <div id="bgz" data-start="0" data-duration="{TOTAL:.2f}" data-track-index="0"><div id="grid"></div><div id="glow"></div>{streaks_html}{parts_html}</div>
  {"".join(clips)}
</div>
<script>gsap.registerPlugin(MotionPathPlugin);window.__timelines=window.__timelines||{{}};const tl=gsap.timeline({{paused:true}});
      {chr(10).join(bg)}
      {chr(10).join(tw)}
window.__timelines["main"]=tl;</script></body></html>'''
open("index.html","w").write(HTML)
print(f"v8: {len(BEATS)} beat")
for i,((trig,t,p),s,e) in enumerate(zip(BEATS,starts,ends)): print(f"  {s:5.2f}-{e:5.2f} {t:9s} {trig}")
