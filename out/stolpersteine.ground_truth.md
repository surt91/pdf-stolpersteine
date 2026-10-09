# Ground Truth

Inhalt, den ein perfekter Extraktor liefern sollte: das, was ein Mensch beim Lesen
als Inhalt wahrnimmt. Ohne Kopf-/Fußzeilen, Wasserzeichen, unsichtbaren oder
geschwärzten Text.

<!-- inhaltsverzeichnis: Seite(n) 1 -->
## 1. Deckblatt und Inhaltsverzeichnis

Stolperstein-Testdokument

Ein PDF, das Textextraktoren das Leben schwer macht

Inhaltsverzeichnis

- 1. Deckblatt und Inhaltsverzeichnis (Seite i)
- 2. Ligaturen (Seite 1)
- 3. Fehlende ToUnicode-CMap (Seite 2)
- 4. Falsche ToUnicode-CMap (Seite 3)
- 5. Null-Bytes und Steuerzeichen (Seite 4)
- 6. Type-3-Schrift ohne Zeichenzuordnung (Seite 5)
- 7. Unicode-Doppelgänger (Seite 6)
- 8. Leerzeichen und Wortgrenzen (Seite 7)
- 9. Nicht eingebettete Schrift (Seite 8)
- 10. Silbentrennung und Zeilenumbrüche (Seite 9)
- 11. Mehrspaltiges Layout (Seite 10)
- 12. Stream-Reihenfolge und Lesereihenfolge (Seite 11)
- 13. Hoch- und Tiefstellungen (Seite 12)
- 14. Überschriften und Listen (Seite 13)
- 15. Tabellen (Seite 14)
- 16. Tabelle über zwei Seiten (Seite 15)
- 17. Gedrehter Text und Schreibrichtung (Seite 17)
- 18. Doppelter Text (Pseudo-Fett, Schatten) (Seite 18)
- 19. Wasserzeichen (Seite 19)
- 20. Satz über die Seitengrenze (Seite 20)
- 21. Text als Kurven (Seite 22)
- 22. Gescannte Seite ohne Text (Seite 23)
- 23. Scan mit fehlerhaftem OCR-Layer (Seite 24)
- 24. Diagramme und Bilder (Seite 25)
- 25. Formularfelder und Kommentare (Seite 26)
- 26. Versteckter Text (Seite 27)
- 27. Schwärzung (Seite 28)
- 28. Inkrementelles Update (Seite 29)
- 29. Text in Form-XObjects (Seite 30)
- 30. Mathematische Formeln (LaTeX) (Seite 31)
- 31. Office-Export (LibreOffice) (Seite 34)
- 32. Browser: Chrome „Drucken als PDF“ (Seite 35)
- 33. Browser über PostScript-Druckertreiber (Seite 36)

<!-- ligaturen: Seite(n) 2 -->
## 2. Ligaturen

*A) ToUnicode löst die Ligatur korrekt auf*

Die Effizienz der Auftragsfinanzierung wurde offiziell geprüft.
Der Stoff ist flexibel, der Einfluss auf die Bilanz gering.

*B) ToUnicode verweist auf das Ligatur-Zeichen (U+FB01 usw.)*

Die Effizienz der Auftragsfinanzierung wurde offiziell geprüft.
Der Stoff ist flexibel, der Einfluss auf die Bilanz gering.

*C) Ligatur-Glyphen fehlen in der ToUnicode-CMap*

Die Effizienz der Auftragsfinanzierung wurde offiziell geprüft.
Der Stoff ist flexibel, der Einfluss auf die Bilanz gering.

<!-- tounicode_fehlt: Seite(n) 3 -->
## 3. Fehlende ToUnicode-CMap

*A) Ohne ToUnicode, eingebettete Schrift hat noch eine cmap-Tabelle*

Kündigungsfrist: drei Monate zum Quartalsende.
Ansprechpartnerin ist Frau Weber, Durchwahl 4711.

*B) Ohne ToUnicode, ohne cmap-Tabelle und ohne Glyphnamen*

Bei Rückfragen wenden Sie sich bitte an den Kundenservice.
Die Servicezeiten sind montags bis freitags von 8 bis 18 Uhr.

<!-- tounicode_falsch: Seite(n) 4 -->
## 4. Falsche ToUnicode-CMap

