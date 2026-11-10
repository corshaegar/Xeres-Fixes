# Änderungen

> *English version: [CHANGELOG.md](CHANGELOG.md).*

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
