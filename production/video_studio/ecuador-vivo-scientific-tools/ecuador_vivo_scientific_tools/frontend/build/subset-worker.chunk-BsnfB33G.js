import "./prod-COEL2BYf.js";
import { n as e, r as t } from "./chunk-EIO257PC-m_FkWvgt.js";
//#region ../../../resource_engines/node_modules/@excalidraw/excalidraw/dist/prod/subset-worker.chunk.js
var n = import.meta.url ? new URL(import.meta.url) : void 0;
typeof window > "u" && typeof self < "u" && (self.onmessage = async (n) => {
	switch (n.data.command) {
		case e.Subset:
			let r = await t(n.data.arrayBuffer, n.data.codePoints);
			self.postMessage(r, { transfer: [r] });
	}
});
//#endregion
export { n as WorkerUrl };
