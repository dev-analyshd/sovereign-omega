import { build } from "esbuild";
import { mkdirSync } from "fs";

mkdirSync("dist", { recursive: true });

await build({
  entryPoints: ["src/index.ts"],
  bundle: true,
  platform: "node",
  target: "node18",
  format: "cjs",
  outfile: "dist/index.js",
  external: [
    "@langchain/core",
    "langchain",
    "zod",
    "viem",
    "pharos-agent-kit",
  ],
  sourcemap: true,
  logLevel: "info",
});

console.log("✅ Build complete → dist/index.js");
