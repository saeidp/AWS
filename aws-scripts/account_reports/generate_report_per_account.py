#!/usr/bin/env python3
"""
Generate one standalone HTML tag-compliance report *per AWS account* from a
single AWS resource-tag compliance CSV export.

The CSV has the usual columns: AccountId, Region, ResourceType,
ComplianceStatus, NoncompliantKeys, KeysWithNoncompliantValues,
MissingTagKeys, ResourceARN, Tags, LastUpdated, PolicyLastUpdated.

Rows are grouped by AccountId and each account gets two files, so a team can
be sent only its own data:

    <prefix>_<accountid>.html  self-contained dashboard (no external assets,
                               no network calls) listing *every* non-compliant
                               resource, filterable and sortable
    <prefix>_<accountid>.csv   the underlying rows, all original columns

--top caps the charts and the crosstab only; the resource table is complete.

Usage:
    python3 generate_report_per_account.py <input.csv> <output_dir>
        [--top N] [--prefix NAME] [--no-csv] [--all-rows]

    <input.csv>   path to the compliance report CSV
    <output_dir>  directory to write the per-account files into
                  (created if it doesn't exist)
    --top N       max rows/bars per chart section (default 10)
    --prefix NAME base filename (default "tag_compliance_report")
    --no-csv      skip the per-account CSV
    --all-rows    include compliant resources in the CSV too
"""
import argparse
import csv
import json
import os
import sys
from collections import Counter, defaultdict
from html import escape

