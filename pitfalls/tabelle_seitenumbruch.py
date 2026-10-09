"""Tabelle über zwei Seiten.

Wie in Office-Dokumenten üblich: Kopfzeile auf der zweiten Seite wiederholt,
"Übertrag"-Zeilen, Beschriftung "(Fortsetzung)" und eine Zeile, deren mehrzeilige
Zelle über die Seitengrenze umbricht. Dazwischen liegen Fußzeile und Kopfzeile.
Extraktoren und Chunker sehen zwei Tabellen, die zweite ohne Bezug zur ersten,
und die gesplittete Zeile zerfällt in zwei halbe Datensätze.
Siehe STOLPERSTEINE.md#tabelle_seitenumbruch.
"""

from reportlab.pdfgen.canvas import Canvas

from pitfalls._lib import LEFT, RIGHT, para

TITLE = "Tabelle über zwei Seiten"

INTRO = "Tabelle 3 listet alle Geräte im Inventar der Niederlassung Köln."
HEADER = ("Nr.", "Gerät", "Standort", "Anschaffung", "Wert (€)")
COLS = [LEFT, LEFT + 35, LEFT + 215, LEFT + 300, LEFT + 380, RIGHT]

_DEVICES = ["Notebook", "Monitor 27 Zoll", "Dockingstation", "Drucker", "Beamer", "Telefon", "Tablet", "Server"]
_ROOMS = ["Raum 1.01", "Raum 1.02", "Raum 2.14", "Empfang", "Serverraum"]
_VALUES = [1290, 349, 189, 640, 899, 129, 579, 4800]

# Deterministische Zeilen; Zeile SPLIT hat eine zweizeilige Zelle, die über die Seitengrenze bricht.
ROWS_PAGE1 = 36
SPLIT = ROWS_PAGE1 + 1
N_ROWS = 48
SPLIT_TEXT = ("Konferenzsystem mit Kamera,", "Mikrofonen und Display")


def _rows() -> list[tuple[str, str, str, str, int]]:
    rows = []
    for i in range(1, N_ROWS + 1):
        k = (i * 7) % len(_DEVICES)
        name = " ".join(SPLIT_TEXT) if i == SPLIT else _DEVICES[k]
        value = 7450 if i == SPLIT else _VALUES[k]
        rows.append((str(i), name, _ROOMS[i % len(_ROOMS)], f"{2019 + i % 6}-{1 + i % 12:02d}", value))
    return rows


def _eur(v: int) -> str:
    return f"{v:,}".replace(",", ".") + ",00"


def _row(c: Canvas, y: float, cells, bold: bool = False) -> None:
    c.setFont("Helvetica-Bold" if bold else "Helvetica", 9)
    for i, text in enumerate(cells):
        if i == len(cells) - 1:
            c.drawRightString(COLS[i + 1] - 4, y, text)
        else:
            c.drawString(COLS[i] + 4, y, text)


def _grid(c: Canvas, top: float, bottom: float, header_bottom: float) -> None:
    c.setLineWidth(0.5)
    c.rect(COLS[0], bottom, COLS[-1] - COLS[0], top - bottom)
    for x in COLS[1:-1]:
        c.line(x, bottom, x, top)
    c.line(COLS[0], header_bottom, COLS[-1], header_bottom)


RH = 15


def draw(c: Canvas, ctx) -> None:
    rows = _rows()
    y = ctx.title()
    y = para(c, LEFT, y, INTRO)
    c.setFont("Helvetica-Bold", 10)
    c.drawString(LEFT, y, "Tabelle 3: Inventarliste")
    y -= 10

    top = y
    _row(c, top - 11, HEADER, bold=True)
    y = top - RH
    header_bottom = y
    running = 0
    for r in rows[:ROWS_PAGE1]:
        _row(c, y - 11, (*r[:4], _eur(r[4])))
        running += r[4]
        y -= RH
    # gesplittete Zeile: erste Zeile der Zelle auf Seite 1
    s = rows[SPLIT - 1]
    _row(c, y - 11, (s[0], SPLIT_TEXT[0], s[2], s[3], _eur(s[4])))
    running += s[4]
    y -= RH
    _row(c, y - 11, ("", "Übertrag", "", "", _eur(running)), bold=True)
    y -= RH
    _grid(c, top, y, header_bottom)

    ctx.new_page()
    y = ctx.height - 100
    c.setFont("Helvetica-Bold", 10)
    c.drawString(LEFT, y, "Tabelle 3: Inventarliste (Fortsetzung)")
    y -= 10
    top = y
    _row(c, top - 11, HEADER, bold=True)
    y = top - RH
    header_bottom = y
    _row(c, y - 11, ("", "Übertrag", "", "", _eur(running)), bold=True)
    y -= RH
    # Fortsetzung der gesplitteten Zelle, übrige Zellen leer
    _row(c, y - 11, ("", SPLIT_TEXT[1], "", "", ""))
    y -= RH
    for r in rows[SPLIT:]:
        _row(c, y - 11, (*r[:4], _eur(r[4])))
        running += r[4]
        y -= RH
    _row(c, y - 11, ("", "Summe", "", "", _eur(running)), bold=True)
    y -= RH
    _grid(c, top, y, header_bottom)


def _gt() -> str:
    rows = _rows()
    lines = [INTRO, "", "Tabelle 3: Inventarliste", "", "| " + " | ".join(HEADER) + " |", "|---|---|---|---|---|"]
    lines += [f"| {r[0]} | {r[1]} | {r[2]} | {r[3]} | {_eur(r[4])} |" for r in rows]
    lines.append(f"| | Summe | | | {_eur(sum(r[4] for r in rows))} |")
    return "\n".join(lines)


GROUND_TRUTH = _gt()
