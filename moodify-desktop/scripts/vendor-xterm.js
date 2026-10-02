/**
 * Copy xterm.js dist assets into renderer/vendor so the file:// page can
 * load them as same-origin scripts (contextIsolation blocks require()).
 * Runs on postinstall.
 */

const fs = require('fs');
const path = require('path');

const pairs = [
  ['@xterm/xterm/lib/xterm.js', 'xterm.js'],
  ['@xterm/xterm/css/xterm.css', 'xterm.css'],
  ['@xterm/addon-fit/lib/addon-fit.js', 'addon-fit.js'],
];

const vendor = path.join(__dirname, '..', 'renderer', 'vendor');
fs.mkdirSync(vendor, { recursive: true });
for (const [from, to] of pairs) {
  fs.copyFileSync(
    path.join(__dirname, '..', 'node_modules', ...from.split('/')),
    path.join(vendor, to),
  );
  console.log('vendored', to);
}
