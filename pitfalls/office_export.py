"""LibreOffice-Export eines typischen Office-Dokuments (Betriebsvereinbarung).

Quelle: quellen/office.fodt (Flat-ODT), konvertiert mit `soffice --convert-to pdf`.
Enthält Office-typische Konstrukte: Kopf-/Fußzeile mit Seitenfeldern, automatische
Kapitelnummern, Initiale, Fußnoten, Änderungsverfolgung (Löschung "zwei", Einfügung
"drei"), einen Kommentar, verborgenen Text, einen schwebenden Textrahmen, eine
automatisch nummerierte Liste und ein nicht fixiertes Datumsfeld.
Die Originalseite wird unverändert eingesetzt.
Siehe STOLPERSTEINE.md#office_export.
"""

from datetime import datetime

import pikepdf
from reportlab.pdfgen.canvas import Canvas

from pitfalls._lib import ExternalPage

TITLE = "Office-Export (LibreOffice)"

PAGE = ExternalPage("office-libreoffice.pdf")
AVAILABLE = PAGE.exists
MISSING = "quellen/out/office-libreoffice.pdf fehlt, erst quellen/build.sh ausführen"


def draw(c: Canvas, ctx) -> None:
    ctx.title()  # Platzhalter, wird durch die Originalseite ersetzt


def postprocess(pdf: pikepdf.Pdf, pages: list[pikepdf.Page]) -> None:
    PAGE.install(pdf, pages[0])


def _export_date() -> str:
    # Das Datumsfeld ist nicht fixiert: LibreOffice setzt beim Export das aktuelle Datum ein.
    with pikepdf.open(PAGE.path) as src:
        raw = str(src.docinfo["/CreationDate"])  # z. B. D:20261002162800+02'00'
    return datetime.strptime(raw[2:10], "%Y%m%d").strftime("%d.%m.%y")


def GROUND_TRUTH(ctx) -> str:
    return f"""\
# Betriebsvereinbarung Mobiles Arbeiten

## 1 Geltungsbereich

Diese Vereinbarung gilt für alle Beschäftigten der Musterfirma GmbH an den Standorten Köln und Bonn. Ausgenommen sind Auszubildende im ersten Ausbildungsjahr¹ sowie Beschäftigte in der Produktion.

## 2 Umfang

Beschäftigte können bis zu drei Tage pro Woche mobil arbeiten. Die Abstimmung erfolgt im Team und ist im Kalender einzutragen. An mindestens einem festen Präsenztag pro Woche ist das gesamte Team vor Ort, damit Besprechungen und Einarbeitungen persönlich stattfinden können.

> Wichtig: Die Vereinbarung tritt am 1. März 2026 in Kraft.

## 3 Voraussetzungen

Mobiles Arbeiten setzt voraus, dass

a) die Tätigkeit dafür geeignet ist,
b) ein dienstliches Notebook mit VPN-Zugang vorhanden ist und
c) die Vorgaben zum Datenschutz² eingehalten werden.

Köln, den {_export_date()}

¹ Für Auszubildende gilt die gesonderte Regelung in Anlage 2.
² Siehe Datenschutzrichtlinie, Abschnitt 4.
"""
