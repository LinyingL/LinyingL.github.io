# Reproduktionscode zu beiden Abbildungen

Artikel: „Wessen Partei ist die SPD?“
https://linyingl.github.io/posts/wessen-partei-spd/

## Zuordnung

- `abb1/sonntagsfrage_spd.py`: Abbildung 1, Links-/Rechtsblock und Zusammensetzung des linken Spektrums, 2017 bis Juni 2026.
- `abb2/sonntagsfrage_spd_laender.py`: Abbildung 2, SPD-Landtagsumfragen vor und seit dem Rentenstreit.
- Die Dateien mit `_original.py` enthalten die unverändert eingereichten Originalskripte.
- Die anderen Skripte ergänzen nur Datumsgrenze, lokale Eingabe und CSV-Ausgabe; Plotgestaltung und Berechnung bleiben erhalten.

## Ausführen

Das gesamte ZIP entpacken, dann im entpackten Verzeichnis:

```bash
python3 -m pip install -r requirements.txt
python3 abb1/sonntagsfrage_spd.py
python3 abb2/sonntagsfrage_spd_laender.py
```

Die Standardläufe lesen ihre JSON-Dateien im jeweiligen Skriptverzeichnis, benötigen keinen API-Zugriff und schreiben dort PNG und CSV.
Die im Paket enthaltenen PNGs sind die Ergebnisse der dokumentierten Reproduktionsläufe.

## Abbildung 1

Datengrenze: 10. Juni 2026. Der letzte enthaltene Bundestagsumfragetag ist der 9. Juni 2026.
2.594 Bundestagsumfragen ab Januar 2017.
Die Rollmittelberechnung bleibt wie im Original: je Partei werden alle verfügbaren Werte vom aktuellen Umfragedatum bis einschließlich 14 Kalendertage davor gemittelt.
Fehlende Parteiwerte bleiben bei der jeweiligen Mittelwertbildung unberücksichtigt; fehlende BSW-Rollmittel werden als null behandelt.
Mehrere Umfragen desselben Tages erzeugen mehrere aufeinanderfolgende Punkte, entsprechend der Originalberechnung.
Linksblock: SPD + Grüne + Linke + BSW. Rechtsblock: CDU/CSU + FDP + AfD.
Ergebnis am Endpunkt, gerundet: links 40 Prozent, rechts 54 Prozent; SPD-Anteil im linken Block 54 Prozent am Anfang und 30 Prozent am Ende.
Die CSV enthält die tatsächlich gezeichneten Parteirollmittel, Blocksummen und Anteile.

## Abbildung 2

Basisfenster: 24. Februar bis einschließlich 16. Oktober 2025.
Vergleichsfenster: 17. Oktober 2025 bis einschließlich 10. Juni 2026.
Arithmetische, ungewichtete Mittel aller vorhandenen SPD-Werte pro Parlament und Zeitfenster.
Ein Land wird nur dargestellt, wenn in beiden Zeitfenstern Daten vorliegen.
„Stabil oder im Plus“ bedeutet eine Veränderung von mindestens −1 Prozentpunkt.
Niedersachsen und Schleswig-Holstein entfallen wegen fehlender Werte in einem der beiden Fenster.
Einige Länder beruhen auf weniger als drei Umfragen in einem Fenster; die CSV weist alle Anzahlen aus.
Ergebnis: 9 von 14 Landesverbänden stabil oder im Plus; Rheinland-Pfalz +4,133 und Mecklenburg-Vorpommern +5,250 Prozentpunkte.
Die Bundesreihe ist eine Vergleichszeile und wird nicht als Landesverband mitgezählt.

## Datenstand und Quellen

Die öffentlichen Daten wurden am 8. November 2026 von https://api.dawum.de/ abgerufen und nach Umfragedatum auf die genannten Zeiträume begrenzt.
Die beiden JSON-Dateien sind nachträgliche Datenauszüge, keine archivierten API-Antworten aus dem Juni.
Die Originalgrafiken aus der Juni-PDF bleiben im Artikel erhalten.

Für andere Stichtage sind `--as-of YYYY-MM-DD` und `--data DATEI.json` verfügbar.
`--live` aktiviert ausdrücklich einen erneuten DAWUM-Abruf. Die Originalskripte verwenden dagegen ohne obere Datumsgrenze die jeweils aktuelle API.

Quelle und Datenlizenz: DAWUM, https://dawum.de/, ODC-ODbL
https://opendatacommons.org/licenses/odbl/1-0/
Bestehende Quellen- und Lizenzangaben bleiben in den Dateien erhalten.
