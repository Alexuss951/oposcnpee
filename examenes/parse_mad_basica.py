"""
Parse MAD "EXAMEN-PROMOCION{N}.pdf" text files (Escala Básica) into JSON.

Each PDF text follows this format:
    1. <statement, multi-line>
        a) <option a>
        b) <option b>
        c) <option c>
    2. <statement>
        ...
    100. <statement>
        a) ...
        b) ...
        c) ...

    Hoja de respuestas
    PREGUNTA RESPUESTA PREGUNTA RESPUESTA PREGUNTA RESPUESTA PREGUNTA RESPUESTA
    1   A  26  C  51    B  76   C
    2   B  27  A  52    A  77   A
    ...

The Escala Básica syllabus is a strict subset of Escala Ejecutiva (45 vs 81
temas), so these questions are reusable for the Inspector study app.
Tema mapping is left as null because MAD does not publish it; can be filled
in later by hand or by classifier.

Output: examenes/estructurado/escala-basica/promocion{N}.json
"""

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SRC_DIR = ROOT / "texto" / "escala-basica"
OUT_DIR = ROOT / "estructurado" / "escala-basica"

QUESTION_START = re.compile(r"^\s*(\d{1,3})\.\s+(\S.*)$")
OPTION_LINE = re.compile(r"^\s*([abc])\)\s*(.*)$")
ANSWER_KEY_HEADER = re.compile(r"Hoja\s+de\s+respuestas", re.IGNORECASE)
# A single row from the answer-key table contains 1..4 pairs of "N  L"
ANSWER_PAIR = re.compile(r"(\d{1,3})\s+([ABC])\b")


def parse_questions(lines: list[str], end_idx: int) -> list[dict]:
    """Parse question blocks from start of file up to end_idx (exclusive)."""
    questions: list[dict] = []
    current: dict | None = None
    current_field: str | None = None  # "enunciado" or "a"/"b"/"c"

    def flush():
        nonlocal current
        if current is not None:
            # collapse multi-line fields
            current["enunciado"] = re.sub(r"\s+", " ", current["enunciado"]).strip()
            for k in ("a", "b", "c"):
                current[k] = re.sub(r"\s+", " ", current[k]).strip()
            questions.append(current)
            current = None

    for ln in lines[:end_idx]:
        m_q = QUESTION_START.match(ln)
        m_o = OPTION_LINE.match(ln)

        if m_q and not m_o:
            # new question
            flush()
            current = {"n": int(m_q.group(1)), "enunciado": m_q.group(2),
                       "a": "", "b": "", "c": ""}
            current_field = "enunciado"
            continue

        if current is None:
            continue

        if m_o:
            letter = m_o.group(1)
            current[letter] = m_o.group(2)
            current_field = letter
            continue

        # continuation of current field
        text = ln.strip()
        if text:
            current[current_field] = (current[current_field] + " " + text).strip()

    flush()
    return questions


def parse_answer_key(lines: list[str], start_idx: int) -> dict[int, str]:
    answers: dict[int, str] = {}
    for ln in lines[start_idx:]:
        # skip the header line itself
        if "PREGUNTA" in ln.upper() and "RESPUESTA" in ln.upper():
            continue
        for m in ANSWER_PAIR.finditer(ln):
            n, letter = int(m.group(1)), m.group(2)
            if 1 <= n <= 100:
                answers[n] = letter
    return answers


def parse_file(promo: int, src: Path) -> dict:
    lines = src.read_text(encoding="utf-8", errors="replace").splitlines()

    # Locate the "Hoja de respuestas" header. The phrase also appears in the
    # instructions block at the top of the PDF, so take the LAST occurrence —
    # which is the real answer-key section.
    key_idx = None
    for i, ln in enumerate(lines):
        if ANSWER_KEY_HEADER.search(ln):
            key_idx = i
    if key_idx is None:
        raise ValueError(f"promo {promo}: no 'Hoja de respuestas' header found")

    questions = parse_questions(lines, key_idx)
    answers = parse_answer_key(lines, key_idx)

    parsed: list[dict] = []
    for q in questions:
        n = q["n"]
        letter = answers.get(n)
        if letter is None:
            correcta = None
        else:
            correcta = "ABC".index(letter)
        parsed.append({
            "n": n,
            "enunciado": q["enunciado"],
            "opciones": [q["a"], q["b"], q["c"]],
            "correcta": correcta,
            "dificultad": None,
            "tema": None,
            "explicacion": "",
        })

    return {
        "promocion": promo,
        "escala": "basica",
        "categoria": "Policía Nacional Escala Básica",
        "fecha": None,
        "modelo": "A",
        "fuente": f"MAD — Examen oficial Promoción {promo} (mad.es)",
        "total_preguntas": len(parsed),
        "preguntas": parsed,
    }


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    promos = [37, 38, 39, 40, 41, 42]
    rc = 0
    summary = []
    for p in promos:
        src = SRC_DIR / f"EXAMEN-PROMOCION{p}.txt"
        if not src.exists():
            print(f"  P{p}: missing source {src}", file=sys.stderr)
            rc = 1
            continue
        try:
            payload = parse_file(p, src)
        except Exception as e:
            print(f"  P{p}: ERROR {e}", file=sys.stderr)
            rc = 1
            continue
        out = OUT_DIR / f"promocion{p}.json"
        out.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        miss_q = 100 - payload["total_preguntas"]
        miss_a = sum(1 for q in payload["preguntas"] if q["correcta"] is None)
        summary.append((p, payload["total_preguntas"], miss_a, out))

    print("Promo | Qs parsed | Qs without answer | File")
    for p, n, ma, out in summary:
        print(f"  {p:3d}  |   {n:3d}     |        {ma:3d}        | {out.name}")
    return rc


if __name__ == "__main__":
    sys.exit(main())
