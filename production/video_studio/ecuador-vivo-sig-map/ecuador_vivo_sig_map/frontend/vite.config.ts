import process from "node:process";
import fs from "node:fs";
import path from "node:path";
import {fileURLToPath} from "node:url";
import {createHash} from "node:crypto";
import { defineConfig, UserConfig } from "vite";

const here=path.dirname(fileURLToPath(import.meta.url));
const hash=(bytes: string | Buffer)=>createHash('sha256').update(bytes).digest('hex');

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
    },writeBundle() {
      const output=path.join(here,'build');
      const modules=JSON.parse(fs.readFileSync(path.join(output,'build-modules.json'),'utf8')) as string[];
      const runtime=['ol','quickselect','rbush'].filter(name=>modules.some(id=>id.startsWith(name+'/'))).map(name=>{
        const folder=path.join(here,'node_modules',name);
        const pkg=JSON.parse(fs.readFileSync(path.join(folder,'package.json'),'utf8'));
        return {name,version:pkg.version,license:pkg.license,notices:['LICENSE','LICENSE.md','LICENSE.txt'].filter(file=>fs.existsSync(path.join(folder,file)))};
      });
      const assets=Object.fromEntries(fs.readdirSync(output).filter(name=>name!=='dependencies.json'&&fs.statSync(path.join(output,name)).isFile()).sort().map(name=>[name,hash(fs.readFileSync(path.join(output,name)))]));
      fs.writeFileSync(path.join(output,'dependencies.json'),JSON.stringify({runtime,geotiff_decoder_bundled:modules.some(id=>id.startsWith('geotiff/')),assets,lock_sha256:hash(fs.readFileSync(path.join(here,'package-lock.json')))},null,2)+'\n');
    }}],
    base: "./",
    define: {
      "process.env.NODE_ENV": JSON.stringify(process.env.NODE_ENV),
    },
    build: {
      minify: isDev ? false : "oxc",
      outDir: "build",
      emptyOutDir: true,
      sourcemap: isDev,
      lib: {
        entry: "./src/index.ts",
        name: "MyComponent",
        formats: ["es"],
        fileName: "sig-workbench",
        cssFileName: "sig-workbench",
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


