"""Variante: PDF mit kaputter xref-Tabelle.

Nach der Kopfzeile werden Bytes eingefügt, damit stimmen alle Offsets in der
xref-Tabelle nicht mehr. Viewer reparieren das stillschweigend, manche Parser
brechen ab, andere reparieren mit Warnung (oder liefern weniger Seiten).
Ergebnis: out/stolpersteine--kaputte_xref.pdf
Siehe STOLPERSTEINE.md#kaputte_xref.
"""

TITLE = "Kaputte xref-Tabelle (Variante)"


def variant(data: bytes) -> bytes:
    header_end = data.index(b"\n") + 1
    junk = b"%" + b"Diese Zeile verschiebt alle Byte-Offsets. " * 3 + b"\n"
    return data[:header_end] + junk + data[header_end:]
