# Änderungen

> *English version: [CHANGELOG.md](CHANGELOG.md).*

## 1.0.0 – Zeiger-Prüfungen oberhalb von 2 GB

- **Behebt 20 Stellen in Xeres' Rückkehr 1.0.9,** an denen die Skripte ein gültiges Objekt für nicht vorhanden halten, weil seine
  Adresse oberhalb von 2 GB liegt: Weltwechsel über Schrein, Obelisk, Runen, Spruchrollen, Steinkreistafeln und Xardas' Ring
  (falsches Ziel oder Absturz), der Pass ins Minental, die beiden Türen des Spinnenbaus nach Vinos Gespräch, die Loren in der
  Eismine, das Herausnehmen von Gegenständen aus Truhen und das Entfernen von Objekten.
- Enthält alles, was der frühere Teleport-Fix vom 17. Oktober 2026 tat (Weltwechsel und Pass); beide können zusammen
  installiert sein.
- Am echten Skript der Mod geprüft (`Test\zeiger_test.py`); im Spiel noch nicht gespielt.
