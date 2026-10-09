"""Variante: verschlüsseltes PDF mit Kopierschutz-Rechten.

Leeres Benutzerpasswort (öffnet ohne Abfrage), Owner-Passwort gesetzt, Rechte
"Text extrahieren" und "Barrierefreiheit" entzogen. Manche Bibliotheken
ignorieren die Rechte, andere brechen ab, manche brauchen Zusatzpakete für AES.
Ergebnis: out/stolpersteine--verschluesselt.pdf
Siehe STOLPERSTEINE.md#verschluesselt.
"""

import io

import pikepdf

TITLE = "Verschlüsselung und Kopierschutz (Variante)"


def variant(data: bytes) -> bytes:
    pdf = pikepdf.open(io.BytesIO(data))
    buf = io.BytesIO()
    pdf.save(
        buf,
        encryption=pikepdf.Encryption(
            owner="geheim",
            user="",
            R=6,
            allow=pikepdf.Permissions(extract=False, accessibility=False, modify_other=False),
        ),
    )
    return buf.getvalue()
