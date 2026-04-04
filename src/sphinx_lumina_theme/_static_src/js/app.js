import Alpine from "alpinejs";
import scrollspy from "./scrollspy.js";
import themeToggle from "./theme-toggle.js";
import searchModal from "./search.js";
import sidebar from "./sidebar.js";
import headerLinks from "./header-links.js";
import copyPage from "./copy-page.js";
import navDropdown from "./nav-dropdown.js";
import curlCopy from "./curl-copy.js";
Alpine.data("scrollspy", scrollspy);
Alpine.data("themeToggle", themeToggle);
Alpine.data("searchModal", searchModal);
Alpine.data("sidebar", sidebar);
Alpine.data("headerLinks", headerLinks);
Alpine.data("copyPage", copyPage);
Alpine.data("navDropdown", navDropdown);

window.Alpine = Alpine;

/* ── Wait for DOM before starting Alpine and post-init modules ── */
function boot() {
  Alpine.start();
  curlCopy();
}

if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", boot);
} else {
  boot();
}

/* ── Easter egg for fellow developers ── */
console.log(
  "%c✦ Lumina Theme %c\nCrafted for clarity. Built on Sphinx.\nhttps://github.com/r4sky0/sphinx-lumina-theme",
  "color: #10b981; font-size: 14px; font-weight: bold;",
  "color: inherit; font-size: 12px;"
);
