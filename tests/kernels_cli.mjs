// Runs site/kernels.js on a JSON list of cases from stdin, for the parity tests.
// Case: {op, x, y, w}. A number JSON cannot carry is sent as {"special": "NaN"} or "Infinity".
// Output: one {"value": ...} or {"error": "..."} per case. A malformed request exits 2.
import fs from "node:fs";
import path from "node:path";
import vm from "node:vm";
import { fileURLToPath } from "node:url";

const here = path.dirname(fileURLToPath(import.meta.url));
const file = path.join(here, "..", "site", "kernels.js");

function fail(message) {
  process.stderr.write(message + "\n");
  process.exit(2);
}

if (!fs.existsSync(file)) fail("kernels.js not found: " + file);
vm.runInThisContext(fs.readFileSync(file, "utf8"), { filename: file });
const K = globalThis.TSC_KERNELS;
if (!K) fail("kernels.js did not define TSC_KERNELS");

const SPECIAL = { NaN: NaN, Infinity: Infinity };
function revive(v) {
  if (Array.isArray(v)) return v.map(revive);
  if (v && typeof v === "object") {
    if (!(v.special in SPECIAL)) fail("unknown tag: " + JSON.stringify(v));
    return SPECIAL[v.special];
  }
  return v;
}

let cases;
try {
  cases = JSON.parse(fs.readFileSync(0, "utf8"));
} catch (e) {
  fail("not JSON: " + e.message);
}
if (!Array.isArray(cases)) fail("request must be a list of cases");

const ops = ["euclidean", "dtw", "dtwPath"];
const results = cases.map((c) => {
  if (!c || !ops.includes(c.op)) fail("unknown op: " + JSON.stringify(c && c.op));
  return c;
}).map((c) => {
  const x = revive(c.x), y = revive(c.y), w = c.w === undefined ? null : revive(c.w);
  try {
    const value = c.op === "euclidean" ? K.euclidean(x, y) : K[c.op](x, y, w);
    return { value };
  } catch (e) {
    return { error: e.message };
  }
});
process.stdout.write(JSON.stringify(results));
