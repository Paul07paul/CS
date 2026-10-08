"""Generate index.html for the Chalet Le Sabot de Venus film from a shot list.

Every shot is a real photo of the chalet: only scale/translate (Ken Burns) and
crossfades are applied, never warping. Run:  python3 build.py
"""
import json

W, H = 1080, 1920
BAND_TOP, BAND_H = 470, 900  # photo band (6:5) — keeps the source photos sharp

# id, photo, start, dur, from{s,x,y}, to{s,x,y}, object-position, fade-in
SHOTS = [
    ("ext1", "03", 0.0, 5.2, (1.00, 0, 0), (1.10, 0, -14), "50% 55%", 0.0),
    ("living", "23", 4.6, 4.8, (1.06, 34, 0), (1.16, -30, -6), "45% 50%", 0.6),
    ("windows", "24", 8.8, 4.6, (1.04, -14, 4), (1.20, 26, -12), "55% 45%", 0.6),
    ("kitchen", "26", 12.8, 3.6, (1.05, 0, 0), (1.17, -44, 10), "55% 55%", 0.6),
    ("master", "12", 15.8, 3.2, (1.03, 0, 0), (1.10, -12, -4), "50% 55%", 0.6),
    ("bed2", "21", 18.6, 1.6, (1.04, 10, 0), (1.09, -10, 0), "50% 55%", 0.4),
    ("bunk", "17", 19.8, 1.6, (1.04, -10, 0), (1.09, 10, 0), "50% 55%", 0.4),
    ("bed3", "13", 21.0, 1.4, (1.04, 0, 0), (1.09, -10, -4), "40% 55%", 0.4),
    ("bath", "09", 22.0, 3.0, (1.04, 0, 0), (1.11, -16, -6), "40% 50%", 0.6),
    ("tub", "08", 24.6, 2.0, (1.04, 10, 0), (1.10, -8, 0), "45% 55%", 0.4),
    ("view", "28", 26.2, 5.0, (1.00, 0, 0), (1.30, -70, 50), "50% 45%", 0.6),
    # montage (short, slightly faster)
    ("m1", "01", 31.0, 0.75, (1.06, 0, 0), (1.12, 0, -8), "50% 55%", 0.15),
    ("m2", "27", 31.6, 0.75, (1.06, 10, 0), (1.12, -10, 0), "50% 50%", 0.15),
    ("m3", "10", 32.2, 0.75, (1.06, 0, 0), (1.12, -8, 0), "50% 55%", 0.15),
    ("m4", "25", 32.8, 0.75, (1.06, -8, 0), (1.12, 8, 0), "45% 55%", 0.15),
    ("m5", "22", 33.4, 0.75, (1.06, 0, 0), (1.12, 8, -6), "50% 50%", 0.15),
    ("m6", "24", 34.0, 0.75, (1.08, 0, 0), (1.15, 10, -8), "70% 40%", 0.15),
    ("m7", "02", 34.6, 0.9, (1.06, 0, 0), (1.12, 0, -8), "50% 55%", 0.15),
    # services backdrop
    ("serv", "05", 35.3, 4.9, (1.06, 0, 0), (1.12, 0, -8), "50% 50%", 0.6),
    # finale
    ("ext2", "02", 39.6, 5.4, (1.14, 0, -10), (1.00, 0, 0), "50% 55%", 0.8),
]
TOTAL = 47.5

