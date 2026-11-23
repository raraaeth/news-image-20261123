import { copyFileSync, existsSync, mkdirSync } from "node:fs";
import { execFileSync } from "node:child_process";
import { join } from "node:path";

const outputDir = process.env.MAKEFUN_OUTPUT_DIR || "/output";
const botDir = process.env.MAKEFUN_BOT_DIR || ".";

mkdirSync(outputDir, { recursive: true });

const outPath = join(outputDir, "entry.png");
const scriptPath = join(botDir, "render_image.py");
const bundledPath = join(botDir, "entry.png");

let rendered = false;
if (existsSync(scriptPath)) {
  try {
    execFileSync("python3", [scriptPath, outPath], { stdio: "inherit" });
    rendered = existsSync(outPath);
  } catch {
    rendered = false;
  }
}

if (!rendered) {
  if (!existsSync(bundledPath)) {
    throw new Error("could not render entry.png and no bundled entry.png found");
  }
  copyFileSync(bundledPath, outPath);
}

console.log(`wrote ${outPath}`);
