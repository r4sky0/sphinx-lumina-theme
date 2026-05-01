/**
 * @module copy-page
 * @description Alpine.js component that converts the rendered article HTML
 * to clean Markdown and copies it to the clipboard. Works regardless of
 * whether the source is rST or MyST Markdown, since it converts from
 * the rendered HTML output.
 */

import { copyText } from "./utils/clipboard.js";

/**
 * Factory for the copy-page Alpine component.
 * Registered as ``Alpine.data("copyPage", copyPage)``.
 *
 * **Properties:**
 *
 * - ``copied`` *(boolean)* — Briefly ``true`` after a successful copy.
 *
 * **Methods:**
 *
 * - ``copy()`` — Converts the article to Markdown and copies it to the clipboard.
 *
 * @function copyPage
 * @returns {object} Alpine.js component data.
 */
export default function copyPage() {
  return {
    copied: false,

    async copy() {
      const article = document.querySelector(".lumina-article");
      if (!article) return;

      const markdown = htmlToMarkdown(article);

      try {
        await copyText(markdown);
        this.copied = true;
        setTimeout(() => {
          this.copied = false;
        }, 1500);
      } catch (err) {
        console.error("Lumina: failed to copy page Markdown", err);
      }
    },
  };
}

/* ── HTML → Markdown converter ── */

function htmlToMarkdown(root) {
  const clone = root.cloneNode(true);

  // Strip elements that shouldn't appear in the markdown output
  clone
    .querySelectorAll(
      "a.headerlink, .copybtn, .linenodiv, script, style, .lumina-copy-page"
    )
    .forEach((el) => el.remove());

  return collapseBlankLines(processNode(clone)).trim() + "\n";
}

function processNode(node) {
  if (node.nodeType === Node.TEXT_NODE) {
    return node.textContent;
  }
  if (node.nodeType !== Node.ELEMENT_NODE) return "";

  const tag = node.tagName.toLowerCase();

  switch (tag) {
    case "h1":
      return `\n# ${children(node).trim()}\n\n`;
    case "h2":
      return `\n## ${children(node).trim()}\n\n`;
    case "h3":
      return `\n### ${children(node).trim()}\n\n`;
    case "h4":
      return `\n#### ${children(node).trim()}\n\n`;
    case "h5":
      return `\n##### ${children(node).trim()}\n\n`;
    case "h6":
      return `\n###### ${children(node).trim()}\n\n`;

    case "p":
      return `${children(node).trim()}\n\n`;

    case "br":
      return "\n";
    case "hr":
      return "\n---\n\n";

    case "strong":
    case "b":
      return `**${children(node)}**`;

    case "em":
    case "i":
    case "cite":
      return `*${children(node)}*`;

    case "code":
      if (!node.closest("pre")) {
        return `\`${node.textContent}\``;
      }
      return node.textContent;

    case "kbd":
      return `\`${node.textContent}\``;

    case "pre":
      return processCodeBlock(node);

    case "a": {
      const href = node.getAttribute("href");
      const text = children(node);
      if (!href) return text;
      return `[${text}](${href})`;
    }

    case "img": {
      const alt = node.getAttribute("alt") || "";
      const src = node.getAttribute("src") || "";
      return `![${alt}](${src})`;
    }

    case "ul":
      return "\n" + processListItems(node, "-") + "\n";
    case "ol":
      return "\n" + processListItems(node, "1.") + "\n";

    case "blockquote": {
      const content = children(node).trim();
      return (
        "\n" +
        content
          .split("\n")
          .map((l) => `> ${l}`)
          .join("\n") +
        "\n\n"
      );
    }

    case "table":
      return processTable(node);

    case "dl":
      return "\n" + processDefinitionList(node) + "\n";

    case "figure": {
      const img = node.querySelector("img");
      const caption = node.querySelector("figcaption");
      let result = img ? processNode(img) : "";
      if (caption) result += `\n*${children(caption).trim()}*`;
      return result + "\n\n";
    }

    case "div":
      return processDiv(node);

    case "section":
    case "article":
    case "span":
    case "abbr":
    case "dd":
      return children(node);

    default:
      return children(node);
  }
}

function children(node) {
  let result = "";
  for (const child of node.childNodes) {
    result += processNode(child);
  }
  return result;
}

/* ── Code blocks ── */

function processCodeBlock(pre) {
  const codeEl = pre.querySelector("code");
  const text = (codeEl || pre).textContent;
  const lang = detectLanguage(pre);
  return `\n\`\`\`${lang}\n${text.trimEnd()}\n\`\`\`\n\n`;
}

