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
        effectiveTheme = window.matchMedia("(prefers-color-scheme: dark)").matches
          ? "dark"
          : "light";
        localStorage.removeItem("lumina-theme");
      } else {
        effectiveTheme = this.mode;
        localStorage.setItem("lumina-theme", this.mode);
      }
      document.documentElement.setAttribute("data-theme", effectiveTheme);
    },
  };
}
