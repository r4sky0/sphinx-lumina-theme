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
      const stored = localStorage.getItem("lumina-theme");
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
      if (this.mode === "auto") {
        // ``dark_mode_default`` (exposed by layout.html as data-theme-default)
        // overrides the OS preference until the reader picks an explicit theme.
        const configured =
          document.documentElement.getAttribute("data-theme-default");
        if (configured === "light" || configured === "dark") {
          effectiveTheme = configured;
        } else {
          effectiveTheme = window.matchMedia("(prefers-color-scheme: dark)")
            .matches
            ? "dark"
            : "light";
        }
        localStorage.removeItem("lumina-theme");
      } else {
        effectiveTheme = this.mode;
        localStorage.setItem("lumina-theme", this.mode);
      }
      document.documentElement.setAttribute("data-theme", effectiveTheme);
    },
  };
}
