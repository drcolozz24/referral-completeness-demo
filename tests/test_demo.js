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
  const forbidden = [/patent pending/i, /medicare/i, /acceptance rate/i, /wait days/i,
                     /rejection risk/i, /risk of rejection/i, /send anyway/i, /\bCPC\b/, /we recommend/i, /you should/i];
  forbidden.forEach(re => check(`no forbidden term ${re}`, !re.test(html.replace(/\.requirement-badge\.recommended/g, '')),
    (html.match(re) || [''])[0]));
  check('no external scripts', !/<script[^>]+src=["']https?:/i.test(html));
  check('no external stylesheets/fonts', !/<link[^>]+href=["']https?:/i.test(html));
  check('page points software and agents to the data file and guide', /href="data\/nsw-chest-pain-adult\.json"/.test(html) && /href="llms\.txt"/.test(html));
  const root = path.dirname(FILE);
  check('data file and agent guide exist beside the page', fs.existsSync(path.join(root, 'data', 'nsw-chest-pain-adult.json')) && fs.existsSync(path.join(root, 'llms.txt')));
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
  const letter = (html.match(/<textarea[^>]*>([\s\S]*?)<\/textarea>/) || ['', ''])[1];
  check('fictional letter found in the file', letter.length > 100, `${letter.length} characters`);
  check('author name not used inside the fictional letter', !/Ferney|Bernal|Buitrago/i.test(letter));
  check('credit states creator and AI assistance', /Created by Dr Ferney Bernal Buitrago, with AI assistance/.test(html));
  check('licence link present', /creativecommons\.org\/licenses\/by\/4\.0\//.test(html));
  check('changes to the NSW text are stated', /Changes made:/.test(html) && /No wording has been changed/.test(html));
  const dates = html.match(/current as at \d{1,2} \w+ \d{4}/gi) || [];
  check('current-as-at date appears at least 3 times in the file, all the same', dates.length >= 3 && new Set(dates.map(d => d.toLowerCase())).size === 1, `${dates.length} found`);
  check('letter is readable (readonly, not disabled)', !/<textarea[^>]*disabled/.test(html));

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
  const defaults = await page.locator('#checkList input[type=checkbox]:checked').evaluateAll(els => els.map(e => e.id).sort().join(','));
  check('default ticks are exactly reason, provisional diagnosis, FBC, EUC, ECG', defaults === 'cb_ecg,cb_euc,cb_fbc,cb_provdx,cb_reason', defaults);
  const subs = await page.locator('#checkList label').evaluateAll(els => els.filter(e => e.style.marginLeft).length);
  check('nine required items shown as sub-items', subs === 9, `${subs}`);
  await page.locator('#screen2').getByText('Back', { exact: true }).click();
  check('Back on the letter screen returns to screen 1', await page.locator('#screen1').isVisible());
  await page.getByText('Show the fictional referral').click();

  // default state
  await page.getByText('Compare against the published list').click();
  let val = await page.locator('#progressValue').textContent();
  check('default count is 5 / 13', val.trim() === '5 / 13', val);
  const missing = await page.locator('#missingReq .finding-item').count();
  check('default missing-required count is 8', missing === 8, `${missing}`);
  let verdict = (await page.locator('#verdict').textContent()).trim();
  check('default result statement', verdict === 'This letter does not mention 8 of the 13 items NSW lists as required.', verdict);
  const consequence = await page.locator('#nswConsequence').textContent();
  check('NSW statement on missing information is quoted with its source',
    /patients may experience delayed access to care/.test(consequence) && /returning the referral to referring health professionals/.test(consequence) && /faqs\.aspx/.test(html) && /page dated \d{1,2} \w+ \d{4}/.test(consequence));
  check('result says NSW does not state which outcome applies', /NSW does not say which of these a service will do with a given referral/.test(consequence));

  // all ticked
  await page.getByText('Change the ticks').click();
  await page.locator('#checkList input[type=checkbox]').evaluateAll(els => els.forEach(e => e.checked = true));
  await page.getByText('Compare against the published list').click();
  val = await page.locator('#progressValue').textContent();
  check('all ticked gives 13 / 13', val.trim() === '13 / 13', val);
  verdict = (await page.locator('#verdict').textContent()).trim();
  check('all-ticked result statement', verdict === 'This letter mentions all 13 items NSW lists as required.', verdict);
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
  check('result does not predict a decision on the referral', !/(will|would|likely to) be (accepted|rejected|declined|returned)|\b(accepted|rejected|declined)\b/i.test(resultText), '');

  await page.getByText('See the full published list').click();
  check('screen 4 shown', await page.locator('#screen4').isVisible());
  const listReq = await page.locator('#listReq .requirement-item').count();
  check('published list shows 13 required items', listReq === 13, `${listReq}`);

  // What the page displays, against the newest snapshot of the NSW page in tests/fetched/.
  const dir = path.join(__dirname, 'fetched');
  const snapName = fs.existsSync(dir) ? fs.readdirSync(dir).filter(f => /^nsw-chest-pain-adult-.*\.json$/.test(f)).sort().pop() : null;
  check('a snapshot of the NSW page is available to compare with', !!snapName, snapName || 'none in tests/fetched');
  if (snapName) {
    const snap = JSON.parse(fs.readFileSync(path.join(dir, snapName), 'utf8'));
    const flat = list => list.flatMap(e => typeof e === 'string' ? [e] : [e.text, ...(e.children || [])]);
    const tri = snap.triage.map(t => typeof t === 'string' ? t : `${t.category} \u2014 ${t.timeframe} \u2014 ${t.criteria}`);
    const same = (a, b) => a.length === b.length && a.every((x, i) => x === b[i]);
    const texts = sel => page.locator(sel).evaluateAll(els => els.map(e => e.textContent));
    const shownReq = await texts('#listReq .requirement-item');
    const shownOpt = await texts('#listOpt .requirement-item');
    const shownTri = (await texts('#screen4 .requirement-item')).filter(t => /^\s*Category\b/.test(t)).map(t => t.trim());
    check(`displayed required list equals snapshot ${snapName}`, same(shownReq, flat(snap.required)));
    check('displayed if-available list equals the snapshot', same(shownOpt, flat(snap.if_available)));
    check('displayed triage lines equal the snapshot', same(shownTri, tri), `${shownTri.length} shown`);
    const ticks = await texts('#checkList label');
    const wanted = [...flat(snap.required), ...flat(snap.if_available)];
    check('every tick-box carries the snapshot wording, in order', ticks.length === wanted.length && wanted.every((w, i) => ticks[i].includes(w)));
  }

  await page.locator('#infoBtn').click();
  check('info modal opens', await page.locator('#infoModal').isVisible());
  await page.locator('#infoModal').getByText('Close').click();
  check('info modal closes', !(await page.locator('#infoModal').isVisible()));
  await page.locator('#infoBtn').click();
  await page.keyboard.press('Escape');
  check('Escape closes the info modal', !(await page.locator('#infoModal').isVisible()));
  const triage = await page.locator('#screen4 .requirement-item', { hasText: /^Category \d/ }).count();
  check('three triage category lines shown', triage === 3, `${triage}`);
  await page.getByText('Back to the comparison').click();
  check('Back to the comparison returns to screen 3', await page.locator('#screen3').isVisible());
  await page.getByText('Start again').click();
  check('Start again returns to screen 1', await page.locator('#screen1').isVisible());

  check('no JavaScript errors', pageErrors.length === 0, pageErrors.join('; '));
  check('no network requests made', requests.length === 0, requests.join(', '));

  // mobile viewport sanity
  await page.setViewportSize({ width: 390, height: 800 });
  for (const n of [1, 2, 3, 4]) {
    await page.evaluate(k => goToScreen(k), n);
    await page.waitForTimeout(150);
    const overflow = await page.evaluate(() => document.documentElement.scrollWidth > document.documentElement.clientWidth + 2);
    check(`no horizontal overflow at phone width on screen ${n}`, !overflow);
  }

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
