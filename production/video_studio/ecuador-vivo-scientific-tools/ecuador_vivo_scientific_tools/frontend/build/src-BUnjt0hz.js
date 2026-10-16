import "./src-Cu_B2g6X.js";
//#region ../../../resource_engines/node_modules/d3-brush/src/brush.js
var { abs: e, max: t, min: n } = Math;
["w", "e"].map(r), ["n", "s"].map(r), [
	"n",
	"w",
	"e",
	"s",
	"nw",
	"ne",
	"sw",
	"se"
].map(r);
function r(e) {
	return { type: e };
}
//#endregion
//#region ../../../resource_engines/node_modules/d3-path/src/path.js
var i = Math.PI, a = 2 * i, o = 1e-6, s = a - o;
function c(e) {
	this._ += e[0];
	for (let t = 1, n = e.length; t < n; ++t) this._ += arguments[t] + e[t];
}
function l(e) {
	let t = Math.floor(e);
	if (!(t >= 0)) throw Error(`invalid digits: ${e}`);
	if (t > 15) return c;
	let n = 10 ** t;
	return function(e) {
		this._ += e[0];
		for (let t = 1, r = e.length; t < r; ++t) this._ += Math.round(arguments[t] * n) / n + e[t];
	};
}
var u = class {
	constructor(e) {
		this._x0 = this._y0 = this._x1 = this._y1 = null, this._ = "", this._append = e == null ? c : l(e);
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
	arcTo(e, t, n, r, a) {
		if (e = +e, t = +t, n = +n, r = +r, a = +a, a < 0) throw Error(`negative radius: ${a}`);
		let s = this._x1, c = this._y1, l = n - e, u = r - t, d = s - e, f = c - t, p = d * d + f * f;
		if (this._x1 === null) this._append`M${this._x1 = e},${this._y1 = t}`;
		else if (p > o) {
			if (!(Math.abs(f * l - u * d) > o) || !a) this._append`L${this._x1 = e},${this._y1 = t}`;
			else {
				let m = n - s, h = r - c, g = l * l + u * u, _ = m * m + h * h, v = Math.sqrt(g), y = Math.sqrt(p), b = a * Math.tan((i - Math.acos((g + p - _) / (2 * v * y))) / 2), x = b / y, S = b / v;
				Math.abs(x - 1) > o && this._append`L${e + x * d},${t + x * f}`, this._append`A${a},${a},0,0,${+(f * m > d * h)},${this._x1 = e + S * l},${this._y1 = t + S * u}`;
			}
		}
	}
	arc(e, t, n, r, c, l) {
		if (e = +e, t = +t, n = +n, l = !!l, n < 0) throw Error(`negative radius: ${n}`);
		let u = n * Math.cos(r), d = n * Math.sin(r), f = e + u, p = t + d, m = 1 ^ l, h = l ? r - c : c - r;
		this._x1 === null ? this._append`M${f},${p}` : (Math.abs(this._x1 - f) > o || Math.abs(this._y1 - p) > o) && this._append`L${f},${p}`, n && (h < 0 && (h = h % a + a), h > s ? this._append`A${n},${n},0,1,${m},${e - u},${t - d}A${n},${n},0,1,${m},${this._x1 = f},${this._y1 = p}` : h > o && this._append`A${n},${n},0,${+(h >= i)},${m},${this._x1 = e + n * Math.cos(c)},${this._y1 = t + n * Math.sin(c)}`);
	}
	rect(e, t, n, r) {
		this._append`M${this._x0 = this._x1 = +e},${this._y0 = this._y1 = +t}h${n = +n}v${+r}h${-n}Z`;
	}
	toString() {
		return this._;
	}
};
u.prototype;
//#endregion
//#region ../../../resource_engines/node_modules/d3-shape/src/constant.js
function d(e) {
	return function() {
		return e;
	};
}
//#endregion
//#region ../../../resource_engines/node_modules/d3-shape/src/math.js
var f = Math.abs, p = Math.atan2, m = Math.cos, h = Math.max, g = Math.min, _ = Math.sin, v = Math.sqrt, y = 1e-12, b = Math.PI, x = b / 2, S = 2 * b;
function C(e) {
	return e > 1 ? 0 : e < -1 ? b : Math.acos(e);
}
function w(e) {
	return e >= 1 ? x : e <= -1 ? -x : Math.asin(e);
}
//#endregion
//#region ../../../resource_engines/node_modules/d3-shape/src/path.js
function T(e) {
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
	}, () => new u(t);
}
Array.prototype.slice;
function E(e) {
	return typeof e == "object" && "length" in e ? e : Array.from(e);
}
//#endregion
//#region ../../../resource_engines/node_modules/d3-shape/src/curve/linear.js
function D(e) {
	this._context = e;
}
D.prototype = {
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
function O(e) {
	return new D(e);
}
//#endregion
//#region ../../../resource_engines/node_modules/d3-shape/src/point.js
function k(e) {
	return e[0];
}
function A(e) {
	return e[1];
}
//#endregion
//#region ../../../resource_engines/node_modules/d3-shape/src/line.js
function j(e, t) {
	var n = d(!0), r = null, i = O, a = null, o = T(s);
	e = typeof e == "function" ? e : e === void 0 ? k : d(e), t = typeof t == "function" ? t : t === void 0 ? A : d(t);
	function s(s) {
		var c, l = (s = E(s)).length, u, d = !1, f;
		for (r ?? (a = i(f = o())), c = 0; c <= l; ++c) !(c < l && n(u = s[c], c, s)) === d && ((d = !d) ? a.lineStart() : a.lineEnd()), d && a.point(+e(u, c, s), +t(u, c, s));
		if (f) return a = null, f + "" || null;
	}
	return s.x = function(t) {
		return arguments.length ? (e = typeof t == "function" ? t : d(+t), s) : e;
	}, s.y = function(e) {
		return arguments.length ? (t = typeof e == "function" ? e : d(+e), s) : t;
	}, s.defined = function(e) {
		return arguments.length ? (n = typeof e == "function" ? e : d(!!e), s) : n;
	}, s.curve = function(e) {
		return arguments.length ? (i = e, r != null && (a = i(r)), s) : i;
	}, s.context = function(e) {
		return arguments.length ? (e == null ? r = a = null : a = i(r = e), s) : r;
	}, s;
}
//#endregion
export { S as _, f as a, p as c, x as d, h as f, v as g, _ as h, T as i, m as l, b as m, O as n, C as o, g as p, E as r, w as s, j as t, y as u, d as v };
