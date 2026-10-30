/**
 * Web Worker for GPU Fluid Simulation.
 *
 * Receives an OffscreenCanvas via postMessage and runs the entire Stable Fluids
 * simulation off the main thread.  The main thread only forwards lightweight
 * pointer / theme / resize events.
 */

/* ── Shared state updated by messages ── */
let canvas, gl;
let cw = 0,
  ch = 0;
let darkMode = 0;
let prefersReduced = false;
let redraw = null; /* set under reduced motion, when no loop repaints the canvas */
/* x/y ease toward the cursor so strokes stay continuous between input events */
const pointer = { x: 0, y: 0, targetX: 0, targetY: 0, active: false };

/* ── Message handler ── */
self.onmessage = (e) => {
  const d = e.data;
  switch (d.type) {
    case "init":
      init(d);
      break;
    case "pointerenter":
      pointer.active = false;
    /* fall through */
    case "pointer":
      /* Snap on first contact, or a tap reads as a stroke from the last tap */
      if (!pointer.active) {
        pointer.x = d.x;
        pointer.y = d.y;
        pointer.active = true;
      }
      pointer.targetX = d.x;
      pointer.targetY = d.y;
      break;
    case "theme":
      darkMode = d.dark ? 1.0 : 0.0;
      redraw?.();
      break;
    case "resize":
      cw = d.w;
      ch = d.h;
      if (canvas) {
        canvas.width = d.w * d.scale;
        canvas.height = d.h * d.scale;
      }
      redraw?.();
      break;
  }
};

