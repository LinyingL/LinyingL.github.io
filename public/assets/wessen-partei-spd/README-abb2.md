# Code und Daten zu Abbildung 2

Dieses Paket gehört zur zweiten Grafik in „Wessen Partei ist die SPD?“:
„SPD in den Ländern seit der Bundestagswahl 2025“.

## Dateien

- `sonntagsfrage_spd_laender_original.py`: unverändertes eingereichtes Originalskript.
- `sonntagsfrage_spd_laender.py`: derselbe Plotcode mit Datumsgrenze, lokalem Dateneingang und CSV-Ausgabe.
- `spd_laender_input_2026-06-10.json`: verwendete öffentliche DAWUM-Umfragedaten.
- `sonntagsfrage_spd_laender.csv`: gezeichnete Mittelwerte und Zahl der Umfragen je Zeitfenster.
- `sonntagsfrage_spd_laender.png`: Ergebnis des dokumentierten Reproduktionslaufs, im ZIP enthalten.
- `requirements-spd-laender.txt`: verwendete Versionen der beiden Python-Abhängigkeiten.

## Reproduzieren

Alle Dateien aus dem ZIP in dasselbe Verzeichnis entpacken, dann:

```bash
python3 -m pip install -r requirements-spd-laender.txt
python3 sonntagsfrage_spd_laender.py
```

Der Standardlauf liest die mitgelieferte JSON-Datei und benötigt keinen API-Zugriff.
Ausgaben: `sonntagsfrage_spd_laender.png` und `sonntagsfrage_spd_laender.csv`.

Die Eingabe kann ausdrücklich gewählt werden:

```bash
python3 sonntagsfrage_spd_laender.py --data spd_laender_input_2026-06-10.json --as-of 2026-06-10
```

Für eine spätere Neuberechnung aus der API:

```bash
python3 sonntagsfrage_spd_laender.py --live --as-of 2026-11-08
```

## Zeitfenster und Definitionen

- Basis: 24. Februar bis einschließlich 16. Oktober 2025.
- Vergleich: 17. Oktober 2025 bis einschließlich 10. Juni 2026.
- Arithmetisches, ungewichtetes Mittel aller verfügbaren SPD-Werte je Parlament und Zeitfenster.
- Ein Land erscheint nur, wenn in beiden Zeitfenstern mindestens eine Umfrage vorliegt.
- „Stabil oder im Plus“: Vergleichsmittel minus Basismittel mindestens −1,0 Prozentpunkte.
- Niedersachsen und Schleswig-Holstein entfallen wegen fehlender Werte in einem der Fenster.
- Mehrere Länder beruhen auf weniger als drei Umfragen in einem Zeitfenster. Die CSV weist die jeweiligen Anzahlen aus.

Der datierte Lauf ergibt 9 von 14 Landesverbänden „stabil oder im Plus“.
Rheinland-Pfalz: +4,133 Prozentpunkte; Mecklenburg-Vorpommern: +5,250 Prozentpunkte.
Der Bundestag ist eine separate Vergleichszeile und wird nicht unter den Landesverbänden mitgezählt.

## Datenstand

Die Daten wurden am 8. November 2026 von https://api.dawum.de/ abgerufen
und nach dem Datum der Umfrage auf die genannten Zeitfenster begrenzt.
Es handelt sich um einen nachträglich erstellten Datenauszug, keinen archivierten API-Stand vom Juni.
Die im Artikel eingebettete Originalgrafik aus der Juni-PDF bleibt erhalten.
Der Originalcode greift ohne obere Datumsgrenze auf die jeweils aktuelle API zu.
Für die historische Grafik ist deshalb der datierte Reproduktionslauf maßgeblich.
Die erste, bundesweite Zeitreihengrafik wird von diesem Skript nicht erzeugt.

Quelle und Datenlizenz: DAWUM, https://dawum.de/, ODC-ODbL
(https://opendatacommons.org/licenses/odbl/1-0/).
Die bestehenden Quellen- und Lizenzangaben im Originalskript und Datensatz bleiben erhalten.
