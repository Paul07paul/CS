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
