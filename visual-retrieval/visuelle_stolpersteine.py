"""Baut die Testseiten für die Gegenprobe: Seiten, deren Textlayer in Ordnung ist und
die für ein visuelles Modell schwer zu lesen sind.

    uv run visuelle_stolpersteine.py

Erzeugt in data/visuelle_stolpersteine/:
- fussnoten.pdf   3 Seiten × 3 Schriftgrößen (8, 6 und 4,5 pt), der gesuchte Inhalt steht
                  nur in der Fußnote und hat mit dem Fließtext nichts zu tun
- rechnungen.pdf  4 Rechnungen aus derselben Vorlage, die Nummern unterscheiden sich
                  nur durch vertauschte Ziffern
- kontrast.pdf    je ein Absatz in hellem Grau und in fast weißem Grau
- gedreht.pdf     Querformat-Inhalt auf einer Hochformat-Seite (um 90° gedreht)
- nup1.pdf        8 Seiten des Mutterschutzgesetzes (quelle/MuSchG.pdf, Seiten 4 bis 11)
- nup2.pdf        dieselben Seiten, zwei pro Blatt
- nup4.pdf        dieselben Seiten, vier pro Blatt
- seiten/         Seitenbilder (150 dpi), text/ pypdf- und Tesseract-Text pro Seite

Die Quelle für nup*.pdf muss vorher geladen werden:
    https://www.gesetze-im-internet.de/muschg_2018/MuSchG.pdf -> data/visuelle_stolpersteine/quelle/
"""

import json
import subprocess
import tempfile
from pathlib import Path

import pymupdf
from pypdf import PdfReader

HERE = Path(__file__).resolve().parent
OUT = HERE / "data" / "visuelle_stolpersteine"
FONTS = {
    "sans": "/usr/share/fonts/liberation/LiberationSans-Regular.ttf",
    "bold": "/usr/share/fonts/liberation/LiberationSans-Bold.ttf",
    "serif": "/usr/share/fonts/liberation/LiberationSerif-Regular.ttf",
}
W, H = 595.28, 841.89
LEFT, RIGHT = 72, W - 72
GRAU = (0.35, 0.35, 0.35)
GROESSEN = [8, 6, 4.5]

FUSSNOTEN = [
    (
        "Betriebsrestaurant",
        [
            "Das Betriebsrestaurant im Erdgeschoss ist montags bis freitags von 11:30 bis 14:00 Uhr "
            "geöffnet. Bezahlt wird bargeldlos mit dem Mitarbeiterausweis, der an den Automaten im "
            "Foyer aufgeladen werden kann.*",
            "Der Speiseplan für die laufende Woche hängt am Eingang aus und steht im Intranet. "
            "Täglich gibt es ein vegetarisches Gericht und eine Salattheke. Gäste können in "
            "Begleitung von Mitarbeitenden essen und zahlen den Gästepreis.",
            "Das Geschirr gehört auf den Rückgabewagen. Wer zuletzt am Tisch sitzt, wischt ihn "
            "bitte kurz ab.",
        ],
        "* Die Tiefgarage in der Lindenstraße wird an jedem ersten Dienstag im Monat zwischen 6 und "
        "9 Uhr gereinigt und ist in dieser Zeit gesperrt. Ersatzschlüssel für die Fahrradbox gibt "
        "Herr Okonkwo am Empfang gegen 25 Euro Pfand aus.",
    ),
    (
        "Drucken und Scannen",
        [
            "Auf jeder Etage steht ein Multifunktionsgerät, an dem man sich mit dem "
            "Mitarbeiterausweis anmeldet. Druckaufträge gehen an die zentrale Warteschlange und "
            "können an jedem Gerät abgeholt werden.*",
            "Nicht abgeholte Aufträge werden nach 24 Stunden gelöscht. Scans landen als PDF im "
            "persönlichen Netzlaufwerk. Farbdrucke sind möglich, kosten aber das Vierfache.",
            "Leere Tonerkartuschen tauscht der IT-Service aus, eine kurze Nachricht über das "
            "Ticketsystem genügt.",
        ],
        "* Der Defibrillator hängt im zweiten Stock neben dem Kopierraum und wird jedes Jahr im "
        "März geprüft. Ersthelferin für das Gebäude ist Frau Brandstetter, erreichbar unter der "
        "Durchwahl 2718.",
    ),
    (
        "Besucherinnen und Besucher",
        [
            "Gäste melden sich am Empfang an und erhalten einen Besucherausweis, der sichtbar zu "
            "tragen ist. Die einladende Person holt ihren Besuch am Empfang ab und begleitet ihn im "
            "Gebäude.*",
            "Besprechungsräume werden über den Kalender gebucht. WLAN-Zugänge für Gäste stellt "
            "der Empfang für jeweils einen Tag aus.",
            "Am Ende des Besuchs wird der Ausweis wieder abgegeben.",
        ],
        "* Das Lastenrad der Firma kann über das Intranet für höchstens drei Tage am Stück "
        "ausgeliehen werden. Private Pakete nimmt die Poststelle nur bis zu einem Gewicht von 5 "
        "Kilogramm an.",
    ),
]

