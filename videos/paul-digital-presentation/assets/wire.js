/* Paul Digital — glowing 3D wireframe renderer (canvas 2D, perspective, deterministic).
   Every animatable value is an accessor: GSAP sets it on each seek, the setter re-renders,
   so the frame depends only on timeline time.

   const W = PDWire.create(canvas, { color: "#5EB0FF" });
   const m = W.add(PDWire.models.chalet(), { x: 0, y: 0, z: 0 });
   tl.to(W.cam, { yaw: 40 })  ·  tl.to(m, { draw: 1 })  ·  tl.to(m, { alpha: 0 })
*/
(function () {
  const D2R = Math.PI / 180;

  // ---------- geometry helpers ----------
  function Geo() {
    this.e = [];
  }
  Geo.prototype.line = function (a, b) {
    this.e.push([a, b]);
    return this;
  };
  Geo.prototype.poly = function (pts, closed) {
    for (let i = 0; i < pts.length - 1; i++) this.line(pts[i], pts[i + 1]);
    if (closed !== false) this.line(pts[pts.length - 1], pts[0]);
    return this;
  };
  // axis-aligned box: x0..x1, y0..y1 (up), z0..z1
  Geo.prototype.box = function (x0, y0, z0, x1, y1, z1) {
    const p = (x, y, z) => [x, y, z];
    this.poly([p(x0, y0, z0), p(x1, y0, z0), p(x1, y0, z1), p(x0, y0, z1)]);
    this.poly([p(x0, y1, z0), p(x1, y1, z0), p(x1, y1, z1), p(x0, y1, z1)]);
    this.line(p(x0, y0, z0), p(x0, y1, z0));
    this.line(p(x1, y0, z0), p(x1, y1, z0));
    this.line(p(x1, y0, z1), p(x1, y1, z1));
    this.line(p(x0, y0, z1), p(x0, y1, z1));
    return this;
  };
  // rectangle on the front plane z, from (x0,y0) to (x1,y1), optional cross mullion
  Geo.prototype.win = function (z, x0, y0, x1, y1, mull) {
    this.poly([[x0, y0, z], [x1, y0, z], [x1, y1, z], [x0, y1, z]]);
    if (mull) {
      const mx = (x0 + x1) / 2;
      this.line([mx, y0, z], [mx, y1, z]);
      if (mull === 2) this.line([x0, (y0 + y1) / 2, z], [x1, (y0 + y1) / 2, z]);
    }
    return this;
  };
  // window on a side plane x
  Geo.prototype.winX = function (x, z0, y0, z1, y1, mull) {
    this.poly([[x, y0, z0], [x, y0, z1], [x, y1, z1], [x, y1, z0]]);
    if (mull) this.line([x, y0, (z0 + z1) / 2], [x, y1, (z0 + z1) / 2]);
    return this;
  };

  // ---------- models (units ≈ metres, y up, centred on x/z, sitting on y=0) ----------
  const models = {
    chalet() {
      const g = new Geo();
      const W = 6, Dp = 5, H = 4.2, R = 8.2, O = 1.0; // half width, half depth, wall h, ridge h, overhang
      g.box(-W, 0, -Dp, W, H, Dp);
      // gable roof, ridge along z, overhanging
      const L = [-W - O, H - 0.5], Rr = [W + O, H - 0.5];
      for (const z of [-Dp - O, Dp + O]) {
        g.poly([[L[0], L[1], z], [0, R, z], [Rr[0], Rr[1], z]], false);
      }
      g.line([0, R, -Dp - O], [0, R, Dp + O]);
      g.line([L[0], L[1], -Dp - O], [L[0], L[1], Dp + O]);
      g.line([Rr[0], Rr[1], -Dp - O], [Rr[0], Rr[1], Dp + O]);
      // gable triangle on the front wall
      g.poly([[-W, H, Dp], [0, R - 0.6, Dp], [W, H, Dp]], false);
      // roof purlins
      for (const t of [0.33, 0.66]) {
        const yl = L[1] + (R - L[1]) * t, xl = L[0] * (1 - t);
        g.line([xl, yl, -Dp - O], [xl, yl, Dp + O]);
        g.line([-xl, yl, -Dp - O], [-xl, yl, Dp + O]);
      }
      // balcony on the front at first floor
      const by = 2.4, bz = Dp + 1.6;
      g.poly([[-W - 0.4, by, Dp], [-W - 0.4, by, bz], [W + 0.4, by, bz], [W + 0.4, by, Dp]], false);
      g.line([-W - 0.4, by + 1.1, bz], [W + 0.4, by + 1.1, bz]);
      for (let i = 0; i <= 10; i++) {
        const x = -W - 0.4 + (2 * W + 0.8) * (i / 10);
        g.line([x, by, bz], [x, by + 1.1, bz]);
      }
      g.line([-W - 0.4, by, bz], [-W - 0.4, 0, bz]);
      g.line([W + 0.4, by, bz], [W + 0.4, 0, bz]);
      // ground floor bay windows + door, upper windows
      g.win(Dp, -5, 0.3, -2.6, 2.0, 1);
      g.win(Dp, 2.6, 0.3, 5, 2.0, 1);
      g.win(Dp, -1.0, 0, 1.0, 2.1, 0);
      g.win(Dp, -4.2, 2.8, -1.6, 4.0, 1);
      g.win(Dp, 1.6, 2.8, 4.2, 4.0, 1);
      g.win(Dp, -1.0, 4.6, 1.0, 6.4, 1);
      g.winX(W, -3.5, 0.6, -1, 2.0, 1);
      g.winX(W, 1, 0.6, 3.5, 2.0, 1);
      g.winX(W, -2, 2.8, 2, 3.8, 1);
      // chimney
      g.box(2.4, 6.0, -2.0, 3.4, 9.0, -1.0);
      return g.e;
    },
    apartment() {
      const g = new Geo();
      const W = 4.2, Dp = 4, H = 15;
      g.box(-W, 0, -Dp, W, H, Dp);
      g.box(-W - 0.3, H, -Dp - 0.3, W + 0.3, H + 0.4, Dp + 0.3);
      for (let f = 1; f < 6; f++) {
        const y = f * 2.5;
        g.line([-W, y, Dp], [W, y, Dp]);
        g.line([W, y, Dp], [W, y, -Dp]);
        // balconies
        g.poly([[-3.6, y, Dp], [-3.6, y, Dp + 1.1], [-0.4, y, Dp + 1.1], [-0.4, y, Dp]], false);
        g.line([-3.6, y + 0.9, Dp + 1.1], [-0.4, y + 0.9, Dp + 1.1]);
      }
      for (let f = 0; f < 6; f++) {
        const y0 = f * 2.5 + 0.6, y1 = y0 + 1.4;
        g.win(Dp, -3.3, y0, -0.7, y1, 1);
        g.win(Dp, 0.8, y0, 3.4, y1, 1);
        g.winX(W, -3, y0, -0.8, y1, 0);
        g.winX(W, 0.8, y0, 3, y1, 0);
      }
      return g.e;
    },
    house() {
      const g = new Geo();
      const W = 5.5, Dp = 4.2, H = 3.4, R = 6.8;
      g.box(-W, 0, -Dp, W, H, Dp);
      // hip roof
      const a = [-W - 0.6, H, -Dp - 0.6], b = [W + 0.6, H, -Dp - 0.6], c = [W + 0.6, H, Dp + 0.6], d = [-W - 0.6, H, Dp + 0.6];
      const r1 = [-2.2, R, 0], r2 = [2.2, R, 0];
      g.poly([a, b, c, d]);
      g.line(r1, r2);
      g.line(a, r1); g.line(d, r1); g.line(b, r2); g.line(c, r2);
      g.win(Dp, -4.6, 0.8, -2.4, 2.4, 2);
      g.win(Dp, 2.4, 0.8, 4.6, 2.4, 2);
      g.win(Dp, -0.8, 0, 0.8, 2.3, 0);
      g.poly([[-1.6, 2.6, Dp], [0, 3.3, Dp + 1.2], [1.6, 2.6, Dp]], false);
      g.winX(W, -2.8, 0.8, -0.6, 2.4, 1);
      g.winX(W, 0.6, 0.8, 2.8, 2.4, 1);
      g.box(2.6, 4.6, -1.6, 3.5, 7.4, -0.7);
      // fence
      for (let i = 0; i <= 8; i++) g.line([-W - 1.5 + i * 1.6, 0, Dp + 3], [-W - 1.5 + i * 1.6, 1, Dp + 3]);
      g.line([-W - 1.5, 0.8, Dp + 3], [-W - 1.5 + 8 * 1.6, 0.8, Dp + 3]);
      return g.e;
    },
    villa() {
      const g = new Geo();
      g.box(-7, 0, -4, 2, 3.2, 4);
      g.box(-3, 3.2, -4.5, 5.5, 6.4, 2.5);
      g.box(-3.3, 6.4, -4.8, 5.8, 6.7, 2.8);
      g.box(-7.3, 3.2, -4.3, 2.3, 3.5, 4.3);
      // glass walls
      for (let i = 0; i <= 6; i++) g.line([-6.5 + i * 1.3, 0, 4], [-6.5 + i * 1.3, 3.2, 4]);
      for (let i = 0; i <= 6; i++) g.line([-2.6 + i * 1.3, 3.2, 2.5], [-2.6 + i * 1.3, 6.4, 2.5]);
      // pool
      g.poly([[2.5, 0.05, 1], [9, 0.05, 1], [9, 0.05, 6], [2.5, 0.05, 6]]);
      g.poly([[2.9, 0.05, 1.4], [8.6, 0.05, 1.4], [8.6, 0.05, 5.6], [2.9, 0.05, 5.6]]);
      // deck
      g.poly([[-7, 0, 4], [-7, 0, 7], [9.5, 0, 7], [9.5, 0, 6]], false);
      // palm-ish posts
      g.line([10.5, 0, 0], [10.2, 5, 0]);
      for (let k = 0; k < 5; k++) {
        const a = (k / 5) * Math.PI * 2;
        g.line([10.2, 5, 0], [10.2 + Math.cos(a) * 2, 4.2, Math.sin(a) * 2]);
      }
      return g.e;
    },
    // a flat UI wireframe (website skeleton) in the x/y plane at z=0 — size 16 x 10
    site() {
      const g = new Geo();
      g.poly([[-8, 0, 0], [8, 0, 0], [8, 10, 0], [-8, 10, 0]]);
      g.poly([[-8, 9.2, 0], [8, 9.2, 0]], false);
      g.poly([[-7.4, 7.6, 0], [-1, 7.6, 0], [-1, 8.4, 0], [-7.4, 8.4, 0]]);
      g.poly([[-7.4, 6.5, 0], [-2.5, 6.5, 0], [-2.5, 7.1, 0], [-7.4, 7.1, 0]]);
      g.poly([[-7.4, 4.6, 0], [-4.4, 4.6, 0], [-4.4, 5.4, 0], [-7.4, 5.4, 0]]);
      g.poly([[2.5, 2.6, 0], [7.2, 2.6, 0], [7.2, 6.4, 0], [2.5, 6.4, 0]]);
      g.line([2.5, 2.6, 0], [7.2, 6.4, 0]);
      g.line([2.5, 6.4, 0], [7.2, 2.6, 0]);
      for (let i = 0; i < 4; i++) g.poly([[-7.4 + i * 3.8, 0.6, 0], [-4.2 + i * 3.8, 0.6, 0], [-4.2 + i * 3.8, 2.0, 0], [-7.4 + i * 3.8, 2.0, 0]]);
      return g.e;
    },
  };

  // ---------- renderer ----------
  function create(canvas, opts) {
    opts = opts || {};
    const ctx = canvas.getContext("2d");
    const Wd = canvas.width, Ht = canvas.height;
    const items = [];
    let ready = false;
    const camState = { yaw: 30, pitch: 18, dist: 32, fov: 40, tx: 0, ty: 4, tz: 0, ox: 0, oy: 0, roll: 0 };
    const gridState = { grid: opts.grid ? 1 : 0, gridSize: opts.gridSize || 40, gridStep: 2 };
    const sceneState = { alpha: 1, glow: 1 };

    function render() {
      if (!ready) return;
      ctx.setTransform(1, 0, 0, 1, 0, 0);
      ctx.clearRect(0, 0, Wd, Ht);
      if (sceneState.alpha <= 0.001) return;
      const c = camState;
      const yaw = c.yaw * D2R, pit = c.pitch * D2R, rol = c.roll * D2R;
      // camera position on a sphere around the target
      const cx = c.tx + c.dist * Math.cos(pit) * Math.sin(yaw);
      const cy = c.ty + c.dist * Math.sin(pit);
      const cz = c.tz + c.dist * Math.cos(pit) * Math.cos(yaw);
      // basis
      let fx = c.tx - cx, fy = c.ty - cy, fz = c.tz - cz;
      const fl = Math.hypot(fx, fy, fz); fx /= fl; fy /= fl; fz /= fl;
      let rx = fz, ry = 0, rz = -fx; // right = forward x up(0,1,0)
      const rl = Math.hypot(rx, rz) || 1; rx /= rl; rz /= rl;
      rx = -rx; rz = -rz;
      const ux = ry * fz - rz * fy, uy = rz * fx - rx * fz, uz = rx * fy - ry * fx;
      const f = (Ht / 2) / Math.tan((c.fov * D2R) / 2);
      const cr = Math.cos(rol), sr = Math.sin(rol);
      const hx = Wd / 2 + c.ox, hy = Ht / 2 + c.oy;
      function proj(p) {
        const dx = p[0] - cx, dy = p[1] - cy, dz = p[2] - cz;
        const z = dx * fx + dy * fy + dz * fz;
        if (z < 0.5) return null;
        const x = (dx * rx + dy * ry + dz * rz) * f / z;
        const y = (dx * ux + dy * uy + dz * uz) * f / z;
        return [hx + x * cr - y * sr, hy - (x * sr + y * cr), z];
      }
      ctx.globalAlpha = sceneState.alpha;
      ctx.lineCap = "round";
      // floor grid
      if (gridState.grid > 0.001) {
        const N = gridState.gridSize, s = gridState.gridStep;
        ctx.strokeStyle = opts.gridColor || "rgba(94,176,255,1)";
        ctx.lineWidth = 1.2;
        for (let i = -N; i <= N; i += s) {
          for (const dir of [0, 1]) {
            const a = dir ? [i, 0, -N] : [-N, 0, i];
            const b = dir ? [i, 0, N] : [N, 0, i];
            // fade with distance from centre
            const fade = 1 - Math.abs(i) / N;
            ctx.globalAlpha = sceneState.alpha * gridState.grid * 0.22 * fade * fade;
            // split into segments so clipping near camera behaves
            const seg = 8;
            ctx.beginPath();
            let started = false;
            for (let k = 0; k <= seg; k++) {
              const t = k / seg;
              const q = proj([a[0] + (b[0] - a[0]) * t, 0, a[2] + (b[2] - a[2]) * t]);
              if (!q) { started = false; continue; }
              if (!started) { ctx.moveTo(q[0], q[1]); started = true; } else ctx.lineTo(q[0], q[1]);
            }
            ctx.stroke();
          }
        }
      }
      for (const it of items) {
        const st = it.state;
        if (st.alpha <= 0.001 || st.draw <= 0.0001) continue;
        const n = it.edges.length;
        const cy0 = Math.cos(st.ry * D2R), sy0 = Math.sin(st.ry * D2R);
        const tf = (p) => {
          const x = p[0] * st.s, y = p[1] * st.s * st.sy, z = p[2] * st.s;
          return [st.x + x * cy0 + z * sy0, st.y + y, st.z - x * sy0 + z * cy0];
        };
        const segs = [];
        for (let i = 0; i < n; i++) {
          // staggered draw-on: each edge starts a bit later, by its build order
          const start = (it.order[i] / n) * 0.72;
          const lp = Math.max(0, Math.min(1, (st.draw - start) / 0.28));
          if (lp <= 0) continue;
          const A = tf(it.edges[i][0]), B0 = tf(it.edges[i][1]);
          const B = [A[0] + (B0[0] - A[0]) * lp, A[1] + (B0[1] - A[1]) * lp, A[2] + (B0[2] - A[2]) * lp];
          const pa = proj(A), pb = proj(B);
          if (!pa || !pb) continue;
          segs.push([pa, pb, lp < 1]);
        }
        const col = st.color || opts.color || "#5EB0FF";
        // glow pass
        ctx.globalAlpha = sceneState.alpha * st.alpha * 0.35 * sceneState.glow;
        ctx.strokeStyle = col;
        ctx.lineWidth = (opts.glowWidth || 7) * st.lw;
        ctx.shadowColor = col;
        ctx.shadowBlur = 18;
        ctx.beginPath();
        for (const s of segs) { ctx.moveTo(s[0][0], s[0][1]); ctx.lineTo(s[1][0], s[1][1]); }
        ctx.stroke();
        ctx.shadowBlur = 0;
        // core pass
        ctx.globalAlpha = sceneState.alpha * st.alpha;
        ctx.strokeStyle = opts.core || "#E8F4FF";
        ctx.lineWidth = 1.8 * st.lw;
        ctx.beginPath();
        for (const s of segs) { ctx.moveTo(s[0][0], s[0][1]); ctx.lineTo(s[1][0], s[1][1]); }
        ctx.stroke();
        // spark at the growing tips
        ctx.fillStyle = "#FFFFFF";
        for (const s of segs) {
          if (!s[2]) continue;
          ctx.globalAlpha = sceneState.alpha * st.alpha;
          ctx.beginPath();
          ctx.arc(s[1][0], s[1][1], 3.2 * st.lw, 0, Math.PI * 2);
          ctx.fill();
        }
      }
      ctx.globalAlpha = 1;
    }

    function accessors(target, state) {
      for (const k of Object.keys(state)) {
        Object.defineProperty(target, k, {
          get: () => state[k],
          set: (v) => { state[k] = v; render(); },
          enumerable: true,
        });
      }
      return target;
    }

    const api = {
      cam: accessors({}, camState),
      grid: accessors({}, gridState),
      scene: accessors({}, sceneState),
      add(edges, o) {
        o = o || {};
        const state = Object.assign({ x: 0, y: 0, z: 0, s: 1, sy: 1, ry: 0, draw: 0, alpha: 1, lw: 1, color: null }, o);
        // build order: bottom-up then by distance from centre, so it "rises"
        const keyed = edges.map((e, i) => [Math.min(e[0][1], e[1][1]) * 10 + Math.abs(e[0][0] + e[1][0]) * 0.15 + i * 0.001, i]);
        keyed.sort((a, b) => a[0] - b[0]);
        const order = new Array(edges.length);
        keyed.forEach((k, rank) => { order[k[1]] = rank; });
        const item = { edges, order, state };
        items.push(item);
        return accessors({}, state);
      },
      render,
      start() { ready = true; render(); },
    };
    return api;
  }

  window.PDWire = { create, models };
})();