function detectLanguage(pre) {
  // Check <code class="language-xxx">
  const codeEl = pre.querySelector("code");
  const codeLang = codeEl?.className?.match(/language-(\w+)/);
  if (codeLang) return codeLang[1];

  // Walk up to find div.highlight-xxx
  let el = pre.parentElement;
  while (el) {
    if (el.classList) {
      for (const cls of el.classList) {
        const m = cls.match(/^highlight-(\w+)$/);
        if (m && m[1] !== "default") return m[1];
      }
    }
    el = el.parentElement;
  }
  return "";
}

/* ── Lists ── */

function processListItems(list, marker, indent) {
  indent = indent || "";
  let result = "";
  let index = 1;

  for (const li of list.children) {
    if (li.tagName?.toLowerCase() !== "li") continue;

    const prefix = marker === "-" ? "- " : `${index}. `;
    const nested = li.querySelector(":scope > ul, :scope > ol");

    // Collect content excluding nested lists
    let content = "";
    for (const child of li.childNodes) {
      if (child === nested) continue;
      // Flatten <p> inside <li> to avoid extra blank lines
      if (
        child.nodeType === Node.ELEMENT_NODE &&
        child.tagName.toLowerCase() === "p"
      ) {
        content += children(child).trim();
      } else {
        content += processNode(child);
      }
    }

    result += `${indent}${prefix}${content.trim()}\n`;

    if (nested) {
      const nestedMarker =
        nested.tagName.toLowerCase() === "ul" ? "-" : "1.";
      result += processListItems(nested, nestedMarker, indent + "  ");
    }

    index++;
  }

  return result;
}

/* ── Tables ── */

function processTable(table) {
  const rows = [];
  table.querySelectorAll("tr").forEach((tr) => {
    const cells = [];
    tr.querySelectorAll("th, td").forEach((cell) => {
      cells.push(children(cell).trim().replace(/\n/g, " "));
    });
    if (cells.length) rows.push(cells);
  });

  if (rows.length === 0) return "";

  // Normalize column count
  const cols = Math.max(...rows.map((r) => r.length));
  rows.forEach((r) => {
    while (r.length < cols) r.push("");
  });

  const widths = Array.from({ length: cols }, (_, i) =>
    Math.max(3, ...rows.map((r) => r[i].length))
  );

  let result = "\n";
  rows.forEach((row, i) => {
    result +=
      "| " + row.map((cell, j) => cell.padEnd(widths[j])).join(" | ") + " |\n";
    if (i === 0) {
      result +=
        "| " +
        widths.map((w) => "-".repeat(w)).join(" | ") +
        " |\n";
    }
  });
  return result + "\n";
}

/* ── Definition lists ── */

function processDefinitionList(dl) {
  let result = "";
  for (const child of dl.children) {
    const tag = child.tagName?.toLowerCase();
    if (tag === "dt") {
      result += `**${children(child).trim()}**\n`;
    } else if (tag === "dd") {
      result += `${children(child).trim()}\n\n`;
    }
  }
  return result;
}

/* ── Divs (admonitions, highlight wrappers, generic) ── */

function processDiv(node) {
  // Sphinx admonitions
  if (node.classList.contains("admonition")) {
    return processAdmonition(node);
  }

  // Code block wrappers (div.highlight)
  if (node.classList.contains("highlight")) {
    const pre = node.querySelector("pre");
    if (pre) return processCodeBlock(pre);
  }

  // highlight-LANG wrappers — look for inner highlight div or pre
  for (const cls of node.classList) {
    if (/^highlight-\w+$/.test(cls)) {
      const pre = node.querySelector("pre");
      if (pre) return processCodeBlock(pre);
    }
  }

  return children(node);
}

function processAdmonition(node) {
  const titleEl = node.querySelector(".admonition-title");
  const title = titleEl ? children(titleEl).trim() : "Note";

  let content = "";
  for (const child of node.children) {
    if (child.classList?.contains("admonition-title")) continue;
    content += processNode(child);
  }

  const body = content.trim();
  const lines = body ? `**${title}:** ${body}` : `**${title}**`;
  return (
    "\n" +
    lines
      .split("\n")
      .map((l) => `> ${l}`)
      .join("\n") +
    "\n\n"
  );
}

/* ── Output cleanup ── */

function collapseBlankLines(text) {
  return text.replace(/\n{3,}/g, "\n\n");
}