Die Zahlung erfolgt innerhalb von 30 Tagen netto.
Der Rabatt beträgt 2 Prozent bei Zahlung binnen 10 Tagen.

<!-- nullbytes: Seite(n) 5 -->
## 5. Null-Bytes und Steuerzeichen

Grüße aus Düsseldorf, Königsallee 12.
Die Gebühren für März sind fällig.

<!-- type3_font: Seite(n) 6 -->
## 6. Type-3-Schrift ohne Zeichenzuordnung

Diese Zeilen verwenden eine Type-3-Schrift.
Die Garantie verlängert sich auf 24 Monate.

<!-- unicode_doppelgaenger: Seite(n) 7 -->
## 7. Unicode-Doppelgänger

Herr Müller und Herr Müller sind dieselbe Person.
Bitte ändern Sie Ihr Passwort regelmäßig.
Kaffee und Kaffee sehen gleich aus.
Der Betrag von 10 000 Euro ist fällig.
Siehe Seiten 3-5, Temperatur -5 °C.
Er sagte "Ja" und meinte 'Nein'.

<!-- leerzeichen: Seite(n) 8 -->
## 8. Leerzeichen und Wortgrenzen

*A) Jeder Buchstabe einzeln positioniert, keine Leerzeichen im Stream*

Die Lieferung erfolgt frei Haus.

*B) Gesperrt: zusätzlicher Zeichenabstand (Tc)*

Wichtiger Hinweis zur Lieferung

*C) TJ-Array: Wörter mit Verschiebungen statt Leerzeichen*

Das Angebot ist gültig bis Ende des Monats.

*D) Zu enge Wortabstände (1 pt)*

Rechnungsadresse und Lieferadresse sind identisch.

*E) Blocksatz: wenige Wörter über die ganze Zeilenbreite*

Kurz und gut.

<!-- schrift_nicht_eingebettet: Seite(n) 9 -->
## 9. Nicht eingebettete Schrift

*A) Leerzeichen im Content-Stream*

Die Kündigungsfrist beträgt drei Monate zum Quartalsende.
Sie ist schriftlich gegenüber der Personalabteilung zu erklären.

*B) Jedes Wort einzeln positioniert*

Die Lieferung erfolgt frei Haus und ist bis zur Übergabe versichert.
Für Teillieferungen fallen keine zusätzlichen Kosten an.

<!-- silbentrennung: Seite(n) 10 -->
## 10. Silbentrennung und Zeilenumbrüche

*A) Schmale Spalte mit Trennstrichen (Bindestrich-Minus)*

Die Donaudampfschifffahrtsgesellschaft hat ihre Rechtsschutzversicherung zum Jahresende gekündigt. Rückfragen bitte per E-Mail an den Vertrieb.

*B) Weiches Trennzeichen U+00AD am Zeilenende*

Bitte reichen Sie die Arbeitsunfähigkeitsbescheinigung spätestens am dritten Kalendertag ein.

<!-- mehrspaltig: Seite(n) 11 -->
## 11. Mehrspaltiges Layout

Urlaubsregelung: Jeder Mitarbeitende hat Anspruch auf 30 Urlaubstage pro Jahr. Resturlaub muss bis zum 31. März des Folgejahres genommen werden, sonst verfällt er. Urlaubsanträge sind mindestens zwei Wochen im Voraus zu stellen.

Reisekosten: Dienstreisen werden mit der Bahn in der zweiten Klasse durchgeführt. Hotelkosten werden bis 120 Euro pro Nacht erstattet. Belege sind innerhalb von vier Wochen nach Reiseende einzureichen.

<!-- stream_reihenfolge: Seite(n) 12 -->
## 12. Stream-Reihenfolge und Lesereihenfolge

*A) Zeilen von unten nach oben gezeichnet*

Der Server wird jeden Sonntag um 3 Uhr neu gestartet. Während des Neustarts sind keine Anmeldungen möglich. Laufende Sitzungen werden vorher automatisch gespeichert. Bei Problemen hilft die Hotline unter der Nummer 1234.

*B) Anleitung in der Reihenfolge 3, 1, 4, 2 gezeichnet*

1. Gerät ausschalten und vom Strom trennen.
2. Gehäuse öffnen und alte Batterie entnehmen.
3. Neue Batterie einsetzen und Gehäuse schließen.
4. Gerät wieder einschalten und Uhrzeit einstellen.