TEMPLATE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<style>
.viz-root {{
  --surface-1:      #fcfcfb;
  --page:           #f9f9f7;
  --text-primary:   #0b0b0b;
  --text-secondary: #52514e;
  --text-muted:     #898781;
  --grid:           #e1e0d9;
  --baseline:       #c3c2b7;
  --border:         rgba(11,11,11,0.10);
  --series-1:       #2a78d6;
  --series-2:       #1baf7a;
  --series-3:       #eda100;
  --series-5:       #4a3aa7;
  --status-critical:#d03b3b;
  --status-warning: #fab219;
  --status-good:    #0ca30c;
}}
@media (prefers-color-scheme: dark) {{
  .viz-root {{
    --surface-1:      #1a1a19;
    --page:           #0d0d0d;
    --text-primary:   #ffffff;
    --text-secondary: #c3c2b7;
    --text-muted:     #898781;
    --grid:           #2c2c2a;
    --baseline:       #383835;
    --border:         rgba(255,255,255,0.10);
    --series-1:       #3987e5;
    --series-2:       #199e70;
    --series-3:       #c98500;
    --series-5:       #9085e9;
  }}
}}
:root[data-theme="dark"] .viz-root {{
  --surface-1:      #1a1a19; --page:#0d0d0d; --text-primary:#ffffff;
  --text-secondary:#c3c2b7; --text-muted:#898781; --grid:#2c2c2a;
  --baseline:#383835; --border:rgba(255,255,255,0.10);
  --series-1:#3987e5; --series-2:#199e70; --series-3:#c98500; --series-5:#9085e9;
}}
:root[data-theme="light"] .viz-root {{
  --surface-1:      #fcfcfb; --page:#f9f9f7; --text-primary:#0b0b0b;
  --text-secondary:#52514e; --text-muted:#898781; --grid:#e1e0d9;
  --baseline:#c3c2b7; --border:rgba(11,11,11,0.10);
  --series-1:#2a78d6; --series-2:#1baf7a; --series-3:#eda100; --series-5:#4a3aa7;
}}
* {{ box-sizing: border-box; }}
body {{ margin:0; }}
.viz-root {{
  font-family: system-ui, -apple-system, "Segoe UI", sans-serif;
  background: var(--page); color: var(--text-primary);
  padding: 32px 20px 60px;
}}
.wrap {{ max-width: 980px; margin: 0 auto; }}
h1 {{ font-size: 22px; margin: 0 0 4px; }}
.subtitle {{ color: var(--text-secondary); font-size: 14px; margin: 0 0 28px; }}
.stat-row {{ display:grid; grid-template-columns: repeat(auto-fit, minmax(180px,1fr)); gap:12px; margin-bottom:28px; }}
.stat-tile {{ background: var(--surface-1); border:1px solid var(--border); border-radius:10px; padding:16px 18px; }}
.stat-tile .label {{ font-size:12px; color:var(--text-muted); margin-bottom:6px; }}
.stat-tile .value {{ font-size:28px; font-weight:600; line-height:1; }}
.stat-tile .value.crit {{ color: var(--status-critical); }}
.stat-tile .foot {{ font-size:12px; color:var(--text-secondary); margin-top:6px; }}
.card {{ background: var(--surface-1); border:1px solid var(--border); border-radius:10px; padding:20px 22px 22px; margin-bottom:20px; }}
.card h2 {{ font-size:15px; margin:0 0 2px; }}
.card .desc {{ font-size:12.5px; color:var(--text-secondary); margin:0 0 16px; }}
.bar-row {{ display:grid; grid-template-columns:190px 1fr 56px; align-items:center; gap:10px; margin:9px 0; }}
.bar-row .name {{ font-size:12.5px; color:var(--text-secondary); text-align:right; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }}
.bar-track {{ background: var(--grid); border-radius:4px; height:16px; position:relative; overflow:hidden; }}
.bar-fill {{ height:100%; border-radius:4px; }}
.bar-row .count {{ font-size:12.5px; color:var(--text-primary); font-variant-numeric: tabular-nums; }}
table {{ width:100%; border-collapse:collapse; font-size:12.5px; }}
th {{ text-align:left; color:var(--text-muted); font-weight:500; padding:6px 10px; border-bottom:1px solid var(--grid); font-size:11.5px; text-transform:uppercase; letter-spacing:.02em; }}
td {{ padding:8px 10px; border-bottom:1px solid var(--grid); vertical-align:top; }}
tr:last-child td {{ border-bottom:none; }}
.mono {{ font-family: ui-monospace, SFMono-Regular, Menlo, monospace; font-size:11.5px; color:var(--text-secondary); }}
.tag-chip {{ display:inline-block; background:rgba(208,59,59,0.10); color:var(--status-critical); border-radius:4px; padding:1px 6px; font-size:11px; margin:1px 3px 1px 0; }}
.tag-chip.warn {{ background:rgba(250,178,25,0.14); color:#a56a00; }}
.tag-chip .chip-k {{ font-family: ui-monospace, SFMono-Regular, Menlo, monospace; opacity:.7; margin-right:4px; }}
@media (prefers-color-scheme: dark) {{ .tag-chip.warn {{ color: var(--status-warning); }} }}
:root[data-theme="dark"] .tag-chip.warn {{ color: var(--status-warning); }}
.scroll-x {{ overflow-x:auto; }}
.tbl-controls {{ display:flex; gap:10px; align-items:center; margin-bottom:12px; flex-wrap:wrap; }}
.tbl-controls input {{ flex:1; min-width:200px; background:var(--page); color:var(--text-primary);
  border:1px solid var(--border); border-radius:6px; padding:7px 10px; font-size:12.5px; font-family:inherit; }}
.tbl-controls input:focus {{ outline:2px solid var(--series-1); outline-offset:-1px; }}
.tbl-controls .hint {{ font-size:12px; color:var(--text-muted); white-space:nowrap; }}
.tbl-scroll {{ overflow:auto; max-height:640px; }}
.tbl-scroll thead th {{ position:sticky; top:0; background:var(--surface-1); z-index:1; }}
th.sortable {{ cursor:pointer; user-select:none; }}
th.sortable:hover {{ color:var(--text-secondary); }}
th.sortable::after {{ content:"\\2195"; opacity:.35; margin-left:4px; }}
th.sortable.asc::after {{ content:"\\2191"; opacity:1; }}
th.sortable.desc::after {{ content:"\\2193"; opacity:1; }}
.empty {{ color:var(--text-muted); font-size:12.5px; padding:14px 10px; }}
.cause-note {{ font-size:12.5px; color:var(--text-secondary); margin:16px 0 0; padding-top:14px;
  border-top:1px solid var(--grid); }}
/* cause labels carry a value and a percentage, so they need more room */
#causes .bar-row {{ grid-template-columns: 300px 1fr 56px; }}
@media (max-width: 620px) {{ #causes .bar-row {{ grid-template-columns: 150px 1fr 48px; }} }}
.legend {{ display:flex; gap:16px; font-size:12px; color:var(--text-secondary); margin-bottom:14px; flex-wrap:wrap; }}
.legend span {{ display:inline-flex; align-items:center; gap:6px; }}
.swatch {{ width:10px; height:10px; border-radius:2px; display:inline-block; }}
</style>
</head>
<body>
<div class="viz-root">
<div class="wrap">

<h1>{title}</h1>
<p class="subtitle">{subtitle}</p>

<div class="stat-row">
  <div class="stat-tile"><div class="label">Resources scanned</div><div class="value">{total:,}</div></div>
  <div class="stat-tile"><div class="label">Non-compliant</div><div class="value crit">{noncompliant:,}</div><div class="foot">{noncompliant_pct}% of all resources</div></div>
  <div class="stat-tile"><div class="label">Compliant</div><div class="value">{compliant:,}</div><div class="foot">{compliant_pct}% of all resources</div></div>
  <div class="stat-tile"><div class="label">Regions affected</div><div class="value">{n_regions}</div><div class="foot">{region_foot}</div></div>
</div>

<div class="card">
  <h2>Top systemic causes</h2>
  <p class="desc">Every non-compliant resource counted once, grouped by what is actually wrong with it.
     Sentinel values such as <span class="mono">placeholder</span> point at provisioning, not at owners.</p>
  <div id="causes"></div>
  <p class="cause-note">{cause_note}</p>
</div>

<div class="card">
  <h2>Non-compliant resources by type</h2>
  <p class="desc">Top resource types contributing to violations.</p>
  <div id="bytype"></div>
</div>

<div class="card">
  <h2>Why resources fail: missing tags vs. bad values</h2>
  <p class="desc">A resource can fail for either reason &mdash; some fail both.</p>
  <div class="legend">
    <span><span class="swatch" style="background:var(--series-1)"></span>Missing required tag key</span>
    <span><span class="swatch" style="background:#e34948"></span>Tag present, value invalid</span>
  </div>
  <div id="byreason"></div>
</div>

<div class="card">
  <h2>Most common missing tag keys</h2>
  <div id="missing"></div>
</div>

<div class="card">
  <h2>Most common invalid tag values</h2>
  <div id="badvals"></div>
</div>

<div class="card">
  <h2>Sample invalid values observed</h2>
  <div class="scroll-x">
  <table>
    <thead><tr><th>Tag key</th><th>Bad value found</th><th>Occurrences</th></tr></thead>
    <tbody id="badval-samples"></tbody>
  </table>
  </div>
</div>

<div class="card">
  <h2>Resource type &times; failure reason</h2>
  <div class="scroll-x">
  <table>
    <thead><tr><th>Resource type</th><th>Total non-compliant</th><th>Missing tags</th><th>Bad values</th></tr></thead>
    <tbody id="crosstab"></tbody>
  </table>
  </div>
</div>

<div class="card">
  <h2>All non-compliant resources</h2>
  <p class="desc">Every non-compliant resource in this account &mdash; the full list, not a sample.
     The same rows are in <span class="mono">{csv_name}</span> next to this file.</p>
  <div class="tbl-controls">
    <input id="filter" type="search" placeholder="Filter by ARN, region, resource type, tag key or bad value&hellip;"
           aria-label="Filter resources">
    <span class="hint" id="rowcount"></span>
  </div>
  <div class="tbl-scroll">
  <table>
    <thead><tr>
      <th class="sortable" data-key="arn">Resource</th>
      <th class="sortable" data-key="region">Region</th>
      <th class="sortable" data-key="type">Type</th>
      <th class="sortable" data-key="missing">Missing tags</th>
      <th class="sortable" data-key="bad">Invalid-value tags</th>
    </tr></thead>
    <tbody id="samples"></tbody>
  </table>
  </div>
</div>

</div>
</div>

<script>
const ESC = {{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}};
function esc(s) {{ return String(s == null ? '' : s).replace(/[&<>"']/g, c => ESC[c]); }}

function bar(container, data, color) {{
  const max = Math.max(...data.map(d => d.value), 1);
  container.innerHTML = data.map(d => `
    <div class="bar-row">
      <div class="name" title="${{esc(d.label)}}">${{esc(d.label)}}</div>
      <div class="bar-track"><div class="bar-fill" style="width:${{(d.value/max*100).toFixed(1)}}%; background:${{d.color || color}}"></div></div>
      <div class="count">${{d.value}}</div>
    </div>`).join('');
}}

const causes = {causes_json};
bar(document.getElementById('causes'), causes, '#e34948');

const byType = {by_type_json};
bar(document.getElementById('bytype'), byType, 'var(--series-1)');

const byReason = {by_reason_json};
bar(document.getElementById('byreason'), byReason, 'var(--series-1)');

const missing = {missing_json};
bar(document.getElementById('missing'), missing, 'var(--series-1)');

const badvals = {badvals_json};
bar(document.getElementById('badvals'), badvals, '#e34948');

document.getElementById('badval-samples').innerHTML = {badval_samples_json}.map(r => `
  <tr><td class="mono">${{esc(r.key)}}</td><td>${{esc(r.value)}}</td><td>${{r.count}}</td></tr>
`).join('');

document.getElementById('crosstab').innerHTML = {crosstab_json}.map(r => `
  <tr><td class="mono">${{esc(r.type)}}</td><td>${{r.total}}</td><td>${{r.missing}}</td><td>${{r.bad}}</td></tr>
`).join('');

// ---- full non-compliant resource table: filter + sort over every row ----
const ROWS = {samples_json};
const tbody = document.getElementById('samples');
const countEl = document.getElementById('rowcount');
const dash = '<span style="color:var(--text-muted)">&mdash;</span>';
let sortKey = null, sortDir = 1, view = ROWS;

function chips(list) {{
  return list.length ? list.map(t => `<span class="tag-chip">${{esc(t)}}</span>`).join('') : dash;
}}

// invalid-value tags render as "key: bad-value" so the fix is self-evident
function pairText(t) {{ return t.k + ': ' + (t.v === '' ? '(empty)' : t.v); }}
function pairChips(list) {{
  return list.length ? list.map(t =>
    `<span class="tag-chip warn"><span class="chip-k">${{esc(t.k)}}:</span>${{esc(t.v === '' ? '(empty)' : t.v)}}</span>`
  ).join('') : dash;
}}

function draw() {{
  tbody.innerHTML = view.length ? view.map(s => `
    <tr>
      <td class="mono">${{esc(s.arn)}}</td>
      <td>${{esc(s.region)}}</td>
      <td>${{esc(s.type)}}</td>
      <td>${{chips(s.missing)}}</td>
      <td>${{pairChips(s.bad)}}</td>
    </tr>`).join('')
    : `<tr><td colspan="5" class="empty">No resources match this filter.</td></tr>`;
  countEl.textContent = view.length === ROWS.length
    ? `${{ROWS.length}} resources`
    : `${{view.length}} of ${{ROWS.length}} resources`;
}}

function apply() {{
  const q = document.getElementById('filter').value.trim().toLowerCase();
  view = q ? ROWS.filter(s => (
    s.arn.toLowerCase().includes(q) || s.region.toLowerCase().includes(q) ||
    s.type.toLowerCase().includes(q) ||
    s.missing.some(t => t.toLowerCase().includes(q)) ||
    s.bad.some(t => pairText(t).toLowerCase().includes(q))
  )) : ROWS.slice();
  if (sortKey) {{
    const key = s => {{
      const v = s[sortKey];
      if (!Array.isArray(v)) return v;
      return v.map(t => (typeof t === 'string' ? t : pairText(t))).join(',');
    }};
    view = view.slice().sort((a, b) => {{
      const x = key(a), y = key(b);
      return x < y ? -sortDir : x > y ? sortDir : 0;
    }});
  }}
  draw();
}}

document.getElementById('filter').addEventListener('input', apply);
document.querySelectorAll('th.sortable').forEach(th => {{
  th.addEventListener('click', () => {{
    const k = th.dataset.key;
    sortDir = (sortKey === k) ? -sortDir : 1;
    sortKey = k;
    document.querySelectorAll('th.sortable').forEach(o => o.classList.remove('asc', 'desc'));
    th.classList.add(sortDir === 1 ? 'asc' : 'desc');
    apply();
  }});
}});
apply();
</script>
</body>
</html>
"""


def js_json(obj):
    """json.dumps for embedding inside a <script> block.

    Escapes the three characters that could break out of the script element
    (a literal '</script' in any tag value would otherwise blank the page).
    """
    return (json.dumps(obj)
            .replace("<", "\\u003c")
            .replace(">", "\\u003e")
            .replace("&", "\\u0026"))


def parse_tags(raw):
    if not raw:
        return {}
    try:
        return json.loads(raw)
    except (json.JSONDecodeError, TypeError):
        return {}


def analyze(rows, top_n):
    total = len(rows)
    noncompliant = [r for r in rows if r.get("ComplianceStatus", "").strip().lower() == "false"]
    compliant_count = total - len(noncompliant)

    by_type = Counter(r.get("ResourceType", "unknown") for r in noncompliant)
    regions = Counter(r.get("Region", "unknown") for r in noncompliant)

    missing_ctr = Counter()
    badkey_ctr = Counter()
    badvalue_samples = defaultdict(Counter)
    type_reason = defaultdict(lambda: {"missing": 0, "bad": 0})

    # resources failing for each reason (a resource can be in both)
    n_missing_resources = 0
    n_bad_resources = 0

    # Each non-compliant resource lands in exactly one "cause" bucket, so the
    # buckets sum to the account total and a team can see at a glance whether
    # they have one repeated cause or many independent ones.
    cause_ctr = Counter()

    for r in noncompliant:
        rtype = r.get("ResourceType", "unknown")
        mk = (r.get("MissingTagKeys") or "").strip()
        bv = (r.get("KeysWithNoncompliantValues") or "").strip()
        tags = parse_tags(r.get("Tags"))

        bvk = [k.strip() for k in bv.split(",") if k.strip()]
        if bvk:
            # bucket on the value repeated across the most of this resource's
            # bad tags; ties broken alphabetically so output is deterministic
            vc = Counter(tags.get(k, "") for k in bvk)
            val = sorted(vc.items(), key=lambda kv: (-kv[1], kv[0]))[0][0]
            cause_ctr[f'value "{val}"' if val else "empty tag value"] += 1
        else:
            cause_ctr["missing required tags only"] += 1

        if mk:
            n_missing_resources += 1
            type_reason[rtype]["missing"] += 1
            for k in mk.split(","):
                k = k.strip()
                if k:
                    missing_ctr[k] += 1
        if bv:
            n_bad_resources += 1
            type_reason[rtype]["bad"] += 1
            for k in bv.split(","):
                k = k.strip()
                if k:
                    badkey_ctr[k] += 1
                    val = tags.get(k, "")
                    badvalue_samples[k][val] += 1

    crosstab = []
    for rtype, cnt in by_type.most_common():
        tr = type_reason[rtype]
        crosstab.append({"type": rtype, "total": cnt, "missing": tr["missing"], "bad": tr["bad"]})

    badval_samples = []
    for key, ctr in badkey_ctr.most_common():
        for val, cnt in badvalue_samples[key].most_common(3):
            badval_samples.append({"key": key, "value": str(val) or "(empty)", "count": cnt})
    badval_samples.sort(key=lambda x: -x["count"])
    badval_samples = badval_samples[: top_n * 3]

    # Every non-compliant resource, not a sample -- --top governs the charts
    # and crosstab only. Tags are deliberately left out (they average ~600
    # bytes/row); the sibling CSV carries the complete record.
    samples = []
    for r in noncompliant:
        mk = [k.strip() for k in (r.get("MissingTagKeys") or "").split(",") if k.strip()]
        tags = parse_tags(r.get("Tags"))
        # carry the offending value, not just the key -- "org:environment: placsholder"
        # tells someone what to fix; the bare key does not
        bv = [{"k": k.strip(), "v": tags.get(k.strip(), "")}
              for k in (r.get("KeysWithNoncompliantValues") or "").split(",") if k.strip()]
        samples.append(
            {
                "arn": r.get("ResourceARN", ""),
                "region": r.get("Region", ""),
                "type": r.get("ResourceType", ""),
                "missing": mk,
                "bad": bv,
            }
        )

    return {
        "total": total,
        "noncompliant": len(noncompliant),
        "compliant": compliant_count,
        "by_type": by_type.most_common(top_n),
        "by_type_other": sum(c for _, c in by_type.most_common()[top_n:]),
        "by_reason": [("Missing required tag key", n_missing_resources),
                      ("Tag present, value invalid", n_bad_resources)],
        "causes": cause_ctr.most_common(top_n),
        "causes_other": sum(c for _, c in cause_ctr.most_common()[top_n:]),
        "n_causes": len(cause_ctr),
        "regions": regions,
        "missing": missing_ctr.most_common(top_n),
        "badkeys": badkey_ctr.most_common(top_n),
        "crosstab": crosstab[:top_n],
        "badval_samples": badval_samples,
        "samples": samples,
    }


def render(stats, account_id, csv_path, csv_name):
    total = stats["total"]
    nc = stats["noncompliant"]
    c = stats["compliant"]
    nc_pct = round(100 * nc / total, 1) if total else 0
    c_pct = round(100 * c / total, 1) if total else 0

    by_type = [{"label": k, "value": v} for k, v in stats["by_type"]]
    if stats["by_type_other"]:
        by_type.append({"label": "other", "value": stats["by_type_other"]})

    by_reason = [{"label": k, "value": v, "color": ("#e34948" if "invalid" in k else "var(--series-1)")}
                 for k, v in stats["by_reason"]]

    def cause_row(label, count):
        pct = round(100 * count / nc) if nc else 0
        return {"label": f"{label} — {pct}%", "value": count,
                "color": ("var(--series-1)" if label.startswith("missing") else "#e34948")}

    causes = [cause_row(k, v) for k, v in stats["causes"]]
    if stats["causes_other"]:
        causes.append(cause_row("other causes", stats["causes_other"]))

    # one-line read of how concentrated this account's problem is
    if stats["causes"] and nc:
        top_label, top_count = stats["causes"][0]
        top_pct = round(100 * top_count / nc)
        if top_label.startswith("missing"):
            cause_note = (f"{top_pct}% of violations here are simply absent tags, "
                          f"which means per-resource remediation rather than a single fix.")
        elif top_pct >= 50:
            cause_note = (f"{top_pct}% of violations share one cause — {top_label}. "
                          f"That points at whatever provisions these resources, not at individual owners.")
        else:
            cause_note = (f"No single dominant cause: the largest bucket ({top_label}) "
                          f"covers {top_pct}%, spread across {stats['n_causes']} distinct causes.")
    else:
        cause_note = "No non-compliant resources in this account."

    missing = [{"label": k, "value": v} for k, v in stats["missing"]]
    badvals = [{"label": k, "value": v} for k, v in stats["badkeys"]]

    n_regions = len(stats["regions"])
    region_foot = ", ".join(f"{v} in {k}" for k, v in stats["regions"].most_common(5))

    html = TEMPLATE.format(
        title=escape(f"Tag Compliance Report — Account {account_id}"),
        subtitle=escape(f"Account {account_id} · source: {os.path.basename(csv_path)}"),
        total=total,
        noncompliant=nc,
        noncompliant_pct=nc_pct,
        compliant=c,
        compliant_pct=c_pct,
        n_regions=n_regions,
        region_foot=escape(region_foot),
        csv_name=escape(csv_name),
        cause_note=escape(cause_note),
        causes_json=js_json(causes),
        by_type_json=js_json(by_type),
        by_reason_json=js_json(by_reason),
        missing_json=js_json(missing),
        badvals_json=js_json(badvals),
        badval_samples_json=js_json(stats["badval_samples"]),
        crosstab_json=js_json(stats["crosstab"]),
        samples_json=js_json(stats["samples"]),
    )
    return html


def safe_account(account_id):
    """Make an AccountId safe to use in a filename."""
    return "".join(ch if ch.isalnum() or ch in "-_" else "_" for ch in str(account_id)) or "unknown"


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("input_csv")
    ap.add_argument("output_dir")
    ap.add_argument("--top", type=int, default=10, help="max rows/bars per section (default 10)")
    ap.add_argument("--prefix", default="tag_compliance_report",
                    help="base filename; files are <prefix>_<accountid>.html")
    ap.add_argument("--no-csv", action="store_true",
                    help="skip the per-account CSV that accompanies each report")
    ap.add_argument("--all-rows", action="store_true",
                    help="include compliant resources in the per-account CSV "
                         "(default: non-compliant rows only)")
    args = ap.parse_args()

    with open(args.input_csv, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        fieldnames = reader.fieldnames or []

    required = {"ComplianceStatus", "ResourceType", "ResourceARN"}
    if not required.issubset(fieldnames):
        miss = required - set(fieldnames)
        print(f"warning: CSV is missing expected columns: {miss}", file=sys.stderr)
    if "AccountId" not in fieldnames:
        print("warning: CSV has no AccountId column; all rows grouped under 'unknown'",
              file=sys.stderr)

    # group rows by account
    by_account = defaultdict(list)
    for r in rows:
        by_account[(r.get("AccountId") or "unknown").strip() or "unknown"].append(r)

    os.makedirs(args.output_dir, exist_ok=True)

    print(f"{len(rows)} rows across {len(by_account)} account(s)")
    for account_id, arows in sorted(by_account.items()):
        base = f"{args.prefix}_{safe_account(account_id)}"
        csv_name = f"{base}.csv"
        stats = analyze(arows, args.top)
        html = render(stats, account_id, args.input_csv, csv_name)
        out_path = os.path.join(args.output_dir, f"{base}.html")
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(html)

        n_csv = 0
        if not args.no_csv:
            crows = arows if args.all_rows else [
                r for r in arows
                if (r.get("ComplianceStatus") or "").strip().lower() == "false"
            ]
            n_csv = len(crows)
            # utf-8-sig so Excel doesn't mangle non-ASCII tag values
            with open(os.path.join(args.output_dir, csv_name), "w",
                      newline="", encoding="utf-8-sig") as f:
                w = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
                w.writeheader()
                w.writerows(crows)

        pct = round(100 * stats["noncompliant"] / stats["total"], 1) if stats["total"] else 0
        extra = "" if args.no_csv else f" + {n_csv} CSV rows"
        print(f"  {account_id}: {stats['total']} resources, "
              f"{stats['noncompliant']} non-compliant ({pct}%) -> {out_path}{extra}")


if __name__ == "__main__":
    main()
