# JavaScript API

Auto-generated reference for the theme’s Alpine.js components. Each component is a factory function registered via `Alpine.data()` in [the entry point]() and referenced in Jinja2 templates with `x-data`.

## Entry Point

### boot()

Initializes the theme by starting Alpine.js and running post-render
boot functions (curlCopy, tryIt). Called on DOMContentLoaded or
immediately if the DOM is already ready.

## Navigation

### scrollspy()

Factory for the scrollspy Alpine component.
Registered as `Alpine.data("scrollspy", scrollspy)`.

**Properties:**

- `activeId`  *(string|null)* — The `id` of the currently visible section.
- `observer`  *(IntersectionObserver|null)* — The observer instance.

**Methods:**

- `init()` — Collects TOC link targets and starts observing.
- `updateActive(nav)` — Toggles the `lumina-toc-active` class on TOC links.
- `destroy()` — Disconnects the IntersectionObserver.

* **Returns:**
  **object** – Alpine.js component data.

### sidebar()

Factory for the sidebar Alpine component.
Registered as `Alpine.data("sidebar", sidebar)`.

**Properties:**

- `mobileOpen`  *(boolean)* — Whether the mobile sidebar is visible.

**Methods:**

- `toggle()` — Toggles the sidebar and locks/unlocks body scroll.
- `close()` — Closes the sidebar and restores focus.
- `init()` — Attaches toggle button handlers and a media-query listener.

* **Returns:**
  **object** – Alpine.js component data.

### navDropdown()

Factory for the nav-dropdown Alpine component.
Registered as `Alpine.data("navDropdown", navDropdown)`.

**Properties:**

- `open`  *(boolean)* — Whether the dropdown is visible.

**Methods:**

- `toggle()` — Toggles the dropdown open/closed.
- `show()` — Opens the dropdown, cancelling any pending hide timer.
- `hide()` — Closes the dropdown after a 150 ms delay.
- `cancelHide()` — Cancels a pending hide (e.g. when re-entering the dropdown).
- `handleKeydown(e)` — Closes on Escape and returns focus to the trigger.

* **Returns:**
  **object** – Alpine.js component data.

### versionSwitcher()

Factory for the version-switcher Alpine component.
Registered as `Alpine.data("versionSwitcher", versionSwitcher)`.

**Properties:**

- `open`  *(boolean)* — Whether the version dropdown is visible.
- `versions`  *(Array)* — Fetched array of `{ version, name, url }` objects.
- `currentLabel`  *(string)* — Display label for the active version.
- `error`  *(boolean)* — Whether version fetching failed.

**Methods:**

- `init()` — Reads config attributes and fetches the version manifest.
- `toggle()` — Toggles the dropdown open/closed.

* **Returns:**
  **object** – Alpine.js component data.

## UI Controls

### themeToggle()

Factory for the theme-toggle Alpine component.
Registered as `Alpine.data("themeToggle", themeToggle)`.

**Properties:**

- `mode`  *(string)* — Current mode: `"auto"`, `"light"`, or `"dark"`.

**Methods:**

- `init()` — Reads stored preference, applies the theme, and listens for OS changes.
- `cycle()` — Advances the mode: auto → light → dark → auto.
- `apply()` — Applies the effective theme to `document.documentElement`.

* **Returns:**
  **object** – Alpine.js component data.

### searchModal()

Factory for the search modal Alpine component.
Registered as `Alpine.data("searchModal", searchModal)`.

**Properties:**

- `open`  *(boolean)* — Whether the modal is visible.
- `query`  *(string)* — Current search input value.
- `results`  *(Array)* — Array of search result objects.
- `selectedIndex`  *(number)* — Index of the keyboard-highlighted result.
- `loaded`  *(boolean)* — Whether the search engine has been initialized.
- `error`  *(string|null)* — Error message, if search initialization failed.
- `backend`  *(string)* — Search backend: `"pagefind"` or `"sphinx"`.

**Methods:**

- `init()` — Sets up keyboard shortcuts and trigger buttons.
- `toggle()` — Opens or closes the modal.
- `openModal()` — Opens the modal, loads the search engine on first use.
- `close()` — Closes the modal and restores focus.
- `search()` — Runs a search query and populates results.
- `moveDown()` — Moves keyboard selection down.
- `moveUp()` — Moves keyboard selection up.
- `goToSelected()` — Navigates to the selected result.

* **Returns:**
  **object** – Alpine.js component data.

### backToTop()

Factory for the back-to-top Alpine component.
Registered as `Alpine.data("backToTop", backToTop)`.

**Properties:**

- `visible`  *(boolean)* — Whether the button is currently shown.

**Methods:**

- `init()` — Attaches a passive scroll listener.
- `destroy()` — Removes the scroll listener.
- `scrollToTop()` — Scrolls the page to the top, respecting reduced-motion preference.

* **Returns:**
  **object** – Alpine.js component data.

### announcementBanner()

Factory for the announcement banner Alpine component.
Registered as `Alpine.data("announcementBanner", announcementBanner)`.

**Methods:**

- `init()` — Reads the announcement ID from `data-announcement-id`.
- `dismiss()` — Hides the banner and persists the dismissal in localStorage.

* **Returns:**
  **object** – Alpine.js component data.

## Content Utilities

### headerLinks()

Factory for the header-links Alpine component.
Registered as `Alpine.data("headerLinks", headerLinks)`.

**Methods:**

- `init()` — Attaches click handlers to all `.headerlink` elements.

* **Returns:**
  **object** – Alpine.js component data.

### copyPage()

Factory for the copy-page Alpine component.
Registered as `Alpine.data("copyPage", copyPage)`.

**Properties:**

- `copied`  *(boolean)* — Briefly `true` after a successful copy.

**Methods:**

- `copy()` — Converts the article to Markdown and copies it to the clipboard.

* **Returns:**
  **object** – Alpine.js component data.

## API Tools

### curlCopyBtn()

Alpine.js data factory for the per-endpoint copy-curl button.
Registered as `Alpine.data("curlCopyBtn", curlCopyBtn)`.

**Properties:**

- `copied`  *(boolean)* — Briefly `true` after a successful copy.

**Methods:**

- `copy()` — Copies the pre-built curl command to the clipboard.

* **Returns:**
  **object** – Alpine.js component data.

### curlCopy()

Boot function that scans the page for HTTP endpoints and injects
copy-curl buttons. Called from `boot()` in app.js after `Alpine.start()`.

### tryItPanel()

Alpine.js data factory for the interactive request panel.
Registered as `Alpine.data("tryItPanel", tryItPanel)`.

**Properties:**

- `open`  *(boolean)* — Whether the panel is expanded.
- `sending`  *(boolean)* — True while a request is in-flight.
- `response`  *(object|null)* — Last response (status, body, elapsed time).
- `method`  *(string)* — HTTP method (GET, POST, etc.).
- `path`  *(string)* — Endpoint path with `{param}` placeholders.
- `baseUrl`  *(string)* — API base URL from theme options.

**Methods:**

- `init()` — Reads config injected by the boot function.
- `send()` — Sends the request and populates the response.
- `copyResponse()` — Copies the response body to the clipboard.
- `clear()` — Resets the response and error state.

* **Returns:**
  **object** – Alpine.js component data.

### tryIt()

Boot function that scans the page for HTTP endpoints and injects
interactive “Try It Out” panels. Called from `boot()` in app.js
after `Alpine.start()`. Skipped if `data-try-it-out="false"`
is set on `<html>`.