<!-- hoch_tiefgestellt: Seite(n) 13 -->
## 13. Hoch- und Tiefstellungen

Der Umsatz stieg 2023¹ um 12 Prozent.
Die Bürofläche beträgt 250 m².
Die zulässige Abweichung liegt bei 10⁻³.
Der CO₂-Ausstoß sank laut Bericht² deutlich.

*Fußnoten*

¹ Vorläufige Zahlen, ungeprüft.
² Nachhaltigkeitsbericht 2024, S. 17.

<!-- ueberschriften_listen: Seite(n) 14 -->
## 14. Überschriften und Listen

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

<!-- tabellen: Seite(n) 15 -->
## 15. Tabellen

*A) Tabelle mit Rahmen und verbundenen Zellen*

| Region | Umsatz (Mio. €) 2023 | Umsatz (Mio. €) 2024 | Anmerkung |
|---|---|---|---|
| Nord | 12,4 | 13,1 | |
| Süd | 8,7 | 9,9 | inkl. Österreich |
| West | 15,0 | | Zahlen folgen |
| Ost (Neugründung seit Q3/2024) | – | 2,3 | |

*B) Rahmenlose Tabelle*

| Position | Menge | Einzelpreis | Summe |
|---|---|---|---|
| Beratung | 12 | 150,00 € | 1.800,00 € |
| Reisekosten | 1 | 320,50 € | 320,50 € |
| Lizenz (jährlich) | 3 | 1.200,00 € | 3.600,00 € |

<!-- tabelle_seitenumbruch: Seite(n) 16, 17 -->
## 16. Tabelle über zwei Seiten

Tabelle 3 listet alle Geräte im Inventar der Niederlassung Köln.

Tabelle 3: Inventarliste

| Nr. | Gerät | Standort | Anschaffung | Wert (€) |
|---|---|---|---|---|
| 1 | Server | Raum 1.02 | 2020-02 | 4.800,00 |
| 2 | Tablet | Raum 2.14 | 2021-03 | 579,00 |
| 3 | Telefon | Empfang | 2022-04 | 129,00 |
| 4 | Beamer | Serverraum | 2023-05 | 899,00 |
| 5 | Drucker | Raum 1.01 | 2024-06 | 640,00 |
| 6 | Dockingstation | Raum 1.02 | 2019-07 | 189,00 |
| 7 | Monitor 27 Zoll | Raum 2.14 | 2020-08 | 349,00 |
| 8 | Notebook | Empfang | 2021-09 | 1.290,00 |
| 9 | Server | Serverraum | 2022-10 | 4.800,00 |
| 10 | Tablet | Raum 1.01 | 2023-11 | 579,00 |
| 11 | Telefon | Raum 1.02 | 2024-12 | 129,00 |
| 12 | Beamer | Raum 2.14 | 2019-01 | 899,00 |
| 13 | Drucker | Empfang | 2020-02 | 640,00 |
| 14 | Dockingstation | Serverraum | 2021-03 | 189,00 |
| 15 | Monitor 27 Zoll | Raum 1.01 | 2022-04 | 349,00 |
| 16 | Notebook | Raum 1.02 | 2023-05 | 1.290,00 |
| 17 | Server | Raum 2.14 | 2024-06 | 4.800,00 |
| 18 | Tablet | Empfang | 2019-07 | 579,00 |
| 19 | Telefon | Serverraum | 2020-08 | 129,00 |
| 20 | Beamer | Raum 1.01 | 2021-09 | 899,00 |
| 21 | Drucker | Raum 1.02 | 2022-10 | 640,00 |
| 22 | Dockingstation | Raum 2.14 | 2023-11 | 189,00 |
| 23 | Monitor 27 Zoll | Empfang | 2024-12 | 349,00 |
| 24 | Notebook | Serverraum | 2019-01 | 1.290,00 |
| 25 | Server | Raum 1.01 | 2020-02 | 4.800,00 |
| 26 | Tablet | Raum 1.02 | 2021-03 | 579,00 |
| 27 | Telefon | Raum 2.14 | 2022-04 | 129,00 |
| 28 | Beamer | Empfang | 2023-05 | 899,00 |
| 29 | Drucker | Serverraum | 2024-06 | 640,00 |
| 30 | Dockingstation | Raum 1.01 | 2019-07 | 189,00 |
| 31 | Monitor 27 Zoll | Raum 1.02 | 2020-08 | 349,00 |
| 32 | Notebook | Raum 2.14 | 2021-09 | 1.290,00 |
| 33 | Server | Empfang | 2022-10 | 4.800,00 |
| 34 | Tablet | Serverraum | 2023-11 | 579,00 |
| 35 | Telefon | Raum 1.01 | 2024-12 | 129,00 |
| 36 | Beamer | Raum 1.02 | 2019-01 | 899,00 |
| 37 | Konferenzsystem mit Kamera, Mikrofonen und Display | Raum 2.14 | 2020-02 | 7.450,00 |
| 38 | Dockingstation | Empfang | 2021-03 | 189,00 |
| 39 | Monitor 27 Zoll | Serverraum | 2022-04 | 349,00 |
| 40 | Notebook | Raum 1.01 | 2023-05 | 1.290,00 |
| 41 | Server | Raum 1.02 | 2024-06 | 4.800,00 |
| 42 | Tablet | Raum 2.14 | 2019-07 | 579,00 |
| 43 | Telefon | Empfang | 2020-08 | 129,00 |
| 44 | Beamer | Serverraum | 2021-09 | 899,00 |
| 45 | Drucker | Raum 1.01 | 2022-10 | 640,00 |
| 46 | Dockingstation | Raum 1.02 | 2023-11 | 189,00 |
| 47 | Monitor 27 Zoll | Raum 2.14 | 2024-12 | 349,00 |
| 48 | Notebook | Empfang | 2019-01 | 1.290,00 |
| | Summe | | | 60.060,00 |

