/**
 * @module app
 * @description Entry point for the Lumina theme's client-side interactivity.
 * Imports all Alpine.js component modules, registers them via
 * ``Alpine.data()``, and starts Alpine once the DOM is ready.
 * Also calls boot functions for modules that inject elements
 * post-render (curlCopy, tryIt).
 */

import Alpine from "alpinejs";
import scrollspy from "./scrollspy.js";
import themeToggle from "./theme-toggle.js";
import searchModal from "./search.js";
import sidebar from "./sidebar.js";
import sidebarNav from "./sidebar-nav.js";
import headerLinks from "./header-links.js";
import copyPage from "./copy-page.js";
import navDropdown from "./nav-dropdown.js";
import curlCopy, { curlCopyBtn } from "./curl-copy.js";
import tryIt, { tryItPanel } from "./try-it.js";
import backToTop from "./back-to-top.js";
import announcementBanner from "./announcement.js";
import versionSwitcher from "./version-switcher.js";
import layoutToggle from "./layout-toggle.js";
import iconBrowser from "./icon-browser.js";
import codeWrapToggle from "./code-wrap.js";
Alpine.data("scrollspy", scrollspy);
Alpine.data("themeToggle", themeToggle);
Alpine.data("searchModal", searchModal);
Alpine.data("sidebar", sidebar);
Alpine.data("sidebarNav", sidebarNav);
Alpine.data("headerLinks", headerLinks);
Alpine.data("copyPage", copyPage);
Alpine.data("navDropdown", navDropdown);
Alpine.data("curlCopyBtn", curlCopyBtn);
Alpine.data("tryItPanel", tryItPanel);
Alpine.data("backToTop", backToTop);
Alpine.data("announcementBanner", announcementBanner);
Alpine.data("versionSwitcher", versionSwitcher);
Alpine.data("layoutToggle", layoutToggle);
Alpine.data("iconBrowser", iconBrowser);

window.Alpine = Alpine;

/* ── Wait for DOM before starting Alpine and post-init modules ── */

/**
 * Initializes the theme by starting Alpine.js and running post-render
 * boot functions (curlCopy, tryIt). Called on DOMContentLoaded or
 * immediately if the DOM is already ready.
 *
 * @function boot
 */
function boot() {
  Alpine.start();
  curlCopy();
  tryIt();
  codeWrapToggle();
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
