import { n as e } from "./chunk-Y2CYZVJY-deSKRZbW.js";
import { t } from "./chunk-X3CZISLH-DvDPwIag.js";
import "./chunk-DU6HZSFF-arEeM9si.js";
import "./dist-BugDrZcE.js";
import { n, r, t as i } from "./chunk-SVP7TREG-BO_ZlCKk.js";
import { t as a } from "./chunk-JWPE2WC7-D4Ntrv_2.js";
import { t as o, w as s } from "./mermaid-parser.core-vxq-OQVs.js";
//#region ../../../resource_engines/node_modules/mermaid/dist/chunks/mermaid.core/pegDiagram-XKGWAZYB.mjs
var c = s().RailroadPeg.parser.LangiumParser, l = /* @__PURE__ */ e((e) => {
	let t = e.alternatives.map(u);
	return t.length === 1 ? t[0] : {
		type: "choice",
		alternatives: t
	};
}, "transformOrderedChoice"), u = /* @__PURE__ */ e((e) => {
	let t = e.elements.map(d);
	return t.length === 1 ? t[0] : {
		type: "sequence",
		elements: t
	};
}, "transformSequence"), d = /* @__PURE__ */ e((e) => {
	let t = p(e.suffix);
	return e.operator ? {
		type: "special",
		text: e.operator === "&" ? `&${f(t)}` : `!${f(t)}`
	} : t;
}, "transformPrefix"), f = /* @__PURE__ */ e((e) => {
	switch (e.type) {
		case "terminal": return `"${e.value}"`;
		case "nonterminal": return e.name;
		case "special": return e.text;
		default: return "(...)";
	}
}, "nodeToLabel"), p = /* @__PURE__ */ e((e) => {
	let t = m(e.primary);
	if (!e.operator) return t;
	switch (e.operator) {
		case "?": return {
			type: "optional",
			element: t
		};
		case "*": return {
			type: "repetition",
			element: t,
			min: 0,
			max: Infinity
		};
		case "+": return {
			type: "repetition",
			element: t,
			min: 1,
			max: Infinity
		};
		default: throw Error(`Unsupported PEG suffix operator: ${e.operator}`);
	}
}, "transformSuffix"), m = /* @__PURE__ */ e((e) => {
	switch (e.$type) {
		case "PegLiteral": return {
			type: "terminal",
			value: e.value
		};
		case "PegIdentifier": return {
			type: "nonterminal",
			name: e.name
		};
		case "PegGroup": return l(e.element);
		case "PegAny": return {
			type: "special",
			text: e.dot
		};
		default: throw Error(`Unsupported PEG primary node: ${e.$type}`);
	}
}, "transformPrimary"), h = /* @__PURE__ */ e((e) => ({
	name: e.name,
	definition: l(e.definition)
}), "transformRule"), g = /* @__PURE__ */ e((e) => {
	a(e, i), e.title && i.setTitle(e.title), e.rules.map((e) => i.addRule(h(e)));
}, "populateDb"), _ = {
	parser: {
		parse: /* @__PURE__ */ e((e) => {
			i.clear(), t.debug("[PEG Parser] Starting Langium parse");
			let n = c.parse(e);
			if (n.lexerErrors.length > 0 || n.parserErrors.length > 0) throw new o(n);
			let r = n.value;
			t.debug("[PEG Parser] Parsed rules:", r.rules.length), g(r), t.debug("[PEG Parser] Parse complete");
		}, "parse"),
		parser: { yy: i }
	},
	db: i,
	renderer: r,
	styles: n
};
//#endregion
export { _ as diagram };
