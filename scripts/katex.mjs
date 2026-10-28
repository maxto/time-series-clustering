// Batch TeX renderer for scripts/build.py (one call per build).
// stdin:  JSON list [{"tex": "...", "display": true|false}, ...]
// stdout: JSON list of HTML strings, same order (KaTeX, HTML and MathML output).
// On any TeX error: exit 1, stderr holds a JSON list [{"index", "tex", "message"}] of every failing item.
import katex from 'katex';

let input = '';
for await (const chunk of process.stdin) input += chunk;
const items = JSON.parse(input);
const html = [], errors = [];
items.forEach(({ tex, display }, index) => {
  try {
    html.push(katex.renderToString(tex, { displayMode: !!display, throwOnError: true, output: 'htmlAndMathml', strict: 'error' }));
  } catch (e) {
    errors.push({ index, tex, message: e.message });
  }
});
if (errors.length) {
  process.stderr.write(JSON.stringify(errors));
  process.exit(1);
}
process.stdout.write(JSON.stringify(html));