# text cues: id, html, start, end, zone, class
TEXTS = [
    ("t-loc1", "COURCHEVEL MORIOND 1650", 0.8, 4.4, "top", "kicker"),
    ("t-name1", "Chalet Le Sabot de Vénus", 1.9, 4.4, "bottom", "title"),
    ("t-share", "Un chalet pensé pour partager", 5.4, 8.9, "bottom", "title"),
    ("t-light", "De grands espaces baignés de lumière", 9.4, 12.9, "bottom", "title"),
    ("t-rooms", "Salon <i>•</i> Cuisine <i>•</i> Salle à manger", 10.6, 12.9, "top", "kicker"),
    ("t-kitchen", "Une cuisine entièrement équipée", 13.4, 16.1, "bottom", "title"),
    ("t-sleep", "Des chambres pensées pour se ressourcer", 16.4, 20.2, "bottom", "title"),
    ("t-five", "Jusqu'à 5 chambres", 20.3, 22.2, "bottom", "title"),
    ("t-bath", "Confort &amp; bien-être", 22.6, 24.8, "bottom", "title"),
    ("t-tub", "Baignoire balnéothérapie dans la suite master", 25.0, 26.5, "bottom", "small"),
    ("t-view", "Une vue panoramique sur les montagnes", 27.0, 29.9, "bottom", "title"),
    ("t-loc2", "COURCHEVEL MORIOND", 29.6, 31.1, "top", "kicker"),
    ("t-family", "En famille ou entre amis", 31.3, 33.1, "bottom", "title"),
    ("t-season", "Hiver comme été", 33.3, 35.2, "bottom", "title"),
    ("t-name2", "Chalet Le Sabot de Vénus", 40.3, 44.9, "top", "title"),
    ("t-loc3", "COURCHEVEL MORIOND 1650", 40.9, 44.9, "top2", "kicker"),
    ("t-end", "Votre séjour à la montagne commence ici.", 41.7, 44.9, "bottom", "title"),
]

SERVICES = [
    ("Ski-room avec sèche-chaussures", "ski"),
    ("Parking privatif", "park"),
    ("Wi-Fi haut débit", "wifi"),
    ("Linge de maison fourni", "linen"),
    ("Entretien pendant le séjour", "clean"),
    ("Accès autonome", "key"),
]
ICONS = {
    "ski": '<path d="M8 40 L40 8 M14 44 L44 14" stroke-linecap="round"/><path d="M30 34 l8 8" stroke-linecap="round"/>',
    "park": '<rect x="9" y="7" width="30" height="34" rx="6"/><path d="M19 33 V16 h7 a6 6 0 0 1 0 12 h-7"/>',
    "wifi": '<path d="M6 19 a26 26 0 0 1 36 0 M12 26 a17 17 0 0 1 24 0 M18 33 a8 8 0 0 1 12 0" stroke-linecap="round"/><circle cx="24" cy="39" r="2.5" fill="currentColor"/>',
    "linen": '<path d="M8 14 h32 v8 h-32 z M10 22 v18 h28 v-18"/><path d="M16 30 h16" stroke-linecap="round"/>',
    "clean": '<path d="M24 6 l3 8 8 3 -8 3 -3 8 -3 -8 -8 -3 8 -3 z"/><path d="M36 30 l1.5 4 4 1.5 -4 1.5 -1.5 4 -1.5 -4 -4 -1.5 4 -1.5 z"/>',
    "key": '<circle cx="16" cy="24" r="8"/><path d="M24 24 h18 M36 24 v6 M41 24 v4" stroke-linecap="round"/>',
}
SERV_T0, SERV_STEP, SERV_END = 35.9, 0.42, 39.5

