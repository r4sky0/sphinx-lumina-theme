/** Keep Mermaid's natural SVG dimensions after rendering and theme changes. */
export default function mermaidSizing() {
  const diagrams = document.querySelectorAll("pre.mermaid");
  if (!diagrams.length) return;

  const resize = () => {
    for (const diagram of diagrams) {
      const svg = diagram.querySelector(":scope > svg");
      const width = svg?.viewBox.baseVal.width;
      if (width > 0) {
        svg.style.setProperty("--lumina-diagram-width", `${width}px`);
      }
    }
  };
  const observer = new MutationObserver(resize);
  for (const diagram of diagrams) {
    observer.observe(diagram, { childList: true });
  }
  resize();
}
