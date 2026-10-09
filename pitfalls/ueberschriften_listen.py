"""Überschriften und Listen existieren nur optisch.

Überschriften sind lediglich größerer/fetter Text, die Hierarchie muss aus
Schriftgrößen erraten werden. Ein fetter Absatzanfang sieht für Heuristiken aus
wie eine Überschrift. Aufzählungszeichen kommen aus ZapfDingbats und werden je
nach Extraktor als "l", "n" oder gar nicht ausgegeben.
Siehe STOLPERSTEINE.md#ueberschriften_listen.
"""

from reportlab.pdfgen.canvas import Canvas

from pitfalls._lib import LEFT, para

TITLE = "Überschriften und Listen"


def draw(c: Canvas, ctx) -> None:
    y = ctx.title()
    c.setFont("Helvetica-Bold", 14)
    c.drawString(LEFT, y, "3 Sicherheitsrichtlinie")
    y -= 24
    c.setFont("Helvetica-Bold", 12)
    c.drawString(LEFT, y, "3.1 Zugang zum Gebäude")
    y -= 20
    y = para(c, LEFT, y, "Der Zugang ist nur mit gültigem Ausweis gestattet. Besucher melden sich am Empfang.")
    c.setFont("Helvetica-Bold", 12)
    c.drawString(LEFT, y, "3.2 Passwörter")
    y -= 20
    c.setFont("Helvetica-Bold", 11)
    c.drawString(LEFT, y, "Wichtig:")
    c.setFont("Helvetica", 11)
    c.drawString(LEFT + 48, y, "Passwörter müssen folgende Regeln erfüllen.")
    y -= 20
    for bullet, text in [
        ("l", "mindestens 12 Zeichen lang"),
        ("l", "Groß- und Kleinbuchstaben sowie Ziffern"),
        ("n", "keine Wiederverwendung der letzten fünf Passwörter"),
    ]:
        c.setFont("ZapfDingbats", 7)
        c.drawString(LEFT + 10, y + 1, bullet)
        c.setFont("Helvetica", 11)
        c.drawString(LEFT + 24, y, text)
        y -= 16
    y -= 10
    c.setFont("Helvetica-Bold", 14)
    c.drawString(LEFT, y, "4 Datenschutz")
    y -= 24
    c.setFont("Helvetica", 11)
    c.drawString(LEFT, y, "1.")
    c.drawString(LEFT + 18, y, "Personenbezogene Daten werden verschlüsselt gespeichert und nach zwei")
    y -= 15
    c.drawString(LEFT + 18, y, "Jahren gelöscht.")
    y -= 18
    c.drawString(LEFT, y, "2.")
    c.drawString(LEFT + 18, y, "Auskunftsersuchen werden innerhalb eines Monats beantwortet.")


GROUND_TRUTH = """\
### 3 Sicherheitsrichtlinie

#### 3.1 Zugang zum Gebäude

Der Zugang ist nur mit gültigem Ausweis gestattet. Besucher melden sich am Empfang.

#### 3.2 Passwörter

**Wichtig:** Passwörter müssen folgende Regeln erfüllen.

- mindestens 12 Zeichen lang
- Groß- und Kleinbuchstaben sowie Ziffern
- keine Wiederverwendung der letzten fünf Passwörter

### 4 Datenschutz

1. Personenbezogene Daten werden verschlüsselt gespeichert und nach zwei Jahren gelöscht.
2. Auskunftsersuchen werden innerhalb eines Monats beantwortet.
"""