out = []
A = out.append
A(f"""<!doctype html>
<html lang="fr">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width={W}, height={H}" />
    <script src="assets/vendor/gsap.min.js"></script>
    <style>
      @font-face {{ font-family: "Cormorant Garamond"; font-style: normal; font-weight: 400 600; src: url("assets/fonts/cormorant.woff2") format("woff2"); }}
      @font-face {{ font-family: "Cormorant Garamond"; font-style: italic; font-weight: 400 600; src: url("assets/fonts/cormorant-italic.woff2") format("woff2"); }}
      @font-face {{ font-family: "Montserrat"; font-style: normal; font-weight: 100 900; src: url("assets/fonts/montserrat.woff2") format("woff2"); }}
      * {{ margin: 0; padding: 0; box-sizing: border-box; }}
      html, body {{ margin: 0; width: {W}px; height: {H}px; overflow: hidden; background: #0d0b09; }}
      #root {{ position: relative; width: 100%; height: 100%; overflow: hidden; background: #0d0b09; font-family: "Montserrat", sans-serif; }}
      .shot {{ position: absolute; inset: 0; }}
      .shot .fade {{ position: absolute; inset: 0; }}
      .shot .bg {{ position: absolute; inset: -40px; width: {W + 80}px; height: {H + 80}px; object-fit: cover; }}
      .shot .band {{ position: absolute; left: 0; top: {BAND_TOP}px; width: {W}px; height: {BAND_H}px; overflow: hidden;
        -webkit-mask-image: linear-gradient(180deg, transparent 0, #000 7%, #000 93%, transparent 100%);
        mask-image: linear-gradient(180deg, transparent 0, #000 7%, #000 93%, transparent 100%); }}
      .shot .band img {{ position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; }}
      .shot .vig {{ position: absolute; inset: 0; background: radial-gradient(ellipse at 50% 50%, rgba(0,0,0,0) 55%, rgba(0,0,0,0.32) 100%); }}
      #grade {{ position: absolute; inset: 0; background: linear-gradient(180deg, rgba(10,8,6,0.55) 0%, rgba(10,8,6,0) 22%, rgba(10,8,6,0) 74%, rgba(10,8,6,0.6) 100%); pointer-events: none; }}
      .txt {{ position: absolute; left: 60px; right: 60px; text-align: center; color: #FFFFFF; white-space: nowrap; }}
      .txt.top {{ top: 268px; }}
      .txt.top2 {{ top: 372px; }}
      .txt.bottom {{ top: 1420px; }}
      .txt.title {{ white-space: normal; font-family: "Cormorant Garamond", serif; font-weight: 500; font-size: 70px; line-height: 1.08; letter-spacing: 0.01em; text-shadow: 0 2px 24px rgba(0,0,0,0.35); }}
      .txt.title.top {{ top: 252px; font-size: 74px; }}
      .txt.small {{ white-space: normal; font-family: "Cormorant Garamond", serif; font-style: italic; font-weight: 500; font-size: 50px; }}
      .txt.kicker {{ font-weight: 500; font-size: 28px; letter-spacing: 0.42em; color: rgba(255,255,255,0.92); }}
      .txt.kicker i {{ font-style: normal; color: #D9B98A; padding: 0 6px; }}
      .rule {{ position: absolute; left: 490px; width: 100px; height: 2px; background: #D9B98A; transform-origin: 50% 50%; }}
      /* snow */
      .snow {{ position: absolute; inset: 0; pointer-events: none; }}
      .flake {{ position: absolute; border-radius: 50%; background: #FFFFFF; }}
      /* services */
      #serv-panel {{ position: absolute; left: 90px; right: 90px; top: 420px; height: 1080px; }}
      #serv-title {{ position: absolute; left: 0; right: 0; top: 0; text-align: center; font-family: "Cormorant Garamond", serif; font-weight: 500; font-size: 64px; color: #FFFFFF; }}
      #serv-kick {{ position: absolute; left: 0; right: 0; top: 96px; text-align: center; font-weight: 500; font-size: 24px; letter-spacing: 0.42em; color: #D9B98A; }}
      .serv {{ position: absolute; left: 40px; right: 40px; height: 120px; border-bottom: 1px solid rgba(255,255,255,0.22); }}
      .serv svg {{ position: absolute; left: 0; top: 34px; width: 52px; height: 52px; color: #D9B98A; fill: none; stroke: currentColor; stroke-width: 2.4; }}
      .serv span {{ position: absolute; left: 92px; top: 0; line-height: 120px; font-family: "Cormorant Garamond", serif; font-size: 48px; font-weight: 500; color: #FFFFFF; white-space: nowrap; }}
      /* booking card */
      #book {{ position: absolute; left: 80px; right: 80px; top: 760px; height: 380px; border-radius: 34px; background: rgba(255,255,255,0.96); box-shadow: 0 30px 80px rgba(0,0,0,0.45); }}
      #book .bt1 {{ position: absolute; left: 48px; top: 38px; font-family: "Cormorant Garamond", serif; font-weight: 600; font-size: 56px; color: #1B1612; white-space: nowrap; }}
      #book .bt2 {{ position: absolute; left: 48px; top: 112px; font-weight: 500; font-size: 24px; letter-spacing: 0.12em; color: #6B6259; white-space: nowrap; }}
      #book .dates {{ position: absolute; left: 48px; right: 48px; top: 172px; height: 72px; border-radius: 16px; border: 2px solid #E4DDD4; }}
      #book .dates span {{ position: absolute; top: 0; line-height: 68px; font-weight: 500; font-size: 26px; color: #6B6259; }}
      #book .btn {{ position: absolute; left: 48px; right: 48px; top: 268px; height: 80px; border-radius: 20px; background: #1B1612; color: #FFFFFF; text-align: center; font-weight: 600; font-size: 30px; letter-spacing: 0.08em; line-height: 80px; overflow: hidden; }}
      #book .ripple {{ position: absolute; left: 50%; top: 50%; width: 40px; height: 40px; margin: -20px 0 0 -20px; border-radius: 50%; background: rgba(217,185,138,0.55); }}
      #cursor {{ position: absolute; left: 0; top: 0; width: 44px; height: 44px; }}
      /* signature */
      #sig {{ position: absolute; inset: 0; background: #F4F1EC; }}
      #sig-by {{ position: absolute; left: 0; right: 0; top: 700px; text-align: center; font-weight: 500; font-size: 26px; letter-spacing: 0.36em; color: #6B7280; }}
      #sig-mark {{ position: absolute; left: 400px; top: 790px; width: 280px; height: 269px; }}
      #sig-mark img {{ position: absolute; left: 0; top: 0; width: 280px; height: 269px; }}
      #sig-word {{ position: absolute; left: 190px; top: 1110px; width: 700px; height: 144px; overflow: hidden; }}
      #sig-word img {{ position: absolute; left: 0; top: 0; width: 700px; height: 144px; }}
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-duration="{TOTAL}" data-width="{W}" data-height="{H}">
""")

