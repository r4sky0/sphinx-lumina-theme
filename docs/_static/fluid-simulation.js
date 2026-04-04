/**
 * GPU Fluid Simulation — Lumina landing page hero background.
 *
 * Implements Jos Stam's Stable Fluids on WebGL2 with ping-pong framebuffers.
 * Supports light/dark mode via a theme-aware display shader.
 *
 * Exported as an Alpine.js component: attach with x-data="fluidSimulation()"
 * and provide a <canvas x-ref="canvas"> inside the element.
 */

// Self-registering Alpine.js component for docs showcase landing page.
// This file is NOT part of the shipped theme — it's docs-only.
document.addEventListener("alpine:init", () => {
  window.Alpine.data("fluidSimulation", () => ({
    _cleanup: null,
    _observer: null,

    init() {
      const canvas = this.$refs.canvas;
      const isMobile = window.innerWidth < 768;
      const opts = isMobile ? { sim: 128, dye: 256, jacobi: 20 } : {};

      const start = () => {
        this._cleanup = startFluid(canvas, this.$el, opts);
      };

      // Defer heavy GPU init to avoid blocking initial page render.
      // requestIdleCallback waits for an idle period; the timeout ensures
      // the simulation starts within 2 s even on a busy main thread.
      if ("requestIdleCallback" in window) {
        this._idleId = requestIdleCallback(start, { timeout: 2000 });
      } else {
        this._timerId = setTimeout(start, 100);
      }

      /* Track hero visibility so the header can go transparent */
      this._observer = new IntersectionObserver(
        ([e]) =>
          document.documentElement.toggleAttribute(
            "data-hero-visible",
            e.isIntersecting,
          ),
        { threshold: 0 },
      );
      this._observer.observe(this.$el);
      document.documentElement.setAttribute("data-hero-visible", "");
    },

    destroy() {
      if (this._idleId) cancelIdleCallback(this._idleId);
      if (this._timerId) clearTimeout(this._timerId);
      if (this._cleanup) this._cleanup();
      if (this._observer) this._observer.disconnect();
      document.documentElement.removeAttribute("data-hero-visible");
    },
  }));
});

/* ────────────────────────────────────────────────────────────────────────── */

