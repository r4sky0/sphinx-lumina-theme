export default function headerLinks() {
  return {
    init() {
      document.querySelectorAll("a.headerlink").forEach((link) => {
        link.addEventListener("click", (e) => {
          e.preventDefault();
          const href = link.getAttribute("href");
          const url = new URL(href, window.location.href).toString();

          navigator.clipboard.writeText(url).then(() => {
            link.setAttribute("data-tooltip", "Copied!");
            link.classList.add("lumina-tooltip-visible");

            setTimeout(() => {
              link.classList.remove("lumina-tooltip-visible");
              setTimeout(() => link.removeAttribute("data-tooltip"), 150);
            }, 1500);
          });
        });
      });
    },
  };
}