for i, (sid, ph, st, du, f, t, pos, fi) in enumerate(SHOTS):
    A(f'''      <div id="{sid}" class="shot clip" data-start="{st}" data-duration="{du}" data-track-index="{1 + i % 2}"><div class="fade" id="{sid}-f">
        <img class="bg" src="assets/photos/bg/p{ph}.jpg" alt="" />
        <div class="band"><img id="{sid}-img" src="assets/photos/p{ph}.jpg" style="object-position:{pos}" alt="" /><div class="vig"></div></div>
      </div></div>''')

# snow layers over the exterior shots
def snow(sid, st, du, n=70, seed=3):
    flakes = []
    for k in range(n):
        x = (k * 157 + seed * 31) % W
        size = 3 + (k * 7 % 5) * 1.6
        op = 0.35 + (k * 13 % 7) / 14
        flakes.append(f'<div class="flake" data-k="{k}" style="left:{x}px;top:0;width:{size:.1f}px;height:{size:.1f}px;opacity:{op:.2f}"></div>')
    A(f'      <div id="{sid}" class="snow clip" data-start="{st}" data-duration="{du}" data-track-index="3">{"".join(flakes)}</div>')

snow("snow1", 0.0, 5.2)
snow("snow2", 39.6, 5.4, seed=9)

A('      <div id="grade" class="clip" data-start="0" data-duration="45" data-track-index="4"></div>')

# services panel
serv_rows = "".join(
    f'<div class="serv" id="sv{i}" style="top:{190 + i * 132}px"><svg viewBox="0 0 48 48">{ICONS[ic]}</svg><span>{name}</span></div>'
    for i, (name, ic) in enumerate(SERVICES)
)
A(f'''      <div id="serv-panel" class="clip" data-start="35.4" data-duration="4.4" data-track-index="5">
        <div id="serv-title">Tout est prévu</div><div id="serv-kick">SERVICES INCLUS</div>{serv_rows}
      </div>''')

for tid, html, s, e, zone, cls in TEXTS:
    A(f'      <div id="{tid}" class="txt {zone} {cls} clip" data-start="{s}" data-duration="{round(e - s, 2)}" data-track-index="6"><div class="in">{html}</div></div>')
A('      <div id="rule1" class="rule clip" style="top:350px" data-start="1.0" data-duration="3.4" data-track-index="7"></div>')
A('      <div id="rule2" class="rule clip" style="top:470px" data-start="41.0" data-duration="3.9" data-track-index="7"></div>')

