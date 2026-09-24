// Agent 1 — internal test of the demonstration page.
// Run:  node tests/test_demo.js [path-to-html]
// Checks the page for the things the liability review requires, and that the logic is right.
// Exit code 0 = all pass, 1 = at least one failure. Prints one line per check.

const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

const FILE = path.resolve(process.argv[2] || 'referral-completeness-demo.html');
const results = [];
const check = (name, ok, detail = '') => { results.push({ name, ok, detail }); };

(async () => {
  const html = fs.readFileSync(FILE, 'utf8');

  // ---- Static checks on the file ----
  const forbidden = [/referright/i, /patent/i, /argyle/i, /medicare/i, /acceptance rate/i, /wait days/i,
                     /rejection risk/i, /risk of rejection/i, /send anyway/i, /\bCPC\b/, /we recommend/i, /you should/i];
  forbidden.forEach(re => check(`no forbidden term ${re}`, !re.test(html.replace(/\.requirement-badge\.recommended/g, '')),
    (html.match(re) || [''])[0]));
  check('no external scripts', !/<script[^>]+src=["']https?:/i.test(html));
  check('no external stylesheets/fonts', !/<link[^>]+href=["']https?:/i.test(html));
  check('no fetch/XHR in code', !/fetch\(|XMLHttpRequest/.test(html));
  check('no storage APIs', !/localStorage|sessionStorage|indexedDB|document\.cookie/.test(html));
  check('gate names negligence', /including liability for negligence/i.test(html));
  check('ACL carve-out present', /Australian Consumer Law/.test(html));
  check('not-a-medical-device statement present', /not a medical device/i.test(html));
  check('do-not-enter-real-patient statement present', /not enter real patient/i.test(html));
  check('author line present', /Dr Ferney Bernal Buitrago/.test(html));
  check('no-affiliation line present', /Not affiliated with, or endorsed by, any practice, health service or employer/.test(html));
  check('NSW attribution formula present', /© State of New South Wales NSW Ministry of Health/.test(html));
  check('CC BY 4.0 stated', /Creative Commons Attribution 4\.0/.test(html));
  check('source URL present', /health\.nsw\.gov\.au\/outpatients\/referrals\/Pages\/chest-pain-tightness-adult\.aspx/.test(html));
  check('current-as-at date present', /current as at \d{1,2} \w+ \d{4}/i.test(html));
  const fictional = (html.match(/FICTIONAL/g) || []).length;
  check('fictional tags on patient and letter', fictional >= 2, `${fictional} found`);
  const realNames = /Dr Ferney Bernal(?! Buitrago)|FRACGP/;
  check('author name not used inside the fictional letter', !realNames.test(html));

  // ---- Behavioural checks in a headless browser ----
  const browser = await chromium.launch();
  try {
  const page = await browser.newPage({ viewport: { width: 1200, height: 900 } });
  const pageErrors = [], requests = [];
  page.on('pageerror', e => pageErrors.push(e.message));
  page.on('request', r => { if (/^https?:/.test(r.url())) requests.push(r.url()); });
  await page.goto('file://' + FILE);
  await page.waitForTimeout(300);

  check('gate is visible on load', await page.locator('#gate').isVisible());
  check('demo content not reachable behind gate', !(await page.locator('#screen2').isVisible()));
  await page.getByText('I understand').click();
  check('gate closes on acknowledgement', !(await page.locator('#gate').isVisible()));
  check('screen 1 shown', await page.locator('#screen1').isVisible());

  await page.getByText('Show the fictional referral').click();
  check('screen 2 shown', await page.locator('#screen2').isVisible());
  const boxes = await page.locator('#checkList input[type=checkbox]').count();
  check('18 checklist items rendered (13 required + 5 if-available)', boxes === 18, `${boxes}`);

  // default state
  await page.getByText('Compare against the published list').click();
  let val = await page.locator('#progressValue').textContent();
  check('default count is 5 / 13', val.trim() === '5 / 13', val);
  const missing = await page.locator('#missingReq .finding-item').count();
  check('default missing-required count is 8', missing === 8, `${missing}`);

  // all ticked
  await page.getByText('Change the ticks').click();
  await page.locator('#checkList input[type=checkbox]').evaluateAll(els => els.forEach(e => e.checked = true));
  await page.getByText('Compare against the published list').click();
  val = await page.locator('#progressValue').textContent();
  check('all ticked gives 13 / 13', val.trim() === '13 / 13', val);
  check('all ticked: "None" shown for missing', /None/.test(await page.locator('#missingReq').textContent()));

  // none ticked
  await page.getByText('Change the ticks').click();
  await page.locator('#checkList input[type=checkbox]').evaluateAll(els => els.forEach(e => e.checked = false));
  await page.getByText('Compare against the published list').click();
  val = await page.locator('#progressValue').textContent();
  check('none ticked gives 0 / 13', val.trim() === '0 / 13', val);

  // output wording never recommends
  const resultText = await page.locator('#screen3').textContent();
  check('result text contains no recommendation language', !/recommend|should order|must order|critical|urgent/i.test(resultText));

  await page.getByText('See the full published list').click();
  check('screen 4 shown', await page.locator('#screen4').isVisible());
  const listReq = await page.locator('#listReq .requirement-item').count();
  check('published list shows 13 required items', listReq === 13, `${listReq}`);

  await page.locator('#infoBtn').click();
  check('info modal opens', await page.locator('#infoModal').isVisible());
  await page.locator('#infoModal').getByText('Close').click();
  check('info modal closes', !(await page.locator('#infoModal').isVisible()));

  check('no JavaScript errors', pageErrors.length === 0, pageErrors.join('; '));
  check('no network requests made', requests.length === 0, requests.join(', '));

  // mobile viewport sanity
  await page.setViewportSize({ width: 390, height: 800 });
  await page.waitForTimeout(200);
  const overflow = await page.evaluate(() => document.documentElement.scrollWidth > document.documentElement.clientWidth + 2);
  check('no horizontal overflow at phone width', !overflow);

  } catch (e) {
    check('behavioural run completed', false, 'aborted: ' + e.message.split('\n')[0]);
  }
  await browser.close();

  // ---- Report ----
  let fails = 0;
  for (const r of results) {
    if (!r.ok) fails++;
    console.log(`${r.ok ? 'PASS' : 'FAIL'}  ${r.name}${r.detail ? '  [' + r.detail + ']' : ''}`);
  }
  console.log(`\n${results.length - fails} passed, ${fails} failed  —  ${new Date().toISOString()}`);
  process.exit(fails ? 1 : 0);
})();
