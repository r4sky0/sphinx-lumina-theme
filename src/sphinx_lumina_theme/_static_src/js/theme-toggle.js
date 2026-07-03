/**
 * @module theme-toggle
 * @description Alpine.js component for cycling between light, dark, and auto
 * color schemes. Persists the user's preference in ``localStorage``
 * (key ``lumina-theme``) and listens for system-level
 * ``prefers-color-scheme`` changes when set to auto.
 */

/**
 * Factory for the theme-toggle Alpine component.
 * Registered as ``Alpine.data("themeToggle", themeToggle)``.
 *
 * **Properties:**
 *
 * - ``mode`` *(string)* — Current mode: ``"auto"``, ``"light"``, or ``"dark"``.
 *
 * **Methods:**
 *
 * - ``init()`` — Reads stored preference, applies the theme, and listens for OS changes.
 * - ``cycle()`` — Advances the mode: auto → light → dark → auto.
 * - ``apply()`` — Applies the effective theme to ``document.documentElement``.
 *
 * @function themeToggle
 * @returns {object} Alpine.js component data.
 */
export default function themeToggle() {
  return {
    mode: "auto",

    init() {
      let stored = null;
      try {
        stored = localStorage.getItem("lumina-theme");
      } catch {
        /* localStorage unavailable (e.g. disabled site data) — fall back to auto */
      }
      if (stored === "light" || stored === "dark") {
        this.mode = stored;
      } else {
        this.mode = "auto";
      }
      this.apply();

      window
        .matchMedia("(prefers-color-scheme: dark)")
        .addEventListener("change", () => {
          if (this.mode === "auto") this.apply();
        });
    },

    cycle() {
      // Enable smooth color transition for deliberate toggle
      const root = document.documentElement;
      root.classList.add("lumina-transitioning");

      if (this.mode === "auto") {
        this.mode = "light";
      } else if (this.mode === "light") {
        this.mode = "dark";
      } else {
        this.mode = "auto";
      }
      this.apply();

      // Remove transition class after animation completes
      setTimeout(() => root.classList.remove("lumina-transitioning"), 500);
    },

    apply() {
      let effectiveTheme;
      // ``dark_mode_default`` (exposed by layout.html as data-theme-default)
      // overrides the OS preference until the reader picks an explicit theme.
      const configured =
        document.documentElement.getAttribute("data-theme-default");
      const forced = configured === "light" || configured === "dark";

      if (this.mode === "auto") {
        if (forced) {
          effectiveTheme = configured;
        } else {
          effectiveTheme = window.matchMedia("(prefers-color-scheme: dark)")
            .matches
            ? "dark"
            : "light";
        }
      } else {
        effectiveTheme = this.mode;
      }

      // Apply the visual change first — persistence is best-effort and
      // must not block the actual theme switch if storage throws (private
      // browsing, disabled site data, quota exceeded).
      document.documentElement.setAttribute("data-theme", effectiveTheme);
      try {
        if (this.mode === "auto") {
          localStorage.removeItem("lumina-theme");
        } else {
          localStorage.setItem("lumina-theme", this.mode);
        }
      } catch {
        /* ignore — theme still applied for this page view */
      }

      // Sphinx gates the dark highlight stylesheet on the OS color scheme
      // only, so a manual override — or a forced ``dark_mode_default`` that
      // disagrees with the OS setting — must rewrite its media query,
      // otherwise code blocks keep the other mode's Pygments palette.
      const pygmentsDark = document.getElementById("pygments_dark_css");
      if (pygmentsDark) {
        if (this.mode === "auto" && !forced) {
          pygmentsDark.media = "(prefers-color-scheme: dark)";
        } else {
          pygmentsDark.media = effectiveTheme === "dark" ? "screen" : "not all";
        }
      }
    },
  };
}
