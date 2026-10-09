"""Registry der Stolpersteine.

Reihenfolge in PITFALLS = Reihenfolge im PDF. Ein neuer Stolperstein ist ein
neues Modul in diesem Verzeichnis plus ein Eintrag hier (siehe README.md).
"""

from importlib import import_module
from types import ModuleType

PITFALLS = [
    # Dokumentweit, ohne eigene Seite
    "kopf_fusszeile",
    "metadaten_seitenzahlen",
    # Seiten
    "inhaltsverzeichnis",
    "ligaturen",
    "tounicode_fehlt",
    "tounicode_falsch",
    "nullbytes",
    "type3_font",
    "unicode_doppelgaenger",
    "leerzeichen",
    "schrift_nicht_eingebettet",
    "silbentrennung",
    "mehrspaltig",
    "stream_reihenfolge",
    "hoch_tiefgestellt",
    "ueberschriften_listen",
    "tabellen",
    "tabelle_seitenumbruch",
    "gedreht_rtl",
    "doppelter_text",
    "wasserzeichen",
    "seitenumbruch",
    "text_als_kurven",
    "scan",
    "ocr_layer",
    "diagramm_bild",
    "formular_annotationen",
    "versteckter_text",
    "schwaerzung",
    "inkrementelles_update",
    "text_in_xobject",
    # Seiten aus fremden Erzeugern (quellen/build.sh)
    "formel",
    "office_export",
    "browser_chrome",
    "browser_postscript",
    # Varianten (eigene Dateien)
    "kaputte_xref",
    "verschluesselt",
]


def load_pitfalls() -> list[ModuleType]:
    """Lädt alle Module. Wer AVAILABLE = False setzt (z. B. fehlende Quelldatei), wird übersprungen."""
    modules = []
    for name in PITFALLS:
        m = import_module(f"pitfalls.{name}")
        m.ID = name
        if not getattr(m, "AVAILABLE", True):
            print(f"übersprungen: {name} ({getattr(m, 'MISSING', 'nicht verfügbar')})")
            continue
        modules.append(m)
    return modules