A('''      <div id="book" class="clip" data-start="42.6" data-duration="2.4" data-track-index="8">
        <div class="bt1">Chalet Le Sabot de Vénus</div>
        <div class="bt2">COURCHEVEL MORIOND · JUSQU'À 5 CHAMBRES</div>
        <div class="dates"><span style="left:22px">Arrivée</span><span style="left:290px">Départ</span><span style="right:22px">Voyageurs</span></div>
        <div class="btn"><div class="ripple"></div><span>Réserver</span></div>
        <svg id="cursor" viewBox="0 0 44 44"><path d="M8 4 L8 36 L16 28 L22 40 L27 38 L21 26 L32 26 Z" fill="#FFFFFF" stroke="#1B1612" stroke-width="2.5" stroke-linejoin="round"/></svg>
      </div>''')

A('''      <div id="sig" class="clip" data-start="44.9" data-duration="2.6" data-track-index="9">
        <div id="sig-by">VIDÉO RÉALISÉE PAR</div>
        <div id="sig-mark"><img id="sig-d" src="assets/logo/mark-d.png" alt="" /><img id="sig-a" src="assets/logo/mark-arrow.png" alt="" /></div>
        <div id="sig-word"><img id="sig-wp" src="assets/logo/word-paul.png" alt="Paul" /><img id="sig-wd" src="assets/logo/word-digital.png" alt="Digital" /></div>
      </div>''')

A('''      <audio id="music" src="assets/audio/music.wav" data-start="0" data-duration="%s" data-track-index="10" data-volume="0.8"></audio>
      <audio id="sfx" src="assets/audio/sfx.wav" data-start="0" data-duration="%s" data-track-index="11" data-volume="1"></audio>
    </div>''' % (TOTAL, TOTAL))