RECHNUNGEN = [
    ("RE-2026-08817", "Bäckerei Feldkamp", "Am Sparrenberg 4, 33602 Bielefeld",
     [("Wartung Kassensystem", "1", "289,00"), ("Bonrollen 80 mm", "50", "57,50"), ("Anfahrt", "1", "65,80")], "412,30"),
    ("RE-2026-08871", "Tischlerei Aumüller", "Innstraße 21, 94032 Passau",
     [("Lizenz Zeiterfassung, 12 Monate", "1", "1.440,00"), ("Einrichtung vor Ort", "4", "480,00"), ("Anfahrt", "1", "44,00")], "1.964,00"),
    ("RE-2026-08187", "Praxis Dr. Sandhoff", "Breite Straße 9, 23552 Lübeck",
     [("Etikettendrucker", "1", "379,00"), ("Etiketten 57 × 32 mm", "20", "118,00"), ("Versand", "1", "41,75")], "538,75"),
    ("RE-2026-08718", "Fahrradladen Kettenreaktion", "Wiehre 12, 79100 Freiburg",
     [("Barcodescanner", "2", "318,00"), ("Schulung Warenwirtschaft", "6", "720,00"), ("Anfahrt", "1", "89,40")], "1.127,40"),
]

KONTRAST = [
    (
        "Sommerfest am 12. Juli",
        [
            "Das Sommerfest findet in diesem Jahr im Innenhof statt und beginnt um 16 Uhr. Für "
            "Essen und Getränke ist gesorgt, Familien sind herzlich eingeladen.",
            "Wer kommt, trägt sich bitte bis zum 30. Juni in die Liste im Intranet ein, damit "
            "die Küche planen kann.",
        ],
        "Der Betriebsarzt Dr. Wieland hält seine Sprechstunde an jedem zweiten Mittwoch von 13 bis "
        "15 Uhr in Raum 0.14 ab. Eine Anmeldung ist nicht nötig.",
        0.78,
    ),
    (
        "Neue Öffnungszeiten der Poststelle",
        [
            "Die Poststelle ist ab August montags bis donnerstags von 8 bis 15 Uhr und freitags "
            "von 8 bis 12 Uhr besetzt. Ausgehende Sendungen müssen bis 14 Uhr abgegeben sein.",
            "Einschreiben und Kuriersendungen bitte am Vortag anmelden.",
        ],
        "Der Tresorcode für den Serverraum wird vierteljährlich geändert und liegt in einem "
        "versiegelten Umschlag bei der Geschäftsführung.",
        0.95,
    ),
]

SCHICHTPLAN = [
    ("Tag", "Frühschicht", "Spätschicht", "Nachtschicht"),
    ("Montag", "Brinkmann", "Yıldız", "Petersen"),
    ("Dienstag", "Brinkmann", "Kowalczyk", "Petersen"),
    ("Mittwoch", "Hartung", "Kowalczyk", "Nowak"),
    ("Donnerstag", "Hartung", "Yıldız", "Seidel"),
    ("Freitag", "Brinkmann", "Hartung", "Nowak"),
]


