/* Shared motion helpers for the luxury house video. All tweens go on the scene's paused timeline. */
(function () {
  // card entrances: each one is a different camera move so no two cuts feel the same
  const IN = {
    flyL: { x: -1500, rotationY: 65, z: -400, opacity: 0 },
    flyR: { x: 1500, rotationY: -65, z: -400, opacity: 0 },
    up: { y: 1200, rotationX: -55, opacity: 0 },
    down: { y: -1200, rotationX: 55, opacity: 0 },
    zoom: { z: -2600, rotationX: 30, rotationY: -25, opacity: 0 },
    spin: { rotationY: -200, z: -900, opacity: 0 },
  };
  window.HIn = function (tl, sel, t, kind, d) {
    tl.from(sel, Object.assign({ duration: d || 0.7, ease: "expo.out", immediateRender: true }, IN[kind]), t);
  };
  const OUT = {
    left: { x: -1700, rotationY: -55, opacity: 0, filter: "blur(18px)" },
    right: { x: 1700, rotationY: 55, opacity: 0, filter: "blur(18px)" },
    up: { y: -1300, rotationX: 40, opacity: 0, filter: "blur(18px)" },
    down: { y: 1300, rotationX: -40, opacity: 0, filter: "blur(18px)" },
    dive: { z: 1100, opacity: 0, filter: "blur(20px)" },
  };
  window.HOut = function (tl, sel, t, kind, d) {
    tl.to(sel, Object.assign({ duration: d || 0.35, ease: "power3.in" }, OUT[kind]), t);
  };
  // slow 3D drift while a card is on screen (keeps footage alive even when the clip is static)
  window.HDrift = function (tl, sel, t, d, dir) {
    dir = dir || 1;
    tl.fromTo(sel, { rotationY: -9 * dir, scale: 1 }, { rotationY: 9 * dir, scale: 1.045, duration: d, ease: "sine.inOut", immediateRender: false }, t);
  };
  // light sweep across a card's glass
  window.HSheen = function (tl, sel, t) {
    gsap.set(sel, { xPercent: -240 }); // parked off-frame between passes
    tl.fromTo(sel, { xPercent: -240 }, { xPercent: 340, duration: 0.9, ease: "power2.inOut", immediateRender: false }, t);
  };
  // gold extruded 3D title: flies in from depth, swings, rings + particles burst behind it
  window.HTitle = function (tl, host, text, x, y, t, o) {
    o = o || {};
    const r = PDExtrude(host, text, { size: o.size || 150, x: x, y: y, layers: o.layers || 12, step: o.step || 6, gold: true, color: "#FFF8EC" });
    const from = o.from || { z: -2400, rotationX: 45, rotationY: -60, scale: 0.6 };
    tl.fromTo(r, Object.assign({ opacity: 0 }, from), { x: 0, y: 0, z: 0, rotationX: 8, rotationY: o.ry0 || -16, scale: 1, opacity: 1, duration: 0.6, ease: "expo.out" }, t);
    tl.to(r, { rotationY: o.ry1 || 14, rotationX: 2, duration: o.hold || 2.0, ease: "sine.inOut" }, t + 0.6);
    if (o.burst !== false) PDBurst(tl, host, x, y, t + 0.05, { r: o.r || 520, seed: o.seed || 3, n: o.n || 22, dur: 1.4, hold: o.burstHold || 1.1, color: "#FFD58A", glow: "#FFAA33", dot: "#FFE6B0" });
    if (o.out) tl.to(r, Object.assign({ duration: 0.35, ease: "power3.in" }, o.out), o.outAt);
    return r;
  };
  // masked line reveal: element slides up from under its own line
  window.HLine = function (tl, sel, t, d) {
    tl.from(sel, { yPercent: 115, duration: d || 0.55, ease: "expo.out" }, t);
  };
  window.HChip = function (tl, sel, t) {
    tl.from(sel, { opacity: 0, scale: 0.4, y: 30, duration: 0.55, ease: "back.out(2.2)" }, t);
  };
})();

/* ---- full-bleed footage transitions (vertical version) ---- */
(function () {
  const IN = {
    zoom: [{ scale: 1.45, filter: "blur(22px) brightness(1.6)" }, { scale: 1.06, filter: "blur(0px) brightness(1)" }],
    wipeUp: [{ clipPath: "inset(100% 0% 0% 0%)" }, { clipPath: "inset(0% 0% 0% 0%)" }],
    wipeDown: [{ clipPath: "inset(0% 0% 100% 0%)" }, { clipPath: "inset(0% 0% 0% 0%)" }],
    iris: [{ clipPath: "circle(0% at 50% 50%)" }, { clipPath: "circle(80% at 50% 50%)" }],
    whipL: [{ x: -1080, filter: "blur(26px)" }, { x: 0, filter: "blur(0px)" }],
    whipR: [{ x: 1080, filter: "blur(26px)" }, { x: 0, filter: "blur(0px)" }],
    rise: [{ y: 1920, filter: "blur(24px)" }, { y: 0, filter: "blur(0px)" }],
  };
  // a shot enters over the previous one
  window.HShot = function (tl, sel, t, kind, d) {
    const [a, b] = IN[kind];
    tl.fromTo(sel, a, Object.assign({ duration: d || 0.55, ease: "expo.out", immediateRender: true }, b), t);
  };
  // slow push-in on the footage while it plays (keeps every shot moving)
  window.HKen = function (tl, sel, t, d, s0, s1, o) {
    o = o || {};
    tl.fromTo(sel, { scale: s0, x: o.x0 || 0, y: o.y0 || 0, rotation: o.r0 || 0 }, { scale: s1, x: o.x1 || 0, y: o.y1 || 0, rotation: o.r1 || 0, duration: d, ease: "none", immediateRender: false }, t);
  };
})();

