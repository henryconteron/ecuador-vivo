import js from "@eslint/js";
import globals from "globals";

export default [
  {
    ignores: [
      "assets/vendor/**",
      "node_modules/**",
      "production/**",
      "tools/biblioteca/original/**",
    ],
  },
  js.configs.recommended,
  {
    files: ["assets/js/**/*.js", "scripts/**/*.{js,mjs}", "tests/**/*.mjs"],
    languageOptions: {
      ecmaVersion: "latest",
      sourceType: "module",
      globals: {
        ...globals.browser,
        ...globals.node,
        L: "readonly",
      },
    },
    linterOptions: {
      reportUnusedDisableDirectives: "warn",
    },
    rules: {
      "eqeqeq": ["error", "always", { null: "ignore" }],
      "no-constant-binary-expression": "error",
      "no-dupe-else-if": "error",
      "no-unused-vars": [
        "error",
        {
          argsIgnorePattern: "^_",
          caughtErrors: "none",
          varsIgnorePattern: "^_",
        },
      ],
    },
  },
  {
    files: ["assets/js/portal-catalog.js"],
    rules: {
      "no-control-regex": "off",
    },
  },
  {
    files: ["scripts/*_gee*.js"],
    languageOptions: {
      globals: {
        ee: "readonly",
        Export: "readonly",
        Map: "readonly",
        print: "readonly",
      },
    },
  },
];
