import { c as e, d as t, m as n, o as r, s as i } from "./src-Cu_B2g6X.js";
//#region ../../../resource_engines/node_modules/d3-interpolate/src/numberArray.js
function a(e, t) {
	t ||= [];
	var n = e ? Math.min(t.length, e.length) : 0, r = t.slice(), i;
	return function(a) {
		for (i = 0; i < n; ++i) r[i] = e[i] * (1 - a) + t[i] * a;
		return r;
	};
}
function o(e) {
	return ArrayBuffer.isView(e) && !(e instanceof DataView);
}
//#endregion
//#region ../../../resource_engines/node_modules/d3-interpolate/src/array.js
function s(e, t) {
	for (var n = t ? t.length : 0, r = e ? Math.min(n, e.length) : 0, i = Array(r), a = Array(n), o = 0; o < r; ++o) i[o] = u(e[o], t[o]);
	for (; o < n; ++o) a[o] = t[o];
	return function(e) {
		for (o = 0; o < r; ++o) a[o] = i[o](e);
		return a;
	};
}
//#endregion
//#region ../../../resource_engines/node_modules/d3-interpolate/src/date.js
function c(e, t) {
	var n = /* @__PURE__ */ new Date();
	return e = +e, t = +t, function(r) {
		return n.setTime(e * (1 - r) + t * r), n;
	};
}
//#endregion
//#region ../../../resource_engines/node_modules/d3-interpolate/src/object.js
function l(e, t) {
	var n = {}, r = {}, i;
	for (i in (typeof e != "object" || !e) && (e = {}), (typeof t != "object" || !t) && (t = {}), t) i in e ? n[i] = u(e[i], t[i]) : r[i] = t[i];
	return function(e) {
		for (i in n) r[i] = n[i](e);
		return r;
	};
}
//#endregion
//#region ../../../resource_engines/node_modules/d3-interpolate/src/value.js
function u(u, d) {
	var f = typeof d, p;
	return d == null || f === "boolean" ? t(d) : (f === "number" ? i : f === "string" ? (p = n(d)) ? (d = p, e) : r : d instanceof n ? e : d instanceof Date ? c : o(d) ? a : Array.isArray(d) ? s : typeof d.valueOf != "function" && typeof d.toString != "function" || isNaN(d) ? l : i)(u, d);
}
//#endregion
export { u as t };