<!-- gedreht_rtl: Seite(n) 18 -->
## 17. Gedrehter Text und Schreibrichtung

*A) und B) Gedrehte Elemente*

Dieser Absatz ist ganz normaler Fließtext. Am rechten Rand steht eine gedrehte Randnotiz, darunter ein kopfstehender Hinweis.

Bitte nicht knicken

Entwurf – Freigabe durch die Rechtsabteilung ausstehend

*C) Hebräisch, in visueller Reihenfolge gespeichert*

שלום עולם

<!-- doppelter_text: Seite(n) 19 -->
## 18. Doppelter Text (Pseudo-Fett, Schatten)

*A) Pseudo-Fettdruck: dreimal versetzt gezeichnet*

Warnung: Gerät nicht öffnen!

Bei Zuwiderhandlung erlischt die Garantie.

*B) Schatten: grauer Text versetzt hinter schwarzem Text*

Jahresabschluss 2025

<!-- wasserzeichen: Seite(n) 20 -->
## 19. Wasserzeichen

Die Arbeitszeit beträgt 40 Stunden pro Woche. Gleitzeit ist zwischen 7 und 20 Uhr möglich, die Kernarbeitszeit liegt zwischen 10 und 15 Uhr.

Überstunden werden auf einem Arbeitszeitkonto erfasst und können in Absprache mit der Führungskraft abgebaut werden. Mehr als 50 Plusstunden sind nicht zulässig.

<!-- seitenumbruch: Seite(n) 21, 22 -->
## 20. Satz über die Seitengrenze

Diese Seite ist mit Absätzen gefüllt, damit der letzte Satz auf die nächste Seite umbricht. Die Regelung gilt für alle Standorte gleichermaßen und wurde mit dem Betriebsrat abgestimmt.

Diese Seite ist mit Absätzen gefüllt, damit der letzte Satz auf die nächste Seite umbricht. Die Regelung gilt für alle Standorte gleichermaßen und wurde mit dem Betriebsrat abgestimmt.

Diese Seite ist mit Absätzen gefüllt, damit der letzte Satz auf die nächste Seite umbricht. Die Regelung gilt für alle Standorte gleichermaßen und wurde mit dem Betriebsrat abgestimmt.

Diese Seite ist mit Absätzen gefüllt, damit der letzte Satz auf die nächste Seite umbricht. Die Regelung gilt für alle Standorte gleichermaßen und wurde mit dem Betriebsrat abgestimmt.

Diese Seite ist mit Absätzen gefüllt, damit der letzte Satz auf die nächste Seite umbricht. Die Regelung gilt für alle Standorte gleichermaßen und wurde mit dem Betriebsrat abgestimmt.

