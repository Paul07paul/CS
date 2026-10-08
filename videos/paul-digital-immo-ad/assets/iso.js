/* Paul Digital — CSS 3D isometric toolkit (orthographic, deterministic).
   World = plane in X/Y with Z up. Camera = 2D pan/zoom wrapper + 3D tilt/orbit on the world.
   Everything is static DOM; GSAP drives the camera through getter/setter methods so
   every seek re-applies the exact state. */
(function () {
  function hexToRgb(h) {
    h = h.replace("#", "");
    return [0, 2, 4].map((i) => parseInt(h.substr(i, 2), 16));
  }
  function shade(hex, f) {
    if (!hex || hex[0] !== "#") return hex;
    const [r, g, b] = hexToRgb(hex).map((c) => Math.max(0, Math.min(255, Math.round(c * f))));
    return `rgb(${r},${g},${b})`;
  }

  function face(parent, cls, css, color) {
    const f = document.createElement("div");
    f.className = "iso-face " + cls;
    f.style.cssText = "position:absolute;" + css + ";background:" + color + ";";
    parent.appendChild(f);
    return f;
  }

  /* box(parent, x, y, z, w, d, h, opts)
     opts: color (top), sides (base side colour), top, s, e, n, w, cls, radius, id, opacity, noBottom */
  function box(parent, x, y, z, w, d, h, o) {
    o = o || {};
    const base = o.color || "#cccccc";
    const side = o.sides || base;
    const el = document.createElement("div");
    el.className = "iso-box " + (o.cls || "");
    if (o.id) el.id = o.id;
    el.style.cssText = `position:absolute;left:${x}px;top:${y}px;width:${w}px;height:${d}px;transform-style:preserve-3d;`;
    // faces live in an inner wrapper so a "cutaway" can scale the height without touching GSAP's z
    const inner = document.createElement("div");
    inner.className = "iso-inner";
    inner.style.cssText = "position:absolute;left:0;top:0;width:100%;height:100%;transform-style:preserve-3d;transform-origin:50% 50% 0;";
    el.appendChild(inner);
    el._inner = inner;
    const op = o.opacity != null ? `opacity:${o.opacity};` : "";
    const rad = o.radius ? `border-radius:${o.radius}px;` : "";
    const top = face(inner, "top", `left:0;top:0;width:${w}px;height:${d}px;transform:translateZ(${h}px);${op}${rad}`, o.top || base);
    if (h > 0.5) {
      face(inner, "s", `left:0;top:${d}px;width:${w}px;height:${h}px;transform-origin:top;transform:rotateX(90deg);${op}`, o.s || shade(side, 0.86));
      face(inner, "e", `left:${w}px;top:0;width:${h}px;height:${d}px;transform-origin:left;transform:rotateY(-90deg);${op}`, o.e || shade(side, 0.7));
      face(inner, "n", `left:0;top:${-h}px;width:${w}px;height:${h}px;transform-origin:bottom;transform:rotateX(-90deg);${op}`, o.n || shade(side, 0.62));
      face(inner, "w", `left:${-h}px;top:0;width:${h}px;height:${d}px;transform-origin:right;transform:rotateY(90deg);${op}`, o.w || shade(side, 0.78));
    }
    el._top = top;
    parent.appendChild(el);
    gsap.set(el, { z: z });
    el._z = z;
    return el;
  }

  /* A billboard = a point in the world whose content always faces the camera. */
  function billboard(parent, x, y, z, html, cls) {
    const el = document.createElement("div");
    el.className = "iso-bb " + (cls || "");
    el.style.cssText = `position:absolute;left:${x}px;top:${y}px;width:0;height:0;transform-style:preserve-3d;`;
    el.innerHTML = html;
    el._z = z;
    parent.appendChild(el);
    return el;
  }

  /* Camera rig. root: positioned container; returns { cam, world, plane, api } */
  function rig(root, size, center) {
    const cam = document.createElement("div");
    cam.className = "iso-cam";
    cam.style.cssText = `position:absolute;left:${center[0]}px;top:${center[1]}px;width:0;height:0;transform-style:preserve-3d;`;
    const world = document.createElement("div");
    world.className = "iso-world";
    world.style.cssText = "position:absolute;left:0;top:0;width:0;height:0;transform-style:preserve-3d;";
    const plane = document.createElement("div");
    plane.className = "iso-plane";
    plane.style.cssText = `position:absolute;left:${-size / 2}px;top:${-size / 2}px;width:${size}px;height:${size}px;transform-style:preserve-3d;`;
    world.appendChild(plane);
    cam.appendChild(world);
    root.appendChild(cam);

    // tx/ty/tz = world point (plane px, plane centre = 0,0) kept at screen offset ox/oy.
    const s = { rx: 60, rz: 45, zoom: 1, tx: 0, ty: 0, tz: 0, ox: 0, oy: 0 };
    const bbs = [];
    const R = Math.PI / 180;
    function project(x, y, z) {
      const a = s.rz * R, b = s.rx * R;
      const x1 = x * Math.cos(a) - y * Math.sin(a);
      const y1 = x * Math.sin(a) + y * Math.cos(a);
      return [x1, y1 * Math.cos(b) - z * Math.sin(b)];
    }
    function apply() {
      const p = project(s.tx, s.ty, s.tz);
      const px = s.ox - s.zoom * p[0], py = s.oy - s.zoom * p[1];
      cam.style.transform = `translate(${px}px,${py}px) scale(${s.zoom})`;
      world.style.transform = `rotateX(${s.rx}deg) rotateZ(${s.rz}deg)`;
      const inv = 1 / s.zoom;
      for (const b of bbs) {
        b.style.transform = `translateZ(${b._z}px) rotateZ(${-s.rz}deg) rotateX(${-s.rx}deg) scale(${inv})`;
      }
    }
    const api = {};
    ["rx", "rz", "zoom", "tx", "ty", "tz", "ox", "oy"].forEach((k) => {
      api[k] = function (v) {
        if (v === undefined) return s[k];
        s[k] = v;
        apply();
      };
    });
    api.set = function (o) {
      Object.assign(s, o);
      apply();
    };
    api.project = project;
    api.addBillboard = function (b) {
      bbs.push(b);
      apply();
    };
    apply();
    return { cam, world, plane, api, state: s };
  }

  /* ---------- The villa ---------- */
  const C = {
    plinthTop: "#E4DCCD",
    plinthSide: "#22324A",
    lawn: "#9CBC86",
    hedge: "#6F9663",
    wall: "#F5F0E8",
    slab: "#E9E1D3",
    floor: "#E7D9C3",
    roof: "#2C3848",
    fascia: "#D6A55A",
    glass: "rgba(150,205,220,0.42)",
    wood: "#B9875A",
    coping: "#F1EBE0",
    water: "#5FB3B3",
    sofa: "#7F90A6",
    oak: "#A9784D",
    linen: "#EFE9DF",
    gold: "#D6A55A",
    ink: "#0E1624",
  };

  function villa(plane) {
    const g = { plinth: [], ground: [], floor: [], walls: [], glass: [], roof: [], furniture: {}, pool: [], deck: [], trees: [], glows: {} };
    const add = (arr, el) => (arr.push(el), el);
    const fur = (room, el) => ((g.furniture[room] = g.furniture[room] || []).push(el), el);

    // Floating plinth
    add(g.plinth, box(plane, 0, 0, -70, 800, 800, 70, { color: C.plinthTop, sides: C.plinthSide, cls: "plinth" }));
    // Lawn + hedges + path
    add(g.ground, box(plane, 24, 24, 0, 752, 752, 4, { color: C.lawn }));
    add(g.ground, box(plane, 24, 24, 4, 752, 18, 22, { color: C.hedge }));
    add(g.ground, box(plane, 24, 42, 4, 18, 734, 22, { color: C.hedge }));
    add(g.ground, box(plane, 40, 280, 4, 100, 70, 3, { color: "#EEE7DB" }));
    add(g.ground, box(plane, 60, 640, 4, 70, 110, 3, { color: "#EEE7DB" }));

    // Floor slabs
    add(g.floor, box(plane, 140, 120, 4, 400, 260, 10, { color: C.slab }));
    add(g.floor, box(plane, 140, 380, 4, 240, 230, 10, { color: C.slab }));
    // interior floor tint + room glows
    ["kitchen:150,130,180,240", "salon:340,130,190,240", "bedroom:150,390,220,210"].forEach((spec) => {
      const [name, r] = spec.split(":");
      const [x, y, w, d] = r.split(",").map(Number);
      add(g.floor, box(plane, x, y, 14, w, d, 0.1, { color: C.floor }));
      const glow = box(plane, x, y, 14.5, w, d, 0.1, {
        color: "radial-gradient(ellipse at 50% 50%, rgba(255,214,150,0.95), rgba(255,190,110,0.35) 55%, rgba(255,190,110,0) 80%)",
        cls: "room-glow",
      });
      glow._top.style.opacity = "0";
      g.glows[name] = glow._top;
    });

    // Walls (z from 14, height 128)
    const WZ = 14,
      WH = 128;
    const wall = (x, y, w, d) => add(g.walls, box(plane, x, y, WZ, w, d, WH, { color: C.wall }));
    const glass = (x, y, w, d) => add(g.glass, box(plane, x, y, WZ, w, d, WH, { color: C.glass, cls: "glass" }));
    wall(140, 120, 400, 10); // north
    wall(140, 130, 10, 470); // west
    wall(330, 130, 10, 140); // kitchen/salon partition
    wall(150, 370, 150, 10); // main / bedroom
    wall(340, 370, 40, 10);
    // main wing east: glass with posts
    wall(530, 130, 10, 14);
    glass(533, 144, 4, 212);
    wall(530, 356, 10, 24);
    // main wing south (over terrace): posts + glass
    wall(380, 370, 14, 10);
    glass(394, 373, 136, 4);
    // bedroom wing
    wall(370, 380, 10, 60);
    glass(373, 440, 4, 100);
    wall(370, 540, 10, 70);
    wall(150, 600, 80, 10);
    glass(230, 603, 90, 4);
    wall(320, 600, 60, 10);

    // Roof slabs with gold fascia
    add(g.roof, box(plane, 122, 102, WZ + WH, 436, 296, 16, { color: C.roof, sides: C.fascia, s: C.fascia, e: "#B98A45", n: "#9C7439", w: "#C29350" }));
    add(g.roof, box(plane, 122, 398, WZ + WH, 276, 230, 16, { color: C.roof, sides: C.fascia, s: C.fascia, e: "#B98A45", n: "#9C7439", w: "#C29350" }));
    // roof-top planter / solar strip detail
    add(g.roof, box(plane, 160, 140, WZ + WH + 16, 120, 60, 10, { color: C.hedge }));

    // Furniture — kitchen
    fur("kitchen", box(plane, 152, 132, 14, 170, 28, 42, { color: "#F0E9DD", sides: "#C9BCA6" }));
    fur("kitchen", box(plane, 190, 215, 14, 100, 42, 40, { color: C.linen, sides: C.oak }));
    fur("kitchen", box(plane, 180, 300, 14, 110, 50, 30, { color: C.oak }));
    [185, 225, 265].forEach((x) => fur("kitchen", box(plane, x, 290, 14, 18, 10, 22, { color: C.ink })));
    [185, 225, 265].forEach((x) => fur("kitchen", box(plane, x, 352, 14, 18, 10, 22, { color: C.ink })));
    // salon
    fur("salon", box(plane, 360, 170, 14, 150, 130, 1, { color: "#CDBB9F" }));
    fur("salon", box(plane, 360, 150, 14, 130, 30, 28, { color: C.sofa }));
    fur("salon", box(plane, 360, 180, 14, 32, 90, 28, { color: C.sofa }));
    fur("salon", box(plane, 420, 215, 14, 56, 44, 14, { color: C.oak }));
    fur("salon", box(plane, 500, 300, 14, 20, 20, 30, { color: "#E3D6C2" }));
    fur("salon", box(plane, 495, 295, 44, 30, 30, 26, { color: C.hedge, radius: 15 }));
    // bedroom
    fur("bedroom", box(plane, 180, 395, 14, 120, 12, 48, { color: "#8B6A4A" }));
    fur("bedroom", box(plane, 180, 407, 14, 120, 140, 24, { color: C.linen }));
    fur("bedroom", box(plane, 190, 412, 38, 46, 24, 8, { color: "#FFFFFF" }));
    fur("bedroom", box(plane, 244, 412, 38, 46, 24, 8, { color: "#FFFFFF" }));
    fur("bedroom", box(plane, 182, 470, 38, 116, 76, 3, { color: C.gold }));
    fur("bedroom", box(plane, 152, 400, 14, 24, 24, 22, { color: C.oak }));
    fur("bedroom", box(plane, 304, 400, 14, 24, 24, 22, { color: C.oak }));
    fur("bedroom", box(plane, 152, 560, 14, 120, 30, 70, { color: "#E8DFD0", sides: "#CDBFA8" }));

    // Terrace deck + pool
    add(g.deck, box(plane, 392, 386, 4, 368, 330, 10, { color: C.wood }));
    add(g.pool, box(plane, 430, 440, 14, 300, 150, 3, { color: C.coping }));
    const water = add(g.pool, box(plane, 444, 454, 17, 272, 122, 1, { color: C.water, cls: "water" }));
    water._top.innerHTML = '<div class="caustics"></div>';
    // loungers + parasol
    [455, 505].forEach((x) => fur("deck", box(plane, x, 620, 14, 34, 70, 9, { color: "#FBF7F0", sides: C.oak })));
    fur("deck", box(plane, 580, 650, 14, 5, 5, 64, { color: C.ink }));
    fur("deck", box(plane, 548, 618, 78, 70, 70, 5, { color: C.gold }));
    fur("deck", box(plane, 640, 620, 14, 90, 50, 26, { color: C.sofa }));

    // Trees (stacked rounded canopies)
    function tree(x, y, s) {
      const t = [];
      t.push(box(plane, x + 14 * s, y + 14 * s, 4, 10 * s, 10 * s, 50 * s, { color: "#7A5A3E" }));
      t.push(box(plane, x, y, 40 * s, 38 * s, 38 * s, 30 * s, { color: "#7FA86E", sides: "#6A9160", radius: 14 * s }));
      t.push(box(plane, x + 6 * s, y + 6 * s, 66 * s, 26 * s, 26 * s, 22 * s, { color: "#94BC80", sides: "#7AA56C", radius: 10 * s }));
      g.trees.push(t);
      return t;
    }
    tree(640, 150, 1.4);
    tree(700, 270, 1.1);
    tree(70, 470, 1.2);
    tree(600, 40, 0.9);
    tree(300, 690, 1.0);
    return g;
  }

  /* Scale the height of a set of boxes (dollhouse cutaway), driven by GSAP through a setter. */
  function heightScaler(boxes) {
    let cur = 1;
    return {
      h(v) {
        if (v === undefined) return cur;
        cur = v;
        for (const b of boxes) b._inner.style.transform = `scale3d(1,1,${v})`;
      },
    };
  }

  window.PDIso = { box, billboard, rig, villa, shade, heightScaler, C };
})();