/* ---- flat kinetic titles: one look, many entrances (so every title is not 3D + rings) ---- */
(function () {
  const DEPTH = "0 3px 0 #E2AE5C, 0 6px 0 #B57B27, 0 9px 0 #7E5216, 0 0 34px rgba(255,170,60,0.55), 0 14px 30px rgba(0,0,0,0.65)";
  // builds a centred title; each letter is its own span so it can be animated
  function build(host, text, y, size) {
    const el = document.createElement("div");
    const lines = text.split("\n");
    el.style.cssText = "position:absolute;left:0;width:1080px;text-align:center;top:" + Math.round(y - size * 0.5 * lines.length) + "px;font-family:Montserrat,sans-serif;font-weight:900;font-size:" + size + "px;line-height:1.0;letter-spacing:-0.035em;color:#FFF8EC;white-space:nowrap;text-shadow:" + DEPTH + ";";
    const letters = [], rows = [];
    lines.forEach((ln) => {
      const row = document.createElement("div");
      row.style.cssText = "position:relative;display:block;";
      [...ln].forEach((ch) => {
        const s = document.createElement("span");
        s.textContent = ch === " " ? " " : ch;
        s.style.cssText = "display:inline-block;";
        row.appendChild(s);
        letters.push(s);
      });
      el.appendChild(row);
      rows.push(row);
    });
    host.appendChild(el);
    return { el, letters, rows, h: size * lines.length };
  }
  const STYLES = {
    // letters rise one by one out of a blur
    rise(tl, b, t) {
      tl.from(b.letters, { yPercent: 90, opacity: 0, filter: "blur(12px)", duration: 0.5, ease: "expo.out", stagger: 0.035 }, t);
    },
    // each letter flips down from the top, like a split-flap board
    flip(tl, b, t) {
      b.el.style.perspective = "900px";
      tl.from(b.letters, { rotationX: -100, opacity: 0, transformOrigin: "50% 0%", duration: 0.55, ease: "back.out(1.6)", stagger: 0.045 }, t);
    },
    // the word slams down from huge and tightens into place
    slam(tl, b, t) {
      tl.from(b.el, { scale: 2.6, opacity: 0, filter: "blur(18px)", duration: 0.45, ease: "power4.out" }, t);
      tl.from(b.letters, { x: (i) => (i - (b.letters.length - 1) / 2) * 26, duration: 0.7, ease: "expo.out" }, t);
    },
    // a light bar sweeps across and leaves the word behind it
    wipe(tl, b, t, host) {
      const bar = document.createElement("div");
      const top = parseFloat(b.el.style.top), h = b.h;
      bar.style.cssText = "position:absolute;left:0;top:" + (top - 20) + "px;width:10px;height:" + (h + 40) + "px;background:#FFF3DC;box-shadow:0 0 30px 10px rgba(255,180,80,0.8);border-radius:5px;opacity:0;";
      host.appendChild(bar);
      tl.fromTo(b.el, { clipPath: "inset(0% 100% 0% 0%)" }, { clipPath: "inset(0% 0% 0% 0%)", duration: 0.6, ease: "power2.inOut" }, t);
      tl.fromTo(bar, { x: 60, opacity: 1 }, { x: 1020, duration: 0.6, ease: "power2.inOut" }, t);
      tl.to(bar, { opacity: 0, duration: 0.15 }, t + 0.55);
    },
    // the two halves of the word arrive from opposite sides
    split(tl, b, t) {
      const n = b.letters.length, half = Math.ceil(n / 2);
      tl.from(b.letters.slice(0, half), { x: -700, opacity: 0, duration: 0.55, ease: "expo.out", stagger: { each: 0.02, from: "end" } }, t);
      tl.from(b.letters.slice(half), { x: 700, opacity: 0, duration: 0.55, ease: "expo.out", stagger: 0.02 }, t);
    },
    // outline is drawn first, then the word fills with light
    outline(tl, b, t) {
      gsap.set(b.el, { color: "rgba(255,248,236,0)", textShadow: "none", webkitTextStroke: "2px #F7D08A" });
      tl.from(b.letters, { opacity: 0, y: 30, duration: 0.4, ease: "power2.out", stagger: 0.03 }, t);
      tl.to(b.el, { color: "rgba(255,248,236,1)", duration: 0.35, ease: "power2.out" }, t + 0.55);
      tl.set(b.el, { textShadow: DEPTH, webkitTextStroke: "0px #F7D08A" }, t + 0.75);
    },
    // light flickers on letter by letter, like neon tubes warming up
    neon(tl, b, t) {
      b.letters.forEach((s, i) => {
        const d = t + ((i * 7) % b.letters.length) * 0.04;
        tl.fromTo(s, { opacity: 0 }, { keyframes: [{ opacity: 1, duration: 0.04 }, { opacity: 0.2, duration: 0.05 }, { opacity: 1, duration: 0.04 }], ease: "none", immediateRender: true }, d);
      });
    },
  };
  // style: one of rise | flip | slam | wipe | split | outline | neon. Returns the title element.
  window.HText = function (tl, host, text, y, t, style, o) {
    o = o || {};
    const b = build(host, text, y, o.size || 150);
    STYLES[style](tl, b, t, host);
    // gentle life while it holds
    tl.fromTo(b.el, { y: 0 }, { y: -14, duration: o.hold || 1.6, ease: "sine.inOut", immediateRender: false }, t + 0.6);
    if (o.outAt != null) tl.to(b.el, { opacity: 0, y: -80, filter: "blur(12px)", duration: 0.3, ease: "power2.in" }, o.outAt);
    return b.el;
  };
})();
