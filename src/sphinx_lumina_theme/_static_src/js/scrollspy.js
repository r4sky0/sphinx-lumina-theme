export default function scrollspy() {
  return {
    activeId: null,
    observer: null,

    init() {
      const nav = this.$el;
      const links = nav.querySelectorAll("a");
      const ids = Array.from(links)
        .map((a) => a.getAttribute("href"))
        .filter((href) => href && href.startsWith("#"))
        .map((href) => href.slice(1));

      if (ids.length === 0) return;

      this.observer = new IntersectionObserver(
        (entries) => {
          for (const entry of entries) {
            if (entry.isIntersecting) {
              this.activeId = entry.target.id;
              this.updateActive(nav);
              break;
            }
          }
        },
        { rootMargin: "-80px 0px -60% 0px" }
      );

      for (const id of ids) {
        const el = document.getElementById(id);
        if (el) this.observer.observe(el);
      }
    },

    updateActive(nav) {
      nav.querySelectorAll("a").forEach((a) => {
        const href = a.getAttribute("href");
        if (href === "#" + this.activeId) {
          a.classList.add("lumina-toc-active");
        } else {
          a.classList.remove("lumina-toc-active");
        }
      });
    },

    destroy() {
      if (this.observer) this.observer.disconnect();
    },
  };
}
