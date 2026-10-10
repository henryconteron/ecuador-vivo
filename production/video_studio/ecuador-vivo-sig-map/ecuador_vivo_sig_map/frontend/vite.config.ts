import process from "node:process";
import { defineConfig, UserConfig } from "vite";

/**
 * Vite configuration for Streamlit Custom Component v2 development (no React).
 */
export default defineConfig(() => {
  const isProd = process.env.NODE_ENV === "production";
  const isDev = !isProd;

  return {
    plugins: [{name:'ecuador-vivo-build-inventory',generateBundle(_options,bundle) {
      const modules=Object.values(bundle).filter((item:any)=>item.type==='chunk')
        .flatMap((item:any)=>Object.keys(item.modules))
        .map(id=>id.replaceAll('\\','/').split('/node_modules/').pop())
        .filter((id):id is string=>!!id&&!id.includes(':'));
      this.emitFile({type:'asset',fileName:'build-modules.json',source:JSON.stringify([...new Set(modules)].sort(),null,2)});
    }}],
    base: "./",
    define: {
      "process.env.NODE_ENV": JSON.stringify(process.env.NODE_ENV),
    },
    build: {
      minify: isDev ? false : "oxc",
      outDir: "build",
      emptyOutDir: false,
      sourcemap: isDev,
      lib: {
        entry: "./src/index.ts",
        name: "MyComponent",
        formats: ["es"],
        fileName: "index-u20",
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


