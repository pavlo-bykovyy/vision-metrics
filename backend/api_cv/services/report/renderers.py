"""Renderers: report dict -> Markdown / standalone HTML."""
from __future__ import annotations

from html import escape
from typing import Any


def _fmt(v: Any) -> str:
    return "—" if v is None else (f"{v:.4f}" if isinstance(v, float) else str(v))


def to_markdown(r: dict[str, Any]) -> str:
    meta, prof = r["meta"], r["profile"]
    lines = [
        f"# Evaluation report #{meta['evaluation_id']}",
        "",
        f"- Model: {meta.get('model_name')}",
        f"- Dataset: {meta.get('dataset_name')}",
        f"- Created: {meta.get('created_at')}",
        f"- Samples: {_fmt(prof['n'])}, prevalence: {_fmt(prof['prevalence'])}, "
        f"threshold: {prof['threshold']}",
        f"- Overall status: **{r['status'].upper()}**",
        "",
        "## Metric profile",
        "",
        "| Metric | Value |",
        "|---|---|",
    ]
    lines += [f"| {k} | {_fmt(v)} |" for k, v in prof["metrics"].items()]
    c = prof["confusion"]
    lines += ["", f"Confusion: TN={c['tn']}, FP={c['fp']}, FN={c['fn']}, TP={c['tp']}", "",
              "## Findings", ""]
    if not r["findings"]:
        lines.append("No discordance patterns detected.")
    for f in r["findings"]:
        lines.append(f"- **[{f['severity']}] {f['title']}** (`{f['code']}`). {f['hint']}")
        lines.append(f"  - evidence: {f['evidence']}")
    if r.get("baseline"):
        b = r["baseline"]
        lines += ["", f"## Comparison with baseline #{b['meta']['evaluation_id']}", "",
                  "| Metric | Delta |", "|---|---|"]
        lines += [f"| {k} | {_fmt(v)} |" for k, v in b["deltas"].items()]
        lines.append("")
        if not b["hypotheses"]:
            lines.append("No similarity to the controlled failure signatures.")
        for h in b["hypotheses"]:
            lines.append(f"- Similar to **{h['similar_to']}** ({h['confidence']} confidence): {h['why']}")
    lines += ["", "---", f"_{r['disclaimer']}_", ""]
    return "\n".join(lines)


_COLORS = {"ok": "#2e7d32", "warning": "#ed6c02", "critical": "#c62828", "info": "#1565c0"}


def to_html(r: dict[str, Any]) -> str:
    meta, prof = r["meta"], r["profile"]
    e = escape
    rows = "".join(f"<tr><td>{e(k)}</td><td>{e(_fmt(v))}</td></tr>"
                   for k, v in prof["metrics"].items())
    findings = "".join(
        f"<li><b style='color:{_COLORS.get(f['severity'], '#000')}'>[{e(f['severity'])}]</b> "
        f"{e(f['title'])} <code>{e(f['code'])}</code><br><small>{e(f['hint'])}</small></li>"
        for f in r["findings"]
    ) or "<li>No discordance patterns detected.</li>"

    baseline = ""
    if r.get("baseline"):
        b = r["baseline"]
        drows = "".join(f"<tr><td>{e(k)}</td><td>{e(_fmt(v))}</td></tr>" for k, v in b["deltas"].items())
        hyps = "".join(
            f"<li>Similar to <b>{e(h['similar_to'])}</b> ({e(h['confidence'])}): {e(h['why'])}</li>"
            for h in b["hypotheses"]
        ) or "<li>No similarity to the controlled failure signatures.</li>"
        baseline = (f"<h2>Comparison with baseline #{e(str(b['meta']['evaluation_id']))}</h2>"
                    f"<table><tr><th>Metric</th><th>Delta</th></tr>{drows}</table><ul>{hyps}</ul>")

    return f"""<!doctype html><html><head><meta charset="utf-8">
<title>Evaluation report #{e(str(meta['evaluation_id']))}</title>
<style>body{{font-family:system-ui,sans-serif;max-width:860px;margin:2rem auto;padding:0 1rem}}
table{{border-collapse:collapse}}td,th{{border:1px solid #ccc;padding:4px 10px;text-align:left}}
.status{{color:#fff;padding:2px 10px;border-radius:4px;background:{_COLORS[r['status']]}}}</style></head><body>
<h1>Evaluation report #{e(str(meta['evaluation_id']))}</h1>
<p>Model: {e(str(meta.get('model_name')))} · Dataset: {e(str(meta.get('dataset_name')))} ·
Samples: {e(_fmt(prof['n']))} · Prevalence: {e(_fmt(prof['prevalence']))}</p>
<p>Status: <span class="status">{e(r['status'].upper())}</span></p>
<h2>Metric profile</h2><table><tr><th>Metric</th><th>Value</th></tr>{rows}</table>
<h2>Findings</h2><ul>{findings}</ul>{baseline}
<hr><p><small>{e(r['disclaimer'])}</small></p></body></html>"""
