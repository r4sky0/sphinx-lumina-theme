import { build, context } from "esbuild";
import { execFileSync, spawn } from "child_process";
import { resolve, dirname } from "path";
import { fileURLToPath } from "url";

const __dirname = dirname(fileURLToPath(import.meta.url));
const root = resolve(__dirname, "..");
const srcDir = resolve(root, "src/sphinx_lumina_theme/_static_src");
const outDir = resolve(root, "src/sphinx_lumina_theme/theme/static");

const isWatch = process.argv.includes("--watch");

// Build JS bundle
async function buildJS() {
  const options = {
    entryPoints: [resolve(srcDir, "js/app.js")],
    bundle: true,
    outfile: resolve(outDir, "lumina.js"),
    format: "iife",
    minify: !isWatch,
    sourcemap: isWatch,
  };

  if (isWatch) {
    const ctx = await context(options);
    await ctx.watch();
    console.log("Watching JS...");
  } else {
    await build(options);
    console.log("JS built.");
  }
}

// Build CSS with Tailwind
function buildCSS() {
  const input = resolve(srcDir, "css/base.css");
  const output = resolve(outDir, "lumina.css");
  const tailwindBin = resolve(root, "node_modules/.bin/tailwindcss");

  if (isWatch) {
    spawn(tailwindBin, ["-i", input, "-o", output, "--watch"], {
      stdio: "inherit",
    });
    console.log("Watching CSS...");
  } else {
    execFileSync(tailwindBin, ["-i", input, "-o", output, "--minify"], {
      stdio: "inherit",
    });
    console.log("CSS built.");
  }
}

buildJS();
buildCSS();
