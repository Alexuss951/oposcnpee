"""
Embed all parsed question banks into app/index.html.

Reads every JSON in `estructurado/escala-{basica,ejecutiva}/` and writes a
single minified JS literal between two sentinel comments inside
`app/index.html`:

    /* >>> BANK START <<< */
    const PREGUNTAS = [...];
    const PREGUNTAS_META = {...};
    /* >>> BANK END <<< */

The app remains a single self-contained HTML file with no runtime fetch.
Rerun this script whenever the JSON sources change (e.g. tema mapping
filled in, typo fixed, new promotion added).

Each PREGUNTAS row: {id, src, n, e, o:[a,b,c], c, d, t}
  id  – stable string id "EE-P40-Q012" / "EB-P38-Q045"
  src – source label "Ejecutiva P40 (Jurispol)" / "Básica P37 (MAD)"
  n   – question number inside the source (1..100)
  e   – enunciado (statement)
  o   – three options [a, b, c]
  c   – correct index 0|1|2 (null if unknown)
  d   – difficulty "facil"|"media"|"dificil" or null
  t   – tema number 1..81 or null
  x   – explanation (only for Jurispol ejecutiva; "" otherwise)
"""

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC_DIR = ROOT / "examenes" / "estructurado"
APP_FILE = ROOT / "app" / "index.html"

MARK_START = "/* >>> BANK START <<< */"
MARK_END = "/* >>> BANK END <<< */"


def label(scale: str, promo: int, fuente: str) -> str:
    """Short human label used in the exam UI."""
    src = "Jurispol" if "jurispol" in fuente.lower() else "MAD"
    name = "Ejecutiva" if scale == "ejecutiva" else "Básica"
    return f"{name} P{promo} ({src})"


def load_bank() -> tuple[list[dict], dict]:
    rows: list[dict] = []
    sources: list[dict] = []
    for scale in ("ejecutiva", "basica"):
        folder = SRC_DIR / f"escala-{scale}"
        if not folder.exists():
            continue
        for f in sorted(folder.glob("promocion*.json")):
            data = json.loads(f.read_text(encoding="utf-8"))
            promo = int(data["promocion"])
            prefix = f"{'EE' if scale == 'ejecutiva' else 'EB'}-P{promo:02d}"
            src_label = label(scale, promo, data.get("fuente", ""))
            count = 0
            for q in data["preguntas"]:
                rows.append({
                    "id": f"{prefix}-Q{q['n']:03d}",
                    "src": src_label,
                    "n": q["n"],
                    "e": q["enunciado"],
                    "o": q["opciones"],
                    "c": q["correcta"],
                    "d": q.get("dificultad"),
                    "t": q.get("tema"),
                    "x": q.get("explicacion") or "",
                })
                count += 1
            sources.append({
                "key": prefix,
                "label": src_label,
                "scale": scale,
                "promo": promo,
                "count": count,
            })
    meta = {
        "total": len(rows),
        "sources": sources,
    }
    return rows, meta


def to_js_literal(rows: list[dict], meta: dict) -> str:
    """Serialize to compact JSON; safe inside a <script> tag because all
    user-supplied text is JSON-escaped. The closing '</script>' sequence
    is broken just in case (defense in depth)."""
    rows_json = json.dumps(rows, ensure_ascii=False, separators=(",", ":"))
    meta_json = json.dumps(meta, ensure_ascii=False, separators=(",", ":"))
    # break any accidental </script> in question text
    rows_json = rows_json.replace("</", "<\\/")
    meta_json = meta_json.replace("</", "<\\/")
    return (
        f"{MARK_START}\n"
        f"const PREGUNTAS = {rows_json};\n"
        f"const PREGUNTAS_META = {meta_json};\n"
        f"{MARK_END}"
    )


def main() -> int:
    rows, meta = load_bank()
    if not rows:
        print("no questions found", file=sys.stderr)
        return 1

    if not APP_FILE.exists():
        print(f"missing {APP_FILE}", file=sys.stderr)
        return 1

    html = APP_FILE.read_text(encoding="utf-8")
    block = to_js_literal(rows, meta)

    pattern = re.compile(
        re.escape(MARK_START) + r".*?" + re.escape(MARK_END),
        re.DOTALL,
    )
    if not pattern.search(html):
        print(f"sentinel markers not found in {APP_FILE.name}", file=sys.stderr)
        print("add this somewhere inside <script>:", file=sys.stderr)
        print(f"  {MARK_START}\n  const PREGUNTAS = [];\n  const PREGUNTAS_META = {{total:0,sources:[]}};\n  {MARK_END}",
              file=sys.stderr)
        return 1

    new_html = pattern.sub(lambda _: block, html, count=1)
    APP_FILE.write_text(new_html, encoding="utf-8")

    print(f"embedded {meta['total']} questions from {len(meta['sources'])} sources")
    for s in meta["sources"]:
        print(f"  - {s['label']:<30} {s['count']:3d} q")
    size_kb = len(new_html.encode("utf-8")) / 1024
    print(f"app/index.html now: {size_kb:.1f} KB")
    return 0


if __name__ == "__main__":
    sys.exit(main())