def neue_seite(doc, kopf="Musterfirma GmbH · Mitarbeiterhandbuch"):
    p = doc.new_page(width=W, height=H)
    for name, f in FONTS.items():
        p.insert_font(fontname=name, fontfile=f)
    if kopf:
        p.insert_text((LEFT, 48), kopf, fontname="sans", fontsize=8, color=GRAU)
        p.draw_line((LEFT, 54), (RIGHT, 54), color=GRAU, width=0.5)
    return p


def absatz(p, y, text, size=11, font="serif", color=(0, 0, 0), unten=H - 60):
    rect = pymupdf.Rect(LEFT, y, RIGHT, unten)
    rest = p.insert_textbox(rect, text, fontname=font, fontsize=size, color=color, lineheight=1.35)
    assert rest >= 0, f"Text passt nicht: {text[:40]}"
    return y + rect.height - rest + size * 0.8


def fussnoten():
    doc = pymupdf.open()
    for titel, body, note in FUSSNOTEN:
        for size in GROESSEN:
            p = neue_seite(doc)
            p.insert_text((LEFT, 100), titel, fontname="bold", fontsize=16)
            y = 125
            for a in body:
                y = absatz(p, y, a)
            p.draw_line((LEFT, 730), (LEFT + 140, 730), color=GRAU, width=0.5)
            absatz(p, 736, note, size=size)
    doc.save(OUT / "fussnoten.pdf")


def rechnungen():
    doc = pymupdf.open()
    for nr, kunde, adresse, posten, summe in RECHNUNGEN:
        p = neue_seite(doc, kopf=None)
        p.insert_text((LEFT, 70), "Musterfirma GmbH · Hafenstraße 12 · 48153 Münster", fontname="sans", fontsize=8, color=GRAU)
        p.insert_text((LEFT, 120), kunde, fontname="sans", fontsize=11)
        strasse, ort = adresse.split(", ")
        p.insert_text((LEFT, 135), strasse, fontname="sans", fontsize=11)
        p.insert_text((LEFT, 150), ort, fontname="sans", fontsize=11)
        p.insert_text((LEFT, 230), f"Rechnung Nr. {nr}", fontname="bold", fontsize=14)
        p.insert_text((RIGHT - 110, 230), "Datum: 3. Juni 2026", fontname="sans", fontsize=10)
        spalten = [LEFT, LEFT + 40, LEFT + 300, LEFT + 370]
        y = 275
        for j, kopf in enumerate(["Pos.", "Bezeichnung", "Menge", "Betrag in Euro"]):
            p.insert_text((spalten[j], y), kopf, fontname="bold", fontsize=10)
        p.draw_line((LEFT, y + 6), (RIGHT, y + 6), width=0.5)
        for i, (bez, menge, betrag) in enumerate(posten):
            y += 22
            for j, zelle in enumerate([str(i + 1), bez, menge, betrag]):
                p.insert_text((spalten[j], y), zelle, fontname="sans", fontsize=10)
        p.draw_line((LEFT, y + 8), (RIGHT, y + 8), width=0.5)
        p.insert_text((spalten[2] - 60, y + 28), "Rechnungsbetrag", fontname="bold", fontsize=10)
        p.insert_text((spalten[3], y + 28), summe, fontname="bold", fontsize=10)
        absatz(p, y + 70, "Der Betrag ist innerhalb von 14 Tagen ohne Abzug zu überweisen. Bitte geben Sie bei "
               "der Zahlung die Rechnungsnummer an.", size=10, font="sans")
        p.insert_text((LEFT, H - 50), "Musterbank · IBAN DE00 0000 0000 0000 0000 00 · Geschäftsführung: Erika Mustermann",
                      fontname="sans", fontsize=8, color=GRAU)
    doc.save(OUT / "rechnungen.pdf")