Diese Seite ist mit Absätzen gefüllt, damit der letzte Satz auf die nächste Seite umbricht. Die Regelung gilt für alle Standorte gleichermaßen und wurde mit dem Betriebsrat abgestimmt.

Diese Seite ist mit Absätzen gefüllt, damit der letzte Satz auf die nächste Seite umbricht. Die Regelung gilt für alle Standorte gleichermaßen und wurde mit dem Betriebsrat abgestimmt.

Diese Seite ist mit Absätzen gefüllt, damit der letzte Satz auf die nächste Seite umbricht. Die Regelung gilt für alle Standorte gleichermaßen und wurde mit dem Betriebsrat abgestimmt.

Diese Seite ist mit Absätzen gefüllt, damit der letzte Satz auf die nächste Seite umbricht. Die Regelung gilt für alle Standorte gleichermaßen und wurde mit dem Betriebsrat abgestimmt.

Diese Seite ist mit Absätzen gefüllt, damit der letzte Satz auf die nächste Seite umbricht. Die Regelung gilt für alle Standorte gleichermaßen und wurde mit dem Betriebsrat abgestimmt.

Diese Seite ist mit Absätzen gefüllt, damit der letzte Satz auf die nächste Seite umbricht. Die Regelung gilt für alle Standorte gleichermaßen und wurde mit dem Betriebsrat abgestimmt.

Diese Seite ist mit Absätzen gefüllt, damit der letzte Satz auf die nächste Seite umbricht. Die Regelung gilt für alle Standorte gleichermaßen und wurde mit dem Betriebsrat abgestimmt.

Wichtig: Die Kündigung eines Vertrags ist nur wirksam, wenn sie schriftlich und unter* Angabe der Vertragsnummer erfolgt sowie spätestens sechs Wochen vor Ablauf der Mindestlaufzeit beim Kundenservice eingeht.

Hier beginnt ein neuer Absatz auf der zweiten Seite.

* Gilt nur für Verträge, die nach dem 1. Januar 2024 geschlossen wurden.

<!-- text_als_kurven: Seite(n) 23 -->
## 21. Text als Kurven

Der folgende Hinweis ist kein Text, sondern eine Grafik aus Pfaden:

*Pfade:*

Kündigungsfrist: 3 Monate zum Quartalsende
Hotline: 0800 123 456 (kostenfrei)

<!-- scan: Seite(n) 24 -->
## 22. Gescannte Seite ohne Text

Musterfirma GmbH · Personalabteilung

Bescheinigung

Hiermit bestätigen wir, dass Frau Erika Mustermann
seit dem 1. April 2019 in unserem Unternehmen als
Projektleiterin in Vollzeit beschäftigt ist.

Köln, den 14. Februar 2026

<!-- ocr_layer: Seite(n) 25 -->
## 23. Scan mit fehlerhaftem OCR-Layer

Rechnung Nr. 2026-0417
Rechnungsbetrag: 1.234,56 EUR
Zahlbar bis: 15.05.2026
IBAN: DE89 3704 0044 0532 0130 00
Verwendungszweck: Kundennummer 88172

<!-- diagramm_bild: Seite(n) 26 -->
## 24. Diagramme und Bilder

*A) Balkendiagramm*

Abbildung 1: Neukunden je Quartal 2025

| Quartal | Neukunden |
|---|---|
| Q1 | 12 |
| Q2 | 18 |
| Q3 | 9 |
| Q4 | 22 |

*B) Screenshot einer Tabelle*

| Tarif | Preis/Monat |
|---|---|
| Basis | 9,99 € |
| Pro | 19,99 € |
| Enterprise | auf Anfrage |

<!-- formular_annotationen: Seite(n) 27 -->
## 25. Formularfelder und Kommentare

Name: Erika Mustermann
Eintrittsdatum: 01.04.2019
Abteilung: Controlling
Teilzeit: ja

Unterschrift: ________________________

*Kommentar:* Bitte bis Freitag unterschreiben und an die Personalabteilung senden.

<!-- versteckter_text: Seite(n) 28 -->
## 26. Versteckter Text

### Bewerbung als Softwareentwicklerin

Ich bringe drei Jahre Erfahrung in der Entwicklung mit Python und TypeScript mit. In meinem letzten Projekt habe ich eine Schnittstelle zur Buchhaltung umgesetzt.

