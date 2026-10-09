# Prompt für das multimodale LLM

So wurden `out/stolpersteine.haiku.txt` und `out/stolpersteine.sonnet.txt` erzeugt:
Claude Haiku 5.5 bzw. Claude Sonnet 5.5 als Subagent in Claude Code (je vier Subagenten
für einen Block von Seiten, Ausgabe danach zusammengefügt) mit Lesezugriff auf die Seitenbilder (`pdftoppm -r 110 -png
out/stolpersteine.pdf out/seiten/seite`). Das Modell durfte ausschließlich die PNGs
lesen, damit es Ground Truth und Code nicht sieht.

---

Du arbeitest als Dokument-Parser für ein RAG-System. Im Verzeichnis out/seiten/ liegen
37 Seitenbilder eines PDFs: seite-01.png bis seite-37.png.

Aufgabe: Sieh dir jedes Bild an (in Reihenfolge) und wandle den Inhalt jeder Seite in
Markdown um, so wie man es für die Indexierung in einem RAG-System machen würde:
- Text originalgetreu übernehmen, in natürlicher Lesereihenfolge. Nichts erfinden,
  nichts weglassen, nicht zusammenfassen.
- Überschriften als Markdown-Überschriften, Listen als Listen, Tabellen als Markdown-Tabellen.
- Bei Diagrammen/Grafiken: kurz beschreiben und ablesbare Werte angeben.
- Kopf- und Fußzeilen ebenfalls übernehmen (kennzeichne sie nicht besonders).
- Wenn etwas unleserlich ist, schreibe [unleserlich].

Lies ausschließlich die PNG-Dateien in out/seiten/.

Schreibe das Ergebnis in die Datei out/stolpersteine.sonnet.txt in genau diesem Format
(für jede Seite N): eine Leerzeile, dann `===== Seite N =====`, dann das Markdown der Seite.