def kontrast():
    doc = pymupdf.open()
    for titel, body, blass, grau in KONTRAST:
        p = neue_seite(doc, kopf="Musterfirma GmbH · Aushang")
        p.insert_text((LEFT, 100), titel, fontname="bold", fontsize=16)
        y = 125
        for a in body:
            y = absatz(p, y, a)
        absatz(p, y + 20, blass, color=(grau, grau, grau))
    doc.save(OUT / "kontrast.pdf")


def gedreht():
    doc = pymupdf.open()
    p = neue_seite(doc, kopf=None)

    def zeile(x, y, text, font="sans", size=11):
        p.insert_text((x, y), text, fontname=font, fontsize=size, rotate=90)

    unten = H - 80
    zeile(110, unten, "Schichtplan Lager, Kalenderwoche 23", font="bold", size=16)
    spalten = [0, 110, 260, 410]
    for i, reihe in enumerate(SCHICHTPLAN):
        for j, zelle in enumerate(reihe):
            zeile(160 + i * 26, unten - spalten[j], zelle, font="bold" if i == 0 else "sans")
    zeile(360, unten, "Die Übergabe zwischen Früh- und Spätschicht findet um 13:45 Uhr an Rampe 3 statt.")
    zeile(386, unten, "Urlaubsanträge für Juli nimmt Frau Hartung bis zum 6. Juni entgegen.")
    doc.save(OUT / "gedreht.pdf")


def nup():
    src = pymupdf.open(OUT / "quelle" / "MuSchG.pdf")
    seiten = list(range(3, 11))
    d1 = pymupdf.open()
    d1.insert_pdf(src, from_page=seiten[0], to_page=seiten[-1])
    d1.save(OUT / "nup1.pdf")
    d2 = pymupdf.open()
    for i in range(0, 8, 2):
        p = d2.new_page(width=H, height=W)
        p.show_pdf_page(pymupdf.Rect(0, 0, H / 2, W), src, seiten[i])
        p.show_pdf_page(pymupdf.Rect(H / 2, 0, H, W), src, seiten[i + 1])
    d2.save(OUT / "nup2.pdf")
    d4 = pymupdf.open()
    for i in (0, 4):
        p = d4.new_page(width=W, height=H)
        for k in range(4):
            x, y = (k % 2) * W / 2, (k // 2) * H / 2
            p.show_pdf_page(pymupdf.Rect(x, y, x + W / 2, y + H / 2), src, seiten[i + k])
    d4.save(OUT / "nup4.pdf")


def tesseract(pdf: Path) -> list[str]:
    import pytesseract
    from PIL import Image

    with tempfile.TemporaryDirectory() as tmp:
        subprocess.run(["pdftoppm", "-r", "300", "-png", str(pdf), f"{tmp}/s"], check=True)
        return [pytesseract.image_to_string(Image.open(p), lang="deu") for p in sorted(Path(tmp).glob("s-*.png"))]


def seiten_und_text():
    (OUT / "seiten").mkdir(exist_ok=True)
    (OUT / "text").mkdir(exist_ok=True)
    texte = {"pypdf": {}, "tesseract": {}}
    for pdf in sorted(OUT.glob("*.pdf")):
        with pymupdf.open(pdf) as doc:
            ids = [f"{pdf.stem}-{i + 1:03d}" for i in range(len(doc))]
            for i, seite in zip(ids, doc):
                seite.get_pixmap(dpi=150).save(OUT / "seiten" / f"{i}.png")
        texte["pypdf"].update(zip(ids, [s.extract_text() or "" for s in PdfReader(pdf).pages], strict=True))
        texte["tesseract"].update(zip(ids, tesseract(pdf), strict=True))
        print(pdf.name, len(ids), flush=True)
    for name, corpus in texte.items():
        (OUT / "text" / f"{name}.json").write_text(json.dumps(corpus, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    fussnoten()
    rechnungen()
    kontrast()
    gedreht()
    nup()
    seiten_und_text()