function startFluid(canvas, container, opts = {}) {
  const gl = canvas.getContext("webgl2", {
    alpha: true,
    premultipliedAlpha: false,
  });
  if (!gl || !gl.getExtension("EXT_color_buffer_float")) {
    canvas.style.display = "none";
    return () => {};
  }

  const prefersReduced = window.matchMedia(
    "(prefers-reduced-motion: reduce)",
  ).matches;

  /* ── Config ── */
  const SIM = opts.sim || 256;
  const DYE = opts.dye || 512;
  const JACOBI_ITERS = opts.jacobi || 30;
  const VEL_DISSIPATION = 0.985;
  const DYE_DISSIPATION = 0.978;
  const PRESS_DISSIPATION = 0.8;
  const SPLAT_RADIUS = 0.006;
  const SPLAT_FORCE = 2000;
  const SIM_TEXEL = new Float32Array([1 / SIM, 1 / SIM]);

  const DYE_COLORS = [
    [0.06, 0.5, 0.28],
    [0.1, 0.55, 0.35],
    [0.07, 0.45, 0.4],
    [0.11, 0.58, 0.32],
    [0.05, 0.4, 0.33],
  ];

  /* ── Dark-mode state ── */
  let darkMode =
    document.documentElement.getAttribute("data-theme") === "dark" ? 1.0 : 0.0;

  const themeObserver = new MutationObserver(() => {
    darkMode =
      document.documentElement.getAttribute("data-theme") === "dark"
        ? 1.0
        : 0.0;
  });
  themeObserver.observe(document.documentElement, {
    attributes: true,
    attributeFilter: ["data-theme"],
  });

  /* ── WebGL helpers ── */
  function compileShader(type, src) {
    const s = gl.createShader(type);
    gl.shaderSource(s, src);
    gl.compileShader(s);
    return s;
  }

  let baseVShader;

  function createProgram(fsSrc) {
    const fs = compileShader(gl.FRAGMENT_SHADER, fsSrc);
    const p = gl.createProgram();
    gl.attachShader(p, baseVShader);
    gl.attachShader(p, fs);
    gl.linkProgram(p);
    gl.deleteShader(fs);
    const uniforms = {};
    for (
      let i = 0, n = gl.getProgramParameter(p, gl.ACTIVE_UNIFORMS);
      i < n;
      i++
    ) {
      const { name } = gl.getActiveUniform(p, i);
      uniforms[name] = gl.getUniformLocation(p, name);
    }
    return { program: p, uniforms };
  }

  function createFBO(w, h, fmt, channels, type, filter) {
    const tex = gl.createTexture();
    gl.bindTexture(gl.TEXTURE_2D, tex);
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MIN_FILTER, filter);
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MAG_FILTER, filter);
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_S, gl.CLAMP_TO_EDGE);
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_T, gl.CLAMP_TO_EDGE);
    gl.texImage2D(gl.TEXTURE_2D, 0, fmt, w, h, 0, channels, type, null);
    const fbo = gl.createFramebuffer();
    gl.bindFramebuffer(gl.FRAMEBUFFER, fbo);
    gl.framebufferTexture2D(
      gl.FRAMEBUFFER,
      gl.COLOR_ATTACHMENT0,
      gl.TEXTURE_2D,
      tex,
      0,
    );
    return { texture: tex, fbo, width: w, height: h };
  }

  function createDoubleFBO(w, h, fmt, channels, type, filter) {
    let a = createFBO(w, h, fmt, channels, type, filter);
    let b = createFBO(w, h, fmt, channels, type, filter);
    return {
      get read() {
        return a;
      },
      get write() {
        return b;
      },
      swap() {
        [a, b] = [b, a];
      },
    };
  }

  /* ── Fullscreen quad VAO ── */
  const quadVAO = gl.createVertexArray();
  gl.bindVertexArray(quadVAO);
  const quadBuf = gl.createBuffer();
  gl.bindBuffer(gl.ARRAY_BUFFER, quadBuf);
  gl.bufferData(
    gl.ARRAY_BUFFER,
    new Float32Array([-1, -1, 1, -1, -1, 1, 1, 1]),
    gl.STATIC_DRAW,
  );
  gl.enableVertexAttribArray(0);
  gl.vertexAttribPointer(0, 2, gl.FLOAT, false, 0, 0);
  gl.bindVertexArray(null);

  function use(prog) {
    gl.useProgram(prog.program);
  }

  function blit(target) {
    if (target) {
      gl.bindFramebuffer(gl.FRAMEBUFFER, target.fbo);
      gl.viewport(0, 0, target.width, target.height);
    } else {
      gl.bindFramebuffer(gl.FRAMEBUFFER, null);
      gl.viewport(0, 0, gl.drawingBufferWidth, gl.drawingBufferHeight);
    }
    gl.drawArrays(gl.TRIANGLE_STRIP, 0, 4);
  }

  function bindTex(unit, texture) {
    gl.activeTexture(gl.TEXTURE0 + unit);
    gl.bindTexture(gl.TEXTURE_2D, texture);
  }

  /* ── Shaders ── */
  const baseVS = `#version 300 es
    layout(location=0) in vec2 a_position;
    out vec2 vUv;
    void main() {
      vUv = a_position * 0.5 + 0.5;
      gl_Position = vec4(a_position, 0, 1);
    }`;

  baseVShader = compileShader(gl.VERTEX_SHADER, baseVS);

  const splatFS = `#version 300 es
    precision highp float;
    in vec2 vUv;
    out vec4 fragColor;
    uniform sampler2D uTarget;
    uniform float aspectRatio;
    uniform vec3 color;
    uniform vec2 point;
    uniform float radius;
    void main() {
      vec2 p = vUv - point;
      p.x *= aspectRatio;
      fragColor = vec4(texture(uTarget, vUv).rgb + exp(-dot(p,p) / radius) * color, 1.0);
    }`;

  const advectionFS = `#version 300 es
    precision highp float;
    in vec2 vUv;
    out vec4 fragColor;
    uniform sampler2D uVelocity;
    uniform sampler2D uSource;
    uniform vec2 texelSize;
    uniform float dt;
    uniform float dissipation;
    void main() {
      fragColor = dissipation * texture(uSource, vUv - dt * texture(uVelocity, vUv).xy * texelSize);
    }`;

  const divergenceFS = `#version 300 es
    precision highp float;
    in vec2 vUv;
    out vec4 fragColor;
    uniform sampler2D uVelocity;
    uniform vec2 texelSize;
    void main() {
      float L = texture(uVelocity, vUv - vec2(texelSize.x, 0)).x;
      float R = texture(uVelocity, vUv + vec2(texelSize.x, 0)).x;
      float B = texture(uVelocity, vUv - vec2(0, texelSize.y)).y;
      float T = texture(uVelocity, vUv + vec2(0, texelSize.y)).y;
      fragColor = vec4(0.5 * (R - L + T - B), 0, 0, 1);
    }`;

  const pressureFS = `#version 300 es
    precision highp float;
    in vec2 vUv;
    out vec4 fragColor;
    uniform sampler2D uPressure;
    uniform sampler2D uDivergence;
    uniform vec2 texelSize;
    void main() {
      float L = texture(uPressure, vUv - vec2(texelSize.x, 0)).x;
      float R = texture(uPressure, vUv + vec2(texelSize.x, 0)).x;
      float B = texture(uPressure, vUv - vec2(0, texelSize.y)).x;
      float T = texture(uPressure, vUv + vec2(0, texelSize.y)).x;
      fragColor = vec4((L + R + B + T - texture(uDivergence, vUv).x) * 0.25, 0, 0, 1);
    }`;

  const gradSubFS = `#version 300 es
    precision highp float;
    in vec2 vUv;
    out vec4 fragColor;
    uniform sampler2D uPressure;
    uniform sampler2D uVelocity;
    uniform vec2 texelSize;
    void main() {
      float L = texture(uPressure, vUv - vec2(texelSize.x, 0)).x;
      float R = texture(uPressure, vUv + vec2(texelSize.x, 0)).x;
      float B = texture(uPressure, vUv - vec2(0, texelSize.y)).x;
      float T = texture(uPressure, vUv + vec2(0, texelSize.y)).x;
      fragColor = vec4(texture(uVelocity, vUv).xy - vec2(R - L, T - B), 0, 1);
    }`;

  /* Display shader — interpolates between light and dark palettes via uDark */
  const displayFS = `#version 300 es
    precision highp float;
    in vec2 vUv;
    out vec4 fragColor;
    uniform sampler2D uDye;
    uniform float uDark;
    void main() {
      vec3 dye = texture(uDye, vUv).rgb * mix(2.5, 3.0, uDark);
      vec3 bg  = mix(vec3(0.988, 0.988, 0.984), vec3(0.035, 0.035, 0.043), uDark);
      float i  = length(dye);

      /* 4-stop emerald tone-map — blended between light/dark palettes */
      vec3 tA = mix(vec3(0.920, 0.978, 0.955), vec3(0.025, 0.065, 0.045), uDark);
      vec3 tB = mix(vec3(0.800, 0.955, 0.900), vec3(0.040, 0.130, 0.085), uDark);
      vec3 tC = mix(vec3(0.500, 0.880, 0.740), vec3(0.070, 0.260, 0.170), uDark);
      vec3 tD = mix(vec3(0.150, 0.770, 0.560), vec3(0.120, 0.480, 0.320), uDark);

      vec3 tinted = mix(tA, tB, smoothstep(0.0, 0.25, i));
      tinted = mix(tinted, tC, smoothstep(0.25, 0.8, i));
      tinted = mix(tinted, tD, smoothstep(0.8, 2.0, i));
      vec3 color = mix(bg, tinted, smoothstep(0.005, 0.25, i) * 0.7);

      /* Elliptical content mask — protects center text readability */
      float contentMask = smoothstep(0.15, 0.6, length((vUv - 0.5) * vec2(1.3, 2.0)));
      color = mix(bg, color, 0.4 + contentMask * 0.6);

      /* Vignette */
      float vig = 1.0 - smoothstep(0.5, 1.3, length(vUv - 0.5) * 1.4);
      color = mix(color * 0.97, color, vig);
      fragColor = vec4(color, 1.0);
    }`;

  const clearFS = `#version 300 es
    precision highp float;
    in vec2 vUv;
    out vec4 fragColor;
    uniform sampler2D uTexture;
    uniform float value;
    void main() { fragColor = value * texture(uTexture, vUv); }`;

  /* ── Programs ── */
  const prog = {
    splat: createProgram(splatFS),
    advection: createProgram(advectionFS),
    divergence: createProgram(divergenceFS),
    pressure: createProgram(pressureFS),
    gradSub: createProgram(gradSubFS),
    display: createProgram(displayFS),
    clear: createProgram(clearFS),
  };
  gl.deleteShader(baseVShader);

  /* ── FBOs ── */
  const velocity = createDoubleFBO(
    SIM,
    SIM,
    gl.RG16F,
    gl.RG,
    gl.HALF_FLOAT,
    gl.LINEAR,
  );
  const pressure = createDoubleFBO(
    SIM,
    SIM,
    gl.R16F,
    gl.RED,
    gl.HALF_FLOAT,
    gl.LINEAR,
  );
  const divergence = createFBO(
    SIM,
    SIM,
    gl.R16F,
    gl.RED,
    gl.HALF_FLOAT,
    gl.NEAREST,
  );
  const dye = createDoubleFBO(
    DYE,
    DYE,
    gl.RGBA16F,
    gl.RGBA,
    gl.HALF_FLOAT,
    gl.LINEAR,
  );

  /* ── Pointer input ──
   * Events are on the container (not canvas) so mouse movement over hero
   * text/buttons still drives the simulation. Deltas are computed per-frame
   * in the step() function to capture the full movement between frames and
   * avoid stale-position spikes.
   */
  const pointer = { x: 0, y: 0, prevX: -1, prevY: -1, active: false };

  function onPointerMove(cx, cy) {
    pointer.x = cx / canvas.clientWidth;
    pointer.y = 1.0 - cy / canvas.clientHeight;
    pointer.active = true;
  }

  const onMouseEnter = (e) => {
    pointer.prevX = e.clientX / canvas.clientWidth;
    pointer.prevY = 1.0 - e.clientY / canvas.clientHeight;
  };
  const onMouseMove = (e) => onPointerMove(e.clientX, e.clientY);
  const onTouchStart = (e) => {
    const t = e.touches[0];
    pointer.prevX = t.clientX / canvas.clientWidth;
    pointer.prevY = 1.0 - t.clientY / canvas.clientHeight;
  };
  const onTouchMove = (e) =>
    onPointerMove(e.touches[0].clientX, e.touches[0].clientY);

  container.addEventListener("mouseenter", onMouseEnter);
  container.addEventListener("mousemove", onMouseMove);
  container.addEventListener("touchstart", onTouchStart, { passive: true });
  container.addEventListener("touchmove", onTouchMove, { passive: true });

  /* ── Splat ── */
  function splat(x, y, dx, dy, radius) {
    const u = prog.splat.uniforms;
    use(prog.splat);
    gl.uniform1i(u.uTarget, 0);
    gl.uniform1f(u.aspectRatio, canvas.clientWidth / canvas.clientHeight);
    gl.uniform2f(u.point, x, y);
    gl.uniform1f(u.radius, radius);

    gl.uniform3f(u.color, dx, dy, 0);
    bindTex(0, velocity.read.texture);
    blit(velocity.write);
    velocity.swap();

    const c = DYE_COLORS[(Math.random() * DYE_COLORS.length) | 0];
    gl.uniform3f(u.color, c[0], c[1], c[2]);
    bindTex(0, dye.read.texture);
    blit(dye.write);
    dye.swap();
  }

  /* ── Ambient edge splats ── */
  let nextAmbientAt = 0.7 + Math.random() * 0.6;
  let ambientTimer = 0;

  function edgeSplat() {
    const regions = [
      () => [0.02 + Math.random() * 0.2, Math.random()],
      () => [0.78 + Math.random() * 0.2, Math.random()],
      () => [Math.random(), 0.75 + Math.random() * 0.23],
      () => [Math.random(), 0.02 + Math.random() * 0.23],
    ];
    const [x, y] = regions[(Math.random() * 4) | 0]();
    const angle = Math.random() * Math.PI * 2;
    const speed = 200 + Math.random() * 400;
    splat(
      x,
      y,
      Math.cos(angle) * speed,
      Math.sin(angle) * speed,
      0.005 + Math.random() * 0.003,
    );
  }

  /* ── Resize ── */
  function resize() {
    const dpr = Math.min(window.devicePixelRatio || 1, 2);
    canvas.width = canvas.clientWidth * dpr;
    canvas.height = canvas.clientHeight * dpr;
  }

  /* ── Simulation loop ── */
  let lastTime = performance.now();
  let frameId = 0;

  function step() {
    const now = performance.now();
    const dt = Math.min((now - lastTime) / 1000, 0.016);
    lastTime = now;

    if (prefersReduced) {
      use(prog.display);
      gl.uniform1i(prog.display.uniforms.uDye, 0);
      gl.uniform1f(prog.display.uniforms.uDark, darkMode);
      bindTex(0, dye.read.texture);
      blit(null);
      return;
    }

    /* Input — compute delta from last processed position to capture full
     * inter-frame movement; cap velocity to stay within half-float range */
    if (pointer.active && pointer.prevX >= 0) {
      const dx = (pointer.x - pointer.prevX) * canvas.clientWidth * 10;
      const dy = (pointer.y - pointer.prevY) * canvas.clientHeight * 10;
      pointer.prevX = pointer.x;
      pointer.prevY = pointer.y;
      if (Math.abs(dx) > 0.1 || Math.abs(dy) > 0.1) {
        const vx = Math.max(-20000, Math.min(20000, dx * SPLAT_FORCE));
        const vy = Math.max(-20000, Math.min(20000, dy * SPLAT_FORCE));
        splat(pointer.x, pointer.y, vx, vy, SPLAT_RADIUS);
      }
    } else if (pointer.active) {
      pointer.prevX = pointer.x;
      pointer.prevY = pointer.y;
    }

    /* Ambient */
    ambientTimer += dt;
    if (ambientTimer >= nextAmbientAt) {
      ambientTimer = 0;
      nextAmbientAt = 0.7 + Math.random() * 0.6;
      edgeSplat();
    }

    /* Advect velocity */
    use(prog.advection);
    gl.uniform2fv(prog.advection.uniforms.texelSize, SIM_TEXEL);
    gl.uniform1i(prog.advection.uniforms.uVelocity, 0);
    gl.uniform1i(prog.advection.uniforms.uSource, 0);
    gl.uniform1f(prog.advection.uniforms.dt, dt);
    gl.uniform1f(prog.advection.uniforms.dissipation, VEL_DISSIPATION);
    bindTex(0, velocity.read.texture);
    blit(velocity.write);
    velocity.swap();

    /* Advect dye — uses SIM_TEXEL because velocity is in SIM-grid units */
    use(prog.advection);
    gl.uniform2fv(prog.advection.uniforms.texelSize, SIM_TEXEL);
    gl.uniform1i(prog.advection.uniforms.uSource, 1);
    gl.uniform1f(prog.advection.uniforms.dissipation, DYE_DISSIPATION);
    bindTex(0, velocity.read.texture);
    bindTex(1, dye.read.texture);
    blit(dye.write);
    dye.swap();

    /* Divergence */
    use(prog.divergence);
    gl.uniform2fv(prog.divergence.uniforms.texelSize, SIM_TEXEL);
    gl.uniform1i(prog.divergence.uniforms.uVelocity, 0);
    bindTex(0, velocity.read.texture);
    blit(divergence);

    /* Clear pressure */
    use(prog.clear);
    gl.uniform1i(prog.clear.uniforms.uTexture, 0);
    gl.uniform1f(prog.clear.uniforms.value, PRESS_DISSIPATION);
    bindTex(0, pressure.read.texture);
    blit(pressure.write);
    pressure.swap();

    /* Pressure solve (Jacobi) */
    use(prog.pressure);
    gl.uniform2fv(prog.pressure.uniforms.texelSize, SIM_TEXEL);
    gl.uniform1i(prog.pressure.uniforms.uDivergence, 1);
    bindTex(1, divergence.texture);
    for (let i = 0; i < JACOBI_ITERS; i++) {
      gl.uniform1i(prog.pressure.uniforms.uPressure, 0);
      bindTex(0, pressure.read.texture);
      blit(pressure.write);
      pressure.swap();
    }

    /* Gradient subtraction */
    use(prog.gradSub);
    gl.uniform2fv(prog.gradSub.uniforms.texelSize, SIM_TEXEL);
    gl.uniform1i(prog.gradSub.uniforms.uPressure, 0);
    gl.uniform1i(prog.gradSub.uniforms.uVelocity, 1);
    bindTex(0, pressure.read.texture);
    bindTex(1, velocity.read.texture);
    blit(velocity.write);
    velocity.swap();

    /* Display */
    use(prog.display);
    gl.uniform1i(prog.display.uniforms.uDye, 0);
    gl.uniform1f(prog.display.uniforms.uDark, darkMode);
    bindTex(0, dye.read.texture);
    blit(null);

    frameId = requestAnimationFrame(step);
  }

  window.addEventListener("resize", resize);
  resize();
  gl.bindVertexArray(quadVAO);

  /* Seed initial wisps at edges */
  [
    [-0.3, 0.04, 0.85],
    [2.6, 0.96, 0.8],
    [0.8, 0.06, 0.18],
    [2.0, 0.93, 0.12],
    [1.2, 0.2, 0.02],
    [4.2, 0.8, 0.98],
    [1.5, 0.5, 0.02],
    [0.0, 0.02, 0.5],
  ].forEach(([angle, x, y]) => {
    const speed = 900 + Math.random() * 500;
    splat(x, y, Math.cos(angle) * speed, Math.sin(angle) * speed, 0.003);
  });

  step();

  /* ── Cleanup ── */
  return () => {
    cancelAnimationFrame(frameId);
    themeObserver.disconnect();
    window.removeEventListener("resize", resize);
    container.removeEventListener("mouseenter", onMouseEnter);
    container.removeEventListener("mousemove", onMouseMove);
    container.removeEventListener("touchstart", onTouchStart);
    container.removeEventListener("touchmove", onTouchMove);
  };
}