/* Flat illustration used as the listing "photo" (same picture before/after). */
window.PDIso.photo = function (variant) {
  const v = variant || "main";
  if (v === "salon")
    return `<svg viewBox="0 0 600 400" preserveAspectRatio="xMidYMid slice" width="100%" height="100%"><rect width="600" height="400" fill="#E9DCC8"/><rect x="0" y="0" width="600" height="250" fill="#F3EADD"/><rect x="330" y="40" width="230" height="180" fill="#A9D3DE"/><rect x="330" y="150" width="230" height="70" fill="#5FA9B8"/><rect x="440" y="40" width="6" height="180" fill="#F3EADD"/><rect x="0" y="250" width="600" height="150" fill="#D8C3A3"/><rect x="60" y="210" width="260" height="70" rx="10" fill="#7F90A6"/><rect x="60" y="190" width="260" height="34" rx="10" fill="#8FA0B5"/><rect x="140" y="300" width="160" height="30" rx="6" fill="#A9784D"/><circle cx="520" cy="270" r="34" fill="#7FA86E"/><rect x="510" y="290" width="22" height="50" fill="#E3D6C2"/></svg>`;
  if (v === "pool")
    return `<svg viewBox="0 0 600 400" preserveAspectRatio="xMidYMid slice" width="100%" height="100%"><rect width="600" height="400" fill="#BFE0EA"/><rect y="150" width="600" height="250" fill="#B9875A"/><polygon points="80,210 560,210 600,380 20,380" fill="#F1EBE0"/><polygon points="105,225 540,225 570,365 45,365" fill="#5FB3B3"/><polygon points="160,260 420,260 430,280 150,280" fill="#8ED0CF" opacity=".7"/><rect x="420" y="40" width="12" height="160" fill="#7A5A3E"/><circle cx="426" cy="50" r="60" fill="#7FA86E"/></svg>`;
  return `<svg viewBox="0 0 900 600" preserveAspectRatio="xMidYMid slice" width="100%" height="100%">
    <defs><linearGradient id="pd-sky-${v}" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#F6C98A"/><stop offset="0.55" stop-color="#F8E3C4"/><stop offset="1" stop-color="#CFE6EC"/></linearGradient></defs>
    <rect width="900" height="600" fill="url(#pd-sky-${v})"/>
    <circle cx="700" cy="150" r="64" fill="#FFF3DA"/>
    <rect y="300" width="900" height="70" fill="#6FB2C1"/>
    <rect y="360" width="900" height="240" fill="#A7C58F"/>
    <rect x="150" y="190" width="520" height="22" fill="#2C3848"/><rect x="150" y="208" width="520" height="8" fill="#D6A55A"/>
    <rect x="175" y="216" width="470" height="150" fill="#F5F0E8"/>
    <rect x="205" y="236" width="170" height="130" fill="#9CCAD6"/><rect x="288" y="236" width="5" height="130" fill="#F5F0E8"/>
    <rect x="400" y="236" width="215" height="130" fill="#B6DDE6"/><rect x="505" y="236" width="5" height="130" fill="#F5F0E8"/>
    <rect x="460" y="120" width="210" height="72" fill="#F5F0E8"/><rect x="450" y="110" width="232" height="14" fill="#2C3848"/>
    <rect x="490" y="135" width="150" height="45" fill="#9CCAD6"/>
    <polygon points="120,420 820,420 870,560 70,560" fill="#B9875A"/>
    <polygon points="230,440 700,440 730,535 200,535" fill="#F1EBE0"/>
    <polygon points="250,452 680,452 705,525 225,525" fill="#5FB3B3"/>
    <polygon points="300,470 560,470 566,482 296,482" fill="#9ED8D6" opacity=".8"/>
    <rect x="770" y="250" width="14" height="190" fill="#7A5A3E"/><circle cx="777" cy="250" r="62" fill="#7FA86E"/><circle cx="740" cy="282" r="38" fill="#94BC80"/>
    <rect x="80" y="300" width="12" height="130" fill="#7A5A3E"/><circle cx="86" cy="300" r="48" fill="#94BC80"/>
  </svg>`;
};
