# Änderungen

> *English version: [CHANGELOG.md](CHANGELOG.md).*

## 1.3.0 – Mehr als vier Nebengilden (Einstellung)

- **Neue Einstellung: Optionen → Speziell → Nebengilden** – „4 (Original)“, 5, 6, 7, 8 oder „unbegrenzt“. Vorgabe ist 4, es
  ändert sich also nichts, solange man sie nicht hochsetzt. Eine Änderung gilt sofort, auch im laufenden Spiel und wenn man
  schon vier Nebengilden hat. Gespeichert in der `Gothic.ini` unter `[XERES_FIXES]` als `nebengilden`.
- **Zweite Gelegenheiten:** Die vier Angebote, die die Mod nur einmal macht (Bruderschaft im Sumpf, Diebe, Hilfe für das Alte
  Lager, Weg zum Versteck der Assassinen), kommen bei derselben Person wieder, wenn man mit voller Grenze daran vorbeigekommen
  ist – nur, solange die Einstellung über 4 steht. In Spielständen von vor 1.3.0 trägt der Fix diese Gespräche beim Laden nach.
- Die Belohnung für die Beliar-Schreine und Marios Aufstieg zum Ritter behandeln vier oder mehr Nebengilden so, wie sie genau
  vier behandelt haben.
- Was sich gegenseitig ausschließt (Banditen oder Gardisten, Gardisten oder Königliche Garde, Miliz, Paladine), bleibt, wie es
  ist.
- Am echten Skript der Mod geprüft (`Test\nebengilden_test.py`: 25 Stellen in 24 Funktionen, mit Einstellung 4 wie das
  Original; `Test\skript_test.py`: beide Skriptdateien gegen die übersetzten Skripte der Mod) und im laufenden Spiel mit einem
  Spielstand aus 1.2.0: alle Stellen umgestellt, die vier Gespräche nachgetragen, die Menüzeile da, und Dragomirs
  Beitrittsbedingung folgt einer Änderung der Einstellung sofort. Noch nicht ausprobiert: das Menü am Bildschirm und die zweiten
  Gelegenheiten im Gespräch.
- Die Tests finden die Skripte der Mod jetzt auch direkt in `Data` (nicht nur in `Data\ModVDF`).

## 1.2.0 – Blutspritzer wieder da

- **Die Blutspritzer bleiben.** 1.1.0 verhinderte den Absturz, indem es den Blutspritzer-Aufruf der Mod wegließ. Weil LeGo 2.9
  seinen Spritzer zeigt, bevor die Mod den Schaden ausgerechnet hat, sah man danach kaum noch welche. 1.2.0 gibt der alten
  Blutspritzer-Funktion der Mod (aus LeGo 2.5) den ersten Befehl zurück, den das Union-Toolkit durch einen Sprung auf LeGo 2.9
  ersetzt hatte. Die Schadens-Funktion der Mod ruft wieder sie auf: Blutspritzer für den tatsächlichen Schaden, keine Schleife,
  kein Absturz.
- Sieht der Code nicht wie erwartet aus, macht der Fix es wie 1.1.0 – kein Absturz, aber kaum Blutspritzer.
- Keine globale Skript-Variable mehr (ein Coop hätte sie an den Mitspieler geschickt).
- Am echten Skript der Mod geprüft (`Test\blut_test.py`, jetzt mit nachgebautem Sprung des Toolkits) und im laufenden Spiel: Ein
  nachgestellter Treffer aus dem Bogen kam ohne Schleife zurück, die Mod zog ihren Schaden ab, und der Blutspritzer zeigte genau
  diesen Schaden.

## 1.1.0 – Absturz durch Blutspritzer

- **Behebt einen Absturz, wenn einen Pfeile treffen und Blutspritzer an sind.** Er tritt auf, wenn das Union-Toolkit
  (`Data\Toolkit.vdf`, das mehrere Union-Plugins mitbringen) das LeGo 2.5 der Mod durch LeGo 2.9 ersetzt: Dann rufen sich der
  Blutspritzer und die Schadens-Funktion der Mod gegenseitig auf, sobald ein Treffer aus Bogen oder Armbrust die Lebenspunkte
  gar nicht oder nur um einen Punkt ändert.
- Der Zeiger-Fix aus 1.0.0 bleibt unverändert; beide stecken jetzt in einem Skript, `XERES_FIXES.D`.
- Am echten Skript der Mod geprüft (`Test\blut_test.py`) und im laufenden Spiel: Die Schleife war da, und der Fix entfernt sie.

## 1.0.0 – Zeiger-Prüfungen oberhalb von 2 GB

- **Behebt 20 Stellen in Xeres' Rückkehr 1.0.9,** an denen die Skripte ein gültiges Objekt für nicht vorhanden halten, weil seine
  Adresse oberhalb von 2 GB liegt: Weltwechsel über Schrein, Obelisk, Runen, Spruchrollen, Steinkreistafeln und Xardas' Ring
  (falsches Ziel oder Absturz), der Pass ins Minental, die beiden Türen des Spinnenbaus nach Vinos Gespräch, die Loren in der
  Eismine, das Herausnehmen von Gegenständen aus Truhen und das Entfernen von Objekten.
- Enthält alles, was der frühere Teleport-Fix vom 17. Oktober 2026 tat (Weltwechsel und Pass); beide können zusammen
  installiert sein.
- Am echten Skript der Mod geprüft (`Test\zeiger_test.py`) und im Spiel bestätigt: Alle 20 Stellen werden umgestellt.