Auf dieser Seite steht mehr Text, als man sieht.

<!-- schwaerzung: Seite(n) 29 -->
## 27. Schwärzung

Auszug aus der Gehaltsabrechnung (personenbezogene Daten geschwärzt):

Mitarbeiter: [geschwärzt]
IBAN: [geschwärzt]
Bruttogehalt: [geschwärzt]
Steuerklasse: [geschwärzt]

<!-- inkrementelles_update: Seite(n) 30 -->
## 28. Inkrementelles Update

Der Vertragswert beträgt 75.000 EUR netto. Die Laufzeit beträgt 24 Monate.

<!-- text_in_xobject: Seite(n) 31 -->
## 29. Text in Form-XObjects

*A) Direkt auf der Seite*

Dieser Absatz steht direkt im Content-Stream der Seite.

*B) In einem Form-XObject, skaliert*

Dieser Absatz steckt in einem Form-XObject, das auf 85 Prozent verkleinert eingebunden wird, so wie es Werkzeuge zum Zusammenfügen, Stempeln oder Verkleinern von Seiten tun. Die Kündigungsfrist beträgt drei Monate zum Quartalsende.

<!-- formel: Seite(n) 32, 33, 34 -->
## 30. Mathematische Formeln (LaTeX)

Das Ising-Modell beschreibt Spins $\sigma_i \in \{-1, +1\}$ auf einem Gitter. Die Energie einer Konfiguration ist durch den Hamiltonoperator gegeben:

$$\mathcal{H}(\sigma) = -J \sum_{\langle i,j \rangle} \sigma_i \sigma_j - h \sum_{i=1}^{N} \sigma_i$$

Für die Zustandssumme gilt

$$Z = \sum_{\{\sigma\}} e^{-\beta \mathcal{H}(\sigma)}, \qquad \beta = \frac{1}{k_B T},$$

und die Magnetisierung pro Spin ergibt sich zu

$$m = \frac{1}{N} \sum_{i=1}^{N} \langle \sigma_i \rangle = \frac{1}{N\beta} \frac{\partial \ln Z}{\partial h}.$$

Das Ising-Modell beschreibt Spins $\sigma_i \in \{-1, +1\}$ auf einem Gitter. Die Energie einer Konfiguration ist durch den Hamiltonoperator gegeben:

$$\mathcal{H}(\sigma) = -J \sum_{\langle i,j \rangle} \sigma_i \sigma_j - h \sum_{i=1}^{N} \sigma_i$$

Für die Zustandssumme gilt

$$Z = \sum_{\{\sigma\}} e^{-\beta \mathcal{H}(\sigma)}, \qquad \beta = \frac{1}{k_B T},$$

und die Magnetisierung pro Spin ergibt sich zu

$$m = \frac{1}{N} \sum_{i=1}^{N} \langle \sigma_i \rangle = \frac{1}{N\beta} \frac{\partial \ln Z}{\partial h}.$$

Das Ising-Modell beschreibt Spins $\sigma_i \in \{-1, +1\}$ auf einem Gitter. Die Energie einer Konfiguration ist durch den Hamiltonoperator gegeben:

$$\mathcal{H}(\sigma) = -J \sum_{\langle i,j \rangle} \sigma_i \sigma_j - h \sum_{i=1}^{N} \sigma_i$$

Für die Zustandssumme gilt

$$Z = \sum_{\{\sigma\}} e^{-\beta \mathcal{H}(\sigma)}, \qquad \beta = \frac{1}{k_B T},$$

und die Magnetisierung pro Spin ergibt sich zu

$$m = \frac{1}{N} \sum_{i=1}^{N} \langle \sigma_i \rangle = \frac{1}{N\beta} \frac{\partial \ln Z}{\partial h}.$$

<!-- office_export: Seite(n) 35 -->
## 31. Office-Export (LibreOffice)

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

Köln, den 02.10.26

¹ Für Auszubildende gilt die gesonderte Regelung in Anlage 2.
² Siehe Datenschutzrichtlinie, Abschnitt 4.

<!-- browser_chrome: Seite(n) 36 -->
## 32. Browser: Chrome „Drucken als PDF“

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

<!-- browser_postscript: Seite(n) 37 -->
## 33. Browser über PostScript-Druckertreiber

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
