"""Gemeinsamer Teil der browser_*-Stolpersteine: Seite einsetzen und Ground Truth."""

from reportlab.pdfgen.canvas import Canvas

from pitfalls._lib import ExternalPage

# Inhalt von quellen/browser.html ohne Boilerplate (Navigation, Cookie-Banner, Skip-Link).
GROUND_TRUTH = """\
# REISERICHTLINIE 2026

Gültig ab 1. Januar 2026 · Herausgegeben von der Personalabteilung

Dienstreisen sind vor Reiseantritt im Reiseportal zu beantragen und durch die Führungskraft freizugeben. Die Auswahl des Verkehrsmittels erfolgt nach den Grundsätzen der Wirtschaftlichkeit und der Effizienz; Bahnreisen haben bei Strecken unter 500 Kilometern grundsätzlich Vorrang vor Flügen. Die offizielle Abrechnung erfolgt ausschließlich über das Reisekostenformular.

Übernachtungskosten werden bis zu einem Betrag von 120 Euro pro Nacht erstattet, in München, Frankfurt und Hamburg bis zu 150 Euro. Für Verpflegungsmehraufwendungen gelten die steuerlichen Pauschalen. Die Erstattung von Taxifahrten ist auf begründete Ausnahmefälle beschränkt.

**Hinweis:** Reisen in Länder mit Reisewarnung des Auswärtigen Amtes müssen zusätzlich von der Geschäftsführung genehmigt werden.

## Ablauf der Abrechnung

1. Belege innerhalb von vier Wochen nach Reiseende hochladen.
2. Reisekostenformular ausfüllen und digital signieren.
3. Freigabe durch die Führungskraft abwarten.

## Erstattungssätze

| Kostenart | Inland | Ausland |
|---|---|---|
| Übernachtung (pro Nacht) | 120 € | nach Land |
| Verpflegung (ganzer Tag) | 28 € | nach Land |
| Kilometerpauschale (Pkw) | 0,30 € | 0,30 € |

## Kontakt

Fragen beantwortet das Reiseteam unter reisen@musterfirma.example 👍

Hotline: 0800 555 0199
"""


def draw_external(c: Canvas, ctx, ext: ExternalPage) -> None:
    # Platzhalter, wird im postprocess durch die Originalseite ersetzt
    ctx.title()
