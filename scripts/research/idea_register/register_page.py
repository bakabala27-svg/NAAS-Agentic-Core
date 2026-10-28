"""Render the register JSON into one self-contained HTML page (data embedded; filters in plain JS)."""

import json
import sys
from pathlib import Path

reg = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
out = Path(sys.argv[2])
data = json.dumps(reg, ensure_ascii=False).replace("</", "<\\/")

HTML = r"""<title>سجلّ الأفكار الموحّد</title>
<meta name="claude:viewport-fit-sides" content="cover">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans+Arabic:wght@400;500;600&family=Noto+Kufi+Arabic:wght@600;700&family=IBM+Plex+Mono:wght@400;500&display=swap">
<style>
/* Layout: a library catalogue — summary strip, groups, then one filterable drawer of index cards (records). */
:root {
  --paper: #f3f5f6; --card: #ffffff; --ink: #172028; --muted: #5a6670; --rule: #d5dbe0;
  --accent: #1f5f8b; --accent-soft: #e1ecf4;
  --ok: #1d6a51; --ok-soft: #e0eee7; --mid: #8a5a00; --mid-soft: #f4e9d2; --no: #9c3527; --no-soft: #f4e0dc;
  --font-display: "Noto Kufi Arabic", "IBM Plex Sans Arabic", Tahoma, sans-serif;
  --font-body: "IBM Plex Sans Arabic", "Segoe UI", Tahoma, sans-serif;
  --font-data: "IBM Plex Mono", ui-monospace, Menlo, monospace;
}
@media (prefers-color-scheme: dark) { :root:not([data-theme="light"]) {
  --paper: #0f151a; --card: #161e25; --ink: #e3e8ec; --muted: #9aa6b0; --rule: #2a343d;
  --accent: #7fb5dc; --accent-soft: #19283a; --ok: #63c39b; --ok-soft: #17302a; --mid: #e2b15a; --mid-soft: #362a14;
  --no: #e78d7f; --no-soft: #3a2320; color-scheme: dark; } }
:root[data-theme="dark"] {
  --paper: #0f151a; --card: #161e25; --ink: #e3e8ec; --muted: #9aa6b0; --rule: #2a343d;
  --accent: #7fb5dc; --accent-soft: #19283a; --ok: #63c39b; --ok-soft: #17302a; --mid: #e2b15a; --mid-soft: #362a14;
  --no: #e78d7f; --no-soft: #3a2320; color-scheme: dark; }
body { background: var(--paper); color: var(--ink); font-family: var(--font-body); font-size: 15px; line-height: 1.7; }
.page { direction: rtl; max-width: 68rem; margin: 0 auto; padding-block: 2rem 4rem;
  padding-left: max(16px, env(safe-area-inset-left, 0px)); padding-right: max(16px, env(safe-area-inset-right, 0px));
  display: grid; gap: 2.25rem; }
h1, h2, h3 { font-family: var(--font-display); margin: 0; line-height: 1.35; text-wrap: balance; }
h1 { font-size: clamp(1.7rem, 4vw, 2.3rem); }
h2 { font-size: 1.25rem; padding-bottom: .35rem; border-bottom: 2px solid var(--ink); }
p { margin: 0; }
section { display: grid; gap: 1rem; }
.lede { max-width: 46rem; color: var(--ink); font-size: 1.05rem; }
.meta { color: var(--muted); font-size: .88rem; max-width: 46rem; }
.num { font-family: var(--font-data); font-variant-numeric: tabular-nums; direction: ltr; unicode-bidi: isolate; }
a { color: var(--accent); text-underline-offset: 3px; }
:focus-visible { outline: 2px solid var(--accent); outline-offset: 2px; }

.flow { display: grid; grid-template-columns: repeat(auto-fit, minmax(8.5rem, 1fr)); gap: .6rem; }
.flow div { background: var(--card); border: 1px solid var(--rule); border-radius: 6px; padding: .7rem .85rem; display: grid; gap: .1rem; }
.flow b { font-family: var(--font-data); font-weight: 500; font-size: 1.55rem; line-height: 1.2; }
.flow span { color: var(--muted); font-size: .8rem; }
.flow .in { border-color: var(--ok); background: var(--ok-soft); }

.groups { display: grid; grid-template-columns: repeat(auto-fit, minmax(17rem, 1fr)); gap: .75rem; }
.group { background: var(--card); border: 1px solid var(--rule); border-radius: 6px; padding: .9rem 1rem; display: grid; gap: .45rem; align-content: start; min-width: 0; }
.group h3 { font-size: 1rem; }
.group .k { font-family: var(--font-data); color: var(--muted); font-size: .8rem; }
.group dl { margin: 0; display: grid; gap: .25rem; font-size: .88rem; }
.group dt { color: var(--muted); font-size: .76rem; }
.group dd { margin: 0; }

.filters { display: flex; flex-wrap: wrap; gap: .6rem; align-items: end; background: var(--card); border: 1px solid var(--rule); border-radius: 6px; padding: .8rem; }
.filters label { display: grid; gap: .2rem; font-size: .78rem; color: var(--muted); min-width: 9rem; flex: 1 1 9rem; }
.filters select, .filters input { font: inherit; font-size: .9rem; color: var(--ink); background: var(--paper); border: 1px solid var(--rule); border-radius: 4px; padding: .35rem .5rem; }
.filters button { font: inherit; font-size: .85rem; color: var(--accent); background: transparent; border: 1px solid var(--accent); border-radius: 4px; padding: .35rem .8rem; cursor: pointer; }
.count { color: var(--muted); font-size: .88rem; }

.cards { display: grid; gap: .45rem; }
details.rec { background: var(--card); border: 1px solid var(--rule); border-radius: 6px; }
details.rec > summary { list-style: none; cursor: pointer; padding: .6rem .85rem; display: grid; grid-template-columns: 4.6rem minmax(0, 1fr) auto; gap: .6rem; align-items: center; }
details.rec > summary::-webkit-details-marker { display: none; }
.rid { font-family: var(--font-data); font-weight: 500; }
.rtitle { min-width: 0; }
.pills { display: flex; flex-wrap: wrap; gap: .3rem; justify-content: end; }
.pill { font-size: .72rem; font-weight: 600; padding: .05rem .5rem; border-radius: 999px; white-space: nowrap; background: var(--accent-soft); color: var(--accent); }
.pill.included { background: var(--ok-soft); color: var(--ok); }
.pill.conditional { background: var(--mid-soft); color: var(--mid); }
.pill.excluded { background: var(--no-soft); color: var(--no); }
.pill.ev { font-family: var(--font-data); background: transparent; border: 1px solid var(--rule); color: var(--muted); }
.body { border-top: 1px dashed var(--rule); padding: .75rem .85rem .9rem; display: grid; grid-template-columns: repeat(auto-fit, minmax(15rem, 1fr)); gap: .7rem 1.2rem; font-size: .9rem; }
.body div { min-width: 0; display: grid; gap: .15rem; }
.body h4 { margin: 0; font-size: .74rem; letter-spacing: .03em; color: var(--muted); font-weight: 600; }
.body .gates { display: flex; gap: .3rem; flex-wrap: wrap; }
.body .hist { display: grid; gap: .2rem; }
.body .hist p { margin: 0; }
.gate { font-family: var(--font-data); font-size: .78rem; border: 1px solid var(--rule); border-radius: 4px; padding: 0 .35rem; }
.gate.pass { color: var(--ok); border-color: var(--ok); } .gate.partial { color: var(--mid); border-color: var(--mid); } .gate.fail { color: var(--no); border-color: var(--no); }
.empty { color: var(--muted); padding: 1rem; text-align: center; }

.tbl { overflow-x: auto; border: 1px solid var(--rule); border-radius: 6px; background: var(--card); }
table { border-collapse: collapse; width: 100%; font-size: .86rem; }
th, td { text-align: start; padding: .5rem .65rem; border-bottom: 1px solid var(--rule); vertical-align: top; }
th { background: var(--paper); font-weight: 600; white-space: nowrap; }
tbody tr:last-child td { border-bottom: 0; }
@media (max-width: 34rem) { details.rec > summary { grid-template-columns: 4rem minmax(0, 1fr); } .pills { grid-column: 1 / -1; justify-content: start; } }
@media (prefers-reduced-motion: reduce) { * { scroll-behavior: auto !important; } }
</style>

<div class="page" lang="ar">
  <header style="display:grid;gap:.7rem">
    <h1>سجلّ الأفكار الموحّد</h1>
    <p class="lede">كلّ فكرةٍ ووظيفةٍ ومسارٍ تناولته أبحاثنا، في مكانٍ واحد. لا شيء محذوف: المستبعد يبقى بسبب استبعاده والشرط الذي يعيد فتحه.</p>
    <p class="meta">آخر مراجعة <span class="num" id="reviewed"></span>. الأصل في المستودع: <span class="num">docs/archive/commercial/IDEA_REGISTER.json</span>، واختبارٌ آلي يرفض أيّ تغييرٍ يُسقط سجلّاً أو يترك مستبعداً بلا سبب. الترتيب ليس دليل شراء، ولا يرخّص بناءً.</p>
  </header>

  <section aria-labelledby="h-flow">
    <h2 id="h-flow">مسار الغربلة</h2>
    <div class="flow" id="flow"></div>
  </section>

  <section aria-labelledby="h-groups">
    <h2 id="h-groups">ما يُختبر الآن وما ينتظر شرطه</h2>
    <div class="groups" id="groups"></div>
  </section>

  <section aria-labelledby="h-all">
    <h2 id="h-all">السجلّ الكامل</h2>
    <form class="filters" id="filters" onsubmit="return false">
      <label for="f-q">بحث<input id="f-q" type="search" placeholder="معرّف أو كلمة"></label>
      <label for="f-kind">النوع<select id="f-kind"></select></label>
      <label for="f-stage">المرحلة<select id="f-stage"></select></label>
      <label for="f-option">حالة الخيار<select id="f-option"></select></label>
      <label for="f-domain">المجال<select id="f-domain"></select></label>
      <label for="f-currency">العملة<select id="f-currency"></select></label>
      <button type="button" id="f-reset">إظهار الكلّ</button>
    </form>
    <p class="count" id="count" aria-live="polite"></p>
    <div class="cards" id="cards"></div>
  </section>

  <section aria-labelledby="h-method">
    <h2 id="h-method">على أيّ أساسٍ رُتّب</h2>
    <p class="meta">ستّة أطرٍ منشورة، ولكلٍّ حقلٌ في السجلّ. الأوجه الخمسة (المجال، السوق، العملة، طريقة التسليم، العائق الحاسم) تسمح بقراءة القائمة من أيّ زاوية دون نسخها.</p>
    <div class="tbl"><table>
      <thead><tr><th>الإطار</th><th>المصدر</th><th>ما يفرضه هنا</th></tr></thead>
      <tbody>
        <tr><td>PRISMA 2020</td><td>Page وآخرون، BMJ 2021;372:n71</td><td>مسارٌ مرئي من المُحدَّد إلى المُدرَج، ولكلّ مستبعَدٍ سببٌ مكتوب</td></tr>
        <tr><td>مبادئ FAIR</td><td>Wilkinson وآخرون، Scientific Data 3:160018، 2016</td><td>معرّفٌ دائم لا يُعاد استعماله، وبياناتٌ مقروءة آلياً، ومصدرٌ لكلّ سجلّ</td></tr>
        <tr><td>المقاربة العلمية لريادة الأعمال</td><td>Camuffo وآخرون، Management Science 2020؛ وإعادة الإنتاج على 759 شركة، Strategic Management Journal 45(6)، 2024</td><td>كلّ فكرة فرضية لها اختبارٌ وشرط إيقاف مكتوبان مسبقاً</td></tr>
        <tr><td>ريادة الأعمال البايزية</td><td>Agrawal وآخرون (محرّرون)، MIT Press، 2026</td><td>الاعتقاد يُحدَّث بالدليل، ويُحفظ أثر كلّ تحديث</td></tr>
        <tr><td>الخيارات الحقيقية</td><td>McGrath، Academy of Management Review 24(1)، 1999</td><td>الفكرة غير المختارة خيارٌ رخيص الحفظ يُمارَس حين يتحقّق شرطه</td></tr>
        <tr><td>المراجعة الحيّة + GRADE</td><td>Elliott وآخرون، J Clin Epidemiol 2017؛ Guyatt وآخرون، BMJ 2008</td><td>مراجعةٌ مؤرَّخة مستمرّة، وقوّة الدليل بسلّمٍ صريح (D0–D5)</td></tr>
      </tbody>
    </table></div>
    <div class="tbl"><table>
      <thead><tr><th>الدرجة</th><th>ما تعنيه</th></tr></thead>
      <tbody id="ladder"></tbody>
    </table></div>
  </section>

  <section aria-labelledby="h-studies">
    <h2 id="h-studies">الدراسات الأصلية التي غذّته</h2>
    <div class="tbl"><table>
      <thead><tr><th>الدراسة</th><th>التاريخ</th><th>العنوان</th><th>تغذّي</th><th>الخلاصة</th></tr></thead>
      <tbody id="studies"></tbody>
    </table></div>
  </section>
</div>

<script id="register-data" type="application/json">__DATA__</script>
<script>
(function () {
  var R = JSON.parse(document.getElementById("register-data").textContent);
  var V = R.vocabularies, recs = R.records;
  var $ = function (id) { return document.getElementById(id); };
  function el(tag, cls, text) { var e = document.createElement(tag); if (cls) e.className = cls; if (text != null) e.textContent = text; return e; }
  $("reviewed").textContent = R.reviewed_on;

  var f = R.flow;
  [["identified_ideas", "فكرة مُحدَّدة"], ["identified_value_chain_paths", "مسار في سلسلة القيمة"], ["identified_jobs", "وظيفة"],
   ["screened", "مُغربَلة بخمس بوّابات"], ["excluded", "مستبعدة ومحفوظة"], ["conditional", "مشروطة"], ["included", "متأهّلة"]
  ].forEach(function (p) { var d = el("div", p[0] === "included" ? "in" : ""); d.appendChild(el("b", "num", String(f[p[0]]))); d.appendChild(el("span", "", p[1])); $("flow").appendChild(d); });

  Object.keys(R.groups).forEach(function (k) {
    var g = R.groups[k], c = el("article", "group");
    c.appendChild(el("span", "k", k + " · " + V.option_state[g.option_state]));
    c.appendChild(el("h3", "", g.title_ar));
    var dl = el("dl");
    [["الأعضاء", g.members.join(" · ")], ["الاختبار التالي", g.next_test_ar], ["شرط الإيقاف", g.kill_ar]].forEach(function (p) { dl.appendChild(el("dt", "", p[0])); dl.appendChild(el("dd", "", p[1])); });
    c.appendChild(dl); $("groups").appendChild(c);
  });

  function fill(id, map, label) {
    var s = $(id); s.appendChild(new Option("الكلّ", ""));
    Object.keys(map).forEach(function (k) { s.appendChild(new Option(map[k], k)); });
  }
  fill("f-kind", V.kind); fill("f-stage", V.stage); fill("f-option", V.option_state); fill("f-domain", V.domain); fill("f-currency", V.currency);

  function stageShort(s) { return (V.stage[s] || s).split(" — ")[0]; }
  function card(r) {
    var d = el("details", "rec"); d.id = "rec-" + r.id;
    var s = el("summary");
    s.appendChild(el("span", "rid", r.id));
    s.appendChild(el("span", "rtitle", r.title_ar || "—"));
    var pills = el("span", "pills");
    pills.appendChild(el("span", "pill " + r.screening.stage, stageShort(r.screening.stage)));
    pills.appendChild(el("span", "pill", V.option_state[r.option.state]));
    if (r.evidence.level !== "na") pills.appendChild(el("span", "pill ev", r.evidence.level));
    s.appendChild(pills); d.appendChild(s);
    var b = el("div", "body");
    function block(h, node) { var x = el("div"); x.appendChild(el("h4", "", h)); x.appendChild(typeof node === "string" ? el("p", "", node) : node); b.appendChild(x); }
    if (r.facets && r.kind === "idea") {
      block("الأوجه", [V.domain[r.facets.domain], r.facets.markets.join(" · "), V.currency[r.facets.currency], V.delivery[r.facets.delivery]].join(" — "));
    }
    if (r.evidence.level !== "na") block("الدليل", r.evidence.level + " — " + r.evidence.basis_ar);
    if (r.kind !== "job" && r.screening.gates.G1 !== "na") {
      var gs = el("div", "gates");
      Object.keys(R.gates).forEach(function (k) { var v = r.screening.gates[k]; var gg = el("span", "gate " + v, k + " " + V.gate_verdict[v]); gg.title = R.gates[k]; gs.appendChild(gg); });
      block("البوّابات", gs);
    }
    if (r.audit && R.claims) {
      var byId = {}; R.claims.forEach(function (c) { byId[c.id] = c; });
      var al = el("div", "hist");
      Object.keys(R.gates).forEach(function (k) {
        var ids = r.audit.support[k] || [];
        var line = el("p"); line.appendChild(el("span", "gate " + r.screening.gates[k], k + " " + V.gate_verdict[r.screening.gates[k]]));
        if (!ids.length) { line.appendChild(document.createTextNode(" — لا سند")); }
        ids.forEach(function (cid) {
          var c = byId[cid]; if (!c) return;
          line.appendChild(document.createTextNode(" — "));
          line.appendChild(el("span", "num", cid + " · " + c.tier + " · " + c.event_date));
          line.appendChild(document.createTextNode(" " + R.audit_standard.kinds[c.kind] + ": "));
          if (c.url.indexOf("https://") === 0) { var a = el("a", "", c.source); a.href = c.url; a.target = "_blank"; a.rel = "noopener"; line.appendChild(a); }
          else { line.appendChild(el("span", "num", c.url.replace("repo:", ""))); }
        });
        al.appendChild(line);
      });
      block("التدقيق الصارم " + r.audit.standard + " (" + r.audit.date + ")", al);
    }
    if (r.screening.binding_constraint && r.screening.binding_constraint !== "none") block("العائق الحاسم", V.constraint[r.screening.binding_constraint] || r.screening.binding_constraint);
    block(r.option.state === "active_test" || r.option.state === "awaiting_owner" ? "الاختبار التالي" : "شرط إعادة الفتح", r.option.trigger_ar);
    if (r.group) block("المجموعة", r.group + " — " + R.groups[r.group].title_ar);
    if (r.related && r.related.length) block("يرتبط بـ", r.related.join(" · "));
    var src = el("p"); src.appendChild(el("span", "num", r.archive || ""));
    if (r.first_recorded) { src.appendChild(document.createTextNode(" · ")); src.appendChild(el("span", "num", r.first_recorded)); }
    if (r.addenda && r.addenda.length) src.appendChild(document.createTextNode(" · ملاحق: " + r.addenda.length));
    block("الأصل", src);
    if (r.history && r.history.length) {
      var hl = el("div", "hist");
      r.history.forEach(function (h) { var line = el("p"); line.appendChild(el("span", "num", h.date)); line.appendChild(document.createTextNode(" — " + h.event_ar)); hl.appendChild(line); });
      block("أثر التحديث", hl);
    }
    d.appendChild(b);
    return d;
  }
  var nodes = recs.map(function (r) { var c = card(r); $("cards").appendChild(c); return { r: r, el: c, text: (r.id + " " + (r.title_ar || "")).toLowerCase() }; });
  var empty = el("p", "empty", "لا سجلّ يطابق هذا الفرز. غيّر أحد المرشّحات أو اضغط «إظهار الكلّ».");
  empty.hidden = true; $("cards").appendChild(empty);

  function apply() {
    var q = $("f-q").value.trim().toLowerCase(), k = $("f-kind").value, st = $("f-stage").value, op = $("f-option").value, dm = $("f-domain").value, cu = $("f-currency").value, n = 0;
    nodes.forEach(function (x) {
      var r = x.r, ok = (!q || x.text.indexOf(q) >= 0) && (!k || r.kind === k) && (!st || r.screening.stage === st) && (!op || r.option.state === op)
        && (!dm || (r.facets && r.facets.domain === dm)) && (!cu || (r.facets && r.facets.currency === cu));
      x.el.hidden = !ok; if (ok) n++;
    });
    empty.hidden = n > 0;
    $("count").textContent = "يظهر " + n + " من " + nodes.length + " سجلّاً";
  }
  ["f-q", "f-kind", "f-stage", "f-option", "f-domain", "f-currency"].forEach(function (id) { $(id).addEventListener("input", apply); });
  $("f-reset").addEventListener("click", function () { $("filters").reset(); apply(); });
  apply();

  Object.keys(V.evidence_level).forEach(function (k) { if (k === "na") return; var tr = el("tr"); tr.appendChild(el("td", "num", k)); tr.appendChild(el("td", "", V.evidence_level[k])); $("ladder").appendChild(tr); });
  R.studies.forEach(function (s) { var tr = el("tr"); [s.id, s.date, s.title_ar, s.feeds.join(" · "), s.finding_ar].forEach(function (v, i) { tr.appendChild(el("td", i < 2 ? "num" : "", v)); }); $("studies").appendChild(tr); });

  if (location.hash && /^#B\d{2}|^#J\d{2}|^#OPP-\d{2}/.test(location.hash)) { var t = $("rec-" + location.hash.slice(1)); if (t) { t.open = true; t.scrollIntoView(); } }
})();
</script>
"""
out.write_text(HTML.replace("__DATA__", data), encoding="utf-8")
print("wrote", out, len(HTML) + len(data))
