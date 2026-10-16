import { o as e } from "./rolldown-runtime-CEFd7nDs.js";
import { t } from "./react-BOiH87ah.js";
import { t as n } from "./react-dom-B0_m6Nyz.js";
import { t as r } from "./jsx-runtime-xKqbzy7D.js";
import { n as i, t as a } from "./with-selector-o2qLEGas.js";
import { T as o, a as s, i as c, r as l, t as u, w as d } from "./src-Cu_B2g6X.js";
import { t as f } from "./drag-CIXYmIU5.js";
import { t as p } from "./value-VMCjJ-Ea.js";
//#region ../../../resource_engines/node_modules/classcat/index.js
var m = /* @__PURE__ */ e(t(), 1), h = /* @__PURE__ */ e(r());
function g(e) {
	if (typeof e == "string" || typeof e == "number") return "" + e;
	let t = "";
	if (Array.isArray(e)) for (let n = 0, r; n < e.length; n++) (r = g(e[n])) !== "" && (t += (t && " ") + r);
	else for (let n in e) e[n] && (t += (t && " ") + n);
	return t;
}
//#endregion
//#region ../../../resource_engines/node_modules/@xyflow/system/dist/esm/index.js
var _ = {
	error001: (e = "react") => `Seems like you have not used ${e === "svelte" ? "SvelteFlowProvider" : "ReactFlowProvider"} as an ancestor. Help: https://${e}flow.dev/error#001`,
	error002: () => "It looks like you've created a new nodeTypes or edgeTypes object. If this wasn't on purpose please define the nodeTypes/edgeTypes outside of the component or memoize them.",
	error003: (e) => `Node type "${e}" not found. Using fallback type "default".`,
	error004: () => "The parent container needs a width and a height to render the graph.",
	error005: () => "Only child nodes can use a parent extent.",
	error006: () => "Can't create edge. An edge needs a source and a target.",
	error007: (e) => `The old edge with id=${e} does not exist.`,
	error009: (e) => `Marker type "${e}" doesn't exist.`,
	error008: (e, { id: t, sourceHandle: n, targetHandle: r }) => `Couldn't create edge for ${e} handle id: "${e === "source" ? n : r}", edge id: ${t}.`,
	error010: () => "Handle: No node id found. Make sure to only use a Handle inside a custom Node.",
	error011: (e) => `Edge type "${e}" not found. Using fallback type "default".`,
	error012: (e) => `Node with id "${e}" does not exist, it may have been removed. This can happen when a node is deleted before the "onNodeClick" handler is called.`,
	error013: (e = "react") => `It seems that you haven't loaded the styles. Please import '@xyflow/${e}/dist/style.css' or base.css to make sure everything is working properly.`,
	error014: () => "useNodeConnections: No node ID found. Call useNodeConnections inside a custom Node or provide a node ID.",
	error015: () => "It seems that you are trying to drag a node that is not initialized. Please use onNodesChange as explained in the docs.",
	error016: (e) => `Edge with id "${e}" does not exist, it may have been removed. This can happen when an edge is deleted before the "onEdgeClick" handler is called.`
}, v = [[-Infinity, -Infinity], [Infinity, Infinity]], y = [
	"Enter",
	" ",
	"Escape"
], b = {
	"node.a11yDescription.default": "Press enter or space to select a node. Press delete to remove it and escape to cancel.",
	"node.a11yDescription.keyboardDisabled": "Press enter or space to select a node. You can then use the arrow keys to move the node around. Press delete to remove it and escape to cancel.",
	"node.a11yDescription.ariaLiveMessage": ({ direction: e, x: t, y: n }) => `Moved selected node ${e}. New position, x: ${t}, y: ${n}`,
	"edge.a11yDescription.default": "Press enter or space to select an edge. You can then press delete to remove it or escape to cancel.",
	"controls.ariaLabel": "Control Panel",
	"controls.zoomIn.ariaLabel": "Zoom In",
	"controls.zoomOut.ariaLabel": "Zoom Out",
	"controls.fitView.ariaLabel": "Fit View",
	"controls.interactive.ariaLabel": "Toggle Interactivity",
	"minimap.ariaLabel": "Mini Map",
	"handle.ariaLabel": "Handle"
}, x;
(function(e) {
	e.Strict = "strict", e.Loose = "loose";
})(x ||= {});
var S;
(function(e) {
	e.Free = "free", e.Vertical = "vertical", e.Horizontal = "horizontal";
})(S ||= {});
var C;
(function(e) {
	e.Partial = "partial", e.Full = "full";
})(C ||= {});
var w = {
	inProgress: !1,
	isValid: null,
	from: null,
	fromHandle: null,
	fromPosition: null,
	fromNode: null,
	to: null,
	toHandle: null,
	toPosition: null,
	toNode: null,
	pointer: null
}, T;
(function(e) {
	e.Bezier = "default", e.Straight = "straight", e.Step = "step", e.SmoothStep = "smoothstep", e.SimpleBezier = "simplebezier";
})(T ||= {});
var E;
(function(e) {
	e.Arrow = "arrow", e.ArrowClosed = "arrowclosed";
})(E ||= {});
var D;
(function(e) {
	e.Left = "left", e.Top = "top", e.Right = "right", e.Bottom = "bottom";
})(D ||= {});
var O = {
	[D.Left]: D.Right,
	[D.Right]: D.Left,
	[D.Top]: D.Bottom,
	[D.Bottom]: D.Top
}, k = (e) => !!e && typeof e == "object" && "id" in e && "source" in e && "target" in e, A = (e) => !!e && typeof e == "object" && "id" in e && "position" in e && !("source" in e) && !("target" in e), j = (e) => !!e && typeof e == "object" && "id" in e && "internals" in e && !("source" in e) && !("target" in e), M = (e, t, n) => {
	if (!e.id) return [];
	let r = /* @__PURE__ */ new Set();
	return n.forEach((t) => {
		t.source === e.id && r.add(t.target);
	}), t.filter((e) => r.has(e.id));
}, N = (e, t, n) => {
	if (!e.id) return [];
	let r = /* @__PURE__ */ new Set();
	return n.forEach((t) => {
		t.target === e.id && r.add(t.source);
	}), t.filter((e) => r.has(e.id));
}, P = (e, t = [0, 0]) => {
	let { width: n, height: r } = Y(e), i = e.origin ?? t, a = n * i[0], o = r * i[1];
	return {
		x: e.position.x - a,
		y: e.position.y - o
	};
}, F = (e, t = { nodeOrigin: [0, 0] }) => {
	if (e.length === 0) return {
		x: 0,
		y: 0,
		width: 0,
		height: 0
	};
	let n = !1, r = e.reduce((e, r) => {
		let i = typeof r == "string", a = !t.nodeLookup && !i ? r : void 0;
		return t.nodeLookup && (a = i ? t.nodeLookup.get(r) : j(r) ? r : t.nodeLookup.get(r.id)), a ? (n = !0, q(e, ie(a, t.nodeOrigin))) : e;
	}, {
		x: Infinity,
		y: Infinity,
		x2: -Infinity,
		y2: -Infinity
	});
	return n ? ne(r) : {
		x: 0,
		y: 0,
		width: 0,
		height: 0
	};
}, I = (e, t = {}) => {
	let n = {
		x: Infinity,
		y: Infinity,
		x2: -Infinity,
		y2: -Infinity
	}, r = !1;
	return e.forEach((e) => {
		(t.filter === void 0 || t.filter(e)) && (n = q(n, ie(e)), r = !0);
	}), r ? ne(n) : {
		x: 0,
		y: 0,
		width: 0,
		height: 0
	};
}, L = (e, t, [n, r, i] = [
	0,
	0,
	1
], a = !1, o = !1) => {
	let s = (t.x - n) / i, c = (t.y - r) / i, l = t.width / i, u = t.height / i, d = [];
	for (let t of e.values()) {
		let { measured: e, selectable: n = !0, hidden: r = !1 } = t;
		if (o && !n || r) continue;
		let i = e.width ?? t.width ?? t.initialWidth ?? 0, f = e.height ?? t.height ?? t.initialHeight ?? 0, { x: p, y: m } = t.internals.positionAbsolute, h = oe(s, c, l, u, p, m, i, f), g = i * f, _ = a && h > 0;
		(!t.internals.handleBounds || _ || h >= g || t.dragging) && d.push(t);
	}
	return d;
}, R = (e, t) => {
	let n = /* @__PURE__ */ new Set();
	return e.forEach((e) => {
		n.add(e.id);
	}), t.filter((e) => n.has(e.source) || n.has(e.target));
};
function z(e, t) {
	let n = /* @__PURE__ */ new Map(), r = t?.nodes ? new Set(t.nodes.map((e) => e.id)) : null;
	return e.forEach((e) => {
		let i;
		if (t?.includeHiddenNodes) {
			let { width: t, height: n } = Y(e);
			i = t > 0 && n > 0;
		} else i = !!(e.measured.width && e.measured.height && !e.hidden);
		i && (!r || r.has(e.id)) && n.set(e.id, e);
	}), n;
}
async function B({ nodes: e, width: t, height: n, panZoom: r, minZoom: i, maxZoom: a }, o) {
	if (e.size === 0) return !0;
	let s = ge(I(z(e, o)), t, n, o?.minZoom ?? i, o?.maxZoom ?? a, o?.padding ?? .1);
	return await r.setViewport(s, {
		duration: o?.duration,
		ease: o?.ease,
		interpolate: o?.interpolate
	}), !0;
}
function V({ nodeId: e, nextPosition: t, nodeLookup: n, nodeOrigin: r = [0, 0], nodeExtent: i, onError: a }) {
	let o = n.get(e), s = o.parentId ? n.get(o.parentId) : void 0, { x: c, y: l } = s ? s.internals.positionAbsolute : {
		x: 0,
		y: 0
	}, u = o.origin ?? r, d = o.extent || i;
	if (o.extent === "parent" && !o.expandParent) {
		if (!s) a?.("005", _.error005());
		else {
			let { width: e, height: t } = Y(s);
			e && t && (d = [[c, l], [c + e, l + t]]);
		}
	} else s && ve(o.extent) && (d = [[o.extent[0][0] + c, o.extent[0][1] + l], [o.extent[1][0] + c, o.extent[1][1] + l]]);
	let f = ve(d) ? W(t, d, o.measured) : t;
	return (o.measured.width === void 0 || o.measured.height === void 0) && a?.("015", _.error015()), {
		position: {
			x: f.x - c + (o.measured.width ?? 0) * u[0],
			y: f.y - l + (o.measured.height ?? 0) * u[1]
		},
		positionAbsolute: f
	};
}
async function H({ nodesToRemove: e = [], edgesToRemove: t = [], nodes: n, edges: r, onBeforeDelete: i }) {
	let a = new Set(e.map((e) => e.id)), o = [];
	for (let e of n) {
		if (e.deletable === !1) continue;
		let t = a.has(e.id), n = !t && e.parentId && o.find((t) => t.id === e.parentId);
		(t || n) && o.push(e);
	}
	let s = new Set(t.map((e) => e.id)), c = r.filter((e) => e.deletable !== !1), l = R(o, c);
	for (let e of c) s.has(e.id) && !l.find((t) => t.id === e.id) && l.push(e);
	if (!i) return {
		edges: l,
		nodes: o
	};
	let u = await i({
		nodes: o,
		edges: l
	});
	return typeof u == "boolean" ? u ? {
		edges: l,
		nodes: o
	} : {
		edges: [],
		nodes: []
	} : u;
}
var U = (e, t = 0, n = 1) => Math.min(Math.max(e, t), n), W = (e = {
	x: 0,
	y: 0
}, t, n) => ({
	x: U(e.x, t[0][0], t[1][0] - (n?.width ?? 0)),
	y: U(e.y, t[0][1], t[1][1] - (n?.height ?? 0))
});
function G(e, t, n) {
	let { width: r, height: i } = Y(n), { x: a, y: o } = n.internals.positionAbsolute;
	return W(e, [[a, o], [a + r, o + i]], t);
}
var K = (e, t, n) => e < t ? U(Math.abs(e - t), 1, t) / t : e > n ? -U(Math.abs(e - n), 1, t) / t : 0, ee = (e, t, n = 15, r = 40) => [K(e.x, r, t.width - r) * n, K(e.y, r, t.height - r) * n], q = (e, t) => ({
	x: Math.min(e.x, t.x),
	y: Math.min(e.y, t.y),
	x2: Math.max(e.x2, t.x2),
	y2: Math.max(e.y2, t.y2)
}), te = ({ x: e, y: t, width: n, height: r }) => ({
	x: e,
	y: t,
	x2: e + n,
	y2: t + r
}), ne = ({ x: e, y: t, x2: n, y2: r }) => ({
	x: e,
	y: t,
	width: n - e,
	height: r - t
}), re = (e, t = [0, 0]) => {
	let { x: n, y: r } = j(e) ? e.internals.positionAbsolute : P(e, t);
	return {
		x: n,
		y: r,
		width: e.measured?.width ?? e.width ?? e.initialWidth ?? 0,
		height: e.measured?.height ?? e.height ?? e.initialHeight ?? 0
	};
}, ie = (e, t = [0, 0]) => {
	let { x: n, y: r } = j(e) ? e.internals.positionAbsolute : P(e, t);
	return {
		x: n,
		y: r,
		x2: n + (e.measured?.width ?? e.width ?? e.initialWidth ?? 0),
		y2: r + (e.measured?.height ?? e.height ?? e.initialHeight ?? 0)
	};
}, ae = (e, t) => ne(q(te(e), te(t))), oe = (e, t, n, r, i, a, o, s) => {
	let c = Math.max(0, Math.min(e + n, i + o) - Math.max(e, i)), l = Math.max(0, Math.min(t + r, a + s) - Math.max(t, a));
	return Math.ceil(c * l);
}, se = (e, t) => oe(e.x, e.y, e.width, e.height, t.x, t.y, t.width, t.height), ce = (e) => J(e.width) && J(e.height) && J(e.x) && J(e.y), J = (e) => !isNaN(e) && isFinite(e), le = (e, t) => (e, t) => {}, ue = (e, t = [1, 1]) => ({
	x: t[0] * Math.round(e.x / t[0]),
	y: t[1] * Math.round(e.y / t[1])
}), de = ({ x: e, y: t }, [n, r, i], a = !1, o = [1, 1]) => {
	let s = {
		x: (e - n) / i,
		y: (t - r) / i
	};
	return a ? ue(s, o) : s;
}, fe = ({ x: e, y: t }, [n, r, i]) => ({
	x: e * i + n,
	y: t * i + r
});
function pe(e, t) {
	if (typeof e == "number") return Math.floor((t - t / (1 + e)) * .5);
	if (typeof e == "string" && e.endsWith("px")) {
		let t = parseFloat(e);
		if (!Number.isNaN(t)) return Math.floor(t);
	}
	if (typeof e == "string" && e.endsWith("%")) {
		let n = parseFloat(e);
		if (!Number.isNaN(n)) return Math.floor(t * n * .01);
	}
	return 0;
}
function me(e, t, n) {
	if (typeof e == "string" || typeof e == "number") {
		let r = pe(e, n), i = pe(e, t);
		return {
			top: r,
			right: i,
			bottom: r,
			left: i,
			x: i * 2,
			y: r * 2
		};
	}
	if (typeof e == "object") {
		let r = pe(e.top ?? e.y ?? 0, n), i = pe(e.bottom ?? e.y ?? 0, n), a = pe(e.left ?? e.x ?? 0, t), o = pe(e.right ?? e.x ?? 0, t);
		return {
			top: r,
			right: o,
			bottom: i,
			left: a,
			x: a + o,
			y: r + i
		};
	}
	return {
		top: 0,
		right: 0,
		bottom: 0,
		left: 0,
		x: 0,
		y: 0
	};
}
function he(e, t, n, r, i, a) {
	let { x: o, y: s } = fe(e, [
		t,
		n,
		r
	]), { x: c, y: l } = fe({
		x: e.x + e.width,
		y: e.y + e.height
	}, [
		t,
		n,
		r
	]), u = i - c, d = a - l;
	return {
		left: Math.floor(o),
		top: Math.floor(s),
		right: Math.floor(u),
		bottom: Math.floor(d)
	};
}
var ge = (e, t, n, r, i, a) => {
	let o = me(a, t, n), s = (t - o.x) / e.width, c = (n - o.y) / e.height, l = U(Math.min(s, c), r, i), u = e.x + e.width / 2, d = e.y + e.height / 2, f = t / 2 - u * l, p = n / 2 - d * l, m = he(e, f, p, l, t, n), h = {
		left: Math.min(m.left - o.left, 0),
		top: Math.min(m.top - o.top, 0),
		right: Math.min(m.right - o.right, 0),
		bottom: Math.min(m.bottom - o.bottom, 0)
	};
	return {
		x: f - h.left + h.right,
		y: p - h.top + h.bottom,
		zoom: l
	};
}, _e = () => typeof navigator < "u" && navigator?.userAgent?.indexOf("Mac") >= 0;
function ve(e) {
	return e != null && e !== "parent";
}
function Y(e) {
	return {
		width: e.measured?.width ?? e.width ?? e.initialWidth ?? 0,
		height: e.measured?.height ?? e.height ?? e.initialHeight ?? 0
	};
}
function ye(e) {
	return (e.measured?.width ?? e.width ?? e.initialWidth) !== void 0 && (e.measured?.height ?? e.height ?? e.initialHeight) !== void 0;
}
function be(e, t = {
	width: 0,
	height: 0
}, n, r, i) {
	let a = { ...e }, o = r.get(n);
	if (o) {
		let e = o.origin || i;
		a.x += o.internals.positionAbsolute.x - (t.width ?? 0) * e[0], a.y += o.internals.positionAbsolute.y - (t.height ?? 0) * e[1];
	}
	return a;
}
function xe(e, t) {
	if (e.size !== t.size) return !1;
	for (let n of e) if (!t.has(n)) return !1;
	return !0;
}
function Se() {
	let e, t;
	return {
		promise: new Promise((n, r) => {
			e = n, t = r;
		}),
		resolve: e,
		reject: t
	};
}
function Ce(e) {
	return {
		...b,
		...e || {}
	};
}
function we(e, t) {
	if (!e && !t) return !0;
	if (!e || !t || e.size !== t.size) return !1;
	if (!e.size && !t.size) return !0;
	for (let n of e.keys()) if (!t.has(n)) return !1;
	return !0;
}
function Te(e, t, n) {
	if (!n) return;
	let r = [];
	e.forEach((e, n) => {
		t?.has(n) || r.push(e);
	}), r.length && n(r);
}
function Ee(e) {
	return e === null ? null : e ? "valid" : "invalid";
}
function De(e, { snapGrid: t = [0, 0], snapToGrid: n = !1, transform: r, containerBounds: i }) {
	let { x: a, y: o } = X(e), s = de({
		x: a - (i?.left ?? 0),
		y: o - (i?.top ?? 0)
	}, r), { x: c, y: l } = n ? ue(s, t) : s;
	return {
		xSnapped: c,
		ySnapped: l,
		...s
	};
}
var Oe = (e) => ({
	width: e.offsetWidth,
	height: e.offsetHeight
}), ke = (e) => e?.getRootNode?.() || window?.document, Ae = [
	"INPUT",
	"SELECT",
	"TEXTAREA"
];
function je(e) {
	let t = e.composedPath?.()?.[0] || e.target;
	return t?.nodeType === 1 ? Ae.includes(t.nodeName) || t.hasAttribute("contenteditable") || !!t.closest(".nokey") : !1;
}
var Me = (e) => "clientX" in e, X = (e, t) => {
	let n = Me(e), r = n ? e.clientX : e.touches?.[0].clientX, i = n ? e.clientY : e.touches?.[0].clientY;
	return {
		x: r - (t?.left ?? 0),
		y: i - (t?.top ?? 0)
	};
}, Ne = (e, t, n, r, i) => {
	let a = t.querySelectorAll(`.${e}`);
	return !a || !a.length ? null : Array.from(a).map((t) => {
		let a = t.getBoundingClientRect();
		return {
			id: t.getAttribute("data-handleid"),
			type: e,
			nodeId: i,
			position: t.getAttribute("data-handlepos"),
			x: (a.left - n.left) / r,
			y: (a.top - n.top) / r,
			...Oe(t)
		};
	});
};
function Pe({ sourceX: e, sourceY: t, targetX: n, targetY: r, sourceControlX: i, sourceControlY: a, targetControlX: o, targetControlY: s }) {
	let c = e * .125 + i * .375 + o * .375 + n * .125, l = t * .125 + a * .375 + s * .375 + r * .125;
	return [
		c,
		l,
		Math.abs(c - e),
		Math.abs(l - t)
	];
}
function Fe(e, t) {
	return e >= 0 ? .5 * e : t * 25 * Math.sqrt(-e);
}
function Ie({ pos: e, x1: t, y1: n, x2: r, y2: i, c: a }) {
	switch (e) {
		case D.Left: return [t - Fe(t - r, a), n];
		case D.Right: return [t + Fe(r - t, a), n];
		case D.Top: return [t, n - Fe(n - i, a)];
		case D.Bottom: return [t, n + Fe(i - n, a)];
	}
}
function Le({ sourceX: e, sourceY: t, sourcePosition: n = D.Bottom, targetX: r, targetY: i, targetPosition: a = D.Top, curvature: o = .25 }) {
	let [s, c] = Ie({
		pos: n,
		x1: e,
		y1: t,
		x2: r,
		y2: i,
		c: o
	}), [l, u] = Ie({
		pos: a,
		x1: r,
		y1: i,
		x2: e,
		y2: t,
		c: o
	}), [d, f, p, m] = Pe({
		sourceX: e,
		sourceY: t,
		targetX: r,
		targetY: i,
		sourceControlX: s,
		sourceControlY: c,
		targetControlX: l,
		targetControlY: u
	});
	return [
		`M${e},${t} C${s},${c} ${l},${u} ${r},${i}`,
		d,
		f,
		p,
		m
	];
}
function Re({ sourceX: e, sourceY: t, targetX: n, targetY: r }) {
	let i = Math.abs(n - e) / 2, a = n < e ? n + i : n - i, o = Math.abs(r - t) / 2;
	return [
		a,
		r < t ? r + o : r - o,
		i,
		o
	];
}
function ze({ sourceNode: e, targetNode: t, selected: n = !1, zIndex: r = 0, elevateOnSelect: i = !1, zIndexMode: a = "basic" }) {
	return a === "manual" ? r : (i && n ? r + 1e3 : r) + Math.max(e.parentId || i && e.selected ? e.internals.z : 0, t.parentId || i && t.selected ? t.internals.z : 0);
}
function Be({ sourceNode: e, targetNode: t, width: n, height: r, transform: i }) {
	let a = q(ie(e), ie(t));
	return a.x === a.x2 && (a.x2 += 1), a.y === a.y2 && (a.y2 += 1), se({
		x: -i[0] / i[2],
		y: -i[1] / i[2],
		width: n / i[2],
		height: r / i[2]
	}, ne(a)) > 0;
}
var Ve = ({ source: e, sourceHandle: t, target: n, targetHandle: r }) => `xy-edge__${e}${t || ""}-${n}${r || ""}`, He = (e, t) => t.some((t) => t.source === e.source && t.target === e.target && (t.sourceHandle === e.sourceHandle || !t.sourceHandle && !e.sourceHandle) && (t.targetHandle === e.targetHandle || !t.targetHandle && !e.targetHandle)), Ue = (e, t, n = {}) => {
	if (!e.source || !e.target) return n.onError?.("006", _.error006()), t;
	let r = n.getEdgeId || Ve, i;
	return i = k(e) ? { ...e } : {
		...e,
		id: r(e)
	}, He(i, t) ? t : (i.sourceHandle === null && delete i.sourceHandle, i.targetHandle === null && delete i.targetHandle, t.concat(i));
}, We = (e, t, n, r = { shouldReplaceId: !0 }) => {
	let { id: i, ...a } = e;
	if (!t.source || !t.target) return r.onError?.("006", _.error006()), n;
	if (!n.find((t) => t.id === e.id)) return r.onError?.("007", _.error007(i)), n;
	let o = r.getEdgeId || Ve, s = {
		...a,
		id: r.shouldReplaceId ? o(t) : i,
		source: t.source,
		target: t.target,
		sourceHandle: t.sourceHandle,
		targetHandle: t.targetHandle
	};
	return n.filter((e) => e.id !== i).concat(s);
};
function Ge({ sourceX: e, sourceY: t, targetX: n, targetY: r }) {
	let [i, a, o, s] = Re({
		sourceX: e,
		sourceY: t,
		targetX: n,
		targetY: r
	});
	return [
		`M ${e},${t}L ${n},${r}`,
		i,
		a,
		o,
		s
	];
}
var Ke = {
	[D.Left]: {
		x: -1,
		y: 0
	},
	[D.Right]: {
		x: 1,
		y: 0
	},
	[D.Top]: {
		x: 0,
		y: -1
	},
	[D.Bottom]: {
		x: 0,
		y: 1
	}
}, qe = ({ source: e, sourcePosition: t = D.Bottom, target: n }) => t === D.Left || t === D.Right ? e.x < n.x ? {
	x: 1,
	y: 0
} : {
	x: -1,
	y: 0
} : e.y < n.y ? {
	x: 0,
	y: 1
} : {
	x: 0,
	y: -1
}, Je = (e, t) => Math.sqrt((t.x - e.x) ** 2 + (t.y - e.y) ** 2);
function Ye({ source: e, sourcePosition: t = D.Bottom, target: n, targetPosition: r = D.Top, center: i, offset: a, stepPosition: o }) {
	let s = Ke[t], c = Ke[r], l = {
		x: e.x + s.x * a,
		y: e.y + s.y * a
	}, u = {
		x: n.x + c.x * a,
		y: n.y + c.y * a
	}, d = qe({
		source: l,
		sourcePosition: t,
		target: u
	}), f = d.x === 0 ? "y" : "x", p = d[f], m = [], h, g, _ = {
		x: 0,
		y: 0
	}, v = {
		x: 0,
		y: 0
	}, [, , y, b] = Re({
		sourceX: e.x,
		sourceY: e.y,
		targetX: n.x,
		targetY: n.y
	});
	if (s[f] * c[f] === -1) {
		f === "x" ? (h = i.x ?? l.x + (u.x - l.x) * o, g = i.y ?? (l.y + u.y) / 2) : (h = i.x ?? (l.x + u.x) / 2, g = i.y ?? l.y + (u.y - l.y) * o);
		let e = [{
			x: h,
			y: l.y
		}, {
			x: h,
			y: u.y
		}], t = [{
			x: l.x,
			y: g
		}, {
			x: u.x,
			y: g
		}];
		m = s[f] === p ? f === "x" ? e : t : f === "x" ? t : e;
	} else {
		let i = [{
			x: l.x,
			y: u.y
		}], o = [{
			x: u.x,
			y: l.y
		}];
		if (m = f === "x" ? s.x === p ? o : i : s.y === p ? i : o, t === r) {
			let t = Math.abs(e[f] - n[f]);
			if (t <= a) {
				let r = Math.min(a - 1, a - t);
				s[f] === p ? _[f] = (l[f] > e[f] ? -1 : 1) * r : v[f] = (u[f] > n[f] ? -1 : 1) * r;
			}
		}
		if (t !== r) {
			let e = f === "x" ? "y" : "x", t = s[f] === c[e], n = l[e] > u[e], r = l[e] < u[e];
			(s[f] === 1 && (!t && n || t && r) || s[f] !== 1 && (!t && r || t && n)) && (m = f === "x" ? i : o);
		}
		let d = {
			x: l.x + _.x,
			y: l.y + _.y
		}, y = {
			x: u.x + v.x,
			y: u.y + v.y
		};
		Math.max(Math.abs(d.x - m[0].x), Math.abs(y.x - m[0].x)) >= Math.max(Math.abs(d.y - m[0].y), Math.abs(y.y - m[0].y)) ? (h = (d.x + y.x) / 2, g = m[0].y) : (h = m[0].x, g = (d.y + y.y) / 2);
	}
	let x = {
		x: l.x + _.x,
		y: l.y + _.y
	}, S = {
		x: u.x + v.x,
		y: u.y + v.y
	};
	return [
		[
			e,
			...x.x !== m[0].x || x.y !== m[0].y ? [x] : [],
			...m,
			...S.x !== m[m.length - 1].x || S.y !== m[m.length - 1].y ? [S] : [],
			n
		],
		h,
		g,
		y,
		b
	];
}
function Xe(e, t, n, r) {
	let i = Math.min(Je(e, t) / 2, Je(t, n) / 2, r), { x: a, y: o } = t;
	if (e.x === a && a === n.x || e.y === o && o === n.y) return `L${a} ${o}`;
	if (e.y === o) {
		let t = e.x < n.x ? -1 : 1, r = e.y < n.y ? 1 : -1;
		return `L ${a + i * t},${o}Q ${a},${o} ${a},${o + i * r}`;
	}
	let s = e.x < n.x ? 1 : -1;
	return `L ${a},${o + i * (e.y < n.y ? -1 : 1)}Q ${a},${o} ${a + i * s},${o}`;
}
function Ze({ sourceX: e, sourceY: t, sourcePosition: n = D.Bottom, targetX: r, targetY: i, targetPosition: a = D.Top, borderRadius: o = 5, centerX: s, centerY: c, offset: l = 20, stepPosition: u = .5 }) {
	let [d, f, p, m, h] = Ye({
		source: {
			x: e,
			y: t
		},
		sourcePosition: n,
		target: {
			x: r,
			y: i
		},
		targetPosition: a,
		center: {
			x: s,
			y: c
		},
		offset: l,
		stepPosition: u
	}), g = `M${d[0].x} ${d[0].y}`;
	for (let e = 1; e < d.length - 1; e++) g += Xe(d[e - 1], d[e], d[e + 1], o);
	return g += `L${d[d.length - 1].x} ${d[d.length - 1].y}`, [
		g,
		f,
		p,
		m,
		h
	];
}
function Qe(e) {
	return e && !!(e.internals.handleBounds || e.handles?.length) && !!(e.measured.width || e.width || e.initialWidth);
}
function $e(e) {
	let { sourceNode: t, targetNode: n } = e;
	if (!Qe(t) || !Qe(n)) return null;
	let r = t.internals.handleBounds || et(t.handles), i = n.internals.handleBounds || et(n.handles), a = nt(r?.source ?? [], e.sourceHandle), o = nt(e.connectionMode === x.Strict ? i?.target ?? [] : (i?.target ?? []).concat(i?.source ?? []), e.targetHandle);
	if (!a || !o) return e.onError?.("008", _.error008(a ? "target" : "source", {
		id: e.id,
		sourceHandle: e.sourceHandle,
		targetHandle: e.targetHandle
	})), null;
	let s = a?.position || D.Bottom, c = o?.position || D.Top, l = tt(t, a, s), u = tt(n, o, c);
	return {
		sourceX: l.x,
		sourceY: l.y,
		targetX: u.x,
		targetY: u.y,
		sourcePosition: s,
		targetPosition: c
	};
}
function et(e) {
	if (!e) return null;
	let t = [], n = [];
	for (let r of e) r.width = r.width ?? 1, r.height = r.height ?? 1, r.type === "source" ? t.push(r) : r.type === "target" && n.push(r);
	return {
		source: t,
		target: n
	};
}
function tt(e, t, n = D.Left, r = !1) {
	let i = (t?.x ?? 0) + e.internals.positionAbsolute.x, a = (t?.y ?? 0) + e.internals.positionAbsolute.y, { width: o, height: s } = t ?? Y(e);
	if (r) return {
		x: i + o / 2,
		y: a + s / 2
	};
	switch (t?.position ?? n) {
		case D.Top: return {
			x: i + o / 2,
			y: a
		};
		case D.Right: return {
			x: i + o,
			y: a + s / 2
		};
		case D.Bottom: return {
			x: i + o / 2,
			y: a + s
		};
		case D.Left: return {
			x: i,
			y: a + s / 2
		};
	}
}
function nt(e, t) {
	return e && (t ? e.find((e) => e.id === t) : e[0]) || null;
}
function rt(e, t) {
	return e ? typeof e == "string" ? e : `${t ? `${t}__` : ""}${Object.keys(e).sort().map((t) => `${t}=${e[t]}`).join("&")}` : "";
}
function it(e, { id: t, defaultColor: n, defaultMarkerStart: r, defaultMarkerEnd: i }) {
	let a = /* @__PURE__ */ new Set();
	return e.reduce((e, o) => ([o.markerStart || r, o.markerEnd || i].forEach((r) => {
		if (r && typeof r == "object") {
			let i = rt(r, t);
			a.has(i) || (e.push({
				id: i,
				color: r.color || n,
				...r
			}), a.add(i));
		}
	}), e), []).sort((e, t) => e.id.localeCompare(t.id));
}
function at(e, t, n, r, i) {
	let a = .5;
	i === "start" ? a = 0 : i === "end" && (a = 1);
	let o = [(e.x + e.width * a) * t.zoom + t.x, e.y * t.zoom + t.y - r], s = [-100 * a, -100];
	switch (n) {
		case D.Right:
			o = [(e.x + e.width) * t.zoom + t.x + r, (e.y + e.height * a) * t.zoom + t.y], s = [0, -100 * a];
			break;
		case D.Bottom:
			o[1] = (e.y + e.height) * t.zoom + t.y + r, s[1] = 0;
			break;
		case D.Left: o = [e.x * t.zoom + t.x - r, (e.y + e.height * a) * t.zoom + t.y], s = [-100, -100 * a];
	}
	return `translate(${o[0]}px, ${o[1]}px) translate(${s[0]}%, ${s[1]}%)`;
}
var ot = {
	left: 0,
	center: 50,
	right: 100
}, st = {
	top: 0,
	center: 50,
	bottom: 100
};
function ct(e, t, n, r = "center", i = "center") {
	return `translate(${e}px, ${t}px) scale(${1 / n}) translate(${-(ot[r] ?? 50)}%, ${-(st[i] ?? 50)}%)`;
}
var lt = 1e3, ut = 10, dt = {
	nodeOrigin: [0, 0],
	nodeExtent: v,
	elevateNodesOnSelect: !0,
	zIndexMode: "basic",
	defaults: {}
}, ft = {
	...dt,
	checkEquality: !0
};
function pt(e, t) {
	let n = { ...e };
	for (let e in t) t[e] !== void 0 && (n[e] = t[e]);
	return n;
}
function mt(e, t, n) {
	let r = pt(dt, n);
	for (let n of e.values()) if (n.parentId) yt(n, e, t, r);
	else {
		let e = W(P(n, r.nodeOrigin), ve(n.extent) ? n.extent : r.nodeExtent, Y(n));
		n.internals.positionAbsolute = e;
	}
}
function ht(e, t) {
	if (!e.handles) return e.measured ? t?.internals.handleBounds : void 0;
	let n = [], r = [];
	for (let t of e.handles) {
		let i = {
			id: t.id,
			width: t.width ?? 1,
			height: t.height ?? 1,
			nodeId: e.id,
			x: t.x,
			y: t.y,
			position: t.position,
			type: t.type
		};
		t.type === "source" ? n.push(i) : t.type === "target" && r.push(i);
	}
	return {
		source: n,
		target: r
	};
}
function gt(e) {
	return e === "manual";
}
function _t(e, t, n, r = {}) {
	let i = pt(ft, r), a = { i: 0 }, o = new Map(t), s = i?.elevateNodesOnSelect && !gt(i.zIndexMode) ? lt : 0, c = e.length > 0, l = !1;
	t.clear(), n.clear();
	for (let u of e) {
		let e = o.get(u.id);
		if (i.checkEquality && u === e?.internals.userNode) t.set(u.id, e);
		else {
			let n = W(P(u, i.nodeOrigin), ve(u.extent) ? u.extent : i.nodeExtent, Y(u));
			e = {
				...i.defaults,
				...u,
				measured: {
					width: u.measured?.width,
					height: u.measured?.height
				},
				internals: {
					positionAbsolute: n,
					handleBounds: ht(u, e),
					z: bt(u, s, i.zIndexMode),
					userNode: u
				}
			}, t.set(u.id, e);
		}
		(e.measured === void 0 || e.measured.width === void 0 || e.measured.height === void 0) && !e.hidden && (c = !1), u.parentId && yt(e, t, n, r, a), l ||= u.selected ?? !1;
	}
	return {
		nodesInitialized: c,
		hasSelectedNodes: l
	};
}
function vt(e, t) {
	if (!e.parentId) return;
	let n = t.get(e.parentId);
	n ? n.set(e.id, e) : t.set(e.parentId, /* @__PURE__ */ new Map([[e.id, e]]));
}
function yt(e, t, n, r, i) {
	let { elevateNodesOnSelect: a, nodeOrigin: o, nodeExtent: s, zIndexMode: c } = pt(dt, r), l = e.parentId, u = t.get(l);
	if (!u) return;
	vt(e, n), i && !u.parentId && u.internals.rootParentIndex === void 0 && c === "auto" && (u.internals.rootParentIndex = ++i.i, u.internals.z = u.internals.z + i.i * ut), i && u.internals.rootParentIndex !== void 0 && (i.i = u.internals.rootParentIndex);
	let { x: d, y: f, z: p } = xt(e, u, o, s, a && !gt(c) ? lt : 0, c), { positionAbsolute: m } = e.internals, h = d !== m.x || f !== m.y;
	(h || p !== e.internals.z) && t.set(e.id, {
		...e,
		internals: {
			...e.internals,
			positionAbsolute: h ? {
				x: d,
				y: f
			} : m,
			z: p
		}
	});
}
function bt(e, t, n) {
	let r = J(e.zIndex) ? e.zIndex : 0;
	return gt(n) ? r : r + (e.selected ? t : 0);
}
function xt(e, t, n, r, i, a) {
	let { x: o, y: s } = t.internals.positionAbsolute, c = Y(e), l = P(e, n), u = ve(e.extent) ? W(l, e.extent, c) : l, d = W({
		x: o + u.x,
		y: s + u.y
	}, r, c);
	e.extent === "parent" && (d = G(d, c, t));
	let f = bt(e, i, a), p = t.internals.z ?? 0;
	return {
		x: d.x,
		y: d.y,
		z: p >= f ? p + 1 : f
	};
}
function St(e, t, n, r = [0, 0]) {
	let i = [], a = /* @__PURE__ */ new Map();
	for (let n of e) {
		let e = t.get(n.parentId);
		if (!e) continue;
		let r = ae(a.get(n.parentId)?.expandedRect ?? re(e), n.rect);
		a.set(n.parentId, {
			expandedRect: r,
			parent: e
		});
	}
	return a.size > 0 && a.forEach(({ expandedRect: t, parent: a }, o) => {
		let s = a.internals.positionAbsolute, c = Y(a), l = a.origin ?? r, u = t.x < s.x ? Math.round(Math.abs(s.x - t.x)) : 0, d = t.y < s.y ? Math.round(Math.abs(s.y - t.y)) : 0, f = Math.max(c.width, Math.round(t.width)), p = Math.max(c.height, Math.round(t.height)), m = (f - c.width) * l[0], h = (p - c.height) * l[1];
		(u > 0 || d > 0 || m || h) && (i.push({
			id: o,
			type: "position",
			position: {
				x: a.position.x - u + m,
				y: a.position.y - d + h
			}
		}), n.get(o)?.forEach((t) => {
			e.some((e) => e.id === t.id) || i.push({
				id: t.id,
				type: "position",
				position: {
					x: t.position.x + u,
					y: t.position.y + d
				}
			});
		})), (c.width < t.width || c.height < t.height || u || d) && i.push({
			id: o,
			type: "dimensions",
			setAttributes: !0,
			dimensions: {
				width: f + (u ? l[0] * u - m : 0),
				height: p + (d ? l[1] * d - h : 0)
			}
		});
	}), i;
}
function Ct(e, t, n, r, i, a, o) {
	let s = r?.querySelector(".xyflow__viewport"), c = !1;
	if (!s) return {
		changes: [],
		updatedInternals: c
	};
	let l = [], u = window.getComputedStyle(s), { m22: d } = new window.DOMMatrixReadOnly(u.transform), f = [];
	for (let r of e.values()) {
		let e = t.get(r.id);
		if (!e) continue;
		if (e.hidden) {
			t.set(e.id, {
				...e,
				internals: {
					...e.internals,
					handleBounds: void 0
				}
			}), c = !0;
			continue;
		}
		let s = Oe(r.nodeElement), u = e.measured.width !== s.width || e.measured.height !== s.height;
		if (s.width && s.height && (u || !e.internals.handleBounds || r.force)) {
			let p = r.nodeElement.getBoundingClientRect(), m = ve(e.extent) ? e.extent : a, { positionAbsolute: h } = e.internals;
			if (e.parentId && e.extent === "parent") {
				let n = t.get(e.parentId);
				n && (h = G(h, s, n));
			} else m && (h = W(h, m, s));
			let g = {
				...e,
				measured: s,
				internals: {
					...e.internals,
					positionAbsolute: h,
					handleBounds: {
						source: Ne("source", r.nodeElement, p, d, e.id),
						target: Ne("target", r.nodeElement, p, d, e.id)
					}
				}
			};
			t.set(e.id, g), e.parentId && yt(g, t, n, {
				nodeOrigin: i,
				zIndexMode: o
			}), c = !0, u && (l.push({
				id: e.id,
				type: "dimensions",
				dimensions: s
			}), e.expandParent && e.parentId && f.push({
				id: e.id,
				parentId: e.parentId,
				rect: re(g, i)
			}));
		}
	}
	if (f.length > 0) {
		let e = St(f, t, n, i);
		l.push(...e);
	}
	return {
		changes: l,
		updatedInternals: c
	};
}
async function wt({ delta: e, panZoom: t, transform: n, translateExtent: r, width: i, height: a }) {
	if (!t || !e.x && !e.y) return !1;
	let o = await t.setViewportConstrained({
		x: n[0] + e.x,
		y: n[1] + e.y,
		zoom: n[2]
	}, [[0, 0], [i, a]], r);
	return !!o && (o.x !== n[0] || o.y !== n[1] || o.k !== n[2]);
}
function Tt(e, t, n, r, i, a) {
	let o = i, s = r.get(o) || /* @__PURE__ */ new Map();
	r.set(o, s.set(n, t)), o = `${i}-${e}`;
	let c = r.get(o) || /* @__PURE__ */ new Map();
	if (r.set(o, c.set(n, t)), a) {
		o = `${i}-${e}-${a}`;
		let s = r.get(o) || /* @__PURE__ */ new Map();
		r.set(o, s.set(n, t));
	}
}
function Et(e, t, n) {
	e.clear(), t.clear();
	for (let r of n) {
		let { source: n, target: i, sourceHandle: a = null, targetHandle: o = null } = r, s = {
			edgeId: r.id,
			source: n,
			target: i,
			sourceHandle: a,
			targetHandle: o
		}, c = `${n}-${a}--${i}-${o}`;
		Tt("source", s, `${i}-${o}--${n}-${a}`, e, n, a), Tt("target", s, c, e, i, o), t.set(r.id, r);
	}
}
function Dt(e, t) {
	if (e === null || t === null) return !1;
	let n = Array.isArray(e) ? e : [e], r = Array.isArray(t) ? t : [t];
	if (n.length !== r.length) return !1;
	for (let e = 0; e < n.length; e++) if (n[e].id !== r[e].id || n[e].type !== r[e].type || !Object.is(n[e].data, r[e].data)) return !1;
	return !0;
}
function Ot(e, t) {
	if (!e.parentId) return !1;
	let n = t.get(e.parentId);
	return n ? n.selected ? !0 : Ot(n, t) : !1;
}
function kt(e, t, n) {
	let r = e;
	do {
		if (r?.matches?.(t)) return !0;
		if (r === n) return !1;
		r = r?.parentElement;
	} while (r);
	return !1;
}
function At(e, t, n, r) {
	let i = /* @__PURE__ */ new Map();
	for (let [a, o] of e) if ((o.selected || o.id === r) && (!o.parentId || !Ot(o, e)) && (o.draggable || t && o.draggable === void 0)) {
		let t = e.get(a);
		t && i.set(a, {
			id: a,
			position: t.position || {
				x: 0,
				y: 0
			},
			distance: {
				x: n.x - t.internals.positionAbsolute.x,
				y: n.y - t.internals.positionAbsolute.y
			},
			extent: t.extent,
			parentId: t.parentId,
			origin: t.origin,
			expandParent: t.expandParent,
			internals: { positionAbsolute: t.internals.positionAbsolute || {
				x: 0,
				y: 0
			} },
			measured: {
				width: t.measured.width ?? 0,
				height: t.measured.height ?? 0
			}
		});
	}
	return i;
}
function jt({ nodeId: e, dragItems: t, nodeLookup: n, dragging: r = !0 }) {
	let i = [];
	for (let [e, a] of t) {
		let t = n.get(e)?.internals.userNode;
		t && i.push({
			...t,
			position: a.position,
			dragging: r
		});
	}
	if (!e) return [i[0], i];
	let a = n.get(e)?.internals.userNode;
	return [a ? {
		...a,
		position: t.get(e)?.position || a.position,
		dragging: r
	} : i[0], i];
}
function Mt({ dragItems: e, snapGrid: t, x: n, y: r }) {
	let i = e.values().next().value;
	if (!i) return null;
	let a = {
		x: n - i.distance.x,
		y: r - i.distance.y
	}, o = ue(a, t);
	return {
		x: o.x - a.x,
		y: o.y - a.y
	};
}
function Nt({ onNodeMouseDown: e, getStoreItems: t, onDragStart: n, onDrag: r, onDragStop: i }) {
	let a = {
		x: null,
		y: null
	}, s = 0, c = /* @__PURE__ */ new Map(), l = !1, u = {
		x: 0,
		y: 0
	}, d = null, p = !1, m = null, h = !1, g = !1, _ = null;
	function v({ noDragClassName: v, handleSelector: y, domNode: b, isSelectable: x, nodeId: S, nodeClickDistance: C = 0 }) {
		m = o(b);
		function w({ x: e, y: n }) {
			let { nodeLookup: i, nodeExtent: o, snapGrid: s, snapToGrid: l, nodeOrigin: u, onNodeDrag: d, onSelectionDrag: f, onError: p, updateNodePositions: m } = t();
			a = {
				x: e,
				y: n
			};
			let h = !1, v = c.size > 1, y = v && o ? te(I(c)) : null, b = v && l ? Mt({
				dragItems: c,
				snapGrid: s,
				x: e,
				y: n
			}) : null;
			for (let [t, r] of c) {
				if (!i.has(t)) continue;
				let a = {
					x: e - r.distance.x,
					y: n - r.distance.y
				};
				l && (a = b ? {
					x: Math.round(a.x + b.x),
					y: Math.round(a.y + b.y)
				} : ue(a, s));
				let c = null;
				if (v && o && !r.extent && y) {
					let { positionAbsolute: e } = r.internals, t = e.x - y.x + o[0][0], n = e.x + r.measured.width - y.x2 + o[1][0], i = e.y - y.y + o[0][1], a = e.y + r.measured.height - y.y2 + o[1][1];
					c = [[t, i], [n, a]];
				}
				let { position: d, positionAbsolute: f } = V({
					nodeId: t,
					nextPosition: a,
					nodeLookup: i,
					nodeExtent: c || o,
					nodeOrigin: u,
					onError: p
				});
				h = h || r.position.x !== d.x || r.position.y !== d.y, r.position = d, r.internals.positionAbsolute = f;
			}
			if (g ||= h, h && (m(c, !0), _ && (r || d || !S && f))) {
				let [e, t] = jt({
					nodeId: S,
					dragItems: c,
					nodeLookup: i
				});
				r?.(_, c, e, t), d?.(_, e, t), S || f?.(_, t);
			}
		}
		async function T() {
			if (!d) return;
			let { transform: e, panBy: n, autoPanSpeed: r, autoPanOnNodeDrag: i } = t();
			if (!i) {
				l = !1, cancelAnimationFrame(s);
				return;
			}
			let [o, c] = ee(u, d, r);
			(o !== 0 || c !== 0) && (a.x = (a.x ?? 0) - o / e[2], a.y = (a.y ?? 0) - c / e[2], await n({
				x: o,
				y: c
			}) && w(a)), s = requestAnimationFrame(T);
		}
		function E(r) {
			let { nodeLookup: i, multiSelectionActive: o, nodesDraggable: s, transform: l, snapGrid: u, snapToGrid: f, selectNodesOnDrag: m, onNodeDragStart: h, onSelectionDragStart: g, unselectNodesAndEdges: _ } = t();
			p = !0, (!m || !x) && !o && S && (i.get(S)?.selected || _()), x && m && S && e?.(S);
			let v = De(r.sourceEvent, {
				transform: l,
				snapGrid: u,
				snapToGrid: f,
				containerBounds: d
			});
			if (a = v, c = At(i, s, v, S), c.size > 0 && (n || h || !S && g)) {
				let [e, t] = jt({
					nodeId: S,
					dragItems: c,
					nodeLookup: i
				});
				n?.(r.sourceEvent, c, e, t), h?.(r.sourceEvent, e, t), S || g?.(r.sourceEvent, t);
			}
		}
		let D = f().clickDistance(C).on("start", (e) => {
			let { domNode: n, nodeDragThreshold: r, transform: i, snapGrid: o, snapToGrid: s } = t();
			d = n?.getBoundingClientRect() || null, h = !1, g = !1, _ = e.sourceEvent, r === 0 && E(e), a = De(e.sourceEvent, {
				transform: i,
				snapGrid: o,
				snapToGrid: s,
				containerBounds: d
			}), u = X(e.sourceEvent, d);
		}).on("drag", (e) => {
			let { autoPanOnNodeDrag: n, transform: r, snapGrid: i, snapToGrid: o, nodeDragThreshold: s, nodeLookup: f } = t(), m = De(e.sourceEvent, {
				transform: r,
				snapGrid: i,
				snapToGrid: o,
				containerBounds: d
			});
			if (_ = e.sourceEvent, (e.sourceEvent.type === "touchmove" && e.sourceEvent.touches.length > 1 || S && !f.has(S)) && (h = !0), !h) {
				if (!l && n && p && (l = !0, T()), !p) {
					let t = X(e.sourceEvent, d), n = t.x - u.x, r = t.y - u.y;
					Math.sqrt(n * n + r * r) > s && E(e);
				}
				(a.x !== m.xSnapped || a.y !== m.ySnapped) && c && p && (u = X(e.sourceEvent, d), w(m));
			}
		}).on("end", (e) => {
			if (!p || h) h && c.size > 0 && t().updateNodePositions(c, !1);
			else if (l = !1, p = !1, cancelAnimationFrame(s), c.size > 0) {
				let { nodeLookup: n, updateNodePositions: r, onNodeDragStop: a, onSelectionDragStop: o } = t();
				if (g &&= (r(c, !1), !1), i || a || !S && o) {
					let [t, r] = jt({
						nodeId: S,
						dragItems: c,
						nodeLookup: n,
						dragging: !1
					});
					i?.(e.sourceEvent, c, t, r), a?.(e.sourceEvent, t, r), S || o?.(e.sourceEvent, r);
				}
			}
		}).filter((e) => {
			let t = e.target;
			return !e.button && (!v || !kt(t, `.${v}`, b)) && (!y || kt(t, y, b));
		});
		m.call(D);
	}
	function y() {
		m?.on(".drag", null);
	}
	return {
		update: v,
		destroy: y
	};
}
function Pt(e, t, n) {
	let r = [], i = {
		x: e.x - n,
		y: e.y - n,
		width: n * 2,
		height: n * 2
	};
	for (let e of t.values()) se(i, re(e)) > 0 && r.push(e);
	return r;
}
var Ft = 250;
function It(e, t, n, r) {
	let i = [], a = Infinity, o = Pt(e, n, t + Ft);
	for (let n of o) {
		let o = [...n.internals.handleBounds?.source ?? [], ...n.internals.handleBounds?.target ?? []];
		for (let s of o) {
			if (r.nodeId === s.nodeId && r.type === s.type && r.id === s.id) continue;
			let { x: o, y: c } = tt(n, s, s.position, !0), l = Math.sqrt((o - e.x) ** 2 + (c - e.y) ** 2);
			l > t || (l < a ? (i = [{
				...s,
				x: o,
				y: c
			}], a = l) : l === a && i.push({
				...s,
				x: o,
				y: c
			}));
		}
	}
	if (!i.length) return null;
	if (i.length > 1) {
		let e = r.type === "source" ? "target" : "source";
		return i.find((t) => t.type === e) ?? i[0];
	}
	return i[0];
}
function Lt(e, t, n, r, i, a = !1) {
	let o = r.get(e);
	if (!o) return null;
	let s = i === "strict" ? o.internals.handleBounds?.[t] : [...o.internals.handleBounds?.source ?? [], ...o.internals.handleBounds?.target ?? []], c = (n ? s?.find((e) => e.id === n) : s?.[0]) ?? null;
	return c && a ? {
		...c,
		...tt(o, c, c.position, !0)
	} : c;
}
function Rt(e, t) {
	return e || (t?.classList.contains("target") ? "target" : t?.classList.contains("source") ? "source" : null);
}
function zt(e, t) {
	let n = null;
	return t ? n = !0 : e && !t && (n = !1), n;
}
var Bt = () => !0;
function Vt(e, { connectionMode: t, connectionRadius: n, handleId: r, nodeId: i, edgeUpdaterType: a, isTarget: o, domNode: s, nodeLookup: c, lib: l, autoPanOnConnect: u, flowId: d, panBy: f, cancelConnection: p, onConnectStart: m, onConnect: h, onConnectEnd: g, isValidConnection: _ = Bt, onReconnectEnd: v, updateConnection: y, getTransform: b, getFromHandle: x, autoPanSpeed: S, dragThreshold: C = 1, handleDomNode: w }) {
	let T = ke(e.target), E = 0, k, { x: A, y: j } = X(e), M = Rt(a, w), N = s?.getBoundingClientRect(), P = !1;
	if (!N || !M) return;
	let F = Lt(i, M, r, c, t);
	if (!F) return;
	let I = X(e, N), L = !1, R = null, z = !1, B = null;
	function V() {
		if (!u || !N) return;
		let [e, t] = ee(I, N, S);
		f({
			x: e,
			y: t
		}), E = requestAnimationFrame(V);
	}
	let H = {
		...F,
		nodeId: i,
		type: M,
		position: F.position
	}, U = c.get(i), W = {
		inProgress: !0,
		isValid: null,
		from: tt(U, H, D.Left, !0),
		fromHandle: H,
		fromPosition: H.position,
		fromNode: U,
		to: I,
		toHandle: null,
		toPosition: O[H.position],
		toNode: null,
		pointer: I
	};
	function G() {
		P = !0, y(W), m?.(e, {
			nodeId: i,
			handleId: r,
			handleType: M
		});
	}
	C === 0 && G();
	function K(e) {
		if (!P) {
			let { x: t, y: n } = X(e), r = t - A, i = n - j;
			if (!(r * r + i * i > C * C)) return;
			G();
		}
		if (!x() || !H) {
			q(e);
			return;
		}
		let a = b();
		I = X(e, N), k = It(de(I, a, !1, [1, 1]), n, c, H), L ||= (V(), !0);
		let s = Ht(e, {
			handle: k,
			connectionMode: t,
			fromNodeId: i,
			fromHandleId: r,
			fromType: o ? "target" : "source",
			isValidConnection: _,
			doc: T,
			lib: l,
			flowId: d,
			nodeLookup: c
		});
		B = s.handleDomNode, R = s.connection, z = zt(!!k, s.isValid);
		let u = c.get(i), f = u ? tt(u, H, D.Left, !0) : W.from, p = {
			...W,
			from: f,
			isValid: z,
			to: s.toHandle && z ? fe({
				x: s.toHandle.x,
				y: s.toHandle.y
			}, a) : I,
			toHandle: s.toHandle,
			toPosition: z && s.toHandle ? s.toHandle.position : O[H.position],
			toNode: s.toHandle ? c.get(s.toHandle.nodeId) : null,
			pointer: I
		};
		y(p), W = p;
	}
	function q(e) {
		if (!("touches" in e && e.touches.length > 0)) {
			if (P) {
				(k || B) && R && z && h?.(R);
				let { inProgress: t, ...n } = W, r = {
					...n,
					toPosition: W.toHandle ? W.toPosition : null
				};
				g?.(e, r), a && v?.(e, r);
			}
			p(), cancelAnimationFrame(E), L = !1, z = !1, R = null, B = null, T.removeEventListener("mousemove", K), T.removeEventListener("mouseup", q), T.removeEventListener("touchmove", K), T.removeEventListener("touchend", q);
		}
	}
	T.addEventListener("mousemove", K), T.addEventListener("mouseup", q), T.addEventListener("touchmove", K), T.addEventListener("touchend", q);
}
function Ht(e, { handle: t, connectionMode: n, fromNodeId: r, fromHandleId: i, fromType: a, doc: o, lib: s, flowId: c, isValidConnection: l = Bt, nodeLookup: u }) {
	let d = a === "target", f = t ? o.querySelector(`.${s}-flow__handle[data-id="${c}-${t?.nodeId}-${t?.id}-${t?.type}"]`) : null, { x: p, y: m } = X(e), h = o.elementFromPoint(p, m), g = h?.classList.contains(`${s}-flow__handle`) ? h : f, _ = {
		handleDomNode: g,
		isValid: !1,
		connection: null,
		toHandle: null
	};
	if (g) {
		let e = Rt(void 0, g), t = g.getAttribute("data-nodeid"), a = g.getAttribute("data-handleid"), o = g.classList.contains("connectable"), s = g.classList.contains("connectableend");
		if (!t || !e) return _;
		let c = {
			source: d ? t : r,
			sourceHandle: d ? a : i,
			target: d ? r : t,
			targetHandle: d ? i : a
		};
		_.connection = c, _.isValid = o && s && (n === x.Strict ? d && e === "source" || !d && e === "target" : t !== r || a !== i) && l(c), _.toHandle = Lt(t, e, a, u, n, !0);
	}
	return _;
}
var Ut = {
	onPointerDown: Vt,
	isValid: Ht
};
function Wt({ domNode: e, panZoom: t, getTransform: n, getViewScale: r }) {
	let i = o(e);
	function a({ translateExtent: e, width: a, height: o, zoomStep: s = 1, pannable: c = !0, zoomable: l = !0, inversePan: d = !1 }) {
		let f = (e) => {
			if (e.sourceEvent.type !== "wheel" || !t) return;
			let r = n(), i = e.sourceEvent.ctrlKey && _e() ? 10 : 1, a = -e.sourceEvent.deltaY * (e.sourceEvent.deltaMode === 1 ? .05 : e.sourceEvent.deltaMode ? 1 : .002) * s, o = r[2] * 2 ** (a * i);
			t.scaleTo(o);
		}, p = [0, 0], m = u().on("start", (e) => {
			(e.sourceEvent.type === "mousedown" || e.sourceEvent.type === "touchstart") && (p = [e.sourceEvent.clientX ?? e.sourceEvent.touches[0].clientX, e.sourceEvent.clientY ?? e.sourceEvent.touches[0].clientY]);
		}).on("zoom", c ? (i) => {
			let s = n();
			if (i.sourceEvent.type !== "mousemove" && i.sourceEvent.type !== "touchmove" || !t) return;
			let c = [i.sourceEvent.clientX ?? i.sourceEvent.touches[0].clientX, i.sourceEvent.clientY ?? i.sourceEvent.touches[0].clientY], l = [c[0] - p[0], c[1] - p[1]];
			p = c;
			let u = r() * Math.max(s[2], Math.log(s[2])) * (d ? -1 : 1), f = {
				x: s[0] - l[0] * u,
				y: s[1] - l[1] * u
			}, m = [[0, 0], [a, o]];
			t.setViewportConstrained({
				x: f.x,
				y: f.y,
				zoom: s[2]
			}, m, e);
		} : null).on("zoom.wheel", l ? f : null);
		i.call(m, {});
	}
	function s() {
		i.on("zoom", null);
	}
	return {
		update: a,
		destroy: s,
		pointer: d
	};
}
var Gt = (e) => ({
	x: e.x,
	y: e.y,
	zoom: e.k
}), Kt = ({ x: e, y: t, zoom: n }) => l.translate(e, t).scale(n), qt = (e, t) => e.target.closest(`.${t}`), Jt = (e, t) => t === 2 && Array.isArray(e) && e.includes(2), Yt = (e) => ((e *= 2) <= 1 ? e * e * e : (e -= 2) * e * e + 2) / 2, Xt = (e, t = 0, n = Yt, r = () => {}) => {
	let i = typeof t == "number" && t > 0;
	return i || r(), i ? e.transition().duration(t).ease(n).on("end", r) : e;
}, Zt = (e) => {
	let t = e.ctrlKey && _e() ? 10 : 1;
	return -e.deltaY * (e.deltaMode === 1 ? .05 : e.deltaMode ? 1 : .002) * t;
};
function Qt({ zoomPanValues: e, noWheelClassName: t, d3Selection: n, d3Zoom: r, panOnScrollMode: i, panOnScrollSpeed: a, zoomOnPinch: o, onPanZoomStart: s, onPanZoom: c, onPanZoomEnd: l }) {
	return (u) => {
		if (qt(u, t)) return u.ctrlKey && u.preventDefault(), !1;
		u.preventDefault(), u.stopImmediatePropagation();
		let f = n.property("__zoom").k || 1;
		if (u.ctrlKey && o) {
			let e = d(u), t = f * 2 ** Zt(u);
			r.scaleTo(n, t, e, u);
			return;
		}
		let p = u.deltaMode === 1 ? 20 : 1, m = i === S.Vertical ? 0 : u.deltaX * p, h = i === S.Horizontal ? 0 : u.deltaY * p;
		!_e() && u.shiftKey && i !== S.Vertical && (m = u.deltaY * p, h = 0), r.translateBy(n, -(m / f) * a, -(h / f) * a, { internal: !0 });
		let g = Gt(n.property("__zoom"));
		clearTimeout(e.panScrollTimeout), e.isPanScrolling ? c?.(u, g) : (e.isPanScrolling = !0, s?.(u, g)), e.panScrollTimeout = setTimeout(() => {
			l?.(u, g), e.isPanScrolling = !1;
		}, 150);
	};
}
function $t({ noWheelClassName: e, preventScrolling: t, d3ZoomHandler: n }) {
	return function(r, i) {
		let a = r.type === "wheel", o = !t && a && !r.ctrlKey, s = qt(r, e);
		if (r.ctrlKey && a && s && r.preventDefault(), o || s) return null;
		r.preventDefault(), n.call(this, r, i);
	};
}
function en({ zoomPanValues: e, onDraggingChange: t, onPanZoomStart: n }) {
	return (r) => {
		if (r.sourceEvent?.internal) return;
		let i = Gt(r.transform);
		e.mouseButton = r.sourceEvent?.button || 0, e.isZoomingOrPanning = !0, e.prevViewport = i, r.sourceEvent?.type === "mousedown" && t(!0), n && n?.(r.sourceEvent, i);
	};
}
function tn({ zoomPanValues: e, panOnDrag: t, onPaneContextMenu: n, onTransformChange: r, onPanZoom: i }) {
	return (a) => {
		e.usedRightMouseButton = !!(n && Jt(t, e.mouseButton ?? 0)), a.sourceEvent?.sync || r([
			a.transform.x,
			a.transform.y,
			a.transform.k
		]), i && !a.sourceEvent?.internal && i?.(a.sourceEvent, Gt(a.transform));
	};
}
function nn({ zoomPanValues: e, panOnDrag: t, panOnScroll: n, onDraggingChange: r, onPanZoomEnd: i, onPaneContextMenu: a }) {
	return (o) => {
		if (!o.sourceEvent?.internal && (e.isZoomingOrPanning = !1, a && Jt(t, e.mouseButton ?? 0) && !e.usedRightMouseButton && o.sourceEvent && a(o.sourceEvent), e.usedRightMouseButton = !1, r(!1), i)) {
			let t = Gt(o.transform);
			e.prevViewport = t, clearTimeout(e.timerId), e.timerId = setTimeout(() => {
				i?.(o.sourceEvent, t);
			}, n ? 150 : 0);
		}
	};
}
function rn({ panActivationKeyPressed: e, zoomActivationKeyPressed: t, zoomOnScroll: n, zoomOnPinch: r, panOnDrag: i, panOnScroll: a, zoomOnDoubleClick: o, userSelectionActive: s, noWheelClassName: c, noPanClassName: l, lib: u, connectionInProgress: d }) {
	return (f) => {
		let p = t || n, m = r && f.ctrlKey, h = f.type === "wheel";
		if (f.button === 1 && f.type === "mousedown" && (qt(f, `${u}-flow__node`) || qt(f, `${u}-flow__edge`) || qt(f, `${u}-flow__selection`) || qt(f, `${u}-flow__nodesselection`))) return !0;
		if (!i && !p && !a && !o && !r || s || d && !h || qt(f, c) && h || qt(f, l) && (!h || a && h && !t) || !r && f.ctrlKey && h) return !1;
		if (!r && f.type === "touchstart" && f.touches?.length > 1) return f.preventDefault(), !1;
		if (!p && !a && !m && h || !i && (f.type === "mousedown" || f.type === "touchstart") || Array.isArray(i) && !i.includes(f.button) && f.type === "mousedown") return !1;
		let g = Array.isArray(i) && i.includes(f.button) || !f.button || f.button <= 1;
		return (!f.ctrlKey || h || e) && g;
	};
}
function an({ domNode: e, minZoom: t, maxZoom: n, translateExtent: r, viewport: i, onPanZoom: a, onPanZoomStart: l, onPanZoomEnd: d, onDraggingChange: f }) {
	let m = {
		isZoomingOrPanning: !1,
		usedRightMouseButton: !1,
		prevViewport: {},
		mouseButton: 0,
		timerId: void 0,
		panScrollTimeout: void 0,
		isPanScrolling: !1
	}, h = e.getBoundingClientRect(), g = [[0, 0], [h.width, h.height]];
	(typeof ResizeObserver < "u" ? new ResizeObserver((e) => {
		let t = e[0];
		t && (g = [[0, 0], [t.contentRect.width, t.contentRect.height]]);
	}) : null)?.observe(e);
	let _ = u().extent(() => g).scaleExtent([t, n]).translateExtent(r), v = o(e).call(_);
	w({
		x: i.x,
		y: i.y,
		zoom: U(i.zoom, t, n)
	}, [[0, 0], [h.width, h.height]], r);
	let y = v.on("wheel.zoom"), b = v.on("dblclick.zoom");
	_.wheelDelta(Zt);
	async function x(e, t) {
		return v ? new Promise((n) => {
			_?.interpolate(t?.interpolate === "linear" ? p : s).transform(Xt(v, t?.duration, t?.ease, () => n(!0)), e);
		}) : !1;
	}
	function S({ noWheelClassName: e, noPanClassName: t, onPaneContextMenu: n, userSelectionActive: r, panOnScroll: i, panOnDrag: o, panOnScrollMode: s, panOnScrollSpeed: c, preventScrolling: u, zoomOnPinch: p, zoomOnScroll: h, zoomOnDoubleClick: g, panActivationKeyPressed: x = !1, zoomActivationKeyPressed: S, lib: w, onTransformChange: T, connectionInProgress: E, paneClickDistance: D, selectionOnDrag: O }) {
		r && !m.isZoomingOrPanning && C();
		let k = i && !S && !r;
		_.clickDistance(O ? Infinity : !J(D) || D < 0 ? 0 : D);
		let A = k ? Qt({
			zoomPanValues: m,
			noWheelClassName: e,
			d3Selection: v,
			d3Zoom: _,
			panOnScrollMode: s,
			panOnScrollSpeed: c,
			zoomOnPinch: p,
			onPanZoomStart: l,
			onPanZoom: a,
			onPanZoomEnd: d
		}) : $t({
			noWheelClassName: e,
			preventScrolling: u,
			d3ZoomHandler: y
		});
		v.on("wheel.zoom", A, { passive: !1 });
		let j = en({
			zoomPanValues: m,
			onDraggingChange: f,
			onPanZoomStart: l
		});
		_.on("start", j);
		let M = tn({
			zoomPanValues: m,
			panOnDrag: o,
			onPaneContextMenu: !!n,
			onPanZoom: a,
			onTransformChange: T
		});
		_.on("zoom", M);
		let N = nn({
			zoomPanValues: m,
			panOnDrag: o,
			panOnScroll: i,
			onPaneContextMenu: n,
			onPanZoomEnd: d,
			onDraggingChange: f
		});
		_.on("end", N);
		let P = rn({
			panActivationKeyPressed: x,
			zoomActivationKeyPressed: S,
			panOnDrag: o,
			zoomOnScroll: h,
			panOnScroll: i,
			zoomOnDoubleClick: g,
			zoomOnPinch: p,
			userSelectionActive: r,
			noPanClassName: t,
			noWheelClassName: e,
			lib: w,
			connectionInProgress: E
		});
		_.filter(P), g ? v.on("dblclick.zoom", b) : v.on("dblclick.zoom", null);
	}
	function C() {
		_.on("zoom", null);
	}
	async function w(e, t, n) {
		let r = Kt(e), i = _?.constrain()(r, t, n);
		return i && await x(i), i;
	}
	async function T(e, t) {
		let n = Kt(e);
		return await x(n, t), n;
	}
	function E(e) {
		if (v) {
			let t = Kt(e), n = v.property("__zoom");
			(n.k !== e.zoom || n.x !== e.x || n.y !== e.y) && _?.transform(v, t, null, { sync: !0 });
		}
	}
	function D() {
		let e = v ? c(v.node()) : {
			x: 0,
			y: 0,
			k: 1
		};
		return {
			x: e.x,
			y: e.y,
			zoom: e.k
		};
	}
	async function O(e, t) {
		return v ? new Promise((n) => {
			_?.interpolate(t?.interpolate === "linear" ? p : s).scaleTo(Xt(v, t?.duration, t?.ease, () => n(!0)), e);
		}) : !1;
	}
	async function k(e, t) {
		return v ? new Promise((n) => {
			_?.interpolate(t?.interpolate === "linear" ? p : s).scaleBy(Xt(v, t?.duration, t?.ease, () => n(!0)), e);
		}) : !1;
	}
	function A(e) {
		_?.scaleExtent(e);
	}
	function j(e) {
		_?.translateExtent(e);
	}
	function M(e) {
		let t = !J(e) || e < 0 ? 0 : e;
		_?.clickDistance(t);
	}
	return {
		update: S,
		destroy: C,
		setViewport: T,
		setViewportConstrained: w,
		getViewport: D,
		scaleTo: O,
		scaleBy: k,
		setScaleExtent: A,
		setTranslateExtent: j,
		syncViewport: E,
		setClickDistance: M
	};
}
var on;
(function(e) {
	e.Line = "line", e.Handle = "handle";
})(on ||= {});
var sn = [
	"top-left",
	"top-right",
	"bottom-left",
	"bottom-right"
], cn = [
	"top",
	"right",
	"bottom",
	"left"
];
function ln({ width: e, prevWidth: t, height: n, prevHeight: r, affectsX: i, affectsY: a }) {
	let o = e - t, s = n - r, c = [o > 0 ? 1 : o < 0 ? -1 : 0, s > 0 ? 1 : s < 0 ? -1 : 0];
	return o && i && (c[0] *= -1), s && a && (c[1] *= -1), c;
}
function un(e) {
	return {
		isHorizontal: e.includes("right") || e.includes("left"),
		isVertical: e.includes("bottom") || e.includes("top"),
		affectsX: e.includes("left"),
		affectsY: e.includes("top")
	};
}
function dn(e, t) {
	return Math.max(0, t - e);
}
function fn(e, t) {
	return Math.max(0, e - t);
}
function pn(e, t, n) {
	return Math.max(0, t - e, e - n);
}
function mn(e, t) {
	return e ? !t : t;
}
function hn(e, t, n, r, i, a, o, s) {
	let { affectsX: c, affectsY: l } = t, { isHorizontal: u, isVertical: d } = t, f = u && d, { xSnapped: p, ySnapped: m } = n, { minWidth: h, maxWidth: g, minHeight: _, maxHeight: v } = r, { x: y, y: b, width: x, height: S, aspectRatio: C } = e, w = Math.floor(u ? p - e.pointerX : 0), T = Math.floor(d ? m - e.pointerY : 0), E = x + (c ? -w : w), D = S + (l ? -T : T), O = -a[0] * x, k = -a[1] * S, A = pn(E, h, g), j = pn(D, _, v);
	if (o) {
		let e = 0, t = 0;
		c && w < 0 ? e = dn(y + w + O, o[0][0]) : !c && w > 0 && (e = fn(y + E + O, o[1][0])), l && T < 0 ? t = dn(b + T + k, o[0][1]) : !l && T > 0 && (t = fn(b + D + k, o[1][1])), A = Math.max(A, e), j = Math.max(j, t);
	}
	if (s) {
		let e = 0, t = 0;
		c && w > 0 ? e = fn(y + w, s[0][0]) : !c && w < 0 && (e = dn(y + E, s[1][0])), l && T > 0 ? t = fn(b + T, s[0][1]) : !l && T < 0 && (t = dn(b + D, s[1][1])), A = Math.max(A, e), j = Math.max(j, t);
	}
	if (i) {
		if (u) {
			let e = pn(E / C, _, v) * C;
			if (A = Math.max(A, e), o) {
				let e = 0;
				e = !c && !l || c && !l && f ? fn(b + k + E / C, o[1][1]) * C : dn(b + k + (c ? w : -w) / C, o[0][1]) * C, A = Math.max(A, e);
			}
			if (s) {
				let e = 0;
				e = !c && !l || c && !l && f ? dn(b + E / C, s[1][1]) * C : fn(b + (c ? w : -w) / C, s[0][1]) * C, A = Math.max(A, e);
			}
		}
		if (d) {
			let e = pn(D * C, h, g) / C;
			if (j = Math.max(j, e), o) {
				let e = 0;
				e = !c && !l || l && !c && f ? fn(y + D * C + O, o[1][0]) / C : dn(y + (l ? T : -T) * C + O, o[0][0]) / C, j = Math.max(j, e);
			}
			if (s) {
				let e = 0;
				e = !c && !l || l && !c && f ? dn(y + D * C, s[1][0]) / C : fn(y + (l ? T : -T) * C, s[0][0]) / C, j = Math.max(j, e);
			}
		}
	}
	T += T < 0 ? j : -j, w += w < 0 ? A : -A, i && (f ? E > D * C ? T = (mn(c, l) ? -w : w) / C : w = (mn(c, l) ? -T : T) * C : u ? (T = w / C, l = c) : (w = T * C, c = l));
	let M = c ? y + w : y, N = l ? b + T : b;
	return {
		width: x + (c ? -w : w),
		height: S + (l ? -T : T),
		x: a[0] * w * (c ? -1 : 1) + M,
		y: a[1] * T * (l ? -1 : 1) + N
	};
}
var gn = {
	width: 0,
	height: 0,
	x: 0,
	y: 0
}, _n = {
	...gn,
	pointerX: 0,
	pointerY: 0,
	aspectRatio: 1
};
function vn(e, t, n) {
	let r = t.position.x + e.position.x, i = t.position.y + e.position.y, a = e.measured.width ?? 0, o = e.measured.height ?? 0, s = n[0] * a, c = n[1] * o;
	return [[r - s, i - c], [r + a - s, i + o - c]];
}
function yn({ domNode: e, nodeId: t, getStoreItems: n, onChange: r, onEnd: i }) {
	let a = o(e), s = {
		controlDirection: un("bottom-right"),
		boundaries: {
			minWidth: 0,
			minHeight: 0,
			maxWidth: Number.MAX_VALUE,
			maxHeight: Number.MAX_VALUE
		},
		resizeDirection: void 0,
		keepAspectRatio: !1
	};
	function c({ controlPosition: e, boundaries: o, keepAspectRatio: c, resizeDirection: l, onResizeStart: u, onResize: d, onResizeEnd: p, shouldResize: m }) {
		let h = { ...gn }, g = { ..._n };
		s = {
			boundaries: o,
			resizeDirection: l,
			keepAspectRatio: c,
			controlDirection: un(e)
		};
		let _, v = null, y = [], b, x, S, C = f().on("start", (e) => {
			let { nodeLookup: r, transform: i, snapGrid: a, snapToGrid: o, nodeOrigin: s, paneDomNode: c } = n();
			if (_ = r.get(t), !_) return;
			v = c?.getBoundingClientRect() ?? null;
			let { xSnapped: l, ySnapped: d } = De(e.sourceEvent, {
				transform: i,
				snapGrid: a,
				snapToGrid: o,
				containerBounds: v
			});
			h = {
				width: _.measured.width ?? 0,
				height: _.measured.height ?? 0,
				x: _.position.x ?? 0,
				y: _.position.y ?? 0
			}, g = {
				...h,
				pointerX: l,
				pointerY: d,
				aspectRatio: h.width / h.height
			}, b = void 0, x = ve(_.extent) ? _.extent : void 0, _.parentId && (_.extent === "parent" || _.expandParent) && (b = r.get(_.parentId)), b && _.extent === "parent" && (x = [[0, 0], [b.measured.width, b.measured.height]]), y = [], S = void 0;
			for (let [e, n] of r) if (n.parentId === t && (y.push({
				id: e,
				position: { ...n.position },
				extent: n.extent
			}), n.extent === "parent" || n.expandParent)) {
				let e = vn(n, _, n.origin ?? s);
				S = S ? [[Math.min(e[0][0], S[0][0]), Math.min(e[0][1], S[0][1])], [Math.max(e[1][0], S[1][0]), Math.max(e[1][1], S[1][1])]] : e;
			}
			u?.(e, { ...h });
		}).on("drag", (e) => {
			let { transform: t, snapGrid: i, snapToGrid: a, nodeOrigin: o } = n(), c = De(e.sourceEvent, {
				transform: t,
				snapGrid: i,
				snapToGrid: a,
				containerBounds: v
			}), l = [];
			if (!_) return;
			let { x: u, y: f, width: p, height: C } = h, w = {}, T = _.origin ?? o, { width: E, height: D, x: O, y: k } = hn(g, s.controlDirection, c, s.boundaries, s.keepAspectRatio, T, x, S), A = E !== p, j = D !== C, M = O !== u && A, N = k !== f && j;
			if (!M && !N && !A && !j) return;
			let P = {
				prevValues: { ...h },
				startX: g.x,
				startY: g.y,
				childNodes: y.map((e) => ({
					...e,
					position: { ...e.position }
				}))
			};
			if ((M || N || T[0] === 1 || T[1] === 1) && (w.x = M ? O : h.x, w.y = N ? k : h.y, h.x = w.x, h.y = w.y, y.length > 0)) {
				let e = O - u, t = k - f;
				for (let n of y) n.position = {
					x: n.position.x - e + T[0] * (E - p),
					y: n.position.y - t + T[1] * (D - C)
				}, l.push(n);
			}
			if ((A || j) && (w.width = A && (!s.resizeDirection || s.resizeDirection === "horizontal") ? E : h.width, w.height = j && (!s.resizeDirection || s.resizeDirection === "vertical") ? D : h.height, h.width = w.width, h.height = w.height), b && _.expandParent) {
				let e = T[0] * (w.width ?? 0);
				w.x && w.x < e && (h.x = e, g.x -= w.x - e);
				let t = T[1] * (w.height ?? 0);
				w.y && w.y < t && (h.y = t, g.y -= w.y - t);
			}
			let F = ln({
				width: h.width,
				prevWidth: p,
				height: h.height,
				prevHeight: C,
				affectsX: s.controlDirection.affectsX,
				affectsY: s.controlDirection.affectsY
			}), I = {
				...h,
				direction: F
			};
			m?.(e, I) === !1 ? (h = P.prevValues, g.x = P.startX, g.y = P.startY, y.forEach((e, t) => {
				e.position = P.childNodes[t].position;
			})) : (d?.(e, I), r(w, l));
		}).on("end", (e) => {
			p?.(e, { ...h }), i?.({ ...h });
		});
		a.call(C);
	}
	function l() {
		a.on(".drag", null);
	}
	return {
		update: c,
		destroy: l
	};
}
//#endregion
//#region ../../../resource_engines/node_modules/zustand/esm/traditional.mjs
var bn = /* @__PURE__ */ e(a(), 1), { useDebugValue: xn } = m.default, { useSyncExternalStoreWithSelector: Sn } = bn.default, Cn = (e) => e;
function wn(e, t = Cn, n) {
	let r = Sn(e.subscribe, e.getState, e.getServerState || e.getInitialState, t, n);
	return xn(r), r;
}
var Tn = (e, t) => {
	let n = i(e), r = (e, r = t) => wn(n, e, r);
	return Object.assign(r, n), r;
}, En = (e, t) => e ? Tn(e, t) : Tn;
//#endregion
//#region ../../../resource_engines/node_modules/zustand/esm/shallow.mjs
function Z(e, t) {
	if (Object.is(e, t)) return !0;
	if (typeof e != "object" || !e || typeof t != "object" || !t) return !1;
	if (e instanceof Map && t instanceof Map) {
		if (e.size !== t.size) return !1;
		for (let [n, r] of e) if (!Object.is(r, t.get(n))) return !1;
		return !0;
	}
	if (e instanceof Set && t instanceof Set) {
		if (e.size !== t.size) return !1;
		for (let n of e) if (!t.has(n)) return !1;
		return !0;
	}
	let n = Object.keys(e);
	if (n.length !== Object.keys(t).length) return !1;
	for (let r of n) if (!Object.prototype.hasOwnProperty.call(t, r) || !Object.is(e[r], t[r])) return !1;
	return !0;
}
//#endregion
//#region ../../../resource_engines/node_modules/@xyflow/react/dist/esm/index.js
var Dn = /* @__PURE__ */ e(n()), On = (0, m.createContext)(null), kn = On.Provider, An = _.error001("react");
function Q(e, t) {
	let n = (0, m.useContext)(On);
	if (n === null) throw Error(An);
	return wn(n, e, t);
}
function $() {
	let e = (0, m.useContext)(On);
	if (e === null) throw Error(An);
	return (0, m.useMemo)(() => ({
		getState: e.getState,
		setState: e.setState,
		subscribe: e.subscribe
	}), [e]);
}
var jn = { display: "none" }, Mn = {
	position: "absolute",
	width: 1,
	height: 1,
	margin: -1,
	border: 0,
	padding: 0,
	overflow: "hidden",
	clip: "rect(0px, 0px, 0px, 0px)",
	clipPath: "inset(100%)"
}, Nn = "react-flow__node-desc", Pn = "react-flow__edge-desc", Fn = "react-flow__aria-live", In = (e) => e.ariaLiveMessage, Ln = (e) => e.ariaLabelConfig;
function Rn({ rfId: e }) {
	let t = Q(In);
	return (0, h.jsx)("div", {
		id: `${Fn}-${e}`,
		"aria-live": "assertive",
		"aria-atomic": "true",
		style: Mn,
		children: t
	});
}
function zn({ rfId: e, disableKeyboardA11y: t }) {
	let n = Q(Ln);
	return (0, h.jsxs)(h.Fragment, { children: [
		(0, h.jsx)("div", {
			id: `${Nn}-${e}`,
			style: jn,
			children: t ? n["node.a11yDescription.default"] : n["node.a11yDescription.keyboardDisabled"]
		}),
		(0, h.jsx)("div", {
			id: `${Pn}-${e}`,
			style: jn,
			children: n["edge.a11yDescription.default"]
		}),
		!t && (0, h.jsx)(Rn, { rfId: e })
	] });
}
var Bn = (0, m.forwardRef)(({ position: e = "top-left", children: t, className: n, style: r, ...i }, a) => {
	let o = `${e}`.split("-");
	return (0, h.jsx)("div", {
		className: g([
			"react-flow__panel",
			n,
			...o
		]),
		style: r,
		ref: a,
		...i,
		children: t
	});
});
Bn.displayName = "Panel";
var Vn = "https://reactflow.dev?utm_source=attribution";
function Hn({ proOptions: e, position: t = "bottom-right" }) {
	return (0, m.useEffect)(() => {}, []), e?.hideAttribution ? null : (0, h.jsx)(Bn, {
		position: t,
		className: "react-flow__attribution",
		"data-message": `Please only hide this attribution when you are subscribed to React Flow Pro: ${Vn}`,
		children: (0, h.jsx)("a", {
			href: Vn,
			target: "_blank",
			rel: "noopener noreferrer",
			"aria-label": "React Flow attribution",
			children: "React Flow"
		})
	});
}
var Un = (e) => {
	let t = [], n = [];
	for (let [, n] of e.nodeLookup) n.selected && t.push(n.internals.userNode);
	for (let [, t] of e.edgeLookup) t.selected && n.push(t);
	return {
		selectedNodes: t,
		selectedEdges: n
	};
}, Wn = (e) => e.id;
function Gn(e, t) {
	return Z(e.selectedNodes.map(Wn), t.selectedNodes.map(Wn)) && Z(e.selectedEdges.map(Wn), t.selectedEdges.map(Wn));
}
function Kn({ onSelectionChange: e }) {
	let t = $(), { selectedNodes: n, selectedEdges: r } = Q(Un, Gn);
	return (0, m.useEffect)(() => {
		let i = {
			nodes: n,
			edges: r
		};
		e?.(i), t.getState().onSelectionChangeHandlers.forEach((e) => e(i));
	}, [
		n,
		r,
		e
	]), null;
}
var qn = (e) => !!e.onSelectionChangeHandlers;
function Jn({ onSelectionChange: e }) {
	let t = Q(qn);
	return e || t ? (0, h.jsx)(Kn, { onSelectionChange: e }) : null;
}
var Yn = [0, 0], Xn = {
	x: 0,
	y: 0,
	zoom: 1
}, Zn = [.../* @__PURE__ */ "nodes.edges.defaultNodes.defaultEdges.onConnect.onConnectStart.onConnectEnd.onClickConnectStart.onClickConnectEnd.nodesDraggable.autoPanOnNodeFocus.nodesConnectable.nodesFocusable.edgesFocusable.edgesReconnectable.elevateNodesOnSelect.elevateEdgesOnSelect.minZoom.maxZoom.nodeExtent.onNodesChange.onEdgesChange.elementsSelectable.connectionMode.snapGrid.snapToGrid.translateExtent.connectOnClick.defaultEdgeOptions.fitView.fitViewOptions.onNodesDelete.onEdgesDelete.onDelete.onNodeDrag.onNodeDragStart.onNodeDragStop.onSelectionDrag.onSelectionDragStart.onSelectionDragStop.onMoveStart.onMove.onMoveEnd.noPanClassName.nodeOrigin.autoPanOnConnect.autoPanOnNodeDrag.onError.connectionRadius.isValidConnection.selectNodesOnDrag.nodeDragThreshold.connectionDragThreshold.onBeforeDelete.debug.autoPanSpeed.ariaLabelConfig.zIndexMode".split("."), "rfId"], Qn = (e) => ({
	setNodes: e.setNodes,
	setEdges: e.setEdges,
	setMinZoom: e.setMinZoom,
	setMaxZoom: e.setMaxZoom,
	setTranslateExtent: e.setTranslateExtent,
	setNodeExtent: e.setNodeExtent,
	reset: e.reset,
	setDefaultNodesAndEdges: e.setDefaultNodesAndEdges
}), $n = {
	translateExtent: v,
	nodeOrigin: Yn,
	minZoom: .5,
	maxZoom: 2,
	elementsSelectable: !0,
	noPanClassName: "nopan",
	rfId: "1"
};
function er(e) {
	let { setNodes: t, setEdges: n, setMinZoom: r, setMaxZoom: i, setTranslateExtent: a, setNodeExtent: o, reset: s, setDefaultNodesAndEdges: c } = Q(Qn, Z), l = $();
	(0, m.useEffect)(() => (c(e.defaultNodes, e.defaultEdges), () => {
		u.current = $n, s();
	}), []);
	let u = (0, m.useRef)($n);
	return (0, m.useEffect)(() => {
		for (let s of Zn) {
			let c = e[s];
			c !== u.current[s] && e[s] !== void 0 && (s === "nodes" ? t(c) : s === "edges" ? n(c) : s === "minZoom" ? r(c) : s === "maxZoom" ? i(c) : s === "translateExtent" ? a(c) : s === "nodeExtent" ? o(c) : s === "ariaLabelConfig" ? l.setState({ ariaLabelConfig: Ce(c) }) : s === "fitView" ? l.setState({ fitViewQueued: c }) : s === "fitViewOptions" ? l.setState({ fitViewOptions: c }) : l.setState({ [s]: c }));
		}
		u.current = e;
	}, Zn.map((t) => e[t])), null;
}
function tr() {
	return typeof window > "u" || !window.matchMedia ? null : window.matchMedia("(prefers-color-scheme: dark)");
}
function nr(e) {
	let [t, n] = (0, m.useState)(e === "system" ? null : e);
	return (0, m.useEffect)(() => {
		if (e !== "system") {
			n(e);
			return;
		}
		let t = tr(), r = () => n(t?.matches ? "dark" : "light");
		return r(), t?.addEventListener("change", r), () => {
			t?.removeEventListener("change", r);
		};
	}, [e]), t === null ? tr()?.matches ? "dark" : "light" : t;
}
var rr = typeof document < "u" ? document : null;
function ir(e = null, t = {
	target: rr,
	actInsideInputWithModifier: !0
}) {
	let [n, r] = (0, m.useState)(!1), i = (0, m.useRef)(!1), a = (0, m.useRef)(/* @__PURE__ */ new Set([])), [o, s] = (0, m.useMemo)(() => {
		if (e !== null) {
			let t = (Array.isArray(e) ? e : [e]).filter((e) => typeof e == "string").map((e) => e.replace(/\+/g, "\n").replace("\n\n", "\n+").split("\n"));
			return [t, t.reduce((e, t) => e.concat(...t), [])];
		}
		return [[], []];
	}, [e]);
	return (0, m.useEffect)(() => {
		let n = t?.target ?? rr, c = t?.actInsideInputWithModifier ?? !0;
		if (e !== null) {
			let e = (e) => {
				if (i.current = e.ctrlKey || e.metaKey || e.shiftKey || e.altKey, (!i.current || i.current && !c) && je(e)) return !1;
				let n = or(e.code, s);
				if (a.current.add(e[n]), ar(o, a.current, !1)) {
					let n = e.composedPath?.()?.[0] || e.target, a = n?.nodeName === "BUTTON" || n?.nodeName === "A";
					t.preventDefault !== !1 && (i.current || !a) && e.preventDefault(), r(!0);
				}
			}, l = (e) => {
				let t = or(e.code, s);
				ar(o, a.current, !0) ? (r(!1), a.current.clear()) : a.current.delete(e[t]), e.key === "Meta" && a.current.clear(), i.current = !1;
			}, u = () => {
				a.current.clear(), r(!1);
			};
			return n?.addEventListener("keydown", e), n?.addEventListener("keyup", l), window.addEventListener("blur", u), window.addEventListener("contextmenu", u), () => {
				n?.removeEventListener("keydown", e), n?.removeEventListener("keyup", l), window.removeEventListener("blur", u), window.removeEventListener("contextmenu", u);
			};
		}
	}, [e, r]), n;
}
function ar(e, t, n) {
	return e.filter((e) => n || e.length === t.size).some((e) => e.every((e) => t.has(e)));
}
function or(e, t) {
	return t.includes(e) ? "code" : "key";
}
var sr = () => {
	let e = $();
	return (0, m.useMemo)(() => ({
		zoomIn: async (t) => {
			let { panZoom: n } = e.getState();
			return n ? n.scaleBy(1.2, t) : !1;
		},
		zoomOut: async (t) => {
			let { panZoom: n } = e.getState();
			return n ? n.scaleBy(1 / 1.2, t) : !1;
		},
		zoomTo: async (t, n) => {
			let { panZoom: r } = e.getState();
			return r ? r.scaleTo(t, n) : !1;
		},
		getZoom: () => e.getState().transform[2],
		setViewport: async (t, n) => {
			let { transform: [r, i, a], panZoom: o } = e.getState();
			return o ? (await o.setViewport({
				x: t.x ?? r,
				y: t.y ?? i,
				zoom: t.zoom ?? a
			}, n), !0) : !1;
		},
		getViewport: () => {
			let [t, n, r] = e.getState().transform;
			return {
				x: t,
				y: n,
				zoom: r
			};
		},
		setCenter: async (t, n, r) => e.getState().setCenter(t, n, r),
		fitBounds: async (t, n) => {
			let { width: r, height: i, minZoom: a, maxZoom: o, panZoom: s } = e.getState(), c = ge(t, r, i, a, o, n?.padding ?? .1);
			return s ? (await s.setViewport(c, {
				duration: n?.duration,
				ease: n?.ease,
				interpolate: n?.interpolate
			}), !0) : !1;
		},
		screenToFlowPosition: (t, n = {}) => {
			let { transform: r, snapGrid: i, snapToGrid: a, domNode: o } = e.getState();
			if (!o) return t;
			let { x: s, y: c } = o.getBoundingClientRect(), l = {
				x: t.x - s,
				y: t.y - c
			}, u = n.snapGrid ?? i;
			return de(l, r, n.snapToGrid ?? a, u);
		},
		flowToScreenPosition: (t) => {
			let { transform: n, domNode: r } = e.getState();
			if (!r) return t;
			let { x: i, y: a } = r.getBoundingClientRect(), o = fe(t, n);
			return {
				x: o.x + i,
				y: o.y + a
			};
		}
	}), []);
};
function cr(e, t) {
	let n = [], r = /* @__PURE__ */ new Map(), i = [];
	for (let t of e) if (t.type === "add") {
		i.push(t);
		continue;
	} else if (t.type === "remove" || t.type === "replace") r.set(t.id, [t]);
	else {
		let e = r.get(t.id);
		e ? e.push(t) : r.set(t.id, [t]);
	}
	for (let e of t) {
		let t = r.get(e.id);
		if (!t) {
			n.push(e);
			continue;
		}
		if (t[0].type === "remove") continue;
		if (t[0].type === "replace") {
			n.push({ ...t[0].item });
			continue;
		}
		let i = { ...e };
		for (let e of t) lr(e, i);
		n.push(i);
	}
	return i.length && i.forEach((e) => {
		e.index === void 0 ? n.push({ ...e.item }) : n.splice(e.index, 0, { ...e.item });
	}), n;
}
function lr(e, t) {
	switch (e.type) {
		case "select":
			t.selected = e.selected;
			break;
		case "position":
			e.position !== void 0 && (t.position = e.position), e.dragging !== void 0 && (t.dragging = e.dragging);
			break;
		case "dimensions": e.dimensions !== void 0 && (t.measured = { ...e.dimensions }, e.setAttributes && ((e.setAttributes === !0 || e.setAttributes === "width") && (t.width = e.dimensions.width), (e.setAttributes === !0 || e.setAttributes === "height") && (t.height = e.dimensions.height))), typeof e.resizing == "boolean" && (t.resizing = e.resizing);
	}
}
function ur(e, t) {
	return cr(e, t);
}
function dr(e, t) {
	return cr(e, t);
}
function fr(e, t) {
	return {
		id: e,
		type: "select",
		selected: t
	};
}
function pr(e, t = /* @__PURE__ */ new Set(), n = !1) {
	let r = [];
	for (let [i, a] of e) {
		let e = t.has(i);
		(a.selected !== void 0 || e) && a.selected !== e && (n && (a.selected = e), r.push(fr(a.id, e)));
	}
	return r;
}
function mr({ items: e = [], lookup: t }) {
	let n = [], r = new Map(e.map((e) => [e.id, e]));
	for (let [r, i] of e.entries()) {
		let e = t.get(i.id), a = e?.internals?.userNode ?? e;
		a !== void 0 && a !== i && n.push({
			id: i.id,
			item: i,
			type: "replace"
		}), a === void 0 && n.push({
			item: i,
			type: "add",
			index: r
		});
	}
	for (let [e] of t) r.get(e) === void 0 && n.push({
		id: e,
		type: "remove"
	});
	return n;
}
function hr(e) {
	return {
		id: e.id,
		type: "remove"
	};
}
var gr = le("React Flow", "https://reactflow.dev/");
function _r(e, t, n = {}) {
	return Ue(e, t, {
		...n,
		onError: n.onError ?? gr
	});
}
function vr(e, t, n, r = { shouldReplaceId: !0 }) {
	return We(e, t, n, {
		...r,
		onError: r.onError ?? gr
	});
}
var yr = (e) => A(e), br = (e) => k(e);
function xr(e) {
	return (0, m.forwardRef)(e);
}
var Sr = typeof window < "u" ? m.useLayoutEffect : m.useEffect;
function Cr(e) {
	let [t, n] = (0, m.useState)(BigInt(0)), [r] = (0, m.useState)(() => wr(() => n((e) => e + BigInt(1))));
	return Sr(() => {
		let t = r.get();
		t.length && (e(t), r.reset());
	}, [t]), r;
}
function wr(e) {
	let t = [];
	return {
		get: () => t,
		reset: () => {
			t = [];
		},
		push: (n) => {
			t.push(n), e();
		}
	};
}
var Tr = (0, m.createContext)(null);
function Er({ children: e }) {
	let t = $(), n = Cr((0, m.useCallback)((e) => {
		let { nodes: n = [], setNodes: r, hasDefaultNodes: i, onNodesChange: a, nodeLookup: o, fitViewQueued: s, onNodesChangeMiddlewareMap: c } = t.getState(), l = n;
		for (let t of e) l = typeof t == "function" ? t(l) : t;
		let u = mr({
			items: l,
			lookup: o
		});
		for (let e of c.values()) u = e(u);
		i && r(l), u.length > 0 ? a?.(u) : s && window.requestAnimationFrame(() => {
			let { fitViewQueued: e, nodes: n, setNodes: r } = t.getState();
			e && r(n);
		});
	}, [])), r = Cr((0, m.useCallback)((e) => {
		let { edges: n = [], setEdges: r, hasDefaultEdges: i, onEdgesChange: a, edgeLookup: o } = t.getState(), s = n;
		for (let t of e) s = typeof t == "function" ? t(s) : t;
		i ? r(s) : a && a(mr({
			items: s,
			lookup: o
		}));
	}, [])), i = (0, m.useMemo)(() => ({
		nodeQueue: n,
		edgeQueue: r
	}), []);
	return (0, h.jsx)(Tr.Provider, {
		value: i,
		children: e
	});
}
function Dr() {
	let e = (0, m.useContext)(Tr);
	if (!e) throw Error("useBatchContext must be used within a BatchProvider");
	return e;
}
var Or = (e) => !!e.panZoom;
function kr() {
	let e = sr(), t = $(), n = Dr(), r = Q(Or), i = (0, m.useMemo)(() => {
		let e = (e) => t.getState().nodeLookup.get(e), r = (e) => {
			n.nodeQueue.push(e);
		}, i = (e) => {
			n.edgeQueue.push(e);
		}, a = (e) => {
			let { nodeLookup: n, nodeOrigin: r } = t.getState(), i = yr(e) ? e : n.get(e.id), a = i.parentId ? be(i.position, i.measured, i.parentId, n, r) : i.position;
			return re({
				...i,
				position: a,
				width: i.measured?.width ?? i.width,
				height: i.measured?.height ?? i.height
			});
		}, o = (e, t, n = { replace: !1 }) => {
			r((r) => r.map((r) => {
				if (r.id === e) {
					let e = typeof t == "function" ? t(r) : t;
					return n.replace && yr(e) ? e : {
						...r,
						...e
					};
				}
				return r;
			}));
		}, s = (e, t, n = { replace: !1 }) => {
			i((r) => r.map((r) => {
				if (r.id === e) {
					let e = typeof t == "function" ? t(r) : t;
					return n.replace && br(e) ? e : {
						...r,
						...e
					};
				}
				return r;
			}));
		};
		return {
			getNodes: () => t.getState().nodes.map((e) => ({ ...e })),
			getNode: (t) => e(t)?.internals.userNode,
			getInternalNode: e,
			getEdges: () => {
				let { edges: e = [] } = t.getState();
				return e.map((e) => ({ ...e }));
			},
			getEdge: (e) => t.getState().edgeLookup.get(e),
			setNodes: r,
			setEdges: i,
			addNodes: (e) => {
				let t = Array.isArray(e) ? e : [e];
				n.nodeQueue.push((e) => [...e, ...t]);
			},
			addEdges: (e) => {
				let t = Array.isArray(e) ? e : [e];
				n.edgeQueue.push((e) => [...e, ...t]);
			},
			toObject: () => {
				let { nodes: e = [], edges: n = [], transform: r } = t.getState(), [i, a, o] = r;
				return {
					nodes: e.map((e) => ({ ...e })),
					edges: n.map((e) => ({ ...e })),
					viewport: {
						x: i,
						y: a,
						zoom: o
					}
				};
			},
			deleteElements: async ({ nodes: e = [], edges: n = [] }) => {
				let { nodes: r, edges: i, onNodesDelete: a, onEdgesDelete: o, triggerNodeChanges: s, triggerEdgeChanges: c, onDelete: l, onBeforeDelete: u } = t.getState(), { nodes: d, edges: f } = await H({
					nodesToRemove: e,
					edgesToRemove: n,
					nodes: r,
					edges: i,
					onBeforeDelete: u
				}), p = f.length > 0, m = d.length > 0;
				if (p) {
					let e = f.map(hr);
					o?.(f), c(e);
				}
				if (m) {
					let e = d.map(hr);
					a?.(d), s(e);
				}
				return (m || p) && l?.({
					nodes: d,
					edges: f
				}), {
					deletedNodes: d,
					deletedEdges: f
				};
			},
			getIntersectingNodes: (e, n = !0, r) => {
				let i = ce(e), o = i ? e : a(e), s = r !== void 0;
				return o ? (r || t.getState().nodes).filter((r) => {
					let a = t.getState().nodeLookup.get(r.id);
					if (a && !i && (r.id === e.id || !a.internals.positionAbsolute)) return !1;
					let c = re(s ? r : a), l = se(c, o);
					return n && l > 0 || l >= c.width * c.height || l >= o.width * o.height;
				}) : [];
			},
			isNodeIntersecting: (e, t, n = !0) => {
				let r = ce(e) ? e : a(e);
				if (!r) return !1;
				let i = se(r, t);
				return n && i > 0 || i >= t.width * t.height || i >= r.width * r.height;
			},
			updateNode: o,
			updateNodeData: (e, t, n = { replace: !1 }) => {
				o(e, (e) => {
					let r = typeof t == "function" ? t(e) : t;
					return n.replace ? {
						...e,
						data: r
					} : {
						...e,
						data: {
							...e.data,
							...r
						}
					};
				}, n);
			},
			updateEdge: s,
			updateEdgeData: (e, t, n = { replace: !1 }) => {
				s(e, (e) => {
					let r = typeof t == "function" ? t(e) : t;
					return n.replace ? {
						...e,
						data: r
					} : {
						...e,
						data: {
							...e.data,
							...r
						}
					};
				}, n);
			},
			getNodesBounds: (e) => {
				let { nodeLookup: n, nodeOrigin: r } = t.getState();
				return F(e, {
					nodeLookup: n,
					nodeOrigin: r
				});
			},
			getHandleConnections: ({ type: e, id: n, nodeId: r }) => Array.from(t.getState().connectionLookup.get(`${r}-${e}${n ? `-${n}` : ""}`)?.values() ?? []),
			getNodeConnections: ({ type: e, handleId: n, nodeId: r }) => Array.from(t.getState().connectionLookup.get(`${r}${e ? n ? `-${e}-${n}` : `-${e}` : ""}`)?.values() ?? []),
			fitView: async (e) => {
				let r = t.getState().fitViewResolver ?? Se();
				return t.setState({
					fitViewQueued: !0,
					fitViewOptions: e,
					fitViewResolver: r
				}), n.nodeQueue.push((e) => [...e]), r.promise;
			}
		};
	}, []);
	return (0, m.useMemo)(() => ({
		...i,
		...e,
		viewportInitialized: r
	}), [r]);
}
var Ar = (e) => e.selected, jr = typeof window < "u" ? window : void 0;
function Mr({ deleteKeyCode: e, multiSelectionKeyCode: t }) {
	let n = $(), { deleteElements: r } = kr(), i = ir(e, { actInsideInputWithModifier: !1 }), a = ir(t, { target: jr });
	(0, m.useEffect)(() => {
		if (i) {
			let { edges: e, nodes: t } = n.getState();
			r({
				nodes: t.filter(Ar),
				edges: e.filter(Ar)
			}), n.setState({ nodesSelectionActive: !1 });
		}
	}, [i]), (0, m.useEffect)(() => {
		n.setState({ multiSelectionActive: a });
	}, [a]);
}
function Nr(e) {
	let t = $();
	(0, m.useEffect)(() => {
		let n = () => {
			if (!e.current || !(e.current.checkVisibility?.() ?? !0)) return !1;
			let n = Oe(e.current);
			(n.height === 0 || n.width === 0) && t.getState().onError?.("004", _.error004()), t.setState({
				width: n.width || 500,
				height: n.height || 500
			});
		};
		if (e.current) {
			n(), window.addEventListener("resize", n);
			let t = new ResizeObserver(() => n());
			return t.observe(e.current), () => {
				window.removeEventListener("resize", n), t && e.current && t.unobserve(e.current);
			};
		}
	}, []);
}
var Pr = {
	position: "absolute",
	width: "100%",
	height: "100%",
	top: 0,
	left: 0
}, Fr = (e) => ({
	userSelectionActive: e.userSelectionActive,
	lib: e.lib,
	connectionInProgress: e.connection.inProgress
});
function Ir({ onPaneContextMenu: e, zoomOnScroll: t = !0, zoomOnPinch: n = !0, panOnScroll: r = !1, panActivationKeyPressed: i, panOnScrollSpeed: a = .5, panOnScrollMode: o = S.Free, zoomOnDoubleClick: s = !0, panOnDrag: c = !0, defaultViewport: l, translateExtent: u, minZoom: d, maxZoom: f, zoomActivationKeyCode: p, preventScrolling: g = !0, children: _, noWheelClassName: v, noPanClassName: y, onViewportChange: b, isControlledViewport: x, paneClickDistance: C, selectionOnDrag: w }) {
	let T = $(), E = (0, m.useRef)(null), { userSelectionActive: D, lib: O, connectionInProgress: k } = Q(Fr, Z), A = ir(p), j = (0, m.useRef)();
	Nr(E);
	let M = (0, m.useCallback)((e) => {
		b?.({
			x: e[0],
			y: e[1],
			zoom: e[2]
		}), x || T.setState({ transform: e });
	}, [b, x]);
	return (0, m.useEffect)(() => {
		if (E.current) {
			j.current = an({
				domNode: E.current,
				minZoom: d,
				maxZoom: f,
				translateExtent: u,
				viewport: l,
				onDraggingChange: (e) => T.setState((t) => t.paneDragging === e ? t : { paneDragging: e }),
				onPanZoomStart: (e, t) => {
					let { onViewportChangeStart: n, onMoveStart: r } = T.getState();
					r?.(e, t), n?.(t);
				},
				onPanZoom: (e, t) => {
					let { onViewportChange: n, onMove: r } = T.getState();
					r?.(e, t), n?.(t);
				},
				onPanZoomEnd: (e, t) => {
					let { onViewportChangeEnd: n, onMoveEnd: r } = T.getState();
					r?.(e, t), n?.(t);
				}
			});
			let { x: e, y: t, zoom: n } = j.current.getViewport();
			return T.setState({
				panZoom: j.current,
				transform: [
					e,
					t,
					n
				],
				domNode: E.current.closest(".react-flow")
			}), () => {
				j.current?.destroy();
			};
		}
	}, []), (0, m.useEffect)(() => {
		j.current?.update({
			onPaneContextMenu: e,
			zoomOnScroll: t,
			zoomOnPinch: n,
			panOnScroll: r,
			panActivationKeyPressed: i,
			panOnScrollSpeed: a,
			panOnScrollMode: o,
			zoomOnDoubleClick: s,
			panOnDrag: c,
			zoomActivationKeyPressed: A,
			preventScrolling: g,
			noPanClassName: y,
			userSelectionActive: D,
			noWheelClassName: v,
			lib: O,
			onTransformChange: M,
			connectionInProgress: k,
			selectionOnDrag: w,
			paneClickDistance: C
		});
	}, [
		e,
		t,
		n,
		r,
		i,
		a,
		o,
		s,
		c,
		A,
		g,
		y,
		D,
		v,
		O,
		M,
		k,
		w,
		C
	]), (0, h.jsx)("div", {
		className: "react-flow__renderer",
		ref: E,
		style: Pr,
		children: _
	});
}
var Lr = (e) => ({
	userSelectionActive: e.userSelectionActive,
	userSelectionRect: e.userSelectionRect
});
function Rr() {
	let { userSelectionActive: e, userSelectionRect: t } = Q(Lr, Z);
	return e && t ? (0, h.jsx)("div", {
		className: "react-flow__selection react-flow__container",
		style: {
			width: t.width,
			height: t.height,
			transform: `translate(${t.x}px, ${t.y}px)`
		}
	}) : null;
}
var zr = (e, t) => (n) => {
	n.target === t.current && e?.(n);
}, Br = (e) => ({
	userSelectionActive: e.userSelectionActive,
	elementsSelectable: e.elementsSelectable,
	dragging: e.paneDragging,
	panBy: e.panBy,
	autoPanSpeed: e.autoPanSpeed
});
function Vr({ isSelecting: e, selectionKeyPressed: t, selectionMode: n = C.Full, panOnDrag: r, autoPanOnSelection: i, paneClickDistance: a, selectionOnDrag: o, onSelectionStart: s, onSelectionEnd: c, onPaneClick: l, onPaneContextMenu: u, onPaneScroll: d, onPaneMouseEnter: f, onPaneMouseMove: p, onPaneMouseLeave: _, children: v }) {
	let y = (0, m.useRef)(0), b = $(), { userSelectionActive: x, elementsSelectable: S, dragging: w, panBy: T, autoPanSpeed: E } = Q(Br, Z), D = S && (e || x), O = (0, m.useRef)(null), k = (0, m.useRef)(), A = (0, m.useRef)(/* @__PURE__ */ new Set()), j = (0, m.useRef)(/* @__PURE__ */ new Set()), M = (0, m.useRef)(!1), N = (0, m.useRef)(!1), P = (0, m.useRef)({
		x: 0,
		y: 0
	}), F = (0, m.useRef)(!1), I = (e) => {
		N.current || M.current || b.getState().connection.inProgress ? (N.current = !1, M.current = !1) : (l?.(e), b.getState().resetSelectedElements(), b.setState({ nodesSelectionActive: !1 }));
	}, R = (e) => {
		Array.isArray(r) && r?.includes(2) ? e.preventDefault() : u?.(e);
	}, z = d ? (e) => d(e) : void 0, B = (e) => {
		N.current &&= (e.stopPropagation(), !1);
	}, V = (n) => {
		if (n.pointerType === "touch" && r !== !1 && !t) return;
		let { domNode: i, transform: a } = b.getState();
		if (k.current = i?.getBoundingClientRect(), !k.current) return;
		let s = n.target === O.current;
		if (!s && n.target.closest(".nokey") || !e || !(o && s || t) || n.button !== 0 || !n.isPrimary) return;
		n.target?.setPointerCapture?.(n.pointerId), N.current = !1;
		let { x: c, y: l } = X(n.nativeEvent, k.current), u = de({
			x: c,
			y: l
		}, a);
		b.setState({ userSelectionRect: {
			width: 0,
			height: 0,
			startX: u.x,
			startY: u.y,
			x: c,
			y: l
		} }), s || (n.stopPropagation(), n.preventDefault());
	};
	function H(e, t) {
		let { userSelectionRect: r } = b.getState();
		if (!r) return;
		let { transform: i, nodeLookup: a, edgeLookup: o, connectionLookup: s, triggerNodeChanges: c, triggerEdgeChanges: l, defaultEdgeOptions: u } = b.getState(), d = {
			x: r.startX,
			y: r.startY
		}, { x: f, y: p } = fe(d, i), m = {
			startX: d.x,
			startY: d.y,
			x: e < f ? e : f,
			y: t < p ? t : p,
			width: Math.abs(e - f),
			height: Math.abs(t - p)
		}, h = A.current, g = j.current;
		A.current = new Set(L(a, m, i, n === C.Partial, !0).map((e) => e.id)), j.current = /* @__PURE__ */ new Set();
		let _ = u?.selectable ?? !0;
		for (let e of A.current) {
			let t = s.get(e);
			if (t) for (let { edgeId: e } of t.values()) {
				let t = o.get(e);
				t && (t.selectable ?? _) && j.current.add(e);
			}
		}
		xe(h, A.current) || c(pr(a, A.current, !0)), xe(g, j.current) || l(pr(o, j.current)), b.setState({
			userSelectionRect: m,
			userSelectionActive: !0,
			nodesSelectionActive: !1
		});
	}
	function U() {
		if (!i || !k.current) return;
		let [e, t] = ee(P.current, k.current, E);
		T({
			x: e,
			y: t
		}).then((e) => {
			if (!N.current || !e) {
				y.current = requestAnimationFrame(U);
				return;
			}
			let { x: t, y: n } = P.current;
			H(t, n), y.current = requestAnimationFrame(U);
		});
	}
	let W = () => {
		cancelAnimationFrame(y.current), y.current = 0, F.current = !1;
	};
	(0, m.useEffect)(() => () => W(), []);
	let G = (e) => {
		let { userSelectionRect: n, transform: r, resetSelectedElements: i } = b.getState();
		if (!k.current || !n) return;
		let { x: o, y: c } = X(e.nativeEvent, k.current);
		P.current = {
			x: o,
			y: c
		};
		let l = fe({
			x: n.startX,
			y: n.startY
		}, r);
		if (!N.current) {
			let n = t ? 0 : a;
			if (Math.hypot(o - l.x, c - l.y) <= n) return;
			i(), s?.(e);
		}
		N.current = !0, F.current ||= (U(), !0), H(o, c);
	}, K = (e) => {
		D ? e.button === 0 && (e.target?.releasePointerCapture?.(e.pointerId), !x && e.target === O.current && b.getState().userSelectionRect && I?.(e), b.setState({
			userSelectionActive: !1,
			userSelectionRect: null
		}), N.current && (c?.(e), b.setState({ nodesSelectionActive: A.current.size > 0 })), W()) : e.target === O.current && b.getState().connection.inProgress && (M.current = !0);
	}, q = (e) => {
		e.target?.releasePointerCapture?.(e.pointerId), W();
	}, te = r === !0 || Array.isArray(r) && r.includes(0);
	return (0, h.jsxs)("div", {
		className: g(["react-flow__pane", {
			draggable: te,
			dragging: w,
			selection: e
		}]),
		onClick: D ? void 0 : zr(I, O),
		onContextMenu: zr(R, O),
		onWheel: zr(z, O),
		onPointerEnter: D ? void 0 : f,
		onPointerMove: D ? G : p,
		onPointerUp: K,
		onPointerCancel: D ? q : void 0,
		onPointerDownCapture: D ? V : void 0,
		onClickCapture: D ? B : void 0,
		onPointerLeave: _,
		ref: O,
		style: Pr,
		children: [v, (0, h.jsx)(Rr, {})]
	});
}
function Hr({ id: e, store: t, unselect: n = !1, nodeRef: r }) {
	let { addSelectedNodes: i, unselectNodesAndEdges: a, multiSelectionActive: o, nodeLookup: s, onError: c } = t.getState(), l = s.get(e);
	l ? (t.setState({ nodesSelectionActive: !1 }), l.selected ? (n || l.selected && o) && (a({
		nodes: [l],
		edges: []
	}), requestAnimationFrame(() => r?.current?.blur())) : i([e])) : c?.("012", _.error012(e));
}
function Ur({ nodeRef: e, disabled: t = !1, noDragClassName: n, handleSelector: r, nodeId: i, isSelectable: a, nodeClickDistance: o }) {
	let s = $(), [c, l] = (0, m.useState)(!1), u = (0, m.useRef)();
	return (0, m.useEffect)(() => {
		if (!t) return u.current = Nt({
			getStoreItems: () => s.getState(),
			onNodeMouseDown: (t) => {
				Hr({
					id: t,
					store: s,
					nodeRef: e
				});
			},
			onDragStart: () => {
				l(!0);
			},
			onDragStop: () => {
				l(!1);
			}
		}), () => {
			u.current?.destroy(), u.current = void 0;
		};
	}, [
		t,
		s,
		e
	]), (0, m.useEffect)(() => {
		!t && e.current && u.current && u.current.update({
			noDragClassName: n,
			handleSelector: r,
			domNode: e.current,
			isSelectable: a,
			nodeId: i,
			nodeClickDistance: o
		});
	}, [
		n,
		r,
		t,
		a,
		e,
		i,
		o
	]), c;
}
var Wr = (e) => (t) => t.selected && (t.draggable || e && t.draggable === void 0);
function Gr() {
	let e = $();
	return (0, m.useCallback)((t) => {
		let { nodeExtent: n, snapToGrid: r, snapGrid: i, nodesDraggable: a, onError: o, updateNodePositions: s, nodeLookup: c, nodeOrigin: l } = e.getState(), u = /* @__PURE__ */ new Map(), d = Wr(a), f = r ? i[0] : 5, p = r ? i[1] : 5, m = t.direction.x * f * t.factor, h = t.direction.y * p * t.factor;
		for (let [, e] of c) {
			if (!d(e)) continue;
			let t = {
				x: e.internals.positionAbsolute.x + m,
				y: e.internals.positionAbsolute.y + h
			};
			r && (t = ue(t, i));
			let { position: a, positionAbsolute: s } = V({
				nodeId: e.id,
				nextPosition: t,
				nodeLookup: c,
				nodeExtent: n,
				nodeOrigin: l,
				onError: o
			});
			e.position = a, e.internals.positionAbsolute = s, u.set(e.id, e);
		}
		s(u);
	}, []);
}
var Kr = (0, m.createContext)(null), qr = Kr.Provider;
Kr.Consumer;
var Jr = () => (0, m.useContext)(Kr), Yr = (e) => ({
	connectOnClick: e.connectOnClick,
	noPanClassName: e.noPanClassName,
	rfId: e.rfId
}), Xr = (0, m.createContext)(null);
function Zr({ children: e }) {
	let t = Q(Yr, Z);
	return (0, h.jsx)(Xr.Provider, {
		value: t,
		children: e
	});
}
function Qr() {
	let e = (0, m.useContext)(Xr);
	if (!e) throw Error("useHandleConfig must be used within a HandleConfigProvider");
	return e;
}
var $r = {
	connectingFrom: !1,
	connectingTo: !1,
	clickConnecting: !1,
	isPossibleEndHandle: !0,
	connectionInProcess: !1,
	clickConnectionInProcess: !1,
	valid: !1
}, ei = (e, t, n) => (r) => {
	let { connectionClickStartHandle: i, connectionMode: a, connection: o } = r, { fromHandle: s, toHandle: c, isValid: l } = o;
	if (!s && !i) return $r;
	let u = c?.nodeId === e && c?.id === t && c?.type === n;
	return {
		connectingFrom: s?.nodeId === e && s?.id === t && s?.type === n,
		connectingTo: u,
		clickConnecting: i?.nodeId === e && i?.id === t && i?.type === n,
		isPossibleEndHandle: a === x.Strict ? s?.type !== n : e !== s?.nodeId || t !== s?.id,
		connectionInProcess: !!s,
		clickConnectionInProcess: !!i,
		valid: u && l
	};
};
function ti({ type: e = "source", position: t = D.Top, isValidConnection: n, isConnectable: r = !0, isConnectableStart: i = !0, isConnectableEnd: a = !0, id: o, onConnect: s, children: c, className: l, onMouseDown: u, onTouchStart: d, ...f }, p) {
	let m = o || null, v = e === "target", y = $(), b = Jr(), { connectOnClick: x, noPanClassName: S, rfId: C } = Qr(), { connectingFrom: w, connectingTo: T, clickConnecting: E, isPossibleEndHandle: O, connectionInProcess: k, clickConnectionInProcess: A, valid: j } = Q(ei(b, m, e), Z);
	b || y.getState().onError?.("010", _.error010());
	let M = (e) => {
		let { defaultEdgeOptions: t, onConnect: n, hasDefaultEdges: r } = y.getState(), i = {
			...t,
			...e
		};
		if (r) {
			let { edges: e, setEdges: t, onError: n } = y.getState();
			t(_r(i, e, { onError: n }));
		}
		n?.(i), s?.(i);
	}, N = (e) => {
		if (!b) return;
		let t = Me(e.nativeEvent);
		if (i && (t && e.button === 0 || !t)) {
			let t = y.getState();
			Ut.onPointerDown(e.nativeEvent, {
				handleDomNode: e.currentTarget,
				autoPanOnConnect: t.autoPanOnConnect,
				connectionMode: t.connectionMode,
				connectionRadius: t.connectionRadius,
				domNode: t.domNode,
				nodeLookup: t.nodeLookup,
				lib: t.lib,
				isTarget: v,
				handleId: m,
				nodeId: b,
				flowId: t.rfId,
				panBy: t.panBy,
				cancelConnection: t.cancelConnection,
				onConnectStart: t.onConnectStart,
				onConnectEnd: (...e) => y.getState().onConnectEnd?.(...e),
				updateConnection: t.updateConnection,
				onConnect: M,
				isValidConnection: n || ((...e) => y.getState().isValidConnection?.(...e) ?? !0),
				getTransform: () => y.getState().transform,
				getFromHandle: () => y.getState().connection.fromHandle,
				autoPanSpeed: t.autoPanSpeed,
				dragThreshold: t.connectionDragThreshold
			});
		}
		t ? u?.(e) : d?.(e);
	};
	return (0, h.jsx)("div", {
		"data-handleid": m,
		"data-nodeid": b,
		"data-handlepos": t,
		"data-id": `${C}-${b}-${m}-${e}`,
		className: g([
			"react-flow__handle",
			`react-flow__handle-${t}`,
			"nodrag",
			S,
			l,
			{
				source: !v,
				target: v,
				connectable: r,
				connectablestart: i,
				connectableend: a,
				clickconnecting: E,
				connectingfrom: w,
				connectingto: T,
				valid: j,
				connectionindicator: r && (!k || O) && (k || A ? a : i)
			}
		]),
		onMouseDown: N,
		onTouchStart: N,
		onClick: x ? (t) => {
			let { onClickConnectStart: r, onClickConnectEnd: a, connectionClickStartHandle: o, connectionMode: s, isValidConnection: c, lib: l, rfId: u, nodeLookup: d, connection: f } = y.getState();
			if (!b || !o && !i) return;
			if (!o) {
				r?.(t.nativeEvent, {
					nodeId: b,
					handleId: m,
					handleType: e
				}), y.setState({ connectionClickStartHandle: {
					nodeId: b,
					type: e,
					id: m
				} });
				return;
			}
			let p = ke(t.target), h = n || c, { connection: g, isValid: _ } = Ut.isValid(t.nativeEvent, {
				handle: {
					nodeId: b,
					id: m,
					type: e
				},
				connectionMode: s,
				fromNodeId: o.nodeId,
				fromHandleId: o.id || null,
				fromType: o.type,
				isValidConnection: h,
				flowId: u,
				doc: p,
				lib: l,
				nodeLookup: d
			});
			_ && g && M(g);
			let v = structuredClone(f);
			delete v.inProgress, v.toPosition = v.toHandle ? v.toHandle.position : null, a?.(t, v), y.setState({ connectionClickStartHandle: null });
		} : void 0,
		ref: p,
		...f,
		children: c
	});
}
var ni = (0, m.memo)(xr(ti));
function ri({ data: e, isConnectable: t, sourcePosition: n = D.Bottom }) {
	return (0, h.jsxs)(h.Fragment, { children: [e?.label, (0, h.jsx)(ni, {
		type: "source",
		position: n,
		isConnectable: t
	})] });
}
function ii({ data: e, isConnectable: t, targetPosition: n = D.Top, sourcePosition: r = D.Bottom }) {
	return (0, h.jsxs)(h.Fragment, { children: [
		(0, h.jsx)(ni, {
			type: "target",
			position: n,
			isConnectable: t
		}),
		e?.label,
		(0, h.jsx)(ni, {
			type: "source",
			position: r,
			isConnectable: t
		})
	] });
}
function ai() {
	return null;
}
function oi({ data: e, isConnectable: t, targetPosition: n = D.Top }) {
	return (0, h.jsxs)(h.Fragment, { children: [(0, h.jsx)(ni, {
		type: "target",
		position: n,
		isConnectable: t
	}), e?.label] });
}
var si = {
	ArrowUp: {
		x: 0,
		y: -1
	},
	ArrowDown: {
		x: 0,
		y: 1
	},
	ArrowLeft: {
		x: -1,
		y: 0
	},
	ArrowRight: {
		x: 1,
		y: 0
	}
}, ci = {
	input: ri,
	default: ii,
	output: oi,
	group: ai
};
function li(e) {
	return e.internals.handleBounds === void 0 ? {
		width: e.width ?? e.initialWidth ?? e.style?.width,
		height: e.height ?? e.initialHeight ?? e.style?.height
	} : {
		width: e.width ?? e.style?.width,
		height: e.height ?? e.style?.height
	};
}
var ui = (e) => {
	let { width: t, height: n, x: r, y: i } = I(e.nodeLookup, { filter: (e) => !!e.selected });
	return {
		width: J(t) ? t : null,
		height: J(n) ? n : null,
		userSelectionActive: e.userSelectionActive,
		transformString: `translate(${e.transform[0]}px,${e.transform[1]}px) scale(${e.transform[2]}) translate(${r}px,${i}px)`
	};
};
function di({ onSelectionContextMenu: e, noPanClassName: t, disableKeyboardA11y: n }) {
	let r = $(), { width: i, height: a, transformString: o, userSelectionActive: s } = Q(ui, Z), c = Gr(), l = (0, m.useRef)(null);
	(0, m.useEffect)(() => {
		n || l.current?.focus({ preventScroll: !0 });
	}, [n]);
	let u = !s && i !== null && a !== null;
	if (Ur({
		nodeRef: l,
		disabled: !u
	}), !u) return null;
	let d = e ? (t) => {
		e(t, r.getState().nodes.filter((e) => e.selected));
	} : void 0;
	return (0, h.jsx)("div", {
		className: g([
			"react-flow__nodesselection",
			"react-flow__container",
			t
		]),
		style: { transform: o },
		children: (0, h.jsx)("div", {
			ref: l,
			className: "react-flow__nodesselection-rect",
			onContextMenu: d,
			tabIndex: n ? void 0 : -1,
			onKeyDown: n ? void 0 : (e) => {
				Object.prototype.hasOwnProperty.call(si, e.key) && (e.preventDefault(), c({
					direction: si[e.key],
					factor: e.shiftKey ? 4 : 1
				}));
			},
			style: {
				width: i,
				height: a
			}
		})
	});
}
var fi = typeof window < "u" ? window : void 0, pi = (e) => ({
	nodesSelectionActive: e.nodesSelectionActive,
	userSelectionActive: e.userSelectionActive
});
function mi({ children: e, onPaneClick: t, onPaneMouseEnter: n, onPaneMouseMove: r, onPaneMouseLeave: i, onPaneContextMenu: a, onPaneScroll: o, paneClickDistance: s, deleteKeyCode: c, selectionKeyCode: l, selectionOnDrag: u, selectionMode: d, onSelectionStart: f, onSelectionEnd: p, multiSelectionKeyCode: m, panActivationKeyCode: g, zoomActivationKeyCode: _, elementsSelectable: v, zoomOnScroll: y, zoomOnPinch: b, panOnScroll: x, panOnScrollSpeed: S, panOnScrollMode: C, zoomOnDoubleClick: w, panOnDrag: T, autoPanOnSelection: E, defaultViewport: D, translateExtent: O, minZoom: k, maxZoom: A, preventScrolling: j, onSelectionContextMenu: M, noWheelClassName: N, noPanClassName: P, disableKeyboardA11y: F, onViewportChange: I, isControlledViewport: L }) {
	let { nodesSelectionActive: R, userSelectionActive: z } = Q(pi, Z), B = ir(l, { target: fi }), V = ir(g, { target: fi }), H = V || T, U = V || x, W = u && H !== !0, G = B || z || W;
	return Mr({
		deleteKeyCode: c,
		multiSelectionKeyCode: m
	}), (0, h.jsx)(Ir, {
		onPaneContextMenu: a,
		elementsSelectable: v,
		zoomOnScroll: y,
		zoomOnPinch: b,
		panOnScroll: U,
		panActivationKeyPressed: V,
		panOnScrollSpeed: S,
		panOnScrollMode: C,
		zoomOnDoubleClick: w,
		panOnDrag: !B && H,
		defaultViewport: D,
		translateExtent: O,
		minZoom: k,
		maxZoom: A,
		zoomActivationKeyCode: _,
		preventScrolling: j,
		noWheelClassName: N,
		noPanClassName: P,
		onViewportChange: I,
		isControlledViewport: L,
		paneClickDistance: s,
		selectionOnDrag: W,
		children: (0, h.jsxs)(Vr, {
			onSelectionStart: f,
			onSelectionEnd: p,
			onPaneClick: t,
			onPaneMouseEnter: n,
			onPaneMouseMove: r,
			onPaneMouseLeave: i,
			onPaneContextMenu: a,
			onPaneScroll: o,
			panOnDrag: H,
			autoPanOnSelection: E,
			isSelecting: !!G,
			selectionMode: d,
			selectionKeyPressed: B,
			paneClickDistance: s,
			selectionOnDrag: W,
			children: [e, R && (0, h.jsx)(di, {
				onSelectionContextMenu: M,
				noPanClassName: P,
				disableKeyboardA11y: F
			})]
		})
	});
}
mi.displayName = "FlowRenderer";
var hi = (0, m.memo)(mi), gi = (e) => (t) => e ? L(t.nodeLookup, {
	x: 0,
	y: 0,
	width: t.width,
	height: t.height
}, t.transform, !0).map((e) => e.id) : Array.from(t.nodeLookup.keys());
function _i(e) {
	return Q((0, m.useCallback)(gi(e), [e]), Z);
}
var vi = (e) => e.updateNodeInternals;
function yi() {
	let e = Q(vi), [t] = (0, m.useState)(() => typeof ResizeObserver > "u" ? null : new ResizeObserver((t) => {
		let n = /* @__PURE__ */ new Map();
		t.forEach((e) => {
			let t = e.target.getAttribute("data-id");
			n.set(t, {
				id: t,
				nodeElement: e.target,
				force: !0
			});
		}), e(n);
	}));
	return (0, m.useEffect)(() => () => {
		t?.disconnect();
	}, [t]), t;
}
function bi({ node: e, nodeType: t, hasDimensions: n, resizeObserver: r }) {
	let i = $(), a = (0, m.useRef)(null), o = (0, m.useRef)(null), s = (0, m.useRef)(e.sourcePosition), c = (0, m.useRef)(e.targetPosition), l = (0, m.useRef)(t), u = n && !!e.internals.handleBounds;
	return (0, m.useEffect)(() => {
		a.current && !e.hidden && (!u || o.current !== a.current) && (o.current && r?.unobserve(o.current), r?.observe(a.current), o.current = a.current);
	}, [u, e.hidden]), (0, m.useEffect)(() => () => {
		o.current &&= (r?.unobserve(o.current), null);
	}, []), (0, m.useEffect)(() => {
		if (a.current) {
			let n = l.current !== t, r = s.current !== e.sourcePosition, o = c.current !== e.targetPosition;
			(n || r || o) && (l.current = t, s.current = e.sourcePosition, c.current = e.targetPosition, i.getState().updateNodeInternals(/* @__PURE__ */ new Map([[e.id, {
				id: e.id,
				nodeElement: a.current,
				force: !0
			}]])));
		}
	}, [
		e.id,
		t,
		e.sourcePosition,
		e.targetPosition
	]), a;
}
function xi({ id: e, onClick: t, onMouseEnter: n, onMouseMove: r, onMouseLeave: i, onContextMenu: a, onDoubleClick: o, nodesDraggable: s, elementsSelectable: c, nodesConnectable: l, nodesFocusable: u, resizeObserver: d, noDragClassName: f, noPanClassName: p, disableKeyboardA11y: m, rfId: v, nodeTypes: b, nodeClickDistance: x, onError: S }) {
	let { node: C, internals: w, isParent: T } = Q((t) => {
		let n = t.nodeLookup.get(e), r = t.parentLookup.has(e);
		return {
			node: n,
			internals: n.internals,
			isParent: r
		};
	}, Z), E = C.type || "default", D = b?.[E] || ci[E];
	D === void 0 && (S?.("003", _.error003(E)), E = "default", D = b?.default || ci.default);
	let O = !!(C.draggable || s && C.draggable === void 0), k = !!(C.selectable || c && C.selectable === void 0), A = !!(C.connectable || l && C.connectable === void 0), j = !!(C.focusable || u && C.focusable === void 0), M = $(), N = ye(C), P = bi({
		node: C,
		nodeType: E,
		hasDimensions: N,
		resizeObserver: d
	}), F = Ur({
		nodeRef: P,
		disabled: C.hidden || !O,
		noDragClassName: f,
		handleSelector: C.dragHandle,
		nodeId: e,
		isSelectable: k,
		nodeClickDistance: x
	}), I = Gr();
	if (C.hidden) return null;
	let R = Y(C), z = li(C), B = k || O || t || n || r || i, V = n ? (e) => n(e, { ...w.userNode }) : void 0, H = r ? (e) => r(e, { ...w.userNode }) : void 0, U = i ? (e) => i(e, { ...w.userNode }) : void 0, W = a ? (e) => a(e, { ...w.userNode }) : void 0, G = o ? (e) => o(e, { ...w.userNode }) : void 0, K = (n) => {
		let { selectNodesOnDrag: r, nodeDragThreshold: i } = M.getState();
		k && (!r || !O || i > 0) && Hr({
			id: e,
			store: M,
			nodeRef: P
		}), t && t(n, { ...w.userNode });
	}, ee = (t) => {
		if (!(je(t.nativeEvent) || m)) {
			if (y.includes(t.key) && k) {
				let n = t.key === "Escape";
				Hr({
					id: e,
					store: M,
					unselect: n,
					nodeRef: P
				});
			} else if (O && C.selected && Object.prototype.hasOwnProperty.call(si, t.key)) {
				t.preventDefault();
				let { ariaLabelConfig: e } = M.getState();
				M.setState({ ariaLiveMessage: e["node.a11yDescription.ariaLiveMessage"]({
					direction: t.key.replace("Arrow", "").toLowerCase(),
					x: ~~w.positionAbsolute.x,
					y: ~~w.positionAbsolute.y
				}) }), I({
					direction: si[t.key],
					factor: t.shiftKey ? 4 : 1
				});
			}
		}
	}, q = () => {
		if (m || !P.current?.matches(":focus-visible")) return;
		let { transform: t, width: n, height: r, autoPanOnNodeFocus: i, setCenter: a } = M.getState();
		i && (L(/* @__PURE__ */ new Map([[e, C]]), {
			x: 0,
			y: 0,
			width: n,
			height: r
		}, t, !0).length > 0 || a(C.position.x + R.width / 2, C.position.y + R.height / 2, { zoom: t[2] }));
	};
	return (0, h.jsx)("div", {
		className: g([
			"react-flow__node",
			`react-flow__node-${E}`,
			{ [p]: O },
			C.className,
			{
				selected: C.selected,
				selectable: k,
				parent: T,
				draggable: O,
				dragging: F
			}
		]),
		ref: P,
		style: {
			zIndex: w.z,
			transform: `translate(${w.positionAbsolute.x}px,${w.positionAbsolute.y}px)`,
			pointerEvents: B ? "all" : "none",
			visibility: N ? "visible" : "hidden",
			...C.style,
			...z
		},
		"data-id": e,
		"data-testid": `rf__node-${e}`,
		onMouseEnter: V,
		onMouseMove: H,
		onMouseLeave: U,
		onContextMenu: W,
		onClick: K,
		onDoubleClick: G,
		onKeyDown: j ? ee : void 0,
		tabIndex: j ? 0 : void 0,
		onFocus: j ? q : void 0,
		role: C.ariaRole ?? (j ? "group" : void 0),
		"aria-roledescription": "node",
		"aria-describedby": m ? void 0 : `${Nn}-${v}`,
		"aria-label": C.ariaLabel,
		...C.domAttributes,
		children: (0, h.jsx)(qr, {
			value: e,
			children: (0, h.jsx)(D, {
				id: e,
				data: C.data,
				type: E,
				positionAbsoluteX: w.positionAbsolute.x,
				positionAbsoluteY: w.positionAbsolute.y,
				selected: C.selected ?? !1,
				selectable: k,
				draggable: O,
				deletable: C.deletable ?? !0,
				isConnectable: A,
				sourcePosition: C.sourcePosition,
				targetPosition: C.targetPosition,
				dragging: F,
				dragHandle: C.dragHandle,
				zIndex: w.z,
				parentId: C.parentId,
				...R
			})
		})
	});
}
var Si = (0, m.memo)(xi), Ci = (e) => ({
	nodesConnectable: e.nodesConnectable,
	nodesFocusable: e.nodesFocusable,
	elementsSelectable: e.elementsSelectable,
	onError: e.onError
});
function wi(e) {
	let { nodesConnectable: t, nodesFocusable: n, elementsSelectable: r, onError: i } = Q(Ci, Z), a = _i(e.onlyRenderVisibleElements), o = yi();
	return (0, h.jsx)("div", {
		className: "react-flow__nodes",
		style: Pr,
		children: a.map((a) => (0, h.jsx)(Si, {
			id: a,
			nodeTypes: e.nodeTypes,
			nodeExtent: e.nodeExtent,
			onClick: e.onNodeClick,
			onMouseEnter: e.onNodeMouseEnter,
			onMouseMove: e.onNodeMouseMove,
			onMouseLeave: e.onNodeMouseLeave,
			onContextMenu: e.onNodeContextMenu,
			onDoubleClick: e.onNodeDoubleClick,
			noDragClassName: e.noDragClassName,
			noPanClassName: e.noPanClassName,
			rfId: e.rfId,
			disableKeyboardA11y: e.disableKeyboardA11y,
			resizeObserver: o,
			nodesDraggable: e.nodesDraggable ?? !0,
			nodesConnectable: t,
			nodesFocusable: n,
			elementsSelectable: r,
			nodeClickDistance: e.nodeClickDistance,
			onError: i
		}, a))
	});
}
wi.displayName = "NodeRenderer";
var Ti = (0, m.memo)(wi);
function Ei(e) {
	return Q((0, m.useCallback)((t) => {
		if (!e) return t.edges.map((e) => e.id);
		let n = [];
		if (t.width && t.height) for (let e of t.edges) {
			let r = t.nodeLookup.get(e.source), i = t.nodeLookup.get(e.target);
			r && i && Be({
				sourceNode: r,
				targetNode: i,
				width: t.width,
				height: t.height,
				transform: t.transform
			}) && n.push(e.id);
		}
		return n;
	}, [e]), Z);
}
var Di = ({ color: e = "none", strokeWidth: t = 1 }) => {
	let n = {
		strokeWidth: t,
		...e && { stroke: e }
	};
	return (0, h.jsx)("polyline", {
		className: "arrow",
		style: n,
		strokeLinecap: "round",
		fill: "none",
		strokeLinejoin: "round",
		points: "-5,-4 0,0 -5,4"
	});
}, Oi = ({ color: e = "none", strokeWidth: t = 1 }) => {
	let n = {
		strokeWidth: t,
		...e && {
			stroke: e,
			fill: e
		}
	};
	return (0, h.jsx)("polyline", {
		className: "arrowclosed",
		style: n,
		strokeLinecap: "round",
		strokeLinejoin: "round",
		points: "-5,-4 0,0 -5,4 -5,-4"
	});
}, ki = {
	[E.Arrow]: Di,
	[E.ArrowClosed]: Oi
};
function Ai(e) {
	let t = $();
	return (0, m.useMemo)(() => Object.prototype.hasOwnProperty.call(ki, e) ? ki[e] : (t.getState().onError?.("009", _.error009(e)), null), [e]);
}
var ji = ({ id: e, type: t, color: n, width: r = 12.5, height: i = 12.5, markerUnits: a = "strokeWidth", strokeWidth: o, orient: s = "auto-start-reverse" }) => {
	let c = Ai(t);
	return c ? (0, h.jsx)("marker", {
		className: "react-flow__arrowhead",
		id: e,
		markerWidth: `${r}`,
		markerHeight: `${i}`,
		viewBox: "-10 -10 20 20",
		markerUnits: a,
		orient: s,
		refX: "0",
		refY: "0",
		children: (0, h.jsx)(c, {
			color: n,
			strokeWidth: o
		})
	}) : null;
}, Mi = ({ defaultColor: e, rfId: t }) => {
	let n = Q((e) => e.edges), r = Q((e) => e.defaultEdgeOptions), i = (0, m.useMemo)(() => it(n, {
		id: t,
		defaultColor: e,
		defaultMarkerStart: r?.markerStart,
		defaultMarkerEnd: r?.markerEnd
	}), [
		n,
		r,
		t,
		e
	]);
	return i.length ? (0, h.jsx)("svg", {
		className: "react-flow__marker",
		"aria-hidden": "true",
		children: (0, h.jsx)("defs", { children: i.map((e) => (0, h.jsx)(ji, {
			id: e.id,
			type: e.type,
			color: e.color,
			width: e.width,
			height: e.height,
			markerUnits: e.markerUnits,
			strokeWidth: e.strokeWidth,
			orient: e.orient
		}, e.id)) })
	}) : null;
};
Mi.displayName = "MarkerDefinitions";
var Ni = (0, m.memo)(Mi);
function Pi({ x: e, y: t, label: n, labelStyle: r, labelShowBg: i = !0, labelBgStyle: a, labelBgPadding: o = [2, 4], labelBgBorderRadius: s = 2, children: c, className: l, ...u }) {
	let [d, f] = (0, m.useState)({
		x: 1,
		y: 0,
		width: 0,
		height: 0
	}), p = g(["react-flow__edge-textwrapper", l]), _ = (0, m.useRef)(null);
	return (0, m.useEffect)(() => {
		if (_.current) {
			let e = _.current.getBBox();
			f({
				x: e.x,
				y: e.y,
				width: e.width,
				height: e.height
			});
		}
	}, [n]), n ? (0, h.jsxs)("g", {
		transform: `translate(${e - d.width / 2} ${t - d.height / 2})`,
		className: p,
		visibility: d.width ? "visible" : "hidden",
		...u,
		children: [
			i && (0, h.jsx)("rect", {
				width: d.width + 2 * o[0],
				x: -o[0],
				y: -o[1],
				height: d.height + 2 * o[1],
				className: "react-flow__edge-textbg",
				style: a,
				rx: s,
				ry: s
			}),
			(0, h.jsx)("text", {
				className: "react-flow__edge-text",
				y: d.height / 2,
				dy: "0.3em",
				ref: _,
				style: r,
				children: n
			}),
			c
		]
	}) : null;
}
Pi.displayName = "EdgeText";
var Fi = (0, m.memo)(Pi);
function Ii({ path: e, labelX: t, labelY: n, label: r, labelStyle: i, labelShowBg: a, labelBgStyle: o, labelBgPadding: s, labelBgBorderRadius: c, interactionWidth: l = 20, ...u }) {
	return (0, h.jsxs)(h.Fragment, { children: [
		(0, h.jsx)("path", {
			...u,
			d: e,
			fill: "none",
			className: g(["react-flow__edge-path", u.className])
		}),
		l ? (0, h.jsx)("path", {
			d: e,
			fill: "none",
			strokeOpacity: 0,
			strokeWidth: l,
			className: "react-flow__edge-interaction"
		}) : null,
		r && J(t) && J(n) ? (0, h.jsx)(Fi, {
			x: t,
			y: n,
			label: r,
			labelStyle: i,
			labelShowBg: a,
			labelBgStyle: o,
			labelBgPadding: s,
			labelBgBorderRadius: c
		}) : null
	] });
}
function Li({ pos: e, x1: t, y1: n, x2: r, y2: i }) {
	return e === D.Left || e === D.Right ? [.5 * (t + r), n] : [t, .5 * (n + i)];
}
function Ri({ sourceX: e, sourceY: t, sourcePosition: n = D.Bottom, targetX: r, targetY: i, targetPosition: a = D.Top }) {
	let [o, s] = Li({
		pos: n,
		x1: e,
		y1: t,
		x2: r,
		y2: i
	}), [c, l] = Li({
		pos: a,
		x1: r,
		y1: i,
		x2: e,
		y2: t
	}), [u, d, f, p] = Pe({
		sourceX: e,
		sourceY: t,
		targetX: r,
		targetY: i,
		sourceControlX: o,
		sourceControlY: s,
		targetControlX: c,
		targetControlY: l
	});
	return [
		`M${e},${t} C${o},${s} ${c},${l} ${r},${i}`,
		u,
		d,
		f,
		p
	];
}
function zi(e) {
	return (0, m.memo)(({ id: t, sourceX: n, sourceY: r, targetX: i, targetY: a, sourcePosition: o, targetPosition: s, label: c, labelStyle: l, labelShowBg: u, labelBgStyle: d, labelBgPadding: f, labelBgBorderRadius: p, style: m, markerEnd: g, markerStart: _, interactionWidth: v }) => {
		let [y, b, x] = Ri({
			sourceX: n,
			sourceY: r,
			sourcePosition: o,
			targetX: i,
			targetY: a,
			targetPosition: s
		}), S = e.isInternal ? void 0 : t;
		return (0, h.jsx)(Ii, {
			id: S,
			path: y,
			labelX: b,
			labelY: x,
			label: c,
			labelStyle: l,
			labelShowBg: u,
			labelBgStyle: d,
			labelBgPadding: f,
			labelBgBorderRadius: p,
			style: m,
			markerEnd: g,
			markerStart: _,
			interactionWidth: v
		});
	});
}
var Bi = zi({ isInternal: !1 }), Vi = zi({ isInternal: !0 });
Bi.displayName = "SimpleBezierEdge", Vi.displayName = "SimpleBezierEdgeInternal";
function Hi(e) {
	return (0, m.memo)(({ id: t, sourceX: n, sourceY: r, targetX: i, targetY: a, label: o, labelStyle: s, labelShowBg: c, labelBgStyle: l, labelBgPadding: u, labelBgBorderRadius: d, style: f, sourcePosition: p = D.Bottom, targetPosition: m = D.Top, markerEnd: g, markerStart: _, pathOptions: v, interactionWidth: y }) => {
		let [b, x, S] = Ze({
			sourceX: n,
			sourceY: r,
			sourcePosition: p,
			targetX: i,
			targetY: a,
			targetPosition: m,
			borderRadius: v?.borderRadius,
			offset: v?.offset,
			stepPosition: v?.stepPosition
		}), C = e.isInternal ? void 0 : t;
		return (0, h.jsx)(Ii, {
			id: C,
			path: b,
			labelX: x,
			labelY: S,
			label: o,
			labelStyle: s,
			labelShowBg: c,
			labelBgStyle: l,
			labelBgPadding: u,
			labelBgBorderRadius: d,
			style: f,
			markerEnd: g,
			markerStart: _,
			interactionWidth: y
		});
	});
}
var Ui = Hi({ isInternal: !1 }), Wi = Hi({ isInternal: !0 });
Ui.displayName = "SmoothStepEdge", Wi.displayName = "SmoothStepEdgeInternal";
function Gi(e) {
	return (0, m.memo)(({ id: t, ...n }) => {
		let r = e.isInternal ? void 0 : t;
		return (0, h.jsx)(Ui, {
			...n,
			id: r,
			pathOptions: (0, m.useMemo)(() => ({
				borderRadius: 0,
				offset: n.pathOptions?.offset
			}), [n.pathOptions?.offset])
		});
	});
}
var Ki = Gi({ isInternal: !1 }), qi = Gi({ isInternal: !0 });
Ki.displayName = "StepEdge", qi.displayName = "StepEdgeInternal";
function Ji(e) {
	return (0, m.memo)(({ id: t, sourceX: n, sourceY: r, targetX: i, targetY: a, label: o, labelStyle: s, labelShowBg: c, labelBgStyle: l, labelBgPadding: u, labelBgBorderRadius: d, style: f, markerEnd: p, markerStart: m, interactionWidth: g }) => {
		let [_, v, y] = Ge({
			sourceX: n,
			sourceY: r,
			targetX: i,
			targetY: a
		}), b = e.isInternal ? void 0 : t;
		return (0, h.jsx)(Ii, {
			id: b,
			path: _,
			labelX: v,
			labelY: y,
			label: o,
			labelStyle: s,
			labelShowBg: c,
			labelBgStyle: l,
			labelBgPadding: u,
			labelBgBorderRadius: d,
			style: f,
			markerEnd: p,
			markerStart: m,
			interactionWidth: g
		});
	});
}
var Yi = Ji({ isInternal: !1 }), Xi = Ji({ isInternal: !0 });
Yi.displayName = "StraightEdge", Xi.displayName = "StraightEdgeInternal";
function Zi(e) {
	return (0, m.memo)(({ id: t, sourceX: n, sourceY: r, targetX: i, targetY: a, sourcePosition: o = D.Bottom, targetPosition: s = D.Top, label: c, labelStyle: l, labelShowBg: u, labelBgStyle: d, labelBgPadding: f, labelBgBorderRadius: p, style: m, markerEnd: g, markerStart: _, pathOptions: v, interactionWidth: y }) => {
		let [b, x, S] = Le({
			sourceX: n,
			sourceY: r,
			sourcePosition: o,
			targetX: i,
			targetY: a,
			targetPosition: s,
			curvature: v?.curvature
		}), C = e.isInternal ? void 0 : t;
		return (0, h.jsx)(Ii, {
			id: C,
			path: b,
			labelX: x,
			labelY: S,
			label: c,
			labelStyle: l,
			labelShowBg: u,
			labelBgStyle: d,
			labelBgPadding: f,
			labelBgBorderRadius: p,
			style: m,
			markerEnd: g,
			markerStart: _,
			interactionWidth: y
		});
	});
}
var Qi = Zi({ isInternal: !1 }), $i = Zi({ isInternal: !0 });
Qi.displayName = "BezierEdge", $i.displayName = "BezierEdgeInternal";
var ea = {
	default: $i,
	straight: Xi,
	step: qi,
	smoothstep: Wi,
	simplebezier: Vi
}, ta = {
	sourceX: null,
	sourceY: null,
	targetX: null,
	targetY: null,
	sourcePosition: null,
	targetPosition: null,
	zIndex: void 0
}, na = (e, t, n) => n === D.Left ? e - t : n === D.Right ? e + t : e, ra = (e, t, n) => n === D.Top ? e - t : n === D.Bottom ? e + t : e, ia = "react-flow__edgeupdater";
function aa({ position: e, centerX: t, centerY: n, radius: r = 10, onMouseDown: i, onMouseEnter: a, onMouseOut: o, type: s }) {
	return (0, h.jsx)("circle", {
		onMouseDown: i,
		onMouseEnter: a,
		onMouseOut: o,
		className: g([ia, `${ia}-${s}`]),
		cx: na(t, r, e),
		cy: ra(n, r, e),
		r,
		stroke: "transparent",
		fill: "transparent"
	});
}
function oa({ isReconnectable: e, reconnectRadius: t, edge: n, sourceX: r, sourceY: i, targetX: a, targetY: o, sourcePosition: s, targetPosition: c, onReconnect: l, onReconnectStart: u, onReconnectEnd: d, setReconnecting: f, setUpdateHover: p }) {
	let m = $(), g = (e, t) => {
		if (e.button !== 0) return;
		let { autoPanOnConnect: r, domNode: i, connectionMode: a, connectionRadius: o, lib: s, onConnectStart: c, cancelConnection: p, nodeLookup: h, rfId: g, panBy: _, updateConnection: v } = m.getState(), y = t.type === "target";
		Ut.onPointerDown(e.nativeEvent, {
			autoPanOnConnect: r,
			connectionMode: a,
			connectionRadius: o,
			domNode: i,
			handleId: t.id,
			nodeId: t.nodeId,
			nodeLookup: h,
			isTarget: y,
			edgeUpdaterType: t.type,
			lib: s,
			flowId: g,
			cancelConnection: p,
			panBy: _,
			isValidConnection: (...e) => m.getState().isValidConnection?.(...e) ?? !0,
			onConnect: (e) => l?.(n, e),
			onConnectStart: (r, i) => {
				f(!0), u?.(e, n, t.type), c?.(r, i);
			},
			onConnectEnd: (...e) => m.getState().onConnectEnd?.(...e),
			onReconnectEnd: (e, r) => {
				f(!1), d?.(e, n, t.type, r);
			},
			updateConnection: v,
			getTransform: () => m.getState().transform,
			getFromHandle: () => m.getState().connection.fromHandle,
			dragThreshold: m.getState().connectionDragThreshold,
			handleDomNode: e.currentTarget
		});
	}, _ = (e) => g(e, {
		nodeId: n.target,
		id: n.targetHandle ?? null,
		type: "target"
	}), v = (e) => g(e, {
		nodeId: n.source,
		id: n.sourceHandle ?? null,
		type: "source"
	}), y = () => p(!0), b = () => p(!1);
	return (0, h.jsxs)(h.Fragment, { children: [(e === !0 || e === "source") && (0, h.jsx)(aa, {
		position: s,
		centerX: r,
		centerY: i,
		radius: t,
		onMouseDown: _,
		onMouseEnter: y,
		onMouseOut: b,
		type: "source"
	}), (e === !0 || e === "target") && (0, h.jsx)(aa, {
		position: c,
		centerX: a,
		centerY: o,
		radius: t,
		onMouseDown: v,
		onMouseEnter: y,
		onMouseOut: b,
		type: "target"
	})] });
}
function sa({ id: e, edgesFocusable: t, edgesReconnectable: n, elementsSelectable: r, onClick: i, onDoubleClick: a, onContextMenu: o, onMouseEnter: s, onMouseMove: c, onMouseLeave: l, reconnectRadius: u, onReconnect: d, onReconnectStart: f, onReconnectEnd: p, rfId: v, edgeTypes: b, noPanClassName: x, onError: S, disableKeyboardA11y: C }) {
	let w = Q((t) => t.edgeLookup.get(e)), T = Q((e) => e.defaultEdgeOptions);
	w = T ? {
		...T,
		...w
	} : w;
	let E = w.type || "default", D = b?.[E] || ea[E];
	D === void 0 && (S?.("011", _.error011(E)), E = "default", D = b?.default || ea.default);
	let O = !!(w.focusable || t && w.focusable === void 0), k = d !== void 0 && (w.reconnectable || n && w.reconnectable === void 0), A = !!(w.selectable || r && w.selectable === void 0), j = (0, m.useRef)(null), [M, N] = (0, m.useState)(!1), [P, F] = (0, m.useState)(!1), I = $(), { zIndex: L = w.zIndex, sourceX: R, sourceY: z, targetX: B, targetY: V, sourcePosition: H, targetPosition: U } = Q((0, m.useCallback)((t) => {
		let n = t.nodeLookup.get(w.source), r = t.nodeLookup.get(w.target);
		if (!n || !r) return ta;
		let i = $e({
			id: e,
			sourceNode: n,
			targetNode: r,
			sourceHandle: w.sourceHandle || null,
			targetHandle: w.targetHandle || null,
			connectionMode: t.connectionMode,
			onError: S
		}), a = ze({
			selected: w.selected,
			zIndex: w.zIndex,
			sourceNode: n,
			targetNode: r,
			elevateOnSelect: t.elevateEdgesOnSelect,
			zIndexMode: t.zIndexMode
		});
		return {
			...i || ta,
			zIndex: a
		};
	}, [
		w.source,
		w.target,
		w.sourceHandle,
		w.targetHandle,
		w.selected,
		w.zIndex,
		S
	]), Z), W = (0, m.useMemo)(() => w.markerStart ? `url('#${rt(w.markerStart, v)}')` : void 0, [w.markerStart, v]), G = (0, m.useMemo)(() => w.markerEnd ? `url('#${rt(w.markerEnd, v)}')` : void 0, [w.markerEnd, v]);
	if (w.hidden || R === null || z === null || B === null || V === null) return null;
	let K = (t) => {
		let { addSelectedEdges: n, unselectNodesAndEdges: r, multiSelectionActive: a } = I.getState();
		A && (I.setState({ nodesSelectionActive: !1 }), w.selected && a ? (r({
			nodes: [],
			edges: [w]
		}), j.current?.blur()) : n([e])), i && i(t, w);
	}, ee = a ? (e) => {
		a(e, { ...w });
	} : void 0, q = o ? (e) => {
		o(e, { ...w });
	} : void 0, te = s ? (e) => {
		s(e, { ...w });
	} : void 0, ne = c ? (e) => {
		c(e, { ...w });
	} : void 0, re = l ? (e) => {
		l(e, { ...w });
	} : void 0;
	return (0, h.jsx)("svg", {
		style: { zIndex: L },
		children: (0, h.jsxs)("g", {
			className: g([
				"react-flow__edge",
				`react-flow__edge-${E}`,
				w.className,
				x,
				{
					selected: w.selected,
					animated: w.animated,
					inactive: !A && !i,
					updating: M,
					selectable: A
				}
			]),
			onClick: K,
			onDoubleClick: ee,
			onContextMenu: q,
			onMouseEnter: te,
			onMouseMove: ne,
			onMouseLeave: re,
			onKeyDown: O ? (t) => {
				if (!C && y.includes(t.key) && A) {
					let { unselectNodesAndEdges: n, addSelectedEdges: r } = I.getState();
					t.key === "Escape" ? (j.current?.blur(), n({ edges: [w] })) : r([e]);
				}
			} : void 0,
			tabIndex: O ? 0 : void 0,
			role: w.ariaRole ?? (O ? "group" : "img"),
			"aria-roledescription": "edge",
			"data-id": e,
			"data-testid": `rf__edge-${e}`,
			"aria-label": w.ariaLabel === null ? void 0 : w.ariaLabel || `Edge from ${w.source} to ${w.target}`,
			"aria-describedby": O ? `${Pn}-${v}` : void 0,
			ref: j,
			...w.domAttributes,
			children: [!P && (0, h.jsx)(D, {
				id: e,
				source: w.source,
				target: w.target,
				type: w.type,
				selected: w.selected,
				animated: w.animated,
				selectable: A,
				deletable: w.deletable ?? !0,
				label: w.label,
				labelStyle: w.labelStyle,
				labelShowBg: w.labelShowBg,
				labelBgStyle: w.labelBgStyle,
				labelBgPadding: w.labelBgPadding,
				labelBgBorderRadius: w.labelBgBorderRadius,
				sourceX: R,
				sourceY: z,
				targetX: B,
				targetY: V,
				sourcePosition: H,
				targetPosition: U,
				data: w.data,
				style: w.style,
				sourceHandleId: w.sourceHandle,
				targetHandleId: w.targetHandle,
				markerStart: W,
				markerEnd: G,
				pathOptions: "pathOptions" in w ? w.pathOptions : void 0,
				interactionWidth: w.interactionWidth
			}), k && (0, h.jsx)(oa, {
				edge: w,
				isReconnectable: k,
				reconnectRadius: u,
				onReconnect: d,
				onReconnectStart: f,
				onReconnectEnd: p,
				sourceX: R,
				sourceY: z,
				targetX: B,
				targetY: V,
				sourcePosition: H,
				targetPosition: U,
				setUpdateHover: N,
				setReconnecting: F
			})]
		})
	});
}
var ca = (0, m.memo)(sa), la = (e) => ({
	edgesFocusable: e.edgesFocusable,
	edgesReconnectable: e.edgesReconnectable,
	elementsSelectable: e.elementsSelectable,
	connectionMode: e.connectionMode,
	onError: e.onError
});
function ua({ defaultMarkerColor: e, onlyRenderVisibleElements: t, rfId: n, edgeTypes: r, noPanClassName: i, onReconnect: a, onEdgeContextMenu: o, onEdgeMouseEnter: s, onEdgeMouseMove: c, onEdgeMouseLeave: l, onEdgeClick: u, reconnectRadius: d, onEdgeDoubleClick: f, onReconnectStart: p, onReconnectEnd: m, disableKeyboardA11y: g }) {
	let { edgesFocusable: _, edgesReconnectable: v, elementsSelectable: y, onError: b } = Q(la, Z), x = Ei(t);
	return (0, h.jsxs)("div", {
		className: "react-flow__edges",
		children: [(0, h.jsx)(Ni, {
			defaultColor: e,
			rfId: n
		}), x.map((e) => (0, h.jsx)(ca, {
			id: e,
			edgesFocusable: _,
			edgesReconnectable: v,
			elementsSelectable: y,
			noPanClassName: i,
			onReconnect: a,
			onContextMenu: o,
			onMouseEnter: s,
			onMouseMove: c,
			onMouseLeave: l,
			onClick: u,
			reconnectRadius: d,
			onDoubleClick: f,
			onReconnectStart: p,
			onReconnectEnd: m,
			rfId: n,
			onError: b,
			edgeTypes: r,
			disableKeyboardA11y: g
		}, e))]
	});
}
ua.displayName = "EdgeRenderer";
var da = (0, m.memo)(ua), fa = (e) => `translate(${e[0]}px,${e[1]}px) scale(${e[2]})`;
function pa({ children: e }) {
	let t = $(), n = (0, m.useRef)(null), [r] = (0, m.useState)(() => t.getState().transform);
	return Sr(() => {
		let e = null, r = () => {
			let r = t.getState().transform;
			e && r[0] === e[0] && r[1] === e[1] && r[2] === e[2] || (e = r, n.current && (n.current.style.transform = fa(r)));
		};
		return r(), t.subscribe(r);
	}, [t]), (0, h.jsx)("div", {
		ref: n,
		className: "react-flow__viewport xyflow__viewport react-flow__container",
		style: { transform: fa(r) },
		children: e
	});
}
function ma(e) {
	let t = kr(), n = (0, m.useRef)(!1);
	(0, m.useEffect)(() => {
		!n.current && t.viewportInitialized && e && (setTimeout(() => e(t), 1), n.current = !0);
	}, [e, t.viewportInitialized]);
}
var ha = (e) => e.panZoom?.syncViewport;
function ga(e) {
	let t = Q(ha), n = $();
	return (0, m.useEffect)(() => {
		e && (t?.(e), n.setState({ transform: [
			e.x,
			e.y,
			e.zoom
		] }));
	}, [e, t]), null;
}
function _a(e) {
	return e.connection.inProgress ? {
		...e.connection,
		to: de(e.connection.to, e.transform)
	} : { ...e.connection };
}
function va(e) {
	return e ? (t) => e(_a(t)) : _a;
}
function ya(e) {
	return Q(va(e), Z);
}
var ba = (e) => ({
	nodesConnectable: e.nodesConnectable,
	isValid: e.connection.isValid,
	inProgress: e.connection.inProgress,
	width: e.width,
	height: e.height
});
function xa({ containerStyle: e, style: t, type: n, component: r }) {
	let { nodesConnectable: i, width: a, height: o, isValid: s, inProgress: c } = Q(ba, Z);
	return a && i && c ? (0, h.jsx)("svg", {
		style: e,
		width: a,
		height: o,
		className: "react-flow__connectionline react-flow__container",
		children: (0, h.jsx)("g", {
			className: g(["react-flow__connection", Ee(s)]),
			children: (0, h.jsx)(Sa, {
				style: t,
				type: n,
				CustomComponent: r,
				isValid: s
			})
		})
	}) : null;
}
var Sa = ({ style: e, type: t = T.Bezier, CustomComponent: n, isValid: r }) => {
	let { inProgress: i, from: a, fromNode: o, fromHandle: s, fromPosition: c, to: l, toNode: u, toHandle: d, toPosition: f, pointer: p } = ya();
	if (!i) return;
	if (n) return (0, h.jsx)(n, {
		connectionLineType: t,
		connectionLineStyle: e,
		fromNode: o,
		fromHandle: s,
		fromX: a.x,
		fromY: a.y,
		toX: l.x,
		toY: l.y,
		fromPosition: c,
		toPosition: f,
		connectionStatus: Ee(r),
		toNode: u,
		toHandle: d,
		pointer: p
	});
	let m = "", g = {
		sourceX: a.x,
		sourceY: a.y,
		sourcePosition: c,
		targetX: l.x,
		targetY: l.y,
		targetPosition: f
	};
	switch (t) {
		case T.Bezier:
			[m] = Le(g);
			break;
		case T.SimpleBezier:
			[m] = Ri(g);
			break;
		case T.Step:
			[m] = Ze({
				...g,
				borderRadius: 0
			});
			break;
		case T.SmoothStep:
			[m] = Ze(g);
			break;
		default: [m] = Ge(g);
	}
	return (0, h.jsx)("path", {
		d: m,
		fill: "none",
		className: "react-flow__connection-path",
		style: e
	});
};
Sa.displayName = "ConnectionLine";
var Ca = {};
function wa(e = Ca) {
	(0, m.useRef)(e), $(), (0, m.useEffect)(() => {}, [e]);
}
function Ta() {
	$(), (0, m.useRef)(!1), (0, m.useEffect)(() => {}, []);
}
function Ea({ nodeTypes: e, edgeTypes: t, onInit: n, onNodeClick: r, onEdgeClick: i, onNodeDoubleClick: a, onEdgeDoubleClick: o, onNodeMouseEnter: s, onNodeMouseMove: c, onNodeMouseLeave: l, onNodeContextMenu: u, onSelectionContextMenu: d, onSelectionStart: f, onSelectionEnd: p, connectionLineType: m, connectionLineStyle: g, connectionLineComponent: _, connectionLineContainerStyle: v, selectionKeyCode: y, selectionOnDrag: b, selectionMode: x, multiSelectionKeyCode: S, panActivationKeyCode: C, zoomActivationKeyCode: w, deleteKeyCode: T, onlyRenderVisibleElements: E, elementsSelectable: D, defaultViewport: O, translateExtent: k, minZoom: A, maxZoom: j, preventScrolling: M, defaultMarkerColor: N, zoomOnScroll: P, zoomOnPinch: F, panOnScroll: I, panOnScrollSpeed: L, panOnScrollMode: R, zoomOnDoubleClick: z, panOnDrag: B, autoPanOnSelection: V, onPaneClick: H, onPaneMouseEnter: U, onPaneMouseMove: W, onPaneMouseLeave: G, onPaneScroll: K, onPaneContextMenu: ee, paneClickDistance: q, nodeClickDistance: te, onEdgeContextMenu: ne, onEdgeMouseEnter: re, onEdgeMouseMove: ie, onEdgeMouseLeave: ae, reconnectRadius: oe, onReconnect: se, onReconnectStart: ce, onReconnectEnd: J, noDragClassName: le, noWheelClassName: ue, noPanClassName: de, disableKeyboardA11y: fe, nodeExtent: pe, rfId: me, viewport: he, onViewportChange: ge, nodesDraggable: _e }) {
	return wa(e), wa(t), Ta(), ma(n), ga(he), (0, h.jsx)(hi, {
		onPaneClick: H,
		onPaneMouseEnter: U,
		onPaneMouseMove: W,
		onPaneMouseLeave: G,
		onPaneContextMenu: ee,
		onPaneScroll: K,
		paneClickDistance: q,
		deleteKeyCode: T,
		selectionKeyCode: y,
		selectionOnDrag: b,
		selectionMode: x,
		onSelectionStart: f,
		onSelectionEnd: p,
		multiSelectionKeyCode: S,
		panActivationKeyCode: C,
		zoomActivationKeyCode: w,
		elementsSelectable: D,
		zoomOnScroll: P,
		zoomOnPinch: F,
		zoomOnDoubleClick: z,
		panOnScroll: I,
		panOnScrollSpeed: L,
		panOnScrollMode: R,
		panOnDrag: B,
		autoPanOnSelection: V,
		defaultViewport: O,
		translateExtent: k,
		minZoom: A,
		maxZoom: j,
		onSelectionContextMenu: d,
		preventScrolling: M,
		noDragClassName: le,
		noWheelClassName: ue,
		noPanClassName: de,
		disableKeyboardA11y: fe,
		onViewportChange: ge,
		isControlledViewport: !!he,
		children: (0, h.jsxs)(pa, { children: [
			(0, h.jsx)(da, {
				edgeTypes: t,
				onEdgeClick: i,
				onEdgeDoubleClick: o,
				onReconnect: se,
				onReconnectStart: ce,
				onReconnectEnd: J,
				onlyRenderVisibleElements: E,
				onEdgeContextMenu: ne,
				onEdgeMouseEnter: re,
				onEdgeMouseMove: ie,
				onEdgeMouseLeave: ae,
				reconnectRadius: oe,
				defaultMarkerColor: N,
				noPanClassName: de,
				disableKeyboardA11y: fe,
				rfId: me
			}),
			(0, h.jsx)(xa, {
				style: g,
				type: m,
				component: _,
				containerStyle: v
			}),
			(0, h.jsx)("div", { className: "react-flow__edgelabel-renderer" }),
			(0, h.jsx)(Ti, {
				nodeTypes: e,
				onNodeClick: r,
				onNodeDoubleClick: a,
				onNodeMouseEnter: s,
				onNodeMouseMove: c,
				onNodeMouseLeave: l,
				onNodeContextMenu: u,
				nodeClickDistance: te,
				onlyRenderVisibleElements: E,
				noPanClassName: de,
				noDragClassName: le,
				disableKeyboardA11y: fe,
				nodeExtent: pe,
				rfId: me,
				nodesDraggable: _e
			}),
			(0, h.jsx)("div", { className: "react-flow__viewport-portal" })
		] })
	});
}
Ea.displayName = "GraphView";
var Da = (0, m.memo)(Ea), Oa = le("React Flow", "https://reactflow.dev/"), ka = ({ nodes: e, edges: t, defaultNodes: n, defaultEdges: r, width: i, height: a, fitView: o, fitViewOptions: s, minZoom: c = .5, maxZoom: l = 2, nodeOrigin: u, nodeExtent: d, zIndexMode: f = "basic" } = {}) => {
	let p = /* @__PURE__ */ new Map(), m = /* @__PURE__ */ new Map(), h = /* @__PURE__ */ new Map(), g = /* @__PURE__ */ new Map(), _ = r ?? t ?? [], y = n ?? e ?? [], S = u ?? [0, 0], C = d ?? v;
	Et(h, g, _);
	let { nodesInitialized: T } = _t(y, p, m, {
		nodeOrigin: S,
		nodeExtent: C,
		zIndexMode: f
	}), E = [
		0,
		0,
		1
	];
	if (o && i && a) {
		let { x: e, y: t, zoom: n } = ge(I(p, { filter: (e) => !(!e.width && !e.initialWidth || !e.height && !e.initialHeight) }), i, a, c, l, s?.padding ?? .1);
		E = [
			e,
			t,
			n
		];
	}
	return {
		rfId: "1",
		width: i ?? 0,
		height: a ?? 0,
		transform: E,
		nodes: y,
		nodesInitialized: T,
		nodeLookup: p,
		parentLookup: m,
		edges: _,
		edgeLookup: g,
		connectionLookup: h,
		onNodesChange: null,
		onEdgesChange: null,
		hasDefaultNodes: n !== void 0,
		hasDefaultEdges: r !== void 0,
		panZoom: null,
		minZoom: c,
		maxZoom: l,
		translateExtent: v,
		nodeExtent: C,
		nodesSelectionActive: !1,
		userSelectionActive: !1,
		userSelectionRect: null,
		connectionMode: x.Strict,
		domNode: null,
		paneDragging: !1,
		noPanClassName: "nopan",
		nodeOrigin: S,
		nodeDragThreshold: 1,
		connectionDragThreshold: 1,
		snapGrid: [15, 15],
		snapToGrid: !1,
		nodesDraggable: !0,
		nodesConnectable: !0,
		nodesFocusable: !0,
		edgesFocusable: !0,
		edgesReconnectable: !0,
		elementsSelectable: !0,
		elevateNodesOnSelect: !0,
		elevateEdgesOnSelect: !0,
		selectNodesOnDrag: !0,
		multiSelectionActive: !1,
		fitViewQueued: o ?? !1,
		fitViewOptions: s,
		fitViewResolver: null,
		connection: { ...w },
		connectionClickStartHandle: null,
		connectOnClick: !0,
		ariaLiveMessage: "",
		autoPanOnConnect: !0,
		autoPanOnNodeDrag: !0,
		autoPanOnNodeFocus: !0,
		autoPanSpeed: 15,
		connectionRadius: 20,
		onError: Oa,
		isValidConnection: void 0,
		onSelectionChangeHandlers: [],
		lib: "react",
		debug: !1,
		ariaLabelConfig: b,
		zIndexMode: f,
		defaultEdgeOptions: void 0,
		onNodesChangeMiddlewareMap: /* @__PURE__ */ new Map(),
		onEdgesChangeMiddlewareMap: /* @__PURE__ */ new Map(),
		onNodesDelete: void 0,
		onEdgesDelete: void 0,
		onDelete: void 0,
		onBeforeDelete: void 0,
		onViewportChangeStart: void 0,
		onViewportChange: void 0,
		onViewportChangeEnd: void 0,
		onNodeDragStart: void 0,
		onNodeDrag: void 0,
		onNodeDragStop: void 0,
		onSelectionDragStart: void 0,
		onSelectionDrag: void 0,
		onSelectionDragStop: void 0,
		onMoveStart: void 0,
		onMove: void 0,
		onMoveEnd: void 0,
		onConnect: void 0,
		onConnectStart: void 0,
		onConnectEnd: void 0,
		onClickConnectStart: void 0,
		onClickConnectEnd: void 0
	};
}, Aa = ({ nodes: e, edges: t, defaultNodes: n, defaultEdges: r, width: i, height: a, fitView: o, fitViewOptions: s, minZoom: c, maxZoom: l, nodeOrigin: u, nodeExtent: d, zIndexMode: f }) => En((p, m) => {
	async function h() {
		let { nodeLookup: e, panZoom: t, fitViewOptions: n, fitViewResolver: r, width: i, height: a, minZoom: o, maxZoom: s } = m();
		t && (await B({
			nodes: e,
			width: i,
			height: a,
			panZoom: t,
			minZoom: o,
			maxZoom: s
		}, n), r?.resolve(!0), p({ fitViewResolver: null }));
	}
	return {
		...ka({
			nodes: e,
			edges: t,
			width: i,
			height: a,
			fitView: o,
			fitViewOptions: s,
			minZoom: c,
			maxZoom: l,
			nodeOrigin: u,
			nodeExtent: d,
			defaultNodes: n,
			defaultEdges: r,
			zIndexMode: f
		}),
		setNodes: (e) => {
			let { nodeLookup: t, parentLookup: n, nodeOrigin: r, nodeExtent: i, elevateNodesOnSelect: a, fitViewQueued: o, zIndexMode: s, nodesSelectionActive: c } = m(), { nodesInitialized: l, hasSelectedNodes: u } = _t(e, t, n, {
				nodeOrigin: r,
				nodeExtent: i,
				elevateNodesOnSelect: a,
				checkEquality: !0,
				zIndexMode: s
			}), d = c && u;
			o && l ? (h(), p({
				nodes: e,
				nodesInitialized: l,
				fitViewQueued: !1,
				fitViewOptions: void 0,
				nodesSelectionActive: d
			})) : p({
				nodes: e,
				nodesInitialized: l,
				nodesSelectionActive: d
			});
		},
		setEdges: (e) => {
			let { connectionLookup: t, edgeLookup: n } = m();
			Et(t, n, e), p({ edges: e });
		},
		setDefaultNodesAndEdges: (e, t) => {
			if (e) {
				let { setNodes: t } = m();
				t(e), p({ hasDefaultNodes: !0 });
			}
			if (t) {
				let { setEdges: e } = m();
				e(t), p({ hasDefaultEdges: !0 });
			}
		},
		updateNodeInternals: (e) => {
			let { triggerNodeChanges: t, nodeLookup: n, parentLookup: r, domNode: i, nodeOrigin: a, nodeExtent: o, debug: s, fitViewQueued: c, zIndexMode: l } = m(), { changes: u, updatedInternals: d } = Ct(e, n, r, i, a, o, l);
			d && (mt(n, r, {
				nodeOrigin: a,
				nodeExtent: o,
				zIndexMode: l
			}), c ? (h(), p({
				fitViewQueued: !1,
				fitViewOptions: void 0
			})) : p({}), u?.length > 0 && t?.(u));
		},
		updateNodePositions: (e, t = !1) => {
			let n = [], r = [], { nodeLookup: i, triggerNodeChanges: a, connection: o, updateConnection: s, onNodesChangeMiddlewareMap: c } = m();
			for (let [a, c] of e) {
				let e = i.get(a), l = !!(e?.expandParent && e?.parentId && c?.position), u = {
					id: a,
					type: "position",
					position: l ? {
						x: Math.max(0, c.position.x),
						y: Math.max(0, c.position.y)
					} : c.position,
					dragging: t
				};
				if (e && o.inProgress && o.fromNode.id === e.id) {
					let t = tt(e, o.fromHandle, D.Left, !0);
					s({
						...o,
						from: t
					});
				}
				l && e.parentId && n.push({
					id: a,
					parentId: e.parentId,
					rect: {
						...c.internals.positionAbsolute,
						width: c.measured.width ?? 0,
						height: c.measured.height ?? 0
					}
				}), r.push(u);
			}
			if (n.length > 0) {
				let { parentLookup: e, nodeOrigin: t } = m(), a = St(n, i, e, t);
				r.push(...a);
			}
			for (let e of c.values()) r = e(r);
			a(r);
		},
		triggerNodeChanges: (e) => {
			let { onNodesChange: t, setNodes: n, nodes: r, hasDefaultNodes: i, debug: a } = m();
			e?.length && (i && n(ur(e, r)), t?.(e));
		},
		triggerEdgeChanges: (e) => {
			let { onEdgesChange: t, setEdges: n, edges: r, hasDefaultEdges: i, debug: a } = m();
			e?.length && (i && n(dr(e, r)), t?.(e));
		},
		addSelectedNodes: (e) => {
			let { multiSelectionActive: t, edgeLookup: n, nodeLookup: r, triggerNodeChanges: i, triggerEdgeChanges: a } = m();
			t ? i(e.map((e) => fr(e, !0))) : (i(pr(r, /* @__PURE__ */ new Set([...e]), !0)), a(pr(n)));
		},
		addSelectedEdges: (e) => {
			let { multiSelectionActive: t, edgeLookup: n, nodeLookup: r, triggerNodeChanges: i, triggerEdgeChanges: a } = m();
			t ? a(e.map((e) => fr(e, !0))) : (a(pr(n, /* @__PURE__ */ new Set([...e]))), i(pr(r, /* @__PURE__ */ new Set(), !0)));
		},
		unselectNodesAndEdges: ({ nodes: e, edges: t } = {}) => {
			let { edges: n, nodes: r, nodeLookup: i, triggerNodeChanges: a, triggerEdgeChanges: o } = m(), s = e || r, c = t || n, l = [];
			for (let e of s) {
				if (!e.selected) continue;
				let t = i.get(e.id);
				t && (t.selected = !1), l.push(fr(e.id, !1));
			}
			let u = [];
			for (let e of c) e.selected && u.push(fr(e.id, !1));
			a(l), o(u);
		},
		setMinZoom: (e) => {
			let { panZoom: t, maxZoom: n } = m();
			t?.setScaleExtent([e, n]), p({ minZoom: e });
		},
		setMaxZoom: (e) => {
			let { panZoom: t, minZoom: n } = m();
			t?.setScaleExtent([n, e]), p({ maxZoom: e });
		},
		setTranslateExtent: (e) => {
			m().panZoom?.setTranslateExtent(e), p({ translateExtent: e });
		},
		resetSelectedElements: () => {
			let { edges: e, nodes: t, triggerNodeChanges: n, triggerEdgeChanges: r, elementsSelectable: i } = m();
			if (!i) return;
			let a = t.reduce((e, t) => t.selected ? [...e, fr(t.id, !1)] : e, []), o = e.reduce((e, t) => t.selected ? [...e, fr(t.id, !1)] : e, []);
			n(a), r(o);
		},
		setNodeExtent: (e) => {
			let { nodes: t, nodeLookup: n, parentLookup: r, nodeOrigin: i, elevateNodesOnSelect: a, nodeExtent: o, zIndexMode: s } = m();
			(e[0][0] !== o[0][0] || e[0][1] !== o[0][1] || e[1][0] !== o[1][0] || e[1][1] !== o[1][1]) && (_t(t, n, r, {
				nodeOrigin: i,
				nodeExtent: e,
				elevateNodesOnSelect: a,
				checkEquality: !1,
				zIndexMode: s
			}), p({ nodeExtent: e }));
		},
		panBy: (e) => {
			let { transform: t, width: n, height: r, panZoom: i, translateExtent: a } = m();
			return wt({
				delta: e,
				panZoom: i,
				transform: t,
				translateExtent: a,
				width: n,
				height: r
			});
		},
		setCenter: async (e, t, n) => {
			let { width: r, height: i, maxZoom: a, panZoom: o } = m();
			if (!o) return !1;
			let s = n?.zoom === void 0 ? a : n.zoom;
			return await o.setViewport({
				x: r / 2 - e * s,
				y: i / 2 - t * s,
				zoom: s
			}, {
				duration: n?.duration,
				ease: n?.ease,
				interpolate: n?.interpolate
			}), !0;
		},
		cancelConnection: () => {
			p({ connection: { ...w } });
		},
		updateConnection: (e) => {
			p({ connection: e });
		},
		reset: () => p({ ...ka() })
	};
}, Object.is);
function ja({ initialNodes: e, initialEdges: t, defaultNodes: n, defaultEdges: r, initialWidth: i, initialHeight: a, initialMinZoom: o, initialMaxZoom: s, initialFitViewOptions: c, fitView: l, nodeOrigin: u, nodeExtent: d, zIndexMode: f, children: p }) {
	let [g] = (0, m.useState)(() => Aa({
		nodes: e,
		edges: t,
		defaultNodes: n,
		defaultEdges: r,
		width: i,
		height: a,
		fitView: l,
		minZoom: o,
		maxZoom: s,
		fitViewOptions: c,
		nodeOrigin: u,
		nodeExtent: d,
		zIndexMode: f
	}));
	return (0, h.jsx)(kn, {
		value: g,
		children: (0, h.jsx)(Er, { children: (0, h.jsx)(Zr, { children: p }) })
	});
}
function Ma({ children: e, nodes: t, edges: n, defaultNodes: r, defaultEdges: i, width: a, height: o, fitView: s, fitViewOptions: c, minZoom: l, maxZoom: u, nodeOrigin: d, nodeExtent: f, zIndexMode: p }) {
	return (0, m.useContext)(On) ? (0, h.jsx)(h.Fragment, { children: e }) : (0, h.jsx)(ja, {
		initialNodes: t,
		initialEdges: n,
		defaultNodes: r,
		defaultEdges: i,
		initialWidth: a,
		initialHeight: o,
		fitView: s,
		initialFitViewOptions: c,
		initialMinZoom: l,
		initialMaxZoom: u,
		nodeOrigin: d,
		nodeExtent: f,
		zIndexMode: p,
		children: e
	});
}
var Na = {
	width: "100%",
	height: "100%",
	overflow: "hidden",
	position: "relative",
	zIndex: 0
};
function Pa({ nodes: e, edges: t, defaultNodes: n, defaultEdges: r, className: i, nodeTypes: a, edgeTypes: o, onNodeClick: s, onEdgeClick: c, onInit: l, onMove: u, onMoveStart: d, onMoveEnd: f, onConnect: p, onConnectStart: _, onConnectEnd: y, onClickConnectStart: b, onClickConnectEnd: x, onNodeMouseEnter: w, onNodeMouseMove: E, onNodeMouseLeave: D, onNodeContextMenu: O, onNodeDoubleClick: k, onNodeDragStart: A, onNodeDrag: j, onNodeDragStop: M, onNodesDelete: N, onEdgesDelete: P, onDelete: F, onSelectionChange: I, onSelectionDragStart: L, onSelectionDrag: R, onSelectionDragStop: z, onSelectionContextMenu: B, onSelectionStart: V, onSelectionEnd: H, onBeforeDelete: U, connectionMode: W, connectionLineType: G = T.Bezier, connectionLineStyle: K, connectionLineComponent: ee, connectionLineContainerStyle: q, deleteKeyCode: te = "Backspace", selectionKeyCode: ne = "Shift", selectionOnDrag: re = !1, selectionMode: ie = C.Full, panActivationKeyCode: ae = "Space", multiSelectionKeyCode: oe = _e() ? "Meta" : "Control", zoomActivationKeyCode: se = _e() ? "Meta" : "Control", snapToGrid: ce, snapGrid: J, onlyRenderVisibleElements: le = !1, selectNodesOnDrag: ue, nodesDraggable: de, autoPanOnNodeFocus: fe, nodesConnectable: pe, nodesFocusable: me, nodeOrigin: he = Yn, edgesFocusable: ge, edgesReconnectable: ve, elementsSelectable: Y = !0, defaultViewport: ye = Xn, minZoom: be = .5, maxZoom: xe = 2, translateExtent: Se = v, preventScrolling: Ce = !0, nodeExtent: we, defaultMarkerColor: Te = "#b1b1b7", zoomOnScroll: Ee = !0, zoomOnPinch: De = !0, panOnScroll: Oe = !1, panOnScrollSpeed: ke = .5, panOnScrollMode: Ae = S.Free, zoomOnDoubleClick: je = !0, panOnDrag: Me = !0, onPaneClick: X, onPaneMouseEnter: Ne, onPaneMouseMove: Pe, onPaneMouseLeave: Fe, onPaneScroll: Ie, onPaneContextMenu: Le, paneClickDistance: Re = 1, nodeClickDistance: ze = 0, children: Be, onReconnect: Ve, onReconnectStart: He, onReconnectEnd: Ue, onEdgeContextMenu: We, onEdgeDoubleClick: Ge, onEdgeMouseEnter: Ke, onEdgeMouseMove: qe, onEdgeMouseLeave: Je, reconnectRadius: Ye = 10, onNodesChange: Xe, onEdgesChange: Ze, noDragClassName: Qe = "nodrag", noWheelClassName: $e = "nowheel", noPanClassName: et = "nopan", fitView: tt, fitViewOptions: nt, connectOnClick: rt, attributionPosition: it, proOptions: at, defaultEdgeOptions: ot, elevateNodesOnSelect: st = !0, elevateEdgesOnSelect: ct = !1, disableKeyboardA11y: lt = !1, autoPanOnConnect: ut, autoPanOnNodeDrag: dt, autoPanOnSelection: ft = !0, autoPanSpeed: pt, connectionRadius: mt, isValidConnection: ht, onError: gt, style: _t, id: vt, nodeDragThreshold: yt, connectionDragThreshold: bt, viewport: xt, onViewportChange: St, width: Ct, height: wt, colorMode: Tt = "light", debug: Et, onScroll: Dt, ariaLabelConfig: Ot, zIndexMode: kt = "basic", ...At }, jt) {
	let Mt = vt || "1", Nt = nr(Tt), Pt = (0, m.useCallback)((e) => {
		e.currentTarget.scrollTo({
			top: 0,
			left: 0,
			behavior: "instant"
		}), Dt?.(e);
	}, [Dt]);
	return (0, h.jsx)("div", {
		"data-testid": "rf__wrapper",
		...At,
		onScroll: Pt,
		style: {
			..._t,
			...Na
		},
		ref: jt,
		className: g([
			"react-flow",
			i,
			Nt
		]),
		id: vt,
		role: "application",
		children: (0, h.jsxs)(Ma, {
			nodes: e,
			edges: t,
			width: Ct,
			height: wt,
			fitView: tt,
			fitViewOptions: nt,
			minZoom: be,
			maxZoom: xe,
			nodeOrigin: he,
			nodeExtent: we,
			zIndexMode: kt,
			children: [
				(0, h.jsx)(er, {
					nodes: e,
					edges: t,
					defaultNodes: n,
					defaultEdges: r,
					onConnect: p,
					onConnectStart: _,
					onConnectEnd: y,
					onClickConnectStart: b,
					onClickConnectEnd: x,
					nodesDraggable: de,
					autoPanOnNodeFocus: fe,
					nodesConnectable: pe,
					nodesFocusable: me,
					edgesFocusable: ge,
					edgesReconnectable: ve,
					elementsSelectable: Y,
					elevateNodesOnSelect: st,
					elevateEdgesOnSelect: ct,
					minZoom: be,
					maxZoom: xe,
					nodeExtent: we,
					onNodesChange: Xe,
					onEdgesChange: Ze,
					snapToGrid: ce,
					snapGrid: J,
					connectionMode: W,
					translateExtent: Se,
					connectOnClick: rt,
					defaultEdgeOptions: ot,
					fitView: tt,
					fitViewOptions: nt,
					onNodesDelete: N,
					onEdgesDelete: P,
					onDelete: F,
					onNodeDragStart: A,
					onNodeDrag: j,
					onNodeDragStop: M,
					onSelectionDrag: R,
					onSelectionDragStart: L,
					onSelectionDragStop: z,
					onMove: u,
					onMoveStart: d,
					onMoveEnd: f,
					noPanClassName: et,
					nodeOrigin: he,
					rfId: Mt,
					autoPanOnConnect: ut,
					autoPanOnNodeDrag: dt,
					autoPanSpeed: pt,
					onError: gt,
					connectionRadius: mt,
					isValidConnection: ht,
					selectNodesOnDrag: ue,
					nodeDragThreshold: yt,
					connectionDragThreshold: bt,
					onBeforeDelete: U,
					debug: Et,
					ariaLabelConfig: Ot,
					zIndexMode: kt
				}),
				(0, h.jsx)(Da, {
					onInit: l,
					onNodeClick: s,
					onEdgeClick: c,
					onNodeMouseEnter: w,
					onNodeMouseMove: E,
					onNodeMouseLeave: D,
					onNodeContextMenu: O,
					onNodeDoubleClick: k,
					nodeTypes: a,
					edgeTypes: o,
					connectionLineType: G,
					connectionLineStyle: K,
					connectionLineComponent: ee,
					connectionLineContainerStyle: q,
					selectionKeyCode: ne,
					selectionOnDrag: re,
					selectionMode: ie,
					deleteKeyCode: te,
					multiSelectionKeyCode: oe,
					panActivationKeyCode: ae,
					zoomActivationKeyCode: se,
					onlyRenderVisibleElements: le,
					defaultViewport: ye,
					translateExtent: Se,
					minZoom: be,
					maxZoom: xe,
					preventScrolling: Ce,
					zoomOnScroll: Ee,
					zoomOnPinch: De,
					zoomOnDoubleClick: je,
					panOnScroll: Oe,
					panOnScrollSpeed: ke,
					panOnScrollMode: Ae,
					panOnDrag: Me,
					autoPanOnSelection: ft,
					onPaneClick: X,
					onPaneMouseEnter: Ne,
					onPaneMouseMove: Pe,
					onPaneMouseLeave: Fe,
					onPaneScroll: Ie,
					onPaneContextMenu: Le,
					paneClickDistance: Re,
					nodeClickDistance: ze,
					onSelectionContextMenu: B,
					onSelectionStart: V,
					onSelectionEnd: H,
					onReconnect: Ve,
					onReconnectStart: He,
					onReconnectEnd: Ue,
					onEdgeContextMenu: We,
					onEdgeDoubleClick: Ge,
					onEdgeMouseEnter: Ke,
					onEdgeMouseMove: qe,
					onEdgeMouseLeave: Je,
					reconnectRadius: Ye,
					defaultMarkerColor: Te,
					noDragClassName: Qe,
					noWheelClassName: $e,
					noPanClassName: et,
					rfId: Mt,
					disableKeyboardA11y: lt,
					nodeExtent: we,
					viewport: xt,
					onViewportChange: St,
					nodesDraggable: de
				}),
				(0, h.jsx)(Jn, { onSelectionChange: I }),
				Be,
				(0, h.jsx)(Hn, {
					proOptions: at,
					position: it
				}),
				(0, h.jsx)(zn, {
					rfId: Mt,
					disableKeyboardA11y: lt
				})
			]
		})
	});
}
var Fa = xr(Pa), Ia = (e) => e.domNode?.querySelector(".react-flow__edgelabel-renderer");
function La({ children: e }) {
	let t = Q(Ia);
	return t ? (0, Dn.createPortal)(e, t) : null;
}
var Ra = (e) => e.domNode?.querySelector(".react-flow__viewport-portal");
function za({ children: e }) {
	let t = Q(Ra);
	return t ? (0, Dn.createPortal)(e, t) : null;
}
function Ba() {
	let e = $();
	return (0, m.useCallback)((t) => {
		let { domNode: n, updateNodeInternals: r } = e.getState(), i = Array.isArray(t) ? t : [t], a = /* @__PURE__ */ new Map();
		i.forEach((e) => {
			let t = n?.querySelector(`.react-flow__node[data-id="${e}"]`);
			t && a.set(e, {
				id: e,
				nodeElement: t,
				force: !0
			});
		}), requestAnimationFrame(() => r(a, { triggerFitView: !1 }));
	}, []);
}
var Va = (e) => e.nodes;
function Ha() {
	return Q(Va, Z);
}
var Ua = (e) => e.edges;
function Wa() {
	return Q(Ua, Z);
}
var Ga = (e) => ({
	x: e.transform[0],
	y: e.transform[1],
	zoom: e.transform[2]
});
function Ka() {
	return Q(Ga, Z);
}
function qa(e) {
	let [t, n] = (0, m.useState)(e);
	return [
		t,
		n,
		(0, m.useCallback)((e) => n((t) => ur(e, t)), [])
	];
}
function Ja(e) {
	let [t, n] = (0, m.useState)(e);
	return [
		t,
		n,
		(0, m.useCallback)((e) => n((t) => dr(e, t)), [])
	];
}
function Ya({ onStart: e, onChange: t, onEnd: n }) {
	let r = $();
	(0, m.useEffect)(() => {
		r.setState({ onViewportChangeStart: e });
	}, [e]), (0, m.useEffect)(() => {
		r.setState({ onViewportChange: t });
	}, [t]), (0, m.useEffect)(() => {
		r.setState({ onViewportChangeEnd: n });
	}, [n]);
}
function Xa({ onChange: e }) {
	let t = $();
	(0, m.useEffect)(() => {
		let n = [...t.getState().onSelectionChangeHandlers, e];
		return t.setState({ onSelectionChangeHandlers: n }), () => {
			let n = t.getState().onSelectionChangeHandlers.filter((t) => t !== e);
			t.setState({ onSelectionChangeHandlers: n });
		};
	}, [e]);
}
var Za = (e) => (t) => {
	if (!e.includeHiddenNodes) return t.nodesInitialized;
	if (t.nodeLookup.size === 0) return !1;
	for (let [, { internals: e }] of t.nodeLookup) if (e.handleBounds === void 0 || !ye(e.userNode)) return !1;
	return !0;
};
function Qa(e = { includeHiddenNodes: !1 }) {
	return Q(Za(e));
}
function $a({ type: e, id: t, nodeId: n, onConnect: r, onDisconnect: i }) {
	let a = Jr(), o = n ?? a, s = (0, m.useRef)(null), c = Q((n) => n.connectionLookup.get(`${o}-${e}${t ? `-${t}` : ""}`), we);
	return (0, m.useEffect)(() => {
		if (s.current && s.current !== c) {
			let e = c ?? /* @__PURE__ */ new Map();
			Te(s.current, e, i), Te(e, s.current, r);
		}
		s.current = c ?? /* @__PURE__ */ new Map();
	}, [
		c,
		r,
		i
	]), (0, m.useMemo)(() => Array.from(c?.values() ?? []), [c]);
}
var eo = _.error014();
function to({ id: e, handleType: t, handleId: n, onConnect: r, onDisconnect: i } = {}) {
	let a = Jr(), o = e ?? a;
	if (!o) throw Error(eo);
	let s = (0, m.useRef)(null), c = Q((e) => e.connectionLookup.get(`${o}${t ? n ? `-${t}-${n}` : `-${t}` : ""}`), we);
	return (0, m.useEffect)(() => {
		if (s.current && s.current !== c) {
			let e = c ?? /* @__PURE__ */ new Map();
			Te(s.current, e, i), Te(e, s.current, r);
		}
		s.current = c ?? /* @__PURE__ */ new Map();
	}, [
		c,
		r,
		i
	]), (0, m.useMemo)(() => Array.from(c?.values() ?? []), [c]);
}
function no(e) {
	return Q((0, m.useCallback)((t) => {
		let n = [], r = Array.isArray(e), i = r ? e : [e];
		for (let e of i) {
			let r = t.nodeLookup.get(e);
			r && n.push({
				id: r.id,
				type: r.type,
				data: r.data
			});
		}
		return r ? n : n[0] ?? null;
	}, [e]), Dt);
}
function ro(e) {
	return Q((0, m.useCallback)((t) => t.nodeLookup.get(e), [e]), Z);
}
function io(e) {
	let t = $(), [n] = (0, m.useState)(() => Symbol());
	(0, m.useEffect)(() => {
		let { onNodesChangeMiddlewareMap: r } = t.getState();
		r.set(n, e);
	}, [e]), (0, m.useEffect)(() => {
		let { onNodesChangeMiddlewareMap: e } = t.getState();
		return () => {
			e.delete(n);
		};
	}, []);
}
function ao(e) {
	let t = $(), [n] = (0, m.useState)(() => Symbol());
	(0, m.useEffect)(() => {
		let { onEdgesChangeMiddlewareMap: r } = t.getState();
		r.set(n, e);
	}, [e]), (0, m.useEffect)(() => {
		let { onEdgesChangeMiddlewareMap: e } = t.getState();
		return () => {
			e.delete(n);
		};
	}, []);
}
function oo({ dimensions: e, lineWidth: t, variant: n, className: r }) {
	return (0, h.jsx)("path", {
		strokeWidth: t,
		d: `M${e[0] / 2} 0 V${e[1]} M0 ${e[1] / 2} H${e[0]}`,
		className: g([
			"react-flow__background-pattern",
			n,
			r
		])
	});
}
function so({ radius: e, className: t }) {
	return (0, h.jsx)("circle", {
		cx: e,
		cy: e,
		r: e,
		className: g([
			"react-flow__background-pattern",
			"dots",
			t
		])
	});
}
var co;
(function(e) {
	e.Lines = "lines", e.Dots = "dots", e.Cross = "cross";
})(co ||= {});
var lo = {
	[co.Dots]: 1,
	[co.Lines]: 1,
	[co.Cross]: 6
}, uo = (e) => ({
	transform: e.transform,
	patternId: `pattern-${e.rfId}`
});
function fo({ id: e, variant: t = co.Dots, gap: n = 20, size: r, lineWidth: i = 1, offset: a = 0, color: o, bgColor: s, style: c, className: l, patternClassName: u }) {
	let d = (0, m.useRef)(null), { transform: f, patternId: p } = Q(uo, Z), _ = r || lo[t], v = t === co.Dots, y = t === co.Cross, b = Array.isArray(n) ? n : [n, n], x = [b[0] * f[2] || 1, b[1] * f[2] || 1], S = _ * f[2], C = Array.isArray(a) ? a : [a, a], w = y ? [S, S] : x, T = [C[0] * f[2] + w[0] / 2, C[1] * f[2] + w[1] / 2], E = `${p}${e || ""}`;
	return (0, h.jsxs)("svg", {
		className: g(["react-flow__background", l]),
		style: {
			...c,
			...Pr,
			"--xy-background-color-props": s,
			"--xy-background-pattern-color-props": o
		},
		ref: d,
		"data-testid": "rf__background",
		children: [(0, h.jsx)("pattern", {
			id: E,
			x: f[0] % x[0],
			y: f[1] % x[1],
			width: x[0],
			height: x[1],
			patternUnits: "userSpaceOnUse",
			patternTransform: `translate(-${T[0]},-${T[1]})`,
			children: v ? (0, h.jsx)(so, {
				radius: S / 2,
				className: u
			}) : (0, h.jsx)(oo, {
				dimensions: w,
				lineWidth: i,
				variant: t,
				className: u
			})
		}), (0, h.jsx)("rect", {
			x: "0",
			y: "0",
			width: "100%",
			height: "100%",
			fill: `url(#${E})`
		})]
	});
}
fo.displayName = "Background";
var po = (0, m.memo)(fo);
function mo() {
	return (0, h.jsx)("svg", {
		xmlns: "http://www.w3.org/2000/svg",
		viewBox: "0 0 32 32",
		children: (0, h.jsx)("path", { d: "M32 18.133H18.133V32h-4.266V18.133H0v-4.266h13.867V0h4.266v13.867H32z" })
	});
}
function ho() {
	return (0, h.jsx)("svg", {
		xmlns: "http://www.w3.org/2000/svg",
		viewBox: "0 0 32 5",
		children: (0, h.jsx)("path", { d: "M0 0h32v4.2H0z" })
	});
}
function go() {
	return (0, h.jsx)("svg", {
		xmlns: "http://www.w3.org/2000/svg",
		viewBox: "0 0 32 30",
		children: (0, h.jsx)("path", { d: "M3.692 4.63c0-.53.4-.938.939-.938h5.215V0H4.708C2.13 0 0 2.054 0 4.63v5.216h3.692V4.631zM27.354 0h-5.2v3.692h5.17c.53 0 .984.4.984.939v5.215H32V4.631A4.624 4.624 0 0027.354 0zm.954 24.83c0 .532-.4.94-.939.94h-5.215v3.768h5.215c2.577 0 4.631-2.13 4.631-4.707v-5.139h-3.692v5.139zm-23.677.94c-.531 0-.939-.4-.939-.94v-5.138H0v5.139c0 2.577 2.13 4.707 4.708 4.707h5.138V25.77H4.631z" })
	});
}
function _o() {
	return (0, h.jsx)("svg", {
		xmlns: "http://www.w3.org/2000/svg",
		viewBox: "0 0 25 32",
		children: (0, h.jsx)("path", { d: "M21.333 10.667H19.81V7.619C19.81 3.429 16.38 0 12.19 0 8 0 4.571 3.429 4.571 7.619v3.048H3.048A3.056 3.056 0 000 13.714v15.238A3.056 3.056 0 003.048 32h18.285a3.056 3.056 0 003.048-3.048V13.714a3.056 3.056 0 00-3.048-3.047zM12.19 24.533a3.056 3.056 0 01-3.047-3.047 3.056 3.056 0 013.047-3.048 3.056 3.056 0 013.048 3.048 3.056 3.056 0 01-3.048 3.047zm4.724-13.866H7.467V7.619c0-2.59 2.133-4.724 4.723-4.724 2.591 0 4.724 2.133 4.724 4.724v3.048z" })
	});
}
function vo() {
	return (0, h.jsx)("svg", {
		xmlns: "http://www.w3.org/2000/svg",
		viewBox: "0 0 25 32",
		children: (0, h.jsx)("path", { d: "M21.333 10.667H19.81V7.619C19.81 3.429 16.38 0 12.19 0c-4.114 1.828-1.37 2.133.305 2.438 1.676.305 4.42 2.59 4.42 5.181v3.048H3.047A3.056 3.056 0 000 13.714v15.238A3.056 3.056 0 003.048 32h18.285a3.056 3.056 0 003.048-3.048V13.714a3.056 3.056 0 00-3.048-3.047zM12.19 24.533a3.056 3.056 0 01-3.047-3.047 3.056 3.056 0 013.047-3.048 3.056 3.056 0 013.048 3.048 3.056 3.056 0 01-3.048 3.047z" })
	});
}
function yo({ children: e, className: t, ...n }) {
	return (0, h.jsx)("button", {
		type: "button",
		className: g(["react-flow__controls-button", t]),
		...n,
		children: e
	});
}
var bo = (e) => ({
	isInteractive: e.nodesDraggable || e.nodesConnectable || e.elementsSelectable,
	minZoomReached: e.transform[2] <= e.minZoom,
	maxZoomReached: e.transform[2] >= e.maxZoom,
	ariaLabelConfig: e.ariaLabelConfig
});
function xo({ style: e, showZoom: t = !0, showFitView: n = !0, showInteractive: r = !0, fitViewOptions: i, onZoomIn: a, onZoomOut: o, onFitView: s, onInteractiveChange: c, className: l, children: u, position: d = "bottom-left", orientation: f = "vertical", "aria-label": p }) {
	let m = $(), { isInteractive: _, minZoomReached: v, maxZoomReached: y, ariaLabelConfig: b } = Q(bo, Z), { zoomIn: x, zoomOut: S, fitView: C } = kr();
	return (0, h.jsxs)(Bn, {
		className: g([
			"react-flow__controls",
			f === "horizontal" ? "horizontal" : "vertical",
			l
		]),
		position: d,
		style: e,
		"data-testid": "rf__controls",
		"aria-label": p ?? b["controls.ariaLabel"],
		children: [
			t && (0, h.jsxs)(h.Fragment, { children: [(0, h.jsx)(yo, {
				onClick: () => {
					x(), a?.();
				},
				className: "react-flow__controls-zoomin",
				title: b["controls.zoomIn.ariaLabel"],
				"aria-label": b["controls.zoomIn.ariaLabel"],
				disabled: y,
				children: (0, h.jsx)(mo, {})
			}), (0, h.jsx)(yo, {
				onClick: () => {
					S(), o?.();
				},
				className: "react-flow__controls-zoomout",
				title: b["controls.zoomOut.ariaLabel"],
				"aria-label": b["controls.zoomOut.ariaLabel"],
				disabled: v,
				children: (0, h.jsx)(ho, {})
			})] }),
			n && (0, h.jsx)(yo, {
				className: "react-flow__controls-fitview",
				onClick: () => {
					C(i), s?.();
				},
				title: b["controls.fitView.ariaLabel"],
				"aria-label": b["controls.fitView.ariaLabel"],
				children: (0, h.jsx)(go, {})
			}),
			r && (0, h.jsx)(yo, {
				className: "react-flow__controls-interactive",
				onClick: () => {
					m.setState({
						nodesDraggable: !_,
						nodesConnectable: !_,
						elementsSelectable: !_
					}), c?.(!_);
				},
				title: b["controls.interactive.ariaLabel"],
				"aria-label": b["controls.interactive.ariaLabel"],
				children: _ ? (0, h.jsx)(vo, {}) : (0, h.jsx)(_o, {})
			}),
			u
		]
	});
}
xo.displayName = "Controls";
var So = (0, m.memo)(xo);
function Co({ id: e, x: t, y: n, width: r, height: i, style: a, color: o, strokeColor: s, strokeWidth: c, className: l, borderRadius: u, shapeRendering: d, selected: f, onClick: p }) {
	let { background: m, backgroundColor: _ } = a || {}, v = o || m || _;
	return (0, h.jsx)("rect", {
		className: g([
			"react-flow__minimap-node",
			{ selected: f },
			l
		]),
		x: t,
		y: n,
		rx: u,
		ry: u,
		width: r,
		height: i,
		style: {
			fill: v,
			stroke: s,
			strokeWidth: c
		},
		shapeRendering: d,
		onClick: p ? (t) => p(t, e) : void 0
	});
}
var wo = (0, m.memo)(Co), To = (e) => e.nodes.map((e) => e.id), Eo = (e) => e instanceof Function ? e : () => e;
function Do({ nodeStrokeColor: e, nodeColor: t, nodeClassName: n = "", nodeBorderRadius: r = 5, nodeStrokeWidth: i, nodeComponent: a = wo, onClick: o }) {
	let s = Q(To, Z), c = Eo(t), l = Eo(e), u = Eo(n), d = typeof window > "u" || window.chrome ? "crispEdges" : "geometricPrecision";
	return (0, h.jsx)(h.Fragment, { children: s.map((e) => (0, h.jsx)(ko, {
		id: e,
		nodeColorFunc: c,
		nodeStrokeColorFunc: l,
		nodeClassNameFunc: u,
		nodeBorderRadius: r,
		nodeStrokeWidth: i,
		NodeComponent: a,
		onClick: o,
		shapeRendering: d
	}, e)) });
}
function Oo({ id: e, nodeColorFunc: t, nodeStrokeColorFunc: n, nodeClassNameFunc: r, nodeBorderRadius: i, nodeStrokeWidth: a, shapeRendering: o, NodeComponent: s, onClick: c }) {
	let { node: l, x: u, y: d, width: f, height: p } = Q((t) => {
		let n = t.nodeLookup.get(e);
		if (!n) return {
			node: void 0,
			x: 0,
			y: 0,
			width: 0,
			height: 0
		};
		let r = n.internals.userNode, { x: i, y: a } = n.internals.positionAbsolute, { width: o, height: s } = Y(r);
		return {
			node: r,
			x: i,
			y: a,
			width: o,
			height: s
		};
	}, Z);
	return !l || l.hidden || !ye(l) ? null : (0, h.jsx)(s, {
		x: u,
		y: d,
		width: f,
		height: p,
		style: l.style,
		selected: !!l.selected,
		className: r(l),
		color: t(l),
		borderRadius: i,
		strokeColor: n(l),
		strokeWidth: a,
		shapeRendering: o,
		onClick: c,
		id: l.id
	});
}
var ko = (0, m.memo)(Oo), Ao = (0, m.memo)(Do), jo = 200, Mo = 150, No = (e) => !e.hidden, Po = (e) => {
	let t = {
		x: -e.transform[0] / e.transform[2],
		y: -e.transform[1] / e.transform[2],
		width: e.width / e.transform[2],
		height: e.height / e.transform[2]
	}, n = !1;
	for (let t of e.nodeLookup.values()) if (!t.hidden) {
		n = !0;
		break;
	}
	return {
		viewBB: t,
		boundingRect: n ? ae(I(e.nodeLookup, { filter: No }), t) : t,
		rfId: e.rfId,
		panZoom: e.panZoom,
		translateExtent: e.translateExtent,
		flowWidth: e.width,
		flowHeight: e.height,
		ariaLabelConfig: e.ariaLabelConfig
	};
}, Fo = (e, t) => e.x === t.x && e.y === t.y && e.width === t.width && e.height === t.height, Io = (e, t) => Fo(e.viewBB, t.viewBB) && Fo(e.boundingRect, t.boundingRect) && e.rfId === t.rfId && e.panZoom === t.panZoom && e.translateExtent === t.translateExtent && e.flowWidth === t.flowWidth && e.flowHeight === t.flowHeight && e.ariaLabelConfig === t.ariaLabelConfig, Lo = "react-flow__minimap-desc";
function Ro({ style: e, className: t, nodeStrokeColor: n, nodeColor: r, nodeClassName: i = "", nodeBorderRadius: a = 5, nodeStrokeWidth: o, nodeComponent: s, bgColor: c, maskColor: l, maskStrokeColor: u, maskStrokeWidth: d, position: f = "bottom-right", onClick: p, onNodeClick: _, pannable: v = !1, zoomable: y = !1, ariaLabel: b, inversePan: x, zoomStep: S = 1, offsetScale: C = 5 }) {
	let w = $(), T = (0, m.useRef)(null), { boundingRect: E, panZoom: D, viewBB: O, rfId: k, translateExtent: A, flowWidth: j, flowHeight: M, ariaLabelConfig: N } = Q(Po, Io), P = e?.width ?? jo, F = e?.height ?? Mo, I = E.width / P, L = E.height / F, R = Math.max(I, L), z = R * P, B = R * F, V = C * R, H = E.x - (z - E.width) / 2 - V, U = E.y - (B - E.height) / 2 - V, W = z + V * 2, G = B + V * 2, K = `${Lo}-${k}`, ee = (0, m.useRef)(0), q = (0, m.useRef)();
	ee.current = R, (0, m.useEffect)(() => {
		let e = w.getState().panZoom;
		if (T.current && e) return q.current = Wt({
			domNode: T.current,
			panZoom: e,
			getTransform: () => w.getState().transform,
			getViewScale: () => ee.current
		}), () => {
			q.current?.destroy();
		};
	}, [D]), (0, m.useEffect)(() => {
		q.current?.update({
			translateExtent: A,
			width: j,
			height: M,
			inversePan: x,
			pannable: v,
			zoomStep: S,
			zoomable: y
		});
	}, [
		v,
		y,
		x,
		S,
		A,
		j,
		M
	]);
	let te = p ? (e) => {
		let [t, n] = q.current?.pointer(e) || [0, 0];
		p(e, {
			x: t,
			y: n
		});
	} : void 0, ne = (0, m.useCallback)((e, t) => {
		let n = w.getState().nodeLookup.get(t).internals.userNode;
		_?.(e, n);
	}, [_]), re = _ ? ne : void 0, ie = b ?? N["minimap.ariaLabel"];
	return (0, h.jsx)(Bn, {
		position: f,
		style: {
			...e,
			"--xy-minimap-background-color-props": typeof c == "string" ? c : void 0,
			"--xy-minimap-mask-background-color-props": typeof l == "string" ? l : void 0,
			"--xy-minimap-mask-stroke-color-props": typeof u == "string" ? u : void 0,
			"--xy-minimap-mask-stroke-width-props": typeof d == "number" ? d * R : void 0,
			"--xy-minimap-node-background-color-props": typeof r == "string" ? r : void 0,
			"--xy-minimap-node-stroke-color-props": typeof n == "string" ? n : void 0,
			"--xy-minimap-node-stroke-width-props": typeof o == "number" ? o : void 0
		},
		className: g(["react-flow__minimap", t]),
		"data-testid": "rf__minimap",
		children: (0, h.jsxs)("svg", {
			width: P,
			height: F,
			viewBox: `${H} ${U} ${W} ${G}`,
			className: "react-flow__minimap-svg",
			role: "img",
			"aria-labelledby": K,
			ref: T,
			onClick: te,
			children: [
				ie && (0, h.jsx)("title", {
					id: K,
					children: ie
				}),
				(0, h.jsx)(Ao, {
					onClick: re,
					nodeColor: r,
					nodeStrokeColor: n,
					nodeBorderRadius: a,
					nodeClassName: i,
					nodeStrokeWidth: o,
					nodeComponent: s
				}),
				(0, h.jsx)("path", {
					className: "react-flow__minimap-mask",
					d: `M${H - V},${U - V}h${W + V * 2}v${G + V * 2}h${-W - V * 2}z
        M${O.x},${O.y}h${O.width}v${O.height}h${-O.width}z`,
					fillRule: "evenodd",
					pointerEvents: "none"
				})
			]
		})
	});
}
Ro.displayName = "MiniMap";
var zo = (0, m.memo)(Ro), Bo = (e) => (t) => e ? `${Math.max(1 / t.transform[2], 1)}` : void 0, Vo = {
	[on.Line]: "right",
	[on.Handle]: "bottom-right"
};
function Ho({ nodeId: e, position: t, variant: n = on.Handle, className: r, style: i = void 0, children: a, color: o, minWidth: s = 10, minHeight: c = 10, maxWidth: l = Number.MAX_VALUE, maxHeight: u = Number.MAX_VALUE, keepAspectRatio: d = !1, resizeDirection: f, autoScale: p = !0, shouldResize: _, onResizeStart: v, onResize: y, onResizeEnd: b }) {
	let x = Jr(), S = typeof e == "string" ? e : x, C = $(), w = (0, m.useRef)(null), T = n === on.Handle, E = Q((0, m.useCallback)(Bo(T && p), [T, p]), Z), D = (0, m.useRef)(null), O = t ?? Vo[n];
	(0, m.useEffect)(() => {
		if (w.current && S) return D.current ||= yn({
			domNode: w.current,
			nodeId: S,
			getStoreItems: () => {
				let { nodeLookup: e, transform: t, snapGrid: n, snapToGrid: r, nodeOrigin: i, domNode: a } = C.getState();
				return {
					nodeLookup: e,
					transform: t,
					snapGrid: n,
					snapToGrid: r,
					nodeOrigin: i,
					paneDomNode: a
				};
			},
			onChange: (e, t) => {
				let { triggerNodeChanges: n, nodeLookup: r, parentLookup: i, nodeOrigin: a } = C.getState(), o = [], s = {
					x: e.x,
					y: e.y
				}, c = r.get(S);
				if (c && c.expandParent && c.parentId) {
					let t = c.origin ?? a, n = e.width ?? c.measured.width ?? 0, l = e.height ?? c.measured.height ?? 0, u = St([{
						id: c.id,
						parentId: c.parentId,
						rect: {
							width: n,
							height: l,
							...be({
								x: e.x ?? c.position.x,
								y: e.y ?? c.position.y
							}, {
								width: n,
								height: l
							}, c.parentId, r, t)
						}
					}], r, i, a);
					o.push(...u), s.x = e.x ? Math.max(t[0] * n, e.x) : void 0, s.y = e.y ? Math.max(t[1] * l, e.y) : void 0;
				}
				if (s.x !== void 0 && s.y !== void 0) {
					let e = {
						id: S,
						type: "position",
						position: { ...s }
					};
					o.push(e);
				}
				if (e.width !== void 0 && e.height !== void 0) {
					let t = {
						id: S,
						type: "dimensions",
						resizing: !0,
						setAttributes: f ? f === "horizontal" ? "width" : "height" : !0,
						dimensions: {
							width: e.width,
							height: e.height
						}
					};
					o.push(t);
				}
				for (let e of t) {
					let t = {
						...e,
						type: "position"
					};
					o.push(t);
				}
				n(o);
			},
			onEnd: ({ width: e, height: t }) => {
				let n = {
					id: S,
					type: "dimensions",
					resizing: !1,
					dimensions: {
						width: e,
						height: t
					}
				};
				C.getState().triggerNodeChanges([n]);
			}
		}), D.current.update({
			controlPosition: O,
			boundaries: {
				minWidth: s,
				minHeight: c,
				maxWidth: l,
				maxHeight: u
			},
			keepAspectRatio: d,
			resizeDirection: f,
			onResizeStart: v,
			onResize: y,
			onResizeEnd: b,
			shouldResize: _
		}), () => {
			D.current?.destroy();
		};
	}, [
		O,
		s,
		c,
		l,
		u,
		d,
		v,
		y,
		b,
		_
	]);
	let k = O.split("-");
	return (0, h.jsx)("div", {
		className: g([
			"react-flow__resize-control",
			"nodrag",
			...k,
			n,
			r
		]),
		ref: w,
		style: {
			...i,
			scale: E,
			...o && { [T ? "backgroundColor" : "borderColor"]: o }
		},
		children: a
	});
}
var Uo = (0, m.memo)(Ho);
function Wo({ nodeId: e, isVisible: t = !0, handleClassName: n, handleStyle: r, lineClassName: i, lineStyle: a, color: o, minWidth: s = 10, minHeight: c = 10, maxWidth: l = Number.MAX_VALUE, maxHeight: u = Number.MAX_VALUE, keepAspectRatio: d = !1, autoScale: f = !0, shouldResize: p, onResizeStart: m, onResize: g, onResizeEnd: _ }) {
	return t ? (0, h.jsxs)(h.Fragment, { children: [cn.map((t) => (0, h.jsx)(Uo, {
		className: i,
		style: a,
		nodeId: e,
		position: t,
		variant: on.Line,
		color: o,
		minWidth: s,
		minHeight: c,
		maxWidth: l,
		maxHeight: u,
		onResizeStart: m,
		keepAspectRatio: d,
		autoScale: f,
		shouldResize: p,
		onResize: g,
		onResizeEnd: _
	}, t)), sn.map((t) => (0, h.jsx)(Uo, {
		className: n,
		style: r,
		nodeId: e,
		position: t,
		color: o,
		minWidth: s,
		minHeight: c,
		maxWidth: l,
		maxHeight: u,
		onResizeStart: m,
		keepAspectRatio: d,
		autoScale: f,
		shouldResize: p,
		onResize: g,
		onResizeEnd: _
	}, t))] }) : null;
}
var Go = (e) => e.domNode?.querySelector(".react-flow__renderer");
function Ko({ children: e }) {
	let t = Q(Go);
	return t ? (0, Dn.createPortal)(e, t) : null;
}
var qo = (e, t) => e?.internals.positionAbsolute.x !== t?.internals.positionAbsolute.x || e?.internals.positionAbsolute.y !== t?.internals.positionAbsolute.y || e?.measured.width !== t?.measured.width || e?.measured.height !== t?.measured.height || e?.selected !== t?.selected || e?.internals.z !== t?.internals.z, Jo = (e, t) => {
	if (e.size !== t.size) return !1;
	for (let [n, r] of e) if (qo(r, t.get(n))) return !1;
	return !0;
}, Yo = (e) => ({
	x: e.transform[0],
	y: e.transform[1],
	zoom: e.transform[2],
	selectedNodesCount: e.nodes.filter((e) => e.selected).length
});
function Xo({ nodeId: e, children: t, className: n, style: r, isVisible: i, position: a = D.Top, offset: o = 10, align: s = "center", ...c }) {
	let l = Jr(), u = Q((0, m.useCallback)((t) => (Array.isArray(e) ? e : [e || l || ""]).reduce((e, n) => {
		let r = t.nodeLookup.get(n);
		return r && e.set(r.id, r), e;
	}, /* @__PURE__ */ new Map()), [e, l]), Jo), { x: d, y: f, zoom: p, selectedNodesCount: _ } = Q(Yo, Z);
	if (!(typeof i == "boolean" ? i : u.size === 1 && u.values().next().value?.selected && _ === 1) || !u.size) return null;
	let v = I(u), y = Array.from(u.values()), b = Math.max(...y.map((e) => e.internals.z + 1)), x = {
		position: "absolute",
		transform: at(v, {
			x: d,
			y: f,
			zoom: p
		}, a, o, s),
		zIndex: b,
		...r
	};
	return (0, h.jsx)(Ko, { children: (0, h.jsx)("div", {
		style: x,
		className: g(["react-flow__node-toolbar", n]),
		...c,
		"data-id": y.reduce((e, t) => `${e}${t.id} `, "").trim(),
		children: t
	}) });
}
var Zo = (e) => e.transform[2];
function Qo({ edgeId: e, x: t, y: n, children: r, className: i, style: a, isVisible: o, alignX: s = "center", alignY: c = "center", ...l }) {
	let u = Q((0, m.useCallback)((t) => t.edgeLookup.get(e), [e]), Z), d = typeof o == "boolean" ? o : u?.selected, f = Q(Zo);
	if (!d) return null;
	let p = (u?.zIndex ?? 0) + 1, _ = ct(t, n, f, s, c);
	return (0, h.jsx)(La, { children: (0, h.jsx)("div", {
		style: {
			position: "absolute",
			transform: _,
			zIndex: p,
			pointerEvents: "all",
			transformOrigin: "0 0",
			...a
		},
		className: g(["react-flow__edge-toolbar", i]),
		"data-id": u?.id ?? "",
		...l,
		children: r
	}) });
}
//#endregion
export { po as Background, co as BackgroundVariant, Ii as BaseEdge, Qi as BezierEdge, T as ConnectionLineType, x as ConnectionMode, yo as ControlButton, So as Controls, La as EdgeLabelRenderer, Fi as EdgeText, Qo as EdgeToolbar, ni as Handle, E as MarkerType, zo as MiniMap, wo as MiniMapNode, Uo as NodeResizeControl, Wo as NodeResizer, Xo as NodeToolbar, S as PanOnScrollMode, Bn as Panel, D as Position, Fa as ReactFlow, ja as ReactFlowProvider, on as ResizeControlVariant, C as SelectionMode, Bi as SimpleBezierEdge, Ui as SmoothStepEdge, Ki as StepEdge, Yi as StraightEdge, za as ViewportPortal, _r as addEdge, dr as applyEdgeChanges, ur as applyNodeChanges, ao as experimental_useOnEdgesChangeMiddleware, io as experimental_useOnNodesChangeMiddleware, Pe as getBezierEdgeCenter, Le as getBezierPath, R as getConnectedEdges, Re as getEdgeCenter, N as getIncomers, F as getNodesBounds, M as getOutgoers, Ri as getSimpleBezierPath, Ze as getSmoothStepPath, Ge as getStraightPath, ge as getViewportForBounds, br as isEdge, yr as isNode, vr as reconnectEdge, ya as useConnection, Wa as useEdges, Ja as useEdgesState, $a as useHandleConnections, ro as useInternalNode, ir as useKeyPress, to as useNodeConnections, Jr as useNodeId, Ha as useNodes, no as useNodesData, Qa as useNodesInitialized, qa as useNodesState, Xa as useOnSelectionChange, Ya as useOnViewportChange, kr as useReactFlow, Q as useStore, $ as useStoreApi, Ba as useUpdateNodeInternals, Ka as useViewport };