/* ── Simulation ── */
function init(cfg) {
  canvas = cfg.canvas;
  cw = cfg.w;
  ch = cfg.h;
  darkMode = cfg.dark ? 1.0 : 0.0;
  prefersReduced = cfg.reduced;

  canvas.width = cw * cfg.scale;
  canvas.height = ch * cfg.scale;

  gl = canvas.getContext("webgl2", {
    alpha: true,
    premultipliedAlpha: false,
    antialias: false,
    depth: false,
    stencil: false,
    powerPreference: "low-power",
  });
  if (!gl || !gl.getExtension("EXT_color_buffer_float")) return;

  /* Square texels keep the flow isotropic; each grid keeps its texel budget.
     shortcut: sized once, so a later aspect change stretches the flow; rebuild the FBOs on resize if that shows. */
  function gridSize(base) {
    const scale = Math.sqrt(cw / ch);
    return [Math.round(base * scale), Math.round(base / scale)];
  }

  const [simW, simH] = gridSize(cfg.sim);
  const [dyeW, dyeH] = gridSize(cfg.dye);
  const JACOBI_ITERS = cfg.jacobi;
  /* Velocity is in texels/s; forces below are tuned for a 256 grid */
  const VELOCITY_SCALE = cfg.sim / 256;
  const VEL_DISSIPATION = 0.985;
  const DYE_DISSIPATION = 0.978;
  const PRESS_DISSIPATION = 0.8;
  const SPLAT_RADIUS = 0.006;
  const POINTER_EASE = 0.25;
  const POINTER_FORCE = 36; /* velocity per px moved in a frame */
  const POINTER_MAX_FORCE = 2000;
  const POINTER_DYE = 0.35;
  const POINTER_DYE_SPEED = 24; /* px per frame that deposits the full POINTER_DYE */
  const AMBIENT_FRAMES = 24;
  const AMBIENT_DYE = 1.6; /* total per wisp */
  const FRAME_MS = 1000 / 60;
  const SETTLE_FRAMES = 45;
  const SIM_TEXEL = new Float32Array([1 / simW, 1 / simH]);

  const DYE_COLORS = [
    [0.06, 0.5, 0.28],
    [0.1, 0.55, 0.35],
    [0.07, 0.45, 0.4],
    [0.11, 0.58, 0.32],
    [0.05, 0.4, 0.33],
  ];

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
    uniform float aspectRatio;
    uniform vec3 color;
    uniform vec2 point;
    uniform float radius;
    void main() {
      vec2 p = vUv - point;
      p.x *= aspectRatio;
      fragColor = vec4(exp(-dot(p,p) / radius) * color, 0.0);
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
    simW,
    simH,
    gl.RG16F,
    gl.RG,
    gl.HALF_FLOAT,
    gl.LINEAR,
  );
  const pressure = createDoubleFBO(
    simW,
    simH,
    gl.R16F,
    gl.RED,
    gl.HALF_FLOAT,
    gl.LINEAR,
  );
  const divergenceFBO = createFBO(
    simW,
    simH,
    gl.R16F,
    gl.RED,
    gl.HALF_FLOAT,
    gl.NEAREST,
  );
  const dye = createDoubleFBO(
    dyeW,
    dyeH,
    gl.RGBA16F,
    gl.RGBA,
    gl.HALF_FLOAT,
    gl.LINEAR,
  );

  /* ── Splat ── */
  function splat(x, y, dx, dy, radius, dyeAmount = 1) {
    const u = prog.splat.uniforms;
    const aspect = cw / ch;
    const reach = 2.5 * Math.sqrt(radius); /* where the gaussian falls below 0.2% */
    /* Blended in place and scissored, so a splat costs its footprint, not the grid */
    const stamp = (target) => {
      gl.scissor(
        (x - reach / aspect) * target.width,
        (y - reach) * target.height,
        ((2 * reach) / aspect) * target.width + 1,
        2 * reach * target.height + 1,
      );
      blit(target);
    };

    use(prog.splat);
    gl.enable(gl.BLEND);
    gl.enable(gl.SCISSOR_TEST);
    gl.uniform1f(u.aspectRatio, aspect);
    gl.uniform2f(u.point, x, y);
    gl.uniform1f(u.radius, radius);

    gl.uniform3f(u.color, dx * VELOCITY_SCALE, dy * VELOCITY_SCALE, 0);
    stamp(velocity.read);

    const c = DYE_COLORS[(Math.random() * DYE_COLORS.length) | 0];
    gl.uniform3f(
      u.color,
      c[0] * dyeAmount,
      c[1] * dyeAmount,
      c[2] * dyeAmount,
    );
    stamp(dye.read);

    gl.disable(gl.SCISSOR_TEST);
    gl.disable(gl.BLEND);
  }

  /* ── Ambient edge splats ── */
  let nextAmbientAt = 0.7 + Math.random() * 0.6;
  let ambientTimer = 0;
  let ambient = null;

  /* Starts a wisp that fades in over AMBIENT_FRAMES instead of popping in */
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
    ambient = {
      x,
      y,
      dx: (Math.cos(angle) * speed) / AMBIENT_FRAMES,
      dy: (Math.sin(angle) * speed) / AMBIENT_FRAMES,
      radius: 0.005 + Math.random() * 0.003,
      framesLeft: AMBIENT_FRAMES,
    };
  }

  /* ── Simulation loop ── */
  let lastTime = performance.now();

  function draw() {
    use(prog.display);
    gl.uniform1i(prog.display.uniforms.uDye, 0);
    gl.uniform1f(prog.display.uniforms.uDark, darkMode);
    bindTex(0, dye.read.texture);
    blit(null);
  }

  function advance(dt) {
    /* Input */
    if (pointer.active) {
      const moveX = (pointer.targetX - pointer.x) * POINTER_EASE;
      const moveY = (pointer.targetY - pointer.y) * POINTER_EASE;
      pointer.x += moveX;
      pointer.y += moveY;
      const pxX = moveX * cw;
      const pxY = moveY * ch;
      const speed = Math.hypot(pxX, pxY);
      if (speed > 0.25) {
        const force = Math.min(POINTER_MAX_FORCE, speed * POINTER_FORCE);
        splat(
          pointer.x,
          pointer.y,
          (pxX / speed) * force,
          (pxY / speed) * force,
          SPLAT_RADIUS,
          /* Dye follows speed, so small movements never stamp a full blob */
          POINTER_DYE * Math.min(1, speed / POINTER_DYE_SPEED),
        );
      }
    }

    /* Ambient */
    ambientTimer += dt;
    if (ambientTimer >= nextAmbientAt) {
      ambientTimer = 0;
      nextAmbientAt = 0.7 + Math.random() * 0.6;
      edgeSplat();
    }
    if (ambient) {
      splat(
        ambient.x,
        ambient.y,
        ambient.dx,
        ambient.dy,
        ambient.radius,
        AMBIENT_DYE / AMBIENT_FRAMES,
      );
      if (--ambient.framesLeft === 0) ambient = null;
    }

    /* Advect velocity */
    use(prog.advection);
    gl.uniform2fv(prog.advection.uniforms.texelSize, SIM_TEXEL);
    gl.uniform1i(prog.advection.uniforms.uVelocity, 0);
    gl.uniform1i(prog.advection.uniforms.uSource, 0);
    gl.uniform1f(prog.advection.uniforms.dt, dt);
    /* Tuned per 60Hz frame; scale by dt so 120Hz displays fade at the same speed */
    gl.uniform1f(
      prog.advection.uniforms.dissipation,
      VEL_DISSIPATION ** (dt * 60),
    );
    bindTex(0, velocity.read.texture);
    blit(velocity.write);
    velocity.swap();

    /* Advect dye */
    gl.uniform1i(prog.advection.uniforms.uSource, 1);
    gl.uniform1f(
      prog.advection.uniforms.dissipation,
      DYE_DISSIPATION ** (dt * 60),
    );
    bindTex(0, velocity.read.texture);
    bindTex(1, dye.read.texture);
    blit(dye.write);
    dye.swap();

    /* Divergence */
    use(prog.divergence);
    gl.uniform2fv(prog.divergence.uniforms.texelSize, SIM_TEXEL);
    gl.uniform1i(prog.divergence.uniforms.uVelocity, 0);
    bindTex(0, velocity.read.texture);
    blit(divergenceFBO);

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
    bindTex(1, divergenceFBO.texture);
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
  }

  function step() {
    requestAnimationFrame(step);
    const now = performance.now();
    /* Cap at 60fps; high refresh displays gain nothing on a soft background.
       The margin keeps a 60Hz display from skipping frames on timer jitter. */
    if (now - lastTime < FRAME_MS - 2) return;
    const dt = Math.min((now - lastTime) / 1000, 0.016);
    lastTime = now;

    advance(dt);
    draw();
  }

  gl.bindVertexArray(quadVAO);
  gl.blendFunc(gl.ONE, gl.ONE);

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

  if (prefersReduced) {
    /* Hold one still frame, after letting the seeds flow into wisps */
    for (let i = 0; i < SETTLE_FRAMES; i++) advance(1 / 60);
    redraw = draw;
    draw();
  } else {
    step();
  }
}
