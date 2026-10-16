import { o as e } from "./rolldown-runtime-CEFd7nDs.js";
import { t } from "./react-BOiH87ah.js";
import { t as n } from "./client-B6ao8twH.js";
import { t as r } from "./jsx-runtime-xKqbzy7D.js";
//#region src/MyComponent.tsx
var i = n(), a = /* @__PURE__ */ e(t(), 1), o = /* @__PURE__ */ e(r(), 1), s = {
	drawing: "Dibujo y flechas · Excalidraw",
	vector: "Ilustración vectorial · Fabric.js",
	diagram: "Mecanismos y relaciones · React Flow",
	molecule: "Estructuras químicas · Ketcher"
};
function c(e) {
	return new Promise((t, n) => {
		let r = URL.createObjectURL(e), i = new Image();
		i.onload = () => {
			try {
				let e = document.createElement("canvas"), n = Math.min(2, 1600 / Math.max(i.width, i.height));
				e.width = Math.max(1, Math.round(i.width * n)), e.height = Math.max(1, Math.round(i.height * n)), e.getContext("2d").drawImage(i, 0, 0, e.width, e.height), t(e.toDataURL("image/png"));
			} catch (e) {
				n(e);
			} finally {
				URL.revokeObjectURL(r);
			}
		}, i.onerror = () => {
			URL.revokeObjectURL(r), n(/* @__PURE__ */ Error("No se pudo representar la figura."));
		}, i.src = r;
	});
}
function l({ recipe: e, onArtifact: t }) {
	let [n, r] = (0, a.useState)(null), i = (0, a.useRef)(null), [s, l] = (0, a.useState)("");
	return (0, a.useEffect)(() => {
		let e = !0;
		return window.EXCALIDRAW_ASSET_PATH = location.origin + "/resource-tool-assets/", import("./prod-COEL2BYf.js").then((e) => e.t).then((t) => {
			e && r(t);
		}).catch((e) => l(String(e))), () => {
			e = !1;
		};
	}, []), /* @__PURE__ */ (0, o.jsxs)(o.Fragment, { children: [
		/* @__PURE__ */ (0, o.jsxs)("div", {
			className: "actions",
			children: [/* @__PURE__ */ (0, o.jsx)("span", { children: "Dibuja y conecta objetos. El documento original se conserva." }), /* @__PURE__ */ (0, o.jsx)("button", {
				onClick: async () => {
					try {
						if (!i.current) return;
						let e = i.current.getSceneElements();
						if (!e.length) throw Error("Añade al menos una pieza.");
						let r = i.current.getFiles(), a = await n.exportToBlob({
							elements: e,
							files: r,
							appState: {
								exportBackground: !1,
								exportWithDarkMode: !1
							},
							maxWidthOrHeight: 1600
						});
						if (!a) throw Error("No se obtuvo una imagen.");
						t({
							tool: "drawing",
							png: await c(a),
							recipe: {
								elements: e,
								files: r
							}
						});
					} catch (e) {
						l(String(e));
					}
				},
				disabled: !n,
				children: "Añadir al recurso"
			})]
		}),
		s && /* @__PURE__ */ (0, o.jsx)("p", {
			role: "alert",
			children: s
		}),
		/* @__PURE__ */ (0, o.jsx)("div", {
			className: "tool-canvas",
			children: n ? /* @__PURE__ */ (0, o.jsx)(n.Excalidraw, {
				theme: "dark",
				langCode: "es-ES",
				excalidrawAPI: (e) => i.current = e,
				initialData: {
					elements: e.elements || [],
					files: e.files || {},
					appState: {
						viewBackgroundColor: "#132b37",
						currentItemFontFamily: 2
					}
				},
				UIOptions: { canvasActions: {
					loadScene: !1,
					saveToActiveFile: !1,
					export: !1
				} }
			}) : /* @__PURE__ */ (0, o.jsx)("p", { children: "Cargando editor de dibujo…" })
		})
	] });
}
function u({ recipe: e, onArtifact: t }) {
	let n = (0, a.useRef)(null), r = (0, a.useRef)(null), i = (0, a.useRef)(null), [s, c] = (0, a.useState)(""), [l, u] = (0, a.useState)(!1);
	(0, a.useEffect)(() => {
		let t = !0;
		return import("./dist-DxGuyIy-.js").then(async (a) => {
			if (!t || !n.current) return;
			i.current = a;
			let o = new a.Canvas(n.current, {
				width: 900,
				height: 470,
				backgroundColor: "#0b1821"
			});
			r.current = o, e.objects && await o.loadFromJSON(e), o.requestRenderAll(), t && u(!0);
		}).catch((e) => c(String(e))), () => {
			t = !1, r.current?.dispose();
		};
	}, []);
	let d = (e) => {
		let t = i.current, n = r.current;
		if (!t || !n) return;
		let a = {
			left: 120,
			top: 100,
			fill: "#70d9c5"
		}, o = e === "text" ? new t.IText("Explica tu idea", {
			...a,
			fontSize: 36,
			fontFamily: "sans-serif"
		}) : e === "circle" ? new t.Circle({
			...a,
			radius: 60
		}) : new t.Rect({
			...a,
			width: 200,
			height: 110,
			rx: 12,
			ry: 12
		});
		n.add(o), n.setActiveObject(o), n.requestRenderAll();
	};
	return /* @__PURE__ */ (0, o.jsxs)(o.Fragment, { children: [
		/* @__PURE__ */ (0, o.jsxs)("div", {
			className: "actions",
			children: [
				/* @__PURE__ */ (0, o.jsx)("button", {
					disabled: !l,
					onClick: () => d("text"),
					children: "Texto"
				}),
				/* @__PURE__ */ (0, o.jsx)("button", {
					disabled: !l,
					onClick: () => d("rectangle"),
					children: "Forma"
				}),
				/* @__PURE__ */ (0, o.jsx)("button", {
					disabled: !l,
					onClick: () => d("circle"),
					children: "Círculo"
				}),
				/* @__PURE__ */ (0, o.jsx)("button", {
					disabled: !l,
					onClick: () => {
						let e = r.current;
						e.getActiveObjects().forEach((t) => e.remove(t)), e.discardActiveObject(), e.requestRenderAll();
					},
					children: "Eliminar"
				}),
				/* @__PURE__ */ (0, o.jsx)("button", {
					disabled: !l,
					onClick: () => t({
						tool: "vector",
						png: r.current.toDataURL({
							format: "png",
							multiplier: 1.5
						}),
						recipe: r.current.toJSON()
					}),
					children: "Añadir al recurso"
				})
			]
		}),
		s && /* @__PURE__ */ (0, o.jsx)("p", {
			role: "alert",
			children: s
		}),
		/* @__PURE__ */ (0, o.jsx)("div", {
			className: "vector-canvas",
			children: /* @__PURE__ */ (0, o.jsx)("canvas", {
				ref: n,
				"aria-label": "Ilustración vectorial editable"
			})
		}),
		/* @__PURE__ */ (0, o.jsx)("p", { children: "Arrastra, gira y cambia el tamaño con los controles. Doble clic para editar el texto." })
	] });
}
function d({ recipe: e, onArtifact: t }) {
	let [n, r] = (0, a.useState)(null), [i, s] = (0, a.useState)(e.nodes || [{
		id: "a",
		position: {
			x: 80,
			y: 70
		},
		data: { label: "Proceso inicial" }
	}, {
		id: "b",
		position: {
			x: 390,
			y: 220
		},
		data: { label: "Resultado" }
	}]), [c, l] = (0, a.useState)(e.edges || [{
		id: "ab",
		source: "a",
		target: "b"
	}]), [u, d] = (0, a.useState)("a"), [f, p] = (0, a.useState)("");
	return (0, a.useEffect)(() => {
		let e = !0;
		return import("./esm-Lw20prh2.js").then((t) => {
			e && r(t);
		}).catch((e) => p(String(e))), () => {
			e = !1;
		};
	}, []), /* @__PURE__ */ (0, o.jsxs)(o.Fragment, { children: [
		/* @__PURE__ */ (0, o.jsxs)("div", {
			className: "actions",
			children: [
				/* @__PURE__ */ (0, o.jsx)("button", {
					onClick: () => s([...i, {
						id: crypto.randomUUID(),
						position: {
							x: 170,
							y: 130
						},
						data: { label: "Nuevo proceso" }
					}]),
					children: "Añadir proceso"
				}),
				/* @__PURE__ */ (0, o.jsxs)("label", { children: ["Texto", /* @__PURE__ */ (0, o.jsx)("input", {
					maxLength: 80,
					value: i.find((e) => e.id === u)?.data.label || "",
					onChange: (e) => s(i.map((t) => t.id === u ? {
						...t,
						data: { label: e.target.value }
					} : t))
				})] }),
				/* @__PURE__ */ (0, o.jsx)("button", {
					onClick: () => {
						if (!i.length) {
							p("Añade al menos un proceso antes de guardar.");
							return;
						}
						let e = document.createElement("canvas");
						e.width = 1400, e.height = 850;
						let n = e.getContext("2d");
						n.fillStyle = "#0b1821", n.fillRect(0, 0, e.width, e.height);
						let r = Math.min(...i.map((e) => e.position.x)) - 40, a = Math.min(...i.map((e) => e.position.y)) - 40, o = Math.max(...i.map((e) => e.position.x)) + 230, s = Math.max(...i.map((e) => e.position.y)) + 120, l = Math.min(1400 / (o - r), 850 / (s - a));
						n.scale(l, l), n.translate(-r, -a), n.lineWidth = 3, n.strokeStyle = "#70d9c5";
						for (let e of c) {
							let t = i.find((t) => t.id === e.source), r = i.find((t) => t.id === e.target);
							if (!t || !r) continue;
							let a = t.position.x + 90, o = t.position.y + 60, s = r.position.x + 90, c = r.position.y;
							n.beginPath(), n.moveTo(a, o), n.bezierCurveTo(a, (o + c) / 2, s, (o + c) / 2, s, c), n.stroke(), n.beginPath(), n.moveTo(s - 6, c - 10), n.lineTo(s, c), n.lineTo(s + 6, c - 10), n.stroke();
						}
						for (let e of i) n.fillStyle = "#203b49", n.fillRect(e.position.x, e.position.y, 180, 60), n.strokeRect(e.position.x, e.position.y, 180, 60), n.fillStyle = "#edf3f5", n.font = "15px sans-serif", n.fillText(String(e.data.label), e.position.x + 12, e.position.y + 36, 156);
						t({
							tool: "diagram",
							png: e.toDataURL("image/png"),
							recipe: {
								nodes: i,
								edges: c
							}
						});
					},
					children: "Añadir al recurso"
				})
			]
		}),
		f && /* @__PURE__ */ (0, o.jsx)("p", {
			role: "alert",
			children: f
		}),
		/* @__PURE__ */ (0, o.jsx)("div", {
			className: "tool-canvas",
			children: n ? /* @__PURE__ */ (0, o.jsxs)(n.ReactFlow, {
				nodes: i,
				edges: c,
				fitView: !0,
				onNodeClick: (e, t) => d(t.id),
				onNodesChange: (e) => s((t) => n.applyNodeChanges(e, t)),
				onEdgesChange: (e) => l((t) => n.applyEdgeChanges(e, t)),
				onConnect: (e) => l((t) => n.addEdge(e, t)),
				colorMode: "dark",
				children: [/* @__PURE__ */ (0, o.jsx)(n.Background, {}), /* @__PURE__ */ (0, o.jsx)(n.Controls, {})]
			}) : /* @__PURE__ */ (0, o.jsx)("p", { children: "Cargando diagramas…" })
		}),
		/* @__PURE__ */ (0, o.jsx)("p", { children: "Arrastra desde los conectores de un proceso a otro. La imagen usa una representación uniforme; las posiciones y conexiones originales se conservan." })
	] });
}
function f({ recipe: e, onArtifact: t }) {
	let [n, r] = (0, a.useState)(null), [i, s] = (0, a.useState)(null), l = (0, a.useRef)(null), [u, d] = (0, a.useState)("");
	return (0, a.useEffect)(() => {
		let e = !0;
		return Promise.all([import("./dist-jB_mkE3r.js").then((e) => e.t), import("./dist-BvRk9kiK.js")]).then(([t, n]) => {
			e && (r(t), s(new n.StandaloneStructServiceProvider()));
		}).catch((e) => d(String(e))), () => {
			e = !1;
		};
	}, []), /* @__PURE__ */ (0, o.jsxs)(o.Fragment, { children: [
		/* @__PURE__ */ (0, o.jsxs)("div", {
			className: "actions",
			children: [/* @__PURE__ */ (0, o.jsx)("span", { children: "Comprueba estructura, valencias y etiquetas antes de publicar." }), /* @__PURE__ */ (0, o.jsx)("button", {
				onClick: async () => {
					try {
						if (!l.current) return;
						let e = await l.current.getMolfile();
						t({
							tool: "molecule",
							png: await c(await l.current.generateImage(e, { outputFormat: "svg" })),
							recipe: { molfile: e }
						});
					} catch (e) {
						d(String(e));
					}
				},
				disabled: !n,
				children: "Añadir al recurso"
			})]
		}),
		u && /* @__PURE__ */ (0, o.jsx)("p", {
			role: "alert",
			children: u
		}),
		/* @__PURE__ */ (0, o.jsx)("div", {
			className: "tool-canvas molecule",
			children: n && i ? /* @__PURE__ */ (0, o.jsx)(n.Editor, {
				staticResourcesUrl: location.origin + "/resource-tool-assets",
				structServiceProvider: i,
				onInit: (t) => {
					l.current = t, e.molfile && t.setMolecule(e.molfile).catch((e) => d(String(e)));
				}
			}) : /* @__PURE__ */ (0, o.jsx)("p", { children: "Cargando editor molecular local…" })
		})
	] });
}
function p(e) {
	return /* @__PURE__ */ (0, o.jsxs)("section", {
		className: "scientific-tool",
		children: [/* @__PURE__ */ (0, o.jsxs)("header", { children: [/* @__PURE__ */ (0, o.jsx)("strong", { children: s[e.tool] || "Editor científico" }), /* @__PURE__ */ (0, o.jsx)("span", { children: "Documento editable + imagen" })] }), e.tool === "drawing" ? /* @__PURE__ */ (0, o.jsx)(l, { ...e }) : e.tool === "vector" ? /* @__PURE__ */ (0, o.jsx)(u, { ...e }) : e.tool === "diagram" ? /* @__PURE__ */ (0, o.jsx)(d, { ...e }) : e.tool === "molecule" ? /* @__PURE__ */ (0, o.jsx)(f, { ...e }) : /* @__PURE__ */ (0, o.jsx)("p", {
			role: "alert",
			children: "Herramienta desconocida."
		})]
	});
}
//#endregion
//#region src/index.tsx
var m = /* @__PURE__ */ new WeakMap(), h = ({ data: e, parentElement: t, setTriggerValue: n }) => {
	let r = t.querySelector(".react-root");
	if (!r) throw Error("No se encontró el editor científico.");
	let a = m.get(t);
	return a || (a = (0, i.createRoot)(r), m.set(t, a)), a.render(/* @__PURE__ */ (0, o.jsx)(p, {
		tool: e.tool,
		recipe: e.recipe,
		onArtifact: (e) => n("artifact", e)
	})), () => {
		setTimeout(() => {
			r.isConnected || (m.get(t)?.unmount(), m.delete(t));
		}, 0);
	};
};
//#endregion
export { h as default };
