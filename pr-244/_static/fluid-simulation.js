/**
 * GPU Fluid Simulation — Lumina landing page hero background.
 *
 * Implements Jos Stam's Stable Fluids on WebGL2 with ping-pong framebuffers.
 * Supports light/dark mode via a theme-aware display shader.
 *
 * The simulation runs in a Web Worker via OffscreenCanvas to keep the main
 * thread free. Unsupported browsers show the normal themed background.
 *
 * Exported as an Alpine.js component: attach with x-data="fluidSimulation()"
 * and provide a <canvas x-ref="canvas"> inside the element.
 */

// Capture script URL at load time so we can resolve the worker path later.
// This file is NOT part of the shipped theme — it's docs-only.
const _scriptSrc = document.currentScript && document.currentScript.src;

// Canvas pixels per CSS pixel. The dye is soft, so extra pixels only cost GPU time.
const RENDER_SCALE = 0.5;

document.addEventListener("alpine:init", () => {
  window.Alpine.data("fluidSimulation", () => ({
    _worker: null,
    _workerCleanup: null,
    _idleId: null,
    _timerId: null,

    init() {
      const canvas = this.$refs.canvas;
      const container = this.$el;
      const isMobile = window.innerWidth < 768;
      const opts = isMobile
        ? { sim: 96, dye: 256, jacobi: 10 }
        : { sim: 128, dye: 384, jacobi: 12 };

      const start = () => {
        if (!_scriptSrc || !canvas.transferControlToOffscreen) return;
        try {
          this._startWorker(canvas, container, opts);
        } catch (_) {
          canvas.hidden = true;
        }
      };

      // Defer heavy GPU init to avoid blocking initial page render.
      if ("requestIdleCallback" in window) {
        this._idleId = requestIdleCallback(start, { timeout: 2000 });
      } else {
        this._timerId = setTimeout(start, 100);
      }
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
          scale: RENDER_SCALE,
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
      const toUv = ({ clientX, clientY }) => {
        const rect = canvas.getBoundingClientRect();
        return {
          x: (clientX - rect.left) / rect.width,
          y: 1.0 - (clientY - rect.top) / rect.height,
        };
      };
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
        pendingEnter = toUv(e);
        scheduleFlush();
      };
      const onMouseMove = (e) => {
        pendingPointer = toUv(e);
        scheduleFlush();
      };
      const onTouchStart = (e) => {
        pendingEnter = toUv(e.touches[0]);
        scheduleFlush();
      };
      const onTouchMove = (e) => {
        pendingPointer = toUv(e.touches[0]);
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
          scale: RENDER_SCALE,
        });
      window.addEventListener("resize", onResize);

      this._worker = worker;
      this._workerCleanup = () => {
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
    },
  }));
});
