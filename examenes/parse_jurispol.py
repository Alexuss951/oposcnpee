"""
Parse Jurispol "informe examen" PDF text into structured JSON.

Input  : examenes/texto/escala-ejecutiva/EE-P40-informe-jurispol.txt
Output : examenes/estructurado/escala-ejecutiva/promocion40.json

Source format (per question block):
    PREGUNTA N <DIFFICULTY>
    <statement, multiple lines>
    [4]a) <option a>
    [4]b) <option b>
    [4]c) <option c>
    TEMA M
    Explicación:
    <explanation, multiple lines>

The "4" prefix on a single option line is the visual checkmark that pdftotext
rendered as a digit. It marks the correct answer.
"""

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "texto" / "escala-ejecutiva" / "EE-P40-informe-jurispol.txt"
OUT_DIR = ROOT / "estructurado" / "escala-ejecutiva"
OUT = OUT_DIR / "promocion40.json"

# page header/footer noise to strip
NOISE_PATTERNS = [
    re.compile(r"^\s*Todos los derechos reservados.*$", re.IGNORECASE),
    re.compile(r"^\s*jurispol\.com\s*$", re.IGNORECASE),
    re.compile(r"^\s*Informe Examen Oficial.*$", re.IGNORECASE),
    re.compile(r"^\s*Promoci[óo]n\s*40.*Inspector.*$", re.IGNORECASE),
    re.compile(r"^\s*DICIEMBRE\s*2025\s*$", re.IGNORECASE),
    re.compile(r"^\s*info@jurispol\.com\s*$", re.IGNORECASE),
]

QUESTION_HEADER = re.compile(r"^\s*PREGUNTA\s+(\d{1,3})\s+(F[ÁA]CIL|MEDIA|DIF[ÍI]CIL)\s*$",
                             re.IGNORECASE)
# Option lines may start with the digit "4" (rendering artifact of the green
# check mark) marking the correct answer, optionally preceded/followed by
# whitespace.
OPTION_LINE = re.compile(r"^\s*(4?)\s*([abc])\)\s*(.*)$")
TEMA_LINE = re.compile(r"^\s*TEMA\s+(\d{1,2})\s*$", re.IGNORECASE)
EXPLAIN_HEADER = re.compile(r"^\s*Explicaci[óo]n\s*:\s*$", re.IGNORECASE)

# Stray control / spacing chars left by pdftotext for the red cross icon on
# incorrect answers; drop them before regex matching.
STRIP_CHARS = str.maketrans("", "", "\x84\x85\x86\u2009\u202f\xa0")


def clean_lines(raw: str) -> list[str]:
    out = []
    for ln in raw.splitlines():
        if any(p.search(ln) for p in NOISE_PATTERNS):
            continue
        out.append(ln.translate(STRIP_CHARS).rstrip())
    return out


def normalize_difficulty(d: str) -> str:
    d = d.upper().replace("Á", "A").replace("Í", "I")
    return {"FACIL": "facil", "MEDIA": "media", "DIFICIL": "dificil"}.get(d, d.lower())


def split_questions(lines: list[str]) -> list[tuple[int, str, list[str]]]:
    """Return list of (number, difficulty, body_lines) per question."""
    questions = []
    current = None
    body: list[str] = []
    for ln in lines:
        m = QUESTION_HEADER.match(ln)
        if m:
            if current:
                questions.append((current[0], current[1], body))
            current = (int(m.group(1)), normalize_difficulty(m.group(2)))
            body = []
        elif current:
            body.append(ln)
    if current:
        questions.append((current[0], current[1], body))
    return questions


def parse_question(num: int, dif: str, body: list[str]) -> dict:
    # find first option line index
    opt_idx = [i for i, ln in enumerate(body) if OPTION_LINE.match(ln)]
    if len(opt_idx) < 3:
        raise ValueError(f"Q{num}: expected 3 options, found {len(opt_idx)}")

    # statement = everything before the first option, joined
    statement_lines = [ln for ln in body[: opt_idx[0]] if ln.strip()]
    enunciado = " ".join(s.strip() for s in statement_lines)

    # collect the 3 options; each option text spans from its line until the
    # next option line, the TEMA line, the Explicación line, or end of body
    stop_set = set(opt_idx[1:])
    options = {"a": "", "b": "", "c": ""}
    correct_idx: int | None = None
    for k, start in enumerate(opt_idx[:3]):
        end = opt_idx[k + 1] if k + 1 < len(opt_idx) else len(body)
        # trim end on TEMA / Explicación markers
        for j in range(start + 1, end):
            if TEMA_LINE.match(body[j]) or EXPLAIN_HEADER.match(body[j]):
                end = j
                break
        m = OPTION_LINE.match(body[start])
        letter = m.group(2).lower()
        if m.group(1) == "4":
            correct_idx = "abc".index(letter)
        text_lines = [m.group(3).strip()] + [body[j].strip() for j in range(start + 1, end)]
        options[letter] = " ".join(t for t in text_lines if t)

    if correct_idx is None:
        raise ValueError(f"Q{num}: no correct-answer marker found")

    # tema number
    tema = None
    for ln in body:
        m = TEMA_LINE.match(ln)
        if m:
            tema = int(m.group(1))
            break

    # explanation = lines after Explicación: until end of body
    explanation = ""
    for i, ln in enumerate(body):
        if EXPLAIN_HEADER.match(ln):
            expl_lines = [body[j].strip() for j in range(i + 1, len(body)) if body[j].strip()]
            explanation = " ".join(expl_lines)
            break

    return {
        "n": num,
        "enunciado": enunciado,
        "opciones": [options["a"], options["b"], options["c"]],
        "correcta": correct_idx,
        "dificultad": dif,
        "tema": tema,
        "explicacion": explanation,
    }


def main() -> int:
    if not SRC.exists():
        print(f"missing: {SRC}", file=sys.stderr)
        return 1
    raw = SRC.read_text(encoding="utf-8", errors="replace")
    lines = clean_lines(raw)
    qs_raw = split_questions(lines)
    if len(qs_raw) != 100:
        print(f"warning: parsed {len(qs_raw)} question blocks (expected 100)", file=sys.stderr)

    parsed = []
    errors = []
    for num, dif, body in qs_raw:
        try:
            parsed.append(parse_question(num, dif, body))
        except Exception as e:
            errors.append(f"  Q{num}: {e}")

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    payload = {
        "promocion": 40,
        "escala": "ejecutiva",
        "categoria": "Inspector turno libre",
        "fecha": "2025-12-13",
        "modelo": "B",
        "fuente": "Jurispol — Informe Examen Oficial Modelo B (jurispol.com)",
        "total_preguntas": len(parsed),
        "preguntas": parsed,
    }
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"parsed: {len(parsed)} / {len(qs_raw)} questions → {OUT}")
    if errors:
        print(f"errors ({len(errors)}):")
        for e in errors:
            print(e)
        return 2
    # quick stats
    by_tema: dict[int | None, int] = {}
    by_dif: dict[str, int] = {}
    by_letter = {0: 0, 1: 0, 2: 0}
    for q in parsed:
        by_tema[q["tema"]] = by_tema.get(q["tema"], 0) + 1
        by_dif[q["dificultad"]] = by_dif.get(q["dificultad"], 0) + 1
        by_letter[q["correcta"]] += 1
    print(f"  difficulty: {by_dif}")
    print(f"  correct letter (a,b,c): {by_letter}")
    print(f"  temas covered: {sum(1 for k in by_tema if k is not None)} distinct; "
          f"missing tema: {by_tema.get(None, 0)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
