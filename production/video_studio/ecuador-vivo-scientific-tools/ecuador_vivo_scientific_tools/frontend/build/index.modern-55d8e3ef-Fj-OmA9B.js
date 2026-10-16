import { o as e, t } from "./rolldown-runtime-CEFd7nDs.js";
import { t as n } from "./react-BOiH87ah.js";
import { t as r } from "./react-dom-B0_m6Nyz.js";
import { t as i } from "./jsx-runtime-xKqbzy7D.js";
import { l as a, n as o, t as s } from "./extends-Dx66qMaz.js";
import { $n as c, $t as l, A as u, Accordion as d, AmbiguousMonomerPreview as f, An as p, ArrowScroll as m, At as h, B as g, Bn as _, Bt as v, Button as y, C as b, Cn as x, Ct as S, D as C, Dn as w, Dt as T, E, EditorClassName as D, En as O, Et as k, F as A, Fn as j, Ft as ee, G as te, Gn as M, Gt as ne, H as re, Hn as N, Ht as ie, I as ae, Icon as P, IconButton as oe, In as se, IndigoProvider as ce, Input as le, It as ue, J as de, Jn as fe, Jt as pe, K as me, KETCHER_MACROMOLECULES_ROOT_NODE_SELECTOR as he, Kn as ge, Kt as _e, L as F, Ln as ve, Lt as ye, M as be, Mn as xe, Mt as Se, N as Ce, Nn as we, Nt as Te, O as Ee, On as De, Ot as Oe, P as ke, Pn as Ae, Pt as je, Q as Me, Qn as Ne, Qt as Pe, R as Fe, Rn as Ie, Rt as Le, S as Re, Sn as ze, St as Be, StructRender as Ve, T as He, Tn as Ue, Tt as We, U as Ge, Un as Ke, Ut as qe, V as Je, Vn as Ye, Vt as Xe, W as Ze, Wn as Qe, Wt as $e, X as et, Xn as tt, Xt as nt, Y as rt, Yn as it, Yt as at, Z as ot, Zn as st, Zt as ct, _ as lt, _n as ut, _t as dt, a as ft, an as pt, ar as mt, at as ht, b as gt, bn as _t, bt as vt, c as yt, calculateAmbiguousMonomerPreviewTop as bt, calculateBondPreviewPosition as xt, calculateMonomerPreviewTop as St, calculateNucleoElementPreviewTop as Ct, cn as wt, cr as I, ct as Tt, d as Et, dn as Dt, dt as Ot, en as kt, er as At, et as jt, f as Mt, fn as Nt, ft as Pt, g as Ft, getFullscreenElement as It, gn as Lt, gt as Rt, h as zt, hn as Bt, ht as Vt, i as Ht, in as Ut, ir as Wt, it as Gt, j as Kt, jn as qt, jt as Jt, k as Yt, kn as Xt, kt as Zt, l as Qt, ln as $t, lr as en, lt as tn, m as nn, mn as rn, mt as an, n as on, nn as sn, nr as L, nt as cn, o as ln, on as un, or as dn, ot as fn, p as pn, pn as mn, preview as hn, pt as gn, q as _n, qn as vn, qt as yn, r as bn, rn as xn, rr as Sn, rt as Cn, s as wn, sn as Tn, sr as R, st as En, tn as Dn, tr as On, u as kn, un as An, usePortalStyle as jn, ut as Mn, v as Nn, vn as Pn, vt as z, w as Fn, wn as In, wt as Ln, x as Rn, xn as zn, xt as Bn, y as Vn, yn as Hn, yt as Un, z as Wn, zn as Gn, zt as Kn } from "./dist-jB_mkE3r.js";
//#region ../../../resource_engines/node_modules/ketcher-core/dist/application/formatters/constants.modern.js
var qn = {
	ket: "chemical/x-indigo-ket",
	mol: "chemical/x-mdl-molfile",
	seq: {
		rna: "chemical/x-rna-sequence",
		dna: "chemical/x-dna-sequence",
		peptide: "chemical/x-peptide-sequence",
		peptide3Letter: "chemical/x-peptide-sequence-3-letter"
	},
	fasta: {
		rna: "chemical/x-rna-fasta",
		dna: "chemical/x-dna-fasta",
		peptide: "chemical/x-peptide-fasta"
	},
	idt: "chemical/x-idt",
	"axo-labs": "chemical/x-axo-labs",
	helm: "chemical/x-helm",
	biln: "chemical/x-biln"
};
//#endregion
//#region ../../../resource_engines/node_modules/@mui/system/node_modules/clsx/dist/clsx.mjs
function Jn(e) {
	var t, n, r = "";
	if (typeof e == "string" || typeof e == "number") r += e;
	else if (typeof e == "object") {
		if (Array.isArray(e)) {
			var i = e.length;
			for (t = 0; t < i; t++) e[t] && (n = Jn(e[t])) && (r && (r += " "), r += n);
		} else for (n in e) e[n] && (r && (r += " "), r += n);
	}
	return r;
}
function Yn() {
	for (var e, t, n = 0, r = "", i = arguments.length; n < i; n++) (e = arguments[n]) && (t = Jn(e)) && (r && (r += " "), r += t);
	return r;
}
o(), Gn();
var B = /* @__PURE__ */ e(n());
Cn(), ot();
var V = /* @__PURE__ */ e(i()), Xn = ["className", "component"];
function Zn(e = {}) {
	let { themeId: t, defaultTheme: n, defaultClassName: r = "MuiBox-root", generateClassName: i } = e, a = Gt("div", { shouldForwardProp: (e) => e !== "theme" && e !== "sx" && e !== "as" })(cn);
	return /* @__PURE__ */ B.forwardRef(function(e, o) {
		let c = jt(n), l = Me(e), { className: u, component: d = "div" } = l, f = Ie(l, Xn);
		return /*#__PURE__*/ (0, V.jsx)(a, s({
			as: d,
			ref: o,
			className: Yn(u, i ? i(r) : r),
			theme: t && c[t] || c
		}, f));
	});
}
//#endregion
//#region ../../../resource_engines/node_modules/@mui/utils/esm/getValidReactChildren/getValidReactChildren.js
function Qn(e) {
	return B.Children.toArray(e).filter((e) => /*#__PURE__*/ B.isValidElement(e));
}
//#endregion
//#region ../../../resource_engines/node_modules/@mui/material/Typography/typographyClasses.js
function $n(e) {
	return rt("MuiTypography", e);
}
de("MuiTypography", [
	"root",
	"h1",
	"h2",
	"h3",
	"h4",
	"h5",
	"h6",
	"subtitle1",
	"subtitle2",
	"body1",
	"body2",
	"inherit",
	"button",
	"caption",
	"overline",
	"alignLeft",
	"alignRight",
	"alignCenter",
	"alignJustify",
	"noWrap",
	"gutterBottom",
	"paragraph"
]), Gn(), o(), ot();
var er = [
	"align",
	"className",
	"component",
	"gutterBottom",
	"noWrap",
	"paragraph",
	"variant",
	"variantMapping"
], tr = (e) => {
	let { align: t, gutterBottom: n, noWrap: r, paragraph: i, variant: a, classes: o } = e, s = { root: [
		"root",
		a,
		e.align !== "inherit" && `align${g(t)}`,
		n && "gutterBottom",
		r && "noWrap",
		i && "paragraph"
	] };
	return me(s, $n, o);
}, nr = Je("span", {
	name: "MuiTypography",
	slot: "Root",
	overridesResolver: (e, t) => {
		let { ownerState: n } = e;
		return [
			t.root,
			n.variant && t[n.variant],
			n.align !== "inherit" && t[`align${g(n.align)}`],
			n.noWrap && t.noWrap,
			n.gutterBottom && t.gutterBottom,
			n.paragraph && t.paragraph
		];
	}
})(({ theme: e, ownerState: t }) => s({ margin: 0 }, t.variant === "inherit" && { font: "inherit" }, t.variant !== "inherit" && e.typography[t.variant], t.align !== "inherit" && { textAlign: t.align }, t.noWrap && {
	overflow: "hidden",
	textOverflow: "ellipsis",
	whiteSpace: "nowrap"
}, t.gutterBottom && { marginBottom: "0.35em" }, t.paragraph && { marginBottom: 16 })), rr = {
	h1: "h1",
	h2: "h2",
	h3: "h3",
	h4: "h4",
	h5: "h5",
	h6: "h6",
	subtitle1: "h6",
	subtitle2: "h6",
	body1: "p",
	body2: "p",
	inherit: "p"
}, ir = {
	primary: "primary.main",
	textPrimary: "text.primary",
	secondary: "secondary.main",
	textSecondary: "text.secondary",
	error: "error.main"
}, ar = (e) => ir[e] || e, or = /*#__PURE__*/ B.forwardRef(function(e, t) {
	let n = Fe({
		props: e,
		name: "MuiTypography"
	}), r = ar(n.color), i = Me(s({}, n, { color: r })), { align: a = "inherit", className: o, component: c, gutterBottom: l = !1, noWrap: u = !1, paragraph: d = !1, variant: f = "body1", variantMapping: p = rr } = i, m = Ie(i, er), h = s({}, i, {
		align: a,
		color: r,
		className: o,
		component: c,
		gutterBottom: l,
		noWrap: u,
		paragraph: d,
		variant: f,
		variantMapping: p
	}), g = c || (d ? "p" : p[f] || rr[f]) || "span", _ = tr(h);
	return /*#__PURE__*/ (0, V.jsx)(nr, s({
		as: g,
		ref: t,
		ownerState: h,
		className: Wn(_.root, o)
	}, m));
}), sr = de("MuiBox", ["root"]), cr = Ze(), lr = Zn({
	themeId: ht,
	defaultTheme: cr,
	defaultClassName: sr.root,
	generateClassName: et.generate
});
//#endregion
//#region ../../../resource_engines/node_modules/@mui/material/ButtonGroup/buttonGroupClasses.js
function ur(e) {
	return rt("MuiButtonGroup", e);
}
var dr = de("MuiButtonGroup", /* @__PURE__ */ "root.contained.outlined.text.disableElevation.disabled.firstButton.fullWidth.vertical.grouped.groupedHorizontal.groupedVertical.groupedText.groupedTextHorizontal.groupedTextVertical.groupedTextPrimary.groupedTextSecondary.groupedOutlined.groupedOutlinedHorizontal.groupedOutlinedVertical.groupedOutlinedPrimary.groupedOutlinedSecondary.groupedContained.groupedContainedHorizontal.groupedContainedVertical.groupedContainedPrimary.groupedContainedSecondary.lastButton.middleButton".split("."));
Gn(), o();
var fr = te(), pr = [
	"children",
	"className",
	"color",
	"component",
	"disabled",
	"disableElevation",
	"disableFocusRipple",
	"disableRipple",
	"fullWidth",
	"orientation",
	"size",
	"variant"
], mr = (e, t) => {
	let { ownerState: n } = e;
	return [
		{ [`& .${dr.grouped}`]: t.grouped },
		{ [`& .${dr.grouped}`]: t[`grouped${g(n.orientation)}`] },
		{ [`& .${dr.grouped}`]: t[`grouped${g(n.variant)}`] },
		{ [`& .${dr.grouped}`]: t[`grouped${g(n.variant)}${g(n.orientation)}`] },
		{ [`& .${dr.grouped}`]: t[`grouped${g(n.variant)}${g(n.color)}`] },
		{ [`& .${dr.firstButton}`]: t.firstButton },
		{ [`& .${dr.lastButton}`]: t.lastButton },
		{ [`& .${dr.middleButton}`]: t.middleButton },
		t.root,
		t[n.variant],
		n.disableElevation === !0 && t.disableElevation,
		n.fullWidth && t.fullWidth,
		n.orientation === "vertical" && t.vertical
	];
}, hr = (e) => {
	let { classes: t, color: n, disabled: r, disableElevation: i, fullWidth: a, orientation: o, variant: s } = e, c = {
		root: [
			"root",
			s,
			o === "vertical" && "vertical",
			a && "fullWidth",
			i && "disableElevation"
		],
		grouped: [
			"grouped",
			`grouped${g(o)}`,
			`grouped${g(s)}`,
			`grouped${g(s)}${g(o)}`,
			`grouped${g(s)}${g(n)}`,
			r && "disabled"
		],
		firstButton: ["firstButton"],
		lastButton: ["lastButton"],
		middleButton: ["middleButton"]
	};
	return me(c, ur, t);
}, gr = Je("div", {
	name: "MuiButtonGroup",
	slot: "Root",
	overridesResolver: mr
})(({ theme: e, ownerState: t }) => s({
	display: "inline-flex",
	borderRadius: (e.vars || e).shape.borderRadius
}, t.variant === "contained" && { boxShadow: (e.vars || e).shadows[2] }, t.disableElevation && { boxShadow: "none" }, t.fullWidth && { width: "100%" }, t.orientation === "vertical" && { flexDirection: "column" }, {
	[`& .${dr.grouped}`]: s({
		minWidth: 40,
		"&:hover": s({}, t.variant === "contained" && { boxShadow: "none" })
	}, t.variant === "contained" && { boxShadow: "none" }),
	[`& .${dr.firstButton},& .${dr.middleButton}`]: s({}, t.orientation === "horizontal" && {
		borderTopRightRadius: 0,
		borderBottomRightRadius: 0
	}, t.orientation === "vertical" && {
		borderBottomRightRadius: 0,
		borderBottomLeftRadius: 0
	}, t.variant === "text" && t.orientation === "horizontal" && {
		borderRight: e.vars ? `1px solid rgba(${e.vars.palette.common.onBackgroundChannel} / 0.23)` : `1px solid ${e.palette.mode === "light" ? "rgba(0, 0, 0, 0.23)" : "rgba(255, 255, 255, 0.23)"}`,
		[`&.${dr.disabled}`]: { borderRight: `1px solid ${(e.vars || e).palette.action.disabled}` }
	}, t.variant === "text" && t.orientation === "vertical" && {
		borderBottom: e.vars ? `1px solid rgba(${e.vars.palette.common.onBackgroundChannel} / 0.23)` : `1px solid ${e.palette.mode === "light" ? "rgba(0, 0, 0, 0.23)" : "rgba(255, 255, 255, 0.23)"}`,
		[`&.${dr.disabled}`]: { borderBottom: `1px solid ${(e.vars || e).palette.action.disabled}` }
	}, t.variant === "text" && t.color !== "inherit" && { borderColor: e.vars ? `rgba(${e.vars.palette[t.color].mainChannel} / 0.5)` : (0, fr.alpha)(e.palette[t.color].main, .5) }, t.variant === "outlined" && t.orientation === "horizontal" && { borderRightColor: "transparent" }, t.variant === "outlined" && t.orientation === "vertical" && { borderBottomColor: "transparent" }, t.variant === "contained" && t.orientation === "horizontal" && {
		borderRight: `1px solid ${(e.vars || e).palette.grey[400]}`,
		[`&.${dr.disabled}`]: { borderRight: `1px solid ${(e.vars || e).palette.action.disabled}` }
	}, t.variant === "contained" && t.orientation === "vertical" && {
		borderBottom: `1px solid ${(e.vars || e).palette.grey[400]}`,
		[`&.${dr.disabled}`]: { borderBottom: `1px solid ${(e.vars || e).palette.action.disabled}` }
	}, t.variant === "contained" && t.color !== "inherit" && { borderColor: (e.vars || e).palette[t.color].dark }, { "&:hover": s({}, t.variant === "outlined" && t.orientation === "horizontal" && { borderRightColor: "currentColor" }, t.variant === "outlined" && t.orientation === "vertical" && { borderBottomColor: "currentColor" }) }),
	[`& .${dr.lastButton},& .${dr.middleButton}`]: s({}, t.orientation === "horizontal" && {
		borderTopLeftRadius: 0,
		borderBottomLeftRadius: 0
	}, t.orientation === "vertical" && {
		borderTopRightRadius: 0,
		borderTopLeftRadius: 0
	}, t.variant === "outlined" && t.orientation === "horizontal" && { marginLeft: -1 }, t.variant === "outlined" && t.orientation === "vertical" && { marginTop: -1 })
})), _r = /*#__PURE__*/ B.forwardRef(function(e, t) {
	let n = Fe({
		props: e,
		name: "MuiButtonGroup"
	}), { children: r, className: i, color: a = "primary", component: o = "div", disabled: c = !1, disableElevation: l = !1, disableFocusRipple: u = !1, disableRipple: d = !1, fullWidth: f = !1, orientation: p = "horizontal", size: m = "medium", variant: h = "outlined" } = n, g = Ie(n, pr), _ = s({}, n, {
		color: a,
		component: o,
		disabled: c,
		disableElevation: l,
		disableFocusRipple: u,
		disableRipple: d,
		fullWidth: f,
		orientation: p,
		size: m,
		variant: h
	}), v = hr(_), y = B.useMemo(() => ({
		className: v.grouped,
		color: a,
		disabled: c,
		disableElevation: l,
		disableFocusRipple: u,
		disableRipple: d,
		fullWidth: f,
		size: m,
		variant: h
	}), [
		a,
		c,
		l,
		u,
		d,
		f,
		m,
		h,
		v.grouped
	]), b = Qn(r), x = b.length, S = (e) => {
		let t = e === 0, n = e === x - 1;
		return t && n ? "" : t ? v.firstButton : n ? v.lastButton : v.middleButton;
	};
	return /*#__PURE__*/ (0, V.jsx)(gr, s({
		as: o,
		role: "group",
		className: Wn(v.root, i),
		ref: t,
		ownerState: _
	}, g, { children: /*#__PURE__*/ (0, V.jsx)(E.Provider, {
		value: y,
		children: b.map((e, t) => /*#__PURE__*/ (0, V.jsx)(He.Provider, {
			value: S(t),
			children: e
		}, t))
	}) }));
});
//#endregion
//#region ../../../resource_engines/node_modules/@mui/material/internal/switchBaseClasses.js
function vr(e) {
	return rt("PrivateSwitchBase", e);
}
de("PrivateSwitchBase", [
	"root",
	"checked",
	"disabled",
	"input",
	"edgeStart",
	"edgeEnd"
]), Gn(), o();
var yr = [
	"autoFocus",
	"checked",
	"checkedIcon",
	"className",
	"defaultChecked",
	"disabled",
	"disableFocusRipple",
	"edge",
	"icon",
	"id",
	"inputProps",
	"inputRef",
	"name",
	"onBlur",
	"onChange",
	"onFocus",
	"readOnly",
	"required",
	"tabIndex",
	"type",
	"value"
], br = (e) => {
	let { classes: t, checked: n, disabled: r, edge: i } = e, a = {
		root: [
			"root",
			n && "checked",
			r && "disabled",
			i && `edge${g(i)}`
		],
		input: ["input"]
	};
	return me(a, vr, t);
}, xr = Je(be, { name: "MuiSwitchBase" })(({ ownerState: e }) => s({
	padding: 9,
	borderRadius: "50%"
}, e.edge === "start" && { marginLeft: e.size === "small" ? -3 : -12 }, e.edge === "end" && { marginRight: e.size === "small" ? -3 : -12 })), Sr = Je("input", {
	name: "MuiSwitchBase",
	shouldForwardProp: re
})({
	cursor: "inherit",
	position: "absolute",
	opacity: 0,
	width: "100%",
	height: "100%",
	top: 0,
	left: 0,
	margin: 0,
	padding: 0,
	zIndex: 1
}), Cr = /*#__PURE__*/ B.forwardRef(function(e, t) {
	let { autoFocus: n, checked: r, checkedIcon: i, className: a, defaultChecked: o, disabled: c, disableFocusRipple: l = !1, edge: u = !1, icon: d, id: f, inputProps: p, inputRef: m, name: h, onBlur: g, onChange: _, onFocus: v, readOnly: y, required: b = !1, tabIndex: x, type: S, value: C } = e, w = Ie(e, yr), [T, E] = F({
		controlled: r,
		default: !!o,
		name: "SwitchBase",
		state: "checked"
	}), D = Yt(), O = (e) => {
		v && v(e), D && D.onFocus && D.onFocus(e);
	}, k = (e) => {
		g && g(e), D && D.onBlur && D.onBlur(e);
	}, A = (e) => {
		if (e.nativeEvent.defaultPrevented) return;
		let t = e.target.checked;
		E(t), _ && _(e, t);
	}, j = c;
	D && j === void 0 && (j = D.disabled);
	let ee = S === "checkbox" || S === "radio", te = s({}, e, {
		checked: T,
		disabled: j,
		disableFocusRipple: l,
		edge: u
	}), M = br(te);
	return /*#__PURE__*/ (0, V.jsxs)(xr, s({
		component: "span",
		className: Wn(M.root, a),
		centerRipple: !0,
		focusRipple: !l,
		disabled: j,
		tabIndex: null,
		role: void 0,
		onFocus: O,
		onBlur: k,
		ownerState: te,
		ref: t
	}, w, { children: [/*#__PURE__*/ (0, V.jsx)(Sr, s({
		autoFocus: n,
		checked: r,
		defaultChecked: o,
		className: M.input,
		disabled: j,
		id: ee ? f : void 0,
		name: h,
		onChange: A,
		readOnly: y,
		ref: m,
		required: b,
		ownerState: te,
		tabIndex: x,
		type: S
	}, S === "checkbox" && C === void 0 ? {} : { value: C }, p)), T ? i : d] }));
});
//#endregion
//#region ../../../resource_engines/node_modules/@mui/material/Dialog/dialogClasses.js
function wr(e) {
	return rt("MuiDialog", e);
}
var Tr = de("MuiDialog", [
	"root",
	"scrollPaper",
	"scrollBody",
	"container",
	"paper",
	"paperScrollPaper",
	"paperScrollBody",
	"paperWidthFalse",
	"paperWidthXs",
	"paperWidthSm",
	"paperWidthMd",
	"paperWidthLg",
	"paperWidthXl",
	"paperFullWidth",
	"paperFullScreen"
]), Er = /*#__PURE__*/ B.createContext({});
Gn(), o();
var Dr = [
	"aria-describedby",
	"aria-labelledby",
	"BackdropComponent",
	"BackdropProps",
	"children",
	"className",
	"disableEscapeKeyDown",
	"fullScreen",
	"fullWidth",
	"maxWidth",
	"onBackdropClick",
	"onClick",
	"onClose",
	"open",
	"PaperComponent",
	"PaperProps",
	"scroll",
	"TransitionComponent",
	"transitionDuration",
	"TransitionProps"
], Or = Je(C, {
	name: "MuiDialog",
	slot: "Backdrop",
	overrides: (e, t) => t.backdrop
})({ zIndex: -1 }), kr = (e) => {
	let { classes: t, scroll: n, maxWidth: r, fullWidth: i, fullScreen: a } = e, o = {
		root: ["root"],
		container: ["container", `scroll${g(n)}`],
		paper: [
			"paper",
			`paperScroll${g(n)}`,
			`paperWidth${g(String(r))}`,
			i && "paperFullWidth",
			a && "paperFullScreen"
		]
	};
	return me(o, wr, t);
}, Ar = Je(Re, {
	name: "MuiDialog",
	slot: "Root",
	overridesResolver: (e, t) => t.root
})({ "@media print": { position: "absolute !important" } }), jr = Je("div", {
	name: "MuiDialog",
	slot: "Container",
	overridesResolver: (e, t) => {
		let { ownerState: n } = e;
		return [t.container, t[`scroll${g(n.scroll)}`]];
	}
})(({ ownerState: e }) => s({
	height: "100%",
	"@media print": { height: "auto" },
	outline: 0
}, e.scroll === "paper" && {
	display: "flex",
	justifyContent: "center",
	alignItems: "center"
}, e.scroll === "body" && {
	overflowY: "auto",
	overflowX: "hidden",
	textAlign: "center",
	"&::after": {
		content: "\"\"",
		display: "inline-block",
		verticalAlign: "middle",
		height: "100%",
		width: "0"
	}
})), Mr = Je(A, {
	name: "MuiDialog",
	slot: "Paper",
	overridesResolver: (e, t) => {
		let { ownerState: n } = e;
		return [
			t.paper,
			t[`scrollPaper${g(n.scroll)}`],
			t[`paperWidth${g(String(n.maxWidth))}`],
			n.fullWidth && t.paperFullWidth,
			n.fullScreen && t.paperFullScreen
		];
	}
})(({ theme: e, ownerState: t }) => s({
	margin: 32,
	position: "relative",
	overflowY: "auto",
	"@media print": {
		overflowY: "visible",
		boxShadow: "none"
	}
}, t.scroll === "paper" && {
	display: "flex",
	flexDirection: "column",
	maxHeight: "calc(100% - 64px)"
}, t.scroll === "body" && {
	display: "inline-block",
	verticalAlign: "middle",
	textAlign: "left"
}, !t.maxWidth && { maxWidth: "calc(100% - 64px)" }, t.maxWidth === "xs" && {
	maxWidth: e.breakpoints.unit === "px" ? Math.max(e.breakpoints.values.xs, 444) : `max(${e.breakpoints.values.xs}${e.breakpoints.unit}, 444px)`,
	[`&.${Tr.paperScrollBody}`]: { [e.breakpoints.down(Math.max(e.breakpoints.values.xs, 444) + 64)]: { maxWidth: "calc(100% - 64px)" } }
}, t.maxWidth && t.maxWidth !== "xs" && {
	maxWidth: `${e.breakpoints.values[t.maxWidth]}${e.breakpoints.unit}`,
	[`&.${Tr.paperScrollBody}`]: { [e.breakpoints.down(e.breakpoints.values[t.maxWidth] + 64)]: { maxWidth: "calc(100% - 64px)" } }
}, t.fullWidth && { width: "calc(100% - 64px)" }, t.fullScreen && {
	margin: 0,
	width: "100%",
	maxWidth: "100%",
	height: "100%",
	maxHeight: "none",
	borderRadius: 0,
	[`&.${Tr.paperScrollBody}`]: {
		margin: 0,
		maxWidth: "100%"
	}
})), Nr = /*#__PURE__*/ B.forwardRef(function(e, t) {
	let n = Fe({
		props: e,
		name: "MuiDialog"
	}), r = Ge(), i = {
		enter: r.transitions.duration.enteringScreen,
		exit: r.transitions.duration.leavingScreen
	}, { "aria-describedby": a, "aria-labelledby": o, BackdropComponent: c, BackdropProps: l, children: u, className: d, disableEscapeKeyDown: f = !1, fullScreen: p = !1, fullWidth: m = !1, maxWidth: h = "sm", onBackdropClick: g, onClick: _, onClose: v, open: y, PaperComponent: b = A, PaperProps: x = {}, scroll: S = "paper", TransitionComponent: C = Ee, transitionDuration: w = i, TransitionProps: T } = n, E = Ie(n, Dr), D = s({}, n, {
		disableEscapeKeyDown: f,
		fullScreen: p,
		fullWidth: m,
		maxWidth: h,
		scroll: S
	}), O = kr(D), k = B.useRef(), j = (e) => {
		k.current = e.target === e.currentTarget;
	}, ee = (e) => {
		_ && _(e), k.current && (k.current = null, g && g(e), v && v(e, "backdropClick"));
	}, te = _n(o), M = B.useMemo(() => ({ titleId: te }), [te]);
	return /*#__PURE__*/ (0, V.jsx)(Ar, s({
		className: Wn(O.root, d),
		closeAfterTransition: !0,
		components: { Backdrop: Or },
		componentsProps: { backdrop: s({
			transitionDuration: w,
			as: c
		}, l) },
		disableEscapeKeyDown: f,
		onClose: v,
		open: y,
		ref: t,
		onClick: ee,
		ownerState: D
	}, E, { children: /*#__PURE__*/ (0, V.jsx)(C, s({
		appear: !0,
		in: y,
		timeout: w,
		role: "presentation"
	}, T, { children: /*#__PURE__*/ (0, V.jsx)(jr, {
		className: Wn(O.container),
		onMouseDown: j,
		ownerState: D,
		children: /*#__PURE__*/ (0, V.jsx)(Mr, s({
			as: b,
			elevation: 24,
			role: "dialog",
			"aria-describedby": a,
			"aria-labelledby": te
		}, x, {
			className: Wn(O.paper, x.className),
			ownerState: D,
			children: /*#__PURE__*/ (0, V.jsx)(Er.Provider, {
				value: M,
				children: u
			})
		}))
	}) })) }));
});
//#endregion
//#region ../../../resource_engines/node_modules/@mui/material/DialogActions/dialogActionsClasses.js
function Pr(e) {
	return rt("MuiDialogActions", e);
}
de("MuiDialogActions", ["root", "spacing"]), Gn(), o();
var Fr = ["className", "disableSpacing"], Ir = (e) => {
	let { classes: t, disableSpacing: n } = e;
	return me({ root: ["root", !n && "spacing"] }, Pr, t);
}, Lr = Je("div", {
	name: "MuiDialogActions",
	slot: "Root",
	overridesResolver: (e, t) => {
		let { ownerState: n } = e;
		return [t.root, !n.disableSpacing && t.spacing];
	}
})(({ ownerState: e }) => s({
	display: "flex",
	alignItems: "center",
	padding: 8,
	justifyContent: "flex-end",
	flex: "0 0 auto"
}, !e.disableSpacing && { "& > :not(style) ~ :not(style)": { marginLeft: 8 } })), Rr = /*#__PURE__*/ B.forwardRef(function(e, t) {
	let n = Fe({
		props: e,
		name: "MuiDialogActions"
	}), { className: r, disableSpacing: i = !1 } = n, a = Ie(n, Fr), o = s({}, n, { disableSpacing: i }), c = Ir(o);
	return /*#__PURE__*/ (0, V.jsx)(Lr, s({
		className: Wn(c.root, r),
		ownerState: o,
		ref: t
	}, a));
});
//#endregion
//#region ../../../resource_engines/node_modules/@mui/material/DialogContent/dialogContentClasses.js
function zr(e) {
	return rt("MuiDialogContent", e);
}
de("MuiDialogContent", ["root", "dividers"]);
//#endregion
//#region ../../../resource_engines/node_modules/@mui/material/DialogTitle/dialogTitleClasses.js
function Br(e) {
	return rt("MuiDialogTitle", e);
}
var Vr = de("MuiDialogTitle", ["root"]);
Gn(), o();
var Hr = ["className", "dividers"], Ur = (e) => {
	let { classes: t, dividers: n } = e;
	return me({ root: ["root", n && "dividers"] }, zr, t);
}, Wr = Je("div", {
	name: "MuiDialogContent",
	slot: "Root",
	overridesResolver: (e, t) => {
		let { ownerState: n } = e;
		return [t.root, n.dividers && t.dividers];
	}
})(({ theme: e, ownerState: t }) => s({
	flex: "1 1 auto",
	WebkitOverflowScrolling: "touch",
	overflowY: "auto",
	padding: "20px 24px"
}, t.dividers ? {
	padding: "16px 24px",
	borderTop: `1px solid ${(e.vars || e).palette.divider}`,
	borderBottom: `1px solid ${(e.vars || e).palette.divider}`
} : { [`.${Vr.root} + &`]: { paddingTop: 0 } })), Gr = /*#__PURE__*/ B.forwardRef(function(e, t) {
	let n = Fe({
		props: e,
		name: "MuiDialogContent"
	}), { className: r, dividers: i = !1 } = n, a = Ie(n, Hr), o = s({}, n, { dividers: i }), c = Ur(o);
	return /*#__PURE__*/ (0, V.jsx)(Wr, s({
		className: Wn(c.root, r),
		ownerState: o,
		ref: t
	}, a));
});
o(), Gn();
var Kr = ["className", "id"], qr = (e) => {
	let { classes: t } = e;
	return me({ root: ["root"] }, Br, t);
}, Jr = Je(or, {
	name: "MuiDialogTitle",
	slot: "Root",
	overridesResolver: (e, t) => t.root
})({
	padding: "16px 24px",
	flex: "0 0 auto"
}), Yr = /*#__PURE__*/ B.forwardRef(function(e, t) {
	let n = Fe({
		props: e,
		name: "MuiDialogTitle"
	}), { className: r, id: i } = n, a = Ie(n, Kr), o = n, c = qr(o), { titleId: l = i } = B.useContext(Er);
	return /*#__PURE__*/ (0, V.jsx)(Jr, s({
		component: "h2",
		className: Wn(c.root, r),
		ownerState: o,
		ref: t,
		variant: "h6",
		id: i ?? l
	}, a));
});
Gn(), o();
var Xr = [
	"children",
	"className",
	"disableTypography",
	"inset",
	"primary",
	"primaryTypographyProps",
	"secondary",
	"secondaryTypographyProps"
], Zr = (e) => {
	let { classes: t, inset: n, primary: r, secondary: i, dense: a } = e;
	return me({
		root: [
			"root",
			n && "inset",
			a && "dense",
			r && i && "multiline"
		],
		primary: ["primary"],
		secondary: ["secondary"]
	}, Nn, t);
}, Qr = Je("div", {
	name: "MuiListItemText",
	slot: "Root",
	overridesResolver: (e, t) => {
		let { ownerState: n } = e;
		return [
			{ [`& .${Vn.primary}`]: t.primary },
			{ [`& .${Vn.secondary}`]: t.secondary },
			t.root,
			n.inset && t.inset,
			n.primary && n.secondary && t.multiline,
			n.dense && t.dense
		];
	}
})(({ ownerState: e }) => s({
	flex: "1 1 auto",
	minWidth: 0,
	marginTop: 4,
	marginBottom: 4
}, e.primary && e.secondary && {
	marginTop: 6,
	marginBottom: 6
}, e.inset && { paddingLeft: 56 })), $r = /*#__PURE__*/ B.forwardRef(function(e, t) {
	let n = Fe({
		props: e,
		name: "MuiListItemText"
	}), { children: r, className: i, disableTypography: a = !1, inset: o = !1, primary: c, primaryTypographyProps: l, secondary: u, secondaryTypographyProps: d } = n, f = Ie(n, Xr), { dense: p } = B.useContext(gt), m = c ?? r, h = u, g = s({}, n, {
		disableTypography: a,
		inset: o,
		primary: !!m,
		secondary: !!h,
		dense: p
	}), _ = Zr(g);
	return m != null && m.type !== or && !a && (m = /*#__PURE__*/ (0, V.jsx)(or, s({
		variant: p ? "body2" : "body1",
		className: _.primary,
		component: l != null && l.variant ? void 0 : "span",
		display: "block"
	}, l, { children: m }))), h != null && h.type !== or && !a && (h = /*#__PURE__*/ (0, V.jsx)(or, s({
		variant: "body2",
		className: _.secondary,
		color: "text.secondary",
		display: "block"
	}, d, { children: h }))), /*#__PURE__*/ (0, V.jsxs)(Qr, s({
		className: Wn(_.root, i),
		ownerState: g,
		ref: t
	}, f, { children: [m, h] }));
});
//#endregion
//#region ../../../resource_engines/node_modules/@mui/material/Switch/switchClasses.js
function ei(e) {
	return rt("MuiSwitch", e);
}
var ti = de("MuiSwitch", [
	"root",
	"edgeStart",
	"edgeEnd",
	"switchBase",
	"colorPrimary",
	"colorSecondary",
	"sizeSmall",
	"sizeMedium",
	"checked",
	"disabled",
	"input",
	"thumb",
	"track"
]);
Gn(), o();
var ni = [
	"className",
	"color",
	"edge",
	"size",
	"sx"
], ri = (e) => {
	let { classes: t, edge: n, size: r, color: i, checked: a, disabled: o } = e, c = {
		root: [
			"root",
			n && `edge${g(n)}`,
			`size${g(r)}`
		],
		switchBase: [
			"switchBase",
			`color${g(i)}`,
			a && "checked",
			o && "disabled"
		],
		thumb: ["thumb"],
		track: ["track"],
		input: ["input"]
	}, l = me(c, ei, t);
	return s({}, t, l);
}, ii = Je("span", {
	name: "MuiSwitch",
	slot: "Root",
	overridesResolver: (e, t) => {
		let { ownerState: n } = e;
		return [
			t.root,
			n.edge && t[`edge${g(n.edge)}`],
			t[`size${g(n.size)}`]
		];
	}
})({
	display: "inline-flex",
	width: 58,
	height: 38,
	overflow: "hidden",
	padding: 12,
	boxSizing: "border-box",
	position: "relative",
	flexShrink: 0,
	zIndex: 0,
	verticalAlign: "middle",
	"@media print": { colorAdjust: "exact" },
	variants: [
		{
			props: { edge: "start" },
			style: { marginLeft: -8 }
		},
		{
			props: { edge: "end" },
			style: { marginRight: -8 }
		},
		{
			props: { size: "small" },
			style: {
				width: 40,
				height: 24,
				padding: 7,
				[`& .${ti.thumb}`]: {
					width: 16,
					height: 16
				},
				[`& .${ti.switchBase}`]: {
					padding: 4,
					[`&.${ti.checked}`]: { transform: "translateX(16px)" }
				}
			}
		}
	]
}), ai = Je(Cr, {
	name: "MuiSwitch",
	slot: "SwitchBase",
	overridesResolver: (e, t) => {
		let { ownerState: n } = e;
		return [
			t.switchBase,
			{ [`& .${ti.input}`]: t.input },
			n.color !== "default" && t[`color${g(n.color)}`]
		];
	}
})(({ theme: e }) => ({
	position: "absolute",
	top: 0,
	left: 0,
	zIndex: 1,
	color: e.vars ? e.vars.palette.Switch.defaultColor : `${e.palette.mode === "light" ? e.palette.common.white : e.palette.grey[300]}`,
	transition: e.transitions.create(["left", "transform"], { duration: e.transitions.duration.shortest }),
	[`&.${ti.checked}`]: { transform: "translateX(20px)" },
	[`&.${ti.disabled}`]: { color: e.vars ? e.vars.palette.Switch.defaultDisabledColor : `${e.palette.mode === "light" ? e.palette.grey[100] : e.palette.grey[600]}` },
	[`&.${ti.checked} + .${ti.track}`]: { opacity: .5 },
	[`&.${ti.disabled} + .${ti.track}`]: { opacity: e.vars ? e.vars.opacity.switchTrackDisabled : `${e.palette.mode === "light" ? .12 : .2}` },
	[`& .${ti.input}`]: {
		left: "-100%",
		width: "300%"
	}
}), ({ theme: e }) => ({
	"&:hover": {
		backgroundColor: e.vars ? `rgba(${e.vars.palette.action.activeChannel} / ${e.vars.palette.action.hoverOpacity})` : (0, fr.alpha)(e.palette.action.active, e.palette.action.hoverOpacity),
		"@media (hover: none)": { backgroundColor: "transparent" }
	},
	variants: [...Object.entries(e.palette).filter(([, e]) => e.main && e.light).map(([t]) => ({
		props: { color: t },
		style: {
			[`&.${ti.checked}`]: {
				color: (e.vars || e).palette[t].main,
				"&:hover": {
					backgroundColor: e.vars ? `rgba(${e.vars.palette[t].mainChannel} / ${e.vars.palette.action.hoverOpacity})` : (0, fr.alpha)(e.palette[t].main, e.palette.action.hoverOpacity),
					"@media (hover: none)": { backgroundColor: "transparent" }
				},
				[`&.${ti.disabled}`]: { color: e.vars ? e.vars.palette.Switch[`${t}DisabledColor`] : `${e.palette.mode === "light" ? (0, fr.lighten)(e.palette[t].main, .62) : (0, fr.darken)(e.palette[t].main, .55)}` }
			},
			[`&.${ti.checked} + .${ti.track}`]: { backgroundColor: (e.vars || e).palette[t].main }
		}
	}))]
})), oi = Je("span", {
	name: "MuiSwitch",
	slot: "Track",
	overridesResolver: (e, t) => t.track
})(({ theme: e }) => ({
	height: "100%",
	width: "100%",
	borderRadius: 7,
	zIndex: -1,
	transition: e.transitions.create(["opacity", "background-color"], { duration: e.transitions.duration.shortest }),
	backgroundColor: e.vars ? e.vars.palette.common.onBackground : `${e.palette.mode === "light" ? e.palette.common.black : e.palette.common.white}`,
	opacity: e.vars ? e.vars.opacity.switchTrack : `${e.palette.mode === "light" ? .38 : .3}`
})), si = Je("span", {
	name: "MuiSwitch",
	slot: "Thumb",
	overridesResolver: (e, t) => t.thumb
})(({ theme: e }) => ({
	boxShadow: (e.vars || e).shadows[1],
	backgroundColor: "currentColor",
	width: 20,
	height: 20,
	borderRadius: "50%"
})), ci = /*#__PURE__*/ B.forwardRef(function(e, t) {
	let n = Fe({
		props: e,
		name: "MuiSwitch"
	}), { className: r, color: i = "primary", edge: a = !1, size: o = "medium", sx: c } = n, l = Ie(n, ni), u = s({}, n, {
		color: i,
		edge: a,
		size: o
	}), d = ri(u), f = /*#__PURE__*/ (0, V.jsx)(si, {
		className: d.thumb,
		ownerState: u
	});
	return /*#__PURE__*/ (0, V.jsxs)(ii, {
		className: Wn(d.root, r),
		sx: c,
		ownerState: u,
		children: [/*#__PURE__*/ (0, V.jsx)(ai, s({
			type: "checkbox",
			icon: f,
			checkedIcon: f,
			ref: t,
			ownerState: u
		}, l, { classes: s({}, d, { root: d.switchBase }) })), /*#__PURE__*/ (0, V.jsx)(oi, {
			className: d.track,
			ownerState: u
		})]
	});
});
T(), h(), Zt();
var H = V.Fragment, U = function(e, t, n) {
	return k.call(t, "css") ? V.jsx(S, We(e, t), n) : V.jsx(e, t, n);
}, W = function(e, t, n) {
	return k.call(t, "css") ? V.jsxs(S, We(e, t), n) : V.jsxs(e, t, n);
}, li = /* @__PURE__ */ t(((e, t) => {
	function n(e, t) {
		for (var n = -1, r = e == null ? 0 : e.length, i = Array(r); ++n < r;) i[n] = t(e[n], n, e);
		return i;
	}
	t.exports = n;
})), ui = /* @__PURE__ */ t(((e, t) => {
	function n() {
		this.__data__ = [], this.size = 0;
	}
	t.exports = n;
})), di = /* @__PURE__ */ t(((e, t) => {
	function n(e, t) {
		return e === t || e !== e && t !== t;
	}
	t.exports = n;
})), fi = /* @__PURE__ */ t(((e, t) => {
	var n = di();
	function r(e, t) {
		for (var r = e.length; r--;) if (n(e[r][0], t)) return r;
		return -1;
	}
	t.exports = r;
})), pi = /* @__PURE__ */ t(((e, t) => {
	var n = fi(), r = Array.prototype.splice;
	function i(e) {
		var t = this.__data__, i = n(t, e);
		return i < 0 ? !1 : (i == t.length - 1 ? t.pop() : r.call(t, i, 1), --this.size, !0);
	}
	t.exports = i;
})), mi = /* @__PURE__ */ t(((e, t) => {
	var n = fi();
	function r(e) {
		var t = this.__data__, r = n(t, e);
		return r < 0 ? void 0 : t[r][1];
	}
	t.exports = r;
})), hi = /* @__PURE__ */ t(((e, t) => {
	var n = fi();
	function r(e) {
		return n(this.__data__, e) > -1;
	}
	t.exports = r;
})), gi = /* @__PURE__ */ t(((e, t) => {
	var n = fi();
	function r(e, t) {
		var r = this.__data__, i = n(r, e);
		return i < 0 ? (++this.size, r.push([e, t])) : r[i][1] = t, this;
	}
	t.exports = r;
})), _i = /* @__PURE__ */ t(((e, t) => {
	var n = ui(), r = pi(), i = mi(), a = hi(), o = gi();
	function s(e) {
		var t = -1, n = e == null ? 0 : e.length;
		for (this.clear(); ++t < n;) {
			var r = e[t];
			this.set(r[0], r[1]);
		}
	}
	s.prototype.clear = n, s.prototype.delete = r, s.prototype.get = i, s.prototype.has = a, s.prototype.set = o, t.exports = s;
})), vi = /* @__PURE__ */ t(((e, t) => {
	var n = _i();
	function r() {
		this.__data__ = new n(), this.size = 0;
	}
	t.exports = r;
})), yi = /* @__PURE__ */ t(((e, t) => {
	function n(e) {
		var t = this.__data__, n = t.delete(e);
		return this.size = t.size, n;
	}
	t.exports = n;
})), bi = /* @__PURE__ */ t(((e, t) => {
	function n(e) {
		return this.__data__.get(e);
	}
	t.exports = n;
})), xi = /* @__PURE__ */ t(((e, t) => {
	function n(e) {
		return this.__data__.has(e);
	}
	t.exports = n;
})), Si = /* @__PURE__ */ t(((e, t) => {
	t.exports = typeof global == "object" && global && global.Object === Object && global;
})), Ci = /* @__PURE__ */ t(((e, t) => {
	var n = Si(), r = typeof self == "object" && self && self.Object === Object && self;
	t.exports = n || r || Function("return this")();
})), wi = /* @__PURE__ */ t(((e, t) => {
	t.exports = Ci().Symbol;
})), Ti = /* @__PURE__ */ t(((e, t) => {
	var n = wi(), r = Object.prototype, i = r.hasOwnProperty, a = r.toString, o = n ? n.toStringTag : void 0;
	function s(e) {
		var t = i.call(e, o), n = e[o];
		try {
			e[o] = void 0;
			var r = !0;
		} catch {}
		var s = a.call(e);
		return r && (t ? e[o] = n : delete e[o]), s;
	}
	t.exports = s;
})), Ei = /* @__PURE__ */ t(((e, t) => {
	var n = Object.prototype.toString;
	function r(e) {
		return n.call(e);
	}
	t.exports = r;
})), Di = /* @__PURE__ */ t(((e, t) => {
	var n = wi(), r = Ti(), i = Ei(), a = "[object Null]", o = "[object Undefined]", s = n ? n.toStringTag : void 0;
	function c(e) {
		return e == null ? e === void 0 ? o : a : s && s in Object(e) ? r(e) : i(e);
	}
	t.exports = c;
})), Oi = /* @__PURE__ */ t(((e, t) => {
	function n(e) {
		var t = typeof e;
		return e != null && (t == "object" || t == "function");
	}
	t.exports = n;
})), ki = /* @__PURE__ */ t(((e, t) => {
	var n = Di(), r = Oi(), i = "[object AsyncFunction]", a = "[object Function]", o = "[object GeneratorFunction]", s = "[object Proxy]";
	function c(e) {
		if (!r(e)) return !1;
		var t = n(e);
		return t == a || t == o || t == i || t == s;
	}
	t.exports = c;
})), Ai = /* @__PURE__ */ t(((e, t) => {
	t.exports = Ci()["__core-js_shared__"];
})), ji = /* @__PURE__ */ t(((e, t) => {
	var n = Ai(), r = function() {
		var e = /[^.]+$/.exec(n && n.keys && n.keys.IE_PROTO || "");
		return e ? "Symbol(src)_1." + e : "";
	}();
	function i(e) {
		return !!r && r in e;
	}
	t.exports = i;
})), Mi = /* @__PURE__ */ t(((e, t) => {
	var n = Function.prototype.toString;
	function r(e) {
		if (e != null) {
			try {
				return n.call(e);
			} catch {}
			try {
				return e + "";
			} catch {}
		}
		return "";
	}
	t.exports = r;
})), Ni = /* @__PURE__ */ t(((e, t) => {
	var n = ki(), r = ji(), i = Oi(), a = Mi(), o = /[\\^$.*+?()[\]{}|]/g, s = /^\[object .+?Constructor\]$/, c = Function.prototype, l = Object.prototype, u = c.toString, d = l.hasOwnProperty, f = RegExp("^" + u.call(d).replace(o, "\\$&").replace(/hasOwnProperty|(function).*?(?=\\\()| for .+?(?=\\\])/g, "$1.*?") + "$");
	function p(e) {
		return !i(e) || r(e) ? !1 : (n(e) ? f : s).test(a(e));
	}
	t.exports = p;
})), Pi = /* @__PURE__ */ t(((e, t) => {
	function n(e, t) {
		return e?.[t];
	}
	t.exports = n;
})), Fi = /* @__PURE__ */ t(((e, t) => {
	var n = Ni(), r = Pi();
	function i(e, t) {
		var i = r(e, t);
		return n(i) ? i : void 0;
	}
	t.exports = i;
})), Ii = /* @__PURE__ */ t(((e, t) => {
	t.exports = Fi()(Ci(), "Map");
})), Li = /* @__PURE__ */ t(((e, t) => {
	t.exports = Fi()(Object, "create");
})), Ri = /* @__PURE__ */ t(((e, t) => {
	var n = Li();
	function r() {
		this.__data__ = n ? n(null) : {}, this.size = 0;
	}
	t.exports = r;
})), zi = /* @__PURE__ */ t(((e, t) => {
	function n(e) {
		var t = this.has(e) && delete this.__data__[e];
		return this.size -= +!!t, t;
	}
	t.exports = n;
})), Bi = /* @__PURE__ */ t(((e, t) => {
	var n = Li(), r = "__lodash_hash_undefined__", i = Object.prototype.hasOwnProperty;
	function a(e) {
		var t = this.__data__;
		if (n) {
			var a = t[e];
			return a === r ? void 0 : a;
		}
		return i.call(t, e) ? t[e] : void 0;
	}
	t.exports = a;
})), Vi = /* @__PURE__ */ t(((e, t) => {
	var n = Li(), r = Object.prototype.hasOwnProperty;
	function i(e) {
		var t = this.__data__;
		return n ? t[e] !== void 0 : r.call(t, e);
	}
	t.exports = i;
})), Hi = /* @__PURE__ */ t(((e, t) => {
	var n = Li(), r = "__lodash_hash_undefined__";
	function i(e, t) {
		var i = this.__data__;
		return this.size += +!this.has(e), i[e] = n && t === void 0 ? r : t, this;
	}
	t.exports = i;
})), Ui = /* @__PURE__ */ t(((e, t) => {
	var n = Ri(), r = zi(), i = Bi(), a = Vi(), o = Hi();
	function s(e) {
		var t = -1, n = e == null ? 0 : e.length;
		for (this.clear(); ++t < n;) {
			var r = e[t];
			this.set(r[0], r[1]);
		}
	}
	s.prototype.clear = n, s.prototype.delete = r, s.prototype.get = i, s.prototype.has = a, s.prototype.set = o, t.exports = s;
})), Wi = /* @__PURE__ */ t(((e, t) => {
	var n = Ui(), r = _i(), i = Ii();
	function a() {
		this.size = 0, this.__data__ = {
			hash: new n(),
			map: new (i || r)(),
			string: new n()
		};
	}
	t.exports = a;
})), Gi = /* @__PURE__ */ t(((e, t) => {
	function n(e) {
		var t = typeof e;
		return t == "string" || t == "number" || t == "symbol" || t == "boolean" ? e !== "__proto__" : e === null;
	}
	t.exports = n;
})), Ki = /* @__PURE__ */ t(((e, t) => {
	var n = Gi();
	function r(e, t) {
		var r = e.__data__;
		return n(t) ? r[typeof t == "string" ? "string" : "hash"] : r.map;
	}
	t.exports = r;
})), qi = /* @__PURE__ */ t(((e, t) => {
	var n = Ki();
	function r(e) {
		var t = n(this, e).delete(e);
		return this.size -= +!!t, t;
	}
	t.exports = r;
})), Ji = /* @__PURE__ */ t(((e, t) => {
	var n = Ki();
	function r(e) {
		return n(this, e).get(e);
	}
	t.exports = r;
})), Yi = /* @__PURE__ */ t(((e, t) => {
	var n = Ki();
	function r(e) {
		return n(this, e).has(e);
	}
	t.exports = r;
})), Xi = /* @__PURE__ */ t(((e, t) => {
	var n = Ki();
	function r(e, t) {
		var r = n(this, e), i = r.size;
		return r.set(e, t), this.size += r.size == i ? 0 : 1, this;
	}
	t.exports = r;
})), Zi = /* @__PURE__ */ t(((e, t) => {
	var n = Wi(), r = qi(), i = Ji(), a = Yi(), o = Xi();
	function s(e) {
		var t = -1, n = e == null ? 0 : e.length;
		for (this.clear(); ++t < n;) {
			var r = e[t];
			this.set(r[0], r[1]);
		}
	}
	s.prototype.clear = n, s.prototype.delete = r, s.prototype.get = i, s.prototype.has = a, s.prototype.set = o, t.exports = s;
})), Qi = /* @__PURE__ */ t(((e, t) => {
	var n = _i(), r = Ii(), i = Zi(), a = 200;
	function o(e, t) {
		var o = this.__data__;
		if (o instanceof n) {
			var s = o.__data__;
			if (!r || s.length < a - 1) return s.push([e, t]), this.size = ++o.size, this;
			o = this.__data__ = new i(s);
		}
		return o.set(e, t), this.size = o.size, this;
	}
	t.exports = o;
})), $i = /* @__PURE__ */ t(((e, t) => {
	var n = _i(), r = vi(), i = yi(), a = bi(), o = xi(), s = Qi();
	function c(e) {
		var t = this.__data__ = new n(e);
		this.size = t.size;
	}
	c.prototype.clear = r, c.prototype.delete = i, c.prototype.get = a, c.prototype.has = o, c.prototype.set = s, t.exports = c;
})), ea = /* @__PURE__ */ t(((e, t) => {
	function n(e, t) {
		for (var n = -1, r = e == null ? 0 : e.length; ++n < r && t(e[n], n, e) !== !1;);
		return e;
	}
	t.exports = n;
})), ta = /* @__PURE__ */ t(((e, t) => {
	var n = Fi();
	t.exports = function() {
		try {
			var e = n(Object, "defineProperty");
			return e({}, "", {}), e;
		} catch {}
	}();
})), na = /* @__PURE__ */ t(((e, t) => {
	var n = ta();
	function r(e, t, r) {
		t == "__proto__" && n ? n(e, t, {
			configurable: !0,
			enumerable: !0,
			value: r,
			writable: !0
		}) : e[t] = r;
	}
	t.exports = r;
})), ra = /* @__PURE__ */ t(((e, t) => {
	var n = na(), r = di(), i = Object.prototype.hasOwnProperty;
	function a(e, t, a) {
		var o = e[t];
		(!(i.call(e, t) && r(o, a)) || a === void 0 && !(t in e)) && n(e, t, a);
	}
	t.exports = a;
})), ia = /* @__PURE__ */ t(((e, t) => {
	var n = ra(), r = na();
	function i(e, t, i, a) {
		var o = !i;
		i ||= {};
		for (var s = -1, c = t.length; ++s < c;) {
			var l = t[s], u = a ? a(i[l], e[l], l, i, e) : void 0;
			u === void 0 && (u = e[l]), o ? r(i, l, u) : n(i, l, u);
		}
		return i;
	}
	t.exports = i;
})), aa = /* @__PURE__ */ t(((e, t) => {
	function n(e, t) {
		for (var n = -1, r = Array(e); ++n < e;) r[n] = t(n);
		return r;
	}
	t.exports = n;
})), oa = /* @__PURE__ */ t(((e, t) => {
	function n(e) {
		return typeof e == "object" && !!e;
	}
	t.exports = n;
})), sa = /* @__PURE__ */ t(((e, t) => {
	var n = Di(), r = oa(), i = "[object Arguments]";
	function a(e) {
		return r(e) && n(e) == i;
	}
	t.exports = a;
})), ca = /* @__PURE__ */ t(((e, t) => {
	var n = sa(), r = oa(), i = Object.prototype, a = i.hasOwnProperty, o = i.propertyIsEnumerable;
	t.exports = n(function() {
		return arguments;
	}()) ? n : function(e) {
		return r(e) && a.call(e, "callee") && !o.call(e, "callee");
	};
})), la = /* @__PURE__ */ t(((e, t) => {
	t.exports = Array.isArray;
})), ua = /* @__PURE__ */ t(((e, t) => {
	function n() {
		return !1;
	}
	t.exports = n;
})), da = /* @__PURE__ */ t(((e, t) => {
	var n = Ci(), r = ua(), i = typeof e == "object" && e && !e.nodeType && e, a = i && typeof t == "object" && t && !t.nodeType && t, o = a && a.exports === i ? n.Buffer : void 0;
	t.exports = (o ? o.isBuffer : void 0) || r;
})), fa = /* @__PURE__ */ t(((e, t) => {
	var n = /^(?:0|[1-9]\d*)$/;
	function r(e, t) {
		var r = typeof e;
		return t ??= 9007199254740991, !!t && (r == "number" || r != "symbol" && n.test(e)) && e > -1 && e % 1 == 0 && e < t;
	}
	t.exports = r;
})), pa = /* @__PURE__ */ t(((e, t) => {
	function n(e) {
		return typeof e == "number" && e > -1 && e % 1 == 0 && e <= 9007199254740991;
	}
	t.exports = n;
})), ma = /* @__PURE__ */ t(((e, t) => {
	var n = Di(), r = pa(), i = oa(), a = "[object Arguments]", o = "[object Array]", s = "[object Boolean]", c = "[object Date]", l = "[object Error]", u = "[object Function]", d = "[object Map]", f = "[object Number]", p = "[object Object]", m = "[object RegExp]", h = "[object Set]", g = "[object String]", _ = "[object WeakMap]", v = "[object ArrayBuffer]", y = "[object DataView]", b = "[object Float32Array]", x = "[object Float64Array]", S = "[object Int8Array]", C = "[object Int16Array]", w = "[object Int32Array]", T = "[object Uint8Array]", E = "[object Uint8ClampedArray]", D = "[object Uint16Array]", O = "[object Uint32Array]", k = {};
	k[b] = k[x] = k[S] = k[C] = k[w] = k[T] = k[E] = k[D] = k[O] = !0, k[a] = k[o] = k[v] = k[s] = k[y] = k[c] = k[l] = k[u] = k[d] = k[f] = k[p] = k[m] = k[h] = k[g] = k[_] = !1;
	function A(e) {
		return i(e) && r(e.length) && !!k[n(e)];
	}
	t.exports = A;
})), ha = /* @__PURE__ */ t(((e, t) => {
	function n(e) {
		return function(t) {
			return e(t);
		};
	}
	t.exports = n;
})), ga = /* @__PURE__ */ t(((e, t) => {
	var n = Si(), r = typeof e == "object" && e && !e.nodeType && e, i = r && typeof t == "object" && t && !t.nodeType && t, a = i && i.exports === r && n.process;
	t.exports = function() {
		try {
			return i && i.require && i.require("util").types || a && a.binding && a.binding("util");
		} catch {}
	}();
})), _a = /* @__PURE__ */ t(((e, t) => {
	var n = ma(), r = ha(), i = ga(), a = i && i.isTypedArray;
	t.exports = a ? r(a) : n;
})), va = /* @__PURE__ */ t(((e, t) => {
	var n = aa(), r = ca(), i = la(), a = da(), o = fa(), s = _a(), c = Object.prototype.hasOwnProperty;
	function l(e, t) {
		var l = i(e), u = !l && r(e), d = !l && !u && a(e), f = !l && !u && !d && s(e), p = l || u || d || f, m = p ? n(e.length, String) : [], h = m.length;
		for (var g in e) (t || c.call(e, g)) && !(p && (g == "length" || d && (g == "offset" || g == "parent") || f && (g == "buffer" || g == "byteLength" || g == "byteOffset") || o(g, h))) && m.push(g);
		return m;
	}
	t.exports = l;
})), ya = /* @__PURE__ */ t(((e, t) => {
	var n = Object.prototype;
	function r(e) {
		var t = e && e.constructor;
		return e === (typeof t == "function" && t.prototype || n);
	}
	t.exports = r;
})), ba = /* @__PURE__ */ t(((e, t) => {
	function n(e, t) {
		return function(n) {
			return e(t(n));
		};
	}
	t.exports = n;
})), xa = /* @__PURE__ */ t(((e, t) => {
	t.exports = ba()(Object.keys, Object);
})), Sa = /* @__PURE__ */ t(((e, t) => {
	var n = ya(), r = xa(), i = Object.prototype.hasOwnProperty;
	function a(e) {
		if (!n(e)) return r(e);
		var t = [];
		for (var a in Object(e)) i.call(e, a) && a != "constructor" && t.push(a);
		return t;
	}
	t.exports = a;
})), Ca = /* @__PURE__ */ t(((e, t) => {
	var n = ki(), r = pa();
	function i(e) {
		return e != null && r(e.length) && !n(e);
	}
	t.exports = i;
})), wa = /* @__PURE__ */ t(((e, t) => {
	var n = va(), r = Sa(), i = Ca();
	function a(e) {
		return i(e) ? n(e) : r(e);
	}
	t.exports = a;
})), Ta = /* @__PURE__ */ t(((e, t) => {
	var n = ia(), r = wa();
	function i(e, t) {
		return e && n(t, r(t), e);
	}
	t.exports = i;
})), Ea = /* @__PURE__ */ t(((e, t) => {
	function n(e) {
		var t = [];
		if (e != null) for (var n in Object(e)) t.push(n);
		return t;
	}
	t.exports = n;
})), Da = /* @__PURE__ */ t(((e, t) => {
	var n = Oi(), r = ya(), i = Ea(), a = Object.prototype.hasOwnProperty;
	function o(e) {
		if (!n(e)) return i(e);
		var t = r(e), o = [];
		for (var s in e) (s != "constructor" || !t && a.call(e, s)) && o.push(s);
		return o;
	}
	t.exports = o;
})), Oa = /* @__PURE__ */ t(((e, t) => {
	var n = va(), r = Da(), i = Ca();
	function a(e) {
		return i(e) ? n(e, !0) : r(e);
	}
	t.exports = a;
})), ka = /* @__PURE__ */ t(((e, t) => {
	var n = ia(), r = Oa();
	function i(e, t) {
		return e && n(t, r(t), e);
	}
	t.exports = i;
})), Aa = /* @__PURE__ */ t(((e, t) => {
	var n = Ci(), r = typeof e == "object" && e && !e.nodeType && e, i = r && typeof t == "object" && t && !t.nodeType && t, a = i && i.exports === r ? n.Buffer : void 0, o = a ? a.allocUnsafe : void 0;
	function s(e, t) {
		if (t) return e.slice();
		var n = e.length, r = o ? o(n) : new e.constructor(n);
		return e.copy(r), r;
	}
	t.exports = s;
})), ja = /* @__PURE__ */ t(((e, t) => {
	function n(e, t) {
		var n = -1, r = e.length;
		for (t ||= Array(r); ++n < r;) t[n] = e[n];
		return t;
	}
	t.exports = n;
})), Ma = /* @__PURE__ */ t(((e, t) => {
	function n(e, t) {
		for (var n = -1, r = e == null ? 0 : e.length, i = 0, a = []; ++n < r;) {
			var o = e[n];
			t(o, n, e) && (a[i++] = o);
		}
		return a;
	}
	t.exports = n;
})), Na = /* @__PURE__ */ t(((e, t) => {
	function n() {
		return [];
	}
	t.exports = n;
})), Pa = /* @__PURE__ */ t(((e, t) => {
	var n = Ma(), r = Na(), i = Object.prototype.propertyIsEnumerable, a = Object.getOwnPropertySymbols;
	t.exports = a ? function(e) {
		return e == null ? [] : (e = Object(e), n(a(e), function(t) {
			return i.call(e, t);
		}));
	} : r;
})), Fa = /* @__PURE__ */ t(((e, t) => {
	var n = ia(), r = Pa();
	function i(e, t) {
		return n(e, r(e), t);
	}
	t.exports = i;
})), Ia = /* @__PURE__ */ t(((e, t) => {
	function n(e, t) {
		for (var n = -1, r = t.length, i = e.length; ++n < r;) e[i + n] = t[n];
		return e;
	}
	t.exports = n;
})), La = /* @__PURE__ */ t(((e, t) => {
	t.exports = ba()(Object.getPrototypeOf, Object);
})), Ra = /* @__PURE__ */ t(((e, t) => {
	var n = Ia(), r = La(), i = Pa(), a = Na();
	t.exports = Object.getOwnPropertySymbols ? function(e) {
		for (var t = []; e;) n(t, i(e)), e = r(e);
		return t;
	} : a;
})), za = /* @__PURE__ */ t(((e, t) => {
	var n = ia(), r = Ra();
	function i(e, t) {
		return n(e, r(e), t);
	}
	t.exports = i;
})), Ba = /* @__PURE__ */ t(((e, t) => {
	var n = Ia(), r = la();
	function i(e, t, i) {
		var a = t(e);
		return r(e) ? a : n(a, i(e));
	}
	t.exports = i;
})), Va = /* @__PURE__ */ t(((e, t) => {
	var n = Ba(), r = Pa(), i = wa();
	function a(e) {
		return n(e, i, r);
	}
	t.exports = a;
})), Ha = /* @__PURE__ */ t(((e, t) => {
	var n = Ba(), r = Ra(), i = Oa();
	function a(e) {
		return n(e, i, r);
	}
	t.exports = a;
})), Ua = /* @__PURE__ */ t(((e, t) => {
	t.exports = Fi()(Ci(), "DataView");
})), Wa = /* @__PURE__ */ t(((e, t) => {
	t.exports = Fi()(Ci(), "Promise");
})), Ga = /* @__PURE__ */ t(((e, t) => {
	t.exports = Fi()(Ci(), "Set");
})), Ka = /* @__PURE__ */ t(((e, t) => {
	t.exports = Fi()(Ci(), "WeakMap");
})), qa = /* @__PURE__ */ t(((e, t) => {
	var n = Ua(), r = Ii(), i = Wa(), a = Ga(), o = Ka(), s = Di(), c = Mi(), l = "[object Map]", u = "[object Object]", d = "[object Promise]", f = "[object Set]", p = "[object WeakMap]", m = "[object DataView]", h = c(n), g = c(r), _ = c(i), v = c(a), y = c(o), b = s;
	(n && b(new n(/* @__PURE__ */ new ArrayBuffer(1))) != m || r && b(new r()) != l || i && b(i.resolve()) != d || a && b(new a()) != f || o && b(new o()) != p) && (b = function(e) {
		var t = s(e), n = t == u ? e.constructor : void 0, r = n ? c(n) : "";
		if (r) switch (r) {
			case h: return m;
			case g: return l;
			case _: return d;
			case v: return f;
			case y: return p;
		}
		return t;
	}), t.exports = b;
})), Ja = /* @__PURE__ */ t(((e, t) => {
	var n = Object.prototype.hasOwnProperty;
	function r(e) {
		var t = e.length, r = new e.constructor(t);
		return t && typeof e[0] == "string" && n.call(e, "index") && (r.index = e.index, r.input = e.input), r;
	}
	t.exports = r;
})), Ya = /* @__PURE__ */ t(((e, t) => {
	t.exports = Ci().Uint8Array;
})), Xa = /* @__PURE__ */ t(((e, t) => {
	var n = Ya();
	function r(e) {
		var t = new e.constructor(e.byteLength);
		return new n(t).set(new n(e)), t;
	}
	t.exports = r;
})), Za = /* @__PURE__ */ t(((e, t) => {
	var n = Xa();
	function r(e, t) {
		var r = t ? n(e.buffer) : e.buffer;
		return new e.constructor(r, e.byteOffset, e.byteLength);
	}
	t.exports = r;
})), Qa = /* @__PURE__ */ t(((e, t) => {
	var n = /\w*$/;
	function r(e) {
		var t = new e.constructor(e.source, n.exec(e));
		return t.lastIndex = e.lastIndex, t;
	}
	t.exports = r;
})), $a = /* @__PURE__ */ t(((e, t) => {
	var n = wi(), r = n ? n.prototype : void 0, i = r ? r.valueOf : void 0;
	function a(e) {
		return i ? Object(i.call(e)) : {};
	}
	t.exports = a;
})), eo = /* @__PURE__ */ t(((e, t) => {
	var n = Xa();
	function r(e, t) {
		var r = t ? n(e.buffer) : e.buffer;
		return new e.constructor(r, e.byteOffset, e.length);
	}
	t.exports = r;
})), to = /* @__PURE__ */ t(((e, t) => {
	var n = Xa(), r = Za(), i = Qa(), a = $a(), o = eo(), s = "[object Boolean]", c = "[object Date]", l = "[object Map]", u = "[object Number]", d = "[object RegExp]", f = "[object Set]", p = "[object String]", m = "[object Symbol]", h = "[object ArrayBuffer]", g = "[object DataView]", _ = "[object Float32Array]", v = "[object Float64Array]", y = "[object Int8Array]", b = "[object Int16Array]", x = "[object Int32Array]", S = "[object Uint8Array]", C = "[object Uint8ClampedArray]", w = "[object Uint16Array]", T = "[object Uint32Array]";
	function E(e, t, E) {
		var D = e.constructor;
		switch (t) {
			case h: return n(e);
			case s:
			case c: return new D(+e);
			case g: return r(e, E);
			case _:
			case v:
			case y:
			case b:
			case x:
			case S:
			case C:
			case w:
			case T: return o(e, E);
			case l: return new D();
			case u:
			case p: return new D(e);
			case d: return i(e);
			case f: return new D();
			case m: return a(e);
		}
	}
	t.exports = E;
})), no = /* @__PURE__ */ t(((e, t) => {
	var n = Oi(), r = Object.create;
	t.exports = function() {
		function e() {}
		return function(t) {
			if (!n(t)) return {};
			if (r) return r(t);
			e.prototype = t;
			var i = new e();
			return e.prototype = void 0, i;
		};
	}();
})), ro = /* @__PURE__ */ t(((e, t) => {
	var n = no(), r = La(), i = ya();
	function a(e) {
		return typeof e.constructor == "function" && !i(e) ? n(r(e)) : {};
	}
	t.exports = a;
})), io = /* @__PURE__ */ t(((e, t) => {
	var n = qa(), r = oa(), i = "[object Map]";
	function a(e) {
		return r(e) && n(e) == i;
	}
	t.exports = a;
})), ao = /* @__PURE__ */ t(((e, t) => {
	var n = io(), r = ha(), i = ga(), a = i && i.isMap;
	t.exports = a ? r(a) : n;
})), oo = /* @__PURE__ */ t(((e, t) => {
	var n = qa(), r = oa(), i = "[object Set]";
	function a(e) {
		return r(e) && n(e) == i;
	}
	t.exports = a;
})), so = /* @__PURE__ */ t(((e, t) => {
	var n = oo(), r = ha(), i = ga(), a = i && i.isSet;
	t.exports = a ? r(a) : n;
})), co = /* @__PURE__ */ t(((e, t) => {
	var n = $i(), r = ea(), i = ra(), a = Ta(), o = ka(), s = Aa(), c = ja(), l = Fa(), u = za(), d = Va(), f = Ha(), p = qa(), m = Ja(), h = to(), g = ro(), _ = la(), v = da(), y = ao(), b = Oi(), x = so(), S = wa(), C = Oa(), w = 1, T = 2, E = 4, D = "[object Arguments]", O = "[object Array]", k = "[object Boolean]", A = "[object Date]", j = "[object Error]", ee = "[object Function]", te = "[object GeneratorFunction]", M = "[object Map]", ne = "[object Number]", re = "[object Object]", N = "[object RegExp]", ie = "[object Set]", ae = "[object String]", P = "[object Symbol]", oe = "[object WeakMap]", se = "[object ArrayBuffer]", ce = "[object DataView]", le = "[object Float32Array]", ue = "[object Float64Array]", de = "[object Int8Array]", fe = "[object Int16Array]", pe = "[object Int32Array]", me = "[object Uint8Array]", he = "[object Uint8ClampedArray]", ge = "[object Uint16Array]", _e = "[object Uint32Array]", F = {};
	F[D] = F[O] = F[se] = F[ce] = F[k] = F[A] = F[le] = F[ue] = F[de] = F[fe] = F[pe] = F[M] = F[ne] = F[re] = F[N] = F[ie] = F[ae] = F[P] = F[me] = F[he] = F[ge] = F[_e] = !0, F[j] = F[ee] = F[oe] = !1;
	function ve(e, t, O, k, A, j) {
		var M, ne = t & w, N = t & T, ie = t & E;
		if (O && (M = A ? O(e, k, A, j) : O(e)), M !== void 0) return M;
		if (!b(e)) return e;
		var ae = _(e);
		if (ae) {
			if (M = m(e), !ne) return c(e, M);
		} else {
			var P = p(e), oe = P == ee || P == te;
			if (v(e)) return s(e, ne);
			if (P == re || P == D || oe && !A) {
				if (M = N || oe ? {} : g(e), !ne) return N ? u(e, o(M, e)) : l(e, a(M, e));
			} else {
				if (!F[P]) return A ? e : {};
				M = h(e, P, ne);
			}
		}
		j ||= new n();
		var se = j.get(e);
		if (se) return se;
		j.set(e, M), x(e) ? e.forEach(function(n) {
			M.add(ve(n, t, O, n, e, j));
		}) : y(e) && e.forEach(function(n, r) {
			M.set(r, ve(n, t, O, r, e, j));
		});
		var ce = ae ? void 0 : (ie ? N ? f : d : N ? C : S)(e);
		return r(ce || e, function(n, r) {
			ce && (r = n, n = e[r]), i(M, r, ve(n, t, O, r, e, j));
		}), M;
	}
	t.exports = ve;
})), lo = /* @__PURE__ */ t(((e, t) => {
	var n = Di(), r = oa(), i = "[object Symbol]";
	function a(e) {
		return typeof e == "symbol" || r(e) && n(e) == i;
	}
	t.exports = a;
})), uo = /* @__PURE__ */ t(((e, t) => {
	var n = la(), r = lo(), i = /\.|\[(?:[^[\]]*|(["'])(?:(?!\1)[^\\]|\\.)*?\1)\]/, a = /^\w*$/;
	function o(e, t) {
		if (n(e)) return !1;
		var o = typeof e;
		return o == "number" || o == "symbol" || o == "boolean" || e == null || r(e) ? !0 : a.test(e) || !i.test(e) || t != null && e in Object(t);
	}
	t.exports = o;
})), fo = /* @__PURE__ */ t(((e, t) => {
	var n = Zi(), r = "Expected a function";
	function i(e, t) {
		if (typeof e != "function" || t != null && typeof t != "function") throw TypeError(r);
		var a = function() {
			var n = arguments, r = t ? t.apply(this, n) : n[0], i = a.cache;
			if (i.has(r)) return i.get(r);
			var o = e.apply(this, n);
			return a.cache = i.set(r, o) || i, o;
		};
		return a.cache = new (i.Cache || n)(), a;
	}
	i.Cache = n, t.exports = i;
})), po = /* @__PURE__ */ t(((e, t) => {
	var n = fo(), r = 500;
	function i(e) {
		var t = n(e, function(e) {
			return i.size === r && i.clear(), e;
		}), i = t.cache;
		return t;
	}
	t.exports = i;
})), mo = /* @__PURE__ */ t(((e, t) => {
	var n = po(), r = /[^.[\]]+|\[(?:(-?\d+(?:\.\d+)?)|(["'])((?:(?!\2)[^\\]|\\.)*?)\2)\]|(?=(?:\.|\[\])(?:\.|\[\]|$))/g, i = /\\(\\)?/g;
	t.exports = n(function(e) {
		var t = [];
		return e.charCodeAt(0) === 46 && t.push(""), e.replace(r, function(e, n, r, a) {
			t.push(r ? a.replace(i, "$1") : n || e);
		}), t;
	});
})), ho = /* @__PURE__ */ t(((e, t) => {
	var n = wi(), r = li(), i = la(), a = lo(), o = 1 / 0, s = n ? n.prototype : void 0, c = s ? s.toString : void 0;
	function l(e) {
		if (typeof e == "string") return e;
		if (i(e)) return r(e, l) + "";
		if (a(e)) return c ? c.call(e) : "";
		var t = e + "";
		return t == "0" && 1 / e == -o ? "-0" : t;
	}
	t.exports = l;
})), go = /* @__PURE__ */ t(((e, t) => {
	var n = ho();
	function r(e) {
		return e == null ? "" : n(e);
	}
	t.exports = r;
})), _o = /* @__PURE__ */ t(((e, t) => {
	var n = la(), r = uo(), i = mo(), a = go();
	function o(e, t) {
		return n(e) ? e : r(e, t) ? [e] : i(a(e));
	}
	t.exports = o;
})), vo = /* @__PURE__ */ t(((e, t) => {
	function n(e) {
		var t = e == null ? 0 : e.length;
		return t ? e[t - 1] : void 0;
	}
	t.exports = n;
})), yo = /* @__PURE__ */ t(((e, t) => {
	var n = lo(), r = 1 / 0;
	function i(e) {
		if (typeof e == "string" || n(e)) return e;
		var t = e + "";
		return t == "0" && 1 / e == -r ? "-0" : t;
	}
	t.exports = i;
})), bo = /* @__PURE__ */ t(((e, t) => {
	var n = _o(), r = yo();
	function i(e, t) {
		t = n(t, e);
		for (var i = 0, a = t.length; e != null && i < a;) e = e[r(t[i++])];
		return i && i == a ? e : void 0;
	}
	t.exports = i;
})), xo = /* @__PURE__ */ t(((e, t) => {
	function n(e, t, n) {
		var r = -1, i = e.length;
		t < 0 && (t = -t > i ? 0 : i + t), n = n > i ? i : n, n < 0 && (n += i), i = t > n ? 0 : n - t >>> 0, t >>>= 0;
		for (var a = Array(i); ++r < i;) a[r] = e[r + t];
		return a;
	}
	t.exports = n;
})), So = /* @__PURE__ */ t(((e, t) => {
	var n = bo(), r = xo();
	function i(e, t) {
		return t.length < 2 ? e : n(e, r(t, 0, -1));
	}
	t.exports = i;
})), Co = /* @__PURE__ */ t(((e, t) => {
	var n = _o(), r = vo(), i = So(), a = yo(), o = Object.prototype.hasOwnProperty;
	function s(e, t) {
		t = n(t, e);
		var s = -1, c = t.length;
		if (!c) return !0;
		for (; ++s < c;) {
			var l = a(t[s]);
			if (l === "__proto__" && !o.call(e, "__proto__") || (l === "constructor" || l === "prototype") && s < c - 1) return !1;
		}
		var u = i(e, t);
		return u == null || delete u[a(r(t))];
	}
	t.exports = s;
})), wo = /* @__PURE__ */ t(((e, t) => {
	var n = Di(), r = La(), i = oa(), a = "[object Object]", o = Function.prototype, s = Object.prototype, c = o.toString, l = s.hasOwnProperty, u = c.call(Object);
	function d(e) {
		if (!i(e) || n(e) != a) return !1;
		var t = r(e);
		if (t === null) return !0;
		var o = l.call(t, "constructor") && t.constructor;
		return typeof o == "function" && o instanceof o && c.call(o) == u;
	}
	t.exports = d;
})), To = /* @__PURE__ */ t(((e, t) => {
	var n = wo();
	function r(e) {
		return n(e) ? void 0 : e;
	}
	t.exports = r;
})), Eo = /* @__PURE__ */ t(((e, t) => {
	var n = wi(), r = ca(), i = la(), a = n ? n.isConcatSpreadable : void 0;
	function o(e) {
		return i(e) || r(e) || !!(a && e && e[a]);
	}
	t.exports = o;
})), Do = /* @__PURE__ */ t(((e, t) => {
	var n = Ia(), r = Eo();
	function i(e, t, a, o, s) {
		var c = -1, l = e.length;
		for (a ||= r, s ||= []; ++c < l;) {
			var u = e[c];
			t > 0 && a(u) ? t > 1 ? i(u, t - 1, a, o, s) : n(s, u) : o || (s[s.length] = u);
		}
		return s;
	}
	t.exports = i;
})), Oo = /* @__PURE__ */ t(((e, t) => {
	var n = Do();
	function r(e) {
		return e != null && e.length ? n(e, 1) : [];
	}
	t.exports = r;
})), ko = /* @__PURE__ */ t(((e, t) => {
	function n(e, t, n) {
		switch (n.length) {
			case 0: return e.call(t);
			case 1: return e.call(t, n[0]);
			case 2: return e.call(t, n[0], n[1]);
			case 3: return e.call(t, n[0], n[1], n[2]);
		}
		return e.apply(t, n);
	}
	t.exports = n;
})), Ao = /* @__PURE__ */ t(((e, t) => {
	var n = ko(), r = Math.max;
	function i(e, t, i) {
		return t = r(t === void 0 ? e.length - 1 : t, 0), function() {
			for (var a = arguments, o = -1, s = r(a.length - t, 0), c = Array(s); ++o < s;) c[o] = a[t + o];
			o = -1;
			for (var l = Array(t + 1); ++o < t;) l[o] = a[o];
			return l[t] = i(c), n(e, this, l);
		};
	}
	t.exports = i;
})), jo = /* @__PURE__ */ t(((e, t) => {
	function n(e) {
		return function() {
			return e;
		};
	}
	t.exports = n;
})), Mo = /* @__PURE__ */ t(((e, t) => {
	function n(e) {
		return e;
	}
	t.exports = n;
})), No = /* @__PURE__ */ t(((e, t) => {
	var n = jo(), r = ta(), i = Mo();
	t.exports = r ? function(e, t) {
		return r(e, "toString", {
			configurable: !0,
			enumerable: !1,
			value: n(t),
			writable: !0
		});
	} : i;
})), Po = /* @__PURE__ */ t(((e, t) => {
	var n = Date.now;
	function r(e) {
		var t = 0, r = 0;
		return function() {
			var i = n(), a = 16 - (i - r);
			if (r = i, a > 0) {
				if (++t >= 800) return arguments[0];
			} else t = 0;
			return e.apply(void 0, arguments);
		};
	}
	t.exports = r;
})), Fo = /* @__PURE__ */ t(((e, t) => {
	var n = No();
	t.exports = Po()(n);
})), Io = /* @__PURE__ */ t(((e, t) => {
	var n = Oo(), r = Ao(), i = Fo();
	function a(e) {
		return i(r(e, void 0, n), e + "");
	}
	t.exports = a;
})), Lo = /* @__PURE__ */ t(((e, t) => {
	var n = li(), r = co(), i = Co(), a = _o(), o = ia(), s = To(), c = Io(), l = Ha(), u = 1, d = 2, f = 4;
	t.exports = c(function(e, t) {
		var c = {};
		if (e == null) return c;
		var p = !1;
		t = n(t, function(t) {
			return t = a(t, e), p ||= t.length > 1, t;
		}), o(e, l(e), c), p && (c = r(c, u | d | f, s));
		for (var m = t.length; m--;) i(c, t[m]);
		return c;
	});
})), Ro = /* @__PURE__ */ t(((e, t) => {
	var n = /\s/;
	function r(e) {
		for (var t = e.length; t-- && n.test(e.charAt(t)););
		return t;
	}
	t.exports = r;
})), zo = /* @__PURE__ */ t(((e, t) => {
	var n = Ro(), r = /^\s+/;
	function i(e) {
		return e && e.slice(0, n(e) + 1).replace(r, "");
	}
	t.exports = i;
})), Bo = /* @__PURE__ */ t(((e, t) => {
	var n = zo(), r = Oi(), i = lo(), a = NaN, o = /^[-+]0x[0-9a-f]+$/i, s = /^0b[01]+$/i, c = /^0o[0-7]+$/i, l = parseInt;
	function u(e) {
		if (typeof e == "number") return e;
		if (i(e)) return a;
		if (r(e)) {
			var t = typeof e.valueOf == "function" ? e.valueOf() : e;
			e = r(t) ? t + "" : t;
		}
		if (typeof e != "string") return e === 0 ? e : +e;
		e = n(e);
		var u = s.test(e);
		return u || c.test(e) ? l(e.slice(2), u ? 2 : 8) : o.test(e) ? a : +e;
	}
	t.exports = u;
})), Vo = /* @__PURE__ */ t(((e, t) => {
	var n = Bo(), r = 1 / 0, i = 17976931348623157e292;
	function a(e) {
		return e ? (e = n(e), e === r || e === -r ? (e < 0 ? -1 : 1) * i : e === e ? e : 0) : e === 0 ? e : 0;
	}
	t.exports = a;
})), Ho = /* @__PURE__ */ t(((e, t) => {
	var n = Vo();
	function r(e) {
		var t = n(e), r = t % 1;
		return t === t ? r ? t - r : t : 0;
	}
	t.exports = r;
})), Uo = /* @__PURE__ */ t(((e, t) => {
	var n = Ci(), r = Ho(), i = Bo(), a = go(), o = n.isFinite, s = Math.min;
	function c(e) {
		var t = Math[e];
		return function(e, n) {
			if (e = i(e), n = n == null ? 0 : s(r(n), 292), n && o(e)) {
				var c = (a(e) + "e").split("e");
				return c = (a(t(c[0] + "e" + (+c[1] + n))) + "e").split("e"), +(c[0] + "e" + (+c[1] - n));
			}
			return t(e);
		};
	}
	t.exports = c;
})), Wo = /* @__PURE__ */ t(((e, t) => {
	t.exports = Uo()("round");
})), Go = /* @__PURE__ */ t(((e, t) => {
	function n(e) {
		return this.__data__.set(e, "__lodash_hash_undefined__"), this;
	}
	t.exports = n;
})), Ko = /* @__PURE__ */ t(((e, t) => {
	function n(e) {
		return this.__data__.has(e);
	}
	t.exports = n;
})), qo = /* @__PURE__ */ t(((e, t) => {
	var n = Zi(), r = Go(), i = Ko();
	function a(e) {
		var t = -1, r = e == null ? 0 : e.length;
		for (this.__data__ = new n(); ++t < r;) this.add(e[t]);
	}
	a.prototype.add = a.prototype.push = r, a.prototype.has = i, t.exports = a;
})), Jo = /* @__PURE__ */ t(((e, t) => {
	function n(e, t) {
		for (var n = -1, r = e == null ? 0 : e.length; ++n < r;) if (t(e[n], n, e)) return !0;
		return !1;
	}
	t.exports = n;
})), Yo = /* @__PURE__ */ t(((e, t) => {
	function n(e, t) {
		return e.has(t);
	}
	t.exports = n;
})), Xo = /* @__PURE__ */ t(((e, t) => {
	var n = qo(), r = Jo(), i = Yo(), a = 1, o = 2;
	function s(e, t, s, c, l, u) {
		var d = s & a, f = e.length, p = t.length;
		if (f != p && !(d && p > f)) return !1;
		var m = u.get(e), h = u.get(t);
		if (m && h) return m == t && h == e;
		var g = -1, _ = !0, v = s & o ? new n() : void 0;
		for (u.set(e, t), u.set(t, e); ++g < f;) {
			var y = e[g], b = t[g];
			if (c) var x = d ? c(b, y, g, t, e, u) : c(y, b, g, e, t, u);
			if (x !== void 0) {
				if (x) continue;
				_ = !1;
				break;
			}
			if (v) {
				if (!r(t, function(e, t) {
					if (!i(v, t) && (y === e || l(y, e, s, c, u))) return v.push(t);
				})) {
					_ = !1;
					break;
				}
			} else if (!(y === b || l(y, b, s, c, u))) {
				_ = !1;
				break;
			}
		}
		return u.delete(e), u.delete(t), _;
	}
	t.exports = s;
})), Zo = /* @__PURE__ */ t(((e, t) => {
	function n(e) {
		var t = -1, n = Array(e.size);
		return e.forEach(function(e, r) {
			n[++t] = [r, e];
		}), n;
	}
	t.exports = n;
})), Qo = /* @__PURE__ */ t(((e, t) => {
	function n(e) {
		var t = -1, n = Array(e.size);
		return e.forEach(function(e) {
			n[++t] = e;
		}), n;
	}
	t.exports = n;
})), $o = /* @__PURE__ */ t(((e, t) => {
	var n = wi(), r = Ya(), i = di(), a = Xo(), o = Zo(), s = Qo(), c = 1, l = 2, u = "[object Boolean]", d = "[object Date]", f = "[object Error]", p = "[object Map]", m = "[object Number]", h = "[object RegExp]", g = "[object Set]", _ = "[object String]", v = "[object Symbol]", y = "[object ArrayBuffer]", b = "[object DataView]", x = n ? n.prototype : void 0, S = x ? x.valueOf : void 0;
	function C(e, t, n, x, C, w, T) {
		switch (n) {
			case b:
				if (e.byteLength != t.byteLength || e.byteOffset != t.byteOffset) return !1;
				e = e.buffer, t = t.buffer;
			case y: return !(e.byteLength != t.byteLength || !w(new r(e), new r(t)));
			case u:
			case d:
			case m: return i(+e, +t);
			case f: return e.name == t.name && e.message == t.message;
			case h:
			case _: return e == t + "";
			case p: var E = o;
			case g:
				var D = x & c;
				if (E ||= s, e.size != t.size && !D) return !1;
				var O = T.get(e);
				if (O) return O == t;
				x |= l, T.set(e, t);
				var k = a(E(e), E(t), x, C, w, T);
				return T.delete(e), k;
			case v: if (S) return S.call(e) == S.call(t);
		}
		return !1;
	}
	t.exports = C;
})), es = /* @__PURE__ */ t(((e, t) => {
	var n = Va(), r = 1, i = Object.prototype.hasOwnProperty;
	function a(e, t, a, o, s, c) {
		var l = a & r, u = n(e), d = u.length;
		if (d != n(t).length && !l) return !1;
		for (var f = d; f--;) {
			var p = u[f];
			if (!(l ? p in t : i.call(t, p))) return !1;
		}
		var m = c.get(e), h = c.get(t);
		if (m && h) return m == t && h == e;
		var g = !0;
		c.set(e, t), c.set(t, e);
		for (var _ = l; ++f < d;) {
			p = u[f];
			var v = e[p], y = t[p];
			if (o) var b = l ? o(y, v, p, t, e, c) : o(v, y, p, e, t, c);
			if (!(b === void 0 ? v === y || s(v, y, a, o, c) : b)) {
				g = !1;
				break;
			}
			_ ||= p == "constructor";
		}
		if (g && !_) {
			var x = e.constructor, S = t.constructor;
			x != S && "constructor" in e && "constructor" in t && !(typeof x == "function" && x instanceof x && typeof S == "function" && S instanceof S) && (g = !1);
		}
		return c.delete(e), c.delete(t), g;
	}
	t.exports = a;
})), ts = /* @__PURE__ */ t(((e, t) => {
	var n = $i(), r = Xo(), i = $o(), a = es(), o = qa(), s = la(), c = da(), l = _a(), u = 1, d = "[object Arguments]", f = "[object Array]", p = "[object Object]", m = Object.prototype.hasOwnProperty;
	function h(e, t, h, g, _, v) {
		var y = s(e), b = s(t), x = y ? f : o(e), S = b ? f : o(t);
		x = x == d ? p : x, S = S == d ? p : S;
		var C = x == p, w = S == p, T = x == S;
		if (T && c(e)) {
			if (!c(t)) return !1;
			y = !0, C = !1;
		}
		if (T && !C) return v ||= new n(), y || l(e) ? r(e, t, h, g, _, v) : i(e, t, x, h, g, _, v);
		if (!(h & u)) {
			var E = C && m.call(e, "__wrapped__"), D = w && m.call(t, "__wrapped__");
			if (E || D) {
				var O = E ? e.value() : e, k = D ? t.value() : t;
				return v ||= new n(), _(O, k, h, g, v);
			}
		}
		return T ? (v ||= new n(), a(e, t, h, g, _, v)) : !1;
	}
	t.exports = h;
})), ns = /* @__PURE__ */ t(((e, t) => {
	var n = ts(), r = oa();
	function i(e, t, a, o, s) {
		return e === t ? !0 : e == null || t == null || !r(e) && !r(t) ? e !== e && t !== t : n(e, t, a, o, i, s);
	}
	t.exports = i;
})), rs = /* @__PURE__ */ t(((e, t) => {
	var n = $i(), r = ns(), i = 1, a = 2;
	function o(e, t, o, s) {
		var c = o.length, l = c, u = !s;
		if (e == null) return !l;
		for (e = Object(e); c--;) {
			var d = o[c];
			if (u && d[2] ? d[1] !== e[d[0]] : !(d[0] in e)) return !1;
		}
		for (; ++c < l;) {
			d = o[c];
			var f = d[0], p = e[f], m = d[1];
			if (u && d[2]) {
				if (p === void 0 && !(f in e)) return !1;
			} else {
				var h = new n();
				if (s) var g = s(p, m, f, e, t, h);
				if (!(g === void 0 ? r(m, p, i | a, s, h) : g)) return !1;
			}
		}
		return !0;
	}
	t.exports = o;
})), is = /* @__PURE__ */ t(((e, t) => {
	var n = Oi();
	function r(e) {
		return e === e && !n(e);
	}
	t.exports = r;
})), as = /* @__PURE__ */ t(((e, t) => {
	var n = is(), r = wa();
	function i(e) {
		for (var t = r(e), i = t.length; i--;) {
			var a = t[i], o = e[a];
			t[i] = [
				a,
				o,
				n(o)
			];
		}
		return t;
	}
	t.exports = i;
})), os = /* @__PURE__ */ t(((e, t) => {
	function n(e, t) {
		return function(n) {
			return n != null && n[e] === t && (t !== void 0 || e in Object(n));
		};
	}
	t.exports = n;
})), ss = /* @__PURE__ */ t(((e, t) => {
	var n = rs(), r = as(), i = os();
	function a(e) {
		var t = r(e);
		return t.length == 1 && t[0][2] ? i(t[0][0], t[0][1]) : function(r) {
			return r === e || n(r, e, t);
		};
	}
	t.exports = a;
})), cs = /* @__PURE__ */ t(((e, t) => {
	var n = bo();
	function r(e, t, r) {
		var i = e == null ? void 0 : n(e, t);
		return i === void 0 ? r : i;
	}
	t.exports = r;
})), ls = /* @__PURE__ */ t(((e, t) => {
	function n(e, t) {
		return e != null && t in Object(e);
	}
	t.exports = n;
})), us = /* @__PURE__ */ t(((e, t) => {
	var n = _o(), r = ca(), i = la(), a = fa(), o = pa(), s = yo();
	function c(e, t, c) {
		t = n(t, e);
		for (var l = -1, u = t.length, d = !1; ++l < u;) {
			var f = s(t[l]);
			if (!(d = e != null && c(e, f))) break;
			e = e[f];
		}
		return d || ++l != u ? d : (u = e == null ? 0 : e.length, !!u && o(u) && a(f, u) && (i(e) || r(e)));
	}
	t.exports = c;
})), ds = /* @__PURE__ */ t(((e, t) => {
	var n = ls(), r = us();
	function i(e, t) {
		return e != null && r(e, t, n);
	}
	t.exports = i;
})), fs = /* @__PURE__ */ t(((e, t) => {
	var n = ns(), r = cs(), i = ds(), a = uo(), o = is(), s = os(), c = yo(), l = 1, u = 2;
	function d(e, t) {
		return a(e) && o(t) ? s(c(e), t) : function(a) {
			var o = r(a, e);
			return o === void 0 && o === t ? i(a, e) : n(t, o, l | u);
		};
	}
	t.exports = d;
})), ps = /* @__PURE__ */ t(((e, t) => {
	function n(e) {
		return function(t) {
			return t?.[e];
		};
	}
	t.exports = n;
})), ms = /* @__PURE__ */ t(((e, t) => {
	var n = bo();
	function r(e) {
		return function(t) {
			return n(t, e);
		};
	}
	t.exports = r;
})), hs = /* @__PURE__ */ t(((e, t) => {
	var n = ps(), r = ms(), i = uo(), a = yo();
	function o(e) {
		return i(e) ? n(a(e)) : r(e);
	}
	t.exports = o;
})), gs = /* @__PURE__ */ t(((e, t) => {
	var n = ss(), r = fs(), i = Mo(), a = la(), o = hs();
	function s(e) {
		return typeof e == "function" ? e : e == null ? i : typeof e == "object" ? a(e) ? r(e[0], e[1]) : n(e) : o(e);
	}
	t.exports = s;
})), _s = /* @__PURE__ */ t(((e, t) => {
	function n(e) {
		return function(t, n, r) {
			for (var i = -1, a = Object(t), o = r(t), s = o.length; s--;) {
				var c = o[e ? s : ++i];
				if (n(a[c], c, a) === !1) break;
			}
			return t;
		};
	}
	t.exports = n;
})), vs = /* @__PURE__ */ t(((e, t) => {
	t.exports = _s()();
})), ys = /* @__PURE__ */ t(((e, t) => {
	var n = vs(), r = wa();
	function i(e, t) {
		return e && n(e, t, r);
	}
	t.exports = i;
})), bs = /* @__PURE__ */ t(((e, t) => {
	var n = Ca();
	function r(e, t) {
		return function(r, i) {
			if (r == null) return r;
			if (!n(r)) return e(r, i);
			for (var a = r.length, o = t ? a : -1, s = Object(r); (t ? o-- : ++o < a) && i(s[o], o, s) !== !1;);
			return r;
		};
	}
	t.exports = r;
})), xs = /* @__PURE__ */ t(((e, t) => {
	var n = ys();
	t.exports = bs()(n);
})), Ss = /* @__PURE__ */ t(((e, t) => {
	var n = xs(), r = Ca();
	function i(e, t) {
		var i = -1, a = r(e) ? Array(e.length) : [];
		return n(e, function(e, n, r) {
			a[++i] = t(e, n, r);
		}), a;
	}
	t.exports = i;
})), Cs = /* @__PURE__ */ t(((e, t) => {
	var n = li(), r = gs(), i = Ss(), a = la();
	function o(e, t) {
		return (a(e) ? n : i)(e, r(t, 3));
	}
	t.exports = o;
}));
//#endregion
//#region ../../../resource_engines/node_modules/ketcher-react/dist/index.modern-55d8e3ef.js
Be();
var ws = /* @__PURE__ */ e(Qe()), Ts = /* @__PURE__ */ e(Lo());
Un();
var Es = /* @__PURE__ */ e(r()), Ds = /* @__PURE__ */ e(mt()), Os = Le(), ks = /* @__PURE__ */ e(Wo()), As = /* @__PURE__ */ e(Cs()), js = Object.defineProperty, Ms = Object.getOwnPropertySymbols, Ns = Object.prototype.hasOwnProperty, Ps = Object.prototype.propertyIsEnumerable, Fs = (e, t, n) => t in e ? js(e, t, {
	enumerable: !0,
	configurable: !0,
	writable: !0,
	value: n
}) : e[t] = n, Is = (e, t) => {
	for (var n in t ||= {}) Ns.call(t, n) && Fs(e, n, t[n]);
	if (Ms) for (var n of Ms(t)) Ps.call(t, n) && Fs(e, n, t[n]);
	return e;
}, Ls = Symbol.for("immer-nothing"), Rs = Symbol.for("immer-draftable"), zs = Symbol.for("immer-state");
function Bs(e, ...t) {
	throw Error(`[Immer] minified error nr: ${e}. Full error at: https://bit.ly/3cXEKWf`);
}
var Vs = Object.getPrototypeOf;
function Hs(e) {
	return !!e && !!e[zs];
}
function Us(e) {
	return e ? Gs(e) || Array.isArray(e) || !!e[Rs] || !!e.constructor?.[Rs] || Zs(e) || Qs(e) : !1;
}
var Ws = Object.prototype.constructor.toString();
function Gs(e) {
	if (!e || typeof e != "object") return !1;
	let t = Vs(e);
	if (t === null) return !0;
	let n = Object.hasOwnProperty.call(t, "constructor") && t.constructor;
	return n === Object || typeof n == "function" && Function.toString.call(n) === Ws;
}
function Ks(e, t) {
	qs(e) === 0 ? Reflect.ownKeys(e).forEach((n) => {
		t(n, e[n], e);
	}) : e.forEach((n, r) => t(r, n, e));
}
function qs(e) {
	let t = e[zs];
	return t ? t.type_ : Array.isArray(e) ? 1 : Zs(e) ? 2 : Qs(e) ? 3 : 0;
}
function Js(e, t) {
	return qs(e) === 2 ? e.has(t) : Object.prototype.hasOwnProperty.call(e, t);
}
function Ys(e, t, n) {
	let r = qs(e);
	r === 2 ? e.set(t, n) : r === 3 ? e.add(n) : e[t] = n;
}
function Xs(e, t) {
	return e === t ? e !== 0 || 1 / e == 1 / t : e !== e && t !== t;
}
function Zs(e) {
	return e instanceof Map;
}
function Qs(e) {
	return e instanceof Set;
}
function $s(e) {
	return e.copy_ || e.base_;
}
function ec(e, t) {
	if (Zs(e)) return new Map(e);
	if (Qs(e)) return new Set(e);
	if (Array.isArray(e)) return Array.prototype.slice.call(e);
	let n = Gs(e);
	if (t === !0 || t === "class_only" && !n) {
		let t = Object.getOwnPropertyDescriptors(e);
		delete t[zs];
		let n = Reflect.ownKeys(t);
		for (let r = 0; r < n.length; r++) {
			let i = n[r], a = t[i];
			a.writable === !1 && (a.writable = !0, a.configurable = !0), (a.get || a.set) && (t[i] = {
				configurable: !0,
				writable: !0,
				enumerable: a.enumerable,
				value: e[i]
			});
		}
		return Object.create(Vs(e), t);
	}
	{
		let t = Vs(e);
		if (t !== null && n) return Is({}, e);
		let r = Object.create(t);
		return Object.assign(r, e);
	}
}
function tc(e, t = !1) {
	return rc(e) || Hs(e) || !Us(e) || (qs(e) > 1 && (e.set = e.add = e.clear = e.delete = nc), Object.freeze(e), t && Object.entries(e).forEach(([e, t]) => tc(t, !0))), e;
}
function nc() {
	Bs(2);
}
function rc(e) {
	return Object.isFrozen(e);
}
var ic = {};
function ac(e) {
	let t = ic[e];
	return t || Bs(0, e), t;
}
var oc;
function sc() {
	return oc;
}
function cc(e, t) {
	return {
		drafts_: [],
		parent_: e,
		immer_: t,
		canAutoFreeze_: !0,
		unfinalizedDrafts_: 0
	};
}
function lc(e, t) {
	t && (ac("Patches"), e.patches_ = [], e.inversePatches_ = [], e.patchListener_ = t);
}
function uc(e) {
	dc(e), e.drafts_.forEach(pc), e.drafts_ = null;
}
function dc(e) {
	e === oc && (oc = e.parent_);
}
function fc(e) {
	return oc = cc(oc, e);
}
function pc(e) {
	let t = e[zs];
	t.type_ === 0 || t.type_ === 1 ? t.revoke_() : t.revoked_ = !0;
}
function mc(e, t) {
	t.unfinalizedDrafts_ = t.drafts_.length;
	let n = t.drafts_[0];
	return e !== void 0 && e !== n ? (n[zs].modified_ && (uc(t), Bs(4)), Us(e) && (e = hc(t, e), t.parent_ || _c(t, e)), t.patches_ && ac("Patches").generateReplacementPatches_(n[zs].base_, e, t.patches_, t.inversePatches_)) : e = hc(t, n, []), uc(t), t.patches_ && t.patchListener_(t.patches_, t.inversePatches_), e === Ls ? void 0 : e;
}
function hc(e, t, n) {
	if (rc(t)) return t;
	let r = t[zs];
	if (!r) return Ks(t, (i, a) => gc(e, r, t, i, a, n)), t;
	if (r.scope_ !== e) return t;
	if (!r.modified_) return _c(e, r.base_, !0), r.base_;
	if (!r.finalized_) {
		r.finalized_ = !0, r.scope_.unfinalizedDrafts_--;
		let t = r.copy_, i = t, a = !1;
		r.type_ === 3 && (i = new Set(t), t.clear(), a = !0), Ks(i, (i, o) => gc(e, r, t, i, o, n, a)), _c(e, t, !1), n && e.patches_ && ac("Patches").generatePatches_(r, n, e.patches_, e.inversePatches_);
	}
	return r.copy_;
}
function gc(e, t, n, r, i, a, o) {
	if (Hs(i)) {
		let o = hc(e, i, a && t && t.type_ !== 3 && !Js(t.assigned_, r) ? a.concat(r) : void 0);
		if (Ys(n, r, o), Hs(o)) e.canAutoFreeze_ = !1;
		else return;
	} else o && n.add(i);
	if (Us(i) && !rc(i)) {
		if (!e.immer_.autoFreeze_ && e.unfinalizedDrafts_ < 1) return;
		hc(e, i), (!t || !t.scope_.parent_) && typeof r != "symbol" && Object.prototype.propertyIsEnumerable.call(n, r) && _c(e, i);
	}
}
function _c(e, t, n = !1) {
	!e.parent_ && e.immer_.autoFreeze_ && e.canAutoFreeze_ && tc(t, n);
}
function vc(e, t) {
	let n = Array.isArray(e), r = {
		type_: +!!n,
		scope_: t ? t.scope_ : sc(),
		modified_: !1,
		finalized_: !1,
		assigned_: {},
		parent_: t,
		base_: e,
		draft_: null,
		copy_: null,
		revoke_: null,
		isManual_: !1
	}, i = r, a = yc;
	n && (i = [r], a = bc);
	let { revoke: o, proxy: s } = Proxy.revocable(i, a);
	return r.draft_ = s, r.revoke_ = o, s;
}
var yc = {
	get(e, t) {
		if (t === zs) return e;
		let n = $s(e);
		if (!Js(n, t)) return Sc(e, n, t);
		let r = n[t];
		return e.finalized_ || !Us(r) ? r : r === xc(e.base_, t) ? (Tc(e), e.copy_[t] = Dc(r, e)) : r;
	},
	has(e, t) {
		return t in $s(e);
	},
	ownKeys(e) {
		return Reflect.ownKeys($s(e));
	},
	set(e, t, n) {
		let r = Cc($s(e), t);
		if (r?.set) return r.set.call(e.draft_, n), !0;
		if (!e.modified_) {
			let r = xc($s(e), t), i = r?.[zs];
			if (i && i.base_ === n) return e.copy_[t] = n, e.assigned_[t] = !1, !0;
			if (Xs(n, r) && (n !== void 0 || Js(e.base_, t))) return !0;
			Tc(e), wc(e);
		}
		return e.copy_[t] === n && (n !== void 0 || t in e.copy_) || Number.isNaN(n) && Number.isNaN(e.copy_[t]) || (e.copy_[t] = n, e.assigned_[t] = !0), !0;
	},
	deleteProperty(e, t) {
		return xc(e.base_, t) !== void 0 || t in e.base_ ? (e.assigned_[t] = !1, Tc(e), wc(e)) : delete e.assigned_[t], e.copy_ && delete e.copy_[t], !0;
	},
	getOwnPropertyDescriptor(e, t) {
		let n = $s(e), r = Reflect.getOwnPropertyDescriptor(n, t);
		return r && {
			writable: !0,
			configurable: e.type_ !== 1 || t !== "length",
			enumerable: r.enumerable,
			value: n[t]
		};
	},
	defineProperty() {
		Bs(11);
	},
	getPrototypeOf(e) {
		return Vs(e.base_);
	},
	setPrototypeOf() {
		Bs(12);
	}
}, bc = {};
Ks(yc, (e, t) => {
	bc[e] = function() {
		return arguments[0] = arguments[0][0], t.apply(this, arguments);
	};
}), bc.deleteProperty = function(e, t) {
	return bc.set.call(this, e, t, void 0);
}, bc.set = function(e, t, n) {
	return yc.set.call(this, e[0], t, n, e[0]);
};
function xc(e, t) {
	let n = e[zs];
	return (n ? $s(n) : e)[t];
}
function Sc(e, t, n) {
	let r = Cc(t, n);
	return r ? "value" in r ? r.value : r.get?.call(e.draft_) : void 0;
}
function Cc(e, t) {
	if (!(t in e)) return;
	let n = Vs(e);
	for (; n;) {
		let e = Object.getOwnPropertyDescriptor(n, t);
		if (e) return e;
		n = Vs(n);
	}
}
function wc(e) {
	e.modified_ || (e.modified_ = !0, e.parent_ && wc(e.parent_));
}
function Tc(e) {
	e.copy_ ||= ec(e.base_, e.scope_.immer_.useStrictShallowCopy_);
}
var Ec = class {
	constructor(e) {
		this.autoFreeze_ = !0, this.useStrictShallowCopy_ = !1, this.produce = (e, t, n) => {
			if (typeof e == "function" && typeof t != "function") {
				let n = t;
				t = e;
				let r = this;
				return function(e = n, ...i) {
					return r.produce(e, (e) => t.call(this, e, ...i));
				};
			}
			typeof t != "function" && Bs(6), n !== void 0 && typeof n != "function" && Bs(7);
			let r;
			if (Us(e)) {
				let i = fc(this), a = Dc(e, void 0), o = !0;
				try {
					r = t(a), o = !1;
				} finally {
					o ? uc(i) : dc(i);
				}
				return lc(i, n), mc(r, i);
			}
			if (!e || typeof e != "object") {
				if (r = t(e), r === void 0 && (r = e), r === Ls && (r = void 0), this.autoFreeze_ && tc(r, !0), n) {
					let t = [], i = [];
					ac("Patches").generateReplacementPatches_(e, r, t, i), n(t, i);
				}
				return r;
			}
			Bs(1, e);
		}, this.produceWithPatches = (e, t) => {
			if (typeof e == "function") return (t, ...n) => this.produceWithPatches(t, (t) => e(t, ...n));
			let n, r;
			return [
				this.produce(e, t, (e, t) => {
					n = e, r = t;
				}),
				n,
				r
			];
		}, typeof e?.autoFreeze == "boolean" && this.setAutoFreeze(e.autoFreeze), typeof e?.useStrictShallowCopy == "boolean" && this.setUseStrictShallowCopy(e.useStrictShallowCopy);
	}
	createDraft(e) {
		Us(e) || Bs(8), Hs(e) && (e = Oc(e));
		let t = fc(this), n = Dc(e, void 0);
		return n[zs].isManual_ = !0, dc(t), n;
	}
	finishDraft(e, t) {
		let n = e && e[zs];
		(!n || !n.isManual_) && Bs(9);
		let { scope_: r } = n;
		return lc(r, t), mc(void 0, r);
	}
	setAutoFreeze(e) {
		this.autoFreeze_ = e;
	}
	setUseStrictShallowCopy(e) {
		this.useStrictShallowCopy_ = e;
	}
	applyPatches(e, t) {
		let n;
		for (n = t.length - 1; n >= 0; n--) {
			let r = t[n];
			if (r.path.length === 0 && r.op === "replace") {
				e = r.value;
				break;
			}
		}
		n > -1 && (t = t.slice(n + 1));
		let r = ac("Patches").applyPatches_;
		return Hs(e) ? r(e, t) : this.produce(e, (e) => r(e, t));
	}
};
function Dc(e, t) {
	let n = Zs(e) ? ac("MapSet").proxyMap_(e, t) : Qs(e) ? ac("MapSet").proxySet_(e, t) : vc(e, t);
	return (t ? t.scope_ : sc()).drafts_.push(n), n;
}
function Oc(e) {
	return Hs(e) || Bs(10, e), kc(e);
}
function kc(e) {
	if (!Us(e) || rc(e)) return e;
	let t = e[zs], n;
	if (t) {
		if (!t.modified_) return t.base_;
		t.finalized_ = !0, n = ec(e, t.scope_.immer_.useStrictShallowCopy_);
	} else n = ec(e, !0);
	return Ks(n, (e, t) => {
		Ys(n, e, kc(t));
	}), t && (t.finalized_ = !1), n;
}
var Ac = new Ec(), jc = Ac.produce;
Ac.produceWithPatches.bind(Ac), Ac.setAutoFreeze.bind(Ac), Ac.setUseStrictShallowCopy.bind(Ac), Ac.applyPatches.bind(Ac), Ac.createDraft.bind(Ac), Ac.finishDraft.bind(Ac);
var Mc = Object.defineProperty, Nc = Object.defineProperties, Pc = Object.getOwnPropertyDescriptors, Fc = Object.getOwnPropertySymbols, Ic = Object.prototype.hasOwnProperty, Lc = Object.prototype.propertyIsEnumerable, Rc = (e, t, n) => t in e ? Mc(e, t, {
	enumerable: !0,
	configurable: !0,
	writable: !0,
	value: n
}) : e[t] = n, zc = (e, t) => {
	for (var n in t ||= {}) Ic.call(t, n) && Rc(e, n, t[n]);
	if (Fc) for (var n of Fc(t)) Lc.call(t, n) && Rc(e, n, t[n]);
	return e;
}, Bc = (e, t) => Nc(e, Pc(t)), Vc = (e, t) => {
	var n = {};
	for (var r in e) Ic.call(e, r) && t.indexOf(r) < 0 && (n[r] = e[r]);
	if (e != null && Fc) for (var r of Fc(e)) t.indexOf(r) < 0 && Lc.call(e, r) && (n[r] = e[r]);
	return n;
}, Hc = typeof window < "u" && window.__REDUX_DEVTOOLS_EXTENSION_COMPOSE__ ? window.__REDUX_DEVTOOLS_EXTENSION_COMPOSE__ : function() {
	if (arguments.length !== 0) return typeof arguments[0] == "object" ? Ot : Ot.apply(null, arguments);
};
function Uc(e, t) {
	function n(...n) {
		if (t) {
			let r = t(...n);
			if (!r) throw Error(ml(0));
			return zc(zc({
				type: e,
				payload: r.payload
			}, "meta" in r && { meta: r.meta }), "error" in r && { error: r.error });
		}
		return {
			type: e,
			payload: n[0]
		};
	}
	return n.toString = () => `${e}`, n.type = e, n.match = (t) => gn(t) && t.type === e, n;
}
var Wc = class e extends Array {
	constructor(...t) {
		super(...t), Object.setPrototypeOf(this, e.prototype);
	}
	static get [Symbol.species]() {
		return e;
	}
	concat(...e) {
		return super.concat.apply(this, e);
	}
	prepend(...t) {
		return t.length === 1 && Array.isArray(t[0]) ? new e(...t[0].concat(this)) : new e(...t.concat(this));
	}
};
function Gc(e) {
	return Us(e) ? jc(e, () => {}) : e;
}
function Kc(e, t, n) {
	return e.has(t) ? e.get(t) : e.set(t, n(t)).get(t);
}
function qc(e) {
	return typeof e == "boolean";
}
var Jc = () => function(e) {
	let { thunk: t = !0, immutableCheck: n = !0, serializableCheck: r = !0, actionCreatorCheck: i = !0 } = e ?? {}, a = new Wc();
	return t && (qc(t) ? a.push(En) : a.push(Tt(t.extraArgument))), a;
}, Yc = "RTK_autoBatch", Xc = (e) => (t) => {
	setTimeout(t, e);
}, Zc = (e = { type: "raf" }) => (t) => (...n) => {
	let r = t(...n), i = !0, a = !1, o = !1, s = /* @__PURE__ */ new Set(), c = e.type === "tick" ? queueMicrotask : e.type === "raf" ? typeof window < "u" && window.requestAnimationFrame ? window.requestAnimationFrame : Xc(10) : e.type === "callback" ? e.queueNotification : Xc(e.timeout), l = () => {
		o = !1, a && (a = !1, s.forEach((e) => e()));
	};
	return Object.assign({}, r, {
		subscribe(e) {
			let t = r.subscribe(() => i && e());
			return s.add(e), () => {
				t(), s.delete(e);
			};
		},
		dispatch(e) {
			try {
				return i = !e?.meta?.[Yc], a = !i, a && (o || (o = !0, c(l))), r.dispatch(e);
			} finally {
				i = !0;
			}
		}
	});
}, Qc = (e) => function(t) {
	let { autoBatch: n = !0 } = t ?? {}, r = new Wc(e);
	return n && r.push(Zc(typeof n == "object" ? n : void 0)), r;
};
function $c(e) {
	let t = Jc(), { reducer: n = void 0, middleware: r, devTools: i = !0, duplicateMiddlewareCheck: a = !0, preloadedState: o = void 0, enhancers: s = void 0 } = e || {}, c;
	if (typeof n == "function") c = n;
	else if (an(n)) c = Mn(n);
	else throw Error(ml(1));
	let l;
	l = typeof r == "function" ? r(t) : t();
	let u = Ot;
	i && (u = Hc(zc({ trace: !1 }, typeof i == "object" && i)));
	let d = Qc(tn(...l)), f = typeof s == "function" ? s(d) : d(), p = u(...f);
	return Pt(c, o, p);
}
function el(e) {
	let t = {}, n = [], r, i = {
		addCase(e, n) {
			let r = typeof e == "string" ? e : e.type;
			if (!r) throw Error(ml(28));
			if (r in t) throw Error(ml(29));
			return t[r] = n, i;
		},
		addMatcher(e, t) {
			return n.push({
				matcher: e,
				reducer: t
			}), i;
		},
		addDefaultCase(e) {
			return r = e, i;
		}
	};
	return e(i), [
		t,
		n,
		r
	];
}
function tl(e) {
	return typeof e == "function";
}
function nl(e, t) {
	let [n, r, i] = el(t), a;
	if (tl(e)) a = () => Gc(e());
	else {
		let t = Gc(e);
		a = () => t;
	}
	function o(e = a(), t) {
		let o = [n[t.type], ...r.filter(({ matcher: e }) => e(t)).map(({ reducer: e }) => e)];
		return o.filter((e) => !!e).length === 0 && (o = [i]), o.reduce((e, n) => {
			if (n) {
				if (Hs(e)) {
					let r = n(e, t);
					return r === void 0 ? e : r;
				}
				if (Us(e)) return jc(e, (e) => n(e, t));
				{
					let r = n(e, t);
					if (r === void 0) {
						if (e === null) return e;
						throw Error("A case reducer on a non-draftable value must not return undefined");
					}
					return r;
				}
			}
			return e;
		}, e);
	}
	return o.getInitialState = a, o;
}
var rl = /* @__PURE__ */ Symbol.for("rtk-slice-createasyncthunk");
function il(e, t) {
	return `${e}/${t}`;
}
function al({ creators: e } = {}) {
	let t = e?.asyncThunk?.[rl];
	return function(e) {
		let { name: n, reducerPath: r = n } = e;
		if (!n) throw Error(ml(11));
		let i = (typeof e.reducers == "function" ? e.reducers(cl()) : e.reducers) || {}, a = Object.keys(i), o = {
			sliceCaseReducersByName: {},
			sliceCaseReducersByType: {},
			actionCreators: {},
			sliceMatchers: []
		}, s = {
			addCase(e, t) {
				let n = typeof e == "string" ? e : e.type;
				if (!n) throw Error(ml(12));
				if (n in o.sliceCaseReducersByType) throw Error(ml(13));
				return o.sliceCaseReducersByType[n] = t, s;
			},
			addMatcher(e, t) {
				return o.sliceMatchers.push({
					matcher: e,
					reducer: t
				}), s;
			},
			exposeAction(e, t) {
				return o.actionCreators[e] = t, s;
			},
			exposeCaseReducer(e, t) {
				return o.sliceCaseReducersByName[e] = t, s;
			}
		};
		a.forEach((r) => {
			let a = i[r], o = {
				reducerName: r,
				type: il(n, r),
				createNotation: typeof e.reducers == "function"
			};
			ul(a) ? fl(o, a, s, t) : ll(o, a, s);
		});
		function c() {
			let [t = {}, n = [], r = void 0] = typeof e.extraReducers == "function" ? el(e.extraReducers) : [e.extraReducers], i = zc(zc({}, t), o.sliceCaseReducersByType);
			return nl(e.initialState, (e) => {
				for (let t in i) e.addCase(t, i[t]);
				for (let t of o.sliceMatchers) e.addMatcher(t.matcher, t.reducer);
				for (let t of n) e.addMatcher(t.matcher, t.reducer);
				r && e.addDefaultCase(r);
			});
		}
		let l = (e) => e, u = /* @__PURE__ */ new Map(), d = /* @__PURE__ */ new WeakMap(), f;
		function p(e, t) {
			return f ||= c(), f(e, t);
		}
		function m() {
			return f ||= c(), f.getInitialState();
		}
		function h(t, n = !1) {
			function r(e) {
				let i = e[t];
				return i === void 0 && n && (i = Kc(d, r, m)), i;
			}
			function i(t = l) {
				return Kc(Kc(u, n, () => /* @__PURE__ */ new WeakMap()), t, () => {
					let r = {};
					for (let [i, a] of Object.entries(e.selectors ?? {})) r[i] = ol(a, t, () => Kc(d, t, m), n);
					return r;
				});
			}
			return {
				reducerPath: t,
				getSelectors: i,
				get selectors() {
					return i(r);
				},
				selectSlice: r
			};
		}
		let g = Bc(zc({
			name: n,
			reducer: p,
			actions: o.actionCreators,
			caseReducers: o.sliceCaseReducersByName,
			getInitialState: m
		}, h(r)), { injectInto(e, t = {}) {
			var n = t, { reducerPath: i } = n, a = Vc(n, ["reducerPath"]);
			let o = i ?? r;
			return e.inject({
				reducerPath: o,
				reducer: p
			}, a), zc(zc({}, g), h(o, !0));
		} });
		return g;
	};
}
function ol(e, t, n, r) {
	function i(i, ...a) {
		let o = t(i);
		return o === void 0 && r && (o = n()), e(o, ...a);
	}
	return i.unwrapped = e, i;
}
var sl = /* @__PURE__ */ al();
function cl() {
	function e(e, t) {
		return zc({
			_reducerDefinitionType: "asyncThunk",
			payloadCreator: e
		}, t);
	}
	return e.withTypes = () => e, {
		reducer(e) {
			return Object.assign({ [e.name](...t) {
				return e(...t);
			} }[e.name], { _reducerDefinitionType: "reducer" });
		},
		preparedReducer(e, t) {
			return {
				_reducerDefinitionType: "reducerWithPrepare",
				prepare: e,
				reducer: t
			};
		},
		asyncThunk: e
	};
}
function ll({ type: e, reducerName: t, createNotation: n }, r, i) {
	let a, o;
	if ("reducer" in r) {
		if (n && !dl(r)) throw Error(ml(17));
		a = r.reducer, o = r.prepare;
	} else a = r;
	i.addCase(e, a).exposeCaseReducer(t, a).exposeAction(t, o ? Uc(e, o) : Uc(e));
}
function ul(e) {
	return e._reducerDefinitionType === "asyncThunk";
}
function dl(e) {
	return e._reducerDefinitionType === "reducerWithPrepare";
}
function fl({ type: e, reducerName: t }, n, r, i) {
	if (!i) throw Error(ml(18));
	let { payloadCreator: a, fulfilled: o, pending: s, rejected: c, settled: l, options: u } = n, d = i(e, a, u);
	r.exposeAction(t, d), o && r.addCase(d.fulfilled, o), s && r.addCase(d.pending, s), c && r.addCase(d.rejected, c), l && r.addMatcher(d.settled, l), r.exposeCaseReducer(t, {
		fulfilled: o || pl,
		pending: s || pl,
		rejected: c || pl,
		settled: l || pl
	});
}
function pl() {}
function ml(e) {
	return `Minified Redux Toolkit error #${e}; visit https://redux-toolkit.js.org/Errors?code=${e} for the full message or use the non-minified dev environment for full errors. `;
}
function hl(e, t) {
	return e == null || t == null ? NaN : e < t ? -1 : e > t ? 1 : e >= t ? 0 : NaN;
}
function gl(e, t) {
	return e == null || t == null ? NaN : t < e ? -1 : t > e ? 1 : t >= e ? 0 : NaN;
}
function _l(e) {
	let t, n, r;
	e.length === 2 ? (t = e === hl || e === gl ? e : vl, n = e, r = e) : (t = hl, n = (t, n) => hl(e(t), n), r = (t, n) => e(t) - n);
	function i(e, r, i = 0, a = e.length) {
		if (i < a) {
			if (t(r, r) !== 0) return a;
			do {
				let t = i + a >>> 1;
				n(e[t], r) < 0 ? i = t + 1 : a = t;
			} while (i < a);
		}
		return i;
	}
	function a(e, r, i = 0, a = e.length) {
		if (i < a) {
			if (t(r, r) !== 0) return a;
			do {
				let t = i + a >>> 1;
				n(e[t], r) <= 0 ? i = t + 1 : a = t;
			} while (i < a);
		}
		return i;
	}
	function o(e, t, n = 0, a = e.length) {
		let o = i(e, t, n, a - 1);
		return o > n && r(e[o - 1], t) > -r(e[o], t) ? o - 1 : o;
	}
	return {
		left: i,
		center: o,
		right: a
	};
}
function vl() {
	return 0;
}
function yl(e) {
	return e === null ? NaN : +e;
}
var bl = _l(hl).right;
_l(yl).center;
var xl = bl, Sl = Math.sqrt(50), Cl = Math.sqrt(10), wl = Math.sqrt(2);
function Tl(e, t, n) {
	let r = (t - e) / Math.max(0, n), i = Math.floor(Math.log10(r)), a = r / 10 ** i, o = a >= Sl ? 10 : a >= Cl ? 5 : a >= wl ? 2 : 1, s, c, l;
	return i < 0 ? (l = 10 ** -i / o, s = Math.round(e * l), c = Math.round(t * l), s / l < e && ++s, c / l > t && --c, l = -l) : (l = 10 ** i * o, s = Math.round(e / l), c = Math.round(t / l), s * l < e && ++s, c * l > t && --c), c < s && .5 <= n && n < 2 ? Tl(e, t, n * 2) : [
		s,
		c,
		l
	];
}
function El(e, t, n) {
	if (t = +t, e = +e, n = +n, !(n > 0)) return [];
	if (e === t) return [e];
	let r = t < e, [i, a, o] = r ? Tl(t, e, n) : Tl(e, t, n);
	if (!(a >= i)) return [];
	let s = a - i + 1, c = Array(s);
	if (r) {
		if (o < 0) for (let e = 0; e < s; ++e) c[e] = (a - e) / -o;
		else for (let e = 0; e < s; ++e) c[e] = (a - e) * o;
	} else if (o < 0) for (let e = 0; e < s; ++e) c[e] = (i + e) / -o;
	else for (let e = 0; e < s; ++e) c[e] = (i + e) * o;
	return c;
}
function Dl(e, t, n) {
	return t = +t, e = +e, n = +n, Tl(e, t, n)[2];
}
function Ol(e, t, n) {
	t = +t, e = +e, n = +n;
	let r = t < e, i = r ? Dl(t, e, n) : Dl(e, t, n);
	return (r ? -1 : 1) * (i < 0 ? 1 / -i : i);
}
function kl(e) {
	return e;
}
var Al = 1, jl = 2, Ml = 3, Nl = 4, Pl = 1e-6;
function Fl(e) {
	return "translate(" + e + ",0)";
}
function Il(e) {
	return "translate(0," + e + ")";
}
function Ll(e) {
	return (t) => +e(t);
}
function Rl(e, t) {
	return t = Math.max(0, e.bandwidth() - t * 2) / 2, e.round() && (t = Math.round(t)), (n) => +e(n) + t;
}
function zl() {
	return !this.__axis;
}
function Bl(e, t) {
	var n = [], r = null, i = null, a = 6, o = 6, s = 3, c = typeof window < "u" && window.devicePixelRatio > 1 ? 0 : .5, l = e === Al || e === Nl ? -1 : 1, u = e === Nl || e === jl ? "x" : "y", d = e === Al || e === Ml ? Fl : Il;
	function f(f) {
		var p = r ?? (t.ticks ? t.ticks.apply(t, n) : t.domain()), m = i ?? (t.tickFormat ? t.tickFormat.apply(t, n) : kl), h = Math.max(a, 0) + s, g = t.range(), _ = +g[0] + c, v = +g[g.length - 1] + c, y = (t.bandwidth ? Rl : Ll)(t.copy(), c), b = f.selection ? f.selection() : f, x = b.selectAll(".domain").data([null]), S = b.selectAll(".tick").data(p, t).order(), C = S.exit(), w = S.enter().append("g").attr("class", "tick"), T = S.select("line"), E = S.select("text");
		x = x.merge(x.enter().insert("path", ".tick").attr("class", "domain").attr("stroke", "currentColor")), S = S.merge(w), T = T.merge(w.append("line").attr("stroke", "currentColor").attr(u + "2", l * a)), E = E.merge(w.append("text").attr("fill", "currentColor").attr(u, l * h).attr("dy", e === Al ? "0em" : e === Ml ? "0.71em" : "0.32em")), f !== b && (x = x.transition(f), S = S.transition(f), T = T.transition(f), E = E.transition(f), C = C.transition(f).attr("opacity", Pl).attr("transform", function(e) {
			return isFinite(e = y(e)) ? d(e + c) : this.getAttribute("transform");
		}), w.attr("opacity", Pl).attr("transform", function(e) {
			var t = this.parentNode.__axis;
			return d((t && isFinite(t = t(e)) ? t : y(e)) + c);
		})), C.remove(), x.attr("d", e === Nl || e === jl ? o ? "M" + l * o + "," + _ + "H" + c + "V" + v + "H" + l * o : "M" + c + "," + _ + "V" + v : o ? "M" + _ + "," + l * o + "V" + c + "H" + v + "V" + l * o : "M" + _ + "," + c + "H" + v), S.attr("opacity", 1).attr("transform", function(e) {
			return d(y(e) + c);
		}), T.attr(u + "2", l * a), E.attr(u, l * h).text(m), b.filter(zl).attr("fill", "none").attr("font-size", 10).attr("font-family", "sans-serif").attr("text-anchor", e === jl ? "start" : e === Nl ? "end" : "middle"), b.each(function() {
			this.__axis = y;
		});
	}
	return f.scale = function(e) {
		return arguments.length ? (t = e, f) : t;
	}, f.ticks = function() {
		return n = Array.from(arguments), f;
	}, f.tickArguments = function(e) {
		return arguments.length ? (n = e == null ? [] : Array.from(e), f) : n.slice();
	}, f.tickValues = function(e) {
		return arguments.length ? (r = e == null ? null : Array.from(e), f) : r && r.slice();
	}, f.tickFormat = function(e) {
		return arguments.length ? (i = e, f) : i;
	}, f.tickSize = function(e) {
		return arguments.length ? (a = o = +e, f) : a;
	}, f.tickSizeInner = function(e) {
		return arguments.length ? (a = +e, f) : a;
	}, f.tickSizeOuter = function(e) {
		return arguments.length ? (o = +e, f) : o;
	}, f.tickPadding = function(e) {
		return arguments.length ? (s = +e, f) : s;
	}, f.offset = function(e) {
		return arguments.length ? (c = +e, f) : c;
	}, f;
}
function Vl(e) {
	return Bl(Ml, e);
}
function Hl(e) {
	return Bl(Nl, e);
}
var Ul = { value: () => {} };
function Wl() {
	for (var e = 0, t = arguments.length, n = {}, r; e < t; ++e) {
		if (!(r = arguments[e] + "") || r in n || /[\s.]/.test(r)) throw Error("illegal type: " + r);
		n[r] = [];
	}
	return new Gl(n);
}
function Gl(e) {
	this._ = e;
}
function Kl(e, t) {
	return e.trim().split(/^|\s+/).map(function(e) {
		var n = "", r = e.indexOf(".");
		if (r >= 0 && (n = e.slice(r + 1), e = e.slice(0, r)), e && !t.hasOwnProperty(e)) throw Error("unknown type: " + e);
		return {
			type: e,
			name: n
		};
	});
}
Gl.prototype = Wl.prototype = {
	constructor: Gl,
	on: function(e, t) {
		var n = this._, r = Kl(e + "", n), i, a = -1, o = r.length;
		if (arguments.length < 2) {
			for (; ++a < o;) if ((i = (e = r[a]).type) && (i = ql(n[i], e.name))) return i;
		} else {
			if (t != null && typeof t != "function") throw Error("invalid callback: " + t);
			for (; ++a < o;) if (i = (e = r[a]).type) n[i] = Jl(n[i], e.name, t);
			else if (t == null) for (i in n) n[i] = Jl(n[i], e.name, null);
			return this;
		}
	},
	copy: function() {
		var e = {}, t = this._;
		for (var n in t) e[n] = t[n].slice();
		return new Gl(e);
	},
	call: function(e, t) {
		if ((i = arguments.length - 2) > 0) for (var n = Array(i), r = 0, i, a; r < i; ++r) n[r] = arguments[r + 2];
		if (!this._.hasOwnProperty(e)) throw Error("unknown type: " + e);
		for (a = this._[e], r = 0, i = a.length; r < i; ++r) a[r].value.apply(t, n);
	},
	apply: function(e, t, n) {
		if (!this._.hasOwnProperty(e)) throw Error("unknown type: " + e);
		for (var r = this._[e], i = 0, a = r.length; i < a; ++i) r[i].value.apply(t, n);
	}
};
function ql(e, t) {
	for (var n = 0, r = e.length, i; n < r; ++n) if ((i = e[n]).name === t) return i.value;
}
function Jl(e, t, n) {
	for (var r = 0, i = e.length; r < i; ++r) if (e[r].name === t) {
		e[r] = Ul, e = e.slice(0, r).concat(e.slice(r + 1));
		break;
	}
	return n != null && e.push({
		name: t,
		value: n
	}), e;
}
var Yl = "http://www.w3.org/1999/xhtml", Xl = {
	svg: "http://www.w3.org/2000/svg",
	xhtml: Yl,
	xlink: "http://www.w3.org/1999/xlink",
	xml: "http://www.w3.org/XML/1998/namespace",
	xmlns: "http://www.w3.org/2000/xmlns/"
};
function Zl(e) {
	var t = e += "", n = t.indexOf(":");
	return n >= 0 && (t = e.slice(0, n)) !== "xmlns" && (e = e.slice(n + 1)), Xl.hasOwnProperty(t) ? {
		space: Xl[t],
		local: e
	} : e;
}
function Ql(e) {
	return function() {
		var t = this.ownerDocument, n = this.namespaceURI;
		return n === Yl && t.documentElement.namespaceURI === Yl ? t.createElement(e) : t.createElementNS(n, e);
	};
}
function $l(e) {
	return function() {
		return this.ownerDocument.createElementNS(e.space, e.local);
	};
}
function eu(e) {
	var t = Zl(e);
	return (t.local ? $l : Ql)(t);
}
function tu() {}
function nu(e) {
	return e == null ? tu : function() {
		return this.querySelector(e);
	};
}
function ru(e) {
	typeof e != "function" && (e = nu(e));
	for (var t = this._groups, n = t.length, r = Array(n), i = 0; i < n; ++i) for (var a = t[i], o = a.length, s = r[i] = Array(o), c, l, u = 0; u < o; ++u) (c = a[u]) && (l = e.call(c, c.__data__, u, a)) && ("__data__" in c && (l.__data__ = c.__data__), s[u] = l);
	return new Gd(r, this._parents);
}
function iu(e) {
	return e == null ? [] : Array.isArray(e) ? e : Array.from(e);
}
function au() {
	return [];
}
function ou(e) {
	return e == null ? au : function() {
		return this.querySelectorAll(e);
	};
}
function su(e) {
	return function() {
		return iu(e.apply(this, arguments));
	};
}
function cu(e) {
	e = typeof e == "function" ? su(e) : ou(e);
	for (var t = this._groups, n = t.length, r = [], i = [], a = 0; a < n; ++a) for (var o = t[a], s = o.length, c, l = 0; l < s; ++l) (c = o[l]) && (r.push(e.call(c, c.__data__, l, o)), i.push(c));
	return new Gd(r, i);
}
function lu(e) {
	return function() {
		return this.matches(e);
	};
}
function uu(e) {
	return function(t) {
		return t.matches(e);
	};
}
var du = Array.prototype.find;
function fu(e) {
	return function() {
		return du.call(this.children, e);
	};
}
function pu() {
	return this.firstElementChild;
}
function mu(e) {
	return this.select(e == null ? pu : fu(typeof e == "function" ? e : uu(e)));
}
var hu = Array.prototype.filter;
function gu() {
	return Array.from(this.children);
}
function _u(e) {
	return function() {
		return hu.call(this.children, e);
	};
}
function vu(e) {
	return this.selectAll(e == null ? gu : _u(typeof e == "function" ? e : uu(e)));
}
function yu(e) {
	typeof e != "function" && (e = lu(e));
	for (var t = this._groups, n = t.length, r = Array(n), i = 0; i < n; ++i) for (var a = t[i], o = a.length, s = r[i] = [], c, l = 0; l < o; ++l) (c = a[l]) && e.call(c, c.__data__, l, a) && s.push(c);
	return new Gd(r, this._parents);
}
function bu(e) {
	return Array(e.length);
}
function xu() {
	return new Gd(this._enter || this._groups.map(bu), this._parents);
}
function Su(e, t) {
	this.ownerDocument = e.ownerDocument, this.namespaceURI = e.namespaceURI, this._next = null, this._parent = e, this.__data__ = t;
}
Su.prototype = {
	constructor: Su,
	appendChild: function(e) {
		return this._parent.insertBefore(e, this._next);
	},
	insertBefore: function(e, t) {
		return this._parent.insertBefore(e, t);
	},
	querySelector: function(e) {
		return this._parent.querySelector(e);
	},
	querySelectorAll: function(e) {
		return this._parent.querySelectorAll(e);
	}
};
function Cu(e) {
	return function() {
		return e;
	};
}
function wu(e, t, n, r, i, a) {
	for (var o = 0, s, c = t.length, l = a.length; o < l; ++o) (s = t[o]) ? (s.__data__ = a[o], r[o] = s) : n[o] = new Su(e, a[o]);
	for (; o < c; ++o) (s = t[o]) && (i[o] = s);
}
function Tu(e, t, n, r, i, a, o) {
	var s, c, l = /* @__PURE__ */ new Map(), u = t.length, d = a.length, f = Array(u), p;
	for (s = 0; s < u; ++s) (c = t[s]) && (f[s] = p = o.call(c, c.__data__, s, t) + "", l.has(p) ? i[s] = c : l.set(p, c));
	for (s = 0; s < d; ++s) p = o.call(e, a[s], s, a) + "", (c = l.get(p)) ? (r[s] = c, c.__data__ = a[s], l.delete(p)) : n[s] = new Su(e, a[s]);
	for (s = 0; s < u; ++s) (c = t[s]) && l.get(f[s]) === c && (i[s] = c);
}
function Eu(e) {
	return e.__data__;
}
function Du(e, t) {
	if (!arguments.length) return Array.from(this, Eu);
	var n = t ? Tu : wu, r = this._parents, i = this._groups;
	typeof e != "function" && (e = Cu(e));
	for (var a = i.length, o = Array(a), s = Array(a), c = Array(a), l = 0; l < a; ++l) {
		var u = r[l], d = i[l], f = d.length, p = Ou(e.call(u, u && u.__data__, l, r)), m = p.length, h = s[l] = Array(m), g = o[l] = Array(m);
		n(u, d, h, g, c[l] = Array(f), p, t);
		for (var _ = 0, v = 0, y, b; _ < m; ++_) if (y = h[_]) {
			for (_ >= v && (v = _ + 1); !(b = g[v]) && ++v < m;);
			y._next = b || null;
		}
	}
	return o = new Gd(o, r), o._enter = s, o._exit = c, o;
}
function Ou(e) {
	return typeof e == "object" && "length" in e ? e : Array.from(e);
}
function ku() {
	return new Gd(this._exit || this._groups.map(bu), this._parents);
}
function Au(e, t, n) {
	var r = this.enter(), i = this, a = this.exit();
	return typeof e == "function" ? (r = e(r), r &&= r.selection()) : r = r.append(e + ""), t != null && (i = t(i), i &&= i.selection()), n == null ? a.remove() : n(a), r && i ? r.merge(i).order() : i;
}
function ju(e) {
	for (var t = e.selection ? e.selection() : e, n = this._groups, r = t._groups, i = n.length, a = r.length, o = Math.min(i, a), s = Array(i), c = 0; c < o; ++c) for (var l = n[c], u = r[c], d = l.length, f = s[c] = Array(d), p, m = 0; m < d; ++m) (p = l[m] || u[m]) && (f[m] = p);
	for (; c < i; ++c) s[c] = n[c];
	return new Gd(s, this._parents);
}
function Mu() {
	for (var e = this._groups, t = -1, n = e.length; ++t < n;) for (var r = e[t], i = r.length - 1, a = r[i], o; --i >= 0;) (o = r[i]) && (a && o.compareDocumentPosition(a) ^ 4 && a.parentNode.insertBefore(o, a), a = o);
	return this;
}
function Nu(e) {
	e ||= Pu;
	function t(t, n) {
		return t && n ? e(t.__data__, n.__data__) : !t - !n;
	}
	for (var n = this._groups, r = n.length, i = Array(r), a = 0; a < r; ++a) {
		for (var o = n[a], s = o.length, c = i[a] = Array(s), l, u = 0; u < s; ++u) (l = o[u]) && (c[u] = l);
		c.sort(t);
	}
	return new Gd(i, this._parents).order();
}
function Pu(e, t) {
	return e < t ? -1 : e > t ? 1 : e >= t ? 0 : NaN;
}
function Fu() {
	var e = arguments[0];
	return arguments[0] = this, e.apply(null, arguments), this;
}
function Iu() {
	return Array.from(this);
}
function Lu() {
	for (var e = this._groups, t = 0, n = e.length; t < n; ++t) for (var r = e[t], i = 0, a = r.length; i < a; ++i) {
		var o = r[i];
		if (o) return o;
	}
	return null;
}
function Ru() {
	let e = 0;
	for (let t of this) ++e;
	return e;
}
function zu() {
	return !this.node();
}
function Bu(e) {
	for (var t = this._groups, n = 0, r = t.length; n < r; ++n) for (var i = t[n], a = 0, o = i.length, s; a < o; ++a) (s = i[a]) && e.call(s, s.__data__, a, i);
	return this;
}
function Vu(e) {
	return function() {
		this.removeAttribute(e);
	};
}
function Hu(e) {
	return function() {
		this.removeAttributeNS(e.space, e.local);
	};
}
function Uu(e, t) {
	return function() {
		this.setAttribute(e, t);
	};
}
function Wu(e, t) {
	return function() {
		this.setAttributeNS(e.space, e.local, t);
	};
}
function Gu(e, t) {
	return function() {
		var n = t.apply(this, arguments);
		n == null ? this.removeAttribute(e) : this.setAttribute(e, n);
	};
}
function Ku(e, t) {
	return function() {
		var n = t.apply(this, arguments);
		n == null ? this.removeAttributeNS(e.space, e.local) : this.setAttributeNS(e.space, e.local, n);
	};
}
function qu(e, t) {
	var n = Zl(e);
	if (arguments.length < 2) {
		var r = this.node();
		return n.local ? r.getAttributeNS(n.space, n.local) : r.getAttribute(n);
	}
	return this.each((t == null ? n.local ? Hu : Vu : typeof t == "function" ? n.local ? Ku : Gu : n.local ? Wu : Uu)(n, t));
}
function Ju(e) {
	return e.ownerDocument && e.ownerDocument.defaultView || e.document && e || e.defaultView;
}
function Yu(e) {
	return function() {
		this.style.removeProperty(e);
	};
}
function Xu(e, t, n) {
	return function() {
		this.style.setProperty(e, t, n);
	};
}
function Zu(e, t, n) {
	return function() {
		var r = t.apply(this, arguments);
		r == null ? this.style.removeProperty(e) : this.style.setProperty(e, r, n);
	};
}
function Qu(e, t, n) {
	return arguments.length > 1 ? this.each((t == null ? Yu : typeof t == "function" ? Zu : Xu)(e, t, n ?? "")) : $u(this.node(), e);
}
function $u(e, t) {
	return e.style.getPropertyValue(t) || Ju(e).getComputedStyle(e, null).getPropertyValue(t);
}
function ed(e) {
	return function() {
		delete this[e];
	};
}
function td(e, t) {
	return function() {
		this[e] = t;
	};
}
function nd(e, t) {
	return function() {
		var n = t.apply(this, arguments);
		n == null ? delete this[e] : this[e] = n;
	};
}
function rd(e, t) {
	return arguments.length > 1 ? this.each((t == null ? ed : typeof t == "function" ? nd : td)(e, t)) : this.node()[e];
}
function id(e) {
	return e.trim().split(/^|\s+/);
}
function ad(e) {
	return e.classList || new od(e);
}
function od(e) {
	this._node = e, this._names = id(e.getAttribute("class") || "");
}
od.prototype = {
	add: function(e) {
		this._names.indexOf(e) < 0 && (this._names.push(e), this._node.setAttribute("class", this._names.join(" ")));
	},
	remove: function(e) {
		var t = this._names.indexOf(e);
		t >= 0 && (this._names.splice(t, 1), this._node.setAttribute("class", this._names.join(" ")));
	},
	contains: function(e) {
		return this._names.indexOf(e) >= 0;
	}
};
function sd(e, t) {
	for (var n = ad(e), r = -1, i = t.length; ++r < i;) n.add(t[r]);
}
function cd(e, t) {
	for (var n = ad(e), r = -1, i = t.length; ++r < i;) n.remove(t[r]);
}
function ld(e) {
	return function() {
		sd(this, e);
	};
}
function ud(e) {
	return function() {
		cd(this, e);
	};
}
function dd(e, t) {
	return function() {
		(t.apply(this, arguments) ? sd : cd)(this, e);
	};
}
function fd(e, t) {
	var n = id(e + "");
	if (arguments.length < 2) {
		for (var r = ad(this.node()), i = -1, a = n.length; ++i < a;) if (!r.contains(n[i])) return !1;
		return !0;
	}
	return this.each((typeof t == "function" ? dd : t ? ld : ud)(n, t));
}
function pd() {
	this.textContent = "";
}
function md(e) {
	return function() {
		this.textContent = e;
	};
}
function hd(e) {
	return function() {
		var t = e.apply(this, arguments);
		this.textContent = t ?? "";
	};
}
function gd(e) {
	return arguments.length ? this.each(e == null ? pd : (typeof e == "function" ? hd : md)(e)) : this.node().textContent;
}
function _d() {
	this.innerHTML = "";
}
function vd(e) {
	return function() {
		this.innerHTML = e;
	};
}
function yd(e) {
	return function() {
		var t = e.apply(this, arguments);
		this.innerHTML = t ?? "";
	};
}
function bd(e) {
	return arguments.length ? this.each(e == null ? _d : (typeof e == "function" ? yd : vd)(e)) : this.node().innerHTML;
}
function xd() {
	this.nextSibling && this.parentNode.appendChild(this);
}
function Sd() {
	return this.each(xd);
}
function Cd() {
	this.previousSibling && this.parentNode.insertBefore(this, this.parentNode.firstChild);
}
function wd() {
	return this.each(Cd);
}
function Td(e) {
	var t = typeof e == "function" ? e : eu(e);
	return this.select(function() {
		return this.appendChild(t.apply(this, arguments));
	});
}
function Ed() {
	return null;
}
function Dd(e, t) {
	var n = typeof e == "function" ? e : eu(e), r = t == null ? Ed : typeof t == "function" ? t : nu(t);
	return this.select(function() {
		return this.insertBefore(n.apply(this, arguments), r.apply(this, arguments) || null);
	});
}
function Od() {
	var e = this.parentNode;
	e && e.removeChild(this);
}
function kd() {
	return this.each(Od);
}
function Ad() {
	var e = this.cloneNode(!1), t = this.parentNode;
	return t ? t.insertBefore(e, this.nextSibling) : e;
}
function jd() {
	var e = this.cloneNode(!0), t = this.parentNode;
	return t ? t.insertBefore(e, this.nextSibling) : e;
}
function Md(e) {
	return this.select(e ? jd : Ad);
}
function Nd(e) {
	return arguments.length ? this.property("__data__", e) : this.node().__data__;
}
function Pd(e) {
	return function(t) {
		e.call(this, t, this.__data__);
	};
}
function Fd(e) {
	return e.trim().split(/^|\s+/).map(function(e) {
		var t = "", n = e.indexOf(".");
		return n >= 0 && (t = e.slice(n + 1), e = e.slice(0, n)), {
			type: e,
			name: t
		};
	});
}
function Id(e) {
	return function() {
		var t = this.__on;
		if (t) {
			for (var n = 0, r = -1, i = t.length, a; n < i; ++n) a = t[n], (!e.type || a.type === e.type) && a.name === e.name ? this.removeEventListener(a.type, a.listener, a.options) : t[++r] = a;
			++r ? t.length = r : delete this.__on;
		}
	};
}
function Ld(e, t, n) {
	return function() {
		var r = this.__on, i, a = Pd(t);
		if (r) {
			for (var o = 0, s = r.length; o < s; ++o) if ((i = r[o]).type === e.type && i.name === e.name) {
				this.removeEventListener(i.type, i.listener, i.options), this.addEventListener(i.type, i.listener = a, i.options = n), i.value = t;
				return;
			}
		}
		this.addEventListener(e.type, a, n), i = {
			type: e.type,
			name: e.name,
			value: t,
			listener: a,
			options: n
		}, r ? r.push(i) : this.__on = [i];
	};
}
function Rd(e, t, n) {
	var r = Fd(e + ""), i, a = r.length, o;
	if (arguments.length < 2) {
		var s = this.node().__on;
		if (s) {
			for (var c = 0, l = s.length, u; c < l; ++c) for (i = 0, u = s[c]; i < a; ++i) if ((o = r[i]).type === u.type && o.name === u.name) return u.value;
		}
	} else {
		for (s = t ? Ld : Id, i = 0; i < a; ++i) this.each(s(r[i], t, n));
		return this;
	}
}
function zd(e, t, n) {
	var r = Ju(e), i = r.CustomEvent;
	typeof i == "function" ? i = new i(t, n) : (i = r.document.createEvent("Event"), n ? (i.initEvent(t, n.bubbles, n.cancelable), i.detail = n.detail) : i.initEvent(t, !1, !1)), e.dispatchEvent(i);
}
function Bd(e, t) {
	return function() {
		return zd(this, e, t);
	};
}
function Vd(e, t) {
	return function() {
		return zd(this, e, t.apply(this, arguments));
	};
}
function Hd(e, t) {
	return this.each((typeof t == "function" ? Vd : Bd)(e, t));
}
function* Ud() {
	for (var e = this._groups, t = 0, n = e.length; t < n; ++t) for (var r = e[t], i = 0, a = r.length, o; i < a; ++i) (o = r[i]) && (yield o);
}
var Wd = [null];
function Gd(e, t) {
	this._groups = e, this._parents = t;
}
function Kd() {
	return new Gd([[document.documentElement]], Wd);
}
function qd() {
	return this;
}
Gd.prototype = Kd.prototype = {
	constructor: Gd,
	select: ru,
	selectAll: cu,
	selectChild: mu,
	selectChildren: vu,
	filter: yu,
	data: Du,
	enter: xu,
	exit: ku,
	join: Au,
	merge: ju,
	selection: qd,
	order: Mu,
	sort: Nu,
	call: Fu,
	nodes: Iu,
	node: Lu,
	size: Ru,
	empty: zu,
	each: Bu,
	attr: qu,
	style: Qu,
	property: rd,
	classed: fd,
	text: gd,
	html: bd,
	raise: Sd,
	lower: wd,
	append: Td,
	insert: Dd,
	remove: kd,
	clone: Md,
	datum: Nd,
	on: Rd,
	dispatch: Hd,
	[Symbol.iterator]: Ud
};
function Jd(e) {
	return typeof e == "string" ? new Gd([[document.querySelector(e)]], [document.documentElement]) : new Gd([[e]], Wd);
}
function Yd(e) {
	let t;
	for (; t = e.sourceEvent;) e = t;
	return e;
}
function Xd(e, t) {
	if (e = Yd(e), t === void 0 && (t = e.currentTarget), t) {
		var n = t.ownerSVGElement || t;
		if (n.createSVGPoint) {
			var r = n.createSVGPoint();
			return r.x = e.clientX, r.y = e.clientY, r = r.matrixTransform(t.getScreenCTM().inverse()), [r.x, r.y];
		}
		if (t.getBoundingClientRect) {
			var i = t.getBoundingClientRect();
			return [e.clientX - i.left - t.clientLeft, e.clientY - i.top - t.clientTop];
		}
	}
	return [e.pageX, e.pageY];
}
var Zd = { passive: !1 }, Qd = {
	capture: !0,
	passive: !1
};
function $d(e) {
	e.stopImmediatePropagation();
}
function ef(e) {
	e.preventDefault(), e.stopImmediatePropagation();
}
function tf(e) {
	var t = e.document.documentElement, n = Jd(e).on("dragstart.drag", ef, Qd);
	"onselectstart" in t ? n.on("selectstart.drag", ef, Qd) : (t.__noselect = t.style.MozUserSelect, t.style.MozUserSelect = "none");
}
function nf(e, t) {
	var n = e.document.documentElement, r = Jd(e).on("dragstart.drag", null);
	t && (r.on("click.drag", ef, Qd), setTimeout(function() {
		r.on("click.drag", null);
	}, 0)), "onselectstart" in n ? r.on("selectstart.drag", null) : (n.style.MozUserSelect = n.__noselect, delete n.__noselect);
}
var rf = (e) => () => e;
function af(e, { sourceEvent: t, subject: n, target: r, identifier: i, active: a, x: o, y: s, dx: c, dy: l, dispatch: u }) {
	Object.defineProperties(this, {
		type: {
			value: e,
			enumerable: !0,
			configurable: !0
		},
		sourceEvent: {
			value: t,
			enumerable: !0,
			configurable: !0
		},
		subject: {
			value: n,
			enumerable: !0,
			configurable: !0
		},
		target: {
			value: r,
			enumerable: !0,
			configurable: !0
		},
		identifier: {
			value: i,
			enumerable: !0,
			configurable: !0
		},
		active: {
			value: a,
			enumerable: !0,
			configurable: !0
		},
		x: {
			value: o,
			enumerable: !0,
			configurable: !0
		},
		y: {
			value: s,
			enumerable: !0,
			configurable: !0
		},
		dx: {
			value: c,
			enumerable: !0,
			configurable: !0
		},
		dy: {
			value: l,
			enumerable: !0,
			configurable: !0
		},
		_: { value: u }
	});
}
af.prototype.on = function() {
	var e = this._.on.apply(this._, arguments);
	return e === this._ ? this : e;
};
function of(e) {
	return !e.ctrlKey && !e.button;
}
function sf() {
	return this.parentNode;
}
function cf(e, t) {
	return t ?? {
		x: e.x,
		y: e.y
	};
}
function lf() {
	return navigator.maxTouchPoints || "ontouchstart" in this;
}
function uf() {
	var e = of, t = sf, n = cf, r = lf, i = {}, a = Wl("start", "drag", "end"), o = 0, s, c, l, u, d = 0;
	function f(e) {
		e.on("mousedown.drag", p).filter(r).on("touchstart.drag", g).on("touchmove.drag", _, Zd).on("touchend.drag touchcancel.drag", v).style("touch-action", "none").style("-webkit-tap-highlight-color", "rgba(0,0,0,0)");
	}
	function p(n, r) {
		if (!u && e.call(this, n, r)) {
			var i = y(this, t.call(this, n, r), n, r, "mouse");
			i && (Jd(n.view).on("mousemove.drag", m, Qd).on("mouseup.drag", h, Qd), tf(n.view), $d(n), l = !1, s = n.clientX, c = n.clientY, i("start", n));
		}
	}
	function m(e) {
		if (ef(e), !l) {
			var t = e.clientX - s, n = e.clientY - c;
			l = t * t + n * n > d;
		}
		i.mouse("drag", e);
	}
	function h(e) {
		Jd(e.view).on("mousemove.drag mouseup.drag", null), nf(e.view, l), ef(e), i.mouse("end", e);
	}
	function g(n, r) {
		if (e.call(this, n, r)) for (var i = n.changedTouches, a = t.call(this, n, r), o = i.length, s = 0, c; s < o; ++s) (c = y(this, a, n, r, i[s].identifier, i[s])) && ($d(n), c("start", n, i[s]));
	}
	function _(e) {
		for (var t = e.changedTouches, n = t.length, r = 0, a; r < n; ++r) (a = i[t[r].identifier]) && (ef(e), a("drag", e, t[r]));
	}
	function v(e) {
		var t = e.changedTouches, n = t.length, r, a;
		for (u && clearTimeout(u), u = setTimeout(function() {
			u = null;
		}, 500), r = 0; r < n; ++r) (a = i[t[r].identifier]) && ($d(e), a("end", e, t[r]));
	}
	function y(e, t, r, s, c, l) {
		var u = a.copy(), d = Xd(l || r, t), p, m, h;
		if ((h = n.call(e, new af("beforestart", {
			sourceEvent: r,
			target: f,
			identifier: c,
			active: o,
			x: d[0],
			y: d[1],
			dx: 0,
			dy: 0,
			dispatch: u
		}), s)) != null) return p = h.x - d[0] || 0, m = h.y - d[1] || 0, function n(r, a, l) {
			var g = d, _;
			switch (r) {
				case "start":
					i[c] = n, _ = o++;
					break;
				case "end": delete i[c], --o;
				case "drag": d = Xd(l || a, t), _ = o;
			}
			u.call(r, e, new af(r, {
				sourceEvent: a,
				subject: h,
				target: f,
				identifier: c,
				active: _,
				x: d[0] + p,
				y: d[1] + m,
				dx: d[0] - g[0],
				dy: d[1] - g[1],
				dispatch: u
			}), s);
		};
	}
	return f.filter = function(t) {
		return arguments.length ? (e = typeof t == "function" ? t : rf(!!t), f) : e;
	}, f.container = function(e) {
		return arguments.length ? (t = typeof e == "function" ? e : rf(e), f) : t;
	}, f.subject = function(e) {
		return arguments.length ? (n = typeof e == "function" ? e : rf(e), f) : n;
	}, f.touchable = function(e) {
		return arguments.length ? (r = typeof e == "function" ? e : rf(!!e), f) : r;
	}, f.on = function() {
		var e = a.on.apply(a, arguments);
		return e === a ? f : e;
	}, f.clickDistance = function(e) {
		return arguments.length ? (d = (e = +e) * e, f) : Math.sqrt(d);
	}, f;
}
function df(e, t, n) {
	e.prototype = t.prototype = n, n.constructor = e;
}
function ff(e, t) {
	var n = Object.create(e.prototype);
	for (var r in t) n[r] = t[r];
	return n;
}
function pf() {}
var mf = .7, hf = 1 / mf, gf = "\\s*([+-]?\\d+)\\s*", _f = "\\s*([+-]?(?:\\d*\\.)?\\d+(?:[eE][+-]?\\d+)?)\\s*", vf = "\\s*([+-]?(?:\\d*\\.)?\\d+(?:[eE][+-]?\\d+)?)%\\s*", yf = /^#([0-9a-f]{3,8})$/, bf = RegExp(`^rgb\\(${gf},${gf},${gf}\\)$`), xf = RegExp(`^rgb\\(${vf},${vf},${vf}\\)$`), Sf = RegExp(`^rgba\\(${gf},${gf},${gf},${_f}\\)$`), Cf = RegExp(`^rgba\\(${vf},${vf},${vf},${_f}\\)$`), wf = RegExp(`^hsl\\(${_f},${vf},${vf}\\)$`), Tf = RegExp(`^hsla\\(${_f},${vf},${vf},${_f}\\)$`), Ef = {
	aliceblue: 15792383,
	antiquewhite: 16444375,
	aqua: 65535,
	aquamarine: 8388564,
	azure: 15794175,
	beige: 16119260,
	bisque: 16770244,
	black: 0,
	blanchedalmond: 16772045,
	blue: 255,
	blueviolet: 9055202,
	brown: 10824234,
	burlywood: 14596231,
	cadetblue: 6266528,
	chartreuse: 8388352,
	chocolate: 13789470,
	coral: 16744272,
	cornflowerblue: 6591981,
	cornsilk: 16775388,
	crimson: 14423100,
	cyan: 65535,
	darkblue: 139,
	darkcyan: 35723,
	darkgoldenrod: 12092939,
	darkgray: 11119017,
	darkgreen: 25600,
	darkgrey: 11119017,
	darkkhaki: 12433259,
	darkmagenta: 9109643,
	darkolivegreen: 5597999,
	darkorange: 16747520,
	darkorchid: 10040012,
	darkred: 9109504,
	darksalmon: 15308410,
	darkseagreen: 9419919,
	darkslateblue: 4734347,
	darkslategray: 3100495,
	darkslategrey: 3100495,
	darkturquoise: 52945,
	darkviolet: 9699539,
	deeppink: 16716947,
	deepskyblue: 49151,
	dimgray: 6908265,
	dimgrey: 6908265,
	dodgerblue: 2003199,
	firebrick: 11674146,
	floralwhite: 16775920,
	forestgreen: 2263842,
	fuchsia: 16711935,
	gainsboro: 14474460,
	ghostwhite: 16316671,
	gold: 16766720,
	goldenrod: 14329120,
	gray: 8421504,
	green: 32768,
	greenyellow: 11403055,
	grey: 8421504,
	honeydew: 15794160,
	hotpink: 16738740,
	indianred: 13458524,
	indigo: 4915330,
	ivory: 16777200,
	khaki: 15787660,
	lavender: 15132410,
	lavenderblush: 16773365,
	lawngreen: 8190976,
	lemonchiffon: 16775885,
	lightblue: 11393254,
	lightcoral: 15761536,
	lightcyan: 14745599,
	lightgoldenrodyellow: 16448210,
	lightgray: 13882323,
	lightgreen: 9498256,
	lightgrey: 13882323,
	lightpink: 16758465,
	lightsalmon: 16752762,
	lightseagreen: 2142890,
	lightskyblue: 8900346,
	lightslategray: 7833753,
	lightslategrey: 7833753,
	lightsteelblue: 11584734,
	lightyellow: 16777184,
	lime: 65280,
	limegreen: 3329330,
	linen: 16445670,
	magenta: 16711935,
	maroon: 8388608,
	mediumaquamarine: 6737322,
	mediumblue: 205,
	mediumorchid: 12211667,
	mediumpurple: 9662683,
	mediumseagreen: 3978097,
	mediumslateblue: 8087790,
	mediumspringgreen: 64154,
	mediumturquoise: 4772300,
	mediumvioletred: 13047173,
	midnightblue: 1644912,
	mintcream: 16121850,
	mistyrose: 16770273,
	moccasin: 16770229,
	navajowhite: 16768685,
	navy: 128,
	oldlace: 16643558,
	olive: 8421376,
	olivedrab: 7048739,
	orange: 16753920,
	orangered: 16729344,
	orchid: 14315734,
	palegoldenrod: 15657130,
	palegreen: 10025880,
	paleturquoise: 11529966,
	palevioletred: 14381203,
	papayawhip: 16773077,
	peachpuff: 16767673,
	peru: 13468991,
	pink: 16761035,
	plum: 14524637,
	powderblue: 11591910,
	purple: 8388736,
	rebeccapurple: 6697881,
	red: 16711680,
	rosybrown: 12357519,
	royalblue: 4286945,
	saddlebrown: 9127187,
	salmon: 16416882,
	sandybrown: 16032864,
	seagreen: 3050327,
	seashell: 16774638,
	sienna: 10506797,
	silver: 12632256,
	skyblue: 8900331,
	slateblue: 6970061,
	slategray: 7372944,
	slategrey: 7372944,
	snow: 16775930,
	springgreen: 65407,
	steelblue: 4620980,
	tan: 13808780,
	teal: 32896,
	thistle: 14204888,
	tomato: 16737095,
	turquoise: 4251856,
	violet: 15631086,
	wheat: 16113331,
	white: 16777215,
	whitesmoke: 16119285,
	yellow: 16776960,
	yellowgreen: 10145074
};
df(pf, jf, {
	copy(e) {
		return Object.assign(new this.constructor(), this, e);
	},
	displayable() {
		return this.rgb().displayable();
	},
	hex: Df,
	formatHex: Df,
	formatHex8: Of,
	formatHsl: kf,
	formatRgb: Af,
	toString: Af
});
function Df() {
	return this.rgb().formatHex();
}
function Of() {
	return this.rgb().formatHex8();
}
function kf() {
	return Wf(this).formatHsl();
}
function Af() {
	return this.rgb().formatRgb();
}
function jf(e) {
	var t, n;
	return e = (e + "").trim().toLowerCase(), (t = yf.exec(e)) ? (n = t[1].length, t = parseInt(t[1], 16), n === 6 ? Mf(t) : n === 3 ? new If(t >> 8 & 15 | t >> 4 & 240, t >> 4 & 15 | t & 240, (t & 15) << 4 | t & 15, 1) : n === 8 ? Nf(t >> 24 & 255, t >> 16 & 255, t >> 8 & 255, (t & 255) / 255) : n === 4 ? Nf(t >> 12 & 15 | t >> 8 & 240, t >> 8 & 15 | t >> 4 & 240, t >> 4 & 15 | t & 240, ((t & 15) << 4 | t & 15) / 255) : null) : (t = bf.exec(e)) ? new If(t[1], t[2], t[3], 1) : (t = xf.exec(e)) ? new If(t[1] * 255 / 100, t[2] * 255 / 100, t[3] * 255 / 100, 1) : (t = Sf.exec(e)) ? Nf(t[1], t[2], t[3], t[4]) : (t = Cf.exec(e)) ? Nf(t[1] * 255 / 100, t[2] * 255 / 100, t[3] * 255 / 100, t[4]) : (t = wf.exec(e)) ? Uf(t[1], t[2] / 100, t[3] / 100, 1) : (t = Tf.exec(e)) ? Uf(t[1], t[2] / 100, t[3] / 100, t[4]) : Ef.hasOwnProperty(e) ? Mf(Ef[e]) : e === "transparent" ? new If(NaN, NaN, NaN, 0) : null;
}
function Mf(e) {
	return new If(e >> 16 & 255, e >> 8 & 255, e & 255, 1);
}
function Nf(e, t, n, r) {
	return r <= 0 && (e = t = n = NaN), new If(e, t, n, r);
}
function Pf(e) {
	return e instanceof pf || (e = jf(e)), e ? (e = e.rgb(), new If(e.r, e.g, e.b, e.opacity)) : new If();
}
function Ff(e, t, n, r) {
	return arguments.length === 1 ? Pf(e) : new If(e, t, n, r ?? 1);
}
function If(e, t, n, r) {
	this.r = +e, this.g = +t, this.b = +n, this.opacity = +r;
}
df(If, Ff, ff(pf, {
	brighter(e) {
		return e = e == null ? hf : hf ** +e, new If(this.r * e, this.g * e, this.b * e, this.opacity);
	},
	darker(e) {
		return e = e == null ? mf : mf ** +e, new If(this.r * e, this.g * e, this.b * e, this.opacity);
	},
	rgb() {
		return this;
	},
	clamp() {
		return new If(Vf(this.r), Vf(this.g), Vf(this.b), Bf(this.opacity));
	},
	displayable() {
		return -.5 <= this.r && this.r < 255.5 && -.5 <= this.g && this.g < 255.5 && -.5 <= this.b && this.b < 255.5 && 0 <= this.opacity && this.opacity <= 1;
	},
	hex: Lf,
	formatHex: Lf,
	formatHex8: Rf,
	formatRgb: zf,
	toString: zf
}));
function Lf() {
	return `#${Hf(this.r)}${Hf(this.g)}${Hf(this.b)}`;
}
function Rf() {
	return `#${Hf(this.r)}${Hf(this.g)}${Hf(this.b)}${Hf((isNaN(this.opacity) ? 1 : this.opacity) * 255)}`;
}
function zf() {
	let e = Bf(this.opacity);
	return `${e === 1 ? "rgb(" : "rgba("}${Vf(this.r)}, ${Vf(this.g)}, ${Vf(this.b)}${e === 1 ? ")" : `, ${e})`}`;
}
function Bf(e) {
	return isNaN(e) ? 1 : Math.max(0, Math.min(1, e));
}
function Vf(e) {
	return Math.max(0, Math.min(255, Math.round(e) || 0));
}
function Hf(e) {
	return e = Vf(e), (e < 16 ? "0" : "") + e.toString(16);
}
function Uf(e, t, n, r) {
	return r <= 0 ? e = t = n = NaN : n <= 0 || n >= 1 ? e = t = NaN : t <= 0 && (e = NaN), new Kf(e, t, n, r);
}
function Wf(e) {
	if (e instanceof Kf) return new Kf(e.h, e.s, e.l, e.opacity);
	if (e instanceof pf || (e = jf(e)), !e) return new Kf();
	if (e instanceof Kf) return e;
	e = e.rgb();
	var t = e.r / 255, n = e.g / 255, r = e.b / 255, i = Math.min(t, n, r), a = Math.max(t, n, r), o = NaN, s = a - i, c = (a + i) / 2;
	return s ? (o = t === a ? (n - r) / s + (n < r) * 6 : n === a ? (r - t) / s + 2 : (t - n) / s + 4, s /= c < .5 ? a + i : 2 - a - i, o *= 60) : s = c > 0 && c < 1 ? 0 : o, new Kf(o, s, c, e.opacity);
}
function Gf(e, t, n, r) {
	return arguments.length === 1 ? Wf(e) : new Kf(e, t, n, r ?? 1);
}
function Kf(e, t, n, r) {
	this.h = +e, this.s = +t, this.l = +n, this.opacity = +r;
}
df(Kf, Gf, ff(pf, {
	brighter(e) {
		return e = e == null ? hf : hf ** +e, new Kf(this.h, this.s, this.l * e, this.opacity);
	},
	darker(e) {
		return e = e == null ? mf : mf ** +e, new Kf(this.h, this.s, this.l * e, this.opacity);
	},
	rgb() {
		var e = this.h % 360 + (this.h < 0) * 360, t = isNaN(e) || isNaN(this.s) ? 0 : this.s, n = this.l, r = n + (n < .5 ? n : 1 - n) * t, i = 2 * n - r;
		return new If(Yf(e >= 240 ? e - 240 : e + 120, i, r), Yf(e, i, r), Yf(e < 120 ? e + 240 : e - 120, i, r), this.opacity);
	},
	clamp() {
		return new Kf(qf(this.h), Jf(this.s), Jf(this.l), Bf(this.opacity));
	},
	displayable() {
		return (0 <= this.s && this.s <= 1 || isNaN(this.s)) && 0 <= this.l && this.l <= 1 && 0 <= this.opacity && this.opacity <= 1;
	},
	formatHsl() {
		let e = Bf(this.opacity);
		return `${e === 1 ? "hsl(" : "hsla("}${qf(this.h)}, ${Jf(this.s) * 100}%, ${Jf(this.l) * 100}%${e === 1 ? ")" : `, ${e})`}`;
	}
}));
function qf(e) {
	return e = (e || 0) % 360, e < 0 ? e + 360 : e;
}
function Jf(e) {
	return Math.max(0, Math.min(1, e || 0));
}
function Yf(e, t, n) {
	return (e < 60 ? t + (n - t) * e / 60 : e < 180 ? n : e < 240 ? t + (n - t) * (240 - e) / 60 : t) * 255;
}
var Xf = (e) => () => e;
function Zf(e, t) {
	return function(n) {
		return e + n * t;
	};
}
function Qf(e, t, n) {
	return e **= +n, t = t ** +n - e, n = 1 / n, function(r) {
		return (e + r * t) ** +n;
	};
}
function $f(e) {
	return (e = +e) == 1 ? ep : function(t, n) {
		return n - t ? Qf(t, n, e) : Xf(isNaN(t) ? n : t);
	};
}
function ep(e, t) {
	var n = t - e;
	return n ? Zf(e, n) : Xf(isNaN(e) ? t : e);
}
var tp = (function e(t) {
	var n = $f(t);
	function r(e, t) {
		var r = n((e = Ff(e)).r, (t = Ff(t)).r), i = n(e.g, t.g), a = n(e.b, t.b), o = ep(e.opacity, t.opacity);
		return function(t) {
			return e.r = r(t), e.g = i(t), e.b = a(t), e.opacity = o(t), e + "";
		};
	}
	return r.gamma = e, r;
})(1);
function np(e, t) {
	t ||= [];
	var n = e ? Math.min(t.length, e.length) : 0, r = t.slice(), i;
	return function(a) {
		for (i = 0; i < n; ++i) r[i] = e[i] * (1 - a) + t[i] * a;
		return r;
	};
}
function rp(e) {
	return ArrayBuffer.isView(e) && !(e instanceof DataView);
}
function ip(e, t) {
	for (var n = t ? t.length : 0, r = e ? Math.min(n, e.length) : 0, i = Array(r), a = Array(n), o = 0; o < r; ++o) i[o] = pp(e[o], t[o]);
	for (; o < n; ++o) a[o] = t[o];
	return function(e) {
		for (o = 0; o < r; ++o) a[o] = i[o](e);
		return a;
	};
}
function ap(e, t) {
	var n = /* @__PURE__ */ new Date();
	return e = +e, t = +t, function(r) {
		return n.setTime(e * (1 - r) + t * r), n;
	};
}
function op(e, t) {
	return e = +e, t = +t, function(n) {
		return e * (1 - n) + t * n;
	};
}
function sp(e, t) {
	var n = {}, r = {}, i;
	for (i in (typeof e != "object" || !e) && (e = {}), (typeof t != "object" || !t) && (t = {}), t) i in e ? n[i] = pp(e[i], t[i]) : r[i] = t[i];
	return function(e) {
		for (i in n) r[i] = n[i](e);
		return r;
	};
}
var cp = /[-+]?(?:\d+\.?\d*|\.?\d+)(?:[eE][-+]?\d+)?/g, lp = new RegExp(cp.source, "g");
function up(e) {
	return function() {
		return e;
	};
}
function dp(e) {
	return function(t) {
		return e(t) + "";
	};
}
function fp(e, t) {
	var n = cp.lastIndex = lp.lastIndex = 0, r, i, a, o = -1, s = [], c = [];
	for (e += "", t += ""; (r = cp.exec(e)) && (i = lp.exec(t));) (a = i.index) > n && (a = t.slice(n, a), s[o] ? s[o] += a : s[++o] = a), (r = r[0]) === (i = i[0]) ? s[o] ? s[o] += i : s[++o] = i : (s[++o] = null, c.push({
		i: o,
		x: op(r, i)
	})), n = lp.lastIndex;
	return n < t.length && (a = t.slice(n), s[o] ? s[o] += a : s[++o] = a), s.length < 2 ? c[0] ? dp(c[0].x) : up(t) : (t = c.length, function(e) {
		for (var n = 0, r; n < t; ++n) s[(r = c[n]).i] = r.x(e);
		return s.join("");
	});
}
function pp(e, t) {
	var n = typeof t, r;
	return t == null || n === "boolean" ? Xf(t) : (n === "number" ? op : n === "string" ? (r = jf(t)) ? (t = r, tp) : fp : t instanceof jf ? tp : t instanceof Date ? ap : rp(t) ? np : Array.isArray(t) ? ip : typeof t.valueOf != "function" && typeof t.toString != "function" || isNaN(t) ? sp : op)(e, t);
}
function mp(e, t) {
	return e = +e, t = +t, function(n) {
		return Math.round(e * (1 - n) + t * n);
	};
}
var hp = 180 / Math.PI, gp = {
	translateX: 0,
	translateY: 0,
	rotate: 0,
	skewX: 0,
	scaleX: 1,
	scaleY: 1
};
function _p(e, t, n, r, i, a) {
	var o, s, c;
	return (o = Math.sqrt(e * e + t * t)) && (e /= o, t /= o), (c = e * n + t * r) && (n -= e * c, r -= t * c), (s = Math.sqrt(n * n + r * r)) && (n /= s, r /= s, c /= s), e * r < t * n && (e = -e, t = -t, c = -c, o = -o), {
		translateX: i,
		translateY: a,
		rotate: Math.atan2(t, e) * hp,
		skewX: Math.atan(c) * hp,
		scaleX: o,
		scaleY: s
	};
}
var vp;
function yp(e) {
	let t = new (typeof DOMMatrix == "function" ? DOMMatrix : WebKitCSSMatrix)(e + "");
	return t.isIdentity ? gp : _p(t.a, t.b, t.c, t.d, t.e, t.f);
}
function bp(e) {
	return e == null || (vp ||= document.createElementNS("http://www.w3.org/2000/svg", "g"), vp.setAttribute("transform", e), !(e = vp.transform.baseVal.consolidate())) ? gp : (e = e.matrix, _p(e.a, e.b, e.c, e.d, e.e, e.f));
}
function xp(e, t, n, r) {
	function i(e) {
		return e.length ? e.pop() + " " : "";
	}
	function a(e, r, i, a, o, s) {
		if (e !== i || r !== a) {
			var c = o.push("translate(", null, t, null, n);
			s.push({
				i: c - 4,
				x: op(e, i)
			}, {
				i: c - 2,
				x: op(r, a)
			});
		} else (i || a) && o.push("translate(" + i + t + a + n);
	}
	function o(e, t, n, a) {
		e === t ? t && n.push(i(n) + "rotate(" + t + r) : (e - t > 180 ? t += 360 : t - e > 180 && (e += 360), a.push({
			i: n.push(i(n) + "rotate(", null, r) - 2,
			x: op(e, t)
		}));
	}
	function s(e, t, n, a) {
		e === t ? t && n.push(i(n) + "skewX(" + t + r) : a.push({
			i: n.push(i(n) + "skewX(", null, r) - 2,
			x: op(e, t)
		});
	}
	function c(e, t, n, r, a, o) {
		if (e !== n || t !== r) {
			var s = a.push(i(a) + "scale(", null, ",", null, ")");
			o.push({
				i: s - 4,
				x: op(e, n)
			}, {
				i: s - 2,
				x: op(t, r)
			});
		} else (n !== 1 || r !== 1) && a.push(i(a) + "scale(" + n + "," + r + ")");
	}
	return function(t, n) {
		var r = [], i = [];
		return t = e(t), n = e(n), a(t.translateX, t.translateY, n.translateX, n.translateY, r, i), o(t.rotate, n.rotate, r, i), s(t.skewX, n.skewX, r, i), c(t.scaleX, t.scaleY, n.scaleX, n.scaleY, r, i), t = n = null, function(e) {
			for (var t = -1, n = i.length, a; ++t < n;) r[(a = i[t]).i] = a.x(e);
			return r.join("");
		};
	};
}
var Sp = xp(yp, "px, ", "px)", "deg)"), Cp = xp(bp, ", ", ")", ")"), wp = 0, Tp = 0, Ep = 0, Dp = 1e3, Op, kp, Ap = 0, jp = 0, Mp = 0, Np = typeof performance == "object" && performance.now ? performance : Date, Pp = typeof window == "object" && window.requestAnimationFrame ? window.requestAnimationFrame.bind(window) : function(e) {
	setTimeout(e, 17);
};
function Fp() {
	return jp ||= (Pp(Ip), Np.now() + Mp);
}
function Ip() {
	jp = 0;
}
function Lp() {
	this._call = this._time = this._next = null;
}
Lp.prototype = Rp.prototype = {
	constructor: Lp,
	restart: function(e, t, n) {
		if (typeof e != "function") throw TypeError("callback is not a function");
		n = (n == null ? Fp() : +n) + (t == null ? 0 : +t), !this._next && kp !== this && (kp ? kp._next = this : Op = this, kp = this), this._call = e, this._time = n, Up();
	},
	stop: function() {
		this._call && (this._call = null, this._time = Infinity, Up());
	}
};
function Rp(e, t, n) {
	var r = new Lp();
	return r.restart(e, t, n), r;
}
function zp() {
	Fp(), ++wp;
	for (var e = Op, t; e;) (t = jp - e._time) >= 0 && e._call.call(void 0, t), e = e._next;
	--wp;
}
function Bp() {
	jp = (Ap = Np.now()) + Mp, wp = Tp = 0;
	try {
		zp();
	} finally {
		wp = 0, Hp(), jp = 0;
	}
}
function Vp() {
	var e = Np.now(), t = e - Ap;
	t > Dp && (Mp -= t, Ap = e);
}
function Hp() {
	for (var e, t = Op, n, r = Infinity; t;) t._call ? (r > t._time && (r = t._time), e = t, t = t._next) : (n = t._next, t._next = null, t = e ? e._next = n : Op = n);
	kp = e, Up(r);
}
function Up(e) {
	wp || (Tp &&= clearTimeout(Tp), e - jp > 24 ? (e < Infinity && (Tp = setTimeout(Bp, e - Np.now() - Mp)), Ep &&= clearInterval(Ep)) : (Ep ||= (Ap = Np.now(), setInterval(Vp, Dp)), wp = 1, Pp(Bp)));
}
function Wp(e, t, n) {
	var r = new Lp();
	return t = t == null ? 0 : +t, r.restart((n) => {
		r.stop(), e(n + t);
	}, t, n), r;
}
var Gp = Wl("start", "end", "cancel", "interrupt"), Kp = [], qp = 0, Jp = 1, Yp = 2, Xp = 3, Zp = 4, Qp = 5, $p = 6;
function em(e, t, n, r, i, a) {
	var o = e.__transition;
	if (!o) e.__transition = {};
	else if (n in o) return;
	im(e, n, {
		name: t,
		index: r,
		group: i,
		on: Gp,
		tween: Kp,
		time: a.time,
		delay: a.delay,
		duration: a.duration,
		ease: a.ease,
		timer: null,
		state: qp
	});
}
function tm(e, t) {
	var n = rm(e, t);
	if (n.state > qp) throw Error("too late; already scheduled");
	return n;
}
function nm(e, t) {
	var n = rm(e, t);
	if (n.state > Xp) throw Error("too late; already running");
	return n;
}
function rm(e, t) {
	var n = e.__transition;
	if (!n || !(n = n[t])) throw Error("transition not found");
	return n;
}
function im(e, t, n) {
	var r = e.__transition, i;
	r[t] = n, n.timer = Rp(a, 0, n.time);
	function a(e) {
		n.state = Jp, n.timer.restart(o, n.delay, n.time), n.delay <= e && o(e - n.delay);
	}
	function o(a) {
		var l, u, d, f;
		if (n.state !== Jp) return c();
		for (l in r) if (f = r[l], f.name === n.name) {
			if (f.state === Xp) return Wp(o);
			f.state === Zp ? (f.state = $p, f.timer.stop(), f.on.call("interrupt", e, e.__data__, f.index, f.group), delete r[l]) : +l < t && (f.state = $p, f.timer.stop(), f.on.call("cancel", e, e.__data__, f.index, f.group), delete r[l]);
		}
		if (Wp(function() {
			n.state === Xp && (n.state = Zp, n.timer.restart(s, n.delay, n.time), s(a));
		}), n.state = Yp, n.on.call("start", e, e.__data__, n.index, n.group), n.state === Yp) {
			for (n.state = Xp, i = Array(d = n.tween.length), l = 0, u = -1; l < d; ++l) (f = n.tween[l].value.call(e, e.__data__, n.index, n.group)) && (i[++u] = f);
			i.length = u + 1;
		}
	}
	function s(t) {
		for (var r = t < n.duration ? n.ease.call(null, t / n.duration) : (n.timer.restart(c), n.state = Qp, 1), a = -1, o = i.length; ++a < o;) i[a].call(e, r);
		n.state === Qp && (n.on.call("end", e, e.__data__, n.index, n.group), c());
	}
	function c() {
		for (var i in n.state = $p, n.timer.stop(), delete r[t], r) return;
		delete e.__transition;
	}
}
function am(e, t) {
	var n = e.__transition, r, i, a = !0, o;
	if (n) {
		for (o in t = t == null ? null : t + "", n) (r = n[o]).name === t ? (i = r.state > Yp && r.state < Qp, r.state = $p, r.timer.stop(), r.on.call(i ? "interrupt" : "cancel", e, e.__data__, r.index, r.group), delete n[o]) : a = !1;
		a && delete e.__transition;
	}
}
function om(e) {
	return this.each(function() {
		am(this, e);
	});
}
function sm(e, t) {
	var n, r;
	return function() {
		var i = nm(this, e), a = i.tween;
		if (a !== n) {
			r = n = a;
			for (var o = 0, s = r.length; o < s; ++o) if (r[o].name === t) {
				r = r.slice(), r.splice(o, 1);
				break;
			}
		}
		i.tween = r;
	};
}
function cm(e, t, n) {
	var r, i;
	if (typeof n != "function") throw Error();
	return function() {
		var a = nm(this, e), o = a.tween;
		if (o !== r) {
			i = (r = o).slice();
			for (var s = {
				name: t,
				value: n
			}, c = 0, l = i.length; c < l; ++c) if (i[c].name === t) {
				i[c] = s;
				break;
			}
			c === l && i.push(s);
		}
		a.tween = i;
	};
}
function lm(e, t) {
	var n = this._id;
	if (e += "", arguments.length < 2) {
		for (var r = rm(this.node(), n).tween, i = 0, a = r.length, o; i < a; ++i) if ((o = r[i]).name === e) return o.value;
		return null;
	}
	return this.each((t == null ? sm : cm)(n, e, t));
}
function um(e, t, n) {
	var r = e._id;
	return e.each(function() {
		var e = nm(this, r);
		(e.value ||= {})[t] = n.apply(this, arguments);
	}), function(e) {
		return rm(e, r).value[t];
	};
}
function dm(e, t) {
	var n;
	return (typeof t == "number" ? op : t instanceof jf ? tp : (n = jf(t)) ? (t = n, tp) : fp)(e, t);
}
function fm(e) {
	return function() {
		this.removeAttribute(e);
	};
}
function pm(e) {
	return function() {
		this.removeAttributeNS(e.space, e.local);
	};
}
function mm(e, t, n) {
	var r, i = n + "", a;
	return function() {
		var o = this.getAttribute(e);
		return o === i ? null : o === r ? a : a = t(r = o, n);
	};
}
function hm(e, t, n) {
	var r, i = n + "", a;
	return function() {
		var o = this.getAttributeNS(e.space, e.local);
		return o === i ? null : o === r ? a : a = t(r = o, n);
	};
}
function gm(e, t, n) {
	var r, i, a;
	return function() {
		var o, s = n(this), c;
		return s == null ? void this.removeAttribute(e) : (o = this.getAttribute(e), c = s + "", o === c ? null : o === r && c === i ? a : (i = c, a = t(r = o, s)));
	};
}
function _m(e, t, n) {
	var r, i, a;
	return function() {
		var o, s = n(this), c;
		return s == null ? void this.removeAttributeNS(e.space, e.local) : (o = this.getAttributeNS(e.space, e.local), c = s + "", o === c ? null : o === r && c === i ? a : (i = c, a = t(r = o, s)));
	};
}
function vm(e, t) {
	var n = Zl(e), r = n === "transform" ? Cp : dm;
	return this.attrTween(e, typeof t == "function" ? (n.local ? _m : gm)(n, r, um(this, "attr." + e, t)) : t == null ? (n.local ? pm : fm)(n) : (n.local ? hm : mm)(n, r, t));
}
function ym(e, t) {
	return function(n) {
		this.setAttribute(e, t.call(this, n));
	};
}
function bm(e, t) {
	return function(n) {
		this.setAttributeNS(e.space, e.local, t.call(this, n));
	};
}
function xm(e, t) {
	var n, r;
	function i() {
		var i = t.apply(this, arguments);
		return i !== r && (n = (r = i) && bm(e, i)), n;
	}
	return i._value = t, i;
}
function Sm(e, t) {
	var n, r;
	function i() {
		var i = t.apply(this, arguments);
		return i !== r && (n = (r = i) && ym(e, i)), n;
	}
	return i._value = t, i;
}
function Cm(e, t) {
	var n = "attr." + e;
	if (arguments.length < 2) return (n = this.tween(n)) && n._value;
	if (t == null) return this.tween(n, null);
	if (typeof t != "function") throw Error();
	var r = Zl(e);
	return this.tween(n, (r.local ? xm : Sm)(r, t));
}
function wm(e, t) {
	return function() {
		tm(this, e).delay = +t.apply(this, arguments);
	};
}
function Tm(e, t) {
	return t = +t, function() {
		tm(this, e).delay = t;
	};
}
function Em(e) {
	var t = this._id;
	return arguments.length ? this.each((typeof e == "function" ? wm : Tm)(t, e)) : rm(this.node(), t).delay;
}
function Dm(e, t) {
	return function() {
		nm(this, e).duration = +t.apply(this, arguments);
	};
}
function Om(e, t) {
	return t = +t, function() {
		nm(this, e).duration = t;
	};
}
function km(e) {
	var t = this._id;
	return arguments.length ? this.each((typeof e == "function" ? Dm : Om)(t, e)) : rm(this.node(), t).duration;
}
function Am(e, t) {
	if (typeof t != "function") throw Error();
	return function() {
		nm(this, e).ease = t;
	};
}
function jm(e) {
	var t = this._id;
	return arguments.length ? this.each(Am(t, e)) : rm(this.node(), t).ease;
}
function Mm(e, t) {
	return function() {
		var n = t.apply(this, arguments);
		if (typeof n != "function") throw Error();
		nm(this, e).ease = n;
	};
}
function Nm(e) {
	if (typeof e != "function") throw Error();
	return this.each(Mm(this._id, e));
}
function Pm(e) {
	typeof e != "function" && (e = lu(e));
	for (var t = this._groups, n = t.length, r = Array(n), i = 0; i < n; ++i) for (var a = t[i], o = a.length, s = r[i] = [], c, l = 0; l < o; ++l) (c = a[l]) && e.call(c, c.__data__, l, a) && s.push(c);
	return new lh(r, this._parents, this._name, this._id);
}
function Fm(e) {
	if (e._id !== this._id) throw Error();
	for (var t = this._groups, n = e._groups, r = t.length, i = n.length, a = Math.min(r, i), o = Array(r), s = 0; s < a; ++s) for (var c = t[s], l = n[s], u = c.length, d = o[s] = Array(u), f, p = 0; p < u; ++p) (f = c[p] || l[p]) && (d[p] = f);
	for (; s < r; ++s) o[s] = t[s];
	return new lh(o, this._parents, this._name, this._id);
}
function Im(e) {
	return (e + "").trim().split(/^|\s+/).every(function(e) {
		var t = e.indexOf(".");
		return t >= 0 && (e = e.slice(0, t)), !e || e === "start";
	});
}
function Lm(e, t, n) {
	var r, i, a = Im(t) ? tm : nm;
	return function() {
		var o = a(this, e), s = o.on;
		s !== r && (i = (r = s).copy()).on(t, n), o.on = i;
	};
}
function Rm(e, t) {
	var n = this._id;
	return arguments.length < 2 ? rm(this.node(), n).on.on(e) : this.each(Lm(n, e, t));
}
function zm(e) {
	return function() {
		var t = this.parentNode;
		for (var n in this.__transition) if (+n !== e) return;
		t && t.removeChild(this);
	};
}
function Bm() {
	return this.on("end.remove", zm(this._id));
}
function Vm(e) {
	var t = this._name, n = this._id;
	typeof e != "function" && (e = nu(e));
	for (var r = this._groups, i = r.length, a = Array(i), o = 0; o < i; ++o) for (var s = r[o], c = s.length, l = a[o] = Array(c), u, d, f = 0; f < c; ++f) (u = s[f]) && (d = e.call(u, u.__data__, f, s)) && ("__data__" in u && (d.__data__ = u.__data__), l[f] = d, em(l[f], t, n, f, l, rm(u, n)));
	return new lh(a, this._parents, t, n);
}
function Hm(e) {
	var t = this._name, n = this._id;
	typeof e != "function" && (e = ou(e));
	for (var r = this._groups, i = r.length, a = [], o = [], s = 0; s < i; ++s) for (var c = r[s], l = c.length, u, d = 0; d < l; ++d) if (u = c[d]) {
		for (var f = e.call(u, u.__data__, d, c), p, m = rm(u, n), h = 0, g = f.length; h < g; ++h) (p = f[h]) && em(p, t, n, h, f, m);
		a.push(f), o.push(u);
	}
	return new lh(a, o, t, n);
}
var Um = Kd.prototype.constructor;
function Wm() {
	return new Um(this._groups, this._parents);
}
function Gm(e, t) {
	var n, r, i;
	return function() {
		var a = $u(this, e), o = (this.style.removeProperty(e), $u(this, e));
		return a === o ? null : a === n && o === r ? i : i = t(n = a, r = o);
	};
}
function Km(e) {
	return function() {
		this.style.removeProperty(e);
	};
}
function qm(e, t, n) {
	var r, i = n + "", a;
	return function() {
		var o = $u(this, e);
		return o === i ? null : o === r ? a : a = t(r = o, n);
	};
}
function Jm(e, t, n) {
	var r, i, a;
	return function() {
		var o = $u(this, e), s = n(this), c = s + "";
		return s ?? (c = s = (this.style.removeProperty(e), $u(this, e))), o === c ? null : o === r && c === i ? a : (i = c, a = t(r = o, s));
	};
}
function Ym(e, t) {
	var n, r, i, a = "style." + t, o = "end." + a, s;
	return function() {
		var c = nm(this, e), l = c.on, u = c.value[a] == null ? s ||= Km(t) : void 0;
		(l !== n || i !== u) && (r = (n = l).copy()).on(o, i = u), c.on = r;
	};
}
function Xm(e, t, n) {
	var r = (e += "") == "transform" ? Sp : dm;
	return t == null ? this.styleTween(e, Gm(e, r)).on("end.style." + e, Km(e)) : typeof t == "function" ? this.styleTween(e, Jm(e, r, um(this, "style." + e, t))).each(Ym(this._id, e)) : this.styleTween(e, qm(e, r, t), n).on("end.style." + e, null);
}
function Zm(e, t, n) {
	return function(r) {
		this.style.setProperty(e, t.call(this, r), n);
	};
}
function Qm(e, t, n) {
	var r, i;
	function a() {
		var a = t.apply(this, arguments);
		return a !== i && (r = (i = a) && Zm(e, a, n)), r;
	}
	return a._value = t, a;
}
function $m(e, t, n) {
	var r = "style." + (e += "");
	if (arguments.length < 2) return (r = this.tween(r)) && r._value;
	if (t == null) return this.tween(r, null);
	if (typeof t != "function") throw Error();
	return this.tween(r, Qm(e, t, n ?? ""));
}
function eh(e) {
	return function() {
		this.textContent = e;
	};
}
function th(e) {
	return function() {
		var t = e(this);
		this.textContent = t ?? "";
	};
}
function nh(e) {
	return this.tween("text", typeof e == "function" ? th(um(this, "text", e)) : eh(e == null ? "" : e + ""));
}
function rh(e) {
	return function(t) {
		this.textContent = e.call(this, t);
	};
}
function ih(e) {
	var t, n;
	function r() {
		var r = e.apply(this, arguments);
		return r !== n && (t = (n = r) && rh(r)), t;
	}
	return r._value = e, r;
}
function ah(e) {
	var t = "text";
	if (arguments.length < 1) return (t = this.tween(t)) && t._value;
	if (e == null) return this.tween(t, null);
	if (typeof e != "function") throw Error();
	return this.tween(t, ih(e));
}
function oh() {
	for (var e = this._name, t = this._id, n = uh(), r = this._groups, i = r.length, a = 0; a < i; ++a) for (var o = r[a], s = o.length, c, l = 0; l < s; ++l) if (c = o[l]) {
		var u = rm(c, t);
		em(c, e, n, l, o, {
			time: u.time + u.delay + u.duration,
			delay: 0,
			duration: u.duration,
			ease: u.ease
		});
	}
	return new lh(r, this._parents, e, n);
}
function sh() {
	var e, t, n = this, r = n._id, i = n.size();
	return new Promise(function(a, o) {
		var s = { value: o }, c = { value: function() {
			--i === 0 && a();
		} };
		n.each(function() {
			var n = nm(this, r), i = n.on;
			i !== e && (t = (e = i).copy(), t._.cancel.push(s), t._.interrupt.push(s), t._.end.push(c)), n.on = t;
		}), i === 0 && a();
	});
}
var ch = 0;
function lh(e, t, n, r) {
	this._groups = e, this._parents = t, this._name = n, this._id = r;
}
function uh() {
	return ++ch;
}
var dh = Kd.prototype;
lh.prototype = {
	constructor: lh,
	select: Vm,
	selectAll: Hm,
	selectChild: dh.selectChild,
	selectChildren: dh.selectChildren,
	filter: Pm,
	merge: Fm,
	selection: Wm,
	transition: oh,
	call: dh.call,
	nodes: dh.nodes,
	node: dh.node,
	size: dh.size,
	empty: dh.empty,
	each: dh.each,
	on: Rm,
	attr: vm,
	attrTween: Cm,
	style: Xm,
	styleTween: $m,
	text: nh,
	textTween: ah,
	remove: Bm,
	tween: lm,
	delay: Em,
	duration: km,
	ease: jm,
	easeVarying: Nm,
	end: sh,
	[Symbol.iterator]: dh[Symbol.iterator]
};
function fh(e) {
	return ((e *= 2) <= 1 ? e * e * e : (e -= 2) * e * e + 2) / 2;
}
var ph = {
	time: null,
	delay: 0,
	duration: 250,
	ease: fh
};
function mh(e, t) {
	for (var n; !(n = e.__transition) || !(n = n[t]);) if (!(e = e.parentNode)) throw Error(`transition ${t} not found`);
	return n;
}
function hh(e) {
	var t, n;
	e instanceof lh ? (t = e._id, e = e._name) : (t = uh(), (n = ph).time = Fp(), e = e == null ? null : e + "");
	for (var r = this._groups, i = r.length, a = 0; a < i; ++a) for (var o = r[a], s = o.length, c, l = 0; l < s; ++l) (c = o[l]) && em(c, e, t, l, o, n || mh(c, t));
	return new lh(r, this._parents, e, t);
}
Kd.prototype.interrupt = om, Kd.prototype.transition = hh;
var gh = Math.PI, _h = 2 * gh, vh = 1e-6, yh = _h - vh;
function bh(e) {
	this._ += e[0];
	for (let t = 1, n = e.length; t < n; ++t) this._ += arguments[t] + e[t];
}
function xh(e) {
	let t = Math.floor(e);
	if (!(t >= 0)) throw Error(`invalid digits: ${e}`);
	if (t > 15) return bh;
	let n = 10 ** t;
	return function(e) {
		this._ += e[0];
		for (let t = 1, r = e.length; t < r; ++t) this._ += Math.round(arguments[t] * n) / n + e[t];
	};
}
var Sh = class {
	constructor(e) {
		this._x0 = this._y0 = this._x1 = this._y1 = null, this._ = "", this._append = e == null ? bh : xh(e);
	}
	moveTo(e, t) {
		this._append`M${this._x0 = this._x1 = +e},${this._y0 = this._y1 = +t}`;
	}
	closePath() {
		this._x1 !== null && (this._x1 = this._x0, this._y1 = this._y0, this._append`Z`);
	}
	lineTo(e, t) {
		this._append`L${this._x1 = +e},${this._y1 = +t}`;
	}
	quadraticCurveTo(e, t, n, r) {
		this._append`Q${+e},${+t},${this._x1 = +n},${this._y1 = +r}`;
	}
	bezierCurveTo(e, t, n, r, i, a) {
		this._append`C${+e},${+t},${+n},${+r},${this._x1 = +i},${this._y1 = +a}`;
	}
	arcTo(e, t, n, r, i) {
		if (e = +e, t = +t, n = +n, r = +r, i = +i, i < 0) throw Error(`negative radius: ${i}`);
		let a = this._x1, o = this._y1, s = n - e, c = r - t, l = a - e, u = o - t, d = l * l + u * u;
		if (this._x1 === null) this._append`M${this._x1 = e},${this._y1 = t}`;
		else if (d > vh) {
			if (!(Math.abs(u * s - c * l) > vh) || !i) this._append`L${this._x1 = e},${this._y1 = t}`;
			else {
				let f = n - a, p = r - o, m = s * s + c * c, h = f * f + p * p, g = Math.sqrt(m), _ = Math.sqrt(d), v = i * Math.tan((gh - Math.acos((m + d - h) / (2 * g * _))) / 2), y = v / _, b = v / g;
				Math.abs(y - 1) > vh && this._append`L${e + y * l},${t + y * u}`, this._append`A${i},${i},0,0,${+(u * f > l * p)},${this._x1 = e + b * s},${this._y1 = t + b * c}`;
			}
		}
	}
	arc(e, t, n, r, i, a) {
		if (e = +e, t = +t, n = +n, a = !!a, n < 0) throw Error(`negative radius: ${n}`);
		let o = n * Math.cos(r), s = n * Math.sin(r), c = e + o, l = t + s, u = 1 ^ a, d = a ? r - i : i - r;
		this._x1 === null ? this._append`M${c},${l}` : (Math.abs(this._x1 - c) > vh || Math.abs(this._y1 - l) > vh) && this._append`L${c},${l}`, n && (d < 0 && (d = d % _h + _h), d > yh ? this._append`A${n},${n},0,1,${u},${e - o},${t - s}A${n},${n},0,1,${u},${this._x1 = c},${this._y1 = l}` : d > vh && this._append`A${n},${n},0,${+(d >= gh)},${u},${this._x1 = e + n * Math.cos(i)},${this._y1 = t + n * Math.sin(i)}`);
	}
	rect(e, t, n, r) {
		this._append`M${this._x0 = this._x1 = +e},${this._y0 = this._y1 = +t}h${n = +n}v${+r}h${-n}Z`;
	}
	toString() {
		return this._;
	}
};
function Ch(e) {
	return Math.abs(e = Math.round(e)) >= 1e21 ? e.toLocaleString("en").replace(/,/g, "") : e.toString(10);
}
function wh(e, t) {
	if ((n = (e = t ? e.toExponential(t - 1) : e.toExponential()).indexOf("e")) < 0) return null;
	var n, r = e.slice(0, n);
	return [r.length > 1 ? r[0] + r.slice(2) : r, +e.slice(n + 1)];
}
function Th(e) {
	return e = wh(Math.abs(e)), e ? e[1] : NaN;
}
function Eh(e, t) {
	return function(n, r) {
		for (var i = n.length, a = [], o = 0, s = e[0], c = 0; i > 0 && s > 0 && (c + s + 1 > r && (s = Math.max(1, r - c)), a.push(n.substring(i -= s, i + s)), !((c += s + 1) > r));) s = e[o = (o + 1) % e.length];
		return a.reverse().join(t);
	};
}
function Dh(e) {
	return function(t) {
		return t.replace(/[0-9]/g, function(t) {
			return e[+t];
		});
	};
}
var Oh = /^(?:(.)?([<>=^]))?([+\-( ])?([$#])?(0)?(\d+)?(,)?(\.\d+)?(~)?([a-z%])?$/i;
function kh(e) {
	if (!(t = Oh.exec(e))) throw Error("invalid format: " + e);
	var t;
	return new Ah({
		fill: t[1],
		align: t[2],
		sign: t[3],
		symbol: t[4],
		zero: t[5],
		width: t[6],
		comma: t[7],
		precision: t[8] && t[8].slice(1),
		trim: t[9],
		type: t[10]
	});
}
kh.prototype = Ah.prototype;
function Ah(e) {
	this.fill = e.fill === void 0 ? " " : e.fill + "", this.align = e.align === void 0 ? ">" : e.align + "", this.sign = e.sign === void 0 ? "-" : e.sign + "", this.symbol = e.symbol === void 0 ? "" : e.symbol + "", this.zero = !!e.zero, this.width = e.width === void 0 ? void 0 : +e.width, this.comma = !!e.comma, this.precision = e.precision === void 0 ? void 0 : +e.precision, this.trim = !!e.trim, this.type = e.type === void 0 ? "" : e.type + "";
}
Ah.prototype.toString = function() {
	return this.fill + this.align + this.sign + this.symbol + (this.zero ? "0" : "") + (this.width === void 0 ? "" : Math.max(1, this.width | 0)) + (this.comma ? "," : "") + (this.precision === void 0 ? "" : "." + Math.max(0, this.precision | 0)) + (this.trim ? "~" : "") + this.type;
};
function jh(e) {
	out: for (var t = e.length, n = 1, r = -1, i; n < t; ++n) switch (e[n]) {
		case ".":
			r = i = n;
			break;
		case "0":
			r === 0 && (r = n), i = n;
			break;
		default:
			if (!+e[n]) break out;
			r > 0 && (r = 0);
	}
	return r > 0 ? e.slice(0, r) + e.slice(i + 1) : e;
}
var Mh;
function Nh(e, t) {
	var n = wh(e, t);
	if (!n) return e + "";
	var r = n[0], i = n[1], a = i - (Mh = Math.max(-8, Math.min(8, Math.floor(i / 3))) * 3) + 1, o = r.length;
	return a === o ? r : a > o ? r + Array(a - o + 1).join("0") : a > 0 ? r.slice(0, a) + "." + r.slice(a) : "0." + Array(1 - a).join("0") + wh(e, Math.max(0, t + a - 1))[0];
}
function Ph(e, t) {
	var n = wh(e, t);
	if (!n) return e + "";
	var r = n[0], i = n[1];
	return i < 0 ? "0." + Array(-i).join("0") + r : r.length > i + 1 ? r.slice(0, i + 1) + "." + r.slice(i + 1) : r + Array(i - r.length + 2).join("0");
}
var Fh = {
	"%": (e, t) => (e * 100).toFixed(t),
	b: (e) => Math.round(e).toString(2),
	c: (e) => e + "",
	d: Ch,
	e: (e, t) => e.toExponential(t),
	f: (e, t) => e.toFixed(t),
	g: (e, t) => e.toPrecision(t),
	o: (e) => Math.round(e).toString(8),
	p: (e, t) => Ph(e * 100, t),
	r: Ph,
	s: Nh,
	X: (e) => Math.round(e).toString(16).toUpperCase(),
	x: (e) => Math.round(e).toString(16)
};
function Ih(e) {
	return e;
}
var Lh = Array.prototype.map, Rh = [
	"y",
	"z",
	"a",
	"f",
	"p",
	"n",
	"µ",
	"m",
	"",
	"k",
	"M",
	"G",
	"T",
	"P",
	"E",
	"Z",
	"Y"
];
function zh(e) {
	var t = e.grouping === void 0 || e.thousands === void 0 ? Ih : Eh(Lh.call(e.grouping, Number), e.thousands + ""), n = e.currency === void 0 ? "" : e.currency[0] + "", r = e.currency === void 0 ? "" : e.currency[1] + "", i = e.decimal === void 0 ? "." : e.decimal + "", a = e.numerals === void 0 ? Ih : Dh(Lh.call(e.numerals, String)), o = e.percent === void 0 ? "%" : e.percent + "", s = e.minus === void 0 ? "−" : e.minus + "", c = e.nan === void 0 ? "NaN" : e.nan + "";
	function l(e) {
		e = kh(e);
		var l = e.fill, u = e.align, d = e.sign, f = e.symbol, p = e.zero, m = e.width, h = e.comma, g = e.precision, _ = e.trim, v = e.type;
		v === "n" ? (h = !0, v = "g") : Fh[v] || (g === void 0 && (g = 12), _ = !0, v = "g"), (p || l === "0" && u === "=") && (p = !0, l = "0", u = "=");
		var y = f === "$" ? n : f === "#" && /[boxX]/.test(v) ? "0" + v.toLowerCase() : "", b = f === "$" ? r : /[%p]/.test(v) ? o : "", x = Fh[v], S = /[defgprs%]/.test(v);
		g = g === void 0 ? 6 : /[gprs]/.test(v) ? Math.max(1, Math.min(21, g)) : Math.max(0, Math.min(20, g));
		function C(e) {
			var n = y, r = b, o, f, C;
			if (v === "c") r = x(e) + r, e = "";
			else {
				e = +e;
				var w = e < 0 || 1 / e < 0;
				if (e = isNaN(e) ? c : x(Math.abs(e), g), _ && (e = jh(e)), w && +e == 0 && d !== "+" && (w = !1), n = (w ? d === "(" ? d : s : d === "-" || d === "(" ? "" : d) + n, r = (v === "s" ? Rh[8 + Mh / 3] : "") + r + (w && d === "(" ? ")" : ""), S) {
					for (o = -1, f = e.length; ++o < f;) if (C = e.charCodeAt(o), 48 > C || C > 57) {
						r = (C === 46 ? i + e.slice(o + 1) : e.slice(o)) + r, e = e.slice(0, o);
						break;
					}
				}
			}
			h && !p && (e = t(e, Infinity));
			var T = n.length + e.length + r.length, E = T < m ? Array(m - T + 1).join(l) : "";
			switch (h && p && (e = t(E + e, E.length ? m - r.length : Infinity), E = ""), u) {
				case "<":
					e = n + e + r + E;
					break;
				case "=":
					e = n + E + e + r;
					break;
				case "^":
					e = E.slice(0, T = E.length >> 1) + n + e + r + E.slice(T);
					break;
				default: e = E + n + e + r;
			}
			return a(e);
		}
		return C.toString = function() {
			return e + "";
		}, C;
	}
	function u(e, t) {
		var n = l((e = kh(e), e.type = "f", e)), r = Math.max(-8, Math.min(8, Math.floor(Th(t) / 3))) * 3, i = 10 ** -r, a = Rh[8 + r / 3];
		return function(e) {
			return n(i * e) + a;
		};
	}
	return {
		format: l,
		formatPrefix: u
	};
}
var Bh, Vh, Hh;
Uh({
	thousands: ",",
	grouping: [3],
	currency: ["$", ""]
});
function Uh(e) {
	return Bh = zh(e), Vh = Bh.format, Hh = Bh.formatPrefix, Bh;
}
function Wh(e) {
	return Math.max(0, -Th(Math.abs(e)));
}
function Gh(e, t) {
	return Math.max(0, Math.max(-8, Math.min(8, Math.floor(Th(t) / 3))) * 3 - Th(Math.abs(e)));
}
function Kh(e, t) {
	return e = Math.abs(e), t = Math.abs(t) - e, Math.max(0, Th(t) - Th(e)) + 1;
}
function qh(e, t) {
	switch (arguments.length) {
		case 0: break;
		case 1:
			this.range(e);
			break;
		default: this.range(t).domain(e);
	}
	return this;
}
function Jh(e) {
	return function() {
		return e;
	};
}
function Yh(e) {
	return +e;
}
var Xh = [0, 1];
function Zh(e) {
	return e;
}
function Qh(e, t) {
	return (t -= e = +e) ? function(n) {
		return (n - e) / t;
	} : Jh(isNaN(t) ? NaN : .5);
}
function $h(e, t) {
	var n;
	return e > t && (n = e, e = t, t = n), function(n) {
		return Math.max(e, Math.min(t, n));
	};
}
function eg(e, t, n) {
	var r = e[0], i = e[1], a = t[0], o = t[1];
	return i < r ? (r = Qh(i, r), a = n(o, a)) : (r = Qh(r, i), a = n(a, o)), function(e) {
		return a(r(e));
	};
}
function tg(e, t, n) {
	var r = Math.min(e.length, t.length) - 1, i = Array(r), a = Array(r), o = -1;
	for (e[r] < e[0] && (e = e.slice().reverse(), t = t.slice().reverse()); ++o < r;) i[o] = Qh(e[o], e[o + 1]), a[o] = n(t[o], t[o + 1]);
	return function(t) {
		var n = xl(e, t, 1, r) - 1;
		return a[n](i[n](t));
	};
}
function ng(e, t) {
	return t.domain(e.domain()).range(e.range()).interpolate(e.interpolate()).clamp(e.clamp()).unknown(e.unknown());
}
function rg() {
	var e = Xh, t = Xh, n = pp, r, i, a, o = Zh, s, c, l;
	function u() {
		var n = Math.min(e.length, t.length);
		return o !== Zh && (o = $h(e[0], e[n - 1])), s = n > 2 ? tg : eg, c = l = null, d;
	}
	function d(i) {
		return i == null || isNaN(i = +i) ? a : (c ||= s(e.map(r), t, n))(r(o(i)));
	}
	return d.invert = function(n) {
		return o(i((l ||= s(t, e.map(r), op))(n)));
	}, d.domain = function(t) {
		return arguments.length ? (e = Array.from(t, Yh), u()) : e.slice();
	}, d.range = function(e) {
		return arguments.length ? (t = Array.from(e), u()) : t.slice();
	}, d.rangeRound = function(e) {
		return t = Array.from(e), n = mp, u();
	}, d.clamp = function(e) {
		return arguments.length ? (o = e ? !0 : Zh, u()) : o !== Zh;
	}, d.interpolate = function(e) {
		return arguments.length ? (n = e, u()) : n;
	}, d.unknown = function(e) {
		return arguments.length ? (a = e, d) : a;
	}, function(e, t) {
		return r = e, i = t, u();
	};
}
function ig() {
	return rg()(Zh, Zh);
}
function ag(e, t, n, r) {
	var i = Ol(e, t, n), a;
	switch (r = kh(r ?? ",f"), r.type) {
		case "s":
			var o = Math.max(Math.abs(e), Math.abs(t));
			return r.precision == null && !isNaN(a = Gh(i, o)) && (r.precision = a), Hh(r, o);
		case "":
		case "e":
		case "g":
		case "p":
		case "r":
			r.precision == null && !isNaN(a = Kh(i, Math.max(Math.abs(e), Math.abs(t)))) && (r.precision = a - (r.type === "e"));
			break;
		case "f":
		case "%": r.precision == null && !isNaN(a = Wh(i)) && (r.precision = a - (r.type === "%") * 2);
	}
	return Vh(r);
}
function og(e) {
	var t = e.domain;
	return e.ticks = function(e) {
		var n = t();
		return El(n[0], n[n.length - 1], e ?? 10);
	}, e.tickFormat = function(e, n) {
		var r = t();
		return ag(r[0], r[r.length - 1], e ?? 10, n);
	}, e.nice = function(n) {
		n ??= 10;
		var r = t(), i = 0, a = r.length - 1, o = r[i], s = r[a], c, l, u = 10;
		for (s < o && (l = o, o = s, s = l, l = i, i = a, a = l); u-- > 0;) {
			if (l = Dl(o, s, n), l === c) return r[i] = o, r[a] = s, t(r);
			if (l > 0) o = Math.floor(o / l) * l, s = Math.ceil(s / l) * l;
			else if (l < 0) o = Math.ceil(o * l) / l, s = Math.floor(s * l) / l;
			else break;
			c = l;
		}
		return e;
	}, e;
}
function sg() {
	var e = ig();
	return e.copy = function() {
		return ng(e, sg());
	}, qh.apply(e, arguments), og(e);
}
function cg(e) {
	return function() {
		return e;
	};
}
function lg(e) {
	let t = 3;
	return e.digits = function(n) {
		if (!arguments.length) return t;
		if (n == null) t = null;
		else {
			let e = Math.floor(n);
			if (!(e >= 0)) throw RangeError(`invalid digits: ${n}`);
			t = e;
		}
		return e;
	}, () => new Sh(t);
}
function ug(e) {
	return typeof e == "object" && "length" in e ? e : Array.from(e);
}
function dg(e) {
	this._context = e;
}
dg.prototype = {
	areaStart: function() {
		this._line = 0;
	},
	areaEnd: function() {
		this._line = NaN;
	},
	lineStart: function() {
		this._point = 0;
	},
	lineEnd: function() {
		(this._line || this._line !== 0 && this._point === 1) && this._context.closePath(), this._line = 1 - this._line;
	},
	point: function(e, t) {
		switch (e = +e, t = +t, this._point) {
			case 0:
				this._point = 1, this._line ? this._context.lineTo(e, t) : this._context.moveTo(e, t);
				break;
			case 1: this._point = 2;
			default: this._context.lineTo(e, t);
		}
	}
};
function fg(e) {
	return new dg(e);
}
function pg(e) {
	return e[0];
}
function mg(e) {
	return e[1];
}
function hg(e, t) {
	var n = cg(!0), r = null, i = fg, a = null, o = lg(s);
	e = typeof e == "function" ? e : e === void 0 ? pg : cg(e), t = typeof t == "function" ? t : t === void 0 ? mg : cg(t);
	function s(s) {
		var c, l = (s = ug(s)).length, u, d = !1, f;
		for (r ?? (a = i(f = o())), c = 0; c <= l; ++c) !(c < l && n(u = s[c], c, s)) === d && ((d = !d) ? a.lineStart() : a.lineEnd()), d && a.point(+e(u, c, s), +t(u, c, s));
		if (f) return a = null, f + "" || null;
	}
	return s.x = function(t) {
		return arguments.length ? (e = typeof t == "function" ? t : cg(+t), s) : e;
	}, s.y = function(e) {
		return arguments.length ? (t = typeof e == "function" ? e : cg(+e), s) : t;
	}, s.defined = function(e) {
		return arguments.length ? (n = typeof e == "function" ? e : cg(!!e), s) : n;
	}, s.curve = function(e) {
		return arguments.length ? (i = e, r != null && (a = i(r)), s) : i;
	}, s.context = function(e) {
		return arguments.length ? (e == null ? r = a = null : a = i(r = e), s) : r;
	}, s;
}
function gg(e, t, n) {
	this.k = e, this.x = t, this.y = n;
}
gg.prototype = {
	constructor: gg,
	scale: function(e) {
		return e === 1 ? this : new gg(this.k * e, this.x, this.y);
	},
	translate: function(e, t) {
		return e === 0 & t === 0 ? this : new gg(this.k, this.x + this.k * e, this.y + this.k * t);
	},
	apply: function(e) {
		return [e[0] * this.k + this.x, e[1] * this.k + this.y];
	},
	applyX: function(e) {
		return e * this.k + this.x;
	},
	applyY: function(e) {
		return e * this.k + this.y;
	},
	invert: function(e) {
		return [(e[0] - this.x) / this.k, (e[1] - this.y) / this.k];
	},
	invertX: function(e) {
		return (e - this.x) / this.k;
	},
	invertY: function(e) {
		return (e - this.y) / this.k;
	},
	rescaleX: function(e) {
		return e.copy().domain(e.range().map(this.invertX, this).map(e.invert, e));
	},
	rescaleY: function(e) {
		return e.copy().domain(e.range().map(this.invertY, this).map(e.invert, e));
	},
	toString: function() {
		return "translate(" + this.x + "," + this.y + ") scale(" + this.k + ")";
	}
}, new gg(1, 0, 0), gg.prototype;
var _g;
(function(e) {
	e.Monomer = "monomer", e.Preset = "preset", e.Bond = "bond", e.AmbiguousMonomer = "ambiguousMonomer";
})(_g ||= {});
var vg;
(function(e) {
	e.Library = "library", e.ChainStart = "chainStart", e.ChainMiddle = "chainMiddle", e.ChainEnd = "chainEnd";
})(vg ||= {});
var yg = "select-submenu";
function bg(e, t) {
	var n = Object.keys(e);
	if (Object.getOwnPropertySymbols) {
		var r = Object.getOwnPropertySymbols(e);
		t && (r = r.filter(function(t) {
			return Object.getOwnPropertyDescriptor(e, t).enumerable;
		})), n.push.apply(n, r);
	}
	return n;
}
function xg(e) {
	for (var t = 1; t < arguments.length; t++) {
		var n = arguments[t] == null ? {} : arguments[t];
		t % 2 ? bg(Object(n), !0).forEach(function(t) {
			I(e, t, n[t]);
		}) : Object.getOwnPropertyDescriptors ? Object.defineProperties(e, Object.getOwnPropertyDescriptors(n)) : bg(Object(n)).forEach(function(t) {
			Object.defineProperty(e, t, Object.getOwnPropertyDescriptor(n, t));
		});
	}
	return e;
}
var Sg;
(function(e) {
	e.nanoMol = "nM", e.microMol = "μM", e.milliMol = "mM";
})(Sg ||= {});
var Cg = I(I(I({}, Sg.nanoMol, 10 ** 9), Sg.microMol, 10 ** 6), Sg.milliMol, 1e3), wg = sl({
	name: "editor",
	initialState: {
		ketcherId: "",
		isReady: null,
		activeTool: "select",
		editor: void 0,
		monomerLibraryLoadError: null,
		editorLayoutMode: void 0,
		editorLineLength: fe.editorLineLength,
		preview: {
			type: _g.Monomer,
			monomer: void 0,
			style: {}
		},
		position: void 0,
		isContextMenuActive: !1,
		isDragging: !1,
		isMacromoleculesPropertiesWindowOpened: !1,
		macromoleculesProperties: void 0,
		unipositiveIonsMeasurementUnit: Sg.milliMol,
		oligonucleotidesMeasurementUnit: Sg.microMol,
		unipositiveIonsValue: 140,
		oligonucleotidesValue: 200,
		app: {
			buildDate: "2026-09-02T13:06:26",
			indigoVersion: "",
			indigoMachine: "",
			version: "3.18.0"
		},
		selectedMenuGroupItems: {}
	},
	reducers: {
		init: function(e) {
			e.isReady = !1;
		},
		initKetcherId: function(e, t) {
			e.ketcherId = t.payload;
		},
		initSuccess: function(e) {
			e.isReady = !0;
		},
		initFailure: function(e) {
			e.isReady = !1;
		},
		setMonomerLibraryLoadError: function(e, t) {
			e.monomerLibraryLoadError = t.payload;
		},
		selectTool: function(e, t) {
			e.activeTool = t.payload;
		},
		setPosition: function(e, t) {
			e.position = t.payload;
		},
		createEditor: function(e, t) {
			var n, r;
			e.monomerLibraryLoadError = null;
			var i = new v({
				theme: t.payload.theme,
				canvas: t.payload.canvas,
				renderersContainer: new $e({ theme: t.payload.theme })
			});
			i.initializeMonomersLibraryFromKetcher(t.payload.monomersLibraryUpdate, t.payload.monomersLibraryReplace, t.payload.onLibraryError), e.editor = i, (n = (r = t.payload).onInit) == null || n.call(r, i);
		},
		destroyEditor: function(e) {
			var t;
			e.editorLayoutMode = e.editor?.mode.modeName, (t = e.editor) == null || t.destroy(), e.editor = void 0;
		},
		showPreview: function(e, t) {
			e.preview = t.payload || {
				monomer: void 0,
				style: ""
			};
		},
		setContextMenuActive: function(e, t) {
			e.isContextMenuActive = t.payload;
		},
		setIsDragging: function(e, t) {
			e.isDragging = t.payload;
		},
		setMacromoleculesPropertiesWindowVisibility: function(e, t) {
			e.isMacromoleculesPropertiesWindowOpened = t.payload;
		},
		toggleMacromoleculesPropertiesWindowVisibility: function(e) {
			e.isMacromoleculesPropertiesWindowOpened = !e.isMacromoleculesPropertiesWindowOpened;
		},
		setMacromoleculesProperties: function(e, t) {
			e.macromoleculesProperties = t.payload;
		},
		setUnipositiveIonsMeasurementUnit: function(e, t) {
			e.unipositiveIonsMeasurementUnit = t.payload;
		},
		setOligonucleotidesMeasurementUnit: function(e, t) {
			e.oligonucleotidesMeasurementUnit = t.payload;
		},
		setEditorLineLength: function(e, t) {
			e.editorLineLength = xg(xg({}, e.editorLineLength), t.payload);
		},
		setUnipositiveIonsValue: function(e, t) {
			e.unipositiveIonsValue = t.payload;
		},
		setOligonucleotidesValue: function(e, t) {
			e.oligonucleotidesValue = t.payload;
		},
		setAppMeta: function(e, t) {
			e.app = t.payload;
		},
		setSelectedMenuGroupItem: function(e, t) {
			e.selectedMenuGroupItems = xg(xg({}, e.selectedMenuGroupItems), {}, I({}, t.payload.groupName, t.payload.activeItemName));
		}
	}
}), G = wg.actions;
G.init, G.initSuccess, G.initFailure;
var Tg = G.setMonomerLibraryLoadError, Eg = G.initKetcherId, Dg = G.selectTool;
G.setPosition;
var Og = G.createEditor, kg = G.destroyEditor, Ag = G.showPreview, jg = G.setContextMenuActive, Mg = G.setIsDragging, Ng = G.setMacromoleculesPropertiesWindowVisibility, Pg = G.toggleMacromoleculesPropertiesWindowVisibility, Fg = G.setMacromoleculesProperties, Ig = G.setUnipositiveIonsMeasurementUnit, Lg = G.setOligonucleotidesMeasurementUnit, Rg = G.setEditorLineLength, zg = G.setUnipositiveIonsValue, Bg = G.setOligonucleotidesValue, Vg = G.setAppMeta, Hg = G.setSelectedMenuGroupItem, Ug = function(e) {
	return e.editor.preview;
}, Wg = function(e) {
	return e.editor.activeTool;
}, Gg = function(e) {
	return e.editor.ketcherId;
}, K = function(e) {
	return e.editor.editor;
}, Kg = function(e) {
	return e.editor.editor?.isSequenceEditInRNABuilderMode;
}, qg = function(e) {
	return e.editor.editor?.isSequenceMode;
}, Jg = function(e) {
	return e.editor.editorLayoutMode;
}, Yg = function(e) {
	return e.editor.editor?.isHandToolSelected;
}, Xg = function(e) {
	var t;
	return (t = e.editor.editor) == null || (t = t.drawingEntitiesManager) == null ? void 0 : t.hasAntisenseChains;
}, Zg = function(e) {
	return e.editor.isContextMenuActive;
}, Qg = function(e) {
	return e.editor.isDragging;
}, $g = function(e) {
	return e.editor.isMacromoleculesPropertiesWindowOpened;
}, e_ = function(e) {
	return e.editor.macromoleculesProperties;
}, t_ = function(e) {
	return e.editor.unipositiveIonsMeasurementUnit;
}, n_ = function(e) {
	return e.editor.oligonucleotidesMeasurementUnit;
}, r_ = function(e) {
	return e.editor.unipositiveIonsValue;
}, i_ = function(e) {
	return e.editor.oligonucleotidesValue;
}, a_ = function(e) {
	return e.editor.editorLineLength;
}, o_ = function(e) {
	return e.editor.app;
}, s_ = function(e) {
	return function(t) {
		return t.editor.selectedMenuGroupItems[e];
	};
}, c_ = function(e) {
	return e.editor.selectedMenuGroupItems[yg] || "select-rectangle";
}, l_ = wg.reducer, u_ = "FAVORITES", d_ = "PEPTIDE", f_ = {
	PEPTIDE: "PEPTIDE",
	CHEM: "CHEM",
	RNA: "RNA"
}, q;
(function(e) {
	e.SUGARS = "Sugars", e.BASES = "Bases", e.PHOSPHATES = "Phosphates", e.PEPTIDES = "Amino Acids", e.NUCLEOTIDES = "Nucleotides";
})(q ||= {});
var p_;
(function(e) {
	e.R = "R", e.A = "A", e.C = "C", e.G = "G", e.T = "T", e.U = "U", e.X = "X", e.P = "P";
})(p_ ||= {}), q.SUGARS, q.BASES, q.BASES, q.BASES, q.BASES, q.BASES, q.BASES, q.PHOSPHATES;
var m_ = "favoriteItemsUniqueKeys", h_ = "ketcher_custom_presets", g_ = "ketcher_preset_phosphate_filter", __ = "ketcher_polymer_sequence_type", v_ = "Z", y_ = "No natural analogue", b_ = "thymine", x_ = "uracil", S_ = {
	FAVORITES: 0,
	PEPTIDES: 1,
	RNA: 2,
	CHEM: 3
}, C_ = "★", w_ = new (function() {
	function e() {
		Wt(this, e), I(this, "localStorage", void 0), this.localStorage = window.localStorage;
	}
	return Sn(e, [
		{
			key: "getItem",
			value: function(e) {
				var t = this.localStorage.getItem(e);
				return t ? JSON.parse(t) : null;
			}
		},
		{
			key: "setItem",
			value: function(e, t) {
				this.localStorage.setItem(e, JSON.stringify(t));
			}
		},
		{
			key: "removeItem",
			value: function(e) {
				this.localStorage.removeItem(e);
			}
		}
	]), e;
}())();
function T_(e, t) {
	var n = Object.keys(e);
	if (Object.getOwnPropertySymbols) {
		var r = Object.getOwnPropertySymbols(e);
		t && (r = r.filter(function(t) {
			return Object.getOwnPropertyDescriptor(e, t).enumerable;
		})), n.push.apply(n, r);
	}
	return n;
}
function E_(e) {
	for (var t = 1; t < arguments.length; t++) {
		var n = arguments[t] == null ? {} : arguments[t];
		t % 2 ? T_(Object(n), !0).forEach(function(t) {
			I(e, t, n[t]);
		}) : Object.getOwnPropertyDescriptors ? Object.defineProperties(e, Object.getOwnPropertyDescriptors(n)) : T_(Object(n)).forEach(function(t) {
			Object.defineProperty(e, t, Object.getOwnPropertyDescriptor(n, t));
		});
	}
	return e;
}
var D_ = I(I({}, Ye.PEPTIDES, st.AminoAcid), Ye.BASES, st.Base), O_ = {
	monomers: [],
	defaultRnaPresets: [],
	favorites: {},
	searchFilter: "",
	selectedTabIndex: S_.RNA
};
function k_(e) {
	if (w(e)) {
		var t = e;
		return t.id || t.label;
	}
	var n = e;
	return `${n.props.MonomerName}___${n.props?.Name}`;
}
function A_(e) {
	return `${e.name}_${e.base?.label ?? "."}_${e.sugar?.label ?? "."}_${e.phosphate?.label ?? "."}`;
}
var j_ = sl({
	name: "library",
	initialState: O_,
	reducers: {
		loadMonomerLibrary: function(e, t) {
			e.monomers = t.payload.map(function(e) {
				return E_(E_({}, e), {}, { props: E_({}, e.props) });
			});
		},
		loadDefaultPresets: function(e, t) {
			e.defaultRnaPresets = t.payload.map(function(e) {
				return E_({}, e);
			});
		},
		setFavoriteMonomersFromLocalStorage: function(e) {
			var t = {}, n = w_.getItem(m_);
			n && Array.isArray(n) && (e.monomers.forEach(function(e) {
				var r = k_(e);
				n.find(function(e) {
					return e === r;
				}) && (t[r] = E_(E_({}, e), {}, { favorite: !0 }));
			}), e.favorites = t);
		},
		clearFavorites: function(e) {
			e.favorites = {};
		},
		toggleMonomerFavorites: function(e, t) {
			var n = k_(t.payload), r = w_.getItem(m_) ?? [];
			e.favorites[n] ? (delete e.favorites[n], w_.setItem(m_, r.filter(function(e) {
				return e !== n;
			}))) : (e.favorites[n] = E_(E_({}, t.payload), {}, { favorite: !0 }), r.push(n), w_.setItem(m_, r));
		},
		setSearchFilter: function(e, t) {
			e.searchFilter = t.payload;
		},
		setSelectedTabIndex: function(e, t) {
			e.selectedTabIndex = t.payload;
		}
	}
}), M_ = j_.actions, N_ = M_.loadMonomerLibrary, P_ = M_.loadDefaultPresets, F_ = M_.setFavoriteMonomersFromLocalStorage;
M_.clearFavorites;
var I_ = M_.toggleMonomerFavorites, L_ = M_.setSearchFilter, R_ = M_.setSelectedTabIndex, z_ = Qt(function(e) {
	return e.library.defaultRnaPresets;
}, function(e) {
	return (e ?? []).reduce(function(e, t) {
		return t.aliasAxoLabs && t.name && e.set(t.name.toLowerCase(), t.aliasAxoLabs.toLowerCase()), e;
	}, /* @__PURE__ */ new Map());
}), B_ = function(e) {
	return e.library.searchFilter;
}, V_ = function(e, t) {
	return e.filter(function(e) {
		return !e.isAmbiguous && e.props?.MonomerType === t;
	});
}, H_ = function(e, t) {
	var n = e.filter(function(e) {
		if (!w(e)) return !1;
		var n = new mn(e, void 0, !1);
		return D_[t] === n.monomerClass;
	});
	if (n.length === 0) return [];
	var r = [];
	t === Ye.BASES ? r = [
		{
			groupTitle: "Ambiguous Bases",
			groupItems: n.filter(function(e) {
				return w(e) && e.options.every(function(e) {
					return !e.templateId.toLowerCase().includes(b_) && !e.templateId.toLowerCase().includes(x_);
				});
			})
		},
		{
			groupTitle: "Ambiguous DNA Bases",
			groupItems: n.filter(function(e) {
				return w(e) && e.options.find(function(e) {
					return e.templateId.toLowerCase().includes(b_);
				});
			})
		},
		{
			groupTitle: "Ambiguous RNA Bases",
			groupItems: n.filter(function(e) {
				return w(e) && e.options.find(function(e) {
					return e.templateId.toLowerCase().includes(x_);
				});
			})
		}
	] : r.push({
		groupTitle: `Ambiguous ${t}`,
		groupItems: n
	});
	var i = ["X", "N"];
	return r.forEach(function(e) {
		e.groupItems.sort(function(e, t) {
			return e.label.localeCompare(t.label);
		}), e.groupItems.sort(function(e) {
			return i.includes(e.label) ? -1 : 1;
		});
	}), r;
}, U_ = function(e) {
	return e.filter(function(e) {
		return !e.isAmbiguous && (e.props?.MonomerClass === st.RNA || e.props?.MonomerClass === st.DNA);
	});
}, W_ = function(e) {
	return e.filter(function(e) {
		return e.favorite && !e.isAmbiguous;
	});
}, G_ = function(e) {
	var t = [];
	for (var n in Ye) {
		var r = H_(e, Ye[n]);
		t = [].concat(L(t), L(r));
	}
	return t.forEach(function(e) {
		e.groupItems = e.groupItems.filter(function(e) {
			return e.favorite;
		});
	}), t.filter(function(e) {
		return e.groupItems.length;
	});
}, K_ = Qt(function(e) {
	return e.library;
}, function(e) {
	var t = e.searchFilter, n = e.monomers, r = e.favorites, i = t.toLowerCase(), a = function(e, t) {
		var n, r = arguments.length > 2 && arguments[2] !== void 0 ? arguments[2] : "", i = arguments.length > 3 && arguments[3] !== void 0 ? arguments[3] : "", a = arguments.length > 4 && arguments[4] !== void 0 ? arguments[4] : "", o = arguments.length > 5 && arguments[5] !== void 0 ? arguments[5] : "", s = arguments.length > 6 && arguments[6] !== void 0 ? arguments[6] : "", c = arguments.length > 7 && arguments[7] !== void 0 ? arguments[7] : [], l = r.toLowerCase(), u = i.toLowerCase(), d = e == null || (n = e.base) == null ? void 0 : n.toLowerCase(), f = e != null && e.modifications ? Object.values(e.modifications).map(function(e) {
			return e.toLowerCase();
		}).join(" ") : "", p = a?.toLowerCase() ?? "", m = o?.toLowerCase() ?? "", h = s?.toLowerCase() ?? "", g = c && c.length > 0 ? c.map(function(e) {
			return e.toLowerCase();
		}).join(" ") : "";
		if (t === "/") return !!(d || f);
		if (t.includes("/")) {
			var _ = t.split("/");
			if (_.length > 3 || _.length === 3 && _[2] !== "") return !1;
			if (_.length === 3 && _[1] !== "") {
				var v = _[1], y = d?.length === v.length && Array.from(d).every(function(e, t) {
					return e === v[t];
				}), b = f ? f.split(" ").some(function(e) {
					return e.length === v.length && Array.from(e).every(function(e, t) {
						return e === v[t];
					});
				}) : !1;
				return y || b;
			}
			var x = _[0], S = _[1];
			if (t.startsWith("/") && t.length > 1) {
				var C, w = {
					5: "endpoint5",
					3: "endpoint3",
					i: "internal"
				}[t[1]];
				if (!w) {
					var T = t.slice(1);
					return d?.startsWith(T) || f?.split(" ").some(function(e) {
						return e.startsWith(T);
					});
				}
				var E = e == null || (C = e.modifications) == null || (C = C[w]) == null ? void 0 : C.toLowerCase(), D = t.slice(2), O = D ? !!d?.startsWith(D) : !!E, k = E ? E.includes(t) : !1;
				return O || k;
			}
			if (t.endsWith("/") && t.length > 1) {
				var A = t.slice(0, -1);
				return d?.endsWith(A) || f?.split(" ").some(function(e) {
					return e.endsWith(A);
				});
			}
			var j = d?.startsWith(S) && d?.endsWith(x), ee = f ? f.split(" ").some(function(e) {
				return e.startsWith(S) && e.endsWith(x);
			}) : !1;
			return j || ee;
		}
		var te = d ? d.includes(t) : !1, M = f ? f.includes(t) : !1, ne = p ? p.includes(t) : !1, re = m ? m.includes(t) : !1, N = h ? h.includes(t) : !1, ie = g ? g.includes(t) : !1;
		return l.includes(t) || u.includes(t) || te || M || ne || re || N || ie;
	};
	return n.filter(function(e) {
		var t;
		if (!e.isAmbiguous && (t = e.props) != null && t.hidden) return !1;
		if (e.isAmbiguous) {
			var n = e.label, r = e.id, o = e.idtAliases, s = e.monomers;
			return a(o, i, n, r) || s.some(function(e) {
				var t = e.monomerItem.props, n = t.Name, r = t.MonomerName, o = t.idtAliases, s = t.aliasHELM, c = t.aliasBILN, l = t.aliasAxoLabs, u = t.modificationTypes;
				return a(o, i, n, r, s, c, l, u);
			});
		}
		var c = e.props, l = c.Name, u = c.MonomerName, d = c.idtAliases, f = c.aliasHELM, p = c.aliasBILN, m = c.aliasAxoLabs, h = c.modificationTypes;
		return a(d, i, l, u, f, p, m, h);
	}).map(function(e) {
		return E_(E_({}, e), {}, { favorite: !!r[k_(e)] });
	});
}), q_ = function(e) {
	var t = e.reduce(function(e, t) {
		var n = t.props.MonomerNaturalAnalogCode || v_;
		return e[n] || (e[n] = []), e[n].push(E_(E_({}, t), {}, { label: t.props.MonomerName })), e;
	}, {}), n = Object.entries(t).reduce(function(e, t) {
		var n = R(t, 2), r = n[0], i = n[1], a = L(i);
		a.sort(function(e, t) {
			return e.label.localeCompare(t.label);
		});
		var o = a.findIndex(function(e) {
			return e.label === r;
		});
		if (o !== -1) {
			var s = a.splice(o, 1);
			a.unshift(s[0]);
		}
		return e[r] = a, e;
	}, {}), r = [], i = Object.keys(n);
	return i.sort(function(e, t) {
		return e.localeCompare(t);
	}), i.reduce(function(e, t) {
		var r = {
			groupTitle: t === v_ ? y_ : t,
			groupItems: []
		};
		return n[t].forEach(function(e) {
			r.groupItems.push(E_(E_({}, e), {}, { props: E_({}, e.props) }));
		}), r.groupItems.length && e.push(r), e;
	}, r);
}, J_ = function(e) {
	return e.library.selectedTabIndex;
}, Y_ = j_.reducer, X_ = function(e) {
	return e.library.defaultRnaPresets;
}, Z_ = sl({
	name: "modal",
	initialState: {
		name: null,
		isOpen: !1,
		additionalProps: null,
		errorTooltips: [],
		errorModalText: "",
		errorModalTitle: ""
	},
	reducers: {
		openModal: function(e, t) {
			typeof t.payload == "string" ? e.name = t.payload : (e.name = t.payload.name, e.additionalProps = t.payload.additionalProps), e.isOpen = !0;
		},
		closeModal: function(e) {
			e.name = null, e.isOpen = !1, e.additionalProps = null;
		},
		openErrorTooltip: function(e, t) {
			e.errorTooltips.includes(t.payload) || e.errorTooltips.push(t.payload);
		},
		closeErrorTooltip: function(e, t) {
			e.errorTooltips = t.payload ? e.errorTooltips.filter(function(e) {
				return e !== t.payload;
			}) : [];
		},
		openErrorModal: function(e, t) {
			if (typeof t.payload == "string") e.errorModalText = t.payload;
			else {
				var n = t.payload, r = n.errorMessage, i = n.errorTitle;
				e.errorModalText = r, e.errorModalTitle = i;
			}
		},
		closeErrorModal: function(e) {
			e.errorModalText = "";
		}
	}
}), Q_ = Z_.actions, $_ = Q_.openModal, ev = Q_.closeModal, tv = Q_.openErrorTooltip, nv = Q_.closeErrorTooltip, rv = Q_.openErrorModal, iv = Q_.closeErrorModal, av = function(e) {
	return e.modal.name;
}, ov = function(e) {
	return e.modal.isOpen;
}, sv = function(e) {
	return e.modal.additionalProps;
}, cv = function(e) {
	return e.modal.errorTooltips;
}, lv = function(e) {
	return e.modal.errorModalText;
}, uv = function(e) {
	return e.modal.errorModalTitle;
}, dv = Z_.reducer, fv = 6e3, pv = function(e) {
	return function(t) {
		return function(n) {
			var r = t(n);
			return tv.match(n) && setTimeout(function() {
				e.dispatch(nv(n.payload));
			}, fv), r;
		};
	};
};
function mv(e, t) {
	var n = Object.keys(e);
	if (Object.getOwnPropertySymbols) {
		var r = Object.getOwnPropertySymbols(e);
		t && (r = r.filter(function(t) {
			return Object.getOwnPropertyDescriptor(e, t).enumerable;
		})), n.push.apply(n, r);
	}
	return n;
}
function hv(e) {
	for (var t = 1; t < arguments.length; t++) {
		var n = arguments[t] == null ? {} : arguments[t];
		t % 2 ? mv(Object(n), !0).forEach(function(t) {
			I(e, t, n[t]);
		}) : Object.getOwnPropertyDescriptors ? Object.defineProperties(e, Object.getOwnPropertyDescriptors(n)) : mv(Object(n)).forEach(function(t) {
			Object.defineProperty(e, t, Object.getOwnPropertyDescriptor(n, t));
		});
	}
	return e;
}
var gv = function() {
	return w_.getItem(h_);
}, _v = function(e) {
	return gv()?.findIndex(function(t) {
		return t.name === e;
	}) ?? -1;
}, vv = function(e) {
	var t = hv({}, e), n = gv() ?? [], r = _v(t.nameInList);
	t.nameInList = t.name, r > -1 ? (n.splice(r, 1, t), w_.setItem(h_, n)) : w_.setItem(h_, [].concat(L(n), [t]));
}, yv = function(e) {
	if (e) {
		var t = gv(), n = _v(e);
		t && (t.splice(n, 1), t.length ? w_.setItem(h_, t) : w_.removeItem(h_));
	}
}, bv = function(e) {
	if (e) {
		var t = gv(), n = _v(e);
		t && n > -1 && (t[n].favorite = !t[n].favorite, w_.setItem(h_, t));
	}
}, xv = function(e) {
	var t = [
		"sugar",
		"base",
		"phosphate"
	], n = (0, Ts.default)(e, t);
	n.templates = [];
	for (var r = 0, i = t; r < i.length; r++) {
		var a, o = e[i[r]], s = (o == null || (a = o.props) == null ? void 0 : a.id) ?? o?.id;
		s && n.templates.push({ $ref: o.isAmbiguous ? _t(s) : zn(s) });
	}
	return n.connections = Xe(e, ie(e)), n;
}, Sv = function(e, t) {
	var n;
	return !!(e != null && (n = e.props) != null && n.MonomerCaps && t in e.props.MonomerCaps);
}, Cv = function(e) {
	return {
		is3PrimeAvailable: (!(e != null && e.sugar) || Sv(e.sugar, "R2")) && (!(e != null && e.phosphate) || Sv(e.phosphate, "R1")),
		is5PrimeAvailable: (!(e != null && e.sugar) || Sv(e.sugar, "R1")) && (!(e != null && e.phosphate) || Sv(e.phosphate, "R2"))
	};
}, wv = function(e, t, n) {
	var r, i = [], a = [], o = [];
	if (!t || !(e != null && e.sugar) && !(e != null && e.phosphate) && !(e != null && e.base)) return {
		sugarValidations: i,
		phosphateValidations: a,
		baseValidations: o
	};
	var s = Cv(e), c = s.is3PrimeAvailable, l = s.is5PrimeAvailable;
	return n === "right" ? (i.push("R2"), a.push("R1")) : n === "left" ? (i.push("R1"), a.push("R2")) : (l || (a.push("R1"), i.push("R2")), c || (a.push("R2"), i.push("R1"))), e != null && e.base && i.push("R3"), o.push("R1"), e != null && (r = e.sugar) != null && (r = r.props) != null && r.MonomerCaps && !Sv(e.sugar, "R3") && o.push("DISABLED"), {
		sugarValidations: i,
		phosphateValidations: a,
		baseValidations: o
	};
}, Tv = /^[a-zA-Z0-9-_*]+$/, Ev = function(e) {
	return Tv.test(e);
}, Dv = Object.defineProperty, Ov = Object.getOwnPropertySymbols, kv = Object.prototype.hasOwnProperty, Av = Object.prototype.propertyIsEnumerable, jv = (e, t, n) => t in e ? Dv(e, t, {
	enumerable: !0,
	configurable: !0,
	writable: !0,
	value: n
}) : e[t] = n, Mv = (e, t) => {
	for (var n in t ||= {}) kv.call(t, n) && jv(e, n, t[n]);
	if (Ov) for (var n of Ov(t)) Av.call(t, n) && jv(e, n, t[n]);
	return e;
}, Nv = Symbol.for("immer-nothing"), Pv = Symbol.for("immer-draftable"), Fv = Symbol.for("immer-state");
function Iv(e, ...t) {
	throw Error(`[Immer] minified error nr: ${e}. Full error at: https://bit.ly/3cXEKWf`);
}
var Lv = Object.getPrototypeOf;
function Rv(e) {
	return !!e && !!e[Fv];
}
function zv(e) {
	return e ? Vv(e) || Array.isArray(e) || !!e[Pv] || !!e.constructor?.[Pv] || qv(e) || Jv(e) : !1;
}
var Bv = Object.prototype.constructor.toString();
function Vv(e) {
	if (!e || typeof e != "object") return !1;
	let t = Lv(e);
	if (t === null) return !0;
	let n = Object.hasOwnProperty.call(t, "constructor") && t.constructor;
	return n === Object || typeof n == "function" && Function.toString.call(n) === Bv;
}
function Hv(e, t) {
	Uv(e) === 0 ? Reflect.ownKeys(e).forEach((n) => {
		t(n, e[n], e);
	}) : e.forEach((n, r) => t(r, n, e));
}
function Uv(e) {
	let t = e[Fv];
	return t ? t.type_ : Array.isArray(e) ? 1 : qv(e) ? 2 : Jv(e) ? 3 : 0;
}
function Wv(e, t) {
	return Uv(e) === 2 ? e.has(t) : Object.prototype.hasOwnProperty.call(e, t);
}
function Gv(e, t, n) {
	let r = Uv(e);
	r === 2 ? e.set(t, n) : r === 3 ? e.add(n) : e[t] = n;
}
function Kv(e, t) {
	return e === t ? e !== 0 || 1 / e == 1 / t : e !== e && t !== t;
}
function qv(e) {
	return e instanceof Map;
}
function Jv(e) {
	return e instanceof Set;
}
function Yv(e) {
	return e.copy_ || e.base_;
}
function Xv(e, t) {
	if (qv(e)) return new Map(e);
	if (Jv(e)) return new Set(e);
	if (Array.isArray(e)) return Array.prototype.slice.call(e);
	let n = Vv(e);
	if (t === !0 || t === "class_only" && !n) {
		let t = Object.getOwnPropertyDescriptors(e);
		delete t[Fv];
		let n = Reflect.ownKeys(t);
		for (let r = 0; r < n.length; r++) {
			let i = n[r], a = t[i];
			a.writable === !1 && (a.writable = !0, a.configurable = !0), (a.get || a.set) && (t[i] = {
				configurable: !0,
				writable: !0,
				enumerable: a.enumerable,
				value: e[i]
			});
		}
		return Object.create(Lv(e), t);
	}
	{
		let t = Lv(e);
		if (t !== null && n) return Mv({}, e);
		let r = Object.create(t);
		return Object.assign(r, e);
	}
}
function Zv(e, t = !1) {
	return $v(e) || Rv(e) || !zv(e) || (Uv(e) > 1 && (e.set = e.add = e.clear = e.delete = Qv), Object.freeze(e), t && Object.entries(e).forEach(([e, t]) => Zv(t, !0))), e;
}
function Qv() {
	Iv(2);
}
function $v(e) {
	return Object.isFrozen(e);
}
var ey = {};
function ty(e) {
	let t = ey[e];
	return t || Iv(0, e), t;
}
var ny;
function ry() {
	return ny;
}
function iy(e, t) {
	return {
		drafts_: [],
		parent_: e,
		immer_: t,
		canAutoFreeze_: !0,
		unfinalizedDrafts_: 0
	};
}
function ay(e, t) {
	t && (ty("Patches"), e.patches_ = [], e.inversePatches_ = [], e.patchListener_ = t);
}
function oy(e) {
	sy(e), e.drafts_.forEach(ly), e.drafts_ = null;
}
function sy(e) {
	e === ny && (ny = e.parent_);
}
function cy(e) {
	return ny = iy(ny, e);
}
function ly(e) {
	let t = e[Fv];
	t.type_ === 0 || t.type_ === 1 ? t.revoke_() : t.revoked_ = !0;
}
function uy(e, t) {
	t.unfinalizedDrafts_ = t.drafts_.length;
	let n = t.drafts_[0];
	return e !== void 0 && e !== n ? (n[Fv].modified_ && (oy(t), Iv(4)), zv(e) && (e = dy(t, e), t.parent_ || py(t, e)), t.patches_ && ty("Patches").generateReplacementPatches_(n[Fv].base_, e, t.patches_, t.inversePatches_)) : e = dy(t, n, []), oy(t), t.patches_ && t.patchListener_(t.patches_, t.inversePatches_), e === Nv ? void 0 : e;
}
function dy(e, t, n) {
	if ($v(t)) return t;
	let r = t[Fv];
	if (!r) return Hv(t, (i, a) => fy(e, r, t, i, a, n)), t;
	if (r.scope_ !== e) return t;
	if (!r.modified_) return py(e, r.base_, !0), r.base_;
	if (!r.finalized_) {
		r.finalized_ = !0, r.scope_.unfinalizedDrafts_--;
		let t = r.copy_, i = t, a = !1;
		r.type_ === 3 && (i = new Set(t), t.clear(), a = !0), Hv(i, (i, o) => fy(e, r, t, i, o, n, a)), py(e, t, !1), n && e.patches_ && ty("Patches").generatePatches_(r, n, e.patches_, e.inversePatches_);
	}
	return r.copy_;
}
function fy(e, t, n, r, i, a, o) {
	if (Rv(i)) {
		let o = dy(e, i, a && t && t.type_ !== 3 && !Wv(t.assigned_, r) ? a.concat(r) : void 0);
		if (Gv(n, r, o), Rv(o)) e.canAutoFreeze_ = !1;
		else return;
	} else o && n.add(i);
	if (zv(i) && !$v(i)) {
		if (!e.immer_.autoFreeze_ && e.unfinalizedDrafts_ < 1) return;
		dy(e, i), (!t || !t.scope_.parent_) && typeof r != "symbol" && Object.prototype.propertyIsEnumerable.call(n, r) && py(e, i);
	}
}
function py(e, t, n = !1) {
	!e.parent_ && e.immer_.autoFreeze_ && e.canAutoFreeze_ && Zv(t, n);
}
function my(e, t) {
	let n = Array.isArray(e), r = {
		type_: +!!n,
		scope_: t ? t.scope_ : ry(),
		modified_: !1,
		finalized_: !1,
		assigned_: {},
		parent_: t,
		base_: e,
		draft_: null,
		copy_: null,
		revoke_: null,
		isManual_: !1
	}, i = r, a = hy;
	n && (i = [r], a = gy);
	let { revoke: o, proxy: s } = Proxy.revocable(i, a);
	return r.draft_ = s, r.revoke_ = o, s;
}
var hy = {
	get(e, t) {
		if (t === Fv) return e;
		let n = Yv(e);
		if (!Wv(n, t)) return vy(e, n, t);
		let r = n[t];
		return e.finalized_ || !zv(r) ? r : r === _y(e.base_, t) ? (xy(e), e.copy_[t] = Cy(r, e)) : r;
	},
	has(e, t) {
		return t in Yv(e);
	},
	ownKeys(e) {
		return Reflect.ownKeys(Yv(e));
	},
	set(e, t, n) {
		let r = yy(Yv(e), t);
		if (r?.set) return r.set.call(e.draft_, n), !0;
		if (!e.modified_) {
			let r = _y(Yv(e), t), i = r?.[Fv];
			if (i && i.base_ === n) return e.copy_[t] = n, e.assigned_[t] = !1, !0;
			if (Kv(n, r) && (n !== void 0 || Wv(e.base_, t))) return !0;
			xy(e), by(e);
		}
		return e.copy_[t] === n && (n !== void 0 || t in e.copy_) || Number.isNaN(n) && Number.isNaN(e.copy_[t]) || (e.copy_[t] = n, e.assigned_[t] = !0), !0;
	},
	deleteProperty(e, t) {
		return _y(e.base_, t) !== void 0 || t in e.base_ ? (e.assigned_[t] = !1, xy(e), by(e)) : delete e.assigned_[t], e.copy_ && delete e.copy_[t], !0;
	},
	getOwnPropertyDescriptor(e, t) {
		let n = Yv(e), r = Reflect.getOwnPropertyDescriptor(n, t);
		return r && {
			writable: !0,
			configurable: e.type_ !== 1 || t !== "length",
			enumerable: r.enumerable,
			value: n[t]
		};
	},
	defineProperty() {
		Iv(11);
	},
	getPrototypeOf(e) {
		return Lv(e.base_);
	},
	setPrototypeOf() {
		Iv(12);
	}
}, gy = {};
Hv(hy, (e, t) => {
	gy[e] = function() {
		return arguments[0] = arguments[0][0], t.apply(this, arguments);
	};
}), gy.deleteProperty = function(e, t) {
	return gy.set.call(this, e, t, void 0);
}, gy.set = function(e, t, n) {
	return hy.set.call(this, e[0], t, n, e[0]);
};
function _y(e, t) {
	let n = e[Fv];
	return (n ? Yv(n) : e)[t];
}
function vy(e, t, n) {
	let r = yy(t, n);
	return r ? "value" in r ? r.value : r.get?.call(e.draft_) : void 0;
}
function yy(e, t) {
	if (!(t in e)) return;
	let n = Lv(e);
	for (; n;) {
		let e = Object.getOwnPropertyDescriptor(n, t);
		if (e) return e;
		n = Lv(n);
	}
}
function by(e) {
	e.modified_ || (e.modified_ = !0, e.parent_ && by(e.parent_));
}
function xy(e) {
	e.copy_ ||= Xv(e.base_, e.scope_.immer_.useStrictShallowCopy_);
}
var Sy = class {
	constructor(e) {
		this.autoFreeze_ = !0, this.useStrictShallowCopy_ = !1, this.produce = (e, t, n) => {
			if (typeof e == "function" && typeof t != "function") {
				let n = t;
				t = e;
				let r = this;
				return function(e = n, ...i) {
					return r.produce(e, (e) => t.call(this, e, ...i));
				};
			}
			typeof t != "function" && Iv(6), n !== void 0 && typeof n != "function" && Iv(7);
			let r;
			if (zv(e)) {
				let i = cy(this), a = Cy(e, void 0), o = !0;
				try {
					r = t(a), o = !1;
				} finally {
					o ? oy(i) : sy(i);
				}
				return ay(i, n), uy(r, i);
			}
			if (!e || typeof e != "object") {
				if (r = t(e), r === void 0 && (r = e), r === Nv && (r = void 0), this.autoFreeze_ && Zv(r, !0), n) {
					let t = [], i = [];
					ty("Patches").generateReplacementPatches_(e, r, t, i), n(t, i);
				}
				return r;
			}
			Iv(1, e);
		}, this.produceWithPatches = (e, t) => {
			if (typeof e == "function") return (t, ...n) => this.produceWithPatches(t, (t) => e(t, ...n));
			let n, r;
			return [
				this.produce(e, t, (e, t) => {
					n = e, r = t;
				}),
				n,
				r
			];
		}, typeof e?.autoFreeze == "boolean" && this.setAutoFreeze(e.autoFreeze), typeof e?.useStrictShallowCopy == "boolean" && this.setUseStrictShallowCopy(e.useStrictShallowCopy);
	}
	createDraft(e) {
		zv(e) || Iv(8), Rv(e) && (e = wy(e));
		let t = cy(this), n = Cy(e, void 0);
		return n[Fv].isManual_ = !0, sy(t), n;
	}
	finishDraft(e, t) {
		let n = e && e[Fv];
		(!n || !n.isManual_) && Iv(9);
		let { scope_: r } = n;
		return ay(r, t), uy(void 0, r);
	}
	setAutoFreeze(e) {
		this.autoFreeze_ = e;
	}
	setUseStrictShallowCopy(e) {
		this.useStrictShallowCopy_ = e;
	}
	applyPatches(e, t) {
		let n;
		for (n = t.length - 1; n >= 0; n--) {
			let r = t[n];
			if (r.path.length === 0 && r.op === "replace") {
				e = r.value;
				break;
			}
		}
		n > -1 && (t = t.slice(n + 1));
		let r = ty("Patches").applyPatches_;
		return Rv(e) ? r(e, t) : this.produce(e, (e) => r(e, t));
	}
};
function Cy(e, t) {
	let n = qv(e) ? ty("MapSet").proxyMap_(e, t) : Jv(e) ? ty("MapSet").proxySet_(e, t) : my(e, t);
	return (t ? t.scope_ : ry()).drafts_.push(n), n;
}
function wy(e) {
	return Rv(e) || Iv(10, e), Ty(e);
}
function Ty(e) {
	if (!zv(e) || $v(e)) return e;
	let t = e[Fv], n;
	if (t) {
		if (!t.modified_) return t.base_;
		t.finalized_ = !0, n = Xv(e, t.scope_.immer_.useStrictShallowCopy_);
	} else n = Xv(e, !0);
	return Hv(n, (e, t) => {
		Gv(n, e, Ty(t));
	}), t && (t.finalized_ = !1), n;
}
var Ey = new Sy();
Ey.produce, Ey.produceWithPatches.bind(Ey), Ey.setAutoFreeze.bind(Ey), Ey.setUseStrictShallowCopy.bind(Ey), Ey.applyPatches.bind(Ey), Ey.createDraft.bind(Ey), Ey.finishDraft.bind(Ey);
function Dy(e) {
	return e;
}
function Oy(e, t) {
	var n = Object.keys(e);
	if (Object.getOwnPropertySymbols) {
		var r = Object.getOwnPropertySymbols(e);
		t && (r = r.filter(function(t) {
			return Object.getOwnPropertyDescriptor(e, t).enumerable;
		})), n.push.apply(n, r);
	}
	return n;
}
function ky(e) {
	for (var t = 1; t < arguments.length; t++) {
		var n = arguments[t] == null ? {} : arguments[t];
		t % 2 ? Oy(Object(n), !0).forEach(function(t) {
			I(e, t, n[t]);
		}) : Object.getOwnPropertyDescriptors ? Object.defineProperties(e, Object.getOwnPropertyDescriptors(n)) : Oy(Object(n)).forEach(function(t) {
			Object.defineProperty(e, t, Object.getOwnPropertyDescriptor(n, t));
		});
	}
	return e;
}
var Ay;
(function(e) {
	e.Presets = "Presets";
})(Ay ||= {});
var jy = {
	activePreset: null,
	sequenceSelection: void 0,
	sequenceSelectionName: void 0,
	isSequenceFirstsOnlyNucleoelementsSelected: void 0,
	activePresetMonomerGroup: null,
	groupItemValidations: I(I(I({}, q.BASES, []), q.SUGARS, []), q.PHOSPHATES, []),
	presetsDefault: [],
	presetsCustom: [],
	activeRnaBuilderItem: null,
	activeMonomerKey: null,
	isEditMode: !1,
	uniqueNameError: "",
	invalidPresetError: "",
	invalidPresetNameError: "",
	activePresetForContextMenu: null,
	presetPhosphateFilter: function() {
		var e = w_.getItem(g_);
		return e && en(e) === "object" && typeof e.fivePrime == "boolean" && typeof e.threePrime == "boolean" && typeof e.noPhosphate == "boolean" ? e : {
			fivePrime: !1,
			threePrime: !1,
			noPhosphate: !1
		};
	}()
}, My = I(I(I({}, q.BASES, "base"), q.SUGARS, "sugar"), q.PHOSPHATES, "phosphate"), Ny = sl({
	name: "rna-builder",
	initialState: jy,
	reducers: {
		createNewPreset: function(e) {
			e.activePreset = {
				base: void 0,
				sugar: void 0,
				phosphate: void 0,
				name: "",
				nameInList: ""
			};
		},
		setActivePreset: function(e, t) {
			e.activePreset = ky(ky({}, t.payload), {}, { nameInList: t.payload.name });
		},
		setSequenceSelection: function(e, t) {
			e.sequenceSelection = L(t.payload);
		},
		setSequenceSelectionName: function(e, t) {
			e.sequenceSelectionName = t.payload;
		},
		setIsSequenceFirstsOnlyNucleoelementsSelected: function(e, t) {
			e.isSequenceFirstsOnlyNucleoelementsSelected = t.payload;
		},
		setActivePresetForContextMenu: function(e, t) {
			e.activePresetForContextMenu = t.payload;
		},
		setPresetPhosphateFilter: function(e, t) {
			e.presetPhosphateFilter = t.payload, w_.setItem(g_, t.payload);
		},
		setActivePresetName: function(e, t) {
			e.activePreset.name = t.payload;
		},
		setActiveRnaBuilderItem: function(e, t) {
			e.activeRnaBuilderItem = t.payload;
		},
		recalculateRnaBuilderValidations: function(e, t) {
			var n = wv(t.payload.rnaPreset, t.payload.isEditMode, t.payload.selectedPhosphatePosition ?? ie(t.payload.rnaPreset)), r = n.sugarValidations, i = n.phosphateValidations, a = n.baseValidations;
			e.groupItemValidations[q.SUGARS] = r, e.groupItemValidations[q.BASES] = a, e.groupItemValidations[q.PHOSPHATES] = i;
		},
		setActivePresetMonomerGroup: function(e, t) {
			e.activePresetMonomerGroup = t.payload ? Dy(t.payload) : null;
		},
		savePreset: function(e, t) {
			var n = t.payload, r = ky({}, n);
			if (vv(xv(r)), r.nameInList) {
				var i = e.presetsCustom.findIndex(function(e) {
					return e.name === r.nameInList;
				});
				r.nameInList = r.name, i === -1 ? e.presetsCustom.push(r) : e.presetsCustom.splice(i, 1, r);
			} else e.presetsCustom.push(r);
			e.activePreset && (e.activePreset.nameInList = r.name);
		},
		deletePreset: function(e, t) {
			var n = t.payload;
			yv(n.name);
			var r = e.presetsCustom.findIndex(function(e) {
				return e.name === n.name;
			});
			e.presetsCustom.splice(r, 1), n.nameInList && (e.activePreset = null);
		},
		setIsEditMode: function(e, t) {
			e.isEditMode = t.payload;
		},
		setUniqueNameError: function(e, t) {
			e.uniqueNameError = t.payload;
		},
		setInvalidPresetError: function(e, t) {
			e.invalidPresetError = t.payload;
		},
		setInvalidPresetNameError: function(e, t) {
			e.invalidPresetNameError = t.payload;
		},
		setDefaultPresets: function(e, t) {
			var n = t.payload[0];
			n && (e.presetsDefault.find(function(e) {
				return e.name === n.name;
			}) || (e.presetsDefault = t.payload));
		},
		setCustomPresets: function(e, t) {
			e.presetsCustom = t.payload;
		},
		setFavoritePresetsFromLocalStorage: function(e) {
			var t = w_.getItem(m_);
			t && Array.isArray(t) && (e.presetsDefault = e.presetsDefault.map(function(e) {
				var n = `${e.name}_${Ne.RNA}`;
				return t.find(function(e) {
					return e === n;
				}) ? ky(ky({}, e), {}, { favorite: !0 }) : e;
			}));
		},
		clearFavorites: function(e) {
			e.presetsDefault = [];
		},
		setActiveMonomerKey: function(e, t) {
			e.activeMonomerKey = t.payload;
		},
		togglePresetFavorites: function(e, t) {
			var n = e.presetsDefault.findIndex(function(e) {
				return e.name === t.payload.name;
			}), r = e.presetsCustom.findIndex(function(e) {
				return e.name === t.payload.name;
			});
			if (n >= 0) {
				var i = e.presetsDefault[n].favorite;
				e.presetsDefault[n].favorite = !i;
			} else if (r >= 0) {
				bv(e.presetsCustom[r].name);
				var a = e.presetsCustom[r].favorite;
				e.presetsCustom[r].favorite = !a;
				return;
			}
			var o = `${t.payload.name}_${Ne.RNA}`, s = w_.getItem(m_) ?? [];
			s.some(function(e) {
				return e === o;
			}) ? w_.setItem(m_, s.filter(function(e) {
				return e !== o;
			})) : (s.push(o), w_.setItem(m_, s));
		}
	}
}), Py = function(e) {
	return e.rnaBuilder;
}, Fy = function(e) {
	return e.rnaBuilder.activeRnaBuilderItem;
}, Iy = function(e) {
	return e.rnaBuilder.groupItemValidations;
}, Ly = function(e) {
	return e.rnaBuilder.activePreset;
}, Ry = function(e) {
	return e.rnaBuilder.sequenceSelection;
}, zy = function(e) {
	return e.rnaBuilder.sequenceSelectionName;
}, By = function(e) {
	return e.rnaBuilder.isSequenceFirstsOnlyNucleoelementsSelected;
}, Vy = function(e, t) {
	if (My[t] && e) return e[My[t]];
}, Hy = function(e) {
	return e.rnaBuilder.activePresetMonomerGroup;
}, Uy = function(e) {
	return !!(e.name && e.sugar && (e.base || e.phosphate));
}, Wy = function(e) {
	return e.rnaBuilder.isEditMode;
}, Gy = function(e) {
	if (!e) return "";
	var t = e.sugar?.label ?? e.sugar?.props.MonomerName ?? "", n = e.base?.label ?? e.base?.props.MonomerName ?? "", r = e.phosphate?.label ?? e.phosphate?.props.MonomerName ?? "", i = ie(e), a = t;
	return a += t && r || (t || r) && n ? `(${n})` : n, r && (a = i === "left" ? `${r}${a}` : `${a}${r}`), a;
}, Ky = function(e) {
	return e.rnaBuilder.uniqueNameError;
}, qy = function(e) {
	return e.rnaBuilder.invalidPresetError;
}, Jy = function(e) {
	return e.rnaBuilder.invalidPresetNameError;
}, Yy = function(e) {
	var t = e.rnaBuilder.activePreset;
	return t && !t.nameInList && !t.name && !t.sugar && !t.base && !t.phosphate;
}, Xy = function(e) {
	return e.rnaBuilder.activePresetForContextMenu;
}, Zy = function(e) {
	return e.rnaBuilder.presetPhosphateFilter;
}, Qy = function(e) {
	return e.filter(function(e) {
		return e.favorite;
	});
}, $y = function(e) {
	return e.rnaBuilder.activeMonomerKey;
}, eb = Qt(Py, function(e) {
	var t = e.presetsDefault, n = t === void 0 ? [] : t, r = e.presetsCustom, i = r === void 0 ? [] : r;
	return [].concat(L(n), L(i));
}), tb = Qt(eb, B_, z_, Zy, function(e, t, n, r) {
	var i = t.toLowerCase();
	return e.filter(function(e) {
		var t, r, a, o, s, c = e.name?.toLowerCase(), l = (t = e.sugar) == null || (t = t.label) == null ? void 0 : t.toLowerCase(), u = (r = e.phosphate) == null || (r = r.label) == null ? void 0 : r.toLowerCase(), d = (a = e.base) == null || (a = a.label) == null ? void 0 : a.toLowerCase(), f = (o = e.idtAliases) == null || (o = o.base) == null ? void 0 : o.toLowerCase(), p = e.aliasAxoLabs?.toLowerCase() ?? (c ? n.get(c) : void 0) ?? "", m = e.idtAliases?.modifications, h = m ? Object.values(m).filter(function(e) {
			return typeof e == "string";
		}) : [], g = f;
		if (f && (s = e.name) != null && s.includes("MOE")) {
			var _ = f;
			g = `${m?.endpoint5 ?? `5${_}`}, ${m?.internal ?? `i${_}`}`;
		}
		var v = (i.match(/\//g) ?? []).length, y = i.split("/");
		if (v >= 2 && y[2] !== void 0 && y[2] !== "") return !1;
		if (i.startsWith("/") && i.length > 1) {
			var b = i.slice(1);
			return g?.toLowerCase().startsWith(b) || f?.startsWith(b) || h.some(function(e) {
				return e.toLowerCase().startsWith(b);
			});
		}
		if (i.endsWith("/") && i.length > 1) {
			var x = i.slice(0, -1), S = i[i.length - 2];
			return g?.toLowerCase().endsWith(x) && g[g.length - 1] === S || f?.endsWith(x) && f[f.length - 1] === S || h.some(function(e) {
				return e.toLowerCase().endsWith(x) && e[e.length - 1] === S;
			});
		}
		return i === "/" ? !!e.idtAliases : c?.includes(i) || l?.includes(i) || u?.includes(i) || d?.includes(i) || g?.toLowerCase().includes(i) || p.includes(i);
	}).filter(function(e) {
		if (!r) return !0;
		var t = r.fivePrime, n = r.threePrime, i = r.noPhosphate;
		return t && n && i || !t && !n && !i ? !0 : e.phosphate ? ie(e) === "left" ? t : n : i;
	});
}), J = Ny.actions, nb = J.setActivePreset, rb = J.setSequenceSelection, ib = J.setSequenceSelectionName, ab = J.setIsSequenceFirstsOnlyNucleoelementsSelected;
J.setActivePresetName;
var ob = J.setActiveRnaBuilderItem, sb = J.setActiveMonomerKey, cb = J.recalculateRnaBuilderValidations, lb = J.setActivePresetMonomerGroup, ub = J.savePreset, db = J.deletePreset, fb = J.createNewPreset, pb = J.setIsEditMode, mb = J.setUniqueNameError, hb = J.setInvalidPresetError, gb = J.setInvalidPresetNameError, _b = J.setDefaultPresets, vb = J.setCustomPresets, yb = J.setActivePresetForContextMenu, bb = J.setPresetPhosphateFilter, xb = J.togglePresetFavorites, Sb = J.setFavoritePresetsFromLocalStorage, Cb = J.clearFavorites, wb = Ny.reducer;
function Tb() {
	var e = arguments.length > 0 && arguments[0] !== void 0 ? arguments[0] : {};
	return $c({
		reducer: {
			editor: l_,
			modal: dv,
			library: Y_,
			rnaBuilder: wb
		},
		middleware: function(e) {
			return e({ serializableCheck: !1 }).concat(pv);
		},
		preloadedState: e
	});
}
var Eb = Tb(), Y = {
	colorA: {
		regular: "#5ADC11",
		hover: "#4FC218"
	},
	colorCM: {
		regular: "#59D0FF",
		hover: "#3CB9EB"
	},
	colorDQ: {
		regular: "#AD4551",
		hover: "#AB0014"
	},
	colorEN: {
		regular: "#93F5F5",
		hover: "#00F0F0"
	},
	colorFY: {
		regular: "#5656BF",
		hover: "#2626BF"
	},
	colorGX: {
		regular: "#FFE97B",
		hover: "#F8DC50"
	},
	colorH: {
		regular: "#BFC9FF",
		hover: "#99AAFF"
	},
	colorILV: {
		regular: "#50E576",
		hover: "#00D936"
	},
	colorKR: {
		regular: "#365CFF",
		hover: "#002CEB"
	},
	colorP: {
		regular: "#F2C5B6",
		hover: "#FFA98C"
	},
	colorST: {
		regular: "#FF8D8D",
		hover: "#ED6868"
	},
	colorW: {
		regular: "#99458B",
		hover: "#7F006B"
	},
	colorU: {
		regular: "#FF973C",
		hover: "#2EE55D"
	},
	colorX: {
		regular: "#CAD3DD",
		hover: "#B8BBCC"
	},
	chem: {
		regular: "#333333",
		hover: "#555555"
	},
	default: {
		regular: "#CCCBD6",
		hover: "#B8BBCC"
	}
}, Db = {
	D: {
		regular: "#FF8C69",
		hover: "#0097A8"
	},
	E: {
		regular: "#DC143C",
		hover: "#0097A8"
	},
	K: {
		regular: "#B0E0E6",
		hover: "#0097A8"
	},
	H: {
		regular: "#007FFF",
		hover: "#0097A8"
	},
	O: {
		regular: "#2A52BE",
		hover: "#0097A8"
	},
	R: {
		regular: "#0A12FF",
		hover: "#0097A8"
	},
	Q: {
		regular: "#EDB4ED",
		hover: "#0097A8"
	},
	Y: {
		regular: "#D65CBC",
		hover: "#0097A8"
	},
	U: {
		regular: "#CA7DE3",
		hover: "#0097A8"
	},
	S: {
		regular: "#9966CC",
		hover: "#0097A8"
	},
	C: {
		regular: "#BF00FF",
		hover: "#0097A8"
	},
	N: {
		regular: "#800080",
		hover: "#0097A8"
	},
	T: {
		regular: "#FF00FF",
		hover: "#0097A8"
	},
	L: {
		regular: "#7FFF00",
		hover: "#0097A8"
	},
	I: {
		regular: "#4CBB17",
		hover: "#0097A8"
	},
	F: {
		regular: "#008A00",
		hover: "#0097A8"
	},
	A: {
		regular: "#008080",
		hover: "#0097A8"
	},
	W: {
		regular: "#50E576",
		hover: "#0097A8"
	},
	P: {
		regular: "#D2D900",
		hover: "#0097A8"
	},
	G: {
		regular: "#BDB76B",
		hover: "#0097A8"
	},
	M: {
		regular: "#FFF600",
		hover: "#0097A8"
	},
	V: {
		regular: "#FFD700",
		hover: "#0097A8"
	}
}, Ob = {
	color: {
		background: {
			canvas: "#F5F5F5",
			primary: "#FFFFFF",
			secondary: "#F8FEFF",
			overlay: "rgba(94,94,94,.8)"
		},
		border: {
			primary: "#CAD3DD",
			secondary: "#7C7C7F"
		},
		text: {
			primary: "#333333",
			secondary: "#167782",
			light: "#585858",
			dark: "#000000",
			error: "#FF4A4A",
			lightgrey: "#7C7C7F"
		},
		tab: {
			regular: "#FFFFFF",
			active: "#E1E5EA",
			hover: "#00838F",
			content: "#EFF2F5"
		},
		scroll: {
			regular: "#717171",
			inactive: "#DDDDDD"
		},
		button: {
			primary: {
				active: "#167782",
				hover: "#00838F",
				clicked: "#4FB3BF",
				disabled: "rgba(113, 113, 113, 0.4)"
			},
			secondary: {
				active: "#585858",
				hover: "#333333",
				clicked: "#AEAEAE",
				disabled: "rgba(113, 113, 113, 0.4)"
			},
			group: {
				active: "#167782",
				hover: "#2E858F"
			},
			transparent: { active: "transparent" },
			text: {
				primary: "#FFFFFF",
				secondary: "#005662",
				disabled: "#7A7A7A"
			}
		},
		dropdown: {
			primary: "#333333",
			secondary: "#FFFFFF",
			hover: "#DDDDDD",
			disabled: "#7A7A7A"
		},
		tooltip: {
			background: "#FFFFFF",
			text: "#333333"
		},
		link: {
			active: "#00838F",
			hover: "#005662"
		},
		divider: "#AEAEAE",
		spinner: "#005662",
		error: "#FF4A4A",
		input: {
			text: {
				default: "#585858",
				active: "#333333",
				disabled: "#585858",
				error: "#FF4A4A"
			},
			background: {
				primary: "#FFFFFF",
				default: "#EFF2F5",
				hover: "#DDDDDD",
				disabled: "#eff2f5"
			},
			border: {
				regular: "#cad3dd",
				active: "#FFFFFF",
				hover: "#43b5c0",
				focus: "#EFF2F5",
				error: "#FF4A4A"
			}
		},
		icon: {
			grey: "#B4B9D6",
			hover: "#005662",
			active: "#525252",
			activeMenu: "#005662",
			clicked: "#FFFFFF",
			disabled: "rgba(82, 82, 82, 0.4)"
		},
		monomer: { default: "#C8C8C8" },
		editMode: { sequenceInRNABuilder: "#99d7dc" }
	},
	font: {
		size: {
			small: "10px",
			regular: "12px",
			medium: "14px",
			xsmall: "6px"
		},
		family: {
			montserrat: "Montserrat, sans-serif",
			inter: "Inter, FreeSans, Arimo, 'Droid Sans', Helvetica, 'Helvetica Neue',\nArial, sans-serif",
			roboto: "Roboto, FreeSans, Arimo, Droid Sans, Helvetica, Helvetica Neue, Arial, sans-serif"
		},
		weight: {
			light: 300,
			regular: 400,
			bold: 600
		}
	},
	monomer: { color: {
		A: Y.colorA,
		C: Y.colorCM,
		M: Y.colorCM,
		D: Y.colorDQ,
		Q: Y.colorDQ,
		E: Y.colorEN,
		N: Y.colorEN,
		F: Y.colorFY,
		Y: Y.colorFY,
		G: Y.colorGX,
		X: Y.colorX,
		Other: Y.colorX,
		H: Y.colorH,
		I: Y.colorILV,
		L: Y.colorILV,
		V: Y.colorILV,
		K: Y.colorKR,
		R: Y.colorKR,
		P: Y.colorP,
		S: Y.colorST,
		T: Y.colorST,
		W: Y.colorW,
		U: Y.colorU,
		CHEM: Y.chem,
		default: Y.default
	} },
	peptide: { color: {
		D: Db.D,
		E: Db.E,
		K: Db.K,
		H: Db.H,
		O: Db.O,
		R: Db.R,
		Q: Db.Q,
		Y: Db.Y,
		U: Db.U,
		S: Db.S,
		C: Db.C,
		N: Db.N,
		T: Db.T,
		L: Db.L,
		I: Db.I,
		F: Db.F,
		A: Db.A,
		W: Db.W,
		P: Db.P,
		G: Db.G,
		M: Db.M,
		V: Db.V,
		Other: Y.colorX
	} },
	border: {
		regular: "1px solid #CAD3DD",
		small: "1px solid #E1E5EA",
		radius: { regular: "4px" }
	},
	shadow: {
		regular: "0px 1px 1px rgba(197, 203, 207, 0.7)",
		mainLayoutBlocks: "0px 2px 5px rgba(103, 104, 132, 0.15)"
	},
	outline: {
		small: "1px solid #B4B9D6",
		medium: "2px solid #B4B9D6",
		color: "#B4B9D6",
		selected: {
			color: "#167782",
			small: "1px solid #167782",
			medium: "2px solid #167782"
		},
		grey: { small: "1px solid #585858" }
	},
	transition: { regular: "all .3s" },
	zIndex: {
		base: 0,
		toolbar: 10,
		sticky: 100,
		overlay: 200,
		modal: 1e3,
		critical: 9999
	}
}, kb = {}, Ab = function(e) {
	return Bn({
		all: "unset",
		".Ketcher-polymer-editor-root": {
			all: "unset",
			fontSize: e.ketcher.font.size.medium,
			fontFamily: e.ketcher.font.family.inter,
			fontWeight: e.ketcher.font.weight.regular,
			backgroundColor: e.ketcher.color.background.primary,
			color: e.ketcher.color.text.primary,
			boxSizing: "border-box"
		},
		":where(.Ketcher-polymer-editor-root) div": { boxSizing: "border-box" },
		":where(.Ketcher-polymer-editor-root) input": {
			fontFamily: e.ketcher.font.family.inter,
			fontWeight: e.ketcher.font.weight.regular,
			fontSize: e.ketcher.font.size.regular,
			boxSizing: "border-box"
		},
		":where(.Ketcher-polymer-editor-root) h1": { fontSize: 96 },
		":where(.Ketcher-polymer-editor-root) h2": { fontSize: 60 },
		":where(.Ketcher-polymer-editor-root) h3": { fontSize: 48 },
		":where(.Ketcher-polymer-editor-root) h4": { fontSize: 34 },
		":where(.Ketcher-polymer-editor-root) h5": { fontSize: 24 },
		":where(.Ketcher-polymer-editor-root) h6": {
			fontSize: 20,
			fontWeight: e.ketcher.font.weight.bold
		},
		":where(.Ketcher-polymer-editor-root) p": { fontSize: e.ketcher.font.size.regular },
		":where(.Ketcher-polymer-editor-root) button": {
			textTransform: "uppercase",
			fontWeight: e.ketcher.font.weight.bold
		}
	}, "", "");
}, jb = "254px", Mb = "100px", Nb = z("div", { target: "e1vkl5kv5" })("width:", jb, ";height:calc(100% - 16px);display:flex;flex-direction:column;background-color:", function(e) {
	return e.theme.ketcher.color.background.primary;
}, ";box-shadow:", function(e) {
	return e.theme.ketcher.shadow.mainLayoutBlocks;
}, ";border-radius:4px;z-index:", function(e) {
	return e.theme.ketcher.zIndex.toolbar;
}, ";"), Pb = z("div", { target: "e1vkl5kv4" })({
	name: "n1y6qf",
	styles: "padding:10px 0 10px 8px;position:relative;display:flex;align-items:center;gap:8px"
}), Fb = z("div", { target: "e1vkl5kv3" })("height:24px;display:flex;flex-grow:1;gap:4px;align-items:center;padding:4px;background-color:", function(e) {
	return e.theme.ketcher.color.input.background.default;
}, ";border-radius:4px;&:hover,&:has(input:focus){outline:", function(e) {
	return e.theme.ketcher.outline.selected.small;
}, ";}"), Ib = z("button", { target: "e1vkl5kv2" })("height:24px;display:flex;align-items:center;gap:2px;border:none;border-radius:4px 0 0 4px;cursor:pointer;background-color:#e2e5e9;text-transform:none;font-weight:", function(e) {
	return e.theme.ketcher.font.weight.regular;
}, ";font-size:", function(e) {
	return e.theme.ketcher.font.size.regular;
}, ";color:", function(e) {
	return e.theme.ketcher.color.text.secondary;
}, ";"), Lb = z(P, { target: "e1vkl5kv1" })("height:16px;width:16px;color:", function(e) {
	return e.theme.ketcher.color.text.secondary;
}, ";"), Rb = z(le, { target: "e1vkl5kv0" })({
	name: "pmmg8c",
	styles: "flex-grow:1;padding:0;margin:0;background-color:transparent;border:none;outline:none;&:hover{outline:none;}&:focus{outline:none;}"
}), zb = ["children"];
function Bb(e, t) {
	var n = Object.keys(e);
	if (Object.getOwnPropertySymbols) {
		var r = Object.getOwnPropertySymbols(e);
		t && (r = r.filter(function(t) {
			return Object.getOwnPropertyDescriptor(e, t).enumerable;
		})), n.push.apply(n, r);
	}
	return n;
}
function Vb(e) {
	for (var t = 1; t < arguments.length; t++) {
		var n = arguments[t] == null ? {} : arguments[t];
		t % 2 ? Bb(Object(n), !0).forEach(function(t) {
			I(e, t, n[t]);
		}) : Object.getOwnPropertyDescriptors ? Object.defineProperties(e, Object.getOwnPropertyDescriptors(n)) : Bb(Object(n)).forEach(function(t) {
			Object.defineProperty(e, t, Object.getOwnPropertyDescriptor(n, t));
		});
	}
	return e;
}
var Hb = z("div", { target: "e1pv9pa12" })(function(e) {
	var t = e.fullWidth, n = e.withPaddingRight;
	return {
		width: t ? "100%" : "fit-content",
		display: "flex",
		flexDirection: "column",
		justifyContent: "space-between",
		paddingRight: n ? "12px" : 0,
		overflow: t ? "hidden" : "initial"
	};
}, ""), Ub = z("div", { target: "e1pv9pa11" })(function(e) {
	return {
		height: "100%",
		width: "100%",
		position: "relative",
		padding: "12px",
		paddingBottom: 0,
		backgroundColor: e.theme.ketcher.color.background.canvas,
		display: "flex",
		justifyContent: "space-between",
		containerType: "size",
		overflow: "clip"
	};
}, ""), Wb = z("div", { target: "e1pv9pa10" })(function(e) {
	return {
		height: "100%",
		width: "100%",
		position: "relative",
		paddingBottom: 0,
		backgroundColor: e.theme.ketcher.color.background.canvas,
		display: "flex",
		justifyContent: "space-between",
		columnGap: "3px"
	};
}, ""), Gb = z("div", { target: "e1pv9pa9" })(function(e) {
	var t = e.hide;
	return {
		height: "100%",
		width: "fit-content",
		display: t !== void 0 && t ? "none" : "flex",
		flexDirection: "column"
	};
}, ""), Kb = z(Gb, { target: "e1pv9pa8" })(""), qb = z(Gb, { target: "e1pv9pa7" })(""), Jb = z("div", { target: "e1pv9pa6" })({
	name: "oixulj",
	styles: "display:flex;justify-content:space-between;width:100cqw"
}), Yb = z("div", { target: "e1pv9pa5" })(function(e) {
	var t = e.shortened, n = t !== void 0 && t, r = e.theme;
	return {
		height: "36px",
		width: n ? "100%" : `calc(100% - ${Mb})`,
		marginBottom: "6px",
		display: "flex",
		alignItems: "center",
		backgroundColor: "#FFFFFF",
		boxShadow: r.ketcher.shadow.mainLayoutBlocks,
		borderRadius: "4px",
		overflowX: "hidden"
	};
}, ""), Xb = z("div", { target: "e1pv9pa4" })("width:42px;height:36px;display:flex;position:relative;right:0;cursor:pointer;background:white;box-shadow:", function(e) {
	return e.theme.ketcher.shadow.mainLayoutBlocks;
}, ";border-radius:4px;"), Zb = z("div", { target: "e1pv9pa3" })({
	name: "1gavlve",
	styles: "&:not(:empty){margin-bottom:15px;}"
}), Qb = z("div", { target: "e1pv9pa2" })({
	name: "nc15h",
	styles: "height:100%;width:100%;position:relative;overflow:hidden"
}), $b = z("div", { target: "e1pv9pa1" })({
	name: "0",
	styles: ""
}), ex = z("div", { target: "e1pv9pa0" })({
	name: "1k18kha",
	styles: "height:40px"
}), tx = function(e) {
	var t = fn({ threshold: 1 }), n = R(t, 2), r = n[0], i = n[1], a = fn({ threshold: 1 }), o = R(a, 2), s = o[0], c = o[1], l = e.children, u = ve(e, zb), d = (0, B.useRef)(null), f = 300;
	return W("div", {
		style: {
			display: "flex",
			position: "relative"
		},
		children: [W(Yb, Vb(Vb({}, u), {}, {
			ref: d,
			children: [
				U("span", { ref: r }),
				U(Jb, { children: U(H, { children: l }) }),
				U("span", { ref: s })
			]
		})), !i || !c ? U(Xb, { children: U(m, {
			startInView: i,
			endInView: c,
			scrollBack: function(e) {
				d.current && (d.current.scrollLeft -= f * e / 1e3);
			},
			scrollForward: function(e) {
				d.current && (d.current.scrollLeft += f * e / 1e3);
			},
			isLeftRight: !0
		}) }) : null]
	});
}, nx = function(e) {
	var t = e.children, n = {
		Left: null,
		Main: null,
		Right: null,
		Top: null,
		Bottom: null,
		InsideRoot: null
	};
	return B.Children.forEach(t, function(e) {
		e.type === Kb ? n.Left = e : e.type === qb ? n.Right = e : e.type === tx ? n.Top = e : e.type === Zb ? n.Bottom = e : e.type === Qb ? n.Main = e : e.type === $b && (n.InsideRoot = e);
	}), W(Ub, { children: [
		W(Hb, {
			fullWidth: !0,
			withPaddingRight: !0,
			children: [
				n.Top,
				W(Wb, { children: [
					n.Left,
					U(ex, {}),
					n.Main
				] }),
				n.Bottom
			]
		}),
		U(Hb, { children: n.Right }),
		n.InsideRoot
	] });
};
nx.Left = Kb, nx.Top = tx, nx.Bottom = Zb, nx.Right = qb, nx.Main = Qb, nx.InsideRoot = $b;
var rx = {
	tabPanelDiv: "TabPanel-module_tabPanelDiv__wMffZ",
	tabPanelBox: "TabPanel-module_tabPanelBox__LY-BB"
}, ix = function(e) {
	var t = e.children, n = e.value, r = e.index;
	return U("div", {
		className: rx.tabPanelDiv,
		role: "tabpanel",
		hidden: n !== r,
		id: r.toString(),
		children: n === r && U(lr, {
			className: rx.tabPanelBox,
			children: U(H, { children: t })
		})
	});
}, ax = z(kn, {
	shouldForwardProp: function(e) {
		return e !== "isLayoutToRight";
	},
	target: "e1rrs7vg3"
})("height:32px;min-height:32px;list-style-type:none;margin:0;padding:4px 8px 0 8px;border-bottom:", function(e) {
	return `1px solid ${e.theme.ketcher.color.border.primary}`;
}, ";overflow:unset;& .MuiTabs-scroller,& .MuiTabs-flexContainer{height:100%;overflow:unset!important;}& .MuiTabs-flexContainer{justify-content:", function(e) {
	return e.isLayoutToRight ? "flex-end" : "flex-start";
}, ";padding-right:", function(e) {
	return e.isLayoutToRight ? "16px" : "0";
}, ";}& .MuiTabs-indicator{display:none;}"), ox = z(Et, {
	shouldForwardProp: function(e) {
		return e !== "isLayoutToRight";
	},
	target: "e1rrs7vg2"
})("min-height:24px;min-width:0;position:relative;padding:7px 12px;font-size:", function(e) {
	return e.theme.ketcher.font.size.regular;
}, ";text-transform:none;cursor:pointer;text-align:center;background-color:", function(e) {
	return e.theme.ketcher.color.tab.regular;
}, ";color:", function(e) {
	return e.theme.ketcher.color.text.light;
}, ";list-style-type:none;margin-left:1px;align-items:center;flex:", function(e) {
	return e.isLayoutToRight ? void 0 : "1 1 auto;";
}, ";border:1px solid transparent;border-bottom:none;border-radius:4px 4px 0 0;&:first-of-type{margin-left:0;}&:hover{background-color:", function(e) {
	return e.theme.ketcher.color.tab.regular;
}, ";color:", function(e) {
	return e.theme.ketcher.color.text.primary;
}, ";border-color:", function(e) {
	return e.theme.ketcher.color.border.primary;
}, ";}&.Mui-selected{background-color:", function(e) {
	return e.theme.ketcher.color.tab.active;
}, ";color:", function(e) {
	return e.theme.ketcher.color.text.primary;
}, ";border-color:", function(e) {
	return e.theme.ketcher.color.border.primary;
}, ";margin-bottom:-1px;padding-bottom:8px;&::after{content:'';position:absolute;left:0;bottom:-1px;height:1px;background-color:", function(e) {
	return e.theme.ketcher.color.tab.active;
}, ";}}&[data-tab='Favorites']{font-size:16px;color:#faa500;}"), sx = z(Et, { target: "e1rrs7vg1" })({
	name: "2934o7",
	styles: "width:0;height:0;min-width:0;min-height:0;padding:0;margin:0;visibility:hidden"
}), cx = z("div", { target: "e1rrs7vg0" })({
	name: "2r6rpv",
	styles: "display:flex;flex-direction:row;flex-wrap:wrap;justify-content:flex-start;width:100%;height:100%"
});
function lx(e, t) {
	var n = Object.keys(e);
	if (Object.getOwnPropertySymbols) {
		var r = Object.getOwnPropertySymbols(e);
		t && (r = r.filter(function(t) {
			return Object.getOwnPropertyDescriptor(e, t).enumerable;
		})), n.push.apply(n, r);
	}
	return n;
}
function ux(e) {
	for (var t = 1; t < arguments.length; t++) {
		var n = arguments[t] == null ? {} : arguments[t];
		t % 2 ? lx(Object(n), !0).forEach(function(t) {
			I(e, t, n[t]);
		}) : Object.getOwnPropertyDescriptors ? Object.defineProperties(e, Object.getOwnPropertyDescriptors(n)) : lx(Object(n)).forEach(function(t) {
			Object.defineProperty(e, t, Object.getOwnPropertyDescriptor(n, t));
		});
	}
	return e;
}
var dx = function(e) {
	return {
		id: `simple-tab-${e}`,
		"aria-controls": `simple-tabpanel-${e}`
	};
}, fx = (0, B.memo)(function(e) {
	var t = e.tabs, n = e.selectedTabIndex, r = e.isLayoutToRight, i = e.onChange, a = t[n], o = a?.component, s = a?.props;
	return W(H, { children: [W(ax, {
		value: n,
		onChange: i,
		isLayoutToRight: r,
		children: [t.map(function(e, t) {
			return U(ox, ux({
				label: e.caption,
				title: e.tooltip,
				isLayoutToRight: r,
				"data-testid": e.testId,
				"data-tab": e.tooltip
			}, dx(t)), e.caption || e.testId);
		}), U(sx, { value: -1 })]
	}), a && U(ix, {
		value: n,
		index: n,
		children: U(cx, { children: U(o, ux({}, s)) })
	})] });
}), px = function() {};
function mx(e, t) {
	var n = Object.keys(e);
	if (Object.getOwnPropertySymbols) {
		var r = Object.getOwnPropertySymbols(e);
		t && (r = r.filter(function(t) {
			return Object.getOwnPropertyDescriptor(e, t).enumerable;
		})), n.push.apply(n, r);
	}
	return n;
}
function hx(e) {
	for (var t = 1; t < arguments.length; t++) {
		var n = arguments[t] == null ? {} : arguments[t];
		t % 2 ? mx(Object(n), !0).forEach(function(t) {
			I(e, t, n[t]);
		}) : Object.getOwnPropertyDescriptors ? Object.defineProperties(e, Object.getOwnPropertyDescriptors(n)) : mx(Object(n)).forEach(function(t) {
			Object.defineProperty(e, t, Object.getOwnPropertyDescriptor(n, t));
		});
	}
	return e;
}
var gx = function(e, t, n) {
	var r = new Map(e.map(function(e) {
		var t;
		if (w(e)) t = _t(e.id);
		else {
			var n = e;
			t = zn(n.props.id || k_(n));
		}
		return [t, e];
	}));
	return t.filter(function(e) {
		return e.templates.every(function(e) {
			return !!r.get(e.$ref);
		});
	}).map(function(e) {
		var t = new Map(e.templates.map(function(e) {
			var t = r.get(e.$ref), n = ct(t);
			return [R(n, 3)[2], t];
		})), i = t.get(st.Sugar), a = t.get(st.Base), o = t.get(st.Phosphate), s = e.connections ?? Xe({
			base: a,
			sugar: i,
			phosphate: o
		});
		return hx(hx(hx({}, {
			base: a ? hx(hx({}, a), {}, { label: a.label }) : void 0,
			name: e.name,
			phosphate: o ? hx(hx({}, o), {}, { label: o.label }) : void 0,
			connections: s,
			sugar: i ? hx(hx({}, i), {}, { label: i.label }) : void 0,
			phosphatePosition: ie({
				sugar: i,
				phosphate: o,
				connections: s
			}),
			favorite: e.favorite,
			default: n || e.default
		}), e.idtAliases && { idtAliases: e.idtAliases }), e.aliasAxoLabs && { aliasAxoLabs: e.aliasAxoLabs });
	});
}, _x = function(e) {
	return Object.entries(e).filter(function(e) {
		var t = R(e, 2);
		return t[0], !!t[1];
	}).map(function(e) {
		return R(e, 1)[0];
	});
}, vx = function(e) {
	return e && e.replace(/(?:^\/+)|(?:\/+$)/g, "");
}, X = function() {
	return Rt();
}, Z = dt;
function yx() {
	var e, t = Z(Gg), n = Z(K), r = Z(Jg), i;
	try {
		i = nt.getKetcher(t);
	} catch (e) {
		tt.error(`Failed to get ketcher instance with id ${t}`, e);
	}
	var a = (e = i) != null && (e = e.editor) != null && e.struct().isBlank() ? yn : pe, o = (0, B.useState)(r || a), s = R(o, 2), c = s[0], l = s[1], u = (0, B.useCallback)(function(e) {
		l(e);
	}, []);
	return (0, B.useEffect)(function() {
		return n?.events.layoutModeChange.add(u), function() {
			u(yn), n?.events.layoutModeChange.remove(u);
		};
	}, [u, n]), c;
}
function bx() {
	var e = Z(K), t = Z(Kg), n = (0, B.useState)(t), r = R(n, 2), i = r[0], a = r[1], o = (0, B.useCallback)(function(e) {
		a(e);
	}, []);
	return (0, B.useEffect)(function() {
		return e?.events.toggleSequenceEditInRNABuilderMode.add(o), function() {
			e?.events.toggleSequenceEditInRNABuilderMode.remove(o);
		};
	}, [o, e]), i;
}
var xx = B.createContext({}), Sx = (0, B.createContext)({
	width: 0,
	height: 0
}), Cx = function(e) {
	var t = e.children, n = e.rootRef, r = e.isMacromoleculesEditorTurnedOn, i = (0, B.useState)({
		width: 0,
		height: 0
	}), a = R(i, 2), o = a[0], s = a[1], c = (0, B.useCallback)(function() {
		if (n != null && n.current) {
			var e = n.current.getBoundingClientRect(), t = e.width, r = e.height;
			s({
				width: t,
				height: r
			});
		}
	}, [n]), l = (0, B.useCallback)((0, ws.debounce)(c, 100), [c]);
	return (0, B.useEffect)(function() {
		c();
	}, [r]), (0, B.useEffect)(function() {
		return l(), window.addEventListener("resize", l), function() {
			window.removeEventListener("resize", l);
		};
	}, [l]), U(Sx.Provider, {
		value: o,
		children: t
	});
}, wx = function() {
	return (0, B.useContext)(Sx).height < 720;
}, Tx = function(e) {
	if (e) return Array.isArray(e) ? e.join(", ") : e;
}, Ex = z("div", { target: "e719szw4" })("background:white;height:48px;text-align:center;cursor:", function(e) {
	var t = e.disabled, n = e.isDragging;
	return t ? "default" : n ? "grabbing !important" : "pointer";
}, ";opacity:", function(e) {
	return e.disabled ? "0.4" : "1";
}, ";display:flex;justify-content:space-between;align-items:center;font-size:", function(e) {
	return e.theme.ketcher.font.size.small;
}, ";color:", function(e) {
	return e.theme.ketcher.color.text.primary;
}, ";position:relative;overflow:hidden;border-radius:4px;box-shadow:0 2px 5px 0 rgba(103, 104, 132, 0.149);margin:0;user-select:none;border-color:#167782;border-width:", function(e) {
	return e.selected ? "2px 2px 2px" : "0px";
}, ";border-style:solid;box-sizing:border-box;z-index:", function(e) {
	return e.selected ? 2 : void 0;
}, ";", function(e) {
	return e.isDragging && "\n    &, & * {\n      pointer-events: none !important;\n      cursor: grabbing !important;\n    }\n  ";
}, " .hidden & .star{visibility:hidden!important;}&:hover{outline:1px solid #b4b9d6;>.star,.autochain{visibility:visible;opacity:1;}}&::after{content:'';display:block;position:absolute;top:0;left:0;width:100%;height:8px;border-bottom:", function(e) {
	return e.isVariantMonomer ? "1px solid #CAD3DD" : "none";
}, ";background:", function(e) {
	var t, n = e.code, r = e.theme, i = e.item;
	return i ? i.props?.MonomerType === "PEPTIDE" && (t = r.ketcher.peptide.color[n]) != null && t.regular ? r.ketcher.peptide.color[n]?.regular : r.ketcher.monomer.color[n]?.regular || r.ketcher.monomer.color.default?.regular : r.ketcher.monomer.color.default?.regular;
}, ";},>span{position:absolute;bottom:", function(e) {
	return e.selected ? "4px" : "6px";
}, ";left:", function(e) {
	return e.selected ? "4px" : "6px";
}, ";overflow:hidden;text-overflow:ellipsis;white-space:nowrap;max-width:85%;}>.star{color:#cad3dd;position:absolute;left:calc(50% - 7px);top:11px;font-size:13px;line-height:13px;opacity:0;transition:0.2s ease;flex-shrink:0;border:0;background:transparent;padding:0;cursor:pointer;&.visible{visibility:visible;opacity:1;}&:active{transform:scale(1.4);}&:hover,&.visible{color:#faa500;}}"), Dx = z("div", { target: "e719szw3" })("display:flex;justify-content:center;align-items:center;height:15px;width:", function(e) {
	return e.monomersAmount >= 10 ? "20px" : "15px";
}, ";border-radius:", function(e) {
	return e.monomersAmount >= 10 ? "20px" : "50%";
}, ";border:1px solid #cceaee;position:absolute;bottom:", function(e) {
	return e.selected ? "4px" : "6px";
}, ";left:", function(e) {
	return e.selected ? "18px" : "20px";
}, ";font-size:12px;line-height:12px;"), Ox = z("span", { target: "e719szw2" })({
	name: "rnnx2x",
	styles: "font-size:12px"
}), kx = z(P, { target: "e719szw1" })("color:#cad3dd;stroke-width:0;opacity:0;transition:0.2s ease;flex-shrink:0;width:13px;&:active{transform:scale(1.2);}&:hover{color:", function(e) {
	return e.disabled ? "#cad3dd" : "#333333";
}, ";}"), Ax = z("div", { target: "e719szw0" })({
	name: "evdt6m",
	styles: "position:absolute;top:12px;left:4px"
}), jx = function(e, t) {
	var n, r, i, a = Z(Kg), o = dt(By), s = (0, B.useState)(!1), c = R(s, 2), l = c[0], u = c[1];
	return (0, B.useEffect)(function() {
		if (!a) return u(!1);
		if (t === Ye.BASES) {
			var n;
			u(!(e != null && (n = e.props) != null && (n = n.MonomerCaps) != null && n.R1));
		} else if (t === Ye.PHOSPHATES) {
			var r, i;
			u(!(e != null && (r = e.props) != null && (r = r.MonomerCaps) != null && r.R1 && e != null && (i = e.props) != null && (i = i.MonomerCaps) != null && i.R2));
		} else if (t === Ye.SUGARS) {
			if (o) {
				var s, c;
				u(!(e != null && (s = e.props) != null && (s = s.MonomerCaps) != null && s.R3 && e != null && (c = e.props) != null && (c = c.MonomerCaps) != null && c.R2));
			} else {
				var l, d, f;
				u(!(e != null && (l = e.props) != null && (l = l.MonomerCaps) != null && l.R3 && e != null && (d = e.props) != null && (d = d.MonomerCaps) != null && d.R2 && e != null && (f = e.props) != null && (f = f.MonomerCaps) != null && f.R1));
			}
		}
	}, [
		t,
		a,
		o,
		e == null || (n = e.props) == null || (n = n.MonomerCaps) == null ? void 0 : n.R1,
		e == null || (r = e.props) == null || (r = r.MonomerCaps) == null ? void 0 : r.R2,
		e == null || (i = e.props) == null || (i = i.MonomerCaps) == null ? void 0 : i.R3,
		u
	]), l;
}, Mx = function(e, t) {
	var n = dt(K), r = Rt();
	(0, B.useEffect)(function() {
		if (n && t.current) {
			var i = Jd(t.current), a = uf().on("start", function() {
				n.isLibraryItemDragCancelled = n.mode.modeName === "sequence-layout-mode", n.isLibraryItemDragCancelled || (document.body.style.cursor = "grabbing");
			}).on("drag", function(t) {
				if (!n.isLibraryItemDragCancelled) {
					r(Mg(!0));
					var i = t.sourceEvent, a = i.clientX, o = i.clientY;
					n.events.setLibraryItemDragState.dispatch({
						item: e,
						position: {
							x: a - (n.ketcherRootElementBoundingClientRect?.left || 0),
							y: o - (n.ketcherRootElementBoundingClientRect?.top || 0)
						}
					});
				}
			}).on("end", function(t) {
				if (!n.isLibraryItemDragCancelled) {
					var i = t.sourceEvent, a = i.clientX, o = i.clientY, s = Ke.instance.canvasWrapper.node()?.getBoundingClientRect();
					if (s) {
						var c = s.top, l = s.left, u = s.right, d = s.bottom, f = Ke.instance.zoomTransform, p = a - l + f.k * 15, m = o - c + f.k * 15, h = f.invert([p, m]), g = R(h, 2), _ = g[0], v = g[1];
						a >= l && a <= u && o >= c && o <= d && n.events.placeLibraryItemOnCanvas.dispatch(e, {
							x: _,
							y: v
						});
					}
				}
				n.events.setLibraryItemDragState.dispatch(null), n.isLibraryItemDragCancelled = !1, document.body.style.cursor = "", r(Mg(!1));
			});
			return i.call(a), function() {
				i.on(".drag", null);
			};
		}
	}, [
		n,
		e,
		t,
		r
	]);
}, Nx = function(e, t) {
	var n = e.getDataForAutochain(), r = n.selectedMonomersWithFreeR2;
	return n.selectedMonomers.length > 0 && r.length !== 1 ? "Select a monomer or a chain that has one R2 available." : r.length === 1 && !xe(t) ? "This monomer cannot be added to a chain using this button, as it lacks R1." : "";
}, Px = function(e, t, n) {
	n(Nx(e, t));
};
function Fx(e, t) {
	var n = Object.keys(e);
	if (Object.getOwnPropertySymbols) {
		var r = Object.getOwnPropertySymbols(e);
		t && (r = r.filter(function(t) {
			return Object.getOwnPropertyDescriptor(e, t).enumerable;
		})), n.push.apply(n, r);
	}
	return n;
}
function Ix(e) {
	for (var t = 1; t < arguments.length; t++) {
		var n = arguments[t] == null ? {} : arguments[t];
		t % 2 ? Fx(Object(n), !0).forEach(function(t) {
			I(e, t, n[t]);
		}) : Object.getOwnPropertyDescriptors ? Object.defineProperties(e, Object.getOwnPropertyDescriptors(n)) : Fx(Object(n)).forEach(function(t) {
			Object.defineProperty(e, t, Object.getOwnPropertyDescriptor(n, t));
		});
	}
	return e;
}
var Lx = "autochain", Rx = function(e) {
	var t, n, r, i, a = e.item, o = e.groupName, s = e.onMouseLeave, c = e.onMouseMove, l = e.isSelected, u = e.disabled, d = e.onClick, f = d === void 0 ? px : d, p = e.onStarClick, m = p === void 0 ? px : p, h = X(), g = Z(K), _ = Z(qg), v = Z(Qg), y = (0, B.useState)(""), b = R(y, 2), x = b[0], S = b[1], C = (0, B.useRef)(null), T = jx(a, o) || u, E = "";
	w(a) || (E = a.props.MonomerType === f_.CHEM ? a.props.MonomerType : a.props.MonomerNaturalAnalogCode);
	var D = k_(a), O = w(a) ? void 0 : a, k = (0, B.useCallback)(function(e) {
		e.stopPropagation(), m(), h(I_(a));
	}, [
		h,
		a,
		m
	]), A = (0, B.useCallback)(function(e) {
		if (e.stopPropagation(), g) {
			var t = Nx(g, a);
			if (S(t), t) return;
		}
		g?.events.autochain.dispatch(a);
	}, [g, a]), j = (0, B.useCallback)(function() {
		return g && Px(g, a, S);
	}, [g, a]), ee = (0, B.useCallback)(function() {
		if (g) {
			var e = Nx(g, a);
			if (S(e), e) return;
		}
		g?.events.previewAutochain.dispatch(a);
	}, [g, a]), te = (0, B.useCallback)(function() {
		g?.events.removeAutochainPreview.dispatch(a);
	}, [g, a]);
	return Mx(a, C), W(Ex, Ix(Ix({
		selected: l,
		disabled: T,
		isDragging: v,
		"data-testid": D,
		"data-monomer-item-id": D,
		item: O,
		isVariantMonomer: a.isAmbiguous,
		code: E,
		onMouseOver: j,
		onMouseLeave: s,
		onMouseMove: c,
		onDoubleClick: function(e) {
			A(e), te();
		}
	}, T ? {} : { onClick: f }), {}, {
		ref: C,
		"data-idtalias-base": (O == null || (t = O.props.idtAliases) == null ? void 0 : t.base) ?? void 0,
		"data-idtalias-modifications-endpoint5": (O == null || (n = O.props.idtAliases) == null || (n = n.modifications) == null ? void 0 : n.endpoint5) ?? void 0,
		"data-idtalias-modifications-endpoint3": (O == null || (r = O.props.idtAliases) == null || (r = r.modifications) == null ? void 0 : r.endpoint3) ?? void 0,
		"data-idtalias-modifications-internal": (O == null || (i = O.props.idtAliases) == null || (i = i.modifications) == null ? void 0 : i.internal) ?? void 0,
		"data-axolabs": O?.props.aliasAxoLabs ?? void 0,
		"data-helm": O?.props.aliasHELM ?? void 0,
		"data-biln": O?.props.aliasBILN ?? void 0,
		"data-modificationtype": Tx(O?.props.modificationTypes),
		children: [
			U(Ox, { children: a.label }),
			!T && W(H, { children: [!_ && U(Mt, {
				title: x,
				children: U(Ax, { children: U(kx, {
					className: Lx,
					name: "monomer-autochain",
					disabled: !!x,
					onMouseOver: ee,
					onMouseOut: te,
					onClick: A,
					onDoubleClick: function(e) {
						return e.stopPropagation();
					}
				}) })
			}), U("button", {
				type: "button",
				onClick: k,
				className: `star ${a.favorite ? "visible" : ""}`,
				"aria-label": "Toggle favorite",
				children: C_
			})] }),
			w(a) && U(Dx, {
				selected: l,
				monomersAmount: a.monomers.length,
				children: a.monomers.length
			})
		]
	}));
}, zx = z("div", { target: "e10tnh3n3" })({
	name: "37420",
	styles: "display:grid;grid-template-columns:repeat(3, 1fr);grid-template-rows:auto;flex:1;gap:4px;&::after{content:'';flex:auto;}"
}), Bx = z("div", { target: "e10tnh3n2" })("position:relative;display:flex;flex-direction:row;flex-wrap:wrap;justify-content:flex-start;font-size:", function(e) {
	return e.theme.ketcher.font.size.small;
}, ";font-family:", function(e) {
	return e.theme.ketcher.font.family.roboto;
}, ";color:", function(e) {
	return e.theme.ketcher.color.divider;
}, ";margin:0;gap:4px;"), Vx = z(Bx, { target: "e10tnh3n1" })({
	name: "qdeacm",
	styles: "flex-direction:column"
}), Hx = z("div", { target: "e10tnh3n0" })("height:100%;display:flex;flex-grow:0;flex-basis:14px;flex-direction:column;flex-wrap:wrap;justify-content:flex-start;font-size:", function(e) {
	return e.theme.ketcher.font.size.medium;
}, ";font-family:", function(e) {
	return e.theme.ketcher.font.family.roboto;
}, ";color:", function(e) {
	return e.theme.ketcher.color.text.primary;
}, ";margin:0;"), Ux = [Lx], Wx = function(e) {
	return Ux.some(function(t) {
		return e.classList.contains(t) || e.closest(`.${t}`);
	});
};
function Gx(e, t) {
	var n = typeof Symbol < "u" && e[Symbol.iterator] || e["@@iterator"];
	if (!n) {
		if (Array.isArray(e) || (n = Kx(e)) || t && e && typeof e.length == "number") {
			n && (e = n);
			var r = 0, i = function() {};
			return {
				s: i,
				n: function() {
					return r >= e.length ? { done: !0 } : {
						done: !1,
						value: e[r++]
					};
				},
				e: function(e) {
					throw e;
				},
				f: i
			};
		}
		throw TypeError("Invalid attempt to iterate non-iterable instance.\nIn order to be iterable, non-array objects must have a [Symbol.iterator]() method.");
	}
	var a, o = !0, s = !1;
	return {
		s: function() {
			n = n.call(e);
		},
		n: function() {
			var e = n.next();
			return o = e.done, e;
		},
		e: function(e) {
			s = !0, a = e;
		},
		f: function() {
			try {
				o || n.return == null || n.return();
			} finally {
				if (s) throw a;
			}
		}
	};
}
function Kx(e, t) {
	if (e) {
		if (typeof e == "string") return qx(e, t);
		var n = {}.toString.call(e).slice(8, -1);
		return n === "Object" && e.constructor && (n = e.constructor.name), n === "Map" || n === "Set" ? Array.from(e) : n === "Arguments" || /^(?:Ui|I)nt(?:8|16|32)(?:Clamped)?Array$/.test(n) ? qx(e, t) : void 0;
	}
}
function qx(e, t) {
	(t == null || t > e.length) && (t = e.length);
	for (var n = 0, r = Array(t); n < t; n++) r[n] = e[n];
	return r;
}
var Jx = function(e) {
	var t = e.items, n = e.title, r = e.groupName, i = e.selectedMonomerUniqueKey, a = e.libraryName, o = e.disabled, s = e.onItemClick, c = s === void 0 ? px : s, l = X(), u = Z(K), d = Z(Iy), f = function(e) {
		var t;
		if (w(e)) return !1;
		var n = e;
		if (o) return o;
		var r = d[`${n.props?.MonomerClass}s`];
		if (r?.length > 0 && (t = n.props) != null && t.MonomerCaps) {
			var i = Gx(r), a;
			try {
				for (i.s(); !(a = i.n()).done;) if (!(a.value in n.props.MonomerCaps)) return !0;
			} catch (e) {
				i.e(e);
			} finally {
				i.f();
			}
		}
		return !1;
	}, p = (0, B.useCallback)(function(e) {
		return l(Ag(e));
	}, [l]), m = (0, B.useCallback)((0, ws.debounce)(function(e) {
		return p(e);
	}, 500), [p]), h = (0, B.useCallback)(function() {
		m.cancel(), l(Ag(void 0));
	}, [m, l]), g = function(e, t) {
		if (h(), !Wx(t.target)) {
			var n = t.currentTarget.getBoundingClientRect(), r, i, a;
			if (w(e)) {
				a = bt(e)(n);
				var o = `${n.left + n.width / 2}px`;
				i = _g.AmbiguousMonomer, r = {
					left: o,
					top: a,
					transform: "translate(-50%, 0)"
				};
			} else a = St(n), r = {
				right: "-88px",
				top: a,
				transform: "translate(-50%, 0)"
			}, i = _g.Monomer;
			m({
				type: i,
				monomer: e,
				style: r
			});
		}
	}, _ = function(e) {
		[
			"FAVORITES",
			"PEPTIDE",
			"CHEM"
		].includes(a ?? "") && u?.events.selectMonomer.dispatch(e), c(e);
	}, v = function(e) {
		return i === k_(e);
	};
	return !t || t.length === 0 ? null : W(Vx, { children: [n && U(Hx, { children: n }), U(zx, { children: t.map(function(e) {
		return U(Rx, {
			disabled: f(e),
			item: e,
			groupName: r,
			isSelected: v(e),
			onMouseLeave: h,
			onMouseMove: function(t) {
				return g(e, t);
			},
			onClick: function() {
				return _(e);
			},
			onStarClick: h
		}, k_(e));
	}) })] });
}, Yx = z("div", { target: "e1bp6il60" })({
	name: "8z91a1",
	styles: "width:100%;display:flex;flex-direction:column;justify-items:center;gap:8px;padding:8px"
}), Xx = z(Ex, { target: "e1txcvj90" })("&::after{content:'';background:", function(e) {
	var t = e.theme;
	return e.selected ? t.ketcher.color.button.primary.active : "#faa500";
}, ";}.dots{visibility:hidden;position:absolute;right:2px;top:10px;}&:hover .dots{visibility:visible;}>.star{right:0;left:calc(50% - 7px);top:11px;width:min-content;}"), Zx = z("div", { target: "e1h0dkll2" })(function(e) {
	return {
		minHeight: "32px",
		display: "flex",
		alignItems: "center",
		padding: "8px 12px",
		gap: "8px",
		borderBottom: e.theme.ketcher.border.small
	};
}, ""), Qx = z("span", { target: "e1h0dkll1" })(function(e) {
	return {
		flexGrow: 1,
		fontSize: e.theme.ketcher.font.size.regular
	};
}, ""), $x = z(P, { target: "e1h0dkll0" })(function(e) {
	return {
		width: "16px",
		height: "16px",
		color: e.theme.ketcher.color.icon.grey,
		transition: e.theme.ketcher.transition.regular,
		transform: e.expanded ? "rotate(180deg)" : "none"
	};
}, ""), eS = (0, B.memo)(function(e) {
	var t = e.preset, n = e.isSelected, r = e.onClick, i = r === void 0 ? px : r, a = e.onContextMenu, o = a === void 0 ? px : a, s = e.onMouseLeave, c = s === void 0 ? px : s, l = e.onMouseMove, u = l === void 0 ? px : l, d = e.onStarClick, f = d === void 0 ? px : d, p = X(), m = Z(K), h = Z(qg), g = Z(Qg), _ = (0, B.useState)(""), v = R(_, 2), y = v[0], b = v[1], x = (0, B.useRef)(null), S = (0, B.useCallback)(function(e) {
		e.stopPropagation(), f(), p(xb(t));
	}, [
		p,
		t,
		f
	]), C = (0, B.useCallback)(function(e) {
		e.stopPropagation(), !y && m?.events.autochain.dispatch(t);
	}, [
		y,
		m,
		t
	]), w = (0, B.useCallback)(function() {
		return m && Px(m, t, b);
	}, [m, t]), T = (0, B.useCallback)(function() {
		y || m?.events.previewAutochain.dispatch(t);
	}, [
		y,
		m,
		t
	]), E = (0, B.useCallback)(function() {
		m?.events.removeAutochainPreview.dispatch(t);
	}, [m, t]);
	return Mx(t, x), W(Xx, {
		"data-testid": A_(t),
		onClick: i,
		onContextMenu: o,
		onMouseOver: w,
		onMouseLeave: c,
		onMouseMove: u,
		onDoubleClick: function(e) {
			C(e), E();
		},
		selected: n,
		isDragging: g,
		code: t.name,
		"data-rna-preset-item-name": t.name,
		ref: x,
		children: [
			!h && U(Mt, {
				title: y,
				children: U(Ax, { children: U(kx, {
					className: Lx,
					name: "monomer-autochain",
					disabled: !!y,
					onMouseOver: T,
					onMouseOut: E,
					onClick: C,
					onDoubleClick: function(e) {
						return e.stopPropagation();
					}
				}) })
			}),
			U("span", { children: t.name }),
			U($x, {
				name: "vertical-dots",
				className: "dots",
				onClick: o
			}),
			U("div", {
				"aria-hidden": !0,
				onClick: S,
				className: `star ${t.favorite ? "visible" : ""}`,
				children: C_
			})
		]
	});
}), tS;
(function(e) {
	e.FOR_RNA = "context-menu-for-RNA", e.FOR_SEQUENCE = "context-menu-for-sequence", e.FOR_POLYMER_BOND = "context-menu-for-polymer-bond", e.FOR_SELECTED_MONOMERS = "context-menu-for-selected-monomers";
})(tS ||= {});
var nS = z(wn, { target: "ekj16lc0" })("--contexify-activeItem-bgColor:rgba(243, 245, 247, 1);--contexify-menu-minWidth:140px;--contexify-activeItem-color:rgba(51, 51, 51, 1);--contexify-menu-padding:4px;--contexify-itemContent-padding:6px 8px;--contexify-separator-margin:4px 0;--contexify-separator-color:#e1e5ea;.contexify_itemContent{font-family:", function(e) {
	return e.theme.ketcher.font.family.inter;
}, ";font-size:", function(e) {
	return e.theme.ketcher.font.size.regular;
}, ";height:28px;}.contexify_item-title{opacity:1;font-weight:bold;background:#e1e5ea;margin:-4px 0 4px -4px;width:calc(100% + 8px);border-radius:4px 4px 0 0;}.context_menu-icon{width:16px;height:16px;display:flex;align-items:center;margin-right:4px;}.context_menu-text{display:flex;align-items:center;line-height:", function(e) {
	return e.theme.ketcher.font.size.regular;
}, ";}.context_menu-delete-text{display:flex;align-items:center;line-height:", function(e) {
	return e.theme.ketcher.font.size.regular;
}, ";margin-left:-3px;}"), rS = function e(t, n) {
	var r = !1, i = [];
	return t.forEach(function(t) {
		var a = t.name, o = t.title, s = t.icon, c = t.hidden, l = t.disabled, u = t.isMenuTitle, d = t.separator, f = t.subMenuItems, p = t.onMouseOver, m = t.onMouseOut, h = f != null && f.length ? U(ln, {
			label: o,
			"data-testid": a,
			children: e(f, n)
		}, a) : W(yt, {
			id: a,
			onClick: function(e) {
				r = !0, setTimeout(function() {
					r = !1;
				}, 500), n(e);
			},
			"data-testid": a,
			hidden: c,
			disabled: l,
			className: u ? "contexify_item-title" : "",
			onMouseOver: function() {
				r || p?.(a);
			},
			onMouseOut: function() {
				return m?.(a);
			},
			children: [s && U("span", {
				className: "context_menu-icon",
				children: s
			}), U("span", {
				className: a === "delete" ? "context_menu-delete-text" : "context_menu-text",
				children: o
			})]
		}, a);
		i.push(h), d && i.push(U(Ht, {}, `separator-${a}`));
	}), i;
}, iS = function(e) {
	var t = e.id, n = e.handleMenuChange, r = e.menuItems, i = X(), a = Z(Zg);
	return (0, B.useEffect)(function() {
		var e = function(e) {
			var t, n;
			(t = e.target) != null && (t = t.__data__) != null && t.node || (n = e.target) != null && (n = n.__data__) != null && n.monomer ? e.stopPropagation() : i(jg(!1));
		};
		return document.addEventListener("click", e), document.addEventListener("contextmenu", e), function() {
			document.removeEventListener("click", e), document.removeEventListener("contextmenu", e);
		};
	}, [i, t]), (0, B.useEffect)(function() {
		var e = function(e) {
			e.key === "Escape" && a && (e.preventDefault(), e.stopPropagation(), bn.hideAll(), i(jg(!1)));
		};
		return document.addEventListener("keydown", e, !0), function() {
			document.removeEventListener("keydown", e, !0);
		};
	}, [i, a]), U(nS, {
		id: t,
		children: rS(r, n)
	});
}, aS = function() {
	var e = S_.RNA, t = X(), n = Z(Xy), r = Z(J_), i = Z(Kg), a = [
		{
			name: "duplicateandedit",
			title: "Duplicate and Edit...",
			disabled: !1
		},
		{
			name: "edit",
			title: "Edit...",
			separator: !0,
			disabled: n?.default
		},
		{
			name: "deletepreset",
			title: "Delete Preset",
			disabled: n?.default
		}
	], o = function(i) {
		var a = i.id, o = i.props;
		switch (a) {
			case "duplicateandedit":
				o.duplicatePreset(n), r !== e && t(R_(e));
				break;
			case "edit":
				o.editPreset(n), r !== e && t(R_(e));
				break;
			case "deletepreset": t($_("delete"));
		}
	}, s = document.querySelector(he);
	return s && !i ? (0, Es.createPortal)(U(iS, {
		id: tS.FOR_RNA,
		menuItems: a,
		handleMenuChange: o
	}), s) : null;
}, oS = function(e) {
	var t = e.presets, n = e.duplicatePreset, r = e.editPreset, i = Z(Ly), a = Z(K), o = ft({ id: tS.FOR_RNA }).show, s = Rt(), c = function(e) {
		return e.phosphatePosition ?? ie(e);
	}, l = function(e) {
		var t, n, r, i = !0, a = !0, o = !0;
		if (e != null && (t = e.base) != null && (t = t.props) != null && t.MonomerCaps && (i = "R1" in e.base.props.MonomerCaps), e != null && (n = e.sugar) != null && (n = n.props) != null && n.MonomerCaps) {
			var s;
			i && e != null && (s = e.base) != null && (s = s.props) != null && s.MonomerCaps && (a = "R3" in e.sugar.props.MonomerCaps);
		}
		if (e != null && (r = e.phosphate) != null && (r = r.props) != null && r.MonomerCaps) {
			var c;
			o = "R1" in e.phosphate.props.MonomerCaps, a && e != null && (c = e.sugar) != null && (c = c.props) != null && c.MonomerCaps && (a = "R2" in e.sugar.props.MonomerCaps);
		}
		return i && a && o;
	}, u = function(e) {
		return function() {
			!l(e) && e.name ? s(hb(e.name)) : (s(nb(e)), a?.events.selectPreset.dispatch(e), e.name !== i.name && s(pb(!1)));
		};
	}, d = function(e) {
		!(e instanceof HTMLDivElement) && e.parentElement && (e = e.parentElement);
		var t = e.getBoundingClientRect(), n = e.offsetParent?.getBoundingClientRect(), r = t.right - 140, i = t.y + t.height / 2;
		return n != null && n.x && n?.x > r && (r = t.x), {
			x: r,
			y: i
		};
	}, f = Z(Ug), p = (0, B.useCallback)(function(e) {
		return s(Ag(e));
	}, [s]), m = (0, B.useCallback)((0, ws.debounce)(function(e) {
		return p(e);
	}, 500), [p]), h = (0, B.useCallback)(function() {
		m.cancel(), s(Ag(void 0));
	}, [m, s]), g = function(e, t) {
		if (h(), !Wx(t.target) && f.type !== _g.Preset && t.currentTarget) {
			var n = [
				e.sugar,
				e.base,
				e.phosphate
			], r = t.currentTarget.getBoundingClientRect(), i = {
				left: `${r.left + r.width}px`,
				top: w(e.base) ? bt(e.base)(r) : Ct(r),
				transform: "translate(-100%, 0)"
			};
			m(w(e.base) ? {
				type: _g.AmbiguousMonomer,
				monomer: e.base,
				presetMonomers: n,
				style: i
			} : {
				type: _g.Preset,
				monomers: n,
				name: e.name,
				idtAliases: e.idtAliases,
				aliasAxoLabs: e.aliasAxoLabs,
				phosphatePosition: c(e),
				position: vg.Library,
				style: i
			});
		}
	}, _ = function(e) {
		return function(t) {
			t.stopPropagation(), s(yb(e)), o({
				event: t,
				props: {
					duplicatePreset: n,
					editPreset: r
				},
				position: d(t.currentTarget)
			});
		};
	};
	return W(Vx, {
		"data-testid": "rna-preset-group",
		children: [U(zx, { children: t.map(function(e, t) {
			return U(eS, {
				isSelected: i?.name === e.name,
				preset: e,
				onClick: u(e),
				onContextMenu: _(e),
				onMouseMove: function(t) {
					return g(e, t);
				},
				onMouseLeave: h,
				onStarClick: h
			}, `${e.name}${t}`);
		}) }), U(aS, {})]
	});
}, sS = function(e) {
	var t = e.onItemClick, n = e.libraryName, r = e.duplicatePreset, i = e.editPreset, a = Z(K_), o = Z(tb), s = Z(Wg), c = n === u_, l = c ? {
		monomers: W_(a),
		presets: Qy(o)
	} : V_(a, n), u = q_(c ? l.monomers : l), d = c ? G_(a) : H_(a, q.PEPTIDES), f = (0, B.useState)(""), p = R(f, 2), m = p[0], h = p[1];
	return (0, B.useEffect)(function() {
		s !== "monomer" && h("");
	}, [s]), W(Yx, { children: [
		c && u.length > 0 && U("div", { children: "Monomers" }),
		u.map(function(e, r, i) {
			var a = e.groupItems, o = e.groupTitle;
			return U(Jx, {
				title: i.length === 1 ? void 0 : o,
				items: a,
				libraryName: n,
				onItemClick: t,
				selectedMonomerUniqueKey: m
			}, o);
		}),
		c && l.presets.length > 0 && W(H, { children: [U("div", { children: "Presets" }), U(oS, {
			duplicatePreset: r,
			editPreset: i,
			presets: l.presets
		})] }),
		U(H, { children: (n === d_ || c) && d.map(function(e) {
			return U(Jx, {
				title: e.groupTitle,
				items: e.groupItems,
				libraryName: n,
				onItemClick: t,
				selectedMonomerUniqueKey: m
			}, e.groupTitle);
		}) })
	] });
}, cS = z("div", { target: "e1fsx6x2" })({
	name: "kxxltl",
	styles: "display:flex;flex-direction:row;justify-content:space-between;align-items:center;padding:8px;background-color:#f7f9fa;border-radius:0 0 4px 4px"
}), lS = z("span", { target: "e1fsx6x1" })("font-size:", function(e) {
	return e.theme.ketcher.font.size.medium;
}, ";overflow:hidden;text-overflow:ellipsis;color:", function(e) {
	return e.theme.ketcher.color.text.primary;
}, ";"), uS = z("div", { target: "e1fsx6x0" })({
	name: "1x17g94",
	styles: "display:flex;align-items:center;width:100%"
}), dS = (0, B.memo)(function(e) {
	var t = e.name, n = e.fullName, r = t ?? n;
	if (!r) return null;
	var i = n ?? r;
	return U(cS, {
		title: i,
		children: U(uS, { children: U(lS, {
			title: i,
			"aria-label": i,
			children: r
		}) })
	});
}), fS = z("div", { target: "e1ie5fzr8" })(function(e) {
	var t = e.selected, n = e.isEditMode, r = e.theme, i = "transparent";
	return t ? i = r.ketcher.color.button.primary.active : n && (i = r.ketcher.color.background.primary), {
		height: "40px",
		position: "relative",
		marginLeft: n ? "30px" : "28.5px",
		display: "flex",
		alignItems: "center",
		border: n ? "none" : `1.5px solid ${r.ketcher.outline.color}`,
		backgroundColor: i,
		borderRadius: r.ketcher.border.radius.regular,
		boxShadow: n ? r.ketcher.shadow.regular : "none",
		padding: "5px 10px",
		color: t ? "white" : "black",
		gap: "8px",
		cursor: "pointer",
		outlineOffset: "1px",
		boxSizing: "border-box",
		":hover": { outline: r.ketcher.outline.small },
		":not(:last-child)": { ":after": {
			content: "\"\"",
			position: "absolute",
			right: "100%",
			bottom: "calc(50% - 1px)",
			borderLeft: r.ketcher.outline.medium,
			borderBottom: r.ketcher.outline.medium,
			height: "2px",
			width: "17px"
		} },
		":last-child": { ":after": {
			content: "\"\"",
			position: "absolute",
			right: "100%",
			bottom: "calc(50% - 1px)",
			borderLeft: r.ketcher.outline.medium,
			borderBottom: r.ketcher.outline.medium,
			borderRadius: "0 0 0 4px",
			height: "130px",
			width: "17px"
		} }
	};
}, ""), pS = z("div", { target: "e1ie5fzr7" })({
	name: "1fttcpj",
	styles: "display:flex;flex-direction:column"
}), mS = z("span", { target: "e1ie5fzr6" })("font-size:", function(e) {
	return e.theme.ketcher.font.size.small;
}, ";color:", function(e) {
	var t = e.selected, n = e.theme;
	return t ? n.ketcher.color.background.primary : n.ketcher.color.text.light;
}, ";opacity:", function(e) {
	return e.selected ? .4 : 1;
}, ";"), hS = z("span", { target: "e1ie5fzr5" })("margin-top:1px;font-size:", function(e) {
	return e.theme.ketcher.font.size.medium;
}, ";color:", function(e) {
	var t = e.selected, n = e.empty, r = e.theme;
	return t ? r.ketcher.color.button.text.primary : n ? "#b4b9d6" : r.ketcher.color.text.primary;
}, ";opacity:", function(e) {
	var t = e.selected, n = e.empty;
	return t && n ? .4 : 1;
}, ";"), gS = z("div", { target: "e1ie5fzr4" })({
	name: "wgokoh",
	styles: "position:relative;width:16px;height:16px;display:flex;align-items:center;justify-content:center"
}), _S = z(P, { target: "e1ie5fzr3" })("fill:", function(e) {
	var t = e.selected, n = e.empty, r = e.theme;
	return n ? "none" : t ? r.ketcher.color.background.primary : r.ketcher.color.icon.grey;
}, ";color:", function(e) {
	var t = e.selected, n = e.theme;
	return t ? n.ketcher.color.background.primary : n.ketcher.color.icon.grey;
}, ";"), vS = z("div", { target: "e1ie5fzr2" })("position:relative;width:60px;display:flex;flex-direction:column;gap:8px;padding:4px;border-radius:4px;box-shadow:0 1px 2px 0 rgba(180, 185, 214, 0.6);cursor:pointer;background-color:", function(e) {
	var t = e.selected, n = e.theme;
	return t ? n.ketcher.color.button.primary.active : n.ketcher.color.background.primary;
}, ";&:hover{outline:", function(e) {
	return e.theme.ketcher.outline.selected.small;
}, ";}"), yS = z("div", { target: "e1ie5fzr1" })("position:absolute;top:-35%;left:50%;height:15px;width:2px;background-color:", function(e) {
	return e.theme.ketcher.outline.color;
}, ";"), bS = z("p", { target: "e1ie5fzr0" })("margin:0;font-size:", function(e) {
	return e.theme.ketcher.font.size.small;
}, ";font-weight:", function(e) {
	return e.theme.ketcher.font.weight.regular;
}, ";color:", function(e) {
	var t = e.selected, n = e.empty, r = e.theme;
	return t ? r.ketcher.color.button.text.primary : n ? "#b4b9d6" : r.ketcher.color.text.primary;
}, ";opacity:", function(e) {
	var t = e.selected, n = e.empty;
	return t && n ? .4 : 1;
}, ";"), xS = I(I(I({}, q.SUGARS, "Sugar"), q.BASES, "Base"), q.PHOSPHATES, "Phosphate"), SS = (0, B.memo)(function(e) {
	var t = e.selected, n = e.empty, r = e.name;
	return U(gS, { children: U(_S, {
		selected: t,
		empty: n,
		name: r
	}) });
}), CS = function(e) {
	var t = e.groupName, n = e.iconName, r = e.monomerName, i = e.selected, a = e.onClick, o = e.testid, s = e.children, c = Z(Wy), l = !r;
	return U(vS, {
		selected: i,
		onClick: a,
		isEditMode: c,
		"data-testid": o,
		children: W(H, { children: [
			U(yS, {}),
			U(SS, {
				name: n,
				selected: i,
				empty: l
			}),
			U(bS, {
				selected: i,
				empty: l,
				children: r ?? xS[t]
			}),
			s
		] })
	});
}, wS = function(e) {
	var t = e.groupName, n = e.iconName, r = e.monomerName, i = e.selected, a = e.onClick, o = e.testid, s = e.children, c = Z(Wy), l = !r;
	return U(fS, {
		selected: i,
		onClick: a,
		isEditMode: c,
		"data-testid": o,
		children: W(H, { children: [
			U(SS, {
				name: n,
				selected: i,
				empty: l
			}),
			W(pS, { children: [U(mS, {
				selected: i,
				children: xS[t]
			}), U(hS, {
				empty: l,
				selected: i,
				children: r ?? "Not selected"
			})] }),
			s
		] })
	});
};
function TS(e, t) {
	var n = Object.keys(e);
	if (Object.getOwnPropertySymbols) {
		var r = Object.getOwnPropertySymbols(e);
		t && (r = r.filter(function(t) {
			return Object.getOwnPropertyDescriptor(e, t).enumerable;
		})), n.push.apply(n, r);
	}
	return n;
}
function ES(e) {
	for (var t = 1; t < arguments.length; t++) {
		var n = arguments[t] == null ? {} : arguments[t];
		t % 2 ? TS(Object(n), !0).forEach(function(t) {
			I(e, t, n[t]);
		}) : Object.getOwnPropertyDescriptors ? Object.defineProperties(e, Object.getOwnPropertyDescriptors(n)) : TS(Object(n)).forEach(function(t) {
			Object.defineProperty(e, t, Object.getOwnPropertyDescriptor(n, t));
		});
	}
	return e;
}
var DS = function(e) {
	return wx() ? U(CS, ES(ES({}, e), {}, { children: e.children })) : U(wS, ES(ES({}, e), {}, { children: e.children }));
}, OS = z("div", { target: "e18wzlbg12" })(function(e) {
	return {
		display: "flex",
		flexDirection: "column",
		padding: "10px",
		backgroundColor: "#F7F9FA",
		borderRadius: "0 0 4px 4px",
		"&.rna-editor-expanded--sequence-edit-mode": {
			padding: "8px",
			paddingTop: "10px",
			border: `2px ${e.theme.ketcher.color.editMode.sequenceInRNABuilder} solid`,
			borderTop: "none"
		}
	};
}, ""), kS = z("input", { target: "e18wzlbg11" })("width:100%;padding:6px;border:none;border-radius:4px;box-shadow:0 1px 2px 0 rgba(180, 185, 214, 0.6);&:hover,&:focus{outline:", function(e) {
	return e.theme.ketcher.outline.selected.small;
}, ";}"), AS = z("div", { target: "e18wzlbg10" })("width:100%;display:flex;flex-direction:", function(e) {
	return e.compact ? "row" : "column";
}, ";justify-content:", function(e) {
	return e.compact ? "space-between" : "flex-start";
}, ";gap:8px;margin-top:16px;");
z("div", { target: "e18wzlbg9" })({
	name: "6erkce",
	styles: "margin-top:12px;display:flex;align-items:center;justify-content:space-between;gap:8px"
}), z("span", { target: "e18wzlbg8" })(function(e) {
	var t = e.theme;
	return {
		fontSize: t.ketcher.font.size.small,
		color: t.ketcher.color.text.light
	};
}, ""), z("div", { target: "e18wzlbg7" })({
	name: "1yydxi7",
	styles: "display:flex;align-items:center;gap:8px"
}), z("button", { target: "e18wzlbg6" })(function(e) {
	var t = e.theme, n = e.selected;
	return {
		minWidth: "40px",
		padding: "4px 8px",
		borderRadius: t.ketcher.border.radius.regular,
		border: n ? t.ketcher.outline.selected.small : t.ketcher.outline.grey.small,
		color: n ? t.ketcher.color.button.text.primary : t.ketcher.color.text.primary,
		backgroundColor: n ? t.ketcher.color.button.primary.active : t.ketcher.color.background.primary,
		cursor: "pointer",
		":disabled": {
			opacity: .5,
			cursor: "not-allowed"
		}
	};
}, "");
var jS = z("div", { target: "e18wzlbg5" })({
	name: "zmhcg5",
	styles: "margin-top:16px;display:flex;justify-content:space-evenly;align-items:center;gap:8px"
}), MS = z(y, { target: "e18wzlbg4" })(function(e) {
	return {
		width: "100%",
		whiteSpace: "nowrap",
		fontSize: e.theme.ketcher.font.size.regular,
		backgroundColor: e.primary ? e.theme.ketcher.color.button.primary.active : void 0,
		color: e.primary && !e.disabled ? e.theme.ketcher.color.button.text.primary : e.theme.ketcher.color.text.light,
		outline: e.primary && !e.disabled ? e.theme.ketcher.outline.selected.small : e.theme.ketcher.outline.grey.small
	};
}, ""), NS = z("div", { target: "e18wzlbg3" })(function(e) {
	return {
		position: "relative",
		borderRadius: e.theme.ketcher.border.radius.regular,
		backgroundColor: e.theme.ketcher.color.background.primary,
		boxShadow: e.theme.ketcher.shadow.regular,
		cursor: "pointer",
		overflow: "hidden",
		padding: "0 6px 6px 6px",
		display: "flex",
		alignItems: "flex-end",
		height: "48px",
		outline: e.selected ? e.theme.ketcher.outline.selected.medium : "none",
		":hover": { outline: e.selected ? void 0 : e.theme.ketcher.outline.small }
	};
}, ""), PS = z("span", { target: "e18wzlbg2" })(function(e) {
	return {
		position: "absolute",
		top: "0",
		left: "0",
		width: "100%",
		height: "8px",
		backgroundColor: e.selected ? e.theme.ketcher.outline.selected.color : e.theme.ketcher.outline.color
	};
}, ""), FS = z(le, { target: "e18wzlbg1" })({
	name: "1jdipvd",
	styles: "width:100%;&:disabled{background:none;outline:none;color:inherit;}"
}), IS = z("div", { target: "e18wzlbg0" })({
	name: "1gz2b5f",
	styles: "overflow:hidden;text-overflow:ellipsis"
}), LS = function(e) {
	document.body.querySelector(e)?.scrollIntoView();
}, RS = function(e) {
	LS(`[data-rna-preset-item-name="${e}"]`);
}, zS = function(e) {
	LS(`[data-monomer-item-id="${e}"]`);
};
function BS(e, t) {
	var n = typeof Symbol < "u" && e[Symbol.iterator] || e["@@iterator"];
	if (!n) {
		if (Array.isArray(e) || (n = VS(e)) || t && e && typeof e.length == "number") {
			n && (e = n);
			var r = 0, i = function() {};
			return {
				s: i,
				n: function() {
					return r >= e.length ? { done: !0 } : {
						done: !1,
						value: e[r++]
					};
				},
				e: function(e) {
					throw e;
				},
				f: i
			};
		}
		throw TypeError("Invalid attempt to iterate non-iterable instance.\nIn order to be iterable, non-array objects must have a [Symbol.iterator]() method.");
	}
	var a, o = !0, s = !1;
	return {
		s: function() {
			n = n.call(e);
		},
		n: function() {
			var e = n.next();
			return o = e.done, e;
		},
		e: function(e) {
			s = !0, a = e;
		},
		f: function() {
			try {
				o || n.return == null || n.return();
			} finally {
				if (s) throw a;
			}
		}
	};
}
function VS(e, t) {
	if (e) {
		if (typeof e == "string") return HS(e, t);
		var n = {}.toString.call(e).slice(8, -1);
		return n === "Object" && e.constructor && (n = e.constructor.name), n === "Map" || n === "Set" ? Array.from(e) : n === "Arguments" || /^(?:Ui|I)nt(?:8|16|32)(?:Clamped)?Array$/.test(n) ? HS(e, t) : void 0;
	}
}
function HS(e, t) {
	(t == null || t > e.length) && (t = e.length);
	for (var n = 0, r = Array(t); n < t; n++) r[n] = e[n];
	return r;
}
var US = function(e) {
	return e.size === 0 ? "" : e.size === 1 ? L(e)[0] : "[multiple]";
}, WS = function(e) {
	if (e != null && e.length) {
		var t = {
			sugarLabel: /* @__PURE__ */ new Set(),
			baseLabel: /* @__PURE__ */ new Set(),
			phosphateLabel: /* @__PURE__ */ new Set()
		}, n = BS(e), r;
		try {
			for (n.s(); !(r = n.n()).done;) for (var i = r.value, a = 0, o = [
				"sugarLabel",
				"baseLabel",
				"phosphateLabel"
			]; a < o.length; a++) {
				var s = o[a];
				(i != null && i[s] || !(i != null && i[s]) && i.type === Ae.Nucleoside && !i.isNucleosideConnectedAndSelectedWithPhosphate) && t[s].add(i?.[s]);
			}
		} catch (e) {
			n.e(e);
		} finally {
			n.f();
		}
		return {
			Sugars: US(t.sugarLabel),
			Bases: US(t.baseLabel),
			Phosphates: US(t.phosphateLabel)
		};
	}
}, GS = function(e) {
	var t = WS(e);
	return `${t?.Sugars}(${t?.Bases})${t?.Phosphates ?? ""}`;
}, KS = function(e) {
	e(lb(null)), e(pb(!1));
}, qS = function(e) {
	KS(e);
}, JS = function(e, t) {
	var n;
	KS(e), e(rb([])), t?.events.turnOffSequenceEditInRNABuilderMode.dispatch(), (t == null || (n = t.mode) == null ? void 0 : n.modeName) === "sequence-layout-mode" && t.mode.turnOffEditMode();
}, YS = function(e) {
	return e.filter(function(e) {
		return e.type ? e.type === Ae.Nucleotide || e.type === Ae.Nucleoside : e.node ? e.node instanceof An || e.node instanceof Dt : !1;
	}).length;
}, XS = {
	groupBlockWrapper: "RnaEditorExpanded-module_groupBlockWrapper__sUlhI",
	phosphatePositionIconWrapper: "RnaEditorExpanded-module_phosphatePositionIconWrapper__XHea5",
	active: "RnaEditorExpanded-module_active__9PKEX",
	hover: "RnaEditorExpanded-module_hover__0ZbV5",
	phosphatePositionIconWrapperOnPresetCard: "RnaEditorExpanded-module_phosphatePositionIconWrapperOnPresetCard__-IbfN",
	phosphatePositionIconWrapperOnPresetCardActive: "RnaEditorExpanded-module_phosphatePositionIconWrapperOnPresetCardActive__bAVbU",
	phosphatePositionSelector: "RnaEditorExpanded-module_phosphatePositionSelector__NE5RX",
	phosphatePositionTrigger: "RnaEditorExpanded-module_phosphatePositionTrigger__IpdSG",
	phosphatePositionOption: "RnaEditorExpanded-module_phosphatePositionOption__GO-S4",
	phosphatePositionOptionDisabled: "RnaEditorExpanded-module_phosphatePositionOptionDisabled__oxZ6W"
};
function ZS(e, t) {
	var n = Object.keys(e);
	if (Object.getOwnPropertySymbols) {
		var r = Object.getOwnPropertySymbols(e);
		t && (r = r.filter(function(t) {
			return Object.getOwnPropertyDescriptor(e, t).enumerable;
		})), n.push.apply(n, r);
	}
	return n;
}
function QS(e) {
	for (var t = 1; t < arguments.length; t++) {
		var n = arguments[t] == null ? {} : arguments[t];
		t % 2 ? ZS(Object(n), !0).forEach(function(t) {
			I(e, t, n[t]);
		}) : Object.getOwnPropertyDescriptors ? Object.defineProperties(e, Object.getOwnPropertyDescriptors(n)) : ZS(Object(n)).forEach(function(t) {
			Object.defineProperty(e, t, Object.getOwnPropertyDescriptor(n, t));
		});
	}
	return e;
}
var $S = function(e) {
	var t, n = e.isEditMode, r = e.onDuplicate, i = [
		{
			groupName: q.SUGARS,
			iconName: "sugar",
			testId: "rna-builder-slot--sugar"
		},
		{
			groupName: q.BASES,
			iconName: "base",
			testId: "rna-builder-slot--base"
		},
		{
			groupName: q.PHOSPHATES,
			iconName: "phosphate",
			testId: "rna-builder-slot--phosphate"
		}
	], o = Rt(), s = yx() === "sequence-layout-mode", c = Z(Ly), l = Z(Yy), u = Z(Fy), d = Z(K), f = Z(eb), p = Z(Hy), m = (0, B.useState)(c), h = R(m, 2), g = h[0], _ = h[1], v = (0, B.useState)(c != null && (t = c.connections) != null && t.length ? ie(c) : void 0), y = R(v, 2), b = y[0], x = y[1], S = function(e) {
		var t;
		if (e != null && e.phosphate) {
			var n = Cv(e), r = n.is3PrimeAvailable, i = n.is5PrimeAvailable;
			if (b === "left" && i) return "left";
			if (b === "right" && r) return "right";
			if ((t = e.connections) != null && t.length) {
				var a = ie(e);
				if (a === "left" && i || a === "right" && r) return a;
			}
			if (s && r) return "right";
			if (i && !r) return "left";
			if (r && !i) return "right";
		}
	}, C = Z(Ry), w = Z(zy), T = Z(Kg), E = (0, B.useState)(!1), D = R(E, 2), O = D[0], k = D[1], A = (0, B.useState)(WS(C)), j = R(A, 2), ee = j[0], te = j[1], M = S(g), ne = Cv(g || {}), re = ne.is3PrimeAvailable, N = ne.is5PrimeAvailable, ae = !!g?.phosphate && re && N, oe = !M && ae, se = oe ? "Before saving you must choose the position of the phosphate." : "", ce = {
		left: "Sugar must have R1, and phosphate must have R2.",
		right: "Sugar must have R2, and phosphate must have R1."
	}, le = function() {
		if (p) {
			var e = My[p.groupName], t = QS(QS({}, g), {}, I({}, e, p.groupItem));
			return _(t), t;
		}
		return g;
	};
	(0, B.useEffect)(function() {
		var e;
		_(c), x(c != null && (e = c.connections) != null && e.length ? ie(c) : void 0);
	}, [c]), (0, B.useEffect)(function() {
		C && (YS(C) === 1 && o(ib(GS(C))), te(WS(C)));
	}, [o, C]), (0, B.useEffect)(function() {
		if (u !== Ay.Presets && n) {
			if (T && p) {
				var e = `${My[p.groupName]}Label`, t = C.map(function(t) {
					return t.isNucleosideConnectedAndSelectedWithPhosphate && e === "phosphateLabel" || t.type === Ae.Phosphate && (e === "sugarLabel" || e === "baseLabel") ? t : QS(QS({}, t), {}, I(I({}, e, p.groupItem.label), "rnaBaseMonomerItem", p.groupName === "Bases" ? p.groupItem : t.rnaBaseMonomerItem));
				});
				k(!0), o(rb(t));
			} else {
				var r = le(), i = S(r), a = g?.name;
				r.editedName || (a = Gy(QS(QS({}, r), {}, { connections: Xe(r, i) }))), _(QS(QS({}, r), {}, { name: a }));
			}
		}
	}, [
		p?.groupItem,
		T,
		b
	]);
	var ue = function(e, t) {
		if (e === Ay.Presets) RS(g?.name), g && d?.events.selectPreset.dispatch(g);
		else {
			var n = g[My[e]];
			n ? zS(k_(n)) : t && zS(t);
		}
	}, de = function(e) {
		return function() {
			var t = Vy(g, e);
			t && !s && d?.events.selectMonomer.dispatch(t), g[My[e]] && o(sb(k_(g[My[e]]))), o(ob(e)), o(cb({
				rnaPreset: g,
				isEditMode: n,
				selectedPhosphatePosition: b
			}));
			var r = "";
			if (T && C.length > 0) {
				var i = C[0].baseLabel;
				if (i && C.every(function(e) {
					return e.baseLabel === i;
				})) {
					var a = C[0].rnaBaseMonomerItem;
					a && (r = k_(a), o(sb(r)));
				}
			}
			setTimeout(function() {
				return ue(e, r);
			}, 100);
		};
	}, fe = function(e) {
		if (n) {
			var t = e.target.value;
			_(QS(QS({}, g), {}, {
				name: t.trim(),
				editedName: !0
			}));
		}
	}, pe = function(e) {
		x(e), o(cb({
			rnaPreset: g,
			isEditMode: n,
			selectedPhosphatePosition: e
		}));
	}, me = function(e) {
		var t = arguments.length > 1 && arguments[1] !== void 0 && arguments[1], n = arguments.length > 2 && arguments[2] !== void 0 && arguments[2];
		return U("div", {
			className: a(XS.phosphatePositionIconWrapper, t && XS.active, n && XS.hover),
			children: e === "left" ? U(P, { name: "preset-left-phosphate" }) : U(P, { name: "preset-right-phosphate" })
		});
	}, he = function(e) {
		return e === "left" ? "Phosphate on the left" : "Phosphate on the right";
	}, ge = function(e, t) {
		var n = t ? ce[e] : b === e ? he(e) : `Switch to ${e}`;
		return U(Mt, {
			title: n,
			children: U("span", { children: U("button", {
				type: "button",
				className: a(XS.phosphatePositionOption, t && XS.phosphatePositionOptionDisabled),
				disabled: t,
				onClick: function() {
					pe(e);
				},
				children: me(e, !1, !0)
			}) })
		}, e);
	}, _e = function(e) {
		var t = T, r = t || !N && !re, i = t ? "right" : e ?? b ?? "right", o = !t && u === q.PHOSPHATES, s = !n || !o;
		return W("div", {
			className: a(XS.phosphatePositionIconWrapperOnPresetCard, o && !r && XS.phosphatePositionIconWrapperOnPresetCardActive),
			children: [U(Mt, {
				title: s ? he(i) : "",
				children: U("span", { children: U("button", {
					type: "button",
					className: XS.phosphatePositionTrigger,
					disabled: r,
					"aria-label": "Select phosphate position",
					children: me(i, o)
				}) })
			}), !r && !s ? W("div", {
				className: XS.phosphatePositionSelector,
				children: [ge("left", !N), ge("right", !re)]
			}) : null]
		});
	}, F = function() {
		YS(C) > 1 ? o($_("updateSequenceInRNABuilder")) : (d?.events.modifySequenceInRnaBuilder.dispatch(C), JS(o, d));
	}, ve = function() {
		var e = g?.name;
		if (e) {
			if (g.editedName && !Ev(e)) o(gb(e));
			else {
				var t = S(g);
				if (g == null || !g.phosphate || t) {
					var n = QS(QS({}, g), {}, { connections: Xe(g, t) }), r = f.find(function(t) {
						return t.name === e;
					});
					r && c.nameInList !== r.name ? o(mb(e)) : (o(ub(n)), o(nb(n)), s || d?.events.selectPreset.dispatch(n), setTimeout(function() {
						RS(e);
					}, 0), qS(o));
				}
			}
		}
	}, ye = function() {
		if (T) JS(o, d);
		else {
			var e;
			_(c), x(c != null && (e = c.connections) != null && e.length ? ie(c) : void 0), qS(o);
		}
	}, be = function() {
		o(pb(!0));
	}, xe = function(e) {
		return p && p.groupName === e ? p.groupItem.label : (Vy(g, e)?.label ?? Vy(g, e)?.props.MonomerName) || void 0;
	}, Se = function(e) {
		return ee ? ee[e] : "";
	};
	(0, B.useEffect)(function() {
		var e = function(e) {
			e.key === "Escape" ? (ye(), e.preventDefault(), e.stopPropagation()) : e.key === "Enter" && (T ? F() : d?.events.startNewSequence.dispatch({}), e.preventDefault(), e.stopPropagation());
		};
		return d?.events.keyDown.add(e), function() {
			d?.events.keyDown.remove(e);
		};
	}, [d, C]);
	var Ce, we = !Uy(g) || oe;
	Ce = l && !T ? U(Mt, {
		title: se,
		children: U(MS, {
			disabled: we,
			primary: !0,
			"data-testid": "add-to-presets-btn",
			onClick: ve,
			children: "Add to Presets"
		})
	}) : n ? U(Mt, {
		title: se,
		children: U(MS, {
			primary: !0,
			disabled: T ? !O : we,
			"data-testid": "save-btn",
			onClick: T ? F : ve,
			children: T ? "Update" : "Save"
		})
	}) : U(MS, {
		"data-testid": "edit-btn",
		onClick: be,
		disabled: c.default,
		children: "Edit"
	});
	var Te = wx();
	return W(OS, {
		"data-testid": "rna-editor-expanded",
		className: a(T && "rna-editor-expanded--sequence-edit-mode"),
		children: [
			Te ? U(kS, {
				value: T ? w : g?.name,
				placeholder: "Name your structure",
				"data-testid": "name-your-structure-editbox",
				disabled: T,
				onChange: fe
			}) : W(NS, {
				selected: u === Ay.Presets,
				onClick: function() {
					return de(Ay.Presets);
				},
				children: [n ? U(FS, {
					value: T ? w : g?.name,
					placeholder: "Name your structure",
					"data-testid": "name-your-structure-editbox",
					disabled: T,
					onChange: fe
				}) : U(IS, { children: g?.name }), U(PS, { selected: u === Ay.Presets })]
			}),
			U(AS, {
				compact: Te,
				children: i.map(function(e) {
					var t = e.groupName, n = e.iconName, r = e.testId, i = t === q.PHOSPHATES;
					return U(DS, {
						selected: u === t,
						groupName: t,
						monomerName: T ? Se(t) : xe(t),
						iconName: n,
						testid: r,
						onClick: de(t),
						children: i ? _e(M) : null
					}, t);
				})
			}),
			W(jS, { children: [n ? U(MS, {
				"data-testid": "cancel-btn",
				onClick: ye,
				children: "Cancel"
			}) : U(MS, {
				"data-testid": "duplicate-btn",
				disabled: !Uy(g),
				onClick: function() {
					return r(g);
				},
				children: "Duplicate and Edit"
			}), Ce] })
		]
	});
}, eC = z("div", { target: "e1ms1w5g2" })({
	name: "1tk8yx0",
	styles: "padding:8px"
}), tC = z("button", { target: "e1ms1w5g1" })("width:100%;display:flex;justify-content:space-between;align-items:center;padding:8px;background-color:", function(e) {
	return e.theme.ketcher.color.background.primary;
}, ";font-weight:", function(e) {
	return e.theme.ketcher.font.weight.regular;
}, ";font-size:", function(e) {
	return e.theme.ketcher.font.size.regular;
}, ";border:none;border-radius:4px;text-transform:none;cursor:pointer;&.styled-header--sequence-edit-mode{background-color:", function(e) {
	return e.theme.ketcher.color.editMode.sequenceInRNABuilder;
}, ";}&.styled-header--expanded,&.styled-header--active-preset{border-radius:4px 4px 0 0;}"), nC = z(P, { target: "e1ms1w5g0" })("height:16px;width:16px;transform:", function(e) {
	return e.expanded ? "rotate(180deg)" : "none";
}, ";"), rC = function(e) {
	var t = e.duplicatePreset, n = Z(Ly), r = Z(Wy), i = Z(Kg), o = Gy(n), s = X(), c = (0, B.useState)(!1), l = R(c, 2), u = l[0], d = l[1];
	return (0, B.useEffect)(function() {
		n ? (n.name || r) && d(!0) : (s(fb()), s(ob(Ay.Presets)));
	}, [n]), (0, B.useEffect)(function() {
		s(cb({
			rnaPreset: n,
			isEditMode: r
		}));
	}, [r]), W(eC, {
		"data-testid": "rna-editor",
		children: [W(tC, {
			className: a(i && "styled-header--sequence-edit-mode", u && "styled-header--expanded", n?.name && "styled-header--active-preset"),
			onClick: function() {
				d(!u), n != null && n.nameInList || s(pb(!0));
			},
			"data-testid": "rna-builder-expand-button",
			children: ["RNA Builder", U(nC, {
				expanded: u,
				name: "chevron"
			})]
		}), n && (u ? U($S, {
			isEditMode: r,
			onDuplicate: t
		}) : U(dS, {
			name: n.name,
			fullName: o
		}))]
	});
}, iC = z("div", { target: "e1ocltcl0" })({
	name: "16fpk5u",
	styles: "height:100%;width:100%;display:flex;flex-direction:column;justify-content:space-between"
}), aC = function(e) {
	var t = e.ketcher;
	return Bn("scrollbar-width:thin;scrollbar-color:", t.color.scroll.regular, " ", t.color.scroll.inactive, ";&::-webkit-scrollbar{width:4px;height:4px;background-color:", t.color.scroll.inactive, ";border-radius:2px;-webkit-border-radius:2px;}&::-webkit-scrollbar-thumb{background-color:", t.color.scroll.regular, ";border-radius:2px;-webkit-border-radius:2px;}&::-webkit-scrollbar-thumb:active{background-color:", t.color.scroll.regular, ";}", "");
}, oC = { expandButton: "Modal-module_expandButton__J1QYl" };
function sC(e, t) {
	var n = Object.keys(e);
	if (Object.getOwnPropertySymbols) {
		var r = Object.getOwnPropertySymbols(e);
		t && (r = r.filter(function(t) {
			return Object.getOwnPropertyDescriptor(e, t).enumerable;
		})), n.push.apply(n, r);
	}
	return n;
}
function cC(e) {
	for (var t = 1; t < arguments.length; t++) {
		var n = arguments[t] == null ? {} : arguments[t];
		t % 2 ? sC(Object(n), !0).forEach(function(t) {
			I(e, t, n[t]);
		}) : Object.getOwnPropertyDescriptors ? Object.defineProperties(e, Object.getOwnPropertyDescriptors(n)) : sC(Object(n)).forEach(function(t) {
			Object.defineProperty(e, t, Object.getOwnPropertyDescriptor(n, t));
		});
	}
	return e;
}
var lC = z(Nr, { target: "e45wfhi5" })({
	name: "dzuq2w",
	styles: ".MuiPaper-root{min-width:304px;}"
}), uC = z(Yr, { target: "e45wfhi4" })(function(e) {
	var t = e.theme, n = e.hideborder;
	return {
		padding: "2px 4px 2px 12px",
		display: "flex",
		alignItems: "center",
		justifyContent: "space-between",
		fontFamily: `${t.ketcher.font.family.inter}`,
		fontSize: `${t.ketcher.font.size.medium}`,
		fontWeight: 500,
		textTransform: "capitalize",
		borderBottom: n ? "none" : "1px solid rgba(202, 211, 221, 1)"
	};
}, ""), dC = z("div", { target: "e45wfhi3" })({
	name: "10by1a4",
	styles: "margin-right:10px;font-size:14px"
}), fC = z(P, { target: "e45wfhi2" })({
	name: "4jxctt",
	styles: "width:16px;height:16px;color:rgba(51, 51, 51, 1)"
}), pC = z(Gr, { target: "e45wfhi1" })("padding:0;font-size:", function(e) {
	return e.theme.ketcher.font.size.medium;
}, ";line-height:17px;color:#000000;", function(e) {
	var t = e.theme;
	return aC(t);
}, ";"), mC = z(Rr, { target: "e45wfhi0" })("height:52px;margin:0;padding:0 12px;border-top:", function(e) {
	var t = e.theme;
	return e.withborder === "true" ? t.ketcher.border.small : "none";
}, ";justify-content:flex-end;.MuiButtonBase-root{border-radius:4px;font-size:", function(e) {
	return e.theme.ketcher.font.size.regular;
}, ";}"), Q = function(e) {
	var t = e.children, n = e.title, r = e.isOpen, i = e.showCloseButton, a = i === void 0 || i, o = e.showExpandButton, s = o !== void 0 && o, c = e.onClose, l = e.className, d = e.modalWidth, f = e.expanded, p = f !== void 0 && f, m = e.setExpanded, h = m === void 0 ? px : m, g = e.testId, _ = e.hideHeaderBorder, v = Oe(), y = (0, B.useMemo)(function() {
		return cC(cC({}, g ? { testid: g } : {}), {}, {
			"data-testid": g,
			style: cC({
				background: v.ketcher.color.background.primary,
				borderRadius: "8px",
				color: v.ketcher.color.text.primary
			}, s && {
				margin: "auto",
				width: p ? "100%" : d,
				height: p ? "100%" : void 0,
				maxWidth: "calc(min(1280px, 100%))",
				maxHeight: "calc(min(980px, 100%))"
			})
		});
	}, [
		g,
		v.ketcher.color.text.primary,
		v.ketcher.color.background.canvas,
		p
	]), b = (0, B.useMemo)(function() {
		return { style: {
			background: v.ketcher.color.background.overlay,
			opacity: .4
		} };
	}, [v.ketcher.color.background.overlay]), x = {
		Content: null,
		Footer: null
	};
	return B.Children.forEach(t, function(e) {
		e.type === pC ? x.Content = e : e.type === mC && (x.Footer = e);
	}), W(lC, {
		BackdropProps: b,
		PaperProps: y,
		open: r,
		onClose: c,
		container: document.querySelector(he),
		disableEscapeKeyDown: !a,
		className: l,
		sx: { padding: "24px" },
		children: [
			n || a || s ? W(uC, {
				hideborder: _,
				children: [U(dC, { children: n }), W("span", { children: [s && U(u, {
					title: p ? "Minimize window" : "Expand window",
					"data-testid": "expand-window-button",
					className: oC.expandButton,
					onClick: function() {
						h(!p);
					},
					children: U(fC, { name: p ? "minimize-expansion" : "expand" })
				}), a && U(u, {
					title: "Close window",
					onClick: c,
					"data-testid": "close-window-button",
					children: U(fC, { name: "close" })
				})] })]
			}) : "",
			x.Content,
			x.Footer
		]
	});
};
Q.Content = pC, Q.Footer = mC;
var hC = [
	"label",
	"clickHandler",
	"children",
	"styleType"
];
function gC(e, t) {
	var n = Object.keys(e);
	if (Object.getOwnPropertySymbols) {
		var r = Object.getOwnPropertySymbols(e);
		t && (r = r.filter(function(t) {
			return Object.getOwnPropertyDescriptor(e, t).enumerable;
		})), n.push.apply(n, r);
	}
	return n;
}
function _C(e) {
	for (var t = 1; t < arguments.length; t++) {
		var n = arguments[t] == null ? {} : arguments[t];
		t % 2 ? gC(Object(n), !0).forEach(function(t) {
			I(e, t, n[t]);
		}) : Object.getOwnPropertyDescriptors ? Object.defineProperties(e, Object.getOwnPropertyDescriptors(n)) : gC(Object(n)).forEach(function(t) {
			Object.defineProperty(e, t, Object.getOwnPropertyDescriptor(n, t));
		});
	}
	return e;
}
var vC = {
	name: "zlt300",
	styles: "padding:5px 8px;border-radius:2px;text-transform:none;line-height:14px;font-size:12px;text-align:center;&.MuiButtonBase-root{width:unset;min-width:70px;}"
}, yC = z(be, { target: "ejign8b1" })(function(e) {
	var t = e.theme;
	return {
		backgroundColor: t.ketcher.color.button.primary.active,
		border: `1px solid ${t.ketcher.color.button.primary.active}`,
		color: "rgb(245, 245, 245)",
		fontWeight: t.ketcher.font.weight.regular,
		width: "62px",
		height: "24px",
		"&:hover": { backgroundColor: t.ketcher.color.button.primary.hover },
		"&:disabled": {
			background: t.ketcher.color.button.primary.disabled,
			border: "1px solid transparent",
			opacity: .4
		}
	};
}, vC, ""), bC = z(be, { target: "ejign8b0" })(function(e) {
	var t = e.theme;
	return {
		backgroundColor: "transparent",
		border: `1px solid ${t.ketcher.color.button.secondary.active}`,
		color: t.ketcher.color.button.secondary.active,
		fontWeight: t.ketcher.font.weight.regular,
		width: "72px",
		height: "24px",
		"&:hover": {
			border: `1px solid ${t.ketcher.color.button.secondary.hover}`,
			color: t.ketcher.color.button.secondary.hover
		},
		"&:disabled": {
			border: `1px solid ${t.ketcher.color.button.secondary.disabled}`,
			color: t.ketcher.color.button.secondary.disabled
		},
		"&:clicked": {
			border: `1px solid ${t.ketcher.color.button.secondary.clicked}`,
			color: t.ketcher.color.button.secondary.clicked
		}
	};
}, vC, ""), xC = function(e) {
	var t = e.label, n = e.clickHandler, r = e.children, i = e.styleType, a = ve(e, hC);
	return U(i === "secondary" ? bC : yC, _C(_C({
		onClick: n,
		title: a.title || t
	}, a), {}, { children: r || t }));
}, SC = z("div", { target: "e117eqk622" })({
	name: "uawiic",
	styles: "display:flex;flex-direction:column;justify-content:flex-start;overflow:hidden;height:100%"
}), CC = z(d, { target: "e117eqk621" })({
	name: "u6kpdv",
	styles: "min-height:32px"
}), wC = z("div", { target: "e117eqk620" })({
	name: "isibqt",
	styles: "flex-grow:2;display:flex;flex-direction:column;min-height:0;>div{overflow:visible;display:flex;flex-direction:column;min-height:0;>div+div{overflow:visible;display:flex;flex-direction:column;min-height:0;flex:1 1 auto;}}"
}), TC = z("div", { target: "e117eqk619" })({
	name: "1gdm1f0",
	styles: "flex:1 1 auto;min-height:0;overflow-y:auto;overflow-x:hidden"
}), EC = z("div", { target: "e117eqk618" })("position:relative;width:100%;display:flex;flex-direction:column;gap:8px;justify-content:start;padding:", function(e) {
	return e.compact ? "4px" : "8px";
}, ";", function(e) {
	return e.compact ? "" : "flex: 1 1 auto; min-height: 0;";
}, ";"), DC = z("div", { target: "e117eqk617" })({
	name: "6imefc",
	styles: "flex-grow:1;min-height:0;background-color:#f7f9fa;border-radius:4px;margin:4px 8px;padding:4px;&.first-tab{border-radius:0 4px 4px 4px;}&.last-tab{border-radius:4px 0 4px 4px;}"
}), OC = z("div", { target: "e117eqk616" })("height:100%;background-color:", function(e) {
	return e.theme.ketcher.color.tab.content;
}, ";border-radius:2px;overflow:auto;"), kC = z(y, { target: "e117eqk615" })("background-color:", function(e) {
	return e.theme.ketcher.color.button.transparent.active;
}, ";color:", function(e) {
	return e.theme.ketcher.color.text.light;
}, ";border-color:", function(e) {
	return e.theme.ketcher.color.text.light;
}, ";"), AC = z("div", { target: "e117eqk614" })({
	name: "388a8c",
	styles: "position:relative;display:flex;flex-direction:row;align-items:center;justify-content:flex-start;gap:8px;width:100%"
}), jC = z(kC, { target: "e117eqk613" })({
	name: "1uga7aq",
	styles: "height:24px;border-radius:4px;font-size:12px"
}), MC = z("button", { target: "e117eqk612" })("position:relative;display:inline-flex;align-items:center;justify-content:center;width:24px;height:24px;padding:0;margin-left:auto;background-color:transparent;border:none;border-radius:4px;cursor:pointer;color:#333333;>svg{width:16px;height:16px;}", function(e) {
	var t = e.hasIndicator, n = e.theme;
	return t ? `
    &::after {
      content: '';
      position: absolute;
      top: 5px;
      right: 5px;
      width: 6px;
      height: 6px;
      border-radius: 50%;
      border: 1px solid #E1E5EA;
      background-color: ${n.ketcher.color.button.primary.active};
    }
  ` : "";
}, ";"), NC = z("div", { target: "e117eqk611" })("position:absolute;top:calc(100% + 4px);right:0;z-index:10;display:flex;flex-direction:column;min-width:160px;padding:4px;background-color:#ffffff;border:1px solid #cad3dd;border-radius:4px;box-shadow:0 4px 12px rgba(0, 0, 0, 0.12);font-size:12px;color:", function(e) {
	return e.theme.ketcher.color.text.primary;
}, ";"), PC = z("label", { target: "e117eqk610" })({
	name: "nwcyk",
	styles: "display:flex;align-items:center;gap:5px;cursor:pointer;user-select:none;margin-left:6px;margin-top:10px"
}), FC = z("input", { target: "e117eqk69" })({
	name: "gwlugh",
	styles: "position:absolute;opacity:0;cursor:pointer;&+span{display:inline-block;width:16px;height:16px;vertical-align:middle;background-image:url(\"data:image/svg+xml,%3Csvg width='16' height='16' viewBox='0 0 16 16' fill='none' xmlns='http://www.w3.org/2000/svg'%3E%3Crect x='0.5' y='0.5' width='15' height='15' rx='3.5' fill='white' stroke='%23B4B9D6'/%3E%3C/svg%3E%0A\");background-repeat:no-repeat;background-size:100%;}&:checked+span{background-image:url(\"data:image/svg+xml,%3Csvg width='16' height='16' viewBox='0 0 16 16' fill='none' xmlns='http://www.w3.org/2000/svg'%3E%3Crect width='16' height='16' rx='4' fill='%23167782'/%3E%3Cpath d='M6.33711 11.8079L2.42578 7.63124L3.39911 6.71991L6.36845 9.89124L12.6171 3.64258L13.5598 4.58524L6.33711 11.8079Z' fill='white'/%3E%3C/svg%3E%0A\");}"
}), IC = z("div", { target: "e117eqk68" })("font-size:12px;font-weight:400;letter-spacing:0.4px;margin:5px 0 5px 2px;color:", function(e) {
	return e.theme.ketcher.color.text.primary;
}, ";"), LC = z("hr", { target: "e117eqk67" })({
	name: "vs4chz",
	styles: "width:100%;height:1px;margin:8px 0 4px;border:none;background-color:#e1e5ea"
}), RC = z("div", { target: "e117eqk66" })({
	name: "jhfq5e",
	styles: "display:flex;flex-direction:row;justify-content:flex-end;gap:8px;margin-top:4px"
}), zC = z(xC, { target: "e117eqk65" })({
	name: "efr2h1",
	styles: "&.MuiButtonBase-root{width:auto;min-width:unset;padding-left:7px;padding-right:7px;border-radius:4px;}"
}), BC = z(zC, { target: "e117eqk64" })({
	name: "syzhjw",
	styles: "&.MuiButtonBase-root{border:none;margin-right:auto;padding-left:0;margin-left:6px;color:#167782;}"
}), VC = z("div", { target: "e117eqk63" })({
	name: "1q5khk2",
	styles: "width:100%;height:100%;background-color:#eff2f594;position:absolute;top:0;left:0"
}), HC = z("div", { target: "e117eqk62" })({
	name: "bimmx8",
	styles: "display:flex;justify-content:space-between;gap:8px;padding:6px 8px 0"
}), UC = z("div", { target: "e117eqk61" })({
	name: "qnk899",
	styles: "position:relative;display:flex;align-items:center;&.rna-tab--selected{& button{border-radius:4px 4px 0 0;background-color:#f7f9fa;}&::after{content:'';position:absolute;bottom:-4px;left:0;right:0;height:8px;background-color:#f7f9fa;}}"
}), WC = z(Et, { target: "e117eqk60" })("height:24px;min-height:24px;min-width:24px;", function(e) {
	return e.selected ? "min-width: 104px;" : "";
}, " display:flex;flex-direction:row;gap:4px;align-items:center;justify-content:center;padding:4px;", function(e) {
	return e.selected ? "margin-top: -8px;" : "";
}, " font-weight:400;font-size:10px;border-radius:4px;background-color:white;opacity:", function(e) {
	return e.selected ? 1 : .6;
}, ";text-transform:none;&:hover{background-color:#f3f8f9;}>svg{height:16px;width:16px;color:#b4b9d6;&.MuiTab-iconWrapper{margin:0;}}");
function GC(e, t) {
	var n = Object.keys(e);
	if (Object.getOwnPropertySymbols) {
		var r = Object.getOwnPropertySymbols(e);
		t && (r = r.filter(function(t) {
			return Object.getOwnPropertyDescriptor(e, t).enumerable;
		})), n.push.apply(n, r);
	}
	return n;
}
function KC(e) {
	for (var t = 1; t < arguments.length; t++) {
		var n = arguments[t] == null ? {} : arguments[t];
		t % 2 ? GC(Object(n), !0).forEach(function(t) {
			I(e, t, n[t]);
		}) : Object.getOwnPropertyDescriptors ? Object.defineProperties(e, Object.getOwnPropertyDescriptors(n)) : GC(Object(n)).forEach(function(t) {
			Object.defineProperty(e, t, Object.getOwnPropertyDescriptor(n, t));
		});
	}
	return e;
}
var qC = function(e) {
	var t = Z(K_), n = Z(tb), r = q_(V_(t, e)), i = q_(U_(t));
	return (0, B.useMemo)(function() {
		return [
			{
				groupName: Ay.Presets,
				iconName: "preset",
				groups: [{ groupItems: n }]
			},
			{
				groupName: q.SUGARS,
				iconName: "sugar",
				groups: r.map(function(e) {
					return KC(KC({}, e), {}, { groupItems: e.groupItems.filter(function(e) {
						return e.props?.MonomerClass === st.Sugar;
					}) });
				}).filter(function(e) {
					return e.groupItems.length;
				})
			},
			{
				groupName: q.BASES,
				iconName: "base",
				groups: r.map(function(e) {
					return KC(KC({}, e), {}, { groupItems: e.groupItems.filter(function(e) {
						return e.props?.MonomerClass === st.Base;
					}) });
				}).filter(function(e) {
					return e.groupItems.length;
				})
			},
			{
				groupName: q.PHOSPHATES,
				iconName: "phosphate",
				groups: r.map(function(e) {
					return KC(KC({}, e), {}, { groupItems: e.groupItems.filter(function(e) {
						return e.props?.MonomerClass === st.Phosphate;
					}) });
				}).filter(function(e) {
					return e.groupItems.length;
				})
			},
			{
				groupName: q.NUCLEOTIDES,
				iconName: "nucleotide",
				groups: i
			}
		];
	}, [
		r,
		n,
		i
	]);
};
function JC(e, t) {
	var n = Object.keys(e);
	if (Object.getOwnPropertySymbols) {
		var r = Object.getOwnPropertySymbols(e);
		t && (r = r.filter(function(t) {
			return Object.getOwnPropertyDescriptor(e, t).enumerable;
		})), n.push.apply(n, r);
	}
	return n;
}
function YC(e) {
	for (var t = 1; t < arguments.length; t++) {
		var n = arguments[t] == null ? {} : arguments[t];
		t % 2 ? JC(Object(n), !0).forEach(function(t) {
			I(e, t, n[t]);
		}) : Object.getOwnPropertyDescriptors ? Object.defineProperties(e, Object.getOwnPropertyDescriptors(n)) : JC(Object(n)).forEach(function(t) {
			Object.defineProperty(e, t, Object.getOwnPropertyDescriptor(n, t));
		});
	}
	return e;
}
var XC = {
	fivePrime: !1,
	threePrime: !1,
	noPhosphate: !1
}, ZC = function(e) {
	var t = e.onClose, n = Rt(), r = Z(Zy), i = (0, B.useState)(r), a = R(i, 2), o = a[0], s = a[1], c = (0, B.useRef)(null);
	(0, B.useEffect)(function() {
		var e = function(e) {
			var n = e.target;
			c.current && n && c.current.contains(n) || n instanceof Element && n.closest("[data-testid=\"preset-filter-button\"]") || t();
		}, n = function(e) {
			e.key === "Escape" && t();
		};
		return document.addEventListener("mousedown", e), document.addEventListener("keydown", n), function() {
			document.removeEventListener("mousedown", e), document.removeEventListener("keydown", n);
		};
	}, [t]);
	var l = function(e) {
		return function() {
			s(function(t) {
				return YC(YC({}, t), {}, I({}, e, !t[e]));
			});
		};
	};
	return W(NC, {
		ref: c,
		"data-testid": "preset-phosphate-filter-popup",
		onClick: function(e) {
			return e.stopPropagation();
		},
		children: [
			U(IC, { children: "Filter" }),
			W(PC, { children: [
				U(FC, {
					type: "checkbox",
					checked: o.fivePrime,
					onChange: l("fivePrime"),
					"data-testid": "preset-filter-5-phosphate"
				}),
				U("span", {}),
				" 5'-phosphate"
			] }),
			W(PC, { children: [
				U(FC, {
					type: "checkbox",
					checked: o.threePrime,
					onChange: l("threePrime"),
					"data-testid": "preset-filter-3-phosphate"
				}),
				U("span", {}),
				" 3'-phosphate"
			] }),
			W(PC, { children: [
				U(FC, {
					type: "checkbox",
					checked: o.noPhosphate,
					onChange: l("noPhosphate"),
					"data-testid": "preset-filter-no-phosphate"
				}),
				U("span", {}),
				" No phosphate group"
			] }),
			U(LC, {}),
			W(RC, { children: [U(BC, {
				styleType: "secondary",
				label: "Reset all",
				clickHandler: function() {
					s(XC), n(bb(XC)), t();
				},
				"data-testid": "preset-filter-reset"
			}), U(zC, {
				label: "Set",
				clickHandler: function() {
					n(bb(o)), t();
				},
				"data-testid": "preset-filter-set"
			})] })
		]
	});
}, QC = (0, B.memo)(function(e) {
	var t = e.activeRnaBuilderItem, n = e.groupsData, r = e.onNewPresetClick, i = e.onSelectItem, o = e.duplicatePreset, s = e.editPreset, c = e.libraryName, l = Rt(), u = Z(tb), d = Z(K_), f = Z(Wy), p = Z(Yy), m = Z($y), h = Z(Zy), g = !!(h?.fivePrime || h?.threePrime || h?.noPhosphate), _ = (0, B.useState)(!1), v = R(_, 2), y = v[0], b = v[1];
	return W(H, { children: [U(HC, { children: n.map(function(e) {
		var n = e.groupName, r = e.groups, i = e.iconName, o = n === t, s = H_(d, n), c = [].concat(L(r), L(s)).reduce(function(e, t) {
			return e + (t.groupItems.length || 0);
		}, 0), u = o ? `${n} (${c})` : null;
		return U(UC, {
			className: a(o && "rna-tab--selected"),
			children: U(WC, {
				label: u,
				title: n,
				selected: o,
				icon: U(P, { name: i }),
				onClick: function() {
					return l(ob(n));
				},
				"data-testid": `summary-${n}`
			})
		}, n);
	}) }), n.map(function(e) {
		var n = e.groupName, l = e.groups;
		if (n !== t) return null;
		var h = H_(d, n), _ = n === Ay.Presets ? W(EC, {
			compact: !0,
			children: [
				W(AC, { children: [
					U(jC, {
						onClick: r,
						"data-testid": "new-preset-button",
						children: "Add new"
					}),
					U(MC, {
						type: "button",
						active: y,
						hasIndicator: g,
						onClick: function(e) {
							e.stopPropagation(), b(function(e) {
								return !e;
							});
						},
						"aria-label": "Filter presets by phosphate position",
						"data-testid": "preset-filter-button",
						children: U(P, { name: "filter" })
					}),
					y && U(ZC, { onClose: function() {
						return b(!1);
					} })
				] }),
				U(oS, {
					duplicatePreset: o,
					editPreset: s,
					presets: u
				}),
				f && !p && U(VC, {})
			]
		}) : U(EC, {
			compact: !0,
			children: W(H, { children: [l.map(function(e) {
				var t = e.groupItems, r = e.groupTitle;
				return U(Jx, {
					title: [q.BASES, q.NUCLEOTIDES].includes(n) || l.length > 1 ? r : void 0,
					groupName: n,
					items: t,
					selectedMonomerUniqueKey: m,
					onItemClick: function(e) {
						return i(e, n);
					}
				}, r);
			}), h.map(function(e) {
				var t = e.groupTitle, r = e.groupItems;
				return U(Jx, {
					title: t,
					items: r,
					libraryName: c,
					selectedMonomerUniqueKey: m,
					onItemClick: function(e) {
						return i(e, n);
					}
				}, t);
			})] })
		}), v = t === Ay.Presets, x = t === q.NUCLEOTIDES;
		return U(DC, {
			className: a(v && "first-tab", x && "last-tab"),
			children: U(OC, { children: _ })
		}, n);
	})] });
}), $C = function(e) {
	var t = e.groupName, n = e.quantity, r = e.expanded, i = e.iconName;
	return W(Zx, {
		"data-testid": `summary-${t}`,
		children: [
			U($x, { name: i }),
			W(Qx, { children: [
				t,
				" (",
				n,
				")"
			] }),
			U($x, {
				name: "chevron",
				expanded: r
			})
		]
	});
}, ew = (0, B.memo)(function(e) {
	var t = e.activeRnaBuilderItem, n = e.groupsData, r = e.newPreset, i = e.onNewPresetClick, a = e.onSelectItem, o = e.duplicatePreset, s = e.editPreset, c = e.libraryName, l = Rt(), u = Z(tb), d = Z(K_), f = Z(Wy), p = Z(Yy), m = Z($y), h = Z(Zy), g = !!(h?.fivePrime || h?.threePrime || h?.noPhosphate), _ = (0, B.useState)(t), v = R(_, 2), y = v[0], b = v[1], x = (0, B.useState)(!1), S = R(x, 2), C = S[0], w = S[1], T = function(e) {
		y === e ? b(null) : (b(e), l(cb({
			rnaPreset: r,
			isEditMode: f
		})));
	};
	return (0, B.useEffect)(function() {
		b(t);
	}, [t]), U(H, { children: n.map(function(e) {
		var t = y === e.groupName, n = H_(d, e.groupName), r = [].concat(L(e.groups), L(n)).reduce(function(e, t) {
			return e + (t.groupItems.length || 0);
		}, 0), l = U($C, {
			iconName: e.iconName,
			groupName: e.groupName,
			quantity: r,
			expanded: t
		}), h = e.groupName === Ay.Presets ? W(EC, { children: [
			W(AC, { children: [
				U(jC, {
					onClick: i,
					"data-testid": "new-preset-button",
					children: "Add new"
				}),
				U(MC, {
					type: "button",
					active: C,
					hasIndicator: g,
					onClick: function(e) {
						e.stopPropagation(), w(function(e) {
							return !e;
						});
					},
					"aria-label": "Filter presets by phosphate position",
					"data-testid": "preset-filter-button",
					children: U(P, { name: "filter" })
				}),
				C && U(ZC, { onClose: function() {
					return w(!1);
				} })
			] }),
			U(TC, { children: U(oS, {
				duplicatePreset: o,
				editPreset: s,
				presets: u
			}) }),
			f && !p && U(VC, {})
		] }) : U(EC, { children: W(H, { children: [e.groups.map(function(t) {
			var n = t.groupItems, r = t.groupTitle;
			return U(Jx, {
				title: [
					q.BASES,
					q.NUCLEOTIDES,
					q.PEPTIDES
				].includes(e.groupName) ? r : void 0,
				groupName: e.groupName,
				items: n,
				selectedMonomerUniqueKey: m,
				onItemClick: function(t) {
					return a(t, e.groupName);
				}
			}, r);
		}), n.map(function(t) {
			return U(Jx, {
				title: t.groupTitle,
				items: t.groupItems,
				libraryName: c,
				selectedMonomerUniqueKey: m,
				onItemClick: function(t) {
					return a(t, e.groupName);
				}
			}, t.groupTitle);
		})] }) });
		return e.groupName === Ay.Presets && t ? U(wC, { children: U(CC, {
			"data-testid": "styled-accordion",
			dataTestIdDetails: `rna-accordion-details-${e.groupName}`,
			summary: l,
			details: h,
			expanded: t,
			onSummaryClick: function() {
				return T(e.groupName);
			}
		}) }, e.groupName) : U(CC, {
			"data-testid": "styled-accordion",
			dataTestIdDetails: `rna-accordion-details-${e.groupName}`,
			summary: l,
			details: h,
			expanded: t,
			onSummaryClick: function() {
				return T(e.groupName);
			}
		}, e.groupName);
	}) });
});
function tw(e, t) {
	var n = Object.keys(e);
	if (Object.getOwnPropertySymbols) {
		var r = Object.getOwnPropertySymbols(e);
		t && (r = r.filter(function(t) {
			return Object.getOwnPropertyDescriptor(e, t).enumerable;
		})), n.push.apply(n, r);
	}
	return n;
}
function nw(e) {
	for (var t = 1; t < arguments.length; t++) {
		var n = arguments[t] == null ? {} : arguments[t];
		t % 2 ? tw(Object(n), !0).forEach(function(t) {
			I(e, t, n[t]);
		}) : Object.getOwnPropertyDescriptors ? Object.defineProperties(e, Object.getOwnPropertyDescriptors(n)) : tw(Object(n)).forEach(function(t) {
			Object.defineProperty(e, t, Object.getOwnPropertyDescriptor(n, t));
		});
	}
	return e;
}
var rw = function(e) {
	var t = e.view, n = e.libraryName, r = e.duplicatePreset, i = e.editPreset, a = Rt(), o = Z(Fy), s = Z(Ly), c = Z(Wy), l = Z(K), u = Z(Kg), d = (0, B.useState)(s), f = R(d, 2), p = f[0], m = f[1];
	(0, B.useEffect)(function() {
		a(ob(c && s ? o : Ay.Presets));
	}, [c]);
	var h = qC(n), g = (0, B.useCallback)(function() {
		a(fb()), a(ob(Ay.Presets)), a(pb(!0));
	}, [a]), _ = (0, B.useCallback)(function(e, t) {
		if (c && a(sb(k_(e))), !u && !c && l?.events.selectMonomer.dispatch(e), c) {
			var n = w(e) ? e.monomers[0].monomerItem.props.MonomerClass?.toLowerCase() : e.props.MonomerClass?.toLowerCase();
			m(nw(nw({}, p), {}, I({}, n, e))), a(lb({
				groupName: t,
				groupItem: e
			})), a(ob(t));
		}
	}, [
		a,
		l,
		c,
		u,
		p
	]);
	return U(SC, {
		"data-testid": "rna-accordion",
		children: t === "tabs" ? U(QC, {
			activeRnaBuilderItem: o,
			groupsData: h,
			onNewPresetClick: g,
			onSelectItem: _,
			libraryName: n,
			editPreset: i,
			duplicatePreset: r
		}) : U(ew, {
			activeRnaBuilderItem: o,
			groupsData: h,
			newPreset: p,
			onNewPresetClick: g,
			onSelectItem: _,
			libraryName: n,
			editPreset: i,
			duplicatePreset: r
		})
	});
}, iw = function(e) {
	var t = e.libraryName, n = e.duplicatePreset, r = e.editPreset, i = X(), a = Z(Ky), o = Z(qy), s = Z(Jy), c = wx(), l = function() {
		a.length > 0 && i(mb("")), o.length > 0 && i(hb("")), s.length > 0 && i(gb(""));
	};
	return W(iC, { children: [
		U(rC, { duplicatePreset: n }),
		U(rw, {
			libraryName: t,
			duplicatePreset: n,
			editPreset: r,
			view: c ? "tabs" : "accordion"
		}),
		W(Q, {
			isOpen: !!a || !!o || !!s,
			title: "Error Message",
			onClose: l,
			children: [U(Q.Content, { children: W("div", {
				style: { padding: "12px" },
				children: [
					a && `Preset with name "${a}" already exists. Please choose another name.`,
					o && `Preset with name "${o}" can't be used. Because it is impossible to establish bonds between monomers. Edit it's structure or choose another one.`,
					s && "The preset code must consist only of uppercase and lowercase letters, numbers, hyphens (-), underscores (_), and asterisks (*)."
				]
			}) }), U(Q.Footer, { children: U(kC, {
				onClick: l,
				children: "Close"
			}) })]
		})
	] });
}, aw = function(e, t) {
	return [
		{
			caption: C_,
			tooltip: "Favorites",
			component: sS,
			testId: "FAVORITES-TAB",
			props: {
				libraryName: u_,
				duplicatePreset: e,
				editPreset: t
			}
		},
		{
			caption: "Peptides",
			component: sS,
			testId: "PEPTIDES-TAB",
			props: { libraryName: f_.PEPTIDE }
		},
		{
			caption: "RNA",
			testId: "RNA-TAB",
			component: iw,
			props: {
				libraryName: f_.RNA,
				duplicatePreset: e,
				editPreset: t
			}
		},
		{
			caption: "CHEM",
			component: sS,
			testId: "CHEM-TAB",
			props: { libraryName: f_.CHEM }
		}
	];
};
function ow(e, t) {
	var n = Object.keys(e);
	if (Object.getOwnPropertySymbols) {
		var r = Object.getOwnPropertySymbols(e);
		t && (r = r.filter(function(t) {
			return Object.getOwnPropertyDescriptor(e, t).enumerable;
		})), n.push.apply(n, r);
	}
	return n;
}
function sw(e) {
	for (var t = 1; t < arguments.length; t++) {
		var n = arguments[t] == null ? {} : arguments[t];
		t % 2 ? ow(Object(n), !0).forEach(function(t) {
			I(e, t, n[t]);
		}) : Object.getOwnPropertyDescriptors ? Object.defineProperties(e, Object.getOwnPropertyDescriptors(n)) : ow(Object(n)).forEach(function(t) {
			Object.defineProperty(e, t, Object.getOwnPropertyDescriptor(n, t));
		});
	}
	return e;
}
var cw = "_Copy", lw = function(e) {
	var t = e.toggleLibraryVisibility, n = (0, B.useRef)([]), r = X(), i = Z(J_);
	(0, B.useEffect)(function() {
		r(L_(""));
	}, [r]), Z(eb, function(e) {
		return n.current = e, !0;
	});
	var a = (0, B.useCallback)(function(e) {
		r(L_(e.target.value));
	}, [r]), o = (0, B.useCallback)(function(e) {
		var t = `${e?.name}${cw}`, i;
		do
			i = n.current.find(function(e) {
				return e.name === t;
			}), i && (t += cw);
		while (i);
		if (i) r(mb(t));
		else {
			var a = i ? `${t}${cw}` : t;
			r(nb(sw(sw({}, e), {}, {
				name: a,
				nameInList: a,
				default: !1,
				favorite: !1
			}))), r(pb(!0)), RS(e?.name);
		}
	}, [r]), s = (0, B.useCallback)(function(e) {
		r(nb(e)), r(pb(!0));
	}, [r]), c = (0, B.useMemo)(function() {
		return aw(o, s);
	}, [o, s]), l = (0, B.useCallback)(function(e, t) {
		r(R_(t));
	}, [r]);
	return W(Nb, {
		"data-testid": "monomer-library",
		children: [W(Pb, { children: [W(Fb, { children: [U(Lb, { name: "search" }), U(Rb, {
			type: "search",
			"data-testid": "monomer-library-input",
			onChange: a,
			placeholder: "Search by name..."
		})] }), U(Ib, {
			title: "Hide library",
			onClick: t,
			"data-testid": "hide-monomer-library",
			children: U(P, { name: "arrows-right" })
		})] }), U(fx, {
			tabs: c,
			selectedTabIndex: i,
			onChange: l
		})]
	});
}, uw = z("div", { target: "emj253a0" })(function(e) {
	var t = e.theme;
	return {
		margin: 0,
		fontSize: t.ketcher.font.size.regular,
		position: "absolute",
		top: "12px",
		cursor: "pointer",
		visibility: "visible",
		opacity: 1,
		whiteSpace: "nowrap",
		display: "flex",
		alignItems: "center",
		lineHeight: 1,
		userSelect: "none",
		backgroundColor: t.ketcher.color.button.primary.active,
		color: t.ketcher.color.button.text.primary,
		right: "12px",
		padding: "10px 8px",
		borderRadius: "4px",
		"& > span": {
			display: "flex",
			justifyContent: "center",
			alignItems: "center",
			"&.icon": { marginRight: "2px" }
		}
	};
}, ""), dw = function(e) {
	var t = e.onClick;
	return W(uw, {
		onClick: t,
		"data-testid": "show-monomer-library",
		children: [
			U("span", {
				className: "icon",
				children: U(P, { name: "arrows-left" })
			}),
			" ",
			"Show Library"
		]
	});
}, fw = z("div", { target: "e10ckbgw0" })("display:flex;flex-direction:row;justify-content:space-between;align-items:flex-start;width:40px;height:12px;margin-top:10px;& span{display:inline-block;width:8px;height:8px;border:2px solid ", function(e) {
	return e.theme.ketcher.color.spinner;
}, ";border-radius:100%;box-sizing:border-box;&:nth-of-type(1){animation:bounce 1s ease-in-out infinite;}&:nth-of-type(2){animation:bounce 1s ease-in-out 0.33s infinite;}&:nth-of-type(3){animation:bounce 1s ease-in-out 0.66s infinite;}}@keyframes bounce{0%,75%,100%{-webkit-transform:translateY(0);-ms-transform:translateY(0);-o-transform:translateY(0);transform:translateY(0);}25%{-webkit-transform:translateY(-100%);-ms-transform:translateY(-100%);-o-transform:translateY(-100%);transform:translateY(-100%);}}"), pw = function() {
	return W(fw, {
		className: "loading-spinner",
		"data-testid": "loading-spinner",
		children: [
			U("span", {}),
			U("span", {}),
			U("span", {})
		]
	});
}, mw = "file-thumbnail", hw = z("div", { target: "ep0evuw1" })({
	name: "1btsn9l",
	styles: "width:410px;min-height:23em;flex:1;display:flex;flex-direction:column;align-items:center;justify-content:center"
}), gw = z("div", { target: "ep0evuw0" })({
	name: "vbftiw",
	styles: "display:flex;flex-direction:row;align-items:center;svg{margin-right:13px;}p{color:#585858;font-size:16px;line-height:19px;}"
}), _w = function(e) {
	var t = e.fileName;
	return W(hw, { children: [t && W(gw, { children: [U(P, { name: mw }), U("p", { children: t })] }), U(pw, {})] });
}, vw = z("p", { target: "eff4ds61" })("font-size:10px;text-transform:uppercase;color:", function(e) {
	return e.theme.ketcher.color.text.light;
}, ";margin:0;text-align:center;line-height:12px;"), yw = z("p", { target: "eff4ds60" })("font-size:10px;margin:0;text-align:center;color:", function(e) {
	return e.theme.ketcher.color.text.primary;
}, ";opacity:50%;line-height:12px;"), bw = [
	"textLabel",
	"iconName",
	"disabled",
	"disabledText"
];
function xw(e, t) {
	var n = Object.keys(e);
	if (Object.getOwnPropertySymbols) {
		var r = Object.getOwnPropertySymbols(e);
		t && (r = r.filter(function(t) {
			return Object.getOwnPropertyDescriptor(e, t).enumerable;
		})), n.push.apply(n, r);
	}
	return n;
}
function Sw(e) {
	for (var t = 1; t < arguments.length; t++) {
		var n = arguments[t] == null ? {} : arguments[t];
		t % 2 ? xw(Object(n), !0).forEach(function(t) {
			I(e, t, n[t]);
		}) : Object.getOwnPropertyDescriptors ? Object.defineProperties(e, Object.getOwnPropertyDescriptors(n)) : xw(Object(n)).forEach(function(t) {
			Object.defineProperty(e, t, Object.getOwnPropertyDescriptor(n, t));
		});
	}
	return e;
}
var Cw = {
	width: "100%",
	height: "100%",
	display: "flex",
	alignItems: "center",
	flexDirection: "column",
	justifyContent: "space-between"
}, ww = z(P, { target: "erk2iw52" })("filter:", function(e) {
	return e.disabled ? "grayscale(1)" : "";
}, ";opacity:", function(e) {
	return e.disabled ? "0.6" : "1";
}, ";"), Tw = { backgroundColor: "#F8FEFFFF" }, Ew = z("div", { target: "erk2iw51" })("display:flex;flex-direction:column;align-items:center;&>span{font-size:", function(e) {
	return e.theme.ketcher.font.size.small;
}, ";color:", function(e) {
	return e.theme.ketcher.color.text.primary;
}, ";opacity:50%;}&>svg{margin-bottom:8px;}"), Dw = z("button", { target: "erk2iw50" })({
	name: "1tt0jw3",
	styles: "all:unset;width:100%;height:100%;display:flex;align-items:center;flex-direction:column;justify-content:space-between;cursor:pointer;&:disabled{cursor:default;}"
}), Ow = function(e) {
	var t = e.textLabel, n = e.iconName, r = e.disabled, i = e.disabledText, a = ve(e, bw), o = on(Sw({
		multiple: !1,
		noClick: !0,
		disabled: r,
		onFileDialogOpen: function() {
			document.fullscreenElement && (window.isKetcherFullscreenBeforeFilePicker = !0);
		},
		onFileDialogCancel: function() {
			var e = window;
			if (e.isKetcherFullscreenBeforeFilePicker) {
				var t, n;
				(t = (n = document.documentElement).requestFullscreen) == null || t.call(n).catch(function() {}), e.isKetcherFullscreenBeforeFilePicker = !1;
			}
		}
	}, a)), s = o.getRootProps, c = o.getInputProps, l = o.isDragActive, u = o.open;
	return W(Dw, Sw(Sw({}, s({ style: (0, B.useMemo)(function() {
		return Sw(Sw({}, Cw), l ? Tw : {});
	}, [l]) })), {}, {
		role: void 0,
		onClick: u,
		onKeyDown: function(e) {
			(e.key === "Enter" || e.key === " ") && (e.preventDefault(), r || u());
		},
		tabIndex: r ? -1 : 0,
		disabled: r,
		type: "button",
		children: [
			U("input", Sw({}, c())),
			U(ww, {
				name: n,
				disabled: r
			}),
			r ? U(yw, { children: i }) : W(H, { children: [U(Ew, { children: t && U("span", { children: t }) }), U(vw, { children: "Open from file" })] })
		]
	}));
}, kw = {
	PASTE: "open-window-paste-icon",
	FILE: "open-window-upload-icon",
	IMAGE: "image-frame"
}, Aw = z("div", { target: "e1035cyz1" })({
	name: "h9hj7s",
	styles: "display:flex;flex-direction:row;justify-content:space-between;align-items:flex-start;margin-bottom:20px;&>*{margin-right:18px;}& :last-child{margin-right:0;}"
}), jw = z("div", { target: "e1035cyz0" })("width:128px;height:134px;box-shadow:0 4px 12px rgba(103, 104, 132, 0.18);padding:16px;border-radius:12px;flex:1;display:flex;flex-direction:column;justify-content:space-between;align-items:center;box-sizing:border-box;position:relative;cursor:pointer;&>p{margin-top:6px;text-align:center;}svg{fill:", function(e) {
	return e.theme.ketcher.color.button.primary.active;
}, ";}"), Mw = function(e) {
	var t = e.selectClipboard, n = e.fileLoadHandler, r = e.errorHandler;
	return W(Aw, { children: [
		W(jw, {
			"data-testid": "paste-from-clipboard-button",
			onClick: t,
			children: [U(P, { name: kw.PASTE }), U(vw, { children: "Paste from clipboard" })]
		}),
		U(jw, {
			"data-testid": "open-from-file-button",
			children: U(Ow, {
				onDropAccepted: n,
				onDropRejected: function(e) {
					return r(`Unable to accept file(s). ${e}`);
				},
				buttonLabel: "Open from file",
				textLabel: "or drag file here",
				iconName: kw.FILE
			})
		}),
		U(jw, {
			"data-testid": "open-from-image-button",
			children: U(Ow, {
				accept: "image/*",
				onDropAccepted: n,
				onDropRejected: function(e) {
					return r(`Unable to accept file(s). ${e}`);
				},
				buttonLabel: "Open from image",
				textLabel: "or drag file here",
				iconName: kw.IMAGE,
				disabled: !0,
				disabledText: "Image Recognition service is not available"
			})
		})
	] });
}, Nw = z("textarea", { target: "e1q335jk0" })("min-width:430px;padding:12px;width:100%;height:100%;overflow:auto;white-space:pre-wrap;resize:none;box-sizing:border-box;outline:transparent;border:none;color:", function(e) {
	return e.theme.ketcher.color.input.text.active;
}, ";font-size:", function(e) {
	return e.theme.ketcher.font.size.regular;
}, ";background-color:", function(e) {
	var t = e.theme;
	return e.readOnly ? t.ketcher.color.input.background.disabled : t.ketcher.color.input.background.primary;
}, ";", function(e) {
	var t = e.theme;
	return aC(t);
}, ";"), Pw = function(e) {
	var t = e.value, n = e.inputHandler, r = e.readonly, i = r !== void 0 && r, a = e.selectOnInit, o = a !== void 0 && a, s = e.className, c = e.testId, l = (0, B.useRef)(null);
	return (0, B.useEffect)(function() {
		if (o) {
			var e;
			(e = l.current) == null || e.select();
		}
	}, [
		l,
		t,
		o
	]), U(Nw, {
		value: t,
		readOnly: i,
		onChange: n && function(e) {
			return n(e.target.value);
		},
		ref: l,
		className: s,
		"data-testid": c
	});
};
function Fw(e, t) {
	var n = Object.keys(e);
	if (Object.getOwnPropertySymbols) {
		var r = Object.getOwnPropertySymbols(e);
		t && (r = r.filter(function(t) {
			return Object.getOwnPropertyDescriptor(e, t).enumerable;
		})), n.push.apply(n, r);
	}
	return n;
}
function Iw(e) {
	for (var t = 1; t < arguments.length; t++) {
		var n = arguments[t] == null ? {} : arguments[t];
		t % 2 ? Fw(Object(n), !0).forEach(function(t) {
			I(e, t, n[t]);
		}) : Object.getOwnPropertyDescriptors ? Object.defineProperties(e, Object.getOwnPropertyDescriptors(n)) : Fw(Object(n)).forEach(function(t) {
			Object.defineProperty(e, t, Object.getOwnPropertyDescriptor(n, t));
		});
	}
	return e;
}
var Lw = z(Pw, { target: "e17hogtk0" })({
	name: "17fmpnb",
	styles: "width:100%;height:320px"
}), Rw = function(e) {
	if (e.isAnalyzingFile) return U(_w, { fileName: e.fileName });
	switch (e.currentState) {
		case e.states.openOptions: return U(Mw, Iw({}, e));
		case e.states.textEditor: return U(Lw, Iw({ testId: "open-structure-textarea" }, e));
		default: return null;
	}
};
function zw() {
	return new Promise(function(e, t) {
		global.FileReader ? e(Bw) : t(/* @__PURE__ */ Error("Your browser does not support opening files locally"));
	});
}
function Bw(e) {
	return new Promise(function(t, n) {
		var r = new FileReader();
		r.onload = function() {
			var n = r.result;
			e.msClose && e.msClose(), t(n);
		}, r.onerror = function(e) {
			n(/* @__PURE__ */ Error(`Failed to read file: ${e.type}`));
		}, r.readAsText(e, "UTF-8");
	});
}
var Vw = {
	openOptions: "openOptions",
	textEditor: "textEditor"
}, Hw = z("div", { target: "efvrr8x1" })("position:relative;padding:", function(e) {
	return e.currentState === Vw.openOptions ? "10px 12px" : "0";
}, ";");
z(xC, { target: "efvrr8x0" })({
	name: "1tx1l5v",
	styles: "margin-right:auto"
}), z(P, { target: "e23iben1" })({
	name: "1ux2zfx",
	styles: "fill:#343434"
});
var Uw = z(P, { target: "e23iben0" })({
	name: "wpnrak",
	styles: "user-select:none;width:16px;height:1em;display:inline-block;flex-shrink:0;transition:fill 200ms cubic-bezier(0.4, 0, 0.2, 1) 0ms;font-size:1.5rem;position:absolute;right:7px;top:calc(50% - 0.5em);pointer-events:none;fill:#5b6077"
}), Ww = function(e) {
	var t = e.className;
	return U(Uw, {
		name: "chevron",
		className: t
	});
};
function Gw(e, t) {
	var n = Object.keys(e);
	if (Object.getOwnPropertySymbols) {
		var r = Object.getOwnPropertySymbols(e);
		t && (r = r.filter(function(t) {
			return Object.getOwnPropertyDescriptor(e, t).enumerable;
		})), n.push.apply(n, r);
	}
	return n;
}
function Kw(e) {
	for (var t = 1; t < arguments.length; t++) {
		var n = arguments[t] == null ? {} : arguments[t];
		t % 2 ? Gw(Object(n), !0).forEach(function(t) {
			I(e, t, n[t]);
		}) : Object.getOwnPropertyDescriptors ? Object.defineProperties(e, Object.getOwnPropertyDescriptors(n)) : Gw(Object(n)).forEach(function(t) {
			Object.defineProperty(e, t, Object.getOwnPropertyDescriptor(n, t));
		});
	}
	return e;
}
var qw = z(Rn, { target: "e944g1i2" })({
	name: "1pt8ucq",
	styles: "width:100%;padding:0 8px;& label{font-size:12px;line-height:unset;}"
}), Jw = {
	name: "af34ib",
	styles: "background-color:white;border-bottom-left-radius:0;border-bottom-right-radius:0"
}, Yw = z(zt, { target: "e944g1i1" })("height:24px;border:1px solid #e1e5ea;border-radius:4px;font-size:12px;background-color:white;", function(e) {
	return e.open && Jw;
}, " & .MuiSelect-select{padding:0 24px 0 8px;height:100%;display:flex;align-items:center;}& span{", function(e) {
	return `font-size: ${e.theme.ketcher.font.size.regular}`;
}, ";}& .MuiOutlinedInput-notchedOutline{border:0;}"), Xw = {
	backgroundColor: "white",
	border: "1px solid #5B6077",
	borderTopWidth: "0",
	borderRadius: "0px 0px 2px 2px",
	boxShadow: "0 6px 10px rgba(103, 104, 132, 0.15)"
}, Zw = z(Ft, { target: "e944g1i0" })("display:flex;flex-direction:row;justify-content:space-between;padding:0 8px;height:28px;font-size:12px;&.MuiButtonBase-root:hover{border-left:2px solid #167782;}& .MuiTypography-root{", function(e) {
	return `font-size: ${e.theme.ketcher.font.size.regular}`;
}, ";}"), Qw = function(e) {
	var t = e.options, n = e.currentSelection, r = e.selectionHandler, i = e.className, a = e.label, o = e.testId, s = e.customStylesForExpanded, c = s === void 0 ? {} : s, l = e.disabled, u = l !== void 0 && l, d = (0, B.useState)(!1), f = R(d, 2), p = f[0], m = f[1], h = document.fullscreenElement ? document.querySelector("#root") : void 0;
	return W(qw, {
		className: i,
		children: [a && U("label", {
			htmlFor: "fileformat",
			children: "File format:"
		}), U(Yw, {
			value: n,
			onChange: function(e) {
				r(e.target.value);
			},
			open: p,
			onOpen: function(e) {
				e.type !== "keydown" && m(!0);
			},
			onClose: function() {
				m(!1);
			},
			renderValue: function(e) {
				var n = t.filter(function(t) {
					return t.id === e;
				})[0];
				return U("span", { children: n.label });
			},
			IconComponent: Ww,
			disabled: u,
			fullWidth: !0,
			"data-testid": o ?? "dropdown-select",
			MenuProps: {
				container: h,
				PaperProps: { style: Kw(Kw({}, Xw), c) },
				MenuListProps: { style: { padding: "0" } }
			},
			children: t.map(function(e) {
				return U(Zw, {
					value: e.id,
					"data-testid": `${e.label}-option`,
					children: U($r, { primary: e.label })
				}, e.id);
			})
		})]
	});
}, $w = z("form", { target: "el6v3ot5" })({
	name: "9pd72t",
	styles: "display:flex;flex-direction:column;height:300px"
}), eT = z("div", { target: "el6v3ot4" })({
	name: "1oj61nw",
	styles: "display:flex;justify-content:space-between;align-items:flex-end;margin-bottom:16px"
}), tT = z(Qw, { target: "el6v3ot3" })(function(e) {
	var t = e.theme;
	return {
		width: "230px",
		flexShrink: 0,
		"& .MuiOutlinedInput-root:hover:not(.Mui-disabled)": { border: `1px solid ${t.ketcher.color.input.border.hover}` },
		"& .MuiOutlinedInput-root": {
			border: `1px solid ${t.ketcher.color.input.border.regular}`,
			backgroundColor: t.ketcher.color.background.primary,
			color: t.ketcher.color.text.primary,
			fontFamily: t.ketcher.font.family.inter
		}
	};
}, ""), nT = { border: "none" }, rT = z("div", { target: "el6v3ot2" })({
	name: "kq43v2",
	styles: "position:absolute;top:0;left:0;width:100%;height:100%;display:flex;justify-content:center;align-items:center;background:#fff"
}), iT = z("div", { target: "el6v3ot1" })(function(e) {
	return {
		height: "100%",
		position: "relative",
		border: `1px solid ${e.theme.ketcher.color.input.border.regular}`,
		"& svg": {
			width: "100%",
			height: "100%",
			"& .drawn-structures": { "& .monomer": { lineHeight: "initial !important" } }
		}
	};
}, ""), aT = z("div", { target: "el6v3ot0" })(function(e) {
	var t = e.theme;
	return {
		display: "flex",
		flexGrow: 1,
		position: "relative",
		"& button": {
			opacity: 0,
			position: "absolute",
			right: "12px",
			top: "12px",
			borderRadius: "4px",
			padding: "2px",
			width: "28px",
			height: "28px",
			"&:not(:active)": {
				backgroundColor: t.ketcher.color.background.primary,
				color: t.ketcher.color.text.primary
			}
		},
		"&:hover button": { opacity: 1 },
		"&:focus-within button": { opacity: 0 },
		"&:focus-within button:hover": { opacity: 1 }
	};
}, ""), oT = z(Q, { target: "e1oaegu38" })(function(e) {
	var t = e.modalWidth;
	return `
    .MuiPaper-root {
      width: ${t};
      max-width: ${t};
    }`;
}, ""), sT = z("div", { target: "e1oaegu37" })({
	name: "kj5rtd",
	styles: "width:100%;display:flex;flex-direction:row;justify-content:space-between;align-items:center"
}), cT = z("div", { target: "e1oaegu36" })({
	name: "rpuipy",
	styles: "display:flex;height:24px;font-size:12px"
}), lT = z(tT, { target: "e1oaegu35" })({
	name: "7nflbq",
	styles: "padding:0;font-size:12px;& .MuiSelect-select{display:flex;align-items:center;padding:0 20px 0 8px;padding-right:20px !important;height:100%;}& span{font-size:12px;}"
}), uT = z(lT, { target: "e1oaegu34" })(function() {
	return { width: "140px" };
}, ""), dT = z(lT, { target: "e1oaegu33" })({
	name: "16zm0c",
	styles: "width:76px;margin-left:8px"
}), fT = z(lT, { target: "e1oaegu32" })({
	name: "l4tg7k",
	styles: "width:105px;margin-left:8px"
}), pT = z("div", { target: "e1oaegu31" })({
	name: "oq6u0f",
	styles: "display:flex;gap:10px"
}), mT = z(xC, { target: "e1oaegu30" })({
	name: "b9l38d",
	styles: "width:min-content"
}), hT = "ket", gT = "seq", _T = "rna", vT = "peptide", yT = "fasta", bT = "one-letter", xT = "three-letter", ST = [
	{
		id: "ket",
		label: "Ket Format"
	},
	{
		id: "mol",
		label: "MDL Molfile V3000"
	},
	{
		id: "seq",
		label: "Sequence"
	},
	{
		id: "fasta",
		label: "FASTA"
	},
	{
		id: "idt",
		label: "IDT"
	},
	{
		id: "axo-labs",
		label: "AxoLabs"
	},
	{
		id: "helm",
		label: "HELM"
	},
	{
		id: "biln",
		label: "BILN"
	}
], CT = [
	{
		id: _T,
		label: "RNA"
	},
	{
		id: "dna",
		label: "DNA"
	},
	{
		id: vT,
		label: "Peptide"
	}
], wT = [{
	id: bT,
	label: "1-letter code"
}, {
	id: xT,
	label: "3-letter code"
}], TT = qn, ET = function(e) {
	var t = kt.getNextChainPosition(), n = e.allEntities[0]?.[1].position;
	if (n) {
		var r = M.diff(t, new M(n));
		e.allEntities.forEach(function(t) {
			var n = R(t, 2)[1];
			e.moveDrawingEntityModelChange(n, r);
		});
	}
}, DT = function(e) {
	var t = e.ketSerializer, n = e.editor, r = e.struct, i = !n.drawingEntitiesManager.hasDrawingEntities, a = t.deserializeToDrawingEntities(r);
	if (!a) throw Error("Error during parsing file");
	var o = n.mode.modeName === "sequence-layout-mode", s = n.mode.modeName === "snake-layout-mode", c = n.mode.modeName === "flex-layout-mode";
	o && !i ? ET(a.drawingEntitiesManager) : a.drawingEntitiesManager.centerMacroStructure();
	var l = a.drawingEntitiesManager.mergeInto(n.drawingEntitiesManager).command, u = at.getInstance(n);
	c && l.merge(n.drawingEntitiesManager.recalculateAntisenseChains()), n.drawingEntitiesManager.detectBondsOverlappedByMonomers(), n.renderersContainer.update(l), u.update(l), o && (l.setUndoOperationReverse(), n.events.selectMode.dispatch({
		mode: ue.sequence,
		mergeWithLatestHistoryCommand: !0
	})), s && (l.setUndoOperationReverse(), n.events.selectMode.dispatch({
		mode: ue.snake,
		mergeWithLatestHistoryCommand: !0
	})), i && n.zoomToStructuresIfNeeded(), n.calculateAndStoreNextAutochainPosition(a.drawingEntitiesManager);
}, OT = function() {
	var e = dn(Ds.default.mark(function e(t) {
		var n, r, i, a, o, s, c, u, d, f, p, m, h, g, _, v, y, b;
		return Ds.default.wrap(function(e) {
			for (;;) switch (e.prev = e.next) {
				case 0:
					if (n = t.struct, r = t.formatSelection, i = t.additionalSelection, a = t.peptideLettersFormatSelection, o = t.onCloseCallback, s = t.setIsLoading, c = t.dispatch, u = r === hT, d = r === gT, f = r === yT, p = new l(), m = rn(), g = n, _ = function(e) {
						var t = "Convert error! " + e;
						c(rv({
							errorMessage: t,
							errorTitle: d || f ? "Unsupported symbols" : ""
						}));
					}, !u) {
						e.next = 13;
						break;
					}
					try {
						DT({
							struct: n,
							ketSerializer: p,
							editor: m
						}), o();
					} catch {
						_("Error during file parsing.");
					}
					return e.abrupt("return");
				case 13: f || d && a !== xT ? (h = TT[r][i], g = g.toUpperCase()) : h = d && a === xT ? TT.seq.peptide3Letter : TT[r];
				case 14: return v = ce.getIndigo(), e.prev = 15, s(!0), e.next = 19, v.convert({
					struct: g,
					output_format: ge.KET,
					input_format: h
				});
				case 19:
					y = e.sent, DT({
						struct: y.struct,
						ketSerializer: p,
						editor: m
					}), o(), e.next = 29;
					break;
				case 24: e.prev = 24, e.t0 = e.catch(15), b = Pe(e.t0).message, _(b), tt.error(e.t0);
				case 29: return e.prev = 29, s(!1), e.finish(29);
				case 32:
				case "end": return e.stop();
			}
		}, e, null, [[
			15,
			24,
			29,
			32
		]]);
	}));
	return function(t) {
		return e.apply(this, arguments);
	};
}(), kT = !1, AT = function(e) {}, jT = function(e) {
	var t = e.isModalOpen, n = e.onClose, r = X(), i = (0, B.useState)(""), a = R(i, 2), o = a[0], s = a[1], c = (0, B.useState)(""), l = R(c, 2), u = l[0], d = l[1], f = (0, B.useState)(!1), p = R(f, 2), m = p[0], h = p[1], g = (0, B.useState)(), _ = R(g, 2), v = _[0], y = _[1], b = (0, B.useState)(Vw.openOptions), x = R(b, 2), S = x[0], C = x[1], w = (0, B.useState)(hT), T = R(w, 2), E = T[0], D = T[1], O = (0, B.useState)(_T), k = R(O, 2), A = k[0], j = k[1], ee = (0, B.useState)(bT), te = R(ee, 2), M = te[0], ne = te[1];
	(0, B.useEffect)(function() {
		var e = u?.split("."), t = e[e.length - 1];
		if (t) {
			var n = ST.find(function(e) {
				return e.id === t;
			});
			D(n != null && n.id ? n.id : gT);
		}
	}, [u]), (0, B.useEffect)(function() {
		zw().then(function(e) {
			y({ chosenOpener: e });
		});
	}, []);
	var re = (0, B.useCallback)(function() {
		C(Vw.openOptions), s(""), D(hT), j(_T), n();
	}, [n]), N = function(e) {
		var t = window;
		if (t.isKetcherFullscreenBeforeFilePicker) {
			var n, r;
			(n = (r = document.documentElement).requestFullscreen) == null || n.call(r).catch(function() {}), t.isKetcherFullscreenBeforeFilePicker = !1;
		}
		d(e[0].name), v?.chosenOpener(e[0]).then(function(e) {
			s(e), C(Vw.textEditor);
		}, function() {});
	}, ie = function() {
		OT({
			struct: o,
			formatSelection: E,
			additionalSelection: A,
			peptideLettersFormatSelection: M,
			onCloseCallback: re,
			setIsLoading: h,
			dispatch: r
		});
	}, ae = function() {
		var e = rn(), t = at.getInstance(e), n = e.drawingEntitiesManager.deleteAllEntities();
		t.update(n), e.renderersContainer.update(n), e.zoomToStructuresIfNeeded(), OT({
			struct: o,
			formatSelection: E,
			additionalSelection: A,
			peptideLettersFormatSelection: M,
			onCloseCallback: re,
			setIsLoading: h,
			dispatch: r
		});
	};
	return W(oT, {
		isOpen: t,
		title: "Open Structure",
		onClose: re,
		modalWidth: S === Vw.textEditor ? "620px" : "",
		testId: "openStructureModal",
		children: [U(Q.Content, { children: W(Hw, {
			currentState: S,
			children: [U(Rw, {
				isAnalyzingFile: kT,
				fileName: u,
				currentState: S,
				states: Vw,
				selectClipboard: function() {
					return C(Vw.textEditor);
				},
				fileLoadHandler: N,
				errorHandler: AT,
				value: o,
				inputHandler: s
			}), m && U(rT, { children: U(pw, {}) })]
		}) }), S === Vw.textEditor ? U(Q.Footer, {
			withborder: "true",
			children: function() {
				return W(sT, { children: [W(cT, { children: [
					U(uT, {
						options: ST,
						currentSelection: E,
						selectionHandler: D,
						customStylesForExpanded: nT
					}, E),
					E === gT || E === yT ? U(dT, {
						options: CT,
						currentSelection: A,
						selectionHandler: j,
						customStylesForExpanded: nT,
						testId: "dropdown-select-type"
					}, A) : null,
					E === gT && A === vT ? U(fT, {
						options: wT,
						currentSelection: M,
						selectionHandler: ne,
						testId: "dropdown-select-peptide-letters-format"
					}) : null
				] }), W(pT, { children: [U(mT, {
					disabled: !o.trim(),
					clickHandler: ae,
					label: "Open as New",
					styleType: "secondary",
					"data-testid": "open-as-new-button"
				}, "openButton"), U(mT, {
					disabled: !o.trim(),
					clickHandler: ie,
					label: "Add to Canvas",
					title: "Structure will be loaded as fragment and added to Clipboard",
					"data-testid": "add-to-canvas-button"
				}, "copyButton")] })] });
			}()
		}) : U(H, {})]
	});
}, MT = [
	"value",
	"id",
	"onChange",
	"label",
	"type",
	"className",
	"inputClassName"
];
function NT(e, t) {
	var n = Object.keys(e);
	if (Object.getOwnPropertySymbols) {
		var r = Object.getOwnPropertySymbols(e);
		t && (r = r.filter(function(t) {
			return Object.getOwnPropertyDescriptor(e, t).enumerable;
		})), n.push.apply(n, r);
	}
	return n;
}
function PT(e) {
	for (var t = 1; t < arguments.length; t++) {
		var n = arguments[t] == null ? {} : arguments[t];
		t % 2 ? NT(Object(n), !0).forEach(function(t) {
			I(e, t, n[t]);
		}) : Object.getOwnPropertyDescriptors ? Object.defineProperties(e, Object.getOwnPropertyDescriptors(n)) : NT(Object(n)).forEach(function(t) {
			Object.defineProperty(e, t, Object.getOwnPropertyDescriptor(n, t));
		});
	}
	return e;
}
var FT = z("label", { target: "e10m4n7r1" })(function(e) {
	return {
		display: "flex",
		flexDirection: "column",
		marginRight: "8px",
		color: e.theme.ketcher.color.text.primary,
		fontSize: "12px"
	};
}, ""), IT = z("input", { target: "e10m4n7r0" })(function(e) {
	var t = e.theme;
	return {
		height: "24px",
		padding: "3px 7px",
		border: `1px solid ${t.ketcher.color.input.border.regular}`,
		fontSize: "14px",
		borderRadius: "4px",
		backgroundColor: t.ketcher.color.input.background.primary,
		color: t.ketcher.color.text.primary,
		outline: "transparent",
		width: "164px",
		letterSpacing: "normal",
		"&:active, &:focus": { color: t.ketcher.color.input.text.active },
		"&:hover": { border: `1px solid ${t.ketcher.color.input.border.hover}` }
	};
}, ""), LT = function(e) {
	var t = e.value, n = e.id, r = e.onChange, i = e.label, a = e.type, o = e.className, s = e.inputClassName, c = ve(e, MT);
	return W(FT, {
		htmlFor: n,
		className: o,
		children: [i && U("span", { children: i }), U(IT, PT({
			type: a || "text",
			id: n,
			value: t,
			className: s,
			onChange: function(e) {
				r(e.target.value);
			}
		}, c))]
	});
}, RT;
(function(e) {
	e.Ket = "chemical/x-ket", e.Mol = "chemical/x-mdl-molfile", e.HELM = "chemincal/x-helm", e.Fasta = "chemical/x-fasta", e.Sequence = "chemical/x-sequence", e.Idt = "chemical/x-idt", e.AxoLabs = "chemical/x-axo-labs", e.Svg = "image/svg+xml", e.BILN = "chemical/x-biln";
})(RT ||= {});
var zT = Sn(function e(t, n, r, i, a) {
	Wt(this, e), I(this, "name", void 0), I(this, "mime", void 0), I(this, "extensions", void 0), I(this, "supportsCoords", void 0), I(this, "options", void 0), this.name = t, this.mime = n, this.extensions = r, this.supportsCoords = i ?? !1, this.options = a ?? {};
}), BT = {
	ket: new zT("Ket file", RT.Ket, [".ket"], !0, {}),
	mol: new zT("MDL Molfile V3000", RT.Mol, [".mol"], !0, { "molfile-saving-mode": "3000" }),
	fasta: new zT("FASTA", RT.Fasta, [".fasta"], !1, {}),
	sequence: new zT("SEQUENCE", RT.Sequence, [".seq"], !1, {}),
	"sequence-3-letter": new zT("SEQUENCE (3-letter code)", RT.Sequence, [".seq"], !1, {}),
	idt: new zT("IDT", RT.Idt, [".idt"], !1, {}),
	"axo-labs": new zT("AxoLabs", RT.AxoLabs, [".axolabs"], !1, {}),
	helm: new zT("HELM", RT.HELM, [".helm"]),
	biln: new zT("BILN", RT.BILN, [".biln"]),
	svg: new zT("SVG Document", RT.Svg, [".svg"])
}, VT = function(e) {
	return BT[e];
}, HT = [
	{
		id: "ket",
		label: "Ket Format"
	},
	{
		id: "mol",
		label: "MDL Molfile V3000"
	},
	{
		id: "sequence",
		label: "Sequence (1-letter code)"
	},
	{
		id: "sequence-3-letter",
		label: "Sequence (3-letter code)"
	},
	{
		id: "fasta",
		label: "FASTA"
	},
	{
		id: "idt",
		label: "IDT"
	},
	{
		id: "axo-labs",
		label: "AxoLabs"
	},
	{
		id: "svg",
		label: "SVG Document"
	},
	{
		id: "helm",
		label: "HELM"
	},
	{
		id: "biln",
		label: "BILN"
	}
], UT = {
	mol: ge.Mol,
	fasta: ge.FASTA,
	sequence: ge.SEQUENCE,
	"sequence-3-letter": ge.PeptideSequenceThreeLetter,
	idt: ge.IDT,
	"axo-labs": ge.AXOLABS,
	helm: ge.HELM,
	biln: ge.BILN
}, WT = z(Q, { target: "e12csxs60" })({
	name: "krpfk5",
	styles: "& div.MuiPaper-root{background:white;min-height:400px;min-width:430px;}& .MuiDialogContent-root{overflow:hidden;height:100%;}"
}), GT = function(e) {
	var t = e.onClose, n = e.isModalOpen, r = X(), i = (0, B.useState)("ket"), a = R(i, 2), o = a[0], s = a[1], c = (0, B.useState)("ketcher"), u = R(c, 2), d = u[0], f = u[1], p = (0, B.useState)(""), m = R(p, 2), h = m[0], g = m[1], _ = (0, B.useState)(!1), v = R(_, 2), y = v[0], b = v[1], x = (0, B.useState)(), S = R(x, 2), C = S[0], w = S[1], T = ce.getIndigo(), E = rn(), D = function() {
		var e = dn(Ds.default.mark(function e(t) {
			var n, i, a, o, c, u, d, f, p, m;
			return Ds.default.wrap(function(e) {
				for (;;) switch (e.prev = e.next) {
					case 0:
						if (s(t), n = new l(), i = n.serialize(E.drawingEntitiesManager.micromoleculesHiddenEntities.clone(), E.drawingEntitiesManager), w(void 0), t !== "ket") {
							e.next = 7;
							break;
						}
						return g(i), e.abrupt("return");
					case 7:
						if (t !== "svg") {
							e.next = 14;
							break;
						}
						return a = E.ketcherRootElementBoundingClientRect, o = a?.x || 0, c = a?.y || 0, u = ye(E.canvas, "preview", {
							horizontal: o,
							vertical: c
						}), w(u), e.abrupt("return");
					case 14:
						if (t === "helm" && (E.drawingEntitiesManager.molecules.length > 0 && E.events.error.dispatch("The molecule will be exported using inline SMILES, and on load will appear as a CHEM monomer"), De(Array.from(E.drawingEntitiesManager.monomers.values()), E.monomersLibrary) || E.events.error.dispatch("Some of the monomers do not have aliases in the HELM Core Library - they are exported using Ketcher aliases.")), e.prev = 15, b(!0), t !== "fasta" && t !== "sequence" && t !== "idt" || (d = E.drawingEntitiesManager.validateIfApplicableForFasta(), d)) {
							e.next = 21;
							break;
						}
						throw Error("Error during sequence type recognition(RNA, DNA or Peptide)");
					case 21: return e.next = 23, T.convert({
						struct: i,
						output_format: UT[t]
					});
					case 23:
						f = e.sent, g(f.struct), e.next = 34;
						break;
					case 27: e.prev = 27, e.t0 = e.catch(15), p = e.t0 instanceof Error ? e.t0.message : typeof e.t0 == "string" ? e.t0 : JSON.stringify(e.t0), m = "Convert error! " + p, r(rv(m)), tt.error(m), s("ket");
					case 34: return e.prev = 34, b(!1), e.finish(34);
					case 37:
					case "end": return e.stop();
				}
			}, e, null, [[
				15,
				27,
				34,
				37
			]]);
		}));
		return function(t) {
			return e.apply(this, arguments);
		};
	}(), O = function(e) {
		f(e);
	}, k = function() {
		var e;
		if (o === "svg") {
			var n = E.ketcherRootElementBoundingClientRect, r = n?.x || 0, i = n?.y || 0, a = ye(E.canvas, "file", {
				horizontal: r,
				vertical: i
			});
			if (!a) {
				t();
				return;
			}
			e = a;
		} else e = h;
		var s = new Blob([e], { type: VT(o).mime }), c = VT(o);
		(0, Os.saveAs)(s, `${d}${c.extensions[0]}`), t();
	};
	return (0, B.useEffect)(function() {
		o === "ket" && g(new l().serialize(E.drawingEntitiesManager.micromoleculesHiddenEntities.clone(), E.drawingEntitiesManager));
	}, [o]), W(WT, {
		title: "save structure",
		isOpen: n,
		onClose: t,
		testId: "save-structure-dialog",
		children: [U(Q.Content, { children: W($w, {
			onSubmit: k,
			id: "save",
			children: [W(eT, {
				style: { padding: "12px 12px 10px" },
				children: [U("div", { children: U(LT, {
					value: d,
					id: "filename",
					onChange: O,
					label: "File name:",
					"data-testid": "filename-input"
				}) }), U(tT, {
					label: "File format:",
					options: HT,
					currentSelection: o,
					selectionHandler: D,
					customStylesForExpanded: nT,
					testId: "file-format-list"
				})]
			}), C ? U(iT, {
				dangerouslySetInnerHTML: { __html: C },
				"data-testid": "preview-area"
			}) : W(aT, { children: [
				U(Pw, {
					testId: "preview-area",
					value: h,
					readonly: !0
				}),
				U(oe, {
					onClick: function(e) {
						e.preventDefault();
						try {
							ne() ? navigator.clipboard.writeText(h) : _e(e.clipboardData, { "text/plain": h });
						} catch (e) {
							tt.error("copyAs.js::copyAs", e), r(rv("This feature is not available in your browser"));
						}
					},
					iconName: "copy",
					title: "Copy to clipboard",
					testId: "copy-to-clipboard"
				}),
				y && U(rT, { children: U(pw, {}) })
			] })]
		}) }), W(Q.Footer, { children: [U(xC, {
			label: "Cancel",
			styleType: "secondary",
			clickHandler: t,
			"data-testid": "cancel-button"
		}), U(xC, {
			label: "Save",
			clickHandler: k,
			disabled: !d,
			"data-testid": "save-button"
		})] })]
	});
}, KT = z(xC, { target: "e1kgbmg80" })(function() {
	return { width: "72px" };
}, ""), qT = z("div", { target: "e11sfr0q0" })({
	name: "606i4c",
	styles: "padding:12px"
}), JT = function(e) {
	var t = e.isModalOpen, n = e.onClose, r = X(), i = Z(Xy), a = Z(K), o = (0, B.useCallback)(function() {
		n();
	}, [n]);
	return W(Q, {
		isOpen: t,
		title: "Delete RNA Preset",
		onClose: o,
		"data-testid": "delete-preset-modal",
		children: [U(Q.Content, { children: W(qT, {
			"data-testid": "delete-preset-popup-content",
			children: [
				U("div", { children: "You are about to delete" }),
				W("div", { children: [
					"\"",
					i.name,
					"\" RNA preset."
				] }),
				U("div", { children: "This operation cannot be undone." })
			]
		}) }), W(Q.Footer, { children: [U(KT, {
			clickHandler: function() {
				o();
			},
			label: "Cancel",
			styleType: "secondary",
			"data-testid": "cancel-delete-preset-button"
		}, "cancel"), U(KT, {
			clickHandler: function() {
				o(), r(db(i)), r(pb(!1)), r(fb()), a?.events.selectPreset.dispatch(null);
			},
			label: "Delete",
			"data-testid": "delete-preset-button"
		}, "delete")] })]
	});
}, YT = z("div", { target: "e1wvbgsi0" })({
	name: "606i4c",
	styles: "padding:12px"
}), XT = function(e) {
	var t = e.isModalOpen, n = e.onClose, r = X(), i = Z(Ry), a = Z(K), o = YS(i), s = (0, B.useCallback)(function() {
		n();
	}, [n]), c = function() {
		JS(r, a);
	};
	return W(Q, {
		isOpen: t,
		title: "Update sequence",
		onClose: s,
		"data-testid": "update-sequence-modal",
		children: [U(Q.Content, {
			"data-testid": "update-sequence-modal-body",
			children: W(YT, { children: [
				"You are going to modify ",
				o,
				" nucleotides. Are you sure?"
			] })
		}), W(Q.Footer, { children: [U(xC, {
			clickHandler: function() {
				s();
			},
			label: "Cancel",
			styleType: "secondary",
			title: "",
			"data-testid": "update-sequence-cancel-button"
		}, "cancel"), U(xC, {
			clickHandler: function() {
				s(), a?.events.modifySequenceInRnaBuilder.dispatch(i), c();
			},
			label: "Yes",
			title: "",
			"data-testid": "update-sequence-yes-button"
		}, "update")] })]
	});
}, ZT = z("div", { target: "e1tvvbc92" })(function() {
	return {
		display: "flex",
		flexDirection: "column",
		rowGap: "2px",
		alignItems: "center",
		marginBottom: "5px"
	};
}, ""), QT = z("span", { target: "e1tvvbc91" })(function(e) {
	return {
		margin: 0,
		padding: 0,
		textAlign: "center",
		display: "block",
		font: e.theme.ketcher.font.family.inter,
		fontSize: e.theme.ketcher.font.size.small,
		fontWeight: e.theme.ketcher.font.weight.regular,
		color: e.disabled ? "rgba(180, 185, 214, 1)" : e.theme.ketcher.color.text.light
	};
}, ""), $T = z("div", { target: "e1tvvbc90" })(function() {
	return { height: "100%" };
}, ""), eE = function(e) {
	return e === "O" ? "OH" : e;
}, tE = z(Ve, { target: "e1huhxto2" })(function(e) {
	var t = e.theme, n = e.isExpanded;
	return {
		display: "flex",
		border: `1.5px solid ${t.ketcher.outline.color}`,
		borderRadius: "6px",
		padding: 5,
		maxHeight: "100%",
		minHeight: "150px",
		height: n ? "auto" : "150px",
		width: n ? "auto" : "150px",
		alignSelf: "stretch",
		"& svg": {
			maxWidth: "fit-content",
			margin: "auto"
		}
	};
}, ""), nE = z("div", { target: "e1huhxto1" })({
	name: "wfzm1y",
	styles: "display:flex;flex-wrap:wrap;justify-content:center;align-self:flex-start;width:100%;gap:7px"
}), rE = z("div", { target: "e1huhxto0" })(function(e) {
	var t = e.isExpanded;
	return {
		minHeight: "150px",
		height: t ? "auto" : "150px",
		width: t ? "auto" : "150px",
		alignSelf: "stretch"
	};
}, ""), iE = z("div", { target: "e8i5wzj0" })({
	name: "2oefzz",
	styles: "display:flex;flex-direction:column;justify-content:center;align-items:center;gap:8px;padding:8px;color:#7c7c7f;border:1px solid #cad3dd;width:100%;height:100%"
}), aE = function(e) {
	var t = e.testId;
	return W(iE, {
		"data-testid": t,
		children: [U(P, { name: "questionMark" }), "Unknown structure"]
	});
}, oE = z("div", { target: "e1q9gayd0" })(function(e) {
	var t = e.theme, n = e.expanded;
	return {
		display: "flex",
		border: `1.5px solid ${t.ketcher.outline.color}`,
		borderRadius: "6px",
		padding: 5,
		maxHeight: "100%",
		minHeight: "150px",
		height: n ? "auto" : "150px",
		width: n ? "auto" : "150px",
		alignSelf: "stretch",
		"& svg": {
			maxWidth: "fit-content",
			margin: "auto"
		}
	};
}, ""), sE = function(e) {
	var t = e.monomer, n = e.expanded, r = e.selectedAttachmentPoint, i = e.connectedAttachmentPoints, a = e.usage, o = e.testId, s = (0, B.useRef)(null);
	return (0, B.useLayoutEffect)(function() {
		var e = s.current;
		if (e) {
			var n = Jd(e);
			if (t instanceof mn) {
				var o = (e.width.baseVal.value - e.x.baseVal.value) / 2, c = (e.height.baseVal.value - e.y.baseVal.value) / 2, l = new M(o, c), u = N.canvasToModel(l), d = new mn(t.variantMonomerItem, u);
				new Dn(d).showExternal({
					canvas: n,
					usage: a,
					selectedAttachmentPoint: r,
					connectedAttachmentPoints: i
				});
			}
		}
	}, [r, i]), U(oE, {
		expanded: n,
		"data-testid": o,
		children: U("svg", { ref: s })
	});
}, cE = function(e) {
	var t = e.monomer, n = e.attachmentPoints, r = e.connectedAttachmentPoints, i = e.selectedAttachmentPoint, a = e.usage, o = e.needCache, s = e.update, c = e.expanded, l = e.testId, u = t instanceof mn, d = t.monomerItem.props.unresolved;
	return W(H, { children: [u ? U(sE, {
		monomer: t,
		expanded: c,
		selectedAttachmentPoint: i,
		connectedAttachmentPoints: r,
		usage: a,
		testId: l
	}) : d ? U(rE, {
		isExpanded: c,
		children: U(aE, { testId: l })
	}) : U(tE, {
		struct: t.monomerItem.struct,
		options: {
			connectedMonomerAttachmentPoints: r,
			currentlySelectedMonomerAttachmentPoint: i ?? void 0,
			usageInMacromolecule: a,
			labelInMonomerConnectionsModal: !0,
			needCache: o ?? !1
		},
		update: s,
		isExpanded: c,
		testId: l
	}), U(nE, { children: U(H, { children: n }) })] });
}, lE = z("div", { target: "e14t14ao2" })(function(e) {
	var t = e.theme, n = e.isExpanded;
	return {
		margin: 0,
		padding: 0,
		textAlign: "center",
		alignSelf: "flex-end",
		display: "block",
		font: t.ketcher.font.family.inter,
		fontSize: t.ketcher.font.size.regular,
		fontWeight: t.ketcher.font.weight.regular,
		flexBasis: "200px",
		lineHeight: "14px",
		maxWidth: n ? void 0 : "150px"
	};
}, ""), uE = z("div", { target: "e14t14ao1" })(function(e) {
	var t = e.theme;
	return {
		width: 10,
		height: 2,
		display: "block",
		color: t.ketcher.color.button.secondary.hover,
		backgroundColor: t.ketcher.color.button.secondary.hover,
		borderRadius: 20,
		margin: "auto"
	};
}, ""), dE = z("div", { target: "e14t14ao0" })(function() {
	return {
		display: "grid",
		gridAutoFlow: "column",
		gridTemplateRows: "auto auto auto",
		gridTemplateColumns: "1fr 10px 1fr",
		justifyContent: "center",
		alignItems: "flex-start",
		padding: "12px",
		paddingBottom: 0,
		height: "100%",
		columnGap: "12px",
		rowGap: "8px"
	};
}, ""), fE = "thymine", pE = "uracil", mE = function(e) {
	var t = e.monomerClass, n = e.variantMonomerItem, r = n.label, i = n.options ?? [];
	if (t === st.Base) {
		var a = i.some(function(e) {
			return e.templateId.toLowerCase().includes(fE);
		}), o = i.some(function(e) {
			return e.templateId.toLowerCase().includes(pE);
		});
		return a ? r === "N" ? "Any DNA base" : "Ambiguous DNA Base" : o ? r === "N" ? "Any RNA Base" : "Ambiguous RNA Base" : "Ambiguous Base";
	}
	return t === st.AminoAcid ? r === "X" ? "Any Amino acid" : "Ambiguous Amino acid" : `Ambiguous ${t}`;
}, hE = function(e) {
	return e instanceof mn ? mE(e) : e.monomerItem.props.Name;
}, gE = function(e) {
	var t = e.firstMonomer, n = e.secondMonomer, r = e.expanded, i = e.firstMonomerOverview, a = e.secondMonomerOverview, o = hE(t), s = hE(n);
	return U(dE, { children: W(H, { children: [
		U(lE, {
			isExpanded: r,
			children: o
		}),
		i,
		U("span", {}),
		U(uE, {}),
		U("span", {}),
		U(lE, {
			isExpanded: r,
			children: s
		}),
		a
	] }) });
};
function _E(e, t) {
	var n = Object.keys(e);
	if (Object.getOwnPropertySymbols) {
		var r = Object.getOwnPropertySymbols(e);
		t && (r = r.filter(function(t) {
			return Object.getOwnPropertyDescriptor(e, t).enumerable;
		})), n.push.apply(n, r);
	}
	return n;
}
function vE(e) {
	for (var t = 1; t < arguments.length; t++) {
		var n = arguments[t] == null ? {} : arguments[t];
		t % 2 ? _E(Object(n), !0).forEach(function(t) {
			I(e, t, n[t]);
		}) : Object.getOwnPropertyDescriptors ? Object.defineProperties(e, Object.getOwnPropertyDescriptors(n)) : _E(Object(n)).forEach(function(t) {
			Object.defineProperty(e, t, Object.getOwnPropertyDescriptor(n, t));
		});
	}
	return e;
}
var yE = z(Q, { target: "e1byht5d3" })({
	name: "1j7jcep",
	styles: "& .MuiPaper-root{background:#fff !important;}& .MuiDialogContent-root{overflow:hidden;}"
}), bE = z(xC, { target: "e1byht5d2" })(function() {
	return { width: "97px !important" };
}, ""), xE = z(xC, { target: "e1byht5d1" })(function(e) {
	return {
		width: "97px !important",
		color: e.disabled ? "rgba(51, 51, 51, 0.6)" : "",
		background: e.disabled ? "rgba(225, 229, 234, 1) !important" : "",
		opacity: "1 !important",
		minHeight: "0"
	};
}, ""), SE = z(xC, { target: "e1byht5d0" })(function(e) {
	return {
		borderRadius: 5,
		minWidth: "45px !important",
		padding: "4px",
		border: `1px solid ${e.theme.ketcher.color.border.secondary}`,
		color: e.disabled ? "rgba(51, 51, 51, 0.6) !important" : "",
		background: e.disabled ? "rgba(225, 229, 234)" : "",
		borderColor: e.disabled ? "rgba(225, 229, 234) !important" : ""
	};
}, ""), CE = function(e) {
	var t = e.onClose, n = e.isModalOpen, r = e.firstMonomer, i = e.secondMonomer, a = e.polymerBond, o = e.isReconnectionDialog, s = Z(K), c = (0, B.useRef)(a?.firstMonomerAttachmentPoint), l = (0, B.useRef)(a?.secondMonomerAttachmentPoint), u = (0, B.useRef)(r?.hasFreeAttachmentPoint || i?.hasFreeAttachmentPoint);
	if (!r || !i) throw Error("Monomers must exist!");
	var d = (0, B.useState)(c.current || TE(r)), f = R(d, 2), p = f[0], m = f[1], h = (0, B.useState)(l.current || TE(i)), g = R(h, 2), _ = g[0], v = g[1], y = (0, B.useState)(!1), b = R(y, 2), x = b[0], S = b[1], C = function() {
		if (o) {
			var e;
			a?.firstMonomer.setBond(c.current, a), a == null || (e = a.secondMonomer) == null || e.setBond(l.current, a), t();
		} else s?.events.cancelBondCreationViaModal.dispatch(i), t();
	};
	return W(yE, {
		title: o ? "Edit Attachment Points" : "Select Attachment Points",
		isOpen: n,
		onClose: C,
		showExpandButton: !0,
		modalWidth: "358px",
		expanded: x,
		setExpanded: S,
		testId: "monomer-connection-modal",
		children: [U(Q.Content, { children: U($T, { children: U(gE, {
			firstMonomer: r,
			secondMonomer: i,
			expanded: x,
			firstMonomerOverview: U(wE, {
				monomer: r,
				selectedAttachmentPoint: p,
				onSelectAttachmentPoint: m,
				expanded: x,
				position: "left"
			}),
			secondMonomerOverview: U(wE, {
				monomer: i,
				selectedAttachmentPoint: _,
				onSelectAttachmentPoint: v,
				expanded: x,
				position: "right"
			})
		}) }) }), W(Q.Footer, { children: [U(bE, {
			label: "Cancel",
			"data-testid": "cancel-button",
			styleType: "secondary",
			clickHandler: C
		}), U(xE, {
			label: o ? "Reconnect" : "Connect",
			"data-testid": o ? "Reconnect-button" : "Connect-button",
			disabled: !p || !_ || !u.current,
			clickHandler: function() {
				if (!p || !_) throw Error("Attachment points cannot be falsy");
				p === c.current && _ === l.current ? C() : (s?.events.createBondViaModal.dispatch({
					firstMonomer: r,
					secondMonomer: i,
					firstSelectedAttachmentPoint: p,
					secondSelectedAttachmentPoint: _,
					polymerBond: a,
					isReconnection: o,
					initialFirstMonomerAttachmentPoint: c.current,
					initialSecondMonomerAttachmentPoint: l.current
				}), t());
			}
		})] })]
	});
};
function wE(e) {
	var t = e.monomer, n = e.selectedAttachmentPoint, r = e.onSelectAttachmentPoint, i = e.expanded, a = i !== void 0 && i, o = e.position, s = (0, B.useState)(t.attachmentPointsToBonds), c = R(s, 2), l = c[0], u = c[1], d = (0, B.useState)(function() {
		return _x(l);
	}), f = R(d, 2), p = f[0], m = f[1];
	(0, B.useEffect)(function() {
		u(t.attachmentPointsToBonds);
	}, [n]), (0, B.useEffect)(function() {
		m(_x(l));
	}, [l]);
	var h = function(e) {
		var n = t.monomerCaps, r = t instanceof mn;
		if (!n) return r ? null : "H";
		var i = n[e];
		return i ? eE(i) : null;
	}, g = function(e) {
		var i = vE({}, t.attachmentPointsToBonds), a = n ? i[n] : null;
		n && a && t.removeBond(a), i[e] = t.getPotentialBond(e), u(i), r(e), m(_x(i));
	};
	return U(cE, {
		monomer: t,
		connectedAttachmentPoints: p,
		selectedAttachmentPoint: n,
		usage: sn.MonomerConnectionsModal,
		update: a,
		expanded: a,
		attachmentPoints: t.listOfAttachmentPoints.map(function(e) {
			var t = !!(p.includes(e) && e !== n);
			return W(ZT, { children: [U(SE, {
				label: e,
				styleType: e === n ? "primary" : "secondary",
				clickHandler: function() {
					return g(e);
				},
				disabled: t,
				"data-testid": `${o}-${e}`,
				"data-isactive": e === n
			}), U(QT, {
				"data-testid": "leaving-group-value",
				disabled: t,
				children: h(e)
			})] }, e);
		}),
		testId: `${o}-monomer-preview`
	});
}
function TE(e) {
	if (e.chosenFirstAttachmentPointForBond) return e.chosenFirstAttachmentPointForBond;
	if (e.chosenSecondAttachmentPointForBond) return e.chosenSecondAttachmentPointForBond;
	var t = Object.entries(e.attachmentPointsToBonds).filter(function(e) {
		var t = R(e, 2);
		return t[0], t[1] == null;
	});
	return t.length === 1 ? R(t[0], 1)[0] : null;
}
var EE = z("p", { target: "e1e4h5hm0" })({
	name: "1fayh9l",
	styles: "padding:12px;font-size:12px;color:#000"
}), DE = function(e) {
	var t = e.title, n = e.confirmationText, r = e.onConfirm, i = e.isModalOpen, a = e.onClose;
	return W(Q, {
		isOpen: i,
		title: t ?? "Confirm your action",
		onClose: a,
		testId: "confirmation-dialog",
		children: [U(Q.Content, { children: U(EE, {
			"data-testid": "confirmation-text",
			children: n
		}) }), W(Q.Footer, { children: [U(xC, {
			label: "Cancel",
			clickHandler: a,
			"data-testid": "cancel-button"
		}), U(xC, {
			label: "Yes",
			clickHandler: function() {
				r(), a();
			},
			styleType: "secondary",
			"data-testid": "yes-button"
		})] })]
	});
}, OE = [
	{
		id: "general",
		title: "General",
		fields: [
			"resetToSelect",
			"rotationStep",
			"showValenceWarnings",
			"atomColoring",
			"font",
			"fontsz",
			"fontszUnit",
			"fontszsub",
			"fontszsubUnit",
			"reactionComponentMarginSize",
			"reactionComponentMarginSizeUnit",
			"imageResolution"
		]
	},
	{
		id: "stereochemistry",
		title: "Stereochemistry",
		fields: [
			"showStereoFlags",
			"stereoLabelStyle",
			"colorOfAbsoluteCenters",
			"colorOfAndCenters",
			"colorOfOrCenters",
			"colorStereogenicCenters",
			"autoFadeOfStereoLabels",
			"absFlagLabel",
			"andFlagLabel",
			"orFlagLabel",
			"mixedFlagLabel",
			"ignoreChiralFlag"
		]
	},
	{
		id: "atoms",
		title: "Atoms",
		fields: [
			"carbonExplicitly",
			"showCharge",
			"showValence",
			"showHydrogenLabels"
		]
	},
	{
		id: "bonds",
		title: "Bonds",
		fields: [
			"aromaticCircle",
			"bondSpacing",
			"bondThickness",
			"bondThicknessUnit",
			"stereoBondWidth",
			"stereoBondWidthUnit",
			"hashSpacing",
			"hashSpacingUnit"
		]
	},
	{
		id: "server",
		title: "Server",
		fields: [
			"smart-layout",
			"ignore-stereochemistry-errors",
			"mass-skip-error-on-pseudoatoms",
			"gross-formula-add-rsites",
			"gross-formula-add-isotopes"
		]
	},
	{
		id: "viewer3d",
		title: "3D Viewer",
		fields: [
			"miewMode",
			"miewTheme",
			"miewAtomLabel"
		]
	},
	{
		id: "debug",
		title: "Options for Debugging",
		fields: [
			"showAtomIds",
			"showBondIds",
			"showHalfBondIds",
			"showLoopIds"
		]
	}
], kE = {
	resetToSelect: {
		label: "Reset to Select Tool",
		type: "select",
		options: [
			{
				value: !0,
				label: "Enabled"
			},
			{
				value: !1,
				label: "Disabled"
			},
			{
				value: "paste",
				label: "After Paste"
			}
		]
	},
	rotationStep: {
		label: "Rotation Step (degrees)",
		type: "number",
		min: 1,
		max: 90,
		step: 1
	},
	showValenceWarnings: {
		label: "Show Valence Warnings",
		type: "checkbox"
	},
	atomColoring: {
		label: "Atom Coloring",
		type: "checkbox"
	},
	font: {
		label: "Font",
		type: "select",
		options: [
			{
				value: "30px Arial",
				label: "Arial"
			},
			{
				value: "30px Arial Black",
				label: "Arial Black"
			},
			{
				value: "30px Comic Sans MS",
				label: "Comic Sans MS"
			},
			{
				value: "30px Courier New",
				label: "Courier New"
			},
			{
				value: "30px Georgia",
				label: "Georgia"
			},
			{
				value: "30px Impact",
				label: "Impact"
			},
			{
				value: "30px Charcoal",
				label: "Charcoal"
			},
			{
				value: "30px Lucida Console",
				label: "Lucida Console"
			},
			{
				value: "30px Monaco",
				label: "Monaco"
			},
			{
				value: "30px Palatino Linotype",
				label: "Palatino Linotype"
			},
			{
				value: "30px Book Antiqua",
				label: "Book Antiqua"
			},
			{
				value: "30px Palatino",
				label: "Palatino"
			},
			{
				value: "30px Tahoma",
				label: "Tahoma"
			},
			{
				value: "30px Geneva",
				label: "Geneva"
			},
			{
				value: "30px Times New Roman",
				label: "Times New Roman"
			},
			{
				value: "30px Times",
				label: "Times"
			},
			{
				value: "30px Verdana",
				label: "Verdana"
			},
			{
				value: "30px Symbol",
				label: "Symbol"
			},
			{
				value: "30px MS Serif",
				label: "MS Serif"
			},
			{
				value: "30px MS Sans Serif",
				label: "MS Sans Serif"
			},
			{
				value: "30px New York",
				label: "New York"
			},
			{
				value: "30px Droid Sans",
				label: "Droid Sans"
			},
			{
				value: "30px Droid Serif",
				label: "Droid Serif"
			},
			{
				value: "30px Droid Sans Mono",
				label: "Droid Sans Mono"
			},
			{
				value: "30px Roboto",
				label: "Roboto"
			}
		]
	},
	fontsz: {
		label: "Font Size",
		type: "number",
		min: 1,
		max: 96,
		step: 1
	},
	fontszUnit: {
		label: "Font Size Unit",
		type: "select",
		options: [
			{
				value: "px",
				label: "px"
			},
			{
				value: "pt",
				label: "pt"
			},
			{
				value: "cm",
				label: "cm"
			},
			{
				value: "inch",
				label: "inch"
			}
		]
	},
	fontszsub: {
		label: "Sub/Superscript Font Size",
		type: "number",
		min: 1,
		max: 96,
		step: 1
	},
	fontszsubUnit: {
		label: "Sub/Superscript Font Size Unit",
		type: "select",
		options: [
			{
				value: "px",
				label: "px"
			},
			{
				value: "pt",
				label: "pt"
			},
			{
				value: "cm",
				label: "cm"
			},
			{
				value: "inch",
				label: "inch"
			}
		]
	},
	reactionComponentMarginSize: {
		label: "Reaction Component Margin Size",
		type: "number",
		min: .1,
		max: 1e3,
		step: .1
	},
	reactionComponentMarginSizeUnit: {
		label: "Reaction Component Margin Size Unit",
		type: "select",
		options: [
			{
				value: "px",
				label: "px"
			},
			{
				value: "pt",
				label: "pt"
			},
			{
				value: "cm",
				label: "cm"
			},
			{
				value: "inch",
				label: "inch"
			}
		]
	},
	imageResolution: {
		label: "Image Resolution",
		type: "select",
		options: [{
			value: "72",
			label: "low (72 DPI)"
		}, {
			value: "600",
			label: "high (600 DPI)"
		}]
	},
	showStereoFlags: {
		label: "Show Stereo Flags",
		type: "checkbox"
	},
	stereoLabelStyle: {
		label: "Label Display at Stereogenic Centers",
		type: "select",
		options: [
			{
				value: "Iupac",
				label: "IUPAC style"
			},
			{
				value: "Classic",
				label: "Classic"
			},
			{
				value: "On",
				label: "On"
			},
			{
				value: "Off",
				label: "Off"
			}
		]
	},
	colorOfAbsoluteCenters: {
		label: "Color of Absolute Centers",
		type: "color"
	},
	colorOfAndCenters: {
		label: "Color of AND Centers",
		type: "color"
	},
	colorOfOrCenters: {
		label: "Color of OR Centers",
		type: "color"
	},
	colorStereogenicCenters: {
		label: "Color Stereogenic Centers",
		type: "select",
		options: [
			{
				value: "LabelsOnly",
				label: "Labels Only"
			},
			{
				value: "BondsOnly",
				label: "Bonds Only"
			},
			{
				value: "LabelsAndBonds",
				label: "Labels and Bonds"
			},
			{
				value: "Off",
				label: "Off"
			}
		]
	},
	autoFadeOfStereoLabels: {
		label: "Auto Fade of Stereo Labels",
		type: "checkbox"
	},
	absFlagLabel: {
		label: "Absolute Flag Label",
		type: "text"
	},
	andFlagLabel: {
		label: "AND Flag Label",
		type: "text"
	},
	orFlagLabel: {
		label: "OR Flag Label",
		type: "text"
	},
	mixedFlagLabel: {
		label: "Mixed Flag Label",
		type: "text"
	},
	ignoreChiralFlag: {
		label: "Ignore Chiral Flag",
		type: "checkbox"
	},
	carbonExplicitly: {
		label: "Show Carbon Explicitly",
		type: "checkbox"
	},
	showCharge: {
		label: "Show Charge",
		type: "checkbox"
	},
	showValence: {
		label: "Show Valence",
		type: "checkbox"
	},
	showHydrogenLabels: {
		label: "Show Hydrogen Labels",
		type: "select",
		options: [
			{
				value: "off",
				label: "Off"
			},
			{
				value: "Hetero",
				label: "Heteroatoms"
			},
			{
				value: "Terminal",
				label: "Terminal"
			},
			{
				value: "Terminal and Hetero",
				label: "Terminal and Hetero"
			},
			{
				value: "On",
				label: "On"
			}
		]
	},
	aromaticCircle: {
		label: "Aromatic Circle",
		type: "checkbox"
	},
	bondSpacing: {
		label: "Bond Spacing",
		type: "number",
		min: .1,
		max: 10,
		step: .1
	},
	bondThickness: {
		label: "Bond Thickness",
		type: "number",
		min: .1,
		max: 96,
		step: .1
	},
	bondThicknessUnit: {
		label: "Bond Thickness Unit",
		type: "select",
		options: [
			{
				value: "px",
				label: "px"
			},
			{
				value: "pt",
				label: "pt"
			},
			{
				value: "cm",
				label: "cm"
			},
			{
				value: "inch",
				label: "inch"
			}
		]
	},
	stereoBondWidth: {
		label: "Stereo Bond Width",
		type: "number",
		min: .1,
		max: 96,
		step: .1
	},
	stereoBondWidthUnit: {
		label: "Stereo Bond Width Unit",
		type: "select",
		options: [
			{
				value: "px",
				label: "px"
			},
			{
				value: "pt",
				label: "pt"
			},
			{
				value: "cm",
				label: "cm"
			},
			{
				value: "inch",
				label: "inch"
			}
		]
	},
	hashSpacing: {
		label: "Hash Spacing",
		type: "number",
		min: .1,
		max: 1e3,
		step: .1
	},
	hashSpacingUnit: {
		label: "Hash Spacing Unit",
		type: "select",
		options: [
			{
				value: "px",
				label: "px"
			},
			{
				value: "pt",
				label: "pt"
			},
			{
				value: "cm",
				label: "cm"
			},
			{
				value: "inch",
				label: "inch"
			}
		]
	},
	"smart-layout": {
		label: "Smart Layout",
		type: "checkbox"
	},
	"ignore-stereochemistry-errors": {
		label: "Ignore Stereochemistry Errors",
		type: "checkbox"
	},
	"mass-skip-error-on-pseudoatoms": {
		label: "Skip Mass Error on Pseudoatoms",
		type: "checkbox"
	},
	"gross-formula-add-rsites": {
		label: "Add R-sites to Gross Formula",
		type: "checkbox"
	},
	"gross-formula-add-isotopes": {
		label: "Add Isotopes to Gross Formula",
		type: "checkbox"
	},
	miewMode: {
		label: "Miew Mode",
		type: "select",
		options: [
			{
				value: "LN",
				label: "Lines"
			},
			{
				value: "BS",
				label: "Ball and Stick"
			},
			{
				value: "LC",
				label: "Licorice"
			}
		]
	},
	miewTheme: {
		label: "Miew Theme",
		type: "select",
		options: [{
			value: "light",
			label: "Light"
		}, {
			value: "dark",
			label: "Dark"
		}]
	},
	miewAtomLabel: {
		label: "Miew Atom Label",
		type: "select",
		options: [
			{
				value: "no",
				label: "None"
			},
			{
				value: "bright",
				label: "Bright"
			},
			{
				value: "blackAndWhite",
				label: "Black and White"
			},
			{
				value: "black",
				label: "Black"
			}
		]
	},
	showAtomIds: {
		label: "Show Atom IDs",
		type: "checkbox"
	},
	showBondIds: {
		label: "Show Bond IDs",
		type: "checkbox"
	},
	showHalfBondIds: {
		label: "Show Half-Bond IDs",
		type: "checkbox"
	},
	showLoopIds: {
		label: "Show Loop IDs",
		type: "checkbox"
	}
}, AE = z("div", { target: "e18f9swt7" })({
	name: "bbzy94",
	styles: "padding:16px;max-height:600px;overflow-y:auto"
}), jE = z("div", { target: "e18f9swt6" })({
	name: "197tvr9",
	styles: "display:flex;gap:8px;align-items:center"
}), ME = z("span", { target: "e18f9swt5" })({
	name: "1yvcaec",
	styles: "padding-right:4px"
}), NE = z("button", { target: "e18f9swt4" })({
	name: "1ylif76",
	styles: "background-color:transparent;border:none;color:#167782;padding:0;font-size:0;cursor:pointer;display:flex;align-items:center;justify-content:center;&:hover{color:#005662;}&:disabled{color:#cad3dd;cursor:not-allowed;}input[type='file']{display:none;}"
}), PE = z("div", { target: "e18f9swt3" })({
	name: "12vf6wv",
	styles: "display:flex;gap:8px;flex:1"
}), FE = z("div", { target: "e18f9swt2" })({
	name: "d1a0dy",
	styles: "display:flex;gap:8px;margin-left:auto"
}), IE = z("div", { target: "e18f9swt1" })({
	name: "1lmm7nm",
	styles: "display:flex;flex-direction:column;gap:12px;padding:8px 0"
}), LE = z("div", { target: "e18f9swt0" })({
	name: "1e32yau",
	styles: "display:flex;align-items:center;justify-content:flex-start;font-size:12px;line-height:14px;margin-bottom:12px;color:#333333;height:24px;label{display:flex;justify-content:flex-start;align-items:center;width:100%;}label>span:first-of-type{width:168px;margin-right:8px;}label>input,label>select,label>div{width:120px;margin-right:auto;}"
}), RE = function(e) {
	var t = e.name, n = e.label, r = e.type, i = e.value, a = e.onChange, o = e.options, s = e.min, c = e.max, l = e.step;
	return U(LE, { children: function() {
		switch (r) {
			case "checkbox": return W("label", { children: [U("span", { children: n }), U(ci, {
				checked: !!i,
				onChange: function(e) {
					return a(e.target.checked);
				},
				size: "small",
				"data-testid": `setting-${t}`
			})] });
			case "number": return W("label", { children: [U("span", { children: n }), U("input", {
				type: "number",
				value: i ?? "",
				onChange: function(e) {
					return a(Number(e.target.value));
				},
				min: s,
				max: c,
				step: l ?? 1,
				"data-testid": `setting-${t}`,
				style: {
					fontSize: "12px",
					padding: "4px 8px",
					height: "24px",
					border: "1px solid #cad3dd",
					borderRadius: "2px"
				}
			})] });
			case "select": return W("label", { children: [U("span", { children: n }), U(Rn, {
				size: "small",
				sx: { border: "none" },
				children: U(zt, {
					value: i ?? "",
					onChange: function(e) {
						return a(e.target.value);
					},
					displayEmpty: !0,
					"data-testid": `setting-${t}`,
					sx: {
						fontSize: "12px",
						height: "24px",
						border: "none",
						"& .MuiOutlinedInput-notchedOutline": { border: "1px solid #cad3dd" },
						"&:hover .MuiOutlinedInput-notchedOutline": { borderColor: "#167782" },
						"&.Mui-focused .MuiOutlinedInput-notchedOutline": { borderColor: "#167782" }
					},
					children: o?.map(function(e) {
						return U(Ft, {
							value: e.value,
							sx: { fontSize: "12px" },
							children: e.label
						}, String(e.value));
					})
				})
			})] });
			case "color": return W("label", { children: [U("span", { children: n }), W("div", {
				style: {
					display: "flex",
					gap: "4px",
					alignItems: "center"
				},
				children: [U("input", {
					type: "color",
					value: i ?? "#000000",
					onChange: function(e) {
						return a(e.target.value);
					},
					"data-testid": `setting-${t}`,
					style: {
						width: "30px",
						height: "24px",
						border: "1px solid #cad3dd",
						borderRadius: "2px",
						cursor: "pointer",
						padding: "2px"
					}
				}), U("input", {
					type: "text",
					value: i ?? "#000000",
					onChange: function(e) {
						return a(e.target.value);
					},
					style: {
						width: "85px",
						fontSize: "12px",
						padding: "4px 8px",
						height: "24px",
						border: "1px solid #cad3dd",
						borderRadius: "2px"
					}
				})]
			})] });
			default: return W("label", { children: [U("span", { children: n }), U("input", {
				type: "text",
				value: i ?? "",
				onChange: function(e) {
					return a(e.target.value);
				},
				"data-testid": `setting-${t}`,
				style: {
					fontSize: "12px",
					padding: "4px 8px",
					height: "24px",
					border: "1px solid #cad3dd",
					borderRadius: "2px"
				}
			})] });
		}
	}() });
}, zE = function(e) {
	var t = e.fields, n = e.settings, r = e.onChange;
	return U(IE, { children: t.map(function(e) {
		var t = kE[e];
		return t ? U(RE, {
			name: String(e),
			label: t.label,
			type: t.type,
			value: n[e],
			options: t.options,
			min: t.min,
			max: t.max,
			step: t.step,
			onChange: function(t) {
				return r(I({}, e, t));
			}
		}, String(e)) : (tt.warn(`Field definition not found: ${String(e)}`), null);
	}) });
}, BE = z("div", { target: "eun7sff2" })({
	name: "1nb5n7m",
	styles: "width:100%;display:flex;align-items:center;justify-content:space-between;font-size:14px;line-height:14px;color:#333333;font-weight:400"
}), VE = z("div", { target: "eun7sff1" })({
	name: "1sg2swb",
	styles: "display:flex;align-items:center;gap:6px;svg{width:15px;height:15px;}span{height:12px;}"
});
z("span", { target: "eun7sff0" })({
	name: "1fcc4f0",
	styles: "width:10px;height:10px;border-radius:50%;background-color:#167782;margin-left:auto;margin-right:8px"
});
var HE = function(e) {
	var t = e.settings, n = e.onChange, r = e.expandedGroups, i = e.onGroupToggle, a = function(e) {
		return !1;
	};
	return U("div", { children: OE.map(function(e) {
		return W(ke, {
			expanded: r.includes(e.id),
			onChange: function() {
				return i(e.id);
			},
			"data-testid": `${e.title}-accordion`,
			children: [U(Kt, {
				"aria-controls": `${e.id}-content`,
				id: `${e.id}-header`,
				children: W(BE, { children: [W(VE, { children: [U(P, { name: "elements-group" }), U("span", { children: e.title })] }), a()] })
			}), U(Ce, { children: U(zE, {
				fields: e.fields,
				settings: t,
				onChange: n
			}) })]
		}, e.id);
	}) });
};
function UE(e, t) {
	var n = Object.keys(e);
	if (Object.getOwnPropertySymbols) {
		var r = Object.getOwnPropertySymbols(e);
		t && (r = r.filter(function(t) {
			return Object.getOwnPropertyDescriptor(e, t).enumerable;
		})), n.push.apply(n, r);
	}
	return n;
}
function WE(e) {
	for (var t = 1; t < arguments.length; t++) {
		var n = arguments[t] == null ? {} : arguments[t];
		t % 2 ? UE(Object(n), !0).forEach(function(t) {
			I(e, t, n[t]);
		}) : Object.getOwnPropertyDescriptors ? Object.defineProperties(e, Object.getOwnPropertyDescriptors(n)) : UE(Object(n)).forEach(function(t) {
			Object.defineProperty(e, t, Object.getOwnPropertyDescriptor(n, t));
		});
	}
	return e;
}
var GE = {
	open: jT,
	save: GT,
	delete: JT,
	updateSequenceInRNABuilder: XT,
	monomerConnection: CE,
	confirmationDialog: DE,
	settings: function(e) {
		var t = e.isModalOpen, n = e.onClose, r = window.ketcher?.settingsService, i = (0, B.useState)(null), a = R(i, 2), o = a[0], s = a[1], c = (0, B.useState)(null), l = R(c, 2), u = l[0], d = l[1], f = (0, B.useState)(["general"]), p = R(f, 2), m = p[0], h = p[1], g = (0, B.useState)(!1), _ = R(g, 2), v = _[0], y = _[1];
		(0, B.useEffect)(function() {
			if (r && t) {
				var e = r.getSettings(), n = ee(e);
				return s(n), d(n), r.subscribe(function(e) {
					s(ee(e));
				});
			}
		}, [r, t]);
		var b = (0, B.useMemo)(function() {
			return !o || !u ? !1 : JSON.stringify(o) !== JSON.stringify(u);
		}, [o, u]), x = function(e) {
			s(function(t) {
				return t ? WE(WE({}, t), e) : null;
			});
		}, S = function(e) {
			h(function(t) {
				return t.includes(e) ? t.filter(function(t) {
					return t !== e;
				}) : [].concat(L(t), [e]);
			});
		}, C = function() {
			var e = dn(Ds.default.mark(function e() {
				var t;
				return Ds.default.wrap(function(e) {
					for (;;) switch (e.prev = e.next) {
						case 0:
							if (r && o) {
								e.next = 2;
								break;
							}
							return e.abrupt("return");
						case 2: return y(!0), e.prev = 3, t = je(o), e.next = 7, r.updateSettings(t);
						case 7:
							d(o), n(), e.next = 14;
							break;
						case 11: e.prev = 11, e.t0 = e.catch(3), tt.error("Failed to save settings:", e.t0);
						case 14: return e.prev = 14, y(!1), e.finish(14);
						case 17:
						case "end": return e.stop();
					}
				}, e, null, [[
					3,
					11,
					14,
					17
				]]);
			}));
			return function() {
				return e.apply(this, arguments);
			};
		}(), w = function() {
			var e = dn(Ds.default.mark(function e() {
				var t, n;
				return Ds.default.wrap(function(e) {
					for (;;) switch (e.prev = e.next) {
						case 0:
							if (r) {
								e.next = 2;
								break;
							}
							return e.abrupt("return");
						case 2: return y(!0), e.prev = 3, e.next = 6, r.resetToDefaults();
						case 6:
							t = e.sent, n = ee(t), s(n), d(n), e.next = 15;
							break;
						case 12: e.prev = 12, e.t0 = e.catch(3), tt.error("Failed to reset settings:", e.t0);
						case 15: return e.prev = 15, y(!1), e.finish(15);
						case 18:
						case "end": return e.stop();
					}
				}, e, null, [[
					3,
					12,
					15,
					18
				]]);
			}));
			return function() {
				return e.apply(this, arguments);
			};
		}(), T = function() {
			n();
		}, E = function() {
			var e = document.createElement("input");
			e.type = "file", e.accept = ".json", e.onchange = function() {
				var e = dn(Ds.default.mark(function e(t) {
					var n, i;
					return Ds.default.wrap(function(e) {
						for (;;) switch (e.prev = e.next) {
							case 0:
								if (n = t.target.files?.[0], n && r) {
									e.next = 3;
									break;
								}
								return e.abrupt("return");
							case 3: return y(!0), e.prev = 4, e.next = 7, n.text();
							case 7: return i = e.sent, e.next = 10, r.importSettings(i);
							case 10:
								e.next = 16;
								break;
							case 12: e.prev = 12, e.t0 = e.catch(4), tt.error("Failed to import settings:", e.t0), alert(`Import failed: ${e.t0 instanceof Error ? e.t0.message : String(e.t0)}`);
							case 16: return e.prev = 16, y(!1), e.finish(16);
							case 19:
							case "end": return e.stop();
						}
					}, e, null, [[
						4,
						12,
						16,
						19
					]]);
				}));
				return function(t) {
					return e.apply(this, arguments);
				};
			}(), e.click();
		}, D = function() {
			if (r) try {
				var e = r.exportSettings(), t = new Blob([e], { type: "application/json" }), n = URL.createObjectURL(t), i = document.createElement("a");
				i.href = n, i.download = `ketcher-settings-${Date.now()}.json`, i.click(), URL.revokeObjectURL(n);
			} catch (e) {
				tt.error("Failed to export settings:", e), alert("Export failed");
			}
		};
		if (!o) return null;
		var O = function() {
			var e = dn(Ds.default.mark(function e() {
				var t, n;
				return Ds.default.wrap(function(e) {
					for (;;) switch (e.prev = e.next) {
						case 0:
							if (r) {
								e.next = 2;
								break;
							}
							return e.abrupt("return");
						case 2: return y(!0), e.prev = 3, e.next = 6, r.loadPreset("acs");
						case 6:
							t = r.getSettings(), n = ee(t), s(n), e.next = 14;
							break;
						case 11: e.prev = 11, e.t0 = e.catch(3), tt.error("Failed to apply ACS style:", e.t0);
						case 14: return e.prev = 14, y(!1), e.finish(14);
						case 17:
						case "end": return e.stop();
					}
				}, e, null, [[
					3,
					11,
					14,
					17
				]]);
			}));
			return function() {
				return e.apply(this, arguments);
			};
		}();
		return W(Q, {
			title: W(jE, { children: [
				U(ME, { children: "Settings" }),
				U(NE, {
					onClick: E,
					disabled: v,
					title: "Open from File",
					"data-testid": "open-settings-from-file-button",
					children: U(P, { name: "open-1" })
				}),
				U(NE, {
					onClick: D,
					disabled: v,
					title: "Save to File",
					"data-testid": "save-settings-to-file-button",
					children: U(P, { name: "save-1" })
				}),
				U(NE, {
					onClick: w,
					disabled: v,
					title: "Reset",
					"data-testid": "reset-settings-button",
					children: U(P, { name: "reset" })
				})
			] }),
			isOpen: t,
			onClose: T,
			showExpandButton: !0,
			testId: "settings-modal",
			children: [U(Q.Content, { children: U(AE, { children: U(HE, {
				settings: o,
				onChange: x,
				expandedGroups: m,
				onGroupToggle: S
			}) }) }), W(Q.Footer, { children: [U(PE, { children: U(xC, {
				label: "Set ACS Settings",
				styleType: "secondary",
				clickHandler: O,
				disabled: v,
				"data-testid": "acs-style-button"
			}) }), W(FE, { children: [U(xC, {
				label: "Cancel",
				styleType: "secondary",
				clickHandler: T,
				disabled: v
			}), U(xC, {
				label: "Apply",
				clickHandler: C,
				disabled: !b || v
			})] })] })]
		});
	}
};
function KE(e, t) {
	var n = Object.keys(e);
	if (Object.getOwnPropertySymbols) {
		var r = Object.getOwnPropertySymbols(e);
		t && (r = r.filter(function(t) {
			return Object.getOwnPropertyDescriptor(e, t).enumerable;
		})), n.push.apply(n, r);
	}
	return n;
}
function qE(e) {
	for (var t = 1; t < arguments.length; t++) {
		var n = arguments[t] == null ? {} : arguments[t];
		t % 2 ? KE(Object(n), !0).forEach(function(t) {
			I(e, t, n[t]);
		}) : Object.getOwnPropertyDescriptors ? Object.defineProperties(e, Object.getOwnPropertyDescriptors(n)) : KE(Object(n)).forEach(function(t) {
			Object.defineProperty(e, t, Object.getOwnPropertyDescriptor(n, t));
		});
	}
	return e;
}
var JE = function() {
	var e = Z(ov), t = Z(av), n = Z(sv), r = X(), i = (0, B.useCallback)(function() {
		r(ev());
	}, [r]);
	if (!t) return null;
	var a = GE[t];
	if (!a) throw Error(`There is no modal window named ${t}`);
	return n ? U(a, qE({
		onClose: i,
		isModalOpen: e
	}, n)) : U(a, {
		onClose: i,
		isModalOpen: e
	});
}, YE = z("div", { target: "e15avtnm3" })({
	name: "3w0yoi",
	styles: "display:flex;flex-direction:column;gap:8px"
}), XE = z("div", { target: "e15avtnm2" })({
	name: "1bweptz",
	styles: "background-color:#333333;max-height:40px;display:flex;align-items:stretch"
}), ZE = z("div", { target: "e15avtnm1" })({
	name: "1my6l07",
	styles: "max-width:356px;padding:4px 10px 4px 10px;color:white;display:flex"
}), QE = z(oe, { target: "e15avtnm0" })({
	name: "1c8hqv0",
	styles: "color:white;width:24px;height:auto;display:flex;align-items:center;justify-content:center;&:hover{background-color:#585858;color:white;}svg{width:16px;height:16px;}"
}), $E = function() {
	return W(H, { children: [
		U("symbol", {
			id: "chem",
			viewBox: "0 0 59 59",
			width: "59",
			height: "59",
			children: U("rect", {
				className: "monomer-body",
				width: "29.5",
				height: "29.5",
				"data-actual-width": "29.5",
				"data-actual-height": "29.5",
				x: "0.5",
				y: "0.5",
				rx: "0.75"
			})
		}),
		U("symbol", {
			id: "chem-selection",
			viewBox: "0 0 59 59",
			width: "59",
			height: "59",
			children: U("rect", {
				width: "29.5",
				height: "29.5",
				x: "0.5",
				y: "0.5",
				rx: "0.75",
				stroke: "#0097A8",
				fill: "none",
				strokeWidth: "1.5"
			})
		}),
		W("symbol", {
			id: "chem-autochain-preview",
			viewBox: "0 0 32 32",
			width: "32",
			height: "32",
			"data-actual-width": "32",
			"data-actual-height": "32",
			children: [
				U("path", { d: "M1 4.63574V2.63574C1 1.53117 1.89543 0.635742 3 0.635742H5" }),
				U("path", { d: "M1 26.6357V28.6357C1 29.7403 1.89543 30.6357 3 30.6357H5" }),
				U("path", { d: "M31 4.63574V2.63574C31 1.53117 30.1046 0.635742 29 0.635742H27" }),
				U("path", { d: "M31 26.6357V28.6357C31 29.7403 30.1046 30.6357 29 30.6357H27" }),
				U("path", { d: "M7.02142 30.6357L10.0214 30.6357" }),
				U("path", { d: "M12.0013 30.6357L15.0013 30.6357" }),
				U("path", { d: "M16.9816 30.6357L19.9816 30.6357" }),
				U("path", { d: "M22.0222 30.6357L25.0222 30.6357" }),
				U("path", { d: "M1.02185 6.63574L1.02185 9.63574" }),
				U("path", { d: "M1.02185 11.6152L1.02185 14.6152" }),
				U("path", { d: "M1.02185 16.5957L1.02185 19.5957" }),
				U("path", { d: "M1.02185 21.6367L1.02185 24.6367" }),
				U("path", { d: "M7.02142 0.635742L10.0214 0.635742" }),
				U("path", { d: "M12.0013 0.635742L15.0013 0.635742" }),
				U("path", { d: "M16.9816 0.635742L19.9816 0.635742" }),
				U("path", { d: "M22.0222 0.635742L25.0222 0.635742" }),
				U("path", { d: "M31.0219 6.63574L31.0219 9.63574" }),
				U("path", { d: "M31.0219 11.6152L31.0219 14.6152" }),
				U("path", { d: "M31.0219 16.5957L31.0219 19.5957" }),
				U("path", { d: "M31.0219 21.6367L31.0219 24.6367" })
			]
		})
	] });
}, eD = function() {
	return W(H, { children: [
		U("symbol", {
			id: "peptide",
			viewBox: "0 0 70 61",
			width: "70",
			height: "61",
			children: U("path", {
				className: "monomer-body",
				transform: "scale(0.5)",
				"data-actual-width": "35",
				"data-actual-height": "30.5",
				d: "M16.9236 1.00466C17.2801 0.383231 17.9418 6.10888e-07 18.6583 5.98224e-07L51.3417 2.04752e-08C52.0582 7.81036e-09 52.7199 0.383234 53.0764 1.00466L69.4289 29.5047C69.7826 30.1211 69.7826 30.8789 69.4289 31.4953L53.0764 59.9953C52.7199 60.6168 52.0582 61 51.3417 61H18.6583C17.9418 61 17.2801 60.6168 16.9236 59.9953L0.571095 31.4953C0.217407 30.8789 0.217408 30.1211 0.571096 29.5047L16.9236 1.00466Z"
			})
		}),
		W("symbol", {
			id: "peptide-hover",
			viewBox: "0 0 70 61",
			width: "70",
			height: "61",
			children: [U("path", {
				d: "M18.2246 1.75116C18.3137 1.59581 18.4792 1.5 18.6583 1.5L51.3417 1.5C51.5208 1.5 51.6863 1.59581 51.7754 1.75116L53.06 1.01408L51.7754 1.75117L68.1279 30.2512C68.2163 30.4053 68.2163 30.5947 68.1279 30.7488L51.7754 59.2488C51.6863 59.4042 51.5208 59.5 51.3417 59.5H18.6583C18.4792 59.5 18.3137 59.4042 18.2246 59.2488L1.87215 30.7488C1.78372 30.5947 1.78372 30.4053 1.87215 30.2512L18.2246 1.75116Z",
				fill: "none",
				transform: "scale(0.5)",
				stroke: "#0097A8",
				strokeWidth: "3"
			}), " "]
		}),
		U("symbol", {
			id: "modified-background",
			viewBox: "0 0 60 20",
			width: "30",
			height: "20",
			x: "2.5",
			y: "5",
			children: U("path", {
				xmlns: "http://www.w3.org/2000/svg",
				d: "M6.52702 20C5.81057 20 5.14885 19.6168 4.79229 18.9953L0.570974 11.6382C0.217285 11.0218 \n           0.217285 10.2639 0.570974 9.64751L5.52999 1.00466C5.88654 0.383235 6.54827 0 7.26472 0H52.735C53.4515\n           0 54.1132 0.383234 54.4698 1.00466L59.4288 9.64751C59.7825 10.2639 59.7825 11.0218 59.4288 11.6382\n           L55.2075 18.9953C54.8509 19.6168 54.1892 20 53.4727 20H6.52702Z",
				fillOpacity: "0.6"
			})
		}),
		W("symbol", {
			id: "peptide-autochain-preview",
			viewBox: "0 0 37 32",
			width: "37",
			height: "32",
			"data-actual-width": "37",
			"data-actual-height": "32",
			children: [
				U("path", { d: "M8.27143 3.53027L9.29272 1.77462C9.65083 1.15901 10.3093 0.780274 11.0215 0.780274L13.1642 0.780274M29.2131 3.53027L28.1919 1.77462C27.8337 1.15901 27.1753 0.780273 26.4631 0.780273L24.3164 0.780273M2.45429 13.5303L1.585 15.0246C1.22337 15.6463 1.22337 16.4143 1.585 17.0359L2.45429 18.5303M29.0386 28.5303L28.0233 30.2756C27.6619 30.897 26.991 31.2803 26.2646 31.2803L24.1459 31.2803M8.09693 28.5303L9.11221 30.2756C9.47371 30.897 10.1446 31.2803 10.871 31.2803H12.9936M34.8558 18.5303L35.7311 17.0256C36.0896 16.4092 36.0896 15.6514 35.7311 15.0349L34.8558 13.5303" }),
				U("path", { d: "M14.8937 0.780178L17.8937 0.780178" }),
				U("path", { d: "M19.597 0.780178L22.597 0.780178" }),
				U("path", { d: "M14.8937 31.2804H17.8937" }),
				U("path", { d: "M19.597 31.2804H22.597" }),
				U("path", { d: "M3.61253 11.7412L5.11253 9.14309" }),
				U("path", { d: "M5.96421 7.66792L7.46421 5.06984" }),
				U("path", { d: "M30.1034 26.877L31.6034 24.2789" }),
				U("path", { d: "M32.455 22.8038L33.955 20.2057" }),
				U("path", { d: "M7.32633 26.9903L5.82633 24.3922" }),
				U("path", { d: "M4.97465 22.917L3.47465 20.319" }),
				U("path", { d: "M33.9528 11.8759L32.4782 9.26339" }),
				U("path", { d: "M31.6409 7.78023L30.1662 5.16769" })
			]
		})
	] });
}, tD = function() {
	return W(H, { children: [
		U("symbol", {
			id: "sugar",
			viewBox: "0 0 70 70",
			width: "70",
			height: "70",
			children: U("rect", {
				className: "monomer-body",
				width: "28.5",
				height: "28.5",
				"data-actual-width": "28.5",
				"data-actual-height": "28.5",
				rx: "5"
			})
		}),
		U("symbol", {
			id: "sugar-selection",
			viewBox: "-1 -1 100 100",
			width: "70",
			height: "70",
			children: U("rect", {
				width: "39",
				height: "39",
				rx: "5",
				fill: "none",
				stroke: "#0097A8",
				strokeWidth: "2.5"
			})
		}),
		U("symbol", {
			id: "sugar-variant",
			viewBox: "0 0 72 72",
			width: "70",
			height: "70",
			children: U("rect", {
				className: "monomer-body",
				width: "28.5",
				height: "28.5",
				"data-actual-width": "28.5",
				"data-actual-height": "28.5",
				x: "0.5",
				y: "0.5",
				rx: "5",
				stroke: "#585858",
				strokeWidth: "0.5"
			})
		}),
		U("symbol", {
			id: "sugar-modified-background",
			viewBox: "0 0 28 10",
			width: "27",
			height: "10",
			x: "0.7",
			y: "10",
			children: U("path", {
				d: "M1.5 10C0.947715 10 0.5 9.55229 0.5 9V1C0.5 0.447715 0.947715 0 1.5 0H26.5C27.0523 0 27.5 0.447715 27.5 1V9C27.5 9.55228 27.0523 10 26.5 10H1.5Z",
				fill: "white",
				fillOpacity: "0.6"
			})
		}),
		W("symbol", {
			id: "sugar-autochain-preview",
			viewBox: "0 0 32 32",
			width: "32",
			height: "32",
			"data-actual-width": "32",
			"data-actual-height": "32",
			children: [
				U("path", { d: "M1 4.63574V2.63574C1 1.53117 1.89543 0.635742 3 0.635742H5" }),
				U("path", { d: "M1 26.6357V28.6357C1 29.7403 1.89543 30.6357 3 30.6357H5" }),
				U("path", { d: "M31 4.63574V2.63574C31 1.53117 30.1046 0.635742 29 0.635742H27" }),
				U("path", { d: "M31 26.6357V28.6357C31 29.7403 30.1046 30.6357 29 30.6357H27" }),
				U("path", { d: "M7.02142 30.6357L10.0214 30.6357" }),
				U("path", { d: "M12.0013 30.6357L15.0013 30.6357" }),
				U("path", { d: "M16.9816 30.6357L19.9816 30.6357" }),
				U("path", { d: "M22.0222 30.6357L25.0222 30.6357" }),
				U("path", { d: "M1.02185 6.63574L1.02185 9.63574" }),
				U("path", { d: "M1.02185 11.6152L1.02185 14.6152" }),
				U("path", { d: "M1.02185 16.5957L1.02185 19.5957" }),
				U("path", { d: "M1.02185 21.6367L1.02185 24.6367" }),
				U("path", { d: "M7.02142 0.635742L10.0214 0.635742" }),
				U("path", { d: "M12.0013 0.635742L15.0013 0.635742" }),
				U("path", { d: "M16.9816 0.635742L19.9816 0.635742" }),
				U("path", { d: "M22.0222 0.635742L25.0222 0.635742" }),
				U("path", { d: "M31.0219 6.63574L31.0219 9.63574" }),
				U("path", { d: "M31.0219 11.6152L31.0219 14.6152" }),
				U("path", { d: "M31.0219 16.5957L31.0219 19.5957" }),
				U("path", { d: "M31.0219 21.6367L31.0219 24.6367" })
			]
		})
	] });
}, nD = function() {
	return W(H, { children: [
		U("symbol", {
			id: "phosphate",
			viewBox: "0 0 70 70",
			width: "70",
			height: "70",
			children: U("rect", {
				className: "monomer-body",
				width: "28",
				height: "28",
				"data-actual-width": "28",
				"data-actual-height": "28",
				rx: "15"
			})
		}),
		U("symbol", {
			id: "phosphate-selection",
			viewBox: "-1 -1 75 75",
			width: "70",
			height: "70",
			children: U("rect", {
				width: "28",
				height: "28",
				rx: "15",
				fill: "none",
				stroke: "#0097A8",
				strokeWidth: "1.5"
			})
		}),
		U("symbol", {
			id: "phosphate-variant",
			viewBox: "0 0 70 70",
			width: "70",
			height: "70",
			children: U("rect", {
				className: "monomer-body",
				width: "27",
				height: "27",
				"data-actual-width": "27",
				"data-actual-height": "27",
				stroke: "#585858",
				strokeWidth: "0.5",
				x: "0.5",
				y: "0.5",
				rx: "15"
			})
		}),
		U("symbol", {
			id: "phosphate-modified-background",
			viewBox: "0 0 28 10",
			width: "26",
			height: "10",
			x: "1",
			y: "9.5",
			children: U("path", {
				d: "M2.13388 0C1.72465 0 1.35333 0.248229 1.22109 0.635509C0.753639 2.00455 0.5 3.47265 0.5 5C0.5 6.52735 0.753639 7.99545 1.22109 9.36449C1.35333 9.75177 1.72465 10 2.13389 10H25.8661C26.2753 10 26.6467 9.75177 26.7789 9.36449C27.2464 7.99545 27.5 6.52735 27.5 5C27.5 3.47265 27.2464 2.00455 26.7789 0.635509C26.6467 0.248229 26.2753 0 25.8661 0H2.13388Z",
				fill: "#333333",
				fillOpacity: "0.6"
			})
		}),
		U("symbol", {
			id: "phosphate-autochain-preview",
			viewBox: "-1 -1 30 30",
			width: "30",
			height: "30",
			"data-actual-width": "30",
			"data-actual-height": "30",
			children: U("rect", {
				width: "28",
				height: "28",
				rx: "15",
				strokeDasharray: "4 4"
			})
		})
	] });
}, rD = function() {
	return W(H, { children: [
		U("symbol", {
			id: "rna-base",
			viewBox: "-16 0 65 65",
			width: "65",
			height: "95",
			children: U("rect", {
				width: "22.5",
				height: "22.5",
				"data-actual-width": "31.82",
				"data-actual-height": "31.82",
				rx: "1",
				x: "-11.25",
				y: "-11.25",
				transform: "rotate(45)",
				className: "monomer-body"
			})
		}),
		U("symbol", {
			id: "rna-base-selection",
			viewBox: "-15.75 -0.25 65 65",
			width: "65",
			height: "95",
			children: U("rect", {
				width: "21",
				height: "21",
				rx: "1",
				x: "-10.5",
				y: "-10.5",
				transform: "rotate(45)",
				stroke: "#0097A8",
				strokeWidth: "1.5",
				fill: "none"
			})
		}),
		U("symbol", {
			id: "rna-base-variant",
			viewBox: "-16 0 65 65",
			width: "65",
			height: "94",
			children: U("rect", {
				width: "21.5",
				height: "21.5",
				"data-actual-width": "30",
				"data-actual-height": "30",
				stroke: "#585858",
				strokeWidth: "0.5",
				rx: "1",
				x: "-10.25",
				y: "-10.25",
				transform: "rotate(45)",
				className: "monomer-body"
			})
		}),
		U("symbol", {
			id: "rna-base-modified-background",
			viewBox: "0 0 32 10",
			width: "30",
			height: "9",
			x: "0.8",
			y: "10.8",
			children: U("path", {
				fillRule: "evenodd",
				clipRule: "evenodd",
				d: "M6.30156 10C6.03634 10 5.78199 9.89464 5.59445 9.70711L1.1508 5.26346C0.760279 4.87293 0.760279 4.23977 1.1508 3.84924L4.70715 0.292893C4.89469 0.105357 5.14904 0 5.41426 0H26.5858C26.851 0 27.1054 0.105357 27.2929 0.292893L30.8493 3.84924C31.2398 4.23977 31.2398 4.87293 30.8493 5.26346L26.4056 9.70711C26.2181 9.89464 25.9637 10 25.6985 10H6.30156Z",
				fill: "#333333",
				fillOpacity: "0.6"
			})
		}),
		W("symbol", {
			id: "rna-base-autochain-preview",
			viewBox: "0 0 36 36",
			width: "36",
			height: "36",
			"data-actual-width": "36",
			"data-actual-height": "36",
			children: [
				U("path", { d: "M2.77636 20.2837L1.83359 19.341C1.05254 18.5599 1.05254 17.2936 1.83359 16.5125L2.77468 15.5715" }),
				U("path", { d: "M15.7398 33.2465L16.6826 34.1893C17.4636 34.9704 18.73 34.9704 19.511 34.1893L20.4521 33.2482" }),
				U("path", { d: "M20.4412 2.61969L19.4984 1.67691C18.7173 0.89586 17.451 0.895861 16.67 1.67691L15.7289 2.618" }),
				U("path", { d: "M33.4046 15.5825L34.3474 16.5252C35.1284 17.3063 35.1284 18.5726 34.3474 19.3537L33.4063 20.2948" }),
				U("path", { d: "M21.6425 32.0586L23.4089 30.2921" }),
				U("path", { d: "M24.5747 29.126L26.3412 27.3595" }),
				U("path", { d: "M27.5073 26.1934L29.2737 24.4269" }),
				U("path", { d: "M30.4753 23.2256L32.2418 21.4591" }),
				U("path", { d: "M3.96771 21.4492L5.73546 23.217" }),
				U("path", { d: "M6.90216 24.3838L8.6699 26.1515" }),
				U("path", { d: "M9.83673 27.3184L11.6045 29.0861" }),
				U("path", { d: "M12.8069 30.2881L14.5747 32.0558" }),
				U("path", { d: "M3.96497 14.3809L5.73145 12.6144" }),
				U("path", { d: "M6.89728 11.4482L8.66376 9.68176" }),
				U("path", { d: "M9.82977 8.5166L11.5963 6.75012" }),
				U("path", { d: "M12.7979 5.54785L14.5643 3.78137" }),
				U("path", { d: "M21.6326 3.78418L23.4003 5.55192" }),
				U("path", { d: "M24.567 6.71875L26.3347 8.48649" }),
				U("path", { d: "M27.5016 9.65332L29.2693 11.4211" }),
				U("path", { d: "M30.4718 12.623L32.2395 14.3908" })
			]
		})
	] });
}, iD = function() {
	return W(H, { children: [
		W("symbol", {
			id: "unresolved-monomer",
			viewBox: "0 0 59 59",
			width: "59",
			height: "59",
			children: [U("rect", {
				className: "monomer-body",
				width: "29.5",
				height: "29.5",
				"data-actual-width": "29.5",
				"data-actual-height": "29.5",
				x: "0.5",
				y: "0.5",
				rx: "1.5",
				stroke: "#333333"
			}), U("rect", {
				width: "29.5",
				height: "29.5",
				"data-actual-width": "29.5",
				"data-actual-height": "29.5",
				x: "0.5",
				y: "0.5",
				rx: "1.5",
				fill: "#585858"
			})]
		}),
		U("symbol", {
			id: "unresolved-monomer-hover",
			children: U("rect", {
				width: "29.5",
				height: "29.5",
				x: "0.5",
				y: "0.5",
				rx: "1.5",
				fill: "none",
				stroke: "#0097A8",
				strokeWidth: "1.5"
			})
		}),
		W("symbol", {
			id: "unresolved-monomer-autochain-preview",
			viewBox: "0 0 32 32",
			width: "32",
			height: "32",
			"data-actual-width": "32",
			"data-actual-height": "32",
			children: [
				U("path", { d: "M1 4.63574V2.63574C1 1.53117 1.89543 0.635742 3 0.635742H5" }),
				U("path", { d: "M1 26.6357V28.6357C1 29.7403 1.89543 30.6357 3 30.6357H5" }),
				U("path", { d: "M31 4.63574V2.63574C31 1.53117 30.1046 0.635742 29 0.635742H27" }),
				U("path", { d: "M31 26.6357V28.6357C31 29.7403 30.1046 30.6357 29 30.6357H27" }),
				U("path", { d: "M7.02142 30.6357L10.0214 30.6357" }),
				U("path", { d: "M12.0013 30.6357L15.0013 30.6357" }),
				U("path", { d: "M16.9816 30.6357L19.9816 30.6357" }),
				U("path", { d: "M22.0222 30.6357L25.0222 30.6357" }),
				U("path", { d: "M1.02185 6.63574L1.02185 9.63574" }),
				U("path", { d: "M1.02185 11.6152L1.02185 14.6152" }),
				U("path", { d: "M1.02185 16.5957L1.02185 19.5957" }),
				U("path", { d: "M1.02185 21.6367L1.02185 24.6367" }),
				U("path", { d: "M7.02142 0.635742L10.0214 0.635742" }),
				U("path", { d: "M12.0013 0.635742L15.0013 0.635742" }),
				U("path", { d: "M16.9816 0.635742L19.9816 0.635742" }),
				U("path", { d: "M22.0222 0.635742L25.0222 0.635742" }),
				U("path", { d: "M31.0219 6.63574L31.0219 9.63574" }),
				U("path", { d: "M31.0219 11.6152L31.0219 14.6152" }),
				U("path", { d: "M31.0219 16.5957L31.0219 19.5957" }),
				U("path", { d: "M31.0219 21.6367L31.0219 24.6367" })
			]
		})
	] });
}, aD = function() {
	return W(H, { children: [
		U("symbol", {
			id: "nucleotide",
			viewBox: "0 0 84 84",
			width: "42",
			height: "42",
			children: U("path", {
				className: "monomer-body",
				"data-actual-width": "42",
				"data-actual-height": "42",
				d: "M43.0152 71.4019C42.3887 71.771 41.6113 71.771 40.9848 71.4019L9.25584 52.7093C8.50744 52.2684 8.1292 51.3948 8.31974 50.5473L16.6358 13.5613C16.841 12.6485 17.6516 12 18.5871 12L65.4129 12C66.3484 12 67.159 12.6485 67.3642 13.5613L75.6803 50.5473C75.8708 51.3948 75.4926 52.2684 74.7442 52.7093L43.0152 71.4019Z",
				transform: "rotate(180, 42, 42)"
			})
		}),
		U("symbol", {
			id: "nucleotide-hover",
			viewBox: "0 0 84 84",
			width: "42",
			height: "42",
			children: U("path", {
				"data-actual-width": "42",
				"data-actual-height": "42",
				d: "M43.0152 71.4019C42.3887 71.771 41.6113 71.771 40.9848 71.4019L9.25584 52.7093C8.50744 52.2684 8.1292 51.3948 8.31974 50.5473L16.6358 13.5613C16.841 12.6485 17.6516 12 18.5871 12L65.4129 12C66.3484 12 67.159 12.6485 67.3642 13.5613L75.6803 50.5473C75.8708 51.3948 75.4926 52.2684 74.7442 52.7093L43.0152 71.4019Z",
				transform: "rotate(180, 42, 42)",
				fill: "none",
				stroke: "#0097A8",
				strokeWidth: "3"
			})
		}),
		W("symbol", {
			id: "nucleotide-autochain-preview",
			viewBox: "0 0 36 32",
			width: "36",
			height: "32",
			"data-actual-width": "36",
			"data-actual-height": "32",
			children: [
				U("path", { d: "M20.3771 2.38574L18.5929 1.0722C18.2402 0.812609 17.7598 0.812609 17.4071 1.0722L15.6229 2.38574M32.6021 11.3857L34.4405 12.7392C34.7769 12.9868 34.9239 13.4174 34.8092 13.8191L34.2725 15.6985M3.39787 11.3857L1.55948 12.7392C1.2231 12.9868 1.07608 13.4174 1.19078 13.8191L1.72751 15.6985M30.8088 27.8266L30.2138 29.9168C30.0914 30.3466 29.6988 30.643 29.252 30.643H27.0063M5.19116 27.8266L5.7931 29.9194C5.91633 30.3479 6.30831 30.643 6.75414 30.643H9.00194" }),
				U("path", { d: "M10.5017 30.6426L13.5017 30.6426" }),
				U("path", { d: "M16.5032 30.6426L19.5032 30.6426" }),
				U("path", { d: "M22.5046 30.6426L25.5046 30.6426" }),
				U("path", { d: "M2.23663 17.4971L3.06363 20.3808" }),
				U("path", { d: "M3.83911 23.0859L4.66611 25.9697" }),
				U("path", { d: "M22.356 3.85059L25.5765 6.22306" }),
				U("path", { d: "M27.5099 7.64746L30.7304 10.0199" }),
				U("path", { d: "M13.605 3.85156L10.3846 6.22404" }),
				U("path", { d: "M8.45105 7.64844L5.23059 10.0209" }),
				U("path", { d: "M33.7705 17.4971L32.9435 20.3808" }),
				U("path", { d: "M32.168 23.0859L31.341 25.9697" })
			]
		})
	] });
}, oD = function() {
	return W(H, { children: [
		U("path", {
			strokeLinecap: "round",
			d: "M5,0 0,2.5 5,5z",
			id: "arrow-marker-content"
		}),
		U("marker", {
			id: "arrow-marker",
			markerHeight: "3",
			markerWidth: "5",
			orient: "auto",
			refX: "2.5",
			refY: "1.5",
			children: U("use", {
				href: "#arrow-marker-content",
				transform: "rotate(180 2.5 1.5) scale(1,0.6)",
				strokeWidth: "1.2500",
				fill: "black",
				stroke: "none"
			})
		}),
		U("marker", {
			id: "arrow-marker-arc",
			markerWidth: "5",
			markerHeight: "5",
			viewBox: "0 0 5 5",
			refX: "5",
			refY: "2.5",
			orient: "auto",
			children: U("use", {
				href: "#arrow-marker-content",
				transform: "rotate(180, 2.5, 2.5)",
				fill: "#365CFF",
				stroke: "none"
			})
		})
	] });
}, sD = function() {
	return U("symbol", {
		id: "sequence-start-arrow",
		viewBox: "0 0 65 65",
		width: "65",
		height: "95",
		children: U("svg", {
			width: "12",
			height: "12",
			viewBox: "0 0 12 12",
			fill: "none",
			xmlns: "http://www.w3.org/2000/svg",
			children: U("path", {
				d: "M10.2802 5.09664C10.9756 5.49813 10.9756 6.50187 10.2802 6.90336L2.56467 11.3579C1.86926 11.7594 1 11.2576 1 10.4546V1.54541C1 0.742426 1.86926 0.240558 2.56467 0.642053L10.2802 5.09664Z",
				stroke: "#7C7C7F"
			})
		})
	});
}, cD = z("div", { target: "e1phidy70" })({
	name: "1fayh9l",
	styles: "padding:12px;font-size:12px;color:#000"
}), lD = function() {
	var e = X(), t = Z(lv), n = Z(uv) || "Error message", r = t !== "", i = function() {
		e(iv());
	};
	return W(Q, {
		isOpen: r,
		title: n,
		onClose: i,
		testId: "info-modal-window",
		children: [U(Q.Content, { children: U(cD, {
			"data-testid": "error-message-body",
			children: t
		}) }), U(Q.Footer, { children: U(xC, {
			label: "Close",
			clickHandler: i,
			"data-testid": "info-modal-close"
		}) })]
	});
}, uD = z("div", { target: "embh3ih3" })(function() {
	return { height: "100%" };
}, ""), dD = z("div", { target: "embh3ih2" })(function() {
	return {
		display: "flex",
		alignItems: "center"
	};
}, ""), fD = z("div", { target: "embh3ih1" })(function() {
	return {
		background: "",
		"&.toggler-component-wrapper--disabled": {
			opacity: .4,
			pointerEvents: "none",
			cursor: "default"
		}
	};
}, ""), pD = z("svg", { target: "embh3ih0" })(function() {
	return {
		"&.handCursor": { cursor: "\n      url('data:image/svg+xml;base64,PHN2ZwogICAgICAgIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyIKICAgICAgICB3aWR0aD0iMjQiCiAgICAgICAgaGVpZ2h0PSIyNCIKICAgICAgICBmaWxsPSJub25lIgogICAgICAgIHZpZXdCb3g9IjAgMCAyNCAyNCI+CiAgICA8cGF0aAogICAgICAgICAgICBmaWxsPSIjMDAwIgogICAgICAgICAgICBkPSJNMjAuNDM0IDcuNjczYy0uMS0uNi0uNzEzLTEuNzMxLTIuMzItMS43MzEtLjEyNiAwLS4yNTIuMDA3LS4zNzcuMDIzdi0uNzlhMS4wMSAxLjAxIDAgMCAwLS4wNDUtLjNjLS4xNzctLjU2NC0uODc2LTEuNjMxLTIuMjYyLTEuNjMxYTIuNTk5IDIuNTk5IDAgMCAwLS42NzYuMDg2IDIuMzk0IDIuMzk0IDAgMCAwLS4xNDYtLjIzYy0uNDUzLS42NDUtMS4xODYtMS0yLjA2My0xLS44NzcgMC0xLjU4NC4zNi0yLjAyNSAxLjAxN2EyLjQ2MSAyLjQ2MSAwIDAgMC0uMzYxLjg1IDIuNjYzIDIuNjYzIDAgMCAwLS40MDgtLjAzYy0xLjQ3NCAwLTIuMTI0IDEuMTUtMi4yNjIgMS43NTdhMS4wMzQgMS4wMzQgMCAwIDAtLjAyNC4yMjJWMTEuMWwtLjEzLS4xYy0uNTg4LS41LTIuMDM0LTEuMTIxLTMuMzkxLjAyOS0xLjM1NyAxLjE1LTEuMDE1IDIuNjY0LS40MzEgMy40NTIuNDUzLjc3MyA0LjUxMiA3LjQyNSAxMC4yMjMgNy40MjUgMy4yNSAwIDQuOTEtMS41MTIgNS43MjktMi43ODFhNi4yOTEgNi4yOTEgMCAwIDAgLjk4LTIuOFY3LjgzOGMuMDAxLS4wNTYtLjAwMy0uMTEtLjAxMS0uMTY1WiIKICAgIC8+CiAgICA8cGF0aAogICAgICAgICAgICBmaWxsPSIjZmZmIgogICAgICAgICAgICBzdHJva2U9IiNmZmYiCiAgICAgICAgICAgIGQ9Ik0xOC40NDggMTYuMjE1YTQuNDc0IDQuNDc0IDAgMCAxLS43IDEuODg3Yy0uODA1IDEuMi0yLjE1MyAxLjgtNC4wMDggMS44LTQuNzY4IDAtOC40ODQtNi40MTItOC41Mi02LjQ3NmEuNjY5LjY2OSAwIDAgMC0uMDktLjEyNmMtLjI5NC0uNDA4IDAtLjY1NS4xMDctLjc0OC4yNjctLjIyNy41NC0uMjM3LjgxLS4wMzFsMS43NyAxLjQ1MmExIDEgMCAwIDAgMS42NDQtLjc2M1Y2LjA4YS4yODcuMjg3IDAgMCAxIC4yOS0uMTQ4LjQ0LjQ0IDAgMCAxIC4zNzIuMTZ2NC43YTEgMSAwIDEgMCAyIDB2LTYuNDVjLjA2OC0uMjQ4LjMtLjI0OC40MjItLjI0OC4yIDAgLjQxNC4wMzIuNDgyLjI1NXY2LjQ0YTEgMSAwIDEgMCAyIDB2LTUuMmEuNzUuNzUgMCAwIDEgLjA3NC0uMTljLjA0OS0uMDgxLjEwOC0uMTUuMzI1LS4xNWEuMzUuMzUgMCAwIDEgLjMwNy4xNXY1LjM5YTEgMSAwIDEgMCAyIDBWOC4wNDdhLjU4My41ODMgMCAwIDEgLjM3Ny0uMWMuMDY1IDAgLjI1OC4wMDYuMzM0LjA3OGwuMDA0IDguMTlaIgogICAgLz4KPC9zdmc+Cg=='),\n      auto\n    " },
		"&.handCursorGrabbing": { cursor: "\n      url('data:image/svg+xml;base64,PHN2ZwogICAgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIgogICAgd2lkdGg9IjI0IgogICAgaGVpZ2h0PSIyNCIKICAgIGZpbGw9Im5vbmUiCiAgICB2aWV3Qm94PSIwIDAgMzAgMzAiCiAgPgogICAgPHBhdGgKICAgICAgZmlsbD0iI2ZmZiIKICAgICAgZD0iTTEwLjc0NCAzQzguODkgMyA3LjM4NCA0LjUyNSA3LjM4NCA2LjR2LjIyaC0uMDEyYy0xLjk5NyAwLTMuNjIyIDEuNjAyLTMuNjIyIDMuNTY4bC4wMDEgNy4wMmMwIDEuNzcgMS41MTIgMy41MTUgMy4xMTIgNS4zNjEuNzIuODMgMS45MTkgMi4yMTYgMi4wMzQgMi43MzF2MS41MjJoMTMuNDQydi0xLjU1NGMwLS41OS42MTgtMS43NyAxLjE2My0yLjgxLjkzOC0xLjc4OSAxLjk5OC0zLjgxNSAxLjk5OC01Ljk5MSAwLTMuMjU4LS4wMS02LjI0OC0uMDEtNi4yNDggMC0xLjY5Ni0xLjM5LTMuMDgtMy4xLTMuMDgtLjIwMyAwLS40LjAyLS41OTIuMDU3YTMuNjUgMy42NSAwIDAgMC0zLjAzMy0xLjYwN2MtLjM2NyAwLS43Mi4wNTMtMS4wNTUuMTUzYTMuNjM2IDMuNjM2IDAgMCAwLTMuMDktMS43MDVjLS40NDQgMC0uODcuMDgtMS4yNjQuMjI1QTMuMzQ1IDMuMzQ1IDAgMCAwIDEwLjc0NCAzWiIKICAgIC8+CiAgICA8cGF0aAogICAgICBmaWxsPSIjMDAwIgogICAgICBkPSJNMTAuNzQ0IDQuNTU0YzEgMCAxLjgwOC44MjYgMS44MDggMS44NDV2MS4xOTdjMC0xLjEwOS45MjctMi4wMDggMi4wNjgtMi4wMDggMS4xNDMgMCAyLjA2OC45IDIuMDY4IDIuMDA4djEuNTUyYzAtMS4xMS45My0yLjAwOCAyLjA3Ny0yLjAwOCAxLjE0NyAwIDIuMDc2Ljg5OSAyLjA3NiAyLjAwOHYxLjA2OEExLjU0IDEuNTQgMCAwIDEgMjIuMzkgOC42OWMuODU2IDAgMS41NDguNjg0IDEuNTQ4IDEuNTMgMCAwIC4wMSAyLjk4OC4wMSA2LjI0NCAwIDMuMjU3LTMuMTYxIDYuNjM2LTMuMTYxIDguODAySDEwLjQ1YzAtMS45NC01LjE0Ni01Ljc3My01LjE0Ni04LjA2MXYtNy4wMmMwLTEuMTEyLjkyNi0yLjAxNCAyLjA3LTIuMDE1djQuMDUxYzAgLjM0Mi4zNS42Mi43ODEuNjIuNDMyIDAgLjc4Mi0uMjc4Ljc4Mi0uNjJWNi40YzAtMS4wMi44MDktMS44NDUgMS44MDctMS44NDVabTAtMS41NTRDOC44OSAzIDcuMzg0IDQuNTI1IDcuMzg0IDYuNHYuMjJoLS4wMTJjLTEuOTk3IDAtMy42MjIgMS42MDItMy42MjIgMy41NjhsLjAwMSA3LjAyYzAgMS43NyAxLjUxMiAzLjUxNSAzLjExMiA1LjM2MS43Mi44MyAxLjkxOSAyLjIxNiAyLjAzNCAyLjczMXYxLjUyMmgxMy40NDJ2LTEuNTU0YzAtLjU5LjYxOC0xLjc3IDEuMTYzLTIuODEuOTM4LTEuNzg5IDEuOTk4LTMuODE1IDEuOTk4LTUuOTkxIDAtMy4yNTgtLjAxLTYuMjQ4LS4wMS02LjI0OCAwLTEuNjk2LTEuMzktMy4wOC0zLjEtMy4wOC0uMjAzIDAtLjQuMDItLjU5Mi4wNTdhMy42NSAzLjY1IDAgMCAwLTMuMDMzLTEuNjA3Yy0uMzY3IDAtLjcyLjA1My0xLjA1NS4xNTNhMy42MzYgMy42MzYgMCAwIDAtMy4wOS0xLjcwNWMtLjQ0NCAwLS44Ny4wOC0xLjI2NC4yMjVBMy4zNDUgMy4zNDUgMCAwIDAgMTAuNzQ0IDNaIgogICAgLz4KICA8L3N2Zz4='),\n      auto\n    " }
	};
}, "");
function mD() {
	var e = Z(Gg), t = (0, B.useState)(!1), n = R(t, 2), r = n[0], i = n[1], a;
	try {
		a = nt.getKetcher(e);
	} catch (t) {
		tt.error(`Failed to get ketcher instance with id ${e}`, t);
	}
	var o = (0, B.useCallback)(function() {
		return i(!0);
	}, [i]), s = (0, B.useCallback)(function() {
		return i(!1);
	}, [i]);
	return (0, B.useEffect)(function() {
		var e, t, n;
		return (e = a) == null || e.eventBus.addListener(it.LOADING, o), (t = a) == null || t.eventBus.addListener(it.SUCCESS, s), (n = a) == null || n.eventBus.addListener(it.FAILURE, s), function() {
			var e, t, n;
			(e = a) == null || e.eventBus.removeListener(it.LOADING, o), (t = a) == null || t.eventBus.removeListener(it.SUCCESS, s), (n = a) == null || n.eventBus.removeListener(it.FAILURE, s);
		};
	}, [
		a?.eventBus,
		s,
		o
	]), r;
}
function hD(e, t) {
	var n = Object.keys(e);
	if (Object.getOwnPropertySymbols) {
		var r = Object.getOwnPropertySymbols(e);
		t && (r = r.filter(function(t) {
			return Object.getOwnPropertyDescriptor(e, t).enumerable;
		})), n.push.apply(n, r);
	}
	return n;
}
function gD(e) {
	for (var t = 1; t < arguments.length; t++) {
		var n = arguments[t] == null ? {} : arguments[t];
		t % 2 ? hD(Object(n), !0).forEach(function(t) {
			I(e, t, n[t]);
		}) : Object.getOwnPropertyDescriptors ? Object.defineProperties(e, Object.getOwnPropertyDescriptors(n)) : hD(Object(n)).forEach(function(t) {
			Object.defineProperty(e, t, Object.getOwnPropertyDescriptor(n, t));
		});
	}
	return e;
}
function _D(e, t) {
	var n = typeof Symbol < "u" && e[Symbol.iterator] || e["@@iterator"];
	if (!n) {
		if (Array.isArray(e) || (n = vD(e)) || t && e && typeof e.length == "number") {
			n && (e = n);
			var r = 0, i = function() {};
			return {
				s: i,
				n: function() {
					return r >= e.length ? { done: !0 } : {
						done: !1,
						value: e[r++]
					};
				},
				e: function(e) {
					throw e;
				},
				f: i
			};
		}
		throw TypeError("Invalid attempt to iterate non-iterable instance.\nIn order to be iterable, non-array objects must have a [Symbol.iterator]() method.");
	}
	var a, o = !0, s = !1;
	return {
		s: function() {
			n = n.call(e);
		},
		n: function() {
			var e = n.next();
			return o = e.done, e;
		},
		e: function(e) {
			s = !0, a = e;
		},
		f: function() {
			try {
				o || n.return == null || n.return();
			} finally {
				if (s) throw a;
			}
		}
	};
}
function vD(e, t) {
	if (e) {
		if (typeof e == "string") return yD(e, t);
		var n = {}.toString.call(e).slice(8, -1);
		return n === "Object" && e.constructor && (n = e.constructor.name), n === "Map" || n === "Set" ? Array.from(e) : n === "Arguments" || /^(?:Ui|I)nt(?:8|16|32)(?:Clamped)?Array$/.test(n) ? yD(e, t) : void 0;
	}
}
function yD(e, t) {
	(t == null || t > e.length) && (t = e.length);
	for (var n = 0, r = Array(t); n < t; n++) r[n] = e[n];
	return r;
}
function bD() {
	var e = X(), t = Z(K), n = Z(X_);
	(0, B.useEffect)(function() {
		if (t) {
			var r = t.monomersLibrary, i = n.length ? n : t.defaultRnaPresetsLibraryItems, a = L(gx(r, i, !0)), o = gv(), s = [], c = a.map(function(e) {
				return e.name;
			});
			if (o) {
				var l = _D(o), u;
				try {
					for (l.s(); !(u = l.n()).done;) {
						for (var d = u.value, f = 0, p = d.name; c.includes(p);) f++, p = `${d.name}${"_Copy".repeat(f)}`;
						p !== d.name && vv(gD(gD({}, d), {}, { name: p }));
					}
				} catch (e) {
					l.e(e);
				} finally {
					l.f();
				}
				o = gv(), s = gx(r, o);
			}
			return e(N_(r)), e(F_(null)), e(_b(a)), o && e(vb(s)), e(Sb()), function() {
				e(N_([])), e(Cb());
			};
		}
	}, [t, n]);
}
function xD() {
	(0, B.useEffect)(function() {
		var e = function(e) {
			if (!e.defaultPrevented) {
				var t = e.target;
				if (!(t && (t.tagName === "INPUT" || t.tagName === "TEXTAREA" || t.isContentEditable || t.closest("[contenteditable=\"true\"]"))) && (e.key === "?" || e.key === "/" && e.shiftKey) && !e.repeat) {
					var n, r;
					e.preventDefault(), (n = window.open("https://github.com/epam/ketcher/blob/master/documentation/help.md#ketcher-macromolecules-mode", "_blank")) == null || (r = n.focus) == null || r.call(n);
				}
			}
		};
		return window.addEventListener("keydown", e), function() {
			return window.removeEventListener("keydown", e);
		};
	}, []);
}
var SD = z("div", { target: "ex562360" })({
	name: "1vtgpt7",
	styles: "position:absolute;top:0;left:0;height:100%;width:100%;display:flex;justify-content:center;align-items:center"
}), CD = function() {
	return U(SD, { children: U(pw, {}) });
}, wD = function(e) {
	e.requestFullscreen ? e.requestFullscreen() : e.msRequestFullscreen ? e.msRequestFullscreen() : e.mozRequestFullScreen ? e.mozRequestFullScreen() : e.webkitRequestFullscreen && e.webkitRequestFullscreen();
}, TD = function() {
	document.exitFullscreen ? document.exitFullscreen() : document.msExitFullscreen ? document.msExitFullscreen() : document.mozCancelFullScreen ? document.mozCancelFullScreen() : document.webkitExitFullscreen && document.webkitExitFullscreen();
}, ED = function() {
	return !!(document.fullscreenElement || document.mozFullScreenElement || document.webkitFullscreenElement || document.msFullscreenElement);
}, DD = z("div", { target: "e1yct69a0" })({
	name: "14ocoqf",
	styles: "display:flex;& svg:first-of-type{display:flex;justify-content:center;align-items:center;width:24px;height:24px;padding:2px;border-radius:4px;}"
}), OD = function(e) {
	var t = (0, B.useState)(ED), n = R(t, 2), r = n[0], i = n[1];
	return (0, B.useEffect)(function() {
		var e = function() {
			return i(ED());
		};
		return document.addEventListener("fullscreenchange", e), document.addEventListener("webkitfullscreenchange", e), document.addEventListener("mozfullscreenchange", e), document.addEventListener("MSFullscreenChange", e), function() {
			document.removeEventListener("fullscreenchange", e), document.removeEventListener("webkitfullscreenchange", e), document.removeEventListener("mozfullscreenchange", e), document.removeEventListener("MSFullscreenChange", e);
		};
	}, []), U(DD, {
		className: e.className,
		children: U(oe, {
			onClick: function() {
				var e = It();
				ED() ? TD() : wD(e);
			},
			iconName: r ? "fullscreen-exit" : "fullscreen-enter",
			testId: "fullscreen-mode-button"
		})
	});
}, kD = function() {
	return B.useContext(xx);
}, AD = z(oe, { target: "e1erwxoo0" })({
	name: "1y95nj0",
	styles: "margin:2px;outline:none"
});
function jD() {
	var e;
	(e = document.activeElement) == null || e.blur();
}
var MD = z(Fn, { target: "e1ann9o40" })({
	name: "2gmlyg",
	styles: "display:flex;justify-content:space-between;font-weight:400;font-size:12px;line-height:14px;padding:7px 8px;text-transform:none;color:#333333;width:max-content"
}), ND = function(e) {
	var t = e.itemId, n = e.title, r = n === void 0 ? "" : n, i = e.disabled, a = e.testId, o = e.onClick, s = e.type, c = s === void 0 ? "icon-button" : s, l = kD(), u = l.isActive, d = l.activate, f = (0, B.useCallback)(function() {
		d(t), jD(), o && o();
	}, [d, t]), p = u(t);
	return U(H, { children: c === "icon-button" ? U(AD, {
		title: r,
		className: t + (p ? " active" : ""),
		isActive: p,
		onClick: f,
		iconName: t,
		testId: a,
		disabled: i
	}) : U(MD, {
		title: r,
		onClick: f,
		disabled: i,
		"data-testid": a,
		children: r
	}) });
}, PD = z(P, {
	shouldForwardProp: function(e) {
		return e !== "isActive";
	},
	target: "e13kdqxv4"
})("position:absolute;height:7px;width:7px;right:3px;bottom:3px;cursor:pointer;path{fill:", function(e) {
	return e.isActive ? "white" : void 0;
}, ";}"), FD = z("div", { target: "e13kdqxv3" })({
	name: "k5saax",
	styles: "display:flex;position:relative;align-items:center;&:active{.dropdown{fill:white;}}"
}), ID = z("div", { target: "e13kdqxv2" })("display:flex;border-radius:4px;flex-direction:", function(e) {
	return e.isVertical ? "column" : "row";
}, ";z-index:", function(e) {
	return e.theme.ketcher.zIndex.overlay;
}, ";background-color:white;padding:2px;width:", function(e) {
	var t = e.isVertical, n = e.isAutoSize;
	return t && !n ? "38px" : "auto";
}, ";height:", function(e) {
	var t = e.isVertical, n = e.isAutoSize;
	return t || n ? "auto" : "38px";
}, ";"), LD = z(ae, { target: "e13kdqxv1" })("position:absolute;z-index:", function(e) {
	return e.theme.ketcher.zIndex.overlay;
}, ";"), RD = z("div", { target: "e13kdqxv0" })({
	name: "a1qh1t",
	styles: "display:flex;align-items:center;position:relative;width:32px;height:32px;padding:0;justify-content:center;border-radius:2px"
});
function zD(e, t) {
	var n = Object.keys(e);
	if (Object.getOwnPropertySymbols) {
		var r = Object.getOwnPropertySymbols(e);
		t && (r = r.filter(function(t) {
			return Object.getOwnPropertyDescriptor(e, t).enumerable;
		})), n.push.apply(n, r);
	}
	return n;
}
function BD(e) {
	for (var t = 1; t < arguments.length; t++) {
		var n = arguments[t] == null ? {} : arguments[t];
		t % 2 ? zD(Object(n), !0).forEach(function(t) {
			I(e, t, n[t]);
		}) : Object.getOwnPropertyDescriptors ? Object.defineProperties(e, Object.getOwnPropertyDescriptors(n)) : zD(Object(n)).forEach(function(t) {
			Object.defineProperty(e, t, Object.getOwnPropertyDescriptor(n, t));
		});
	}
	return e;
}
var VD = function(e) {
	var t = e.children, n = e.vertical, r = n !== void 0 && n, i = e.autoSize, a = i !== void 0 && i, o = e.disabled, s = o !== void 0 && o, c = e.needOpenByMenuItemClick, l = c !== void 0 && c, u = e.testId, d = e.layoutModeButton, f = d !== void 0 && d, p = e.generalTitle, m = e.activeItem, h = e.subMenuId, g = X(), _ = (0, B.useRef)(null), v = (0, B.useState)(!1), y = R(v, 2), x = y[0], S = y[1], C = kD().isActive, w = jn([
		_,
		x,
		r,
		he
	]), T = R(w, 1)[0], E = Z(s_(h)), D = h ? E : null, O = function() {
		s || S(function(e) {
			return !e;
		});
	}, k = function() {
		x && S(!1);
	}, A = B.Children.map(t, function(e) {
		return e.type === ND ? e : null;
	}), j = A.map(function(e) {
		return e.props.itemId;
	}).filter(function(e) {
		return e;
	}), ee = j.filter(function(e) {
		return C(e);
	})[0];
	(0, B.useEffect)(function() {
		h && ee && ee !== D && g(Hg({
			groupName: h,
			activeItemName: ee
		}));
	}, [
		g,
		h,
		ee,
		D
	]);
	var te = m ?? (ee || D || j[0]), M = A.find(function(e) {
		return e.props.itemId === te;
	}), ne = M?.props.testId, re = p ?? M?.props.title, N = document.querySelector(he);
	return U(FD, {
		"data-testid": u,
		"data-is-selected": C(te) ? "true" : "false",
		ref: _,
		children: W(H, { children: [W(RD, { children: [U(ND, {
			disabled: s,
			itemId: te,
			title: re,
			testId: ne,
			onClick: l ? O : px
		}), x || U(PD, {
			className: "dropdown",
			name: "dropdown",
			onClick: O,
			isActive: C(te),
			dataTestId: "dropdown-expand"
		})] }), N && (0, Es.createPortal)(U(LD, {
			in: x,
			timeout: 0,
			style: BD({}, T),
			unmountOnExit: !0,
			onClick: k,
			children: U(b, {
				onClickAway: k,
				children: U(ID, {
					isVertical: r,
					isAutoSize: a,
					islayoutModeButton: f,
					"data-testid": "multi-tool-dropdown",
					children: A.map(function(e) {
						return B.cloneElement(e, { key: e.props.itemId });
					})
				})
			})
		}), N)] })
	});
}, HD = z("div", { target: "e1fh0ozy3" })(function(e) {
	var t = e.theme, n = e.isHorizontal;
	return {
		backgroundColor: t.ketcher.color.background.primary,
		borderRadius: "4px",
		display: "flex",
		flexDirection: n ? "row" : "column",
		zIndex: t.ketcher.zIndex.toolbar
	};
}, ""), UD = z("hr", { target: "e1fh0ozy2" })("width:18px;margin:6px 0;align-self:center;border-width:thin 0px 0px 0px;border-style:solid;border-color:", function(e) {
	return e.theme.ketcher.color.divider;
}, ";"), WD = z("hr", { target: "e1fh0ozy1" })("height:18px;margin:0px 6px;align-self:center;border-width:0px thin 0px 0px;border-style:solid;border-color:", function(e) {
	return e.theme.ketcher.color.divider;
}, ";"), GD = z("div", { target: "e1fh0ozy0" })(function(e) {
	var t = e.theme, n = e.isHorizontal;
	return {
		display: "flex",
		flexDirection: n ? "row" : "column",
		flexWrap: "nowrap",
		alignItems: "center",
		backgroundColor: t.ketcher.color.background.primary,
		borderRadius: "2px",
		width: n ? void 0 : "32px",
		marginBottom: n ? void 0 : "8px",
		"> :last-child": n ? void 0 : { marginBottom: 0 }
	};
}, ""), KD = function(e) {
	var t = e.children, n = e.divider, r = n !== void 0 && n, i = e.isHorizontal;
	return W(H, { children: [U(GD, {
		isHorizontal: i,
		children: B.Children.map(t, function(e) {
			return e;
		})
	}), r && U(i ? WD : UD, {})] });
}, $ = function(e) {
	var t = e.children, n = e.onItemClick, r = e.activeMenuItems, i = e.testId, a = e.isHorizontal, o = B.useMemo(function() {
		return {
			isActive: function(e) {
				return r ? r.includes(e) : !1;
			},
			activate: function(e) {
				n(e);
			}
		};
	}, [r, n]), s = B.Children.map(t, function(e) {
		return e && e.type === KD ? e : null;
	});
	return U(xx.Provider, {
		value: o,
		children: U(HD, {
			"data-testid": i,
			isHorizontal: a,
			children: s
		})
	});
};
$.Group = KD, $.Item = ND, $.Submenu = VD;
var qD = function() {
	var e = Z(K), t = yx(), n = (0, B.useState)(t), r = R(n, 2), i = r[0], a = r[1], o = Z(Kg), s = (0, B.useMemo)(function() {
		return {
			isActive: function(e) {
				return i === e;
			},
			activate: function(t) {
				t !== i && (a(t), e?.events.selectMode.dispatch(t), e?.events.layoutModeChange.dispatch(t));
			}
		};
	}, [i, e]);
	return (0, B.useEffect)(function() {
		a(t);
	}, [t]), U(xx.Provider, {
		value: s,
		children: W($.Submenu, {
			disabled: o,
			testId: "layout-mode",
			vertical: !0,
			needOpenByMenuItemClick: !0,
			layoutModeButton: !0,
			children: [
				U($.Item, {
					itemId: "sequence-layout-mode",
					testId: "sequence-layout-mode",
					title: "Switch to sequence layout mode"
				}),
				U($.Item, {
					itemId: "snake-layout-mode",
					testId: "snake-layout-mode",
					title: "Switch to snake layout mode"
				}),
				U($.Item, {
					itemId: "flex-layout-mode",
					testId: "flex-layout-mode",
					title: "Switch to flex layout mode"
				})
			]
		})
	});
};
function JD(e, t) {
	var n = typeof Symbol < "u" && e[Symbol.iterator] || e["@@iterator"];
	if (!n) {
		if (Array.isArray(e) || (n = YD(e)) || t && e && typeof e.length == "number") {
			n && (e = n);
			var r = 0, i = function() {};
			return {
				s: i,
				n: function() {
					return r >= e.length ? { done: !0 } : {
						done: !1,
						value: e[r++]
					};
				},
				e: function(e) {
					throw e;
				},
				f: i
			};
		}
		throw TypeError("Invalid attempt to iterate non-iterable instance.\nIn order to be iterable, non-array objects must have a [Symbol.iterator]() method.");
	}
	var a, o = !0, s = !1;
	return {
		s: function() {
			n = n.call(e);
		},
		n: function() {
			var e = n.next();
			return o = e.done, e;
		},
		e: function(e) {
			s = !0, a = e;
		},
		f: function() {
			try {
				o || n.return == null || n.return();
			} finally {
				if (s) throw a;
			}
		}
	};
}
function YD(e, t) {
	if (e) {
		if (typeof e == "string") return XD(e, t);
		var n = {}.toString.call(e).slice(8, -1);
		return n === "Object" && e.constructor && (n = e.constructor.name), n === "Map" || n === "Set" ? Array.from(e) : n === "Arguments" || /^(?:Ui|I)nt(?:8|16|32)(?:Clamped)?Array$/.test(n) ? XD(e, t) : void 0;
	}
}
function XD(e, t) {
	(t == null || t > e.length) && (t = e.length);
	for (var n = 0, r = Array(t); n < t; n++) r[n] = e[n];
	return r;
}
var ZD = function(e) {
	var t = [], n = JD(e), r;
	try {
		for (n.s(); !(r = n.n()).done;) {
			var i = r.value, a = i.node, o = i.nodeIndexOverall, s = i.isNucleosideConnectedAndSelectedWithPhosphate, c = i.hasR1Connection, l = !!i.twoStrandedNode?.antisenseNode;
			if (a instanceof An) {
				var u, d, f;
				t.push({
					type: Ae.Nucleotide,
					baseLabel: a == null || (u = a.rnaBase) == null ? void 0 : u.label,
					sugarLabel: a == null || (d = a.sugar) == null ? void 0 : d.label,
					phosphateLabel: a == null || (f = a.phosphate) == null ? void 0 : f.label,
					rnaBaseMonomerItem: a.rnaBase instanceof mn ? a.rnaBase.variantMonomerItem : a.rnaBase.monomerItem,
					hasR1Connection: c,
					nodeIndexOverall: o,
					hasAntisense: l
				});
			} else if (a instanceof Dt) {
				var p, m;
				t.push({
					type: Ae.Nucleoside,
					baseLabel: a == null || (p = a.rnaBase) == null ? void 0 : p.label,
					sugarLabel: a == null || (m = a.sugar) == null ? void 0 : m.label,
					rnaBaseMonomerItem: a.rnaBase instanceof mn ? a.rnaBase.variantMonomerItem : a.rnaBase.monomerItem,
					isNucleosideConnectedAndSelectedWithPhosphate: s,
					hasR1Connection: c,
					nodeIndexOverall: o,
					hasAntisense: l
				});
			} else if (a?.monomer instanceof Bt) {
				var h;
				t.push({
					type: Ae.Phosphate,
					phosphateLabel: a == null || (h = a.monomer) == null ? void 0 : h.label,
					nodeIndexOverall: o,
					hasAntisense: l
				});
			}
		}
	} catch (e) {
		n.e(e);
	} finally {
		n.f();
	}
	return t;
};
function QD(e) {
	var t = e.node;
	return t instanceof An || t instanceof Dt || t?.monomer instanceof Bt;
}
var $D = function(e) {
	for (var t = "", n = e.length === 1 ? e[0] : ws.merge.apply(void 0, [{}].concat(L(e))), r = 0, i = [
		"sugarLabel",
		"baseLabel",
		"phosphateLabel"
	]; r < i.length; r++) {
		var a = i[r], o = (0, ws.get)(n, a, "");
		t += a === "baseLabel" ? `(${o})` : o;
	}
	return t;
}, eO = function(e) {
	if (e != null && e.length) {
		for (var t = (0, ws.flatten)(e), n = t.length, r = YS(t), i, a = !1, o = !0, s = !1, c = !0, l = ZD(t), u = 0; u < l.length; u++) {
			var d = l[u], f = l[u - 1], p = d.type === Ae.Nucleotide || d.type === Ae.Nucleoside, m = f?.isNucleosideConnectedAndSelectedWithPhosphate;
			p && (a = !0), p || m ? d.hasR1Connection && (c = !1) : (c = !1, o = !1), d.hasAntisense && (s = !0);
		}
		return n > r && (t.every(QD) || (o = !1)), i = n === 1 || r === 1 && o ? $D(l) : o ? `${r} nucleotides` : `${n} elements`, {
			title: i,
			selectedSequenceLabeledNodes: l,
			isSelectedOnlyNucleoelements: o,
			isSelectedAtLeastOneNucleoelement: a,
			isSequenceFirstsOnlyNucleoelementsSelected: c,
			hasAntisense: s
		};
	}
};
function tO() {
	return (arguments.length > 0 && arguments[0] !== void 0 ? arguments[0] : []).every(function(e) {
		return e.every(function(e) {
			return Kn(e.twoStrandedNode);
		});
	});
}
function nO(e) {
	return e?.monomers.some(function(e) {
		return e.hydrogenBonds.length !== 0;
	});
}
function rO(e, t) {
	var n = typeof Symbol < "u" && e[Symbol.iterator] || e["@@iterator"];
	if (!n) {
		if (Array.isArray(e) || (n = iO(e)) || t && e && typeof e.length == "number") {
			n && (e = n);
			var r = 0, i = function() {};
			return {
				s: i,
				n: function() {
					return r >= e.length ? { done: !0 } : {
						done: !1,
						value: e[r++]
					};
				},
				e: function(e) {
					throw e;
				},
				f: i
			};
		}
		throw TypeError("Invalid attempt to iterate non-iterable instance.\nIn order to be iterable, non-array objects must have a [Symbol.iterator]() method.");
	}
	var a, o = !0, s = !1;
	return {
		s: function() {
			n = n.call(e);
		},
		n: function() {
			var e = n.next();
			return o = e.done, e;
		},
		e: function(e) {
			s = !0, a = e;
		},
		f: function() {
			try {
				o || n.return == null || n.return();
			} finally {
				if (s) throw a;
			}
		}
	};
}
function iO(e, t) {
	if (e) {
		if (typeof e == "string") return aO(e, t);
		var n = {}.toString.call(e).slice(8, -1);
		return n === "Object" && e.constructor && (n = e.constructor.name), n === "Map" || n === "Set" ? Array.from(e) : n === "Arguments" || /^(?:Ui|I)nt(?:8|16|32)(?:Clamped)?Array$/.test(n) ? aO(e, t) : void 0;
	}
}
function aO(e, t) {
	(t == null || t > e.length) && (t = e.length);
	for (var n = 0, r = Array(t); n < t; n++) r[n] = e[n];
	return r;
}
var oO = function(e) {
	return e.map(function(e) {
		return e.monomerItem.props.MonomerNaturalAnalogCode;
	}).sort(function(e, t) {
		return e.localeCompare(t);
	}).join("");
}, sO = function(e) {
	var t = e.monomerItem;
	if (t.props.MonomerNaturalAnalogCode === "A" || t.props.MonomerNaturalAnalogCode === "C" || t.props.MonomerNaturalAnalogCode === "G" || t.props.MonomerNaturalAnalogCode === "T" || t.props.MonomerNaturalAnalogCode === "U") return !0;
	if (!e.monomerItem.isAmbiguous || e.subtype === se.MIXTURE) return !1;
	var n = [
		"ACGT",
		"ACGU",
		"CGT",
		"CGU",
		"AGT",
		"AGU",
		"ACT",
		"ACU",
		"GT",
		"GU",
		"AT",
		"AU",
		"CT",
		"CU",
		"AC",
		"AG",
		"CG",
		"ACG"
	], r = oO(e.monomers);
	return n.some(function(e) {
		return e === r;
	});
}, cO = function(e) {
	return e?.some(function(e) {
		var t = e instanceof ut && Ue(e);
		return e instanceof Lt && (e.hydrogenBonds.length > 0 || e.covalentBonds.length > 1) || p(e) && !sO(e) || t && (t.hydrogenBonds.length > 0 || t.covalentBonds.length > 1 || !sO(t));
	});
}, lO = function(e) {
	return e?.every(function(e) {
		return e instanceof ut ? e.label === c.SUGAR_DNA : !0;
	});
}, uO = function(e) {
	return e?.every(function(e) {
		return e instanceof ut ? e.label === c.SUGAR_RNA : !0;
	});
}, dO = function(e) {
	return e?.some(function(e) {
		return e instanceof Lt && O(e) || qt(e) && Ue(e);
	});
}, fO = "aminoAcidModification-", pO = function(e) {
	var t = /* @__PURE__ */ new Set(), n = /* @__PURE__ */ new Set(), r = /* @__PURE__ */ new Map(), i = rn();
	e.forEach(function(e) {
		var t, n = e.monomerItem.props.MonomerNaturalAnalogCode;
		e instanceof Pn && n && (r.has(n) || r.set(n, []), (t = r.get(n)) == null || t.push(e));
	}), i?.monomersLibrary.forEach(function(e) {
		var i = r.get(e.props?.MonomerNaturalAnalogCode);
		if (e.props && i) {
			var a = e.props.modificationTypes;
			a && a.forEach(function(r) {
				i.every(function(t) {
					return t.label === e.label;
				}) || (i.some(function(t) {
					return t.label !== e.label && ze(t, e);
				}) ? t.add(r) : n.add(r));
			});
		}
	});
	var a = L(t.values()).filter(function(e) {
		return !n.has(e);
	}).map(function(t) {
		var n = In(e, t, i.monomersLibrary);
		return {
			name: `${fO}${t}`,
			title: t,
			onMouseOver: function() {
				i.transientDrawingView.showModifyAminoAcidsView({ monomersToModify: L(n.keys()) }), i.transientDrawingView.update();
			},
			onMouseOut: function() {
				i.transientDrawingView.hideModifyAminoAcidsView(), i.transientDrawingView.update();
			}
		};
	});
	return a.sort(Jt), a;
}, mO = function(e, t) {
	var n, r, i = t == null || (n = t.target) == null ? void 0 : n.__data__, a = i == null || (r = i.node) == null ? void 0 : r.monomer, o = [];
	return e.length ? o = e : a && (o = [a]), o.filter(function(e) {
		return e instanceof Pn;
	});
}, hO = function(e) {
	if (e.length < 3) return !1;
	var t = new Set(e), n = /* @__PURE__ */ new Set(), r = /* @__PURE__ */ new Set(), i = function(e) {
		var n = [];
		return e.forEachBond(function(r) {
			if (!(r instanceof we)) {
				var i = r.firstMonomer, a = r.secondMonomer;
				if (i && a) {
					var o = r.getAnotherMonomer(e);
					o && t.has(o) && n.push(o);
				}
			}
		}), n;
	}, a = function e(t, a) {
		n.add(t), r.add(t);
		var o = rO(i(t)), s;
		try {
			for (o.s(); !(s = o.n()).done;) {
				var c = s.value;
				if (c !== a && (r.has(c) || !n.has(c) && e(c, t))) return !0;
			}
		} catch (e) {
			o.e(e);
		} finally {
			o.f();
		}
		return r.delete(t), !1;
	}, o = rO(e), s;
	try {
		for (o.s(); !(s = o.n()).done;) {
			var c = s.value;
			if (!n.has(c) && a(c, null)) return !0;
		}
	} catch (e) {
		o.e(e);
	} finally {
		o.f();
	}
	return !1;
}, gO;
(function(e) {
	e.title = "sequence_menu_title", e.createRnaAntisenseStrand = "create_antisense_rna_chain", e.createDnaAntisenseStrand = "create_antisense_dna_chain", e.modifyInRnaBuilder = "modify_in_rna_builder", e.modifyAminoAcids = "modify_amino_acids", e.establishHydrogenBond = "establish_hydrogen_bond", e.deleteHydrogenBond = "delete_hydrogen_bond", e.editSequence = "edit_sequence", e.startNewSequence = "start_new_sequence", e.copy = "copy", e.paste = "paste", e.delete = "delete";
})(gO ||= {});
var _O = function(e) {
	var t, n = e.selections, r = e.contextMenuEvent, i = Z(K), a = X(), o = eO(n), s = (n == null || (t = n.flat()) == null ? void 0 : t.flatMap(function(e) {
		return e.node.monomers;
	})) || [], c = mO(s, r), l = Z(Kg), u = yx() === "sequence-layout-mode", d = pO(c), f = n?.some(function(e) {
		return e.some(function(e) {
			return nO(e.node);
		});
	}) ?? !1, p = s?.length > 0 && dO(s), m = !tO(n) || f, h = [
		{
			name: gO.title,
			title: o?.title,
			isMenuTitle: !0,
			disabled: !0,
			hidden: function(e) {
				var t = e.props;
				return !(t != null && t.sequenceItemRenderer) || !(o != null && o.isSelectedAtLeastOneNucleoelement);
			}
		},
		{
			name: gO.copy,
			title: "Copy",
			icon: U(P, { name: "copyMenu" }),
			disabled: s?.length === 0
		},
		{
			name: gO.paste,
			title: "Paste",
			icon: U(P, { name: "pasteNavBar" }),
			disabled: !1,
			separator: !0
		},
		{
			name: gO.editSequence,
			title: "Edit sequence",
			disabled: !1,
			hidden: function(e) {
				var t = e.props;
				return !(t != null && t.sequenceItemRenderer);
			}
		},
		{
			name: gO.startNewSequence,
			title: "Start new sequence",
			disabled: !1,
			separator: p || m
		},
		{
			name: gO.createRnaAntisenseStrand,
			title: "Create RNA antisense strand",
			disabled: cO(s),
			hidden: function() {
				return !s || !dO(s);
			}
		},
		{
			name: gO.createDnaAntisenseStrand,
			title: "Create DNA antisense strand",
			disabled: cO(s),
			hidden: function() {
				return !s || !dO(s);
			}
		},
		{
			name: gO.establishHydrogenBond,
			title: "Establish Hydrogen Bonds",
			disabled: function(e) {
				var t, r = e.props;
				return n?.length === 0 ? Kn(r == null || (t = r.sequenceItemRenderer) == null ? void 0 : t.twoStrandedNode) : tO(n);
			},
			hidden: function(e) {
				var t = e.props;
				return !(t != null && t.sequenceItemRenderer);
			}
		},
		{
			name: gO.deleteHydrogenBond,
			title: "Remove hydrogen bonds",
			disabled: function(e) {
				var t, r = e.props;
				return n?.length === 0 ? !nO(r == null || (t = r.sequenceItemRenderer) == null ? void 0 : t.node) : !(n != null && n.some(function(e) {
					return e.some(function(e) {
						return nO(e.node);
					});
				}));
			},
			hidden: function(e) {
				var t = e.props;
				return !(t != null && t.sequenceItemRenderer);
			}
		},
		{
			name: gO.modifyInRnaBuilder,
			title: "Modify in RNA Builder...",
			disabled: !(o != null && o.isSelectedOnlyNucleoelements) || o.hasAntisense,
			hidden: function(e) {
				var t = e.props;
				return !(t != null && t.sequenceItemRenderer) || !(o != null && o.isSelectedAtLeastOneNucleoelement);
			}
		},
		{
			name: gO.modifyAminoAcids,
			title: "Modify amino acids",
			disabled: !1,
			hidden: !d.length,
			subMenuItems: d,
			separator: !0
		},
		{
			name: gO.delete,
			title: "Delete",
			disabled: s?.length === 0,
			icon: U(P, { name: "deleteMenu" })
		}
	], g = function(e) {
		var t, r = e.id, s = e.props;
		if (i) switch (!0) {
			case r === gO.modifyInRnaBuilder:
				i.events.turnOnSequenceEditInRNABuilderMode.dispatch(), a(R_(S_.RNA)), a(pb(!0)), a(nb({})), a(ob(null)), o != null && (t = o.selectedSequenceLabeledNodes) != null && t.length && o != null && o.title && (a(ib(o?.title)), a(rb(o?.selectedSequenceLabeledNodes)), a(ab(o?.isSequenceFirstsOnlyNucleoelementsSelected)));
				break;
			case r === gO.startNewSequence:
				i.events.startNewSequence.dispatch(s.sequenceItemRenderer);
				break;
			case r === gO.editSequence:
				i.events.editSequence.dispatch(s.sequenceItemRenderer);
				break;
			case r === gO.createRnaAntisenseStrand:
				i.events.createAntisenseChain.dispatch(!1);
				break;
			case r === gO.createDnaAntisenseStrand:
				i.events.createAntisenseChain.dispatch(!0);
				break;
			case r === gO.establishHydrogenBond:
				i.events.establishHydrogenBond.dispatch(s.sequenceItemRenderer);
				break;
			case r === gO.deleteHydrogenBond:
				var l = kt.sequenceViewModel.chainsCollection.monomerToChain, u = /* @__PURE__ */ new Map();
				(n != null && n.length ? n.reduce(function(e, t) {
					return [].concat(L(e), L(t));
				}, []).map(function(e) {
					return e.twoStrandedNode;
				}) : [s.sequenceItemRenderer?.twoStrandedNode]).forEach(function(e) {
					if (e.antisenseChain && e.antisenseNode && !(e.antisenseNode instanceof $t || e.antisenseNode instanceof un)) {
						u.has(e.antisenseChain) || u.set(e.antisenseChain, /* @__PURE__ */ new Set());
						var t = u.get(e.antisenseChain);
						if (!t) return;
						t.add(e);
					}
				});
				var d = !1;
				u.forEach(function(e, t) {
					var n = L(e.values())[0].chain, r = new Set(L(e.values()).map(function(e) {
						return e.antisenseNode;
					}));
					t.nodes.some(function(e) {
						return !r.has(e) && e.monomers.some(function(e) {
							return e.hydrogenBonds.some(function(t) {
								var r = t.getAnotherMonomer(e);
								return (r && l.get(r)) === n;
							});
						});
					}) || (d = !0);
				}), d ? i.events.openConfirmationDialog.dispatch({
					title: "Deletion of all Hydrogen Bonds",
					confirmationText: "Deleting all hydrogen bonds will cause the separation of two chains. Do you wish to proceed?",
					onConfirm: function() {
						i.events.deleteHydrogenBond.dispatch(s.sequenceItemRenderer);
					}
				}) : i.events.deleteHydrogenBond.dispatch(s.sequenceItemRenderer);
				break;
			case r?.startsWith(fO):
				var f = r?.replace(fO, "");
				i.events.modifyAminoAcids.dispatch({
					monomers: c,
					modificationType: f
				});
				break;
			case r === "copy":
				i.events.copySelectedStructure.dispatch();
				break;
			case r === "paste":
				i.events.pasteFromClipboard.dispatch();
				break;
			case r === "delete": i.events.deleteSelectedStructure.dispatch();
		}
	}, _ = document.querySelector(he);
	return _ && u && !l ? (0, Es.createPortal)(U(iS, {
		id: tS.FOR_SEQUENCE,
		handleMenuChange: g,
		menuItems: h
	}), _) : null;
}, vO = z("div", { target: "e1amohl43" })("display:flex;flex-direction:column;align-items:start;gap:8px;overflow:hidden;width:", function(e) {
	return e.isLongName ? "450px" : "345px";
}, ";height:345px;background:", function(e) {
	return e.theme.ketcher.color.background.primary;
}, ";border:", function(e) {
	return e.theme.ketcher.border.regular;
}, ";border-radius:", function(e) {
	return e.theme.ketcher.border.radius.regular;
}, ";box-shadow:", function(e) {
	return e.theme.ketcher.shadow.regular;
}, ";"), yO = z("p", { target: "e1amohl42" })("width:calc(100% - 16px);padding:8px;color:", function(e) {
	return e.theme.ketcher.color.text.primary;
}, ";background-color:#cceaee;font-size:", function(e) {
	return e.isLongName ? "8px" : e.theme.ketcher.font.size.regular;
}, ";font-weight:700;word-break:break-all;text-align:left;margin:0;white-space:pre-wrap;", function(e) {
	return e.isLongName && "\n    max-height: 200px;\n    overflow: hidden;\n    display: -webkit-box;\n    -webkit-line-clamp: 15;\n    -webkit-box-orient: vertical;\n  ";
}, ";"), bO = z(Ve, { target: "e1amohl41" })({
	name: "tqmz0h",
	styles: "flex:1 1 auto;min-height:80px;width:100%;padding:0 8px"
}), xO = z("div", { target: "e1amohl40" })({
	name: "1i0z1wm",
	styles: "width:100%;display:flex;flex-shrink:0;gap:8px;padding:0 8px 4px"
}), SO = function(e) {
	var t = e.monomerCaps, n = e.attachmentPointsToBonds;
	return (0, B.useMemo)(function() {
		var e = [], r = [];
		return t && Object.keys(t).length > 0 ? (Object.entries(t).forEach(function(t) {
			var i = R(t, 2), a = i[0], o = i[1], s = !!n?.[a];
			s && r.push(a);
			var c = {
				id: a,
				label: eE(o),
				connected: s
			};
			e.push(c);
		}), {
			preparedAttachmentPointsData: e,
			connectedAttachmentPoints: r
		}) : (n && Object.keys(n).forEach(function(t) {
			var i = !!n[t];
			i && r.push(t), e.push({
				id: t,
				label: "",
				connected: i
			});
		}), {
			preparedAttachmentPointsData: e,
			connectedAttachmentPoints: r
		});
	}, [t, n]);
}, CO = function(e) {
	var t = e.idtAliases, n = e.attachmentPointsToBonds;
	return (0, B.useMemo)(function() {
		if (!t) return null;
		var e = t.base, r = t.modifications;
		if (!r) return vx(e);
		var i = r.endpoint5, a = r.internal, o = r.endpoint3;
		if (n) {
			var s = n.R1, c = n.R2, l = s != null, u = c != null;
			return vx(l && !u ? o ?? a : !l && u ? i ?? a : l && u ? a ?? i ?? o : i ?? a ?? o);
		}
		var d = Object.values(r).every(function(t) {
			return t.includes(e);
		});
		if (o && i && a && d) return vx(e);
		var f = {};
		return Object.values(r).forEach(function(e) {
			var t = vx(e) ?? "", n = [t.charAt(0), t.slice(1)], r = n[0], i = n[1];
			f[i] = f[i] ? [].concat(L(f[i]), [r]) : [r];
		}), Object.entries(f).map(function(e) {
			var t = R(e, 2), n = t[0];
			return `(${t[1].join(", ")})${n}`;
		}).join(", ");
	}, [t, n]);
}, wO = z("span", { target: "epjjwrk3" })("width:max-content;max-width:100%;display:flex;flex-direction:column;align-items:flex-start;font-size:", function(e) {
	return e.theme.ketcher.font.size.regular;
}, ";font-weight:500;line-height:normal;color:", function(e) {
	return e.theme.ketcher.color.text.lightgrey;
}, ";padding-left:", function(e) {
	return e.preset ? "0" : "8px";
}, ";border-left:", function(e) {
	return e.preset ? "none" : "1px solid #D9DCEA";
}, ";"), TO = z("p", { target: "epjjwrk2" })({
	name: "ti75j2",
	styles: "margin:0"
}), EO = z("span", { target: "epjjwrk1" })({
	name: "3myie7",
	styles: "color:#7c7c7c;margin-right:4px"
}), DO = z("span", { target: "epjjwrk0" })({
	name: "9ig07c",
	styles: "color:#585858;white-space:normal;overflow-wrap:anywhere;word-break:break-word"
}), OO = function(e) {
	return e.replace(/\[|\]/g, "");
};
function kO(e) {
	var t = e.idtAliasesText, n = e.axoLabsText, r = e.helmText, i = e.bilnText, a = e.modificationTypeText, o = e.preset, s = [].concat(L(t ? [{
		label: "IDT",
		text: t
	}] : []), L(n ? [{
		label: "AxoLabs",
		text: n
	}] : []), L(r ? [{
		label: "HELM",
		text: OO(r)
	}] : []), L(i ? [{
		label: "BILN",
		text: OO(i)
	}] : []), L(a ? [{
		label: "Modification type",
		text: a
	}] : []));
	return s.length ? U(wO, {
		preset: o,
		children: s.map(function(e) {
			return W(TO, { children: [W(EO, { children: [e.label, ":"] }), U(DO, { children: e.text })] }, e.label);
		})
	}) : null;
}
var AO = z("div", { target: "e112ss7f3" })({
	name: "1m2mukt",
	styles: "flex:1;display:flex;align-items:center;flex-wrap:wrap;gap:8px;font-size:12px;line-height:14px"
}), jO = z("div", { target: "e112ss7f2" })("display:flex;align-items:center;gap:2px;border-radius:4px;background-color:", function(e) {
	return e.connected ? "#E1E5EA" : "transparent";
}, ";padding:", function(e) {
	return e.connected ? "4px" : "0";
}, ";color:", function(e) {
	return e.connected ? "#8A8B8E" : "inherit";
}, ";"), MO = z("span", { target: "e112ss7f1" })({
	name: "f3vz0n",
	styles: "font-weight:500"
}), NO = z("span", { target: "e112ss7f0" })({
	name: "16ceglb",
	styles: "font-weight:600"
}), PO = function(e) {
	var t = e.preparedAttachmentPointsData;
	return t.length ? U(AO, { children: t.map(function(e) {
		var t = e.id, n = e.connected, r = e.label;
		return W(jO, {
			connected: n,
			children: [W(MO, { children: [t, !n && ":"] }), !n && U(NO, { children: r })]
		}, t);
	}) }) : null;
}, FO = function(e) {
	var t = e.className, n = Z(Ug), r = 100, i = n.monomer, a = n.attachmentPointsToBonds, o = i?.props.idtAliases, s = i?.props.aliasAxoLabs, c = i?.props.aliasHELM, l = i?.props.aliasBILN, u = i?.props.modificationTypes, d = SO({
		monomerCaps: i?.props.MonomerCaps,
		attachmentPointsToBonds: a
	}), f = d.preparedAttachmentPointsData, p = d.connectedAttachmentPoints, m = CO({
		idtAliases: o,
		attachmentPointsToBonds: a
	});
	if (!i) return null;
	var h = i.props.unresolved, g = h ? i.label : i.struct?.name || i.label, _ = m || s || c || l || u;
	return (i.struct || h) && W(vO, {
		className: t,
		isLongName: g.length > r,
		"data-testid": "polymer-library-preview",
		"data-idtaliases": m ?? void 0,
		"data-axolabs": s ?? void 0,
		"data-helm": c ?? void 0,
		"data-biln": l ?? void 0,
		"data-modificationtype": Tx(u),
		children: [
			g.length > 0 && U(yO, {
				"data-testid": "preview-tooltip-title",
				isLongName: g.length > 100,
				children: g
			}),
			h ? U(aE, {}) : U(bO, {
				struct: i.struct,
				options: {
					connectedMonomerAttachmentPoints: p,
					usageInMacromolecule: sn.MonomerPreview,
					labelInPreview: !0,
					needCache: !1
				}
			}),
			W(xO, { children: [U(PO, { preparedAttachmentPointsData: f }), _ && U(kO, {
				idtAliasesText: m ?? void 0,
				axoLabsText: s ?? void 0,
				helmText: c ?? void 0,
				bilnText: l ?? void 0,
				modificationTypeText: Array.isArray(u) ? u.join(", ") : u
			})] })
		]
	});
}, IO = z("div", { target: "ec5fs977" })("display:flex;flex-direction:column;align-items:center;gap:8px;padding:8px;background:", function(e) {
	return e.theme.ketcher.color.background.primary;
}, ";border:", function(e) {
	return e.theme.ketcher.border.regular;
}, ";border-radius:", function(e) {
	return e.theme.ketcher.border.radius.regular;
}, ";box-shadow:", function(e) {
	return e.theme.ketcher.shadow.regular;
}, ";"), LO = z("div", { target: "ec5fs976" })({
	name: "s5xdrg",
	styles: "display:flex;align-items:center"
}), RO = z("div", { target: "ec5fs975" })("font-size:", function(e) {
	return e.theme.ketcher.font.size.regular;
}, ";line-height:", function(e) {
	return e.theme.ketcher.font.size.regular;
}, ";font-weight:600;padding-right:2px;"), zO = z("div", { target: "ec5fs974" })("color:", function(e) {
	return e.theme.ketcher.color.text.lightgrey;
}, ";font-size:", function(e) {
	return e.theme.ketcher.font.size.regular;
}, ";font-weight:400;white-space:nowrap;"), BO = z("p", { target: "ec5fs973" })("color:", function(e) {
	return e.theme.ketcher.color.text.primary;
}, ";font-size:", function(e) {
	return e.theme.ketcher.font.size.regular;
}, ";font-weight:700;word-break:break-all;text-align:center;margin-top:0;margin-bottom:8px;"), VO = z(P, { target: "ec5fs972" })("height:14px;width:14px;margin-right:4px;color:", function(e) {
	return e.theme.ketcher.color.icon.grey;
}, ";stroke:", function(e) {
	return e.theme.ketcher.color.icon.grey;
}, ";"), HO = z(P, { target: "ec5fs971" })({
	name: "1j379ef",
	styles: "height:15px;width:15px;flex-shrink:0"
}), UO = z("span", { target: "ec5fs970" })({
	name: "1ag7b4g",
	styles: "display:inline-flex;align-items:center;margin-left:6px"
}), WO = function(e) {
	var t = e.presetName, n = e.position, r = e.idtAliases;
	return (0, B.useMemo)(function() {
		if (!t || !r) return null;
		if (t.includes("MOE")) {
			var e = r.base, i = r.modifications, a = vx(i?.endpoint5) ?? `5${e}`, o = vx(i?.internal) ?? `i${e}`, s = vx(i?.endpoint3) ?? `3${e}`;
			switch (n) {
				case vg.Library: return [
					a,
					o,
					s
				].every(function(t) {
					return t.includes(e);
				}) ? e : `${a}, ${o}`;
				case vg.ChainStart: return a;
				case vg.ChainMiddle: return o;
				case vg.ChainEnd: return s;
			}
		}
		return vx(r.base);
	}, [
		t,
		n,
		r
	]);
}, GO = function(e) {
	switch (e.props.MonomerClass) {
		case st.Sugar: return "sugar";
		case st.Base: return "base";
		case st.Phosphate: return "phosphate";
		default: return "chem";
	}
}, KO = 2, qO = z(function(e) {
	var t = e.className, n = Z(Ug), r = n.monomers, i = n.name, a = n.position, o = n.idtAliases, s = n.aliasAxoLabs, c = R(r, 2)[1], l = i ?? c?.props.Name, u = s ?? c?.props.aliasAxoLabs, d = WO({
		presetName: l,
		position: a,
		idtAliases: o
	}), f = d || u, p = n.phosphatePosition === "left" ? "preset-left-phosphate" : n.phosphatePosition === "right" ? "preset-right-phosphate" : void 0, m = n.phosphatePosition === "left" ? "Phosphate on the left (5')" : n.phosphatePosition === "right" ? "Phosphate on the right (3')" : void 0, h = function(e) {
		return `(${e.props.Name})`;
	};
	return W(IO, {
		className: t,
		style: { alignItems: "flex-start" },
		"data-testid": "polymer-library-preview",
		"data-idtaliases": d ?? void 0,
		"data-axolabs": u ?? void 0,
		children: [
			U(BO, {
				"data-testid": "preview-tooltip-title",
				children: l
			}),
			r.map(function(e, t) {
				return e ? W(LO, { children: [
					U(VO, { name: GO(e) }),
					U(RO, { children: e.label }),
					U(zO, { children: h(e) }),
					t === KO && p && U(UO, {
						title: m,
						"data-testid": "preset-preview-phosphate-position-icon",
						"data-phosphate-position": n.phosphatePosition,
						children: U(HO, { name: p })
					})
				] }, e.props.id ?? t) : null;
			}),
			f && U(kO, {
				preset: !0,
				idtAliasesText: d ?? void 0,
				axoLabsText: u
			})
		]
	});
}, { target: "e1wupxfd0" })(""), JO = z("div", { target: "envzkt90" })("display:flex;flex-direction:column;align-items:start;gap:8px;background:", function(e) {
	return e.theme.ketcher.color.background.primary;
}, ";border:", function(e) {
	return e.theme.ketcher.border.regular;
}, ";border-radius:", function(e) {
	return e.theme.ketcher.border.radius.regular;
}, ";box-shadow:", function(e) {
	return e.theme.ketcher.shadow.regular;
}, ";"), YO = z("div", { target: "e1m0yzrp2" })(function(e) {
	var t = e.connected, n = e.inBond, r = e.theme;
	return {
		display: "flex",
		flexDirection: "column",
		alignItems: "center",
		gap: "2px",
		color: n || !t ? r.ketcher.color.text.primary : "#B4B9D6"
	};
}, ""), XO = z("p", { target: "e1m0yzrp1" })(function(e) {
	return {
		margin: 0,
		fontSize: e.theme.ketcher.font.size.small,
		lineHeight: "12px"
	};
}, ""), ZO = z("p", { target: "e1m0yzrp0" })(function(e) {
	var t = e.inBond;
	return {
		margin: 0,
		padding: "4px",
		fontWeight: e.theme.ketcher.font.weight.bold,
		lineHeight: "14px",
		borderRadius: "4px",
		backgroundColor: t ? "#CDF1FC" : "transparent",
		minWidth: t ? "8px" : void 0,
		minHeight: t ? "14px" : void 0
	};
}, ""), QO = function(e) {
	var t = e.attachmentPoints, n = e.attachmentPointInBond;
	return U(H, { children: t.map(function(e) {
		var t = e.id === n;
		return W(YO, {
			connected: e.connected,
			inBond: t,
			children: [U(XO, { children: e.id }), (e.label || t) && U(ZO, {
				inBond: t,
				children: e.label
			})]
		}, e.id);
	}) });
}, $O = z(function(e) {
	var t = e.className, n = Z(Ug), r = n.polymerBond, i = n.style, a = (0, B.useMemo)(function() {
		return i ? z(JO, { target: "e18hk05c1" })("top:", i?.top ?? "", ";left:", i?.left ?? "", ";right:", i?.right ?? "", ";") : z(JO, { target: "e18hk05c2" })("");
	}, [i]), o = r.firstMonomer, s = r.secondMonomer, c = r.firstMonomerAttachmentPoint, l = r.secondMonomerAttachmentPoint, u = SO({
		monomerCaps: o.monomerCaps,
		attachmentPointsToBonds: o.attachmentPointsToBonds
	}), d = u.preparedAttachmentPointsData, f = u.connectedAttachmentPoints, p = SO({
		monomerCaps: s?.monomerCaps,
		attachmentPointsToBonds: s?.attachmentPointsToBonds
	}), m = p.preparedAttachmentPointsData, h = p.connectedAttachmentPoints;
	return !o || !s ? null : U(a, {
		className: t,
		"data-testid": "polymer-library-preview",
		children: U(gE, {
			firstMonomer: o,
			secondMonomer: s,
			firstMonomerOverview: U(cE, {
				monomer: o,
				usage: sn.BondPreview,
				connectedAttachmentPoints: f,
				selectedAttachmentPoint: c,
				attachmentPoints: U(QO, {
					attachmentPoints: d,
					attachmentPointInBond: c
				})
			}),
			secondMonomerOverview: U(cE, {
				monomer: s,
				usage: sn.BondPreview,
				connectedAttachmentPoints: h,
				selectedAttachmentPoint: l,
				attachmentPoints: U(QO, {
					attachmentPoints: m,
					attachmentPointInBond: l
				})
			})
		})
	});
}, { target: "e18hk05c0" })("width:", hn.widthForBond, "px;height:", hn.heightForBond, "px;");
function ek(e, t) {
	var n = Object.keys(e);
	if (Object.getOwnPropertySymbols) {
		var r = Object.getOwnPropertySymbols(e);
		t && (r = r.filter(function(t) {
			return Object.getOwnPropertyDescriptor(e, t).enumerable;
		})), n.push.apply(n, r);
	}
	return n;
}
function tk(e) {
	for (var t = 1; t < arguments.length; t++) {
		var n = arguments[t] == null ? {} : arguments[t];
		t % 2 ? ek(Object(n), !0).forEach(function(t) {
			I(e, t, n[t]);
		}) : Object.getOwnPropertyDescriptors ? Object.defineProperties(e, Object.getOwnPropertyDescriptors(n)) : ek(Object(n)).forEach(function(t) {
			Object.defineProperty(e, t, Object.getOwnPropertyDescriptor(n, t));
		});
	}
	return e;
}
var nk = z("div", { target: "e88xzqx0" })("display:inline-block;position:absolute;background:", function(e) {
	return e.theme.ketcher.color.background.primary;
}, ";z-index:", function(e) {
	return e.theme.ketcher.zIndex.overlay;
}, ";"), rk = function() {
	var e = Z(Ug), t = (0, B.useRef)(null), n = (0, B.useState)(!1), r = R(n, 2), i = r[0], a = r[1], o = dt(K);
	return (0, B.useEffect)(function() {
		if (t.current && !e.style) {
			if (e != null && e.type) {
				var n;
				t.current.setAttribute("style", ""), a(!0);
				var r = 5, s = t.current?.getBoundingClientRect(), c = s?.height || 0, l = s?.width || 0, u = (n = Ke.instance) == null || (n = n.canvasWrapper.node()) == null ? void 0 : n.getBoundingClientRect(), d = u?.top || 0, f = u?.bottom || 0, p = u?.left || 0, m = u?.right || 0, h = e.target?.getBoundingClientRect(), g = h?.top || 0, _ = h?.bottom || 0, v = h?.left || 0, y = h?.width || 0, b = v - y / 2, x = o?.ketcherRootElementBoundingClientRect, S = x?.x || 0, C = x?.y || 0, w = g - c - r - C, T = _ + r - C, E = v + y / 2 - l / 2 - S;
				if (g - c - r >= d || _ + c > f && _ > f / 2 ? t.current.style.top = `${w}px` : t.current.style.top = `${T}px`, b > l / 2 && b + l / 2 < m) t.current.style.left = `${E}px`;
				else if (b < l / 2) t.current.style.left = `${p}px`;
				else {
					var D = 10;
					t.current.style.left = `${m - l - D}px`;
				}
			} else i && (a(!1), t.current.setAttribute("style", ""));
		}
	}, [e]), e ? W(nk, {
		ref: t,
		style: tk({}, e?.style),
		children: [
			e.type === _g.Monomer && U(FO, {}),
			e.type === _g.Preset && U(qO, {}),
			e.type === _g.Bond && U($O, {}),
			e.type === _g.AmbiguousMonomer && U(f, { preview: e })
		]
	}) : null;
}, ik = function(e) {
	return e === Nt.RNA || e === Nt.DNA || e === Nt.PEPTIDE;
}, ak = function() {
	var e;
	try {
		e = w_.getItem(__);
	} catch (e) {
		return tt.error("sequenceTypeStorage.ts::getPersistedSequenceType", e), Nt.RNA;
	}
	return ik(e) ? e : Nt.RNA;
}, ok = function(e) {
	w_.setItem(__, e);
}, sk = z(Fn, { target: "e1brfei30" })(function(e) {
	var t = e.theme, n = e.variant;
	return {
		color: n === "outlined" ? t.ketcher.color.text.primary : t.ketcher.color.button.text.primary,
		boxShadow: "none",
		transition: "none",
		display: "flex",
		justifyContent: "center",
		alignItems: "center",
		cursor: "pointer",
		padding: "4px 8px",
		border: n === "outlined" ? t.ketcher.outline.small : "none",
		background: n === "outlined" ? t.ketcher.color.background.primary : t.ketcher.color.button.group.active,
		borderRadius: t.ketcher.border.radius.regular,
		textTransform: "none",
		fontSize: t.ketcher.font.size.regular,
		fontWeight: t.ketcher.font.weight.regular,
		":hover": {
			color: n === "outlined" ? t.ketcher.color.text.dark : t.ketcher.color.button.text.primary,
			background: n === "outlined" ? t.ketcher.color.background.primary : t.ketcher.color.button.group.hover,
			boxShadow: "none"
		},
		":disabled": {
			cursor: "auto",
			background: "#e1e5ea",
			outline: "none"
		}
	};
}, ""), ck = function() {
	var e = Z(K), t = (0, B.useState)(e?.events.changeSequenceTypeEnterMode), n = R(t, 2), r = n[0], i = n[1], a = (0, B.useState)(!1), o = R(a, 2), s = o[0], c = o[1], l = Z(Kg), u = yx(), d = !!l, f = X(), p = function(e) {
		c((en(e) === "object" ? e.mode : e) === "sequence-layout-mode");
	};
	(0, B.useEffect)(function() {
		var t = function(e) {
			f(R_(e === f_.PEPTIDE ? S_.PEPTIDES : S_.RNA)), i(e), ok(e);
		};
		return e?.events.selectMode.add(p), e?.events.changeSequenceTypeEnterMode.add(t), e?.events.changeSequenceTypeEnterMode.dispatch(ak()), function() {
			e?.events.selectMode.remove(p), e?.events.changeSequenceTypeEnterMode.remove(t);
		};
	}, [e]), (0, B.useEffect)(function() {
		p(u);
	}, [u]);
	var m = function(t) {
		e?.events.changeSequenceTypeEnterMode.dispatch(t);
	};
	return s ? U(lr, {
		sx: {
			mr: 1,
			ml: 1
		},
		children: W(_r, {
			disabled: d,
			children: [
				U(sk, {
					"data-testid": `${Nt.RNA}Btn`,
					title: "RNA (Ctrl+Alt+R)",
					variant: r === Nt.RNA ? "contained" : "outlined",
					onClick: function() {
						return m(Nt.RNA);
					},
					children: "RNA"
				}),
				U(sk, {
					"data-testid": `${Nt.DNA}Btn`,
					title: "DNA (Ctrl+Alt+D)",
					variant: r === Nt.DNA ? "contained" : "outlined",
					onClick: function() {
						return m(Nt.DNA);
					},
					children: "DNA"
				}),
				U(sk, {
					"data-testid": `${Nt.PEPTIDE}Btn`,
					title: "Peptides (Ctrl+Alt+P)",
					variant: r === Nt.PEPTIDE ? "contained" : "outlined",
					onClick: function() {
						return m(Nt.PEPTIDE);
					},
					children: "PEP"
				})
			]
		})
	}) : null;
}, lk = function() {
	var e = X(), t = Z(K), n = Z(t_), r = Z(n_), i = Z(r_), a = Z(i_);
	return function() {
		var o = dn(Ds.default.mark(function o(s) {
			var c, u, d, f, p, m, h, g, v, y, b, S;
			return Ds.default.wrap(function(o) {
				for (;;) switch (o.prev = o.next) {
					case 0:
						if (t && !s) {
							o.next = 2;
							break;
						}
						return o.abrupt("return");
					case 2:
						if (c = ce.getIndigo(), u = t.drawingEntitiesManager.filterSelection(), d = new l(), f = !u.hasDrawingEntities, p = u.hasDrawingEntities ? u : t.drawingEntitiesManager, m = Tn.fromMonomers(L(p.monomers.values())), h = m.firstNode?.monomer, g = !h || m.chains.reduce(function(e, t) {
							return e + t.monomers.length;
						}, 0) <= x(h).length, v = m.chains.length === 0 && L(p.monomers.values()).filter(function(e) {
							return e.monomerItem.props.isMicromoleculeFragment;
						}).length > 1, !(!p.hasDrawingEntities || !g || f && v)) {
							o.next = 14;
							break;
						}
						return e(Fg(void 0)), o.abrupt("return");
					case 14: return y = d.serialize(new _(), t.drawingEntitiesManager, void 0, !1, !0), o.next = 17, c.calculateMacromoleculeProperties({ struct: y }, {
						upc: i / Cg[n],
						nac: a / Cg[r]
					});
					case 17:
						b = o.sent;
						try {
							S = b.properties && JSON.parse(b.properties), Te(), e(Fg(S));
						} catch (t) {
							tt.error("Error during parsing macromolecule properties: ", t), e(Fg(void 0));
						}
					case 19:
					case "end": return o.stop();
				}
			}, o);
		}));
		return function(e) {
			return o.apply(this, arguments);
		};
	}();
}, uk = ["className"];
function dk(e, t) {
	var n = typeof Symbol < "u" && e[Symbol.iterator] || e["@@iterator"];
	if (!n) {
		if (Array.isArray(e) || (n = fk(e)) || t && e && typeof e.length == "number") {
			n && (e = n);
			var r = 0, i = function() {};
			return {
				s: i,
				n: function() {
					return r >= e.length ? { done: !0 } : {
						done: !1,
						value: e[r++]
					};
				},
				e: function(e) {
					throw e;
				},
				f: i
			};
		}
		throw TypeError("Invalid attempt to iterate non-iterable instance.\nIn order to be iterable, non-array objects must have a [Symbol.iterator]() method.");
	}
	var a, o = !0, s = !1;
	return {
		s: function() {
			n = n.call(e);
		},
		n: function() {
			var e = n.next();
			return o = e.done, e;
		},
		e: function(e) {
			s = !0, a = e;
		},
		f: function() {
			try {
				o || n.return == null || n.return();
			} finally {
				if (s) throw a;
			}
		}
	};
}
function fk(e, t) {
	if (e) {
		if (typeof e == "string") return pk(e, t);
		var n = {}.toString.call(e).slice(8, -1);
		return n === "Object" && e.constructor && (n = e.constructor.name), n === "Map" || n === "Set" ? Array.from(e) : n === "Arguments" || /^(?:Ui|I)nt(?:8|16|32)(?:Clamped)?Array$/.test(n) ? pk(e, t) : void 0;
	}
}
function pk(e, t) {
	(t == null || t > e.length) && (t = e.length);
	for (var n = 0, r = Array(t); n < t; n++) r[n] = e[n];
	return r;
}
function mk(e, t) {
	var n = Object.keys(e);
	if (Object.getOwnPropertySymbols) {
		var r = Object.getOwnPropertySymbols(e);
		t && (r = r.filter(function(t) {
			return Object.getOwnPropertyDescriptor(e, t).enumerable;
		})), n.push.apply(n, r);
	}
	return n;
}
function hk(e) {
	for (var t = 1; t < arguments.length; t++) {
		var n = arguments[t] == null ? {} : arguments[t];
		t % 2 ? mk(Object(n), !0).forEach(function(t) {
			I(e, t, n[t]);
		}) : Object.getOwnPropertyDescriptors ? Object.defineProperties(e, Object.getOwnPropertyDescriptors(n)) : mk(Object(n)).forEach(function(t) {
			Object.defineProperty(e, t, Object.getOwnPropertyDescriptor(n, t));
		});
	}
	return e;
}
var gk = "Other", _k = function(e, t) {
	var n, r = e == null || (n = e.monomerCount) == null ? void 0 : n[t];
	return r && Object.keys(r).length > 0;
}, vk = z("div", { target: "eifx56c30" })(function(e) {
	return {
		width: "100%",
		height: e.hasError ? "124px" : "177px",
		position: "relative",
		backgroundColor: "white",
		padding: "2px 0",
		borderRadius: "8px 8px",
		overflow: "hidden",
		boxShadow: "0px 2px 5px rgba(103, 104, 132, 0.15)"
	};
}, ""), yk = z("div", { target: "eifx56c29" })(function() {
	return { display: "flex" };
}, ""), bk = z("div", { target: "eifx56c28" })(function() {
	return {
		flex: 1,
		display: "flex",
		justifyContent: "center"
	};
}, ""), xk = z(P, { target: "eifx56c27" })(function() {
	return {
		display: "flex",
		alignItems: "center",
		width: "12px",
		height: "12px",
		padding: "2px 6px",
		cursor: "pointer"
	};
}, ""), Sk = z("div", { target: "eifx56c26" })(function() {
	return {
		display: "flex",
		height: "25px",
		alignItems: "center",
		padding: "0 8px"
	};
}, ""), Ck = z("div", { target: "eifx56c25" })(function() {
	return {
		display: "flex",
		alignItems: "center",
		fontSize: "14px",
		fontWeight: "700",
		padding: "0 8px",
		color: "#585858"
	};
}, ""), wk = z("div", { target: "eifx56c24" })(function() {
	return {
		display: "flex",
		alignItems: "center",
		height: "24px",
		borderLeft: "1px solid #CAD3DD",
		color: "#585858"
	};
}, ""), Tk = z("div", { target: "eifx56c23" })(function() {
	return {
		fontSize: "14px",
		fontWeight: "700",
		padding: "0 8px"
	};
}, ""), Ek = z("div", { target: "eifx56c22" })(function() {
	return {
		width: "100%",
		height: "100%",
		top: "-25px",
		position: "relative"
	};
}, ""), Dk = z("div", { target: "eifx56c21" })(function() {
	return {
		width: "100%",
		padding: "0 4px 4px"
	};
}, ""), Ok = z("div", { target: "eifx56c20" })(function() {
	return {
		display: "flex",
		width: "100%",
		height: "74px",
		flexDirection: "column",
		justifyContent: "center",
		alignItems: "center"
	};
}, ""), kk = z("div", { target: "eifx56c19" })(function() {
	return { fontSize: "14px" };
}, ""), Ak = z("div", { target: "eifx56c18" })(function() {
	return { fontSize: "12px" };
}, ""), jk = z("div", { target: "eifx56c17" })(function() {
	return {
		display: "flex",
		padding: "4px 0px",
		height: "32px",
		gap: "12px"
	};
}, ""), Mk = z("div", { target: "eifx56c16" })(function() {
	return {
		display: "grid",
		gridTemplateColumns: "2fr 1fr",
		gap: "0 2px"
	};
}, ""), Nk = z("div", { target: "eifx56c15" })(function() {
	return {
		height: "90px",
		backgroundColor: "white",
		borderRadius: "8px",
		padding: "5px"
	};
}, ""), Pk = z("div", { target: "eifx56c14" })(function() {
	return {
		display: "flex",
		justifyContent: "space-between"
	};
}, ""), Fk = z("div", { target: "eifx56c13" })(function() {
	return {
		display: "grid",
		gridTemplateColumns: "2fr 1fr"
	};
}, ""), Ik = z("div", { target: "eifx56c12" })(function(e) {
	var t = e.disabled;
	return {
		display: "flex",
		alignItems: "center",
		padding: "0 0 0 6px",
		pointerEvents: t ? "none" : "auto",
		opacity: t ? .5 : 1
	};
}, ""), Lk = z(function(e) {
	var t = e.className, n = ve(e, uk);
	return U(Mt, hk(hk({}, n), {}, { classes: { popper: t } }));
}, { target: "eifx56c11" })(function() {
	return I({}, `& .${pn.tooltip}`, {
		maxWidth: "220px",
		padding: "12px",
		backgroundColor: "white",
		color: "rgba(0, 0, 0, 0.87)",
		boxShadow: "0 1px 5px 0 #CCCCCC",
		fontSize: 11
	});
}, ""), Rk = z("div", { target: "eifx56c10" })(function() {
	return {
		display: "flex",
		flexDirection: "column",
		gap: "4px",
		fontSize: "12px",
		fontWeight: "700",
		color: "#585858",
		borderBottom: "1px solid #585858",
		paddingBottom: "8px",
		marginBottom: "8px"
	};
}, ""), zk = z("div", { target: "eifx56c9" })(function() {
	return {
		fontSize: "10px",
		paddingRight: "5px",
		whiteSpace: "nowrap"
	};
}, ""), Bk = z("div", { target: "eifx56c8" })(function() {
	return {
		fontSize: "14px",
		fontWeight: "700"
	};
}, ""), Vk = z(P, { target: "eifx56c7" })(function() {
	return {
		width: "20px",
		height: "20px"
	};
}, ""), Hk = z("div", { target: "eifx56c6" })(function() {
	return {
		display: "flex",
		alignItems: "center"
	};
}, ""), Uk = z(Qw, { target: "eifx56c5" })(function() {
	return {
		position: "relative",
		padding: "0 0 0 5px",
		zIndex: 1
	};
}, ""), Wk = "text-input-field-input", Gk = z(LT, { target: "eifx56c4" })(function() {
	return I({ margin: 0 }, `.${Wk}`, {
		width: "60px",
		"::-webkit-inner-spin-button": {
			WebkitAppearance: "none",
			margin: 0
		},
		"::-webkit-outer-spin-button": {
			WebkitAppearance: "none",
			margin: 0
		},
		MozAppearance: "textfield"
	});
}, ""), Kk = z("div", { target: "eifx56c3" })(function() {
	return {
		display: "grid",
		gridTemplateColumns: "repeat(8, 1fr)",
		gap: "4px 6px",
		width: "100%",
		backgroundColor: "white",
		borderRadius: "8px",
		padding: "6px",
		height: "90px",
		alignContent: "flex-start"
	};
}, ""), qk = z("div", { target: "eifx56c2" })("display:flex;position:relative;justify-content:space-between;background-color:#eff2f5;padding:4px 6px;font-weight:500;font-size:12px;border-radius:2px;min-width:50px;flex:1;opacity:", function(e) {
	return e.disabled ? .4 : 1;
}, ";&:after{content:'';position:absolute;bottom:0;left:0;width:15px;height:2px;background:", function(e) {
	var t = e.theme, n = e.monomerShortName;
	return (e.isPeptide ? t.ketcher.peptide.color : t.ketcher.monomer.color)[n]?.regular || t.ketcher.monomer.color.default.regular;
}, ";border-radius:0 0 0 2px;}"), Jk = z("div", { target: "eifx56c1" })(function() {
	return { fontWeight: "700" };
}, ""), Yk = function(e) {
	var t = (e.isPeptide ? At : On).map(function(t) {
		return [t, e.monomerCount[t] || 0];
	});
	return t.push([gk, e.monomerCount[gk] || 0]), t.sort(function(e, t) {
		return e[0] === gk ? 1 : e[0].localeCompare(t[0]);
	}), U(Kk, { children: (0, As.default)(t, function(t) {
		var n = R(t, 2), r = n[0], i = n[1];
		return W(qk, {
			monomerShortName: r,
			"data-testid": r + "-option",
			isPeptide: e.isPeptide,
			disabled: i === 0,
			children: [U(Jk, { children: r }), U("div", { children: i })]
		}, r);
	}) });
}, Xk = function(e) {
	return U(Ik, {
		"data-testid": e.testId,
		disabled: e.disabled,
		children: W(H, { children: [
			W(zk, { children: [e.name, e.value !== void 0 && ":"] }),
			e.onChangeValue ? U(Gk, {
				value: e.value ?? "",
				id: `macromolecule-property-${e.name}`,
				"data-testid": `${e.testId}-input`,
				type: "number",
				min: 0,
				inputClassName: Wk,
				onChange: function(t) {
					var n;
					return e == null || (n = e.onChangeValue) == null ? void 0 : n.call(e, Number(t));
				}
			}) : U(Bk, {
				"data-testid": e.testId + "-value",
				children: e.value
			}),
			e.hint && U(Lk, {
				title: e.hint,
				children: U(Hk, { children: U(Vk, {
					name: "about",
					dataTestId: e.name + "-info"
				}) })
			}),
			e.options && e.selectedOption && e.onChangeOption && U(Uk, {
				options: e.options.map(function(e) {
					return {
						id: e,
						label: e
					};
				}),
				testId: e.testId + "-selector",
				currentSelection: e.selectedOption,
				selectionHandler: e.onChangeOption
			})
		] })
	});
}, Zk = function(e) {
	var t = e.part, n = t.match(/^([A-Za-z]+)(\d+)$/);
	if (!n) return t;
	var r = R(n, 3);
	r[0];
	var i = r[1], a = r[2];
	return W("span", { children: [i, U("sub", { children: a })] });
}, Qk = z("svg", { target: "eifx56c0" })(function() {
	return {
		width: "100%",
		height: "100%"
	};
}, "");
function $k(e, t, n) {
	var r = e.length;
	if (n >= r || n === 0) return {
		xs: e,
		ys: t
	};
	for (var i = [e[0]], a = [t[0]], o = (r - 2) / (n - 2), s = 0, c = 0; c < n - 2; c++) {
		for (var l = Math.floor((c + 1) * o) + 1, u = Math.floor((c + 2) * o) + 1, d = l, f = u, p = 0, m = 0, h = f - d, g = d; g < f; g++) p += e[g], m += t[g];
		p /= h, m /= h;
		for (var _ = Math.floor(c * o) + 1, v = Math.floor((c + 1) * o) + 1, y = -1, b = _, x = _; x < v; x++) {
			var S = Math.abs((e[s] - p) * (t[x] - t[s]) - (e[s] - e[x]) * (m - t[s]));
			S > y && (y = S, b = x);
		}
		i.push(e[b]), a.push(t[b]), s = b;
	}
	return i.push(e[r - 1]), a.push(t[r - 1]), {
		xs: i,
		ys: a
	};
}
var eA = function(e) {
	return e > 360 ? 5 : e > 300 ? 4 : e > 240 ? 3 : 2;
}, tA = function(e) {
	return e < 1 ? 0 : e < 2 ? 1 : e < 3 ? 2 : e < 5 ? 3 : e < 10 ? 5 : e < 100 ? Math.floor(e / 10) * 10 : e < 1e3 ? Math.floor(e / 50) * 50 : Math.floor(e / 100) * 100;
}, nA = function(e) {
	var t = e.data, n = $k(t.map(function(e, t) {
		return t + 1;
	}), t, 100), r = (0, B.useState)(0), i = R(r, 2), a = i[0], o = i[1], s = (0, B.useRef)(null);
	(0, B.useEffect)(function() {
		if (n.xs.length && s.current) {
			var e = s.current.width.baseVal.value, r = s.current.height.baseVal.value, i = {
				top: 10,
				right: 10,
				bottom: 20,
				left: 30
			};
			Jd(s.current).selectAll("*").remove();
			var a = sg().domain([0, n.xs.length - 1]).range([i.left, e - i.right]), o = sg().domain([0, 1]).range([r - i.bottom, i.top]), c = hg().x(function(e, t) {
				return a(t);
			}).y(function(e) {
				return o(e);
			}).curve(fg), l = Jd(s.current), u = eA(e), d = tA(t.length / u), f = d, p;
			if (d >= 1) {
				for (var m = -Infinity, h = -Infinity, g = -Infinity, _ = 2; _ <= u; _++) {
					var v = _, y = tA(t.length / v), b = Number((y * (v / t.length)).toFixed(2));
					(b > g || b === g && v > m) && (m = v, g = b, h = y);
				}
				p = Array.from({ length: m }, function(e, t) {
					return n.xs.findLastIndex(function(e) {
						return e <= (t + 1) * h && e > t * h;
					});
				}), f = h;
			} else p = L(Array(Math.min(u, n.xs.length)).keys()), f = 1;
			var x = Vl(a).tickValues(p).tickFormat(function(e, t) {
				return ((t + 1) * f).toString();
			});
			l.append("g").attr("transform", `translate(0,${r - i.bottom})`).call(x).call(function(e) {
				return e.select(".domain").remove();
			}).call(function(e) {
				return e.selectAll("line").attr("stroke", "#CAD3DD").attr("y1", -r);
			}).call(function(e) {
				return e.selectAll("text").attr("font-size", "8px");
			});
			var S = Hl(o).tickValues([
				0,
				.5,
				1
			]).tickFormat(Vh(".1f"));
			l.append("g").attr("transform", `translate(${i.left},0)`).call(S).call(function(e) {
				return e.select(".domain").remove();
			}).call(function(t) {
				t.selectAll("line").each(function(t, n, r) {
					t === .5 ? Jd(r[n]).attr("x1", e).attr("stroke", "#CAD3DD").attr("stroke-dasharray", 2) : Jd(r[n]).remove();
				});
			}).call(function(e) {
				return e.selectAll("text").attr("font-size", "8px");
			}), l.append("path").datum(n.ys).attr("fill", "none").attr("stroke", "#167782").attr("stroke-width", 1).attr("d", c);
		}
	}, [t, a]);
	var c = new ResizeObserver((0, ws.debounce)(function(e) {
		var t = dk(e), n;
		try {
			for (t.s(); !(n = t.n()).done;) {
				var r = n.value;
				r.contentRect.width !== a && o(r.contentRect.width);
			}
		} catch (e) {
			t.e(e);
		} finally {
			t.f();
		}
	}, 100));
	return (0, B.useEffect)(function() {
		return s.current && c.observe(s.current), function() {
			c.disconnect();
		};
	}, [s, a]), U(Qk, {
		"data-testid": "Hydrophobicity-Chart",
		ref: s
	});
}, rA = function(e) {
	return e.isError ? W(Ok, { children: [U(kk, { children: "No Data Available" }), U(Ak, { children: "Select monomer, chain or part of a chain" })] }) : W(Dk, { children: [W(Fk, { children: [W(jk, { children: [U(Xk, {
		name: "Isoelectric Point",
		testId: "Isoelectric Point",
		value: (0, ws.isNumber)(e.macromoleculesProperties.pKa) ? (0, ks.default)(e.macromoleculesProperties.pKa, 2) : "–",
		hint: W("div", { children: [
			"The isoelectric point is calculated as the median of all pKa values for amino acids (values from",
			" ",
			U("i", { children: "Miclotte et. al. (2020))" }),
			". Only amino acid natural analogues are used in the calculation."
		] })
	}), U(Xk, {
		name: "Extinction Coef.(1/Mcm)",
		testId: "Extinction Coefficient",
		value: (0, ws.isNumber)(e.macromoleculesProperties.extinctionCoefficient) ? (0, ks.default)(e.macromoleculesProperties.extinctionCoefficient) : "–",
		hint: W("div", { children: [
			"The extinction coefficient for wavelength of 280nm is calculated using the method from",
			" ",
			U("i", { children: "Gill, S.C. and von Hippel, P.H. (1989)." }),
			" Natural analogue is used in place of a modified amino acid."
		] })
	})] }), U(Xk, {
		name: "Hydrophobicity",
		testId: "Hydrophobicity",
		hint: W("div", { children: [
			W(Rk, { children: [U("div", { children: "y = Hydrophobicity score" }), U("div", { children: "x = Position of the amino acid residue" })] }),
			"The hydrophobicity is calculated using the method from",
			" ",
			U("i", { children: "Black S.D. and Mould D.R. (1991)." }),
			" Natural analogue is used in place of a modified amino acid."
		] })
	})] }), W(Mk, { children: [e.macromoleculesProperties.monomerCount.peptides && U(Yk, {
		monomerCount: e.macromoleculesProperties.monomerCount.peptides,
		isPeptide: !0
	}), U(Nk, { children: e.macromoleculesProperties.hydrophobicity && U(nA, { data: e.macromoleculesProperties.hydrophobicity }) })] })] });
}, iA = function(e) {
	return !/[^0.,]/.test(String(e));
}, aA = function(e) {
	var t = X(), n = Z(t_), r = Z(n_), i = Z(r_), a = Z(i_);
	return e.isError ? W(Ok, { children: [U(kk, { children: "No Data Available" }), U(Ak, { children: "Select a nucleotide/nucleoside, chain or part of a chain containing nucleotides/nucleosides" })] }) : W(Dk, { children: [W(Pk, { children: [(0, ws.isNumber)(e.macromoleculesProperties.Tm) ? U(Xk, {
		name: "Melting Temp. (°C)",
		value: (0, ks.default)(e.macromoleculesProperties.Tm, 1),
		testId: "Melting-Temperature",
		hint: W("div", { children: [
			"The melting temperature is calculated using the method from",
			" ",
			U("i", { children: "Khandelwal G. and Bhyravabhotla J. (2010)." }),
			" Natural analogue is used in place of a modified base."
		] })
	}) : U("div", {}), W(jk, { children: [U(Xk, {
		name: "[Unipositive Ions]",
		value: i,
		options: [
			"nM",
			"μM",
			"mM"
		],
		testId: "Unipositive Ions",
		selectedOption: n,
		disabled: !(0, ws.isNumber)(e.macromoleculesProperties.Tm) && !iA(i),
		onChangeOption: function(e) {
			t(Ig(e));
		},
		onChangeValue: function(e) {
			t(zg(e.toString()));
		}
	}), U(Xk, {
		name: "[Oligonucleotides]",
		value: a,
		options: [
			"nM",
			"μM",
			"mM"
		],
		testId: "Oligonucleotides",
		selectedOption: r,
		disabled: !(0, ws.isNumber)(e.macromoleculesProperties.Tm) && !iA(a),
		onChangeOption: function(e) {
			t(Lg(e));
		},
		onChangeValue: function(e) {
			t(Bg(e.toString()));
		}
	})] })] }), e.macromoleculesProperties.monomerCount.nucleotides && U(Yk, { monomerCount: e.macromoleculesProperties.monomerCount.nucleotides })] });
}, oA;
(function(e) {
	e[e.PEPTIDES = 0] = "PEPTIDES", e[e.RNA = 1] = "RNA", e[e.NO_TAB = -1] = "NO_TAB";
})(oA ||= {});
var sA;
(function(e) {
	e.Da = "Da", e.kDa = "kDa", e.MDa = "MDa";
})(sA ||= {});
var cA = I(I(I({}, sA.Da, 1), sA.kDa, 1e3), sA.MDa, 1e6), lA = function(e) {
	return !(0, ws.isNumber)(e) || e < 1e3 ? sA.Da : e < 1e6 ? sA.kDa : sA.MDa;
}, uA, dA = function() {
	var e = X(), t = Z(K), n = Z(e_), r = Z(t_), i = Z(n_), a = Z(r_), o = Z(i_), s = n?.[0], c = (0, B.useState)(oA.PEPTIDES), l = R(c, 2), u = l[0], d = l[1], f = (0, B.useState)(lA(s?.mass)), p = R(f, 2), m = p[0], h = p[1], g = Z($g), _ = lk(), v = !g, y = (0, B.useRef)(_), b = (0, B.useCallback)((0, ws.debounce)(function(e) {
		y.current(e);
	}, 500), []);
	(0, B.useEffect)(function() {
		y.current = function(e) {
			_(e);
		};
	}, [_]), (0, B.useEffect)(function() {
		return uA && t != null && t.events.selectEntities.hasHandler(uA) && t?.events.selectEntities.remove(uA), uA = function() {
			b(v);
		}, t?.events.selectEntities.add(uA), function() {
			t?.events.selectEntities.remove(uA);
		};
	}, [
		b,
		t,
		v
	]), (0, B.useEffect)(function() {
		b(v);
	}, [
		r,
		i,
		a,
		o,
		v,
		b
	]), (0, B.useEffect)(function() {
		d(_k(s, "nucleotides") ? oA.RNA : oA.PEPTIDES), h(lA(s?.mass));
	}, [s]);
	var x = function(e, t) {
		d(t);
	}, S = function() {
		e(Ng(!1));
	}, C = function(e) {
		h(e);
	}, w = !s || n.length > 1, T = w || !_k(s, "peptides"), E = w || !_k(s, "nucleotides"), D = (0, B.useMemo)(function() {
		return s != null && s.grossFormula ? U(Ck, {
			"data-testid": "Gross-formula",
			children: s?.grossFormula.split(" ").map(function(e, t, n) {
				return W("span", { children: [U(Zk, { part: e }), t < n.length - 1 ? " " : ""] }, `${e}-${t}`);
			})
		}) : null;
	}, [s?.grossFormula]), O = (0, B.useMemo)(function() {
		return s != null && s.mass ? W(H, { children: [U(Tk, {
			"data-testid": "Molecular-Mass-Value",
			children: (0, ks.default)(s?.mass / cA[m], 3)
		}), " "] }) : null;
	}, [s?.mass, m]);
	return g ? W(vk, {
		hasError: u === oA.PEPTIDES && T || u === oA.RNA && E,
		"data-testid": "macromolecule-properties-window",
		children: [
			W(yk, { children: [U(bk, { children: W("svg", {
				width: "16",
				height: "16",
				viewBox: "0 0 16 16",
				fill: "none",
				xmlns: "http://www.w3.org/2000/svg",
				children: [U("path", {
					d: "M2 6H14",
					stroke: "#333333"
				}), U("path", {
					d: "M2 10H14",
					stroke: "#333333"
				})]
			}) }), U(xk, {
				name: "close",
				onClick: S,
				dataTestId: "macromolecule-properties-close"
			})] }),
			W(Sk, { children: [D, O && W(wk, { children: [O, U(Uk, {
				testId: "Molecular Mass Unit",
				options: [
					sA.Da,
					sA.kDa,
					sA.MDa
				].map(function(e) {
					return {
						id: e,
						label: e
					};
				}),
				currentSelection: m,
				selectionHandler: C
			})] })] }),
			U(Ek, { children: U(fx, {
				selectedTabIndex: u,
				onChange: x,
				isLayoutToRight: !0,
				tabs: [{
					caption: "Peptides",
					testId: "peptides-properties-tab",
					component: rA,
					props: {
						macromoleculesProperties: s,
						isError: T
					}
				}, {
					caption: "RNA/DNA",
					component: aA,
					testId: "rna-properties-tab",
					props: {
						macromoleculesProperties: s,
						isError: E
					}
				}]
			}) })
		]
	}) : null;
}, fA = Se(xn), pA = function(e) {
	var t = parseInt(e ?? "");
	return isNaN(t) ? 0 : t;
}, mA = function(e, t) {
	if (e === 0) return t;
	var n = Ke.instance.MINZOOMSCALE * 100, r = Ke.instance.MAXZOOMSCALE * 100;
	return e < n ? n : e > r ? r : e;
}, hA = function(e, t) {
	t && (t.value = `${Math.round(e)}%`);
}, gA = z(y, { target: "e1pc97tg0" })(function(e) {
	var t = e.theme, n = e.isActive;
	return {
		width: "28px",
		height: "28px",
		backgroundColor: n ? t.ketcher.color.button.group.active : "white",
		margin: "2px",
		padding: "0",
		borderRadius: "4px",
		outline: "none",
		":hover": { backgroundColor: n ? t.ketcher.color.button.group.hover : "white" },
		":hover svg": { fill: n ? "white" : t.ketcher.color.button.group.active }
	};
}, ""), _A = function() {
	var e = X(), t = Z($g), n = lk();
	return U(gA, {
		isActive: t,
		onClick: function() {
			var r = dn(Ds.default.mark(function r() {
				var i;
				return Ds.default.wrap(function(r) {
					for (;;) switch (r.prev = r.next) {
						case 0: return i = !t, r.next = 3, n(i);
						case 3: e(Pg({})), jD();
						case 5:
						case "end": return r.stop();
					}
				}, r);
			}));
			return function() {
				return r.apply(this, arguments);
			};
		}(),
		title: `Calculate properties (${fA.toggleMacromoleculesPropertiesVisibility})`,
		"data-testid": "calculate-macromolecule-properties-button",
		children: U("svg", {
			width: "15",
			height: "16",
			viewBox: "0 0 15 16",
			xmlns: "http://www.w3.org/2000/svg",
			fill: t ? "white" : "#333333",
			children: U("path", {
				fillRule: "evenodd",
				clipRule: "evenodd",
				d: "M9.87727 1.65517H9.03053V4.46737L9.42288 5.12973C9.76799 5.04496 10.1287 5 10.5 5C12.9853 5 15 7.01472 15 9.5C15 10.6812 14.5449 11.7562 13.8004 12.559C14.4936 14.1572 13.3016 16 11.456 16H2.54694C0.627617 16 -0.60048 14.0008 0.302223 12.3451C1.6087 9.94883 3.5345 6.39671 4.51457 4.49368V1.65517H3.66783V0H9.87727V1.65517ZM12.2962 13.6272C11.746 13.867 11.1385 14 10.5 14C8.01472 14 6 11.9853 6 9.5C6 7.98987 6.74386 6.65348 7.88515 5.83725L7.33705 4.91194V1.65517H6.20806V4.88502L6.11866 5.05976C5.15873 6.93619 3.14099 10.658 1.79676 13.1235C1.49524 13.6765 1.9056 14.3448 2.54694 14.3448H11.456C11.9075 14.3448 12.2417 14.0139 12.2962 13.6272ZM13.5375 9.5C13.5375 11.1776 12.1776 12.5375 10.5 12.5375C8.82244 12.5375 7.4625 11.1776 7.4625 9.5C7.4625 7.82243 8.82244 6.4625 10.5 6.4625C12.1776 6.4625 13.5375 7.82243 13.5375 9.5Z"
			})
		})
	});
};
function vA() {
	var e = X(), t = Z(Wg), n = Z(K), r = yx(), i = Z(Kg), a = (0, B.useState)([]), o = R(a, 2), s = o[0], c = o[1], l = (0, B.useState)(!1), u = R(l, 2), d = u[0], f = u[1], p = (0, B.useState)(), m = R(p, 2), h = m[0], g = m[1], _ = [t], v = i, y = Z(c_), b = r === "flex-layout-mode", x = s.filter(function(e) {
		return e && typeof e.forEachBond == "function";
	}), S = (n?.drawingEntitiesManager.selectedMicromoleculeEntities.length ?? 0) > 0 || !hO(x);
	return (0, B.useEffect)(function() {
		var e = function(e) {
			c(e), e.length && !cO(e) && (f(!1), lO(e) ? g("antisenseDnaStrand") : uO(e) ? g("antisenseRnaStrand") : (g("antisenseStrand"), f(!0)));
		};
		return n?.events.selectEntities.add(e), function() {
			n?.events.selectEntities.remove(e);
		};
	}, [n]), W($, {
		onItemClick: function(t) {
			GE[t] ? e($_(t)) : t === "undo" || t === "redo" ? n?.events.selectHistory.dispatch(t) : t === "clear" ? (n?.events.resetSequenceEditMode.dispatch(), n?.events.selectTool.dispatch([t]), e(Dg(y)), n?.events.selectTool.dispatch([y]), i && JS(e, n)) : t === "antisenseRnaStrand" || t === "antisenseDnaStrand" ? n?.events.createAntisenseChain.dispatch(t === "antisenseDnaStrand") : t === "arrange-ring" && n?.events.layoutCircular.dispatch();
		},
		activeMenuItems: _,
		isHorizontal: !0,
		children: [
			W($.Group, {
				isHorizontal: !0,
				divider: !0,
				children: [
					U($.Item, {
						itemId: "clear",
						title: `Clear Canvas (${fA.clear})`,
						testId: "clear-canvas"
					}),
					U($.Item, {
						itemId: "open",
						title: "Open...",
						disabled: v,
						testId: "open-file-button"
					}),
					U($.Item, {
						itemId: "save",
						title: "Save as...",
						testId: "save-file-button"
					})
				]
			}),
			W($.Group, {
				isHorizontal: !0,
				divider: !0,
				children: [U($.Item, {
					itemId: "undo",
					title: `Undo (${fA.undo})`,
					disabled: v,
					testId: "undo"
				}), U($.Item, {
					itemId: "redo",
					title: `Redo (${fA.redo})`,
					disabled: v,
					testId: "redo"
				})]
			}),
			b && U($.Group, {
				isHorizontal: !0,
				divider: !0,
				children: U($.Item, {
					itemId: "arrange-ring",
					title: `Arrange as a Ring (${fA.arrangeRing})`,
					disabled: S,
					testId: "arrange-ring"
				})
			}),
			W($.Group, {
				isHorizontal: !0,
				children: [W($.Submenu, {
					disabled: !(s != null && s.length) || !dO(s) || cO(s),
					needOpenByMenuItemClick: d,
					vertical: !0,
					autoSize: !0,
					layoutModeButton: !0,
					generalTitle: "Create Antisense Strand",
					testId: "Create Antisense Strand",
					activeItem: h,
					children: [U($.Item, {
						itemId: "antisenseRnaStrand",
						title: `Create RNA Antisense Strand (${fA.createRnaAntisenseStrand})`,
						disabled: !(s != null && s.length) || !dO(s) || cO(s),
						testId: "antisenseRnaStrand",
						type: "button"
					}), U($.Item, {
						itemId: "antisenseDnaStrand",
						title: `Create DNA Antisense Strand (${fA.createDnaAntisenseStrand})`,
						disabled: !(s != null && s.length) || !dO(s) || cO(s),
						testId: "antisenseDnaStrand",
						type: "button"
					})]
				}), U(_A, {})]
			})
		]
	});
}
function yA() {
	var e = Z(Wg), t = Z(K), n = yx() === "sequence-layout-mode";
	return W($, {
		testId: "left-toolbar",
		onItemClick: function(e) {
			t?.events.selectTool.dispatch([e, { toolName: e }]);
		},
		activeMenuItems: [e],
		children: [W($.Group, {
			divider: !0,
			children: [
				U($.Item, {
					itemId: "hand",
					title: `Hand Tool (${fA.hand})`,
					testId: "hand"
				}),
				U($.Group, { children: W($.Submenu, {
					testId: "select-drop-down-button",
					subMenuId: yg,
					needOpenByMenuItemClick: !0,
					children: [
						U($.Item, {
							itemId: "select-rectangle",
							title: `Select Rectangle (${fA.switchSelectTool})`,
							testId: "select-rectangle"
						}),
						U($.Item, {
							itemId: "select-lasso",
							title: `Lasso selection (${fA.switchSelectTool})`,
							testId: "select-lasso"
						}),
						U($.Item, {
							itemId: "select-structure",
							title: `Structure Selection (${fA.switchSelectTool})`,
							testId: "select-structure"
						})
					]
				}) }),
				U($.Item, {
					itemId: "erase",
					title: `Erase (${fA.erase})`,
					testId: "erase",
					disabled: n
				})
			]
		}), U($.Group, { children: W($.Submenu, {
			disabled: n,
			testId: "bonds-drop-down-button",
			needOpenByMenuItemClick: !1,
			children: [U($.Item, {
				itemId: "bond-single",
				title: "Single Bond (1)",
				testId: "single-bond",
				disabled: n
			}), U($.Item, {
				itemId: "bond-hydrogen",
				title: "Hydrogen Bond (2)",
				testId: "hydrogen-bond",
				disabled: n
			})]
		}) })]
	});
}
var bA = z("div", { target: "e1aw4j3q7" })({
	name: "bjn8wh",
	styles: "position:relative"
}), xA = z(Fn, { target: "e1aw4j3q6" })("display:flex;color:", function(e) {
	return e.theme.ketcher.color.dropdown.primary;
}, ";padding-right:0;padding-left:0;& svg{margin-left:2px;width:1rem;height:1rem;}"), SA = z("span", { target: "e1aw4j3q5" })({
	name: "td41hq",
	styles: "width:35px"
}), CA = z(lt, { target: "e1aw4j3q4" })("& .MuiPopover-paper{padding:8px;width:175px;border:none;border-radius:0px 0px 4px 4px;box-shadow:", function(e) {
	return e.theme.ketcher.shadow.regular;
}, ";box-sizing:border-box;}"), wA = z("div", { target: "e1aw4j3q3" })({
	name: "5s1n17",
	styles: "display:flex;flex-direction:column;white-space:nowrap;word-break:keep-all;background:white"
}), TA = z(Fn, { target: "e1aw4j3q2" })("display:flex;justify-content:space-between;font-size:", function(e) {
	return e.theme.ketcher.font.size.regular;
}, ";line-height:14px;padding:7px 8px;text-transform:none;color:", function(e) {
	return e.theme.ketcher.color.dropdown.primary;
}, ";"), EA = z("span", { target: "e1aw4j3q1" })({
	name: "btyqtq",
	styles: "color:#cad3dd"
}), DA = z("input", { target: "e1aw4j3q0" })("border:1px solid #cad3dd;border-radius:4px;padding:3px 8px;color:", function(e) {
	return e.theme.ketcher.color.text.light;
}, ";font-size:", function(e) {
	return e.theme.ketcher.font.size.medium;
}, ";line-height:16px;margin-bottom:8px;&:hover{border-color:", function(e) {
	return e.theme.ketcher.color.input.border.hover;
}, ";}&:active,&:focus{border-color:", function(e) {
	return e.theme.ketcher.outline.selected.color;
}, ";outline:none;}&::after,&::before{display:none;}"), OA = function(e) {
	var t = e.onZoomSubmit, n = e.currentZoom, r = e.inputRef, i = (0, B.useCallback)(function(e) {
		var n = r.current;
		n && ([fA["zoom-out"], fA["zoom-in"]].includes(e.key) || e.nativeEvent.stopImmediatePropagation(), e.key === "Enter" && (t(), n.select()));
	}, [
		t,
		r,
		fA
	]);
	return (0, B.useEffect)(function() {
		var e = r.current;
		hA(n, e), document.activeElement === e && e?.select();
	}, [n, r]), (0, B.useEffect)(function() {
		var e = r.current;
		e?.focus(), e?.select();
	}, [r]), U(DA, {
		ref: r,
		"data-testid": "zoom-value",
		onFocus: function(e) {
			e.target.select();
		},
		onKeyDown: i
	});
}, kA = function() {
	var e = (0, B.useState)(!1), t = R(e, 2), n = t[0], r = t[1], i = (0, B.useState)(100), a = R(i, 2), o = a[0], s = a[1], c = (0, B.useRef)(null), l = (0, B.useRef)(null);
	(0, B.useEffect)(function() {
		var e;
		Ke == null || (e = Ke.instance) == null || e.subscribeOnZoomEvent(function() {
			var e;
			s(Math.round((Ke == null || (e = Ke.instance) == null ? void 0 : e.getZoomLevel()) * 100));
		});
	}, [Ke?.instance]);
	var u = (0, B.useCallback)(function() {
		var e = l.current;
		if (e) {
			var t = pA(e.value);
			if (t && t !== o) {
				var n = mA(t, o);
				hA(n, e), Ke.instance.zoomTo(n / 100);
			} else hA(o, e);
		}
	}, [o]);
	return W(bA, {
		ref: c,
		children: [W(xA, {
			onClick: function() {
				r(!0);
			},
			"data-testid": "zoom-selector",
			children: [W(SA, {
				"data-testid": "zoom-input",
				children: [o, "%"]
			}), U(P, { name: "chevron" })]
		}), U(CA, {
			open: n,
			onClose: function() {
				r(!1);
			},
			anchorEl: c.current,
			container: document.querySelector(he),
			anchorOrigin: {
				vertical: "bottom",
				horizontal: "right"
			},
			transformOrigin: {
				vertical: "top",
				horizontal: "right"
			},
			disableEnforceFocus: !0,
			children: W(wA, { children: [
				U(OA, {
					onZoomSubmit: u,
					inputRef: l,
					currentZoom: o
				}),
				W(TA, {
					"data-testid": "zoom-out",
					title: "Zoom Out",
					onClick: function() {
						Ke.instance.zoomOut();
					},
					children: [U("span", { children: "Zoom out" }), U(EA, { children: fA["zoom-minus"] })]
				}),
				W(TA, {
					"data-testid": "zoom-in",
					title: "Zoom In",
					onClick: function() {
						Ke.instance.zoomIn();
					},
					children: [U("span", { children: "Zoom in" }), U(EA, { children: fA["zoom-plus"] })]
				}),
				W(TA, {
					"data-testid": "zoom-default",
					title: "Zoom 100%",
					onClick: function() {
						Ke.instance.resetZoom();
					},
					children: [U("span", { children: "Zoom 100%" }), U(EA, { children: fA["zoom-reset"] })]
				})
			] })
		})]
	});
};
function AA(e, t) {
	var n = Object.keys(e);
	if (Object.getOwnPropertySymbols) {
		var r = Object.getOwnPropertySymbols(e);
		t && (r = r.filter(function(t) {
			return Object.getOwnPropertyDescriptor(e, t).enumerable;
		})), n.push.apply(n, r);
	}
	return n;
}
function jA(e) {
	for (var t = 1; t < arguments.length; t++) {
		var n = arguments[t] == null ? {} : arguments[t];
		t % 2 ? AA(Object(n), !0).forEach(function(t) {
			I(e, t, n[t]);
		}) : Object.getOwnPropertyDescriptors ? Object.defineProperties(e, Object.getOwnPropertyDescriptors(n)) : AA(Object(n)).forEach(function(t) {
			Object.defineProperty(e, t, Object.getOwnPropertyDescriptor(n, t));
		});
	}
	return e;
}
var MA = [Ut.bondSingle, Ut.selectRectangle], NA = function() {
	var e = Z(K), t = Z(Wg), n = Z(Zg), r = X(), i = Z(eb), a = Z(Xg), o = Z(c_), s = (0, B.useCallback)(function() {
		r(N_(e?.monomersLibrary)), r(P_(e?.defaultRnaPresetsLibraryItems));
	}, [e]);
	(0, B.useEffect)(function() {
		return e?.events.updateMonomersLibrary.add(s), function() {
			e?.events.updateMonomersLibrary.remove(s);
		};
	}, [e]), (0, B.useEffect)(function() {
		var t = function() {
			e?.events.selectTool.dispatch([o]), r(Dg(o));
		};
		return e && e.events.selectSelectionTool.add(t), function() {
			e?.events.selectSelectionTool.remove(t);
		};
	}, [
		r,
		e,
		o
	]), (0, B.useEffect)(function() {
		var n = function(e) {
			var n = R(e, 1)[0];
			n !== t && r(Dg(n));
		};
		return e && (e.events.error.add(function(e) {
			r(tv(e));
		}), e.events.openErrorModal.add(function(e) {
			r(rv(e));
		}), r(Dg("select-rectangle")), e.events.selectTool.dispatch(["select-rectangle"]), e.events.openMonomerConnectionModal.add(function(e) {
			return r($_({
				name: "monomerConnection",
				additionalProps: e
			}));
		}), e.events.openConfirmationDialog.add(function(e) {
			return r($_({
				name: "confirmationDialog",
				additionalProps: e
			}));
		}), e.events.selectTool.add(n)), function() {
			r(Dg(null)), e?.events.selectTool.remove(n);
		};
	}, [e]);
	var c = (0, B.useCallback)(function(e) {
		return r(Ag(e));
	}, [r]), l = (0, B.useCallback)((0, ws.debounce)(function(e) {
		return c(e);
	}, 500), [c]);
	(0, B.useEffect)(function() {
		var n = function(e) {
			var n = R(e, 1)[0];
			n !== t && r(Dg(n));
		};
		return e && (e.events.error.add(function(e) {
			r(tv(e));
		}), e.events.openErrorModal.add(function(e) {
			r(rv(e));
		}), r(Dg("select-rectangle")), e.events.selectTool.dispatch(["select-rectangle"]), e.events.openMonomerConnectionModal.add(function(e) {
			return r($_({
				name: "monomerConnection",
				additionalProps: e
			}));
		}), e.events.selectTool.add(n)), function() {
			r(Dg(null)), e?.events.selectTool.remove(n);
		};
	}, [e]);
	var u = (0, B.useCallback)(function(e, t) {
		l({
			type: _g.Bond,
			polymerBond: e,
			style: t
		});
	}, [l]), d = (0, B.useCallback)(function(e) {
		if (e.buttons !== 1 && e.buttons !== 2) {
			if (n) e.preventDefault(), e.stopPropagation();
			else {
				var t = e.target.__data__?.polymerBond;
				if (!(t && !t.finished || t instanceof j)) {
					if (t) u(t, xt(t, e.target.getBoundingClientRect()));
					else {
						var r = e.target.__data__?.node, a = e.target.__data__?.monomer || r?.monomer;
						if (!(r && r instanceof un)) {
							if (a instanceof mn) l({
								type: _g.AmbiguousMonomer,
								monomer: a.variantMonomerItem,
								target: e.target
							});
							else {
								var o = a.monomerItem, s = jA({}, a.attachmentPointsToBonds), c = r instanceof An || r instanceof Dt;
								if (r instanceof wt) {
									var d = r.monomers;
									if (d.length > 1) {
										l({
											type: _g.Preset,
											monomers: d.map(function(e) {
												return e.monomerItem;
											}),
											position: vg.ChainMiddle,
											target: e.target
										});
										return;
									}
								}
								if (c) {
									var f = r instanceof An ? [
										r.sugar.monomerItem,
										r.rnaBase.monomerItem,
										r.phosphate?.monomerItem
									] : [r.sugar.monomerItem, r.rnaBase.monomerItem];
									if (r.rnaBase instanceof mn) {
										l({
											type: _g.AmbiguousMonomer,
											monomer: r.rnaBase.variantMonomerItem,
											presetMonomers: f,
											target: e.target
										});
										return;
									}
									var p = i.find(function(e) {
										var t = [
											e.sugar,
											e.base,
											e.phosphate
										];
										return f.every(function(e, n) {
											return e?.props.Name === t[n]?.props.Name;
										});
									}), m = r instanceof Dt ? vg.ChainEnd : r.firstMonomerInNode.R1AttachmentPoint === void 0 ? vg.ChainMiddle : vg.ChainStart;
									l({
										type: _g.Preset,
										monomers: f,
										name: p?.name,
										idtAliases: p?.idtAliases,
										aliasAxoLabs: p?.aliasAxoLabs,
										phosphatePosition: r instanceof An ? "right" : void 0,
										position: m,
										target: e.target
									});
								} else l({
									type: _g.Monomer,
									monomer: o,
									attachmentPointsToBonds: s,
									target: e.target
								});
							}
						}
					}
				}
			}
		}
	}, [
		u,
		l,
		i,
		n
	]), f = (0, B.useCallback)(function() {
		l.cancel(), r(Ag(void 0));
	}, [l, r]);
	return (0, B.useEffect)(function() {
		e?.events.mouseOverMonomer.add(d), e?.events.mouseLeaveMonomer.add(f), e?.events.mouseLeaveAttachmentPoint.add(f), e?.events.mouseDownAttachmentPoint.add(f), e?.events.mouseOverSequenceItem.add(d), e?.events.mouseLeaveSequenceItem.add(f), e?.events.mouseOverPolymerBond.add(d), e?.events.mouseLeavePolymerBond.add(f);
		var n = function(e) {
			f(), (e.buttons !== 1 || !MA.includes(t)) && d(e);
		};
		return e?.events.mouseOnMoveMonomer.add(n), e?.events.mouseMoveAttachmentPoint.add(n), e?.events.mouseOnMoveSequenceItem.add(n), e?.events.mouseOnMovePolymerBond.add(n), window.addEventListener("hidePreview", f), function() {
			e?.events.mouseOverMonomer.remove(d), e?.events.mouseLeaveMonomer.remove(f), e?.events.mouseLeaveAttachmentPoint.remove(f), e?.events.mouseOverSequenceItem.remove(d), e?.events.mouseLeaveSequenceItem.remove(f), e?.events.mouseOverPolymerBond.remove(d), e?.events.mouseLeavePolymerBond.remove(f), e?.events.mouseOnMoveMonomer.remove(n), e?.events.mouseMoveAttachmentPoint.remove(n), e?.events.mouseOnMoveSequenceItem.remove(n), e?.events.mouseOnMovePolymerBond.remove(n), window.removeEventListener("hidePreview", f);
		};
	}, [
		e,
		t,
		d,
		f
	]), (0, B.useEffect)(function() {
		a || e?.events.resetSequenceEditMode.dispatch();
	}, [a]), U(H, {});
}, PA = function(e) {
	var t = e.selectedMonomers, n = e.contextMenuEvent, r = t || [], i = Z(K), a = ft({ id: tS.FOR_SELECTED_MONOMERS }).hideAll, o = mO(r, n), s = function(e) {
		var t, n = ((i == null || (t = i.drawingEntitiesManager) == null || (t = t.selectedEntitiesArr) == null ? void 0 : t.length) ?? 0) > 0;
		return !(e != null && e.polymerBondRenderer) && (!(e != null && e.selectedMonomers) || e?.selectedMonomers.length === 0) && !n;
	}, c = pO(o), l = function(e) {
		return !!(e != null && e.polymerBondRenderer);
	}, u = r && r.length > 0 && dO(r), d = i?.mode.modeName === "flex-layout-mode", f = !d || i?.drawingEntitiesManager.selectedMicromoleculeEntities.length > 0 || !hO(r), p = [
		{
			name: "copy",
			title: "Copy",
			icon: U(P, { name: "copyMenu" }),
			disabled: function(e) {
				var t = e.props, n = t === void 0 ? {} : t;
				return l(n) || s(n);
			}
		},
		{
			name: gO.paste,
			title: "Paste",
			icon: U(P, { name: "pasteNavBar" }),
			disabled: function(e) {
				var t = e.props;
				return !s(t === void 0 ? {} : t);
			},
			separator: !0
		},
		{
			name: "create_antisense_rna_chain",
			title: "Create Antisense RNA Strand",
			separator: !1,
			disabled: cO(r),
			hidden: function(e) {
				var t = e.props;
				return !(t != null && t.selectedMonomers) || !dO(t?.selectedMonomers);
			}
		},
		{
			name: "create_antisense_dna_chain",
			title: "Create Antisense DNA Strand",
			disabled: cO(r),
			hidden: function(e) {
				var t = e.props;
				return !(t != null && t.selectedMonomers) || !dO(t?.selectedMonomers);
			},
			separator: u
		},
		{
			name: gO.modifyAminoAcids,
			title: "Modify amino acids",
			disabled: !1,
			hidden: !c.length,
			subMenuItems: c
		},
		{
			name: "layout_circular",
			title: "Arrange as a Ring",
			disabled: f,
			hidden: !d
		},
		{
			name: "edit_attachment_points",
			title: "Edit Attachment Points...",
			disabled: function(e) {
				var t = e.props;
				return !l(t);
			},
			separator: !0
		},
		{
			name: "delete",
			title: "Delete",
			icon: U(P, { name: "deleteMenu" }),
			disabled: function(e) {
				var t = e.props;
				return s(t === void 0 ? {} : t);
			}
		}
	], m = function(e) {
		var t = e.id, n = e.props;
		switch (!0) {
			case t === "layout_circular":
				i?.events.layoutCircular.dispatch(), a();
				break;
			case t === "copy":
				i?.events.copySelectedStructure.dispatch();
				break;
			case t === "create_antisense_rna_chain":
				i?.events.createAntisenseChain.dispatch(!1);
				break;
			case t === "create_antisense_dna_chain":
				i?.events.createAntisenseChain.dispatch(!0);
				break;
			case t === "delete":
				i?.events.deleteSelectedStructure.dispatch();
				break;
			case t === "paste":
				i?.events.pasteFromClipboard.dispatch();
				break;
			case t === "edit_attachment_points":
				var r, s = n == null || (r = n.polymerBondRenderer) == null ? void 0 : r.polymerBond;
				if (!s) return;
				i?.events.openMonomerConnectionModal.dispatch({
					firstMonomer: s.firstMonomer,
					secondMonomer: s.secondMonomer,
					polymerBond: s,
					isReconnectionDialog: !0
				});
				break;
			case t?.startsWith(fO):
				var c = t?.replace(fO, "");
				i?.events.modifyAminoAcids.dispatch({
					monomers: o,
					modificationType: c
				});
		}
	}, h = document.querySelector(he);
	return h && (0, Es.createPortal)(U(iS, {
		id: tS.FOR_SELECTED_MONOMERS,
		handleMenuChange: m,
		menuItems: p
	}), h);
}, FA = z(y, { target: "e1846tr80" })(function(e) {
	var t = e.theme, n = e.isActive;
	return {
		width: "40px",
		height: "31px",
		backgroundColor: n ? t.ketcher.color.button.group.active : "white",
		marginRight: "8px",
		border: n ? t.ketcher.outline.selected.color : t.ketcher.outline.small,
		borderRadius: "4px",
		outline: "none",
		":hover": { backgroundColor: n ? t.ketcher.color.button.group.hover : "white" },
		":hover svg": { fill: n ? "white" : t.ketcher.color.button.group.active }
	};
}, ""), IA = function() {
	var e = Z(K), t = (0, B.useState)(!0), n = R(t, 2), r = n[0], i = n[1], a = yx() === "sequence-layout-mode", o = Z(Xg);
	return (0, B.useEffect)(function() {
		a && o && e?.events.toggleIsSequenceSyncEditMode.dispatch(r);
	}, [a, o]), a && o ? U(FA, {
		isActive: r,
		onClick: function() {
			var t = !r;
			i(t), e?.events.toggleIsSequenceSyncEditMode.dispatch(t), jD();
		},
		"data-testid": "sync_sequence_edit_mode",
		"data-isactive": r,
		children: W("svg", {
			width: "24",
			height: "24",
			viewBox: "0 0 24 24",
			xmlns: "http://www.w3.org/2000/svg",
			fill: r ? "white" : "#333333",
			children: [
				U("rect", {
					x: "1",
					y: "1.5",
					width: "22",
					height: "2",
					rx: "1"
				}),
				U("rect", {
					x: "2.5",
					y: "1.5",
					width: "5",
					height: "1.5",
					rx: "0.75",
					transform: "rotate(90 2.5 1.5)"
				}),
				U("rect", {
					x: "9.33333",
					y: "1.5",
					width: "5",
					height: "1.5",
					rx: "0.75",
					transform: "rotate(90 9.33333 1.5)"
				}),
				U("rect", {
					x: "16.1667",
					y: "1.5",
					width: "5",
					height: "1.5",
					rx: "0.75",
					transform: "rotate(90 16.1667 1.5)"
				}),
				U("rect", {
					x: "23",
					y: "1.5",
					width: "5",
					height: "1.5",
					rx: "0.75",
					transform: "rotate(90 23 1.5)"
				}),
				U("path", { d: "M2.16873 14.2715C2.08963 14.3652 2.02518 14.4253 1.97537 14.4517C1.9285 14.478 1.8699 14.4912 1.79959 14.4912C1.66189 14.4912 1.55057 14.4458 1.46561 14.355C1.38357 14.2612 1.34256 14.1074 1.34256 13.8936V13.2871C1.34256 13.0703 1.38357 12.9165 1.46561 12.8257C1.55057 12.7319 1.66189 12.6851 1.79959 12.6851C1.90506 12.6851 1.99295 12.7129 2.06326 12.7686C2.1365 12.8242 2.19217 12.918 2.23025 13.0498C2.26834 13.1787 2.30789 13.2666 2.34891 13.3135C2.43387 13.4043 2.58475 13.4966 2.80154 13.5903C3.01834 13.6841 3.25564 13.731 3.51346 13.731C3.91482 13.731 4.24441 13.6372 4.50223 13.4497C4.66629 13.3354 4.74832 13.1948 4.74832 13.0278C4.74832 12.9165 4.70877 12.8125 4.62967 12.7158C4.55057 12.6162 4.42166 12.5342 4.24295 12.4697C4.12576 12.4258 3.86355 12.3657 3.45633 12.2896C2.96414 12.1987 2.59207 12.0889 2.34012 11.96C2.08816 11.8311 1.88895 11.6494 1.74246 11.415C1.59598 11.1807 1.52273 10.9272 1.52273 10.6548C1.52273 10.2241 1.70291 9.84766 2.06326 9.52539C2.42361 9.2002 2.89236 9.0376 3.46951 9.0376C3.70096 9.0376 3.91482 9.06396 4.11111 9.1167C4.31033 9.1665 4.49051 9.24414 4.65164 9.34961C4.76883 9.23535 4.88602 9.17822 5.0032 9.17822C5.13504 9.17822 5.24197 9.2251 5.324 9.31885C5.40897 9.40967 5.45145 9.56201 5.45145 9.77588V10.4526C5.45145 10.6694 5.40897 10.8247 5.324 10.9185C5.24197 11.0093 5.13504 11.0547 5.0032 11.0547C4.89188 11.0547 4.7952 11.021 4.71316 10.9536C4.64871 10.9038 4.60037 10.8042 4.56814 10.6548C4.53592 10.5054 4.4949 10.3984 4.4451 10.334C4.36014 10.2227 4.2327 10.1289 4.06277 10.0527C3.89285 9.97656 3.69656 9.93848 3.47391 9.93848C3.14871 9.93848 2.8909 10.0146 2.70047 10.167C2.51297 10.3164 2.41922 10.4731 2.41922 10.6372C2.41922 10.7485 2.4573 10.8569 2.53348 10.9624C2.61258 11.0649 2.72684 11.1455 2.87625 11.2041C2.97586 11.2451 3.25564 11.311 3.71561 11.4019C4.1785 11.4927 4.53299 11.5923 4.77908 11.7007C5.02811 11.8091 5.23465 11.979 5.39871 12.2104C5.56277 12.4419 5.6448 12.7173 5.6448 13.0366C5.6448 13.4819 5.48807 13.8379 5.17459 14.1045C4.75857 14.4561 4.2283 14.6318 3.58377 14.6318C3.33475 14.6318 3.09158 14.6011 2.85428 14.5396C2.6199 14.481 2.39139 14.3916 2.16873 14.2715ZM9.615 12.2632V13.5991H10.2214C10.4382 13.5991 10.5921 13.6416 10.6829 13.7266C10.7766 13.8086 10.8235 13.917 10.8235 14.0518C10.8235 14.1836 10.7766 14.292 10.6829 14.377C10.5921 14.459 10.4382 14.5 10.2214 14.5H8.10768C7.89381 14.5 7.74 14.459 7.64625 14.377C7.55543 14.292 7.51002 14.1821 7.51002 14.0474C7.51002 13.9155 7.55543 13.8086 7.64625 13.7266C7.74 13.6416 7.89381 13.5991 8.10768 13.5991H8.71412V12.2632L7.22438 10.0747C7.02516 10.0747 6.87867 10.0322 6.78492 9.94727C6.6941 9.8623 6.64869 9.75391 6.64869 9.62207C6.64869 9.4873 6.6941 9.37891 6.78492 9.29688C6.87867 9.21191 7.03395 9.16943 7.25074 9.16943L8.06813 9.17383C8.28492 9.17383 8.43873 9.21484 8.52955 9.29688C8.6233 9.37891 8.67018 9.4873 8.67018 9.62207C8.67018 9.82422 8.55152 9.9751 8.31422 10.0747L9.16676 11.3315L10.0017 10.0747C9.86988 10.0249 9.77613 9.96191 9.72047 9.88574C9.6648 9.80957 9.63697 9.72168 9.63697 9.62207C9.63697 9.4873 9.68238 9.37891 9.7732 9.29688C9.86695 9.21484 10.0222 9.17236 10.239 9.16943L11.0872 9.17383C11.304 9.17383 11.4578 9.21484 11.5486 9.29688C11.6423 9.37891 11.6892 9.4873 11.6892 9.62207C11.6892 9.75684 11.6423 9.8667 11.5486 9.95166C11.4548 10.0337 11.3025 10.0747 11.0916 10.0747L9.615 12.2632ZM13.7082 10.8745V13.5991H14.0334C14.2502 13.5991 14.404 13.6416 14.4949 13.7266C14.5886 13.8086 14.6355 13.917 14.6355 14.0518C14.6355 14.1836 14.5886 14.292 14.4949 14.377C14.404 14.459 14.2502 14.5 14.0334 14.5H12.8513C12.6345 14.5 12.4792 14.459 12.3855 14.377C12.2947 14.292 12.2493 14.1821 12.2493 14.0474C12.2493 13.9185 12.2947 13.8115 12.3855 13.7266C12.4763 13.6416 12.6169 13.5991 12.8074 13.5991V10.0747H12.6667C12.4499 10.0747 12.2947 10.0337 12.2009 9.95166C12.1101 9.8667 12.0647 9.75684 12.0647 9.62207C12.0647 9.4873 12.1101 9.37891 12.2009 9.29688C12.2947 9.21191 12.4499 9.16943 12.6667 9.16943L13.7082 9.17383L16.011 12.7861V10.0747H15.6858C15.469 10.0747 15.3137 10.0337 15.22 9.95166C15.1291 9.8667 15.0837 9.75684 15.0837 9.62207C15.0837 9.4873 15.1291 9.37891 15.22 9.29688C15.3137 9.21191 15.469 9.16943 15.6858 9.16943L16.8679 9.17383C17.0847 9.17383 17.2385 9.21484 17.3293 9.29688C17.4231 9.37891 17.47 9.4873 17.47 9.62207C17.47 9.75391 17.4246 9.8623 17.3337 9.94727C17.2429 10.0322 17.1038 10.0747 16.9163 10.0747V14.5H16.0242L13.7082 10.8745ZM21.9236 9.40234C21.9792 9.32617 22.0393 9.26904 22.1037 9.23096C22.1711 9.19287 22.2429 9.17383 22.3191 9.17383C22.4509 9.17383 22.5578 9.21924 22.6399 9.31006C22.7248 9.40088 22.7673 9.55469 22.7673 9.77148V10.5361C22.7673 10.7529 22.7248 10.9082 22.6399 11.002C22.5578 11.0928 22.4509 11.1382 22.3191 11.1382C22.1989 11.1382 22.1023 11.1045 22.029 11.0371C21.9558 10.9697 21.9016 10.8438 21.8664 10.6592C21.8459 10.5361 21.8049 10.4409 21.7434 10.3735C21.6233 10.2417 21.4548 10.1362 21.238 10.0571C21.0241 9.97803 20.8088 9.93848 20.592 9.93848C20.3225 9.93848 20.0749 9.99707 19.8493 10.1143C19.6237 10.2314 19.4245 10.4219 19.2517 10.6855C19.0788 10.9492 18.9924 11.2627 18.9924 11.626V12.2104C18.9924 12.644 19.1491 13.0059 19.4626 13.2959C19.779 13.5859 20.217 13.731 20.7766 13.731C21.1106 13.731 21.3933 13.6855 21.6247 13.5947C21.7595 13.542 21.903 13.438 22.0554 13.2827C22.1491 13.189 22.2224 13.1289 22.2751 13.1025C22.3279 13.0732 22.3879 13.0586 22.4553 13.0586C22.5754 13.0586 22.6809 13.104 22.7717 13.1948C22.8625 13.2856 22.9079 13.3926 22.9079 13.5156C22.9079 13.6387 22.8464 13.7705 22.7234 13.9111C22.5446 14.1162 22.3147 14.2773 22.0334 14.3945C21.6555 14.5527 21.238 14.6318 20.781 14.6318C20.2478 14.6318 19.7673 14.522 19.3396 14.3022C18.9939 14.1265 18.6994 13.8496 18.4563 13.4717C18.2131 13.0908 18.0915 12.6763 18.0915 12.228V11.6172C18.0915 11.1484 18.1999 10.7119 18.4167 10.3076C18.6364 9.90039 18.9397 9.58691 19.3264 9.36719C19.7131 9.14746 20.1233 9.0376 20.5569 9.0376C20.8176 9.0376 21.0608 9.06836 21.2863 9.12988C21.5149 9.18848 21.7273 9.2793 21.9236 9.40234Z" }),
				U("rect", {
					x: "23",
					y: "22.5",
					width: "22",
					height: "2",
					rx: "1",
					transform: "rotate(-180 23 22.5)"
				}),
				U("rect", {
					x: "21.5",
					y: "22.5",
					width: "5",
					height: "1.5",
					rx: "0.75",
					transform: "rotate(-90 21.5 22.5)"
				}),
				U("rect", {
					x: "14.6667",
					y: "22.5",
					width: "5",
					height: "1.5",
					rx: "0.75",
					transform: "rotate(-90 14.6667 22.5)"
				}),
				U("rect", {
					x: "7.83333",
					y: "22.5",
					width: "5",
					height: "1.5",
					rx: "0.75",
					transform: "rotate(-90 7.83333 22.5)"
				}),
				U("rect", {
					x: "1",
					y: "22.5",
					width: "5",
					height: "1.5",
					rx: "0.75",
					transform: "rotate(-90 1 22.5)"
				})
			]
		})
	}) : null;
}, LA = function(e, t) {
	var n = (0, B.useRef)(null);
	(0, B.useLayoutEffect)(function() {
		var r = e.current;
		if (r) return n.current = requestAnimationFrame(function() {
			r.style.transform = `translateX(${t}px)`;
		}), function() {
			n.current &&= (cancelAnimationFrame(n.current), null);
		};
	}, [e, t]);
}, RA = {
	rulerArea: "RulerArea-module_rulerArea__Kix1O",
	rulerInput: "RulerArea-module_rulerInput__nCNOa",
	rulerInputDragging: "RulerArea-module_rulerInputDragging__saoOk",
	rulerScale: "RulerArea-module_rulerScale__4YOKH",
	rulerHandle: "RulerArea-module_rulerHandle__g4GPl"
}, zA = (0, B.memo)(function(e) {
	var t = e.lineLengthValue, n = e.offsetX, r = e.isDragging, i = e.layoutMode, o = e.onCommitValue, s = (0, B.useRef)(null);
	LA(s, n);
	var c = t.toString(), l = (0, B.useState)(null), u = R(l, 2), d = u[0], f = u[1], p = d === null ? c : d;
	return U("input", {
		className: a(RA.rulerInput, r && RA.rulerInputDragging),
		title: "Number of monomers in a line",
		type: "text",
		inputMode: "numeric",
		pattern: "[0-9]*",
		value: p,
		onChange: function(e) {
			f(e.target.value);
		},
		onBlur: function() {
			if (!d || d.trim() === "") f(null);
			else {
				var e = Number(d);
				if (Number.isNaN(e) || e < 1) f(null);
				else {
					var t = i === "sequence-layout-mode" ? Math.round(e / 10) * 10 : e;
					f(null), o(t);
				}
			}
		},
		onKeyDown: function(e) {
			e.key === "Enter" && (e.preventDefault(), e.currentTarget.blur());
		},
		"data-testid": "ruler-input",
		disabled: r,
		ref: s
	});
}), BA = 40, VA = 20, HA = 10, UA = 25, WA = 60, GA = (0, B.memo)(function(e) {
	var t = e.transform, n = e.layoutMode;
	e.lineLengthValue;
	var r = (0, B.useRef)(null), i = t.k - .5 < 2 ** -52, a = function(e, t, n, r) {
		var i = Math.max(0, Math.floor((e - r) / n)), a = Math.ceil((t - r) / n) + 10;
		return Array.from({ length: a - i }, function(e, t) {
			return r + (i + t) * n;
		});
	}, o = (0, B.useMemo)(function() {
		var e, i = ((e = r.current) == null || (e = e.ownerSVGElement) == null ? void 0 : e.width.baseVal.value) || 1e3, o = t.invertX(0), s = t.invertX(i);
		return n === "sequence-layout-mode" ? a(o, s, 10 * VA + HA, BA) : n === "snake-layout-mode" ? a(o, s, WA, UA) : [];
	}, [n, t]), s = (0, B.useMemo)(function() {
		var e = [];
		return o.forEach(function(r, a) {
			n === "sequence-layout-mode" ? e.push(U("line", {
				x1: t.applyX(r),
				y1: 14,
				x2: t.applyX(r),
				y2: 22,
				stroke: "#7C7C7F",
				strokeWidth: 1
			}, `ruler-mark-${r}`)) : n === "snake-layout-mode" && (i ? a % 5 == 0 ? e.push(U("text", {
				x: t.applyX(r),
				y: 18,
				fontSize: 10,
				fontWeight: 500,
				fill: "#7C7C7F",
				textAnchor: "middle",
				dominantBaseline: "middle",
				children: a
			}, `ruler-label-${r}`)) : e.push(U("line", {
				x1: t.applyX(r),
				y1: 14,
				x2: t.applyX(r),
				y2: 22,
				stroke: "#7C7C7F",
				strokeWidth: 1
			}, `ruler-mark-${r}`)) : e.push(U("text", {
				x: t.applyX(r),
				y: 18,
				fontSize: 10,
				fontWeight: 500,
				fill: "#7C7C7F",
				textAnchor: "middle",
				dominantBaseline: "middle",
				children: a
			}, `ruler-label-${r}`)));
			var s = o[a + 1];
			s !== void 0 && (i && n === "snake-layout-mode" || e.push(U("line", {
				x1: t.applyX(r + 10),
				y1: 18,
				x2: t.applyX(s - 10),
				y2: 18,
				stroke: "#B4B9D6",
				strokeDasharray: "2,2",
				strokeWidth: 1
			}, `ruler-fill-${r}-${s}`)));
		}), e;
	}, [
		o,
		n,
		t,
		i
	]);
	return U("svg", {
		className: RA.rulerScale,
		ref: r,
		"data-testid": "ruler-scale",
		children: s
	});
}), KA = (0, B.memo)(function(e) {
	var t = e.offsetX, n = e.onDragStart, r = e.onDrag, i = e.onDragEnd, a = (0, B.useRef)(null), o = (0, B.useRef)(null);
	return LA(a, t), (0, B.useEffect)(function() {
		if (o.current) {
			var e = Jd(o.current), t = uf().on("start", n).on("drag", r).on("end", i);
			return e.call(t), function() {
				e.on(".drag", null);
			};
		}
	}, [
		r,
		i,
		n
	]), U("svg", {
		xmlns: "http://www.w3.org/2000/svg",
		className: RA.rulerHandle,
		viewBox: "0 0 16 13",
		fill: "none",
		pointerEvents: "none",
		ref: a,
		"data-testid": "ruler-handle",
		children: W("g", {
			cursor: "pointer",
			pointerEvents: "all",
			ref: o,
			children: [
				U("mask", {
					id: "ruler-handle-mask",
					fill: "#fff",
					children: U("path", {
						fillRule: "evenodd",
						d: "M16 1.625a1 1 0 0 0-1-1H1a1 1 0 0 0-1 1v4.5a1 1 0 0 0 .4.8l7 5.25a1 1 0 0 0 1.2 0l7-5.25a1 1 0 0 0 .4-.8v-4.5Z",
						clipRule: "evenodd"
					})
				}),
				U("path", {
					fill: "#CAD3DD",
					fillRule: "evenodd",
					d: "M16 1.625a1 1 0 0 0-1-1H1a1 1 0 0 0-1 1v4.5a1 1 0 0 0 .4.8l7 5.25a1 1 0 0 0 1.2 0l7-5.25a1 1 0 0 0 .4-.8v-4.5Z",
					clipRule: "evenodd"
				}),
				U("path", {
					fill: "#B4B9D6",
					d: "m15.6 6.925-.6-.8.6.8Zm-8.2 5.25.6-.8-.6.8Zm-7-5.25.6-.8-.6.8Zm.6-5.3h14v-2H1v2Zm0 4.5v-4.5h-2v4.5h2Zm7 5.25-7-5.25-1.2 1.6 7 5.25 1.2-1.6Zm7-5.25-7 5.25 1.2 1.6 7-5.25-1.2-1.6Zm0-4.5v4.5h2v-4.5h-2Zm1.2 6.1a2 2 0 0 0 .8-1.6h-2l1.2 1.6Zm-9.4 5.25a2 2 0 0 0 2.4 0l-1.2-1.6-1.2 1.6ZM-1 6.125a2 2 0 0 0 .8 1.6l1.2-1.6h-2Zm16-4.5h2a2 2 0 0 0-2-2v2Zm-14-2a2 2 0 0 0-2 2h2v-2Z",
					mask: "url(#ruler-handle-mask)"
				})
			]
		})
	});
}), qA = function() {
	var e = (0, B.useState)(new gg(1, 0, 0)), t = R(e, 2), n = t[0], r = t[1];
	return (0, B.useEffect)(function() {
		var e = Ke.instance;
		if (e) {
			var t = function(e) {
				e && requestAnimationFrame(function() {
					r(e);
				});
			};
			return e.subscribeOnZoomEvent(t), function() {
				e.unsubscribeOnZoomEvent(t);
			};
		}
	}, [Ke.instance]), n;
}, JA = function() {
	var e, t, n, r = yx(), i = dt(a_)[r], o = dt(K), s = (0, B.useRef)(0), c = (0, B.useState)(0), l = R(c, 2), u = l[0], d = l[1], f = (0, B.useState)(!1), p = R(f, 2), m = p[0], h = p[1], g = qA(), _ = i / 10 - 1, v = (0, B.useMemo)(function() {
		if (r === "sequence-layout-mode") {
			var e = 10 * VA + HA;
			return BA + Math.floor(i / 10) * e;
		}
		return r === "snake-layout-mode" ? UA + i * WA : 0;
	}, [r, i]), y = (0, B.useMemo)(function() {
		var e = g.applyX(v) + u, t = e - 8, n = e + 10, r = o?.canvas.width.baseVal.value;
		if (!r) return [n, t];
		var i = o?.canvas.parentElement, a = i?.scrollLeft || 0, s = a, c = a + (i?.clientWidth || r);
		return n + 35 > c && (n = c - 35), n < s && (n = s), [n, t];
	}, [
		o?.canvas.width.baseVal.value,
		o?.canvas.parentElement,
		g,
		v,
		u
	]), b = R(y, 2), x = b[0], S = b[1], C = (0, B.useCallback)(function(e) {
		o?.events.setEditorLineLength.dispatch(I({}, r, e));
	}, [o == null || (e = o.events) == null ? void 0 : e.setEditorLineLength, r]), w = (0, B.useCallback)(function(e) {
		if (r === "sequence-layout-mode") {
			var t = (e - _ * HA - BA) / VA;
			return Math.max(10, Math.round(t / 10) * 10);
		}
		if (r === "snake-layout-mode") {
			var n = (e - UA) / WA;
			return Math.max(1, Math.round(n));
		}
		return i;
	}, [
		r,
		_,
		i
	]), T = (0, B.useCallback)(function(e) {
		var t = e - s.current, n = g.applyX(v) + t;
		return [t, g.invertX(n)];
	}, [g, v]), E = (0, B.useMemo)(function() {
		if (!m) return i;
		var e = T(s.current + u), t = R(e, 2)[1];
		return w(t);
	}, [
		m,
		i,
		T,
		s,
		u,
		w
	]), D = (0, B.useCallback)(function(e) {
		h(!0), s.current = e.sourceEvent.clientX, o?.events.toggleLineLengthHighlighting.dispatch(!0, v);
	}, [o == null || (t = o.events) == null ? void 0 : t.toggleLineLengthHighlighting, v]), O = (0, B.useCallback)(function(e) {
		var t = T(e.sourceEvent.clientX), n = R(t, 2), r = n[0], i = n[1];
		d(r), o?.events.toggleLineLengthHighlighting.dispatch(!0, i);
	}, [o == null || (n = o.events) == null ? void 0 : n.toggleLineLengthHighlighting, T]), k = (0, B.useCallback)(function(e) {
		h(!1);
		var t = T(e.sourceEvent.clientX), n = R(t, 2)[1], r = w(n);
		r !== i && C(r), d(0), s.current = 0, o?.events.toggleLineLengthHighlighting.dispatch(!1);
	}, [
		T,
		w,
		i,
		o?.events.toggleLineLengthHighlighting,
		C
	]);
	return r === "flex-layout-mode" || window._ketcher_isChainLengthRulerDisabled ? null : W("div", {
		className: a(RA.rulerArea, m && RA.rulerAreaDragging),
		"data-testid": "ruler-area",
		children: [
			U(zA, {
				lineLengthValue: m ? E : i,
				offsetX: x,
				isDragging: m,
				layoutMode: r,
				onCommitValue: C
			}),
			U(KA, {
				offsetX: S,
				onDragStart: D,
				onDrag: O,
				onDragEnd: k
			}),
			U(GA, {
				transform: g,
				layoutMode: r,
				lineLengthValue: i
			})
		]
	});
}, YA = { dragGhost: "DragGhost-module_dragGhost__m5lHf" }, XA = function(e) {
	var t = e.preset, n = t.sugar, r = t.phosphate, i = t.base;
	if (!n) return null;
	var a = ct(n), o = R(a, 2), s = o[0], c = o[1], l = new c(new s(n)), u = r ? function() {
		var e = ct(r), t = R(e, 2), n = t[0], i = t[1];
		return new i(new n(r));
	}() : null, d = i ? function() {
		var e = ct(i), t = R(e, 2), n = t[0], r = t[1];
		return new r(new n(i));
	}() : null, f = l.monomerSize, p = u?.monomerSize, m = d?.monomerSize, h = (t.phosphatePosition ?? ie(t)) === "left", g = p && h ? p.width + 30 : 0, _ = 0, v = 0;
	p && (v = h ? 0 : g + f.width + 30);
	var y = _, b = g + (f.width - (m?.width || 0)) / 2, x = _ + f.height + 30, S = Math.max(g + f.width, p ? v + p.width : 0, m ? b + m.width : 0), C = Math.max(_ + f.height, p ? y + p.height : 0, m ? x + m.height : 0), w = 2, T = (f.width - w * 2) / f.width, E = (f.height - w * 2) / f.height, D = Math.min(T, E), O = (f.width - f.width * D) / 2, k = (f.height - f.height * D) / 2, A = p ? Math.min((p.width - w * 2) / p.width, (p.height - w * 2) / p.height) : 1, j = p ? (p.width - p.width * A) / 2 : 0, ee = p ? (p.height - p.height * A) / 2 : 0, te = m ? Math.min((m.width - w * 2) / m.width, (m.height - w * 2) / m.height) : 1, M = m ? (m.width - m.width * te) / 2 : 0, ne = m ? (m.height - m.height * te) / 2 : 0, re = 4, N = 6;
	return U("svg", {
		xmlns: "http://www.w3.org/2000/svg",
		width: S,
		height: C,
		viewBox: `0 0 ${S} ${C}`,
		overflow: "visible",
		children: W("g", {
			style: { filter: "drop-shadow(0px 2px 2px rgba(0, 0, 0, 0.4))" },
			children: [
				W("g", {
					transform: `translate(${g}, ${_})`,
					children: [
						U("use", {
							href: l.monomerSymbolElementId,
							fill: "white"
						}),
						U("g", {
							transform: `translate(${O}, ${k}) scale(${D})`,
							children: U("use", {
								href: l.monomerSymbolElementId,
								fill: "#CAD3DD"
							})
						}),
						U("text", {
							x: f.width / 2,
							y: f.height / 2,
							textAnchor: "middle",
							dominantBaseline: "central",
							pointerEvents: "none",
							fill: "#333",
							fontSize: "7px",
							fontWeight: "bold",
							children: n.label
						})
					]
				}),
				p && W("g", {
					transform: `translate(${v}, ${y})`,
					children: [
						U("use", {
							href: u.monomerSymbolElementId,
							fill: "white"
						}),
						U("g", {
							transform: `translate(${j}, ${ee}) scale(${A})`,
							children: U("use", {
								href: u.monomerSymbolElementId,
								fill: "#CAD3DD"
							})
						}),
						U("text", {
							x: p.width / 2,
							y: p.height / 2,
							textAnchor: "middle",
							dominantBaseline: "central",
							pointerEvents: "none",
							fill: "#333",
							fontSize: "7px",
							fontWeight: "bold",
							children: r?.label
						})
					]
				}),
				m && W("g", {
					transform: `translate(${b}, ${x})`,
					children: [
						U("use", {
							href: d.monomerSymbolElementId,
							fill: "white"
						}),
						U("g", {
							transform: `translate(${M}, ${ne}) scale(${te})`,
							children: U("use", {
								href: d.monomerSymbolElementId,
								fill: "#CAD3DD"
							})
						}),
						U("text", {
							x: m.width / 2,
							y: m.height / 2,
							textAnchor: "middle",
							dominantBaseline: "central",
							pointerEvents: "none",
							fill: "#333",
							fontSize: "7px",
							fontWeight: "bold",
							children: i?.label
						})
					]
				}),
				p && W("g", { children: [U("line", {
					x1: h ? v + p.width : g + f.width,
					y1: _ + f.height / 2,
					x2: h ? g + N / 3 : v + N / 3,
					y2: y + p.height / 2,
					stroke: "white",
					strokeWidth: 7,
					strokeLinecap: "butt"
				}), U("line", {
					x1: h ? v + p.width - N / 2 : g + f.width - N / 2,
					y1: _ + f.height / 2,
					x2: h ? g + N / 2 : v + N / 2,
					y2: y + p.height / 2,
					stroke: "#CAD3DD",
					strokeWidth: re,
					strokeLinecap: "round"
				})] }),
				m && W("g", { children: [U("line", {
					x1: g + f.width / 2,
					y1: _ + f.height,
					x2: b + m.width / 2,
					y2: x + N / 2,
					stroke: "white",
					strokeWidth: 7,
					strokeLinecap: "butt"
				}), U("line", {
					x1: g + f.width / 2,
					y1: _ + f.height - N / 2,
					x2: b + m.width / 2,
					y2: x + N / 2,
					stroke: "#CAD3DD",
					strokeWidth: re,
					strokeLinecap: "round"
				})] })
			]
		})
	});
}, ZA = function(e) {
	var t = e.monomerItem, n = (0, B.useMemo)(function() {
		if (w(t)) {
			var e = new mn(t);
			return new Dn(e);
		}
		var n = ct(t), r = R(n, 2), i = r[0], a = r[1];
		return new a(new i(t));
	}, [t]), r = n.monomerSymbolElementId, i = n.monomerSize, a = i.width, o = i.height;
	return W("svg", {
		xmlns: "http://www.w3.org/2000/svg",
		width: a,
		height: o,
		viewBox: `0 0 ${a} ${o}`,
		overflow: "visible",
		children: [U("use", {
			href: r,
			fill: "#CAD3DD",
			stroke: "white",
			strokeWidth: 2,
			style: { filter: "drop-shadow(0px 2px 2px rgba(0, 0, 0, 0.4))" }
		}), U("text", {
			x: a / 2,
			y: o / 2,
			textAnchor: "middle",
			dominantBaseline: "central",
			pointerEvents: "none",
			fill: "#333",
			fontSize: "7px",
			fontWeight: "bold",
			children: t.label
		})]
	});
}, QA = function() {
	var e, t, n = dt(K), r = (0, B.useState)(null), i = R(r, 2), a = i[0], o = i[1], s = (0, B.useRef)(null), c = (0, B.useRef)(null), l = (0, B.useRef)(null), u = qA();
	(0, B.useEffect)(function() {
		if (n) {
			var e = function(e) {
				o(e);
			};
			return n.events.setLibraryItemDragState.add(e), function() {
				n.events.setLibraryItemDragState.remove(e);
			};
		}
	}, [n]), (0, B.useEffect)(function() {
		if (Ke.instance && a) {
			var e = Ke.instance.canvasWrapper.node();
			e && (l.current = e.getBoundingClientRect());
		}
	}, [a]);
	var d = (n == null || (e = n.ketcherRootElementBoundingClientRect) == null ? void 0 : e.left) || 0, f = (n == null || (t = n.ketcherRootElementBoundingClientRect) == null ? void 0 : t.top) || 0, p = l.current && a && a.position.x + d >= l.current.left && a.position.x + d <= l.current.right && a.position.y + f >= l.current.top && a.position.y + f <= l.current.bottom;
	return (0, B.useLayoutEffect)(function() {
		var e = s.current;
		if (e && a) return c.current = requestAnimationFrame(function() {
			var t = a.position, n = t.x, r = t.y;
			if (p && l.current) {
				var i = u.k;
				e.style.transformOrigin = "0 0", e.style.transform = `translate(${n}px, ${r}px) scale(${i})`;
			} else e.style.transform = `translate(${n}px, ${r}px)`;
		}), function() {
			c.current &&= (cancelAnimationFrame(c.current), null);
		};
	}, [
		p,
		a,
		u.k
	]), a ? U("div", {
		className: YA.dragGhost,
		ref: s,
		"data-testid": "drag-ghost",
		children: Xt(a.item) ? U(XA, { preset: a.item }) : U(ZA, { monomerItem: a.item })
	}) : null;
}, $A, ej, tj, nj, rj;
function ij() {
	return ij = Object.assign ? Object.assign.bind() : function(e) {
		for (var t = 1; t < arguments.length; t++) {
			var n = arguments[t];
			for (var r in n) ({}).hasOwnProperty.call(n, r) && (e[r] = n[r]);
		}
		return e;
	}, ij.apply(null, arguments);
}
function aj(e) {
	return /*#__PURE__*/ B.createElement("svg", ij({
		width: 22,
		height: 24,
		viewBox: "0 0 22 24",
		fill: "none",
		xmlns: "http://www.w3.org/2000/svg"
	}, e), $A ||= /*#__PURE__*/ B.createElement("path", {
		fill: "transparent",
		d: "M0 0h21.503v24H0z"
	}), ej ||= /*#__PURE__*/ B.createElement("path", {
		d: "M13.507 18.936l-2.04-1.92c-.7-.659-1.403-1.317-2.108-1.983v3.097c0 .43.003.86.007 1.289 0 .049-.007.09-.007.126v2.04c0 .834 0 1.557.003 2.02l.278.163c.719.3 1.434.307 2.151.033l4.264-2.469c-.358-.326-1.395-1.31-2.548-2.396zM6.159 19.39v-1.091L6.163 2.23v-.002L1.26 5.059C.421 5.647.002 6.482.002 7.553c0 2.944.006 5.888-.002 8.831-.003 1.08.398 1.913 1.212 2.517l4.946 2.856v-2.318-.05z",
		fill: "#676767"
	}), tj ||= /*#__PURE__*/ B.createElement("path", {
		d: "M18.642 4.137l1.672.966c.785.58 1.187 1.385 1.188 2.41v8.974c0 1-.385 1.79-1.133 2.367l-1.423.822h-.004c-.097-.097-6.384-6.375-6.513-6.386.044-.044.56-.582 1.278-1.33L20.3 5.097l-1.658-.96z",
		fill: "url(#logo_svg__paint0_linear_5175_84899)"
	}), nj ||= /*#__PURE__*/ B.createElement("path", {
		d: "M17.335 3.383L11.849.216c-.718-.29-1.455-.29-2.219.011l-.27.139s0 10.346.041 11.106c.341-.346 7.808-7.96 7.934-8.09z",
		fill: "url(#logo_svg__paint1_linear_5175_84899)"
	}), rj ||= /*#__PURE__*/ B.createElement("defs", null, /*#__PURE__*/ B.createElement("linearGradient", {
		id: "logo_svg__paint0_linear_5175_84899",
		x1: 19.854,
		y1: 4.363,
		x2: 11.579,
		y2: 13.111,
		gradientUnits: "userSpaceOnUse"
	}, /*#__PURE__*/ B.createElement("stop", { stopColor: "#3BC2D7" }), /*#__PURE__*/ B.createElement("stop", {
		offset: .74,
		stopColor: "#1D9DB1"
	})), /*#__PURE__*/ B.createElement("linearGradient", {
		id: "logo_svg__paint1_linear_5175_84899",
		x1: 19.854,
		y1: 4.363,
		x2: 11.579,
		y2: 13.111,
		gradientUnits: "userSpaceOnUse"
	}, /*#__PURE__*/ B.createElement("stop", { stopColor: "#3BC2D7" }), /*#__PURE__*/ B.createElement("stop", {
		offset: .74,
		stopColor: "#1D9DB1"
	}))));
}
var oj = z("div", { target: "e1dr48d30" })(function(e) {
	var t, n, r = e.theme;
	return {
		width: "430px",
		minHeight: "260px",
		padding: "0 18px",
		borderRadius: "6px",
		fontSize: "12px",
		color: r.ketcher.color.text.primary,
		fontWeight: (t = r.ketcher) == null || (t = t.font) == null || (t = t.weight) == null ? void 0 : t.regular,
		a: { color: "#167782" },
		".body": {
			borderRadius: "6px",
			padding: "5px 65px",
			overflowY: "auto",
			overflowX: "hidden",
			".versionName": {
				fontWeight: 400,
				marginBottom: "2px"
			},
			".firstline": { display: "inline-block" },
			".links": { textAlign: "right" },
			".indigoVersion": {
				marginTop: "20px",
				display: "flex",
				gap: "2px"
			}
		},
		".headerContent": {
			display: "flex",
			justifyContent: "space-between",
			padding: "0 30px",
			a: {
				display: "flex",
				alignItems: "center",
				gap: "10px",
				textDecoration: "none",
				color: (n = r.ketcher) == null || (n = n.color) == null || (n = n.text) == null ? void 0 : n.primary
			},
			".title": {
				fontSize: "20px",
				lineHeight: "22px"
			}
		},
		".indigoFirstLine": { display: "inline-block" },
		dd: {
			margin: 0,
			marginBottom: "0.2em"
		},
		dt: { marginTop: "3px" },
		".okButton": {
			border: "1px solid #333333",
			backgroundColor: "#FFFFFF",
			color: "#333333",
			display: "inline-flex",
			justifyContent: "center",
			alignItems: "center",
			outline: "none",
			minWidth: "70px",
			lineHeight: "14px",
			height: "24px",
			borderRadius: "4px",
			fontSize: "10px",
			"&:hover": {
				color: "#333333",
				border: "1px solid  #333333"
			},
			"&:active": {
				color: "#333333",
				border: "1px solid #333333"
			},
			"&:disabled": {
				color: "rgba(51, 51, 51, 0.7)",
				border: "1px solid rgba(51, 51, 51, 0.7)"
			}
		},
		".aboutFooter": {
			borderTop: "1px solid #e1e5ea",
			margin: 0,
			padding: "15px 0",
			display: "flex",
			justifyContent: "flex-end",
			alignItems: "center"
		}
	};
}, "");
function sj(e, t) {
	var n = Object.keys(e);
	if (Object.getOwnPropertySymbols) {
		var r = Object.getOwnPropertySymbols(e);
		t && (r = r.filter(function(t) {
			return Object.getOwnPropertyDescriptor(e, t).enumerable;
		})), n.push.apply(n, r);
	}
	return n;
}
function cj(e) {
	for (var t = 1; t < arguments.length; t++) {
		var n = arguments[t] == null ? {} : arguments[t];
		t % 2 ? sj(Object(n), !0).forEach(function(t) {
			I(e, t, n[t]);
		}) : Object.getOwnPropertyDescriptors ? Object.defineProperties(e, Object.getOwnPropertyDescriptors(n)) : sj(Object(n)).forEach(function(t) {
			Object.defineProperty(e, t, Object.getOwnPropertyDescriptor(n, t));
		});
	}
	return e;
}
function lj() {
	var e = X(), t = Z(o_);
	(0, B.useEffect)(function() {
		function n() {
			return r.apply(this, arguments);
		}
		function r() {
			return r = dn(Ds.default.mark(function n() {
				var r, i;
				return Ds.default.wrap(function(n) {
					for (;;) switch (n.prev = n.next) {
						case 0:
							if (r = ce.getIndigo(), !(r != null && r.info)) {
								n.next = 11;
								break;
							}
							return n.prev = 2, n.next = 5, r.info();
						case 5:
							i = n.sent, e(Vg(cj(cj({}, t), {}, { indigoVersion: i.indigoVersion ?? "" }))), n.next = 11;
							break;
						case 9: n.prev = 9, n.t0 = n.catch(2);
						case 11:
						case "end": return n.stop();
					}
				}, n, null, [[2, 9]]);
			})), r.apply(this, arguments);
		}
		n();
	}, [e]);
}
var uj = "http://lifescience.opensource.epam.com/ketcher/#feedback", dj = "https://lifescience.opensource.epam.com/ketcher/index.html", fj = "http://lifescience.opensource.epam.com/", pj = "http://lifescience.opensource.epam.com/indigo/";
function mj() {
	var e = arguments.length > 0 && arguments[0] !== void 0 ? arguments[0] : "";
	if (!e.includes("T")) return e;
	var t = e.split("T"), n = R(t, 2);
	return `${n[0]}; ${n[1]}`;
}
function hj(e) {
	var t = e.isOpen, n = e.onClose, r = X();
	lj();
	var i = Z(o_), a = i.buildDate, o = i.indigoVersion, s = i.version, c = mj(a), l = function() {
		r({ type: "MODAL_CLOSE" }), n();
	};
	return U(Q, {
		title: "",
		isOpen: t,
		onClose: l,
		hideHeaderBorder: !0,
		children: U(Q.Content, { children: W(oj, { children: [
			U("div", {
				className: "headerContent",
				children: W("a", {
					href: dj,
					target: "_blank",
					rel: "noopener noreferrer",
					children: [U(aj, {}), U("span", {
						className: "title",
						children: "Ketcher"
					})]
				})
			}),
			U("div", {
				className: "body",
				children: W("dl", { children: [
					U("dt", {
						"data-testid": "build-version",
						children: W("a", {
							href: dj,
							target: "_blank",
							rel: "noopener noreferrer",
							children: ["Version ", s]
						})
					}),
					W("dd", {
						"data-testid": "build-time",
						children: ["Build at ", U("time", { children: c })]
					}),
					W("div", {
						className: "infoLinks",
						children: [U("dt", { children: U("a", {
							href: uj,
							target: "_blank",
							rel: "noopener noreferrer",
							children: "Feedback"
						}) }), U("dt", { children: U("a", {
							href: fj,
							target: "_blank",
							rel: "noopener noreferrer",
							children: "EPAM Life Sciences"
						}) })]
					}),
					U("div", {
						className: "indigoVersion",
						children: U("a", {
							href: pj,
							target: "_blank",
							rel: "noopener noreferrer",
							children: "Indigo Toolkit"
						})
					}),
					U("div", {
						"data-testid": "build-indigo-version",
						children: o ? W("dd", { children: ["Version ", o] }) : U("p", { children: "Standalone" })
					})
				] })
			}),
			U("div", {
				className: "aboutFooter",
				children: U("button", {
					onClick: l,
					className: "okButton",
					"data-testid": "ok-button",
					children: "Ok"
				})
			})
		] }) })
	});
}
function gj(e, t) {
	var n = Object.keys(e);
	if (Object.getOwnPropertySymbols) {
		var r = Object.getOwnPropertySymbols(e);
		t && (r = r.filter(function(t) {
			return Object.getOwnPropertyDescriptor(e, t).enumerable;
		})), n.push.apply(n, r);
	}
	return n;
}
function _j(e) {
	for (var t = 1; t < arguments.length; t++) {
		var n = arguments[t] == null ? {} : arguments[t];
		t % 2 ? gj(Object(n), !0).forEach(function(t) {
			I(e, t, n[t]);
		}) : Object.getOwnPropertyDescriptors ? Object.defineProperties(e, Object.getOwnPropertyDescriptors(n)) : gj(Object(n)).forEach(function(t) {
			Object.defineProperty(e, t, Object.getOwnPropertyDescriptor(n, t));
		});
	}
	return e;
}
function vj() {
	var e = (0, B.useState)(!1), t = R(e, 2), n = t[0], r = t[1], i = {
		isOpen: n,
		onClose: function() {
			return r(!1);
		}
	};
	return W(H, { children: [W("div", {
		style: {
			display: "flex",
			alignItems: "center"
		},
		children: [U(oe, {
			iconName: "help",
			title: "Help (?)",
			onClick: function() {
				window.open("https://github.com/epam/ketcher/blob/master/documentation/help.md#ketcher-macromolecules-mode", "_blank");
			},
			testId: "help-button"
		}), U(oe, {
			iconName: "about",
			title: "About",
			onClick: function() {
				return r(!0);
			},
			testId: "about-button"
		})]
	}), U(hj, _j({}, i))] });
}
var yj = z("div", { target: "e1lzguhf1" })("position:absolute;left:", function(e) {
	return e.left;
}, "px;top:", function(e) {
	return e.top;
}, "px;display:flex;flex-direction:row;gap:8px;transform:translate(-50%, -100%) translateY(-10px);z-index:100;"), bj = z("button", { target: "e1lzguhf0" })({
	name: "11kiyhp",
	styles: "width:28px;height:28px;display:flex;align-items:center;justify-content:center;background:white;border:none;border-radius:4px;cursor:pointer;padding:0;color:#2b2f3a;box-shadow:0 6px 10px rgba(103, 104, 132, 0.15);&:hover{color:#188794;}&:active{background:#167782;color:#fff;}&>svg{width:20px;height:20px;}"
}), xj = .1, Sj = function() {
	var e = Z(K), t = (0, B.useState)(!1), n = R(t, 2), r = n[0], i = n[1], a = (0, B.useState)(new M(0, 0)), o = R(a, 2), s = o[0], c = o[1], l = (0, B.useRef)(new M(0, 0)), u = (0, B.useCallback)(function() {
		if (e) {
			var t = e.drawingEntitiesManager?.getSelectedEntitiesBoundingBox();
			if (t) {
				var n = (t.left + t.right) / 2, r = t.top - 1.7, i = N.modelToView(new M(n, r)), a = Math.abs(i.x - l.current.x), o = Math.abs(i.y - l.current.y);
				(a > xj || o > xj) && (l.current = i, c(i));
			}
		}
	}, [e]);
	return (0, B.useEffect)(function() {
		if (e) {
			var t = function() {
				var t = (e.drawingEntitiesManager?.selectedEntitiesArr ?? []).filter(function(e) {
					return e instanceof pt || e instanceof Hn;
				}), n = e.selectedTool instanceof qe && (e.selectedTool.mode === "rotating" || e.selectedTool.mode === "moving");
				t.length >= 2 && e.mode.modeName !== "sequence-layout-mode" && e.selectedTool instanceof qe && !n ? (u(), i(!0)) : i(!1);
			};
			return e.events.selectEntities.add(t), function() {
				e.events.selectEntities.remove(t);
			};
		}
	}, [e, u]), (0, B.useEffect)(function() {
		if (e && r) {
			var t = 0;
			return t = requestAnimationFrame(function n() {
				e.selectedTool instanceof qe && (e.selectedTool.mode === "rotating" || e.selectedTool.mode === "moving") ? i(!1) : (u(), t = requestAnimationFrame(n));
			}), function() {
				return cancelAnimationFrame(t);
			};
		}
	}, [
		e,
		r,
		u
	]), r ? W(yj, {
		left: s.x,
		top: s.y,
		children: [
			U(bj, {
				onClick: function() {
					e?.events.flipHorizontal.dispatch();
				},
				title: "Flip horizontally",
				"data-testid": "transform-flip-h",
				children: U(P, { name: "transform-flip-h" })
			}),
			U(bj, {
				onClick: function() {
					e?.events.flipVertical.dispatch();
				},
				title: "Flip vertically",
				"data-testid": "transform-flip-v",
				children: U(P, { name: "transform-flip-v" })
			}),
			U(bj, {
				onClick: function() {
					e?.events.deleteSelectedStructure.dispatch(), i(!1);
				},
				title: "Delete",
				"data-testid": "float-delete",
				children: U(P, { name: "delete" })
			})
		]
	}) : null;
}, Cj = Ze(kb);
function wj(e) {
	var t = e.onInit, n = e.ketcherId, r = e.theme, i = e.togglerComponent, a = e.monomersLibraryUpdate, o = e.monomersLibraryReplace, s = e.isMacromoleculesEditorTurnedOn, c = (0, B.useRef)(null), l = r ? (0, ws.merge)(Ob, r) : Ob, u = (0, ws.merge)(Cj, { ketcher: l });
	return (0, B.useEffect)(function() {
		Eb.dispatch(Eg(n));
	}, [n]), U(Vt, {
		store: Eb,
		children: W(Ln, {
			theme: u,
			children: [U(vt, { styles: Ab }), U(Cx, {
				rootRef: c,
				isMacromoleculesEditorTurnedOn: s,
				children: U(uD, {
					ref: c,
					className: D,
					children: U(Tj, {
						ketcherId: n,
						theme: l,
						togglerComponent: i,
						monomersLibraryUpdate: a,
						monomersLibraryReplace: o,
						onInit: t
					})
				})
			})]
		})
	});
}
function Tj(e) {
	var t = e.theme, n = e.togglerComponent, r = e.monomersLibraryUpdate, i = e.monomersLibraryReplace, a = e.onInit, o = X(), s = (0, B.useRef)(null), c = Z(cv), l = Z(K), u = Z(Yg), d = mD(), f = (0, B.useState)(!1), p = R(f, 2), m = p[0], h = p[1], g = bx(), _ = (0, B.useState)(), v = R(_, 2), y = v[0], b = v[1], x = (0, B.useState)(), S = R(x, 2), C = S[0], w = S[1], T = (0, B.useState)([]), E = R(T, 2), D = E[0], O = E[1], k = ft({ id: tS.FOR_SEQUENCE }).show, A = ft({ id: tS.FOR_SELECTED_MONOMERS }).show;
	(0, B.useEffect)(function() {
		return o(Og({
			theme: t,
			canvas: s.current,
			monomersLibraryUpdate: r,
			monomersLibraryReplace: i,
			onInit: a,
			onLibraryError: function(e) {
				o(Tg(e instanceof Error ? e.message : "Failed to load monomers library"));
			}
		})), function() {
			o(kg(null));
		};
	}, [o]), bD(), xD(), (0, B.useEffect)(function() {
		l?.events.rightClickSequence.add(function(e) {
			var t = R(e, 2), n = t[0], r = t[1];
			b(r), w(n), window.dispatchEvent(new Event("hidePreview")), o(jg(!0)), k({
				event: n,
				props: { sequenceItemRenderer: n.target.__data__ }
			});
		}), l?.events.rightClickPolymerBond.add(function(e) {
			var t = R(e, 2), n = t[0], r = t[1];
			w(n), O([]), A({
				event: n,
				props: { polymerBondRenderer: r }
			});
		}), l?.events.rightClickSelectedMonomers.add(function(e) {
			var t = R(e, 2), n = t[0], r = t[1];
			O(r), w(n), A({
				event: n,
				props: { selectedMonomers: r }
			});
		}), l?.events.rightClickCanvas.add(function(e) {
			var t = R(e, 2), n = t[0], r = t[1];
			w(n), window.dispatchEvent(new Event("hidePreview")), o(jg(!0)), O(r), A({
				event: n,
				props: { selectedMonomers: r }
			});
		}), l?.events.rightClickCanvasSequence.add(function(e) {
			var t = R(e, 2), n = t[0], r = t[1];
			w(n), window.dispatchEvent(new Event("hidePreview")), o(jg(!0)), b(r), k({
				event: n,
				props: {}
			});
		}), l?.events.toggleMacromoleculesPropertiesVisibility.add(function() {
			o(Pg({}));
		});
	}, [l]), (0, B.useEffect)(function() {
		return l?.zoomTool.observeCanvasResize(), function() {
			l?.zoomTool.destroy();
		};
	}, [l]), (0, B.useEffect)(function() {
		var e = function(e) {
			var t = e.detail;
			t && o(Rg(t));
		};
		return window.addEventListener(vn, e), function() {
			window.removeEventListener(vn, e);
		};
	}, [o]);
	var j = function(e) {
		o(nv(e));
	}, ee = (0, B.useCallback)(function() {
		h(function(e) {
			return !e;
		});
	}, []);
	return W(H, { children: [
		W(nx, { children: [
			W(nx.Top, {
				shortened: !m,
				"data-testid": "top-toolbar",
				children: [U(vA, {}), W(dD, { children: [
					U(IA, {}),
					U(qD, {}),
					U(ck, {}),
					U(fD, {
						className: g ? "toggler-component-wrapper--disabled" : "",
						children: n
					}),
					U(WD, {}),
					U(vj, {}),
					U(OD, {}),
					U(WD, {}),
					U(kA, {})
				] })]
			}),
			U(nx.Left, { children: U(yA, {}) }),
			W(nx.Main, { children: [
				U(NA, {}),
				U(JA, {}),
				W(pD, {
					id: "polymer-editor-canvas",
					"data-testid": "ketcher-canvas",
					"data-canvasmode": "macromolecules-mode",
					preserveAspectRatio: "xMidYMid meet",
					ref: s,
					width: "100%",
					height: "100%",
					style: {
						overflow: "hidden",
						overflowClipMargin: "content-box"
					},
					children: [
						W("defs", { children: [
							U(eD, {}),
							U($E, {}),
							U(tD, {}),
							U(nD, {}),
							U(rD, {}),
							U(iD, {}),
							U(aD, {}),
							U(sD, {}),
							U(oD, {})
						] }),
						U("g", {
							className: "drawn-structures",
							"data-testid": "drawn-structures"
						}),
						u && U("rect", {
							x: 0,
							y: 0,
							width: "100%",
							height: "100%",
							fill: "transparent",
							pointerEvents: "all"
						})
					]
				}),
				U(Sj, {}),
				d && U(CD, {})
			] }),
			U(nx.Right, {
				hide: m,
				children: U(lw, { toggleLibraryVisibility: ee })
			}),
			U(nx.Bottom, { children: U(dA, {}) }),
			U(nx.InsideRoot, { children: m && U(dw, { onClick: ee }) })
		] }),
		U(rk, {}),
		U(QA, {}),
		U(_O, {
			selections: y,
			contextMenuEvent: C
		}),
		U(PA, {
			selectedMonomers: D,
			contextMenuEvent: C
		}),
		U(JE, {}),
		U(lD, {}),
		U(nn, {
			anchorOrigin: {
				vertical: "bottom",
				horizontal: "center"
			},
			open: c.length > 0,
			children: U(YE, {
				id: "error-tooltip-list",
				"data-testid": "error-tooltip-list",
				children: c.map(function(e, t) {
					return W(XE, { children: [U(ZE, {
						"data-testid": `error-tooltip-${t}`,
						children: e
					}), U(QE, {
						testId: `error-tooltip-close-${t}`,
						iconName: "close",
						onClick: function() {
							return j(e);
						}
					})] }, e);
				})
			})
		})
	] });
}
//#endregion
export { wj as default };