js = f"""
    <script>
      const SHOTS = {json.dumps(SHOTS)};
      const TEXTS = {json.dumps(TEXTS)};
      const tl = gsap.timeline({{ paused: true }});
      // shots: crossfade in, slow Ken Burns across the whole clip (scale/translate only)
      SHOTS.forEach(([id, ph, st, du, f, t, pos, fi]) => {{
        if (fi > 0) tl.fromTo("#" + id + "-f", {{ opacity: 0 }}, {{ opacity: 1, duration: fi, ease: "sine.inOut" }}, st);
        tl.fromTo("#" + id + "-img", {{ scale: f[0], x: f[1], y: f[2] }}, {{ scale: t[0], x: t[1], y: t[2], duration: du, ease: id === "view" ? "power1.inOut" : "none" }}, st);
        tl.fromTo("#" + id + " .bg", {{ scale: 1.05 }}, {{ scale: 1.12, duration: du, ease: "none" }}, st);
      }});
      // text: soft blur-rise in, soft fade out
      TEXTS.forEach(([id, html, s, e]) => {{
        const el = "#" + id + " .in";
        tl.fromTo(el, {{ opacity: 0, y: 18, filter: "blur(8px)" }}, {{ opacity: 1, y: 0, filter: "blur(0px)", duration: 0.9, ease: "power2.out" }}, s);
        tl.to(el, {{ opacity: 0, y: -8, filter: "blur(6px)", duration: 0.55, ease: "power1.in" }}, e - 0.55);
      }});
      tl.fromTo("#rule1", {{ scaleX: 0, opacity: 1 }}, {{ scaleX: 1, duration: 1.0, ease: "power2.out" }}, 1.0);
      tl.to("#rule1", {{ opacity: 0, duration: 0.5 }}, 3.9);
      tl.fromTo("#rule2", {{ scaleX: 0, opacity: 1 }}, {{ scaleX: 1, duration: 1.0, ease: "power2.out" }}, 41.0);
      // snow: each flake falls with its own speed and sway (deterministic, finite repeats)
      document.querySelectorAll(".snow").forEach((layer) => {{
        const st = parseFloat(layer.dataset.start), du = parseFloat(layer.dataset.duration);
        layer.querySelectorAll(".flake").forEach((fl) => {{
          const k = +fl.dataset.k;
          const fall = 4.5 + (k * 37 % 30) / 10;
          const y0 = -60 - (k * 89 % 1900);
          tl.fromTo(fl, {{ y: y0 }}, {{ y: y0 + (2000 / fall) * du, duration: du, ease: "none" }}, st);
          tl.fromTo(fl, {{ x: -14 }}, {{ x: 14, duration: 1.6 + (k % 5) * 0.3, ease: "sine.inOut", yoyo: true, repeat: Math.ceil(du / 1.6) }}, st);
        }});
        tl.fromTo(layer, {{ opacity: 0 }}, {{ opacity: 1, duration: 0.8 }}, st);
      }});
      // services: lines appear one by one
      tl.fromTo("#serv-title", {{ opacity: 0, y: 20 }}, {{ opacity: 1, y: 0, duration: 0.8, ease: "power2.out" }}, 35.5);
      tl.fromTo("#serv-kick", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.8, ease: "power2.out" }}, 35.7);
      {json.dumps([f"sv{i}" for i in range(len(SERVICES))])}.forEach((id, i) => {{
        const at = {SERV_T0} + i * {SERV_STEP};
        tl.fromTo("#" + id + " svg", {{ opacity: 0, scale: 0.6 }}, {{ opacity: 1, scale: 1, duration: 0.5, ease: "back.out(1.6)" }}, at);
        tl.fromTo("#" + id + " span", {{ opacity: 0, x: 24 }}, {{ opacity: 1, x: 0, duration: 0.6, ease: "power2.out" }}, at + 0.05);
        tl.fromTo("#" + id, {{ borderBottomColor: "rgba(255,255,255,0)" }}, {{ borderBottomColor: "rgba(255,255,255,0.22)", duration: 0.6 }}, at);
      }});
      tl.to("#serv-panel", {{ opacity: 0, duration: 0.5 }}, {SERV_END - 0.2});
      tl.to("#serv-f", {{ opacity: 0.42, duration: 0.6, ease: "sine.inOut" }}, 35.9);
      // booking card
      tl.fromTo("#book", {{ opacity: 0, y: 120 }}, {{ opacity: 1, y: 0, duration: 0.7, ease: "power3.out" }}, 42.6);
      tl.fromTo("#cursor", {{ x: 760, y: 360, opacity: 0 }}, {{ x: 470, y: 296, opacity: 1, duration: 0.7, ease: "power2.inOut" }}, 43.1);
      tl.fromTo("#book .btn", {{ scale: 1 }}, {{ scale: 0.96, duration: 0.12, ease: "power2.out", yoyo: true, repeat: 1 }}, 43.85);
      tl.fromTo("#book .ripple", {{ scale: 0, opacity: 1 }}, {{ scale: 22, opacity: 0, duration: 0.8, ease: "power2.out" }}, 43.9);
      tl.to("#book", {{ opacity: 0, y: -30, duration: 0.4, ease: "power1.in" }}, 44.6);
      // signature: Paul Digital logo
      tl.fromTo("#sig", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.5, ease: "sine.inOut" }}, 44.9);
      tl.fromTo("#sig-by", {{ opacity: 0, y: 12 }}, {{ opacity: 1, y: 0, duration: 0.6, ease: "power2.out" }}, 45.2);
      tl.fromTo("#sig-d", {{ clipPath: "inset(0% 100% 0% 0%)" }}, {{ clipPath: "inset(0% 0% 0% 0%)", duration: 0.7, ease: "expo.out" }}, 45.3);
      tl.fromTo("#sig-a", {{ x: -90, y: 90, opacity: 0 }}, {{ x: 0, y: 0, opacity: 1, duration: 0.6, ease: "back.out(1.6)" }}, 45.45);
      tl.fromTo("#sig-wp", {{ y: 150 }}, {{ y: 0, duration: 0.6, ease: "power4.out" }}, 45.6);
      tl.fromTo("#sig-wd", {{ y: 150 }}, {{ y: 0, duration: 0.6, ease: "power4.out" }}, 45.75);
      tl.fromTo("#sig-mark", {{ scale: 1 }}, {{ scale: 1.03, duration: 1.4, ease: "sine.inOut" }}, 46.1);
      window.__timelines["main"] = tl;
    </script>
  </body>
</html>
"""
A(js)
open("index.html", "w").write("\n".join(out))
print("index.html written:", len(SHOTS), "shots,", len(TEXTS), "texts, total", TOTAL, "s")
