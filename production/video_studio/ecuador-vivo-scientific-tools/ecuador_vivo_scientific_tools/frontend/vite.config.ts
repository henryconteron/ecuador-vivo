import react from "@vitejs/plugin-react";
import process from "node:process";
import { defineConfig, UserConfig } from "vite";
import path from "node:path";
import fs from "node:fs";
import {fileURLToPath} from "node:url";
const here=path.dirname(fileURLToPath(import.meta.url));
const engines=path.resolve(here,"../../../resource_engines/node_modules");

/**
 * Vite configuration for Streamlit Custom Component v2 development using React.
 *
 * @see https://vitejs.dev/config/ for complete Vite configuration options.
 */
export default defineConfig(() => {
  const isProd = process.env.NODE_ENV === "production";
  const isDev = !isProd;

  return {
    base: "./",
    resolve:{dedupe:["react","react-dom"],alias:{...Object.fromEntries(["fabric","@excalidraw/excalidraw","@xyflow/react","ketcher-react","ketcher-standalone"].map(name=>[name,path.join(engines,name)])),events:path.join(here,"node_modules/events")}},
    plugins: [react(),{name:"local-scientific-assets",closeBundle(){
      fs.cpSync(path.join(engines,"@excalidraw/excalidraw/dist/prod/fonts"),path.join(here,"build/fonts"),{recursive:true});
    }}],
    define: {
      // We are building in library mode, we need to define the NODE_ENV
      // variable to prevent issues when executing the JS.
      "process.env.NODE_ENV": JSON.stringify(process.env.NODE_ENV),
    },
    build: {
      minify: isDev ? false : "oxc",
      outDir: "build",
      sourcemap: isDev,
      lib: {
        entry: "./src/index.tsx",
        name: "MyComponent",
        cssFileName: "scientific-tools",
        formats: ["es"],
        fileName: "scientific-entry",
      },
      ...(!isDev && {
        rolldownOptions: {
          output: {
            minify: {
              compress: {
                dropConsole: true,
                dropDebugger: true,
              },
            },
          },
        },
      }),
    },
  } satisfies UserConfig;
});
