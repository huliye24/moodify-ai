import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const assets = path.join(path.dirname(fileURLToPath(import.meta.url)), 'assets');
const mark = `data:image/png;base64,${fs.readFileSync(path.join(assets, 'moodify-symbol.png')).toString('base64')}`;
const svg = `<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="1600" height="480" viewBox="0 0 1600 480" role="img" aria-label="Moodify — Every voice deserves to be heard">
<defs>
  <linearGradient id="ground" x1="0" y1="0" x2="1" y2="1"><stop stop-color="#FFFFFF"/><stop offset="1" stop-color="#F2F7FF"/></linearGradient>
  <linearGradient id="accent" x1="0" y1="0" x2="1" y2="0"><stop stop-color="#8A00FF"/><stop offset=".52" stop-color="#5145FF"/><stop offset="1" stop-color="#00D8E8"/></linearGradient>
</defs>
<rect width="1600" height="480" fill="url(#ground)"/>
<path d="M0 438H1600" stroke="#E8EDF8" stroke-width="2"/>
<image x="86" y="100" width="380" height="255" href="${mark}" xlink:href="${mark}"/>
<text x="514" y="254" fill="#111733" font-family="Arial, Helvetica, sans-serif" font-size="136" font-weight="700" letter-spacing="-5">Moodify</text>
<rect x="520" y="278" width="250" height="5" rx="2.5" fill="url(#accent)"/>
<text x="520" y="337" fill="#59647C" font-family="Arial, Helvetica, sans-serif" font-size="30" letter-spacing="1.1">Every voice deserves to be heard.</text>
<text x="520" y="396" fill="#7E8BA4" font-family="Arial, Helvetica, sans-serif" font-size="18" letter-spacing="3.2">LISTEN. THEN PLAY.</text>
</svg>\n`;
fs.writeFileSync(path.join(assets, 'moodify-horizontal.svg'), svg, 'utf8');
