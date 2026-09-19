/**
 * GPU Fluid Simulation — Lumina landing page hero background.
 *
 * Implements Jos Stam's Stable Fluids on WebGL2 with ping-pong framebuffers.
 * Supports light/dark mode via a theme-aware display shader.
 *
 * The simulation runs in a Web Worker via OffscreenCanvas to keep the main
 * thread free.  Browsers without OffscreenCanvas fall back to main-thread
 * rendering.
 *
 * Exported as an Alpine.js component: attach with x-data="fluidSimulation()"
 * and provide a <canvas x-ref="canvas"> inside the element.
 */

// Capture script URL at load time so we can resolve the worker path later.
// This file is NOT part of the shipped theme — it's docs-only.
const _scriptSrc = document.currentScript && document.currentScript.src;

document.addEventListener("alpine:init", () => {
  window.Alpine.data("fluidSimulation", () => ({
    _worker: null,
    _cleanup: null,
    _workerCleanup: null,
    _observer: null,
    _idleId: null,
    _timerId: null,

    init() {
      const canvas = this.$refs.canvas;
      const container = this.$el;
      const isMobile = window.innerWidth < 768;
      const opts = isMobile
        ? { sim: 128, dye: 256, jacobi: 20 }
        : { sim: 256, dye: 512, jacobi: 30 };

      const start = () => {
        // Try OffscreenCanvas + Worker (moves all GPU work off main thread)
        if (typeof OffscreenCanvas !== "undefined" && _scriptSrc) {
          try {
            this._startWorker(canvas, container, opts);
            return;
          } catch (_) {
            /* fall through to main-thread path */
          }
        }
        // Fallback: run on main thread
        this._cleanup = startFluid(canvas, container, opts);
      };

      // Defer heavy GPU init to avoid blocking initial page render.
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

    _startWorker(canvas, container, opts) {
      const workerUrl = _scriptSrc.replace(
        "fluid-simulation.js",
        "fluid-worker.js",
      );
      const offscreen = canvas.transferControlToOffscreen();
      const worker = new Worker(workerUrl);

      worker.postMessage(
        {
          type: "init",
          canvas: offscreen,
          w: canvas.clientWidth,
          h: canvas.clientHeight,
          dpr: Math.min(window.devicePixelRatio || 1, 2),
          dark:
            document.documentElement.getAttribute("data-theme") === "dark",
          reduced: window.matchMedia("(prefers-reduced-motion: reduce)")
            .matches,
          ...opts,
        },
        [offscreen],
      );

      /* Forward pointer events to the worker — rAF-gated to send at most
         one message per display frame regardless of input event frequency. */
      const cw = () => canvas.clientWidth;
      const ch = () => canvas.clientHeight;
      let pendingEnter = null;
      let pendingPointer = null;
      let sendScheduled = false;

      function flushPointer() {
        sendScheduled = false;
        if (pendingEnter) {
          worker.postMessage({ type: "pointerenter", ...pendingEnter });
          pendingEnter = null;
        }
        if (pendingPointer) {
          worker.postMessage({ type: "pointer", ...pendingPointer });
          pendingPointer = null;
        }
      }

      function scheduleFlush() {
        if (!sendScheduled) {
          sendScheduled = true;
          requestAnimationFrame(flushPointer);
        }
      }

      const onMouseEnter = (e) => {
        pendingEnter = { x: e.clientX / cw(), y: 1.0 - e.clientY / ch() };
        scheduleFlush();
      };
      const onMouseMove = (e) => {
        pendingPointer = { x: e.clientX / cw(), y: 1.0 - e.clientY / ch() };
        scheduleFlush();
      };
      const onTouchStart = (e) => {
        const t = e.touches[0];
        pendingEnter = { x: t.clientX / cw(), y: 1.0 - t.clientY / ch() };
        scheduleFlush();
      };
      const onTouchMove = (e) => {
        const t = e.touches[0];
        pendingPointer = { x: t.clientX / cw(), y: 1.0 - t.clientY / ch() };
        scheduleFlush();
      };

      container.addEventListener("mouseenter", onMouseEnter);
      container.addEventListener("mousemove", onMouseMove);
      container.addEventListener("touchstart", onTouchStart, {
        passive: true,
      });
      container.addEventListener("touchmove", onTouchMove, {
        passive: true,
      });

      /* Forward theme changes */
      const themeObs = new MutationObserver(() =>
        worker.postMessage({
          type: "theme",
          dark:
            document.documentElement.getAttribute("data-theme") === "dark",
        }),
      );
      themeObs.observe(document.documentElement, {
        attributes: true,
        attributeFilter: ["data-theme"],
      });

      /* Forward resize */
      const onResize = () =>
        worker.postMessage({
          type: "resize",
          w: canvas.clientWidth,
          h: canvas.clientHeight,
          dpr: Math.min(window.devicePixelRatio || 1, 2),
        });
      window.addEventListener("resize", onResize);

      this._worker = worker;
      this._workerCleanup = () => {
        worker.postMessage({ type: "stop" });
        worker.terminate();
        themeObs.disconnect();
        window.removeEventListener("resize", onResize);
        container.removeEventListener("mouseenter", onMouseEnter);
        container.removeEventListener("mousemove", onMouseMove);
        container.removeEventListener("touchstart", onTouchStart);
        container.removeEventListener("touchmove", onTouchMove);
      };
    },

    destroy() {
      if (this._idleId) cancelIdleCallback(this._idleId);
      if (this._timerId) clearTimeout(this._timerId);
      if (this._workerCleanup) this._workerCleanup();
      if (this._cleanup) this._cleanup();
      if (this._observer) this._observer.disconnect();
      document.documentElement.removeAttribute("data-hero-visible");
    },
  }));
});

/* Main-thread fallback uses the same engine as the worker. */
function startFluid(canvas, container, opts = {}) {
  const send = window.luminaFluidMessage;
  if (!send) return () => {};

  send({
    type: "init",
    canvas,
    w: canvas.clientWidth,
    h: canvas.clientHeight,
    dpr: Math.min(window.devicePixelRatio || 1, 2),
    dark: document.documentElement.getAttribute("data-theme") === "dark",
    reduced: window.matchMedia("(prefers-reduced-motion: reduce)").matches,
    ...opts,
  });

  const point = (type, x, y) => send({
    type,
    x: x / canvas.clientWidth,
    y: 1 - y / canvas.clientHeight,
  });
  const onMouseEnter = (e) => point("pointerenter", e.clientX, e.clientY);
  const onMouseMove = (e) => point("pointer", e.clientX, e.clientY);
  const onTouchStart = (e) => point("pointerenter", e.touches[0].clientX, e.touches[0].clientY);
  const onTouchMove = (e) => point("pointer", e.touches[0].clientX, e.touches[0].clientY);
  const onResize = () => send({
    type: "resize",
    w: canvas.clientWidth,
    h: canvas.clientHeight,
    dpr: Math.min(window.devicePixelRatio || 1, 2),
  });
  const themeObserver = new MutationObserver(() => send({
    type: "theme",
    dark: document.documentElement.getAttribute("data-theme") === "dark",
  }));

  container.addEventListener("mouseenter", onMouseEnter);
  container.addEventListener("mousemove", onMouseMove);
  container.addEventListener("touchstart", onTouchStart, { passive: true });
  container.addEventListener("touchmove", onTouchMove, { passive: true });
  window.addEventListener("resize", onResize);
  themeObserver.observe(document.documentElement, {
    attributes: true,
    attributeFilter: ["data-theme"],
  });

  return () => {
    send({ type: "stop" });
    themeObserver.disconnect();
    window.removeEventListener("resize", onResize);
    container.removeEventListener("mouseenter", onMouseEnter);
    container.removeEventListener("mousemove", onMouseMove);
    container.removeEventListener("touchstart", onTouchStart);
    container.removeEventListener("touchmove", onTouchMove);
  };
}
