// Gera a imagem de compartilhamento e o ícone da Apple a partir do preview local (porta 5310).
// Rodar de dentro de achilles-video/ (onde está o playwright-core): node ../mellcorr/tools/og.mjs
import { chromium } from 'playwright-core';
const b = await chromium.launch({ executablePath: 'C:/Program Files/Google/Chrome/Application/chrome.exe', headless: true });
const p = await b.newPage({ viewport: { width: 1200, height: 630 }, deviceScaleFactor: 1 });
await p.goto('http://localhost:5310/index.html', { waitUntil: 'networkidle' });
await p.addStyleTag({ content: '.hero{min-height:630px;padding:40px 0}.hero-trust,.wa-float,.site-header{display:none!important}.hero-visual{max-width:400px}' });
await p.waitForTimeout(4000);
await p.screenshot({ path: '../mellcorr/dist/assets/og-melina.jpg', type: 'jpeg', quality: 84 });
const q = await b.newPage({ viewport: { width: 180, height: 180 } });
await q.goto('http://localhost:5310/robots.txt');
await q.evaluate(() => { document.documentElement.innerHTML = '<body style="margin:0"><img src="/assets/favicon.svg" style="width:180px;height:180px;display:block"></body>'; });
await q.waitForTimeout(500);
await q.screenshot({ path: '../mellcorr/dist/assets/apple-touch-icon.png' });
await b.close(); console.log('ok');
