# Card snippets (copy-paste code)

The REAL code of the new animated building blocks, ready to paste into `gen.py`. Each card has 3 parts:
**inner()** (HTML), **CSS**, **JS GSAP** (anchor the times to `find(word)` / `find_after(word, after)`).
Color tokens at the top of gen.py: `A` accent (#2fe081), `AD` (border .45), `GL` (glow .16), `RED`, `REDD`, `GREY`.

---

## TERMINAL that TYPES (typewriter) — messy → XML
The critical part: it types with a tween on a counter + `textContent=val.slice(0,n)`. **NEVER TextPlugin**
(it writes into innerHTML → eats the `<role>` tags). `textContent` shows `<` `>` literally.

**inner()**
```python
if t=="terminal":
    return (f'<div class="numbadge sm" id="nb{i}">{esc(p["num"])}</div>'
            f'<div class="skname sm" id="sk{i}">{esc(p["name"])}</div>'
            f'<div class="term"><div class="tbar"><span class="td r"></span><span class="td y"></span><span class="td g"></span><span class="ttitle">claude</span></div>'
            f'<div class="tbody">'
            f'<div class="tbad" id="tb{i}"><span class="tlabel bad">CONFUSO</span><div class="tline grey"><span id="tbx{i}"></span><span class="cur">▋</span></div></div>'
            f'<div class="tgood" id="tg{i}"><span class="tlabel good">PERFETTO</span><div class="tline acc"><span id="tgx{i}"></span><span class="cur">▋</span></div></div>'
            f'</div></div>')
# in BEATS: {"num":"03","name":"PROMPT MASTER","confword":"richieste","perfword":"perfetto"}
# at the top of the file: CONF="write me an email for a client"
#   PERF="> claude\\n  <role> copywriter B2B </role>\\n  <goal> follow-up email </goal>\\n  <tone> direct, pro </tone>"
```
**CSS**
```css
.term{margin-top:4px;background:#0c0f0e;border:2px solid {AD};border-radius:20px;overflow:hidden;box-shadow:0 0 40px {GL}}
.tbar{display:flex;align-items:center;gap:12px;background:#161b19;padding:16px 22px;border-bottom:1px solid rgba(255,255,255,0.06)}
.td{width:18px;height:18px;border-radius:50%}.td.r{background:#ff5f57}.td.y{background:#febc2e}.td.g{background:#28c840}
.ttitle{color:#7f877f;font-size:26px;font-weight:700;margin-left:10px;font-family:ui-monospace,"SF Mono",Menlo,monospace}
.tbody{padding:26px 28px;min-height:240px;font-family:ui-monospace,"SF Mono",Menlo,Consolas,monospace}
.tlabel{display:inline-block;font-size:24px;font-weight:900;letter-spacing:3px;border-radius:8px;padding:5px 14px;margin-bottom:14px;font-family:"Montserrat",sans-serif}
.tlabel.bad{color:{RED};border:2px solid {REDD}}.tlabel.good{color:#06140d;background:{A}}
.tline{color:#e7efe9;font-size:36px;line-height:1.5;font-weight:600;white-space:pre-wrap;word-break:break-word}
.tline.grey{color:{GREY}}.tline.acc{color:{A}}
.cur{color:{A};animation:blink 1s steps(1) infinite}@keyframes blink{50%{opacity:0}}
```
**JS** (cf=find(confword), pf=find(perfword))
```python
js.append(f'tl.fromTo("#tb{i}",{{opacity:0,y:14}},{{opacity:1,y:0,duration:0.22,ease:"power3.out"}},{cf-0.1:.2f});')
js.append(f'var cv{i}="{CONF}";tl.to({{n:0}},{{n:cv{i}.length,duration:0.95,ease:"none",onUpdate:function(){{document.getElementById("tbx{i}").textContent=cv{i}.slice(0,Math.round(this.targets()[0].n));}}}},{cf:.2f});')
js.append(f'tl.to("#tb{i}",{{opacity:0,height:0,marginBottom:0,duration:0.2,ease:"power2.in"}},{pf-0.02:.2f});')
js.append(f'tl.fromTo("#tg{i}",{{opacity:0}},{{opacity:1,duration:0.2}},{pf:.2f});')
js.append(f'var pv{i}="{PERF}";tl.to({{n:0}},{{n:pv{i}.length,duration:1.5,ease:"none",onUpdate:function(){{document.getElementById("tgx{i}").textContent=pv{i}.slice(0,Math.round(this.targets()[0].n));}}}},{pf+0.1:.2f});')
```

---

## Per-word PILL + result (Humanizer: output/text/email → human)
One pill per word that enters on that word's `find()`; then the pills fade and the result appears.

**inner()**
```python
if t=="humanizer":
    pills="".join(f'<span class="hpill" id="b{i}w{j}">{em} {esc(lbl)}</span>' for j,(em,lbl,_) in enumerate(p["words"]))
    return (f'<div class="numbadge" id="nb{i}">{esc(p["num"])}</div><div class="skname" id="sk{i}">{esc(p["name"])}</div>'
            f'<div class="hpills" id="hp{i}">{pills}</div><div class="swaparr" id="ha{i}">↓</div>'
            f'<div class="hres" id="hr{i}">{esc(p["result"])}</div>')
# words=[("📄","OUTPUT","output"),("✍🏻","TESTO","testo"),("📧","EMAIL","email")], fixword="riscrive", result="COME LO SCRIVI TU"
```
**CSS**
```css
.inner.humanizer{align-items:flex-start}
.hpills{display:flex;flex-wrap:wrap;gap:16px;margin-top:6px}
.hpill{color:{GREY};font-size:44px;font-weight:800;text-transform:uppercase;border:2px solid rgba(255,255,255,0.1);border-radius:18px;padding:14px 26px;background:rgba(40,44,42,0.7)}
.hres{color:#06140d;font-size:58px;font-weight:900;text-transform:uppercase;background:{A};border-radius:18px;padding:18px 34px;align-self:center;box-shadow:0 0 34px {A}}
.swaparr{color:{A};font-size:56px;font-weight:900;line-height:0.5;align-self:center}
```
**JS**
```python
for j,(_,_,wd) in enumerate(p["words"]): js.append(f'tl.fromTo("#b{i}w{j}",{{opacity:0,y:18,scale:0.85}},{{opacity:1,y:0,scale:1,duration:0.26,ease:"back.out(1.9)"}},{find(wd):.2f});')
js.append(f'tl.to("#hp{i}",{{opacity:0.3,duration:0.3}},{find(p["fixword"]):.2f});')
js.append(f'tl.fromTo("#ha{i}",{{opacity:0}},{{opacity:1,duration:0.2}},{find(p["fixword"])-0.1:.2f});')
js.append(f'tl.fromTo("#hr{i}",{{opacity:0,y:18,scale:0.9}},{{opacity:1,y:0,scale:1,duration:0.32,ease:"back.out(1.9)"}},{find(p["fixword"]):.2f});')
```

---

## Staged HOOK with big LOGO (text → logo → stamp)
Stage1 text that pops and exits; stage2 big logo that enters; stage3 stamp. Each stage on a DIFFERENT word.

**inner()**
```python
if t=="hook":
    return (f'<div class="hookwrap">'
            f'<div class="hooks1" id="h1{i}"><div class="hooktop">QUESTE</div><div class="hookbig">4 SKILL</div></div>'
            f'<img src="assets/logos/claude.svg" class="clogobig" id="h2{i}"/>'
            f'<div class="stamp" id="h3{i}">ILLEGALE</div></div>')
# {"quatword":"quattro","claudeword":"rendono Claude","stampword":"illegale"}
```
**CSS**
```css
.inner.hook{align-items:center;justify-content:center}
.hookwrap{position:relative;width:100%;height:100%;display:flex;flex-direction:column;align-items:center;justify-content:center}
.hooks1{position:absolute;display:flex;flex-direction:column;align-items:center;gap:6px}
.hooktop{color:{A};font-size:44px;font-weight:800;letter-spacing:10px}
.hookbig{color:#fff;font-size:200px;font-weight:900;line-height:0.82;letter-spacing:-4px;text-shadow:0 0 40px {GL}}
.clogobig{height:360px;width:360px;object-fit:contain;margin-bottom:28px;filter:drop-shadow(0 0 40px rgba(217,119,87,0.55))}
.stamp{color:{RED};font-size:118px;font-weight:900;border:7px solid {RED};border-radius:20px;padding:6px 40px;text-transform:uppercase;box-shadow:0 0 38px {REDD};text-shadow:0 0 26px {REDD}}
```
**JS** (cl=find(claudeword))
```python
js.append(f'tl.fromTo("#h1{i}",{{opacity:0,scale:1.4}},{{opacity:1,scale:1,duration:0.3,ease:"back.out(2)"}},{find(p["quatword"]):.2f});')
js.append(f'tl.to("#h1{i}",{{opacity:0,scale:0.85,duration:0.22,ease:"power2.in"}},{cl:.2f});')
js.append(f'tl.fromTo("#h2{i}",{{opacity:0,scale:0.4,rotate:-30}},{{opacity:1,scale:1,rotate:0,duration:0.5,ease:"back.out(1.7)"}},{cl+0.04:.2f});')
js.append(f'tl.fromTo("#h3{i}",{{opacity:0,scale:1.8,rotate:-10}},{{opacity:1,scale:1,rotate:-7,duration:0.3,ease:"back.out(2)"}},{find(p["stampword"]):.2f});')
```

---

## Numbered BLOCKS 1-2-3-4 (the "cards")
Green boxes that enter staggered. **ANCHOR with `find_after`** if the anchor word occurs earlier (hook).

**inner()**
```python
if t=="count":
    blk="".join(f'<span class="cblk" id="b{i}k{j}"><b>{j+1}</b></span>' for j in range(4))
    return (f'{eb(p["eyebrow"])}<div class="statrow ctr"><div class="big" id="big{i}">0</div><div class="unit">{esc(p["unit"])}</div></div>'
            f'<div class="cblocks" id="cb{i}">{blk}</div>')   # blkanchor:"queste quattro"
```
**CSS**
```css
.inner.count{align-items:center;text-align:center}
.statrow.ctr{justify-content:center}
.cblocks{display:flex;gap:22px;justify-content:center;margin-top:14px}
.cblk{width:150px;height:180px;border-radius:24px;background:{A};box-shadow:0 0 30px {A};display:flex;align-items:center;justify-content:center}
.cblk b{color:#06140d;font-size:80px;font-weight:900}
```
**JS**
```python
blk0=find_after(p["blkanchor"],s)
for j in range(4): js.append(f'tl.fromTo("#b{i}k{j}",{{opacity:0,y:24,scale:0.6}},{{opacity:1,y:0,scale:1,duration:0.26,ease:"back.out(2)"}},{blk0+j*0.2:.2f});')
```

---

## Before/after SWAP (grey struck-through line → green line)
**inner()**: `<div class="swaprow bad">X 🤖</div><div class="swaparr">↓</div><div class="swaprow good">Y ✅</div>`
**CSS**
```css
.swaprow{font-size:60px;font-weight:900;text-transform:uppercase;border-radius:20px;padding:24px 32px;letter-spacing:-1px}
.swaprow.bad{color:{GREY};background:rgba(40,44,42,0.7);border:2px solid rgba(255,255,255,0.08);text-decoration:line-through;text-decoration-color:{RED};text-decoration-thickness:5px}
.swaprow.good{color:#06140d;background:{A};box-shadow:0 0 34px {A}}
```
**JS**: bad enters on `aiword`, arrow + good enter on `fixword`.

---

## SKILLTITLE (number badge + name + chip) · BIGSTAT pop · CTA colored word
**SKILLTITLE** — badge `01` + big name + optional chips (for Find Skills pass `chips:[]` = no chip).
```css
.numbadge{width:118px;height:118px;border-radius:26px;background:{A};color:#06140d;font-size:64px;font-weight:900;display:flex;align-items:center;justify-content:center;box-shadow:0 0 36px {A}}
.numbadge.sm{width:88px;height:88px;font-size:48px;border-radius:20px}
.skname{color:#fff;font-size:104px;font-weight:900;line-height:0.95;letter-spacing:-2px;text-shadow:0 0 30px {GL}}.skname.sm{font-size:72px}
.chip{color:{A};font-size:40px;font-weight:800;text-transform:uppercase;border:2px solid {AD};border-radius:40px;padding:12px 28px;background:rgba(14,18,16,0.7);box-shadow:0 0 18px {GL}}
```
**BIGSTAT pop** (number that does NOT count, it pops — for beats <1.2s). `num=f'{count:,}'.replace(",",".")+"+"` → "91.000+".
```python
js.append(f'tl.fromTo("#big{i}",{{opacity:0,scale:1.45}},{{opacity:1,scale:1,duration:0.34,ease:"back.out(2.2)"}},{max(s+0.02,cw-0.12):.2f});')
```
**CTA colored word**: `<div class="kw">COMMENTA: <span class="acc">SKILL</span></div>` with `.kw .acc{color:{A};text-shadow:0 0 26px {A}}`.
