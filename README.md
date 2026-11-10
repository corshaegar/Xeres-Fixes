# Xeres-Fixes

**Bug fixes for the Gothic 2 mod *Xeres' Rückkehr* (Clockwork Origins, version 1.0.9).** One small file for your `Data` folder.
It does not modify any of the mod's files and stores nothing in your saves.

> *Deutsche Fassung: [weiter unten auf dieser Seite](#deutsch).*

**Contents:** [What it fixes](#what-it-fixes) · [Installation](#installation) · [How it works](#how-it-works) ·
[Test status](#test-status) · [Building](#building-it-yourself) · [Origin and license](#origin-and-license)

## What it fixes

Gothic 2 may use up to 4 GB of memory. Whenever an object of the game world lands in the upper half of that memory, the
mod's scripts see its address as a negative number. In 20 places, Xeres' Rückkehr checks such an address with `> 0` – and
treats a perfectly valid object as missing. What you notice depends on where it happens:

- **World changes go wrong** – via a Beliar shrine, an obelisk, teleport runes and scrolls, stone circle tablets or Xardas'
  ring. You either arrive at the destination you used last time (e.g. Relendel instead of the harbour), or the game unloads
  the current world without loading a new one and crashes.
- **The pass from Khorinis does not lead into the Valley of Mines.**
- **The two doors of the spider burrow** stay locked although Vino's conversation about his distillery should unlock them.
- **The mine carts in the ice mine** do not get their speed and collision when you set them off at the wheel.
- **Items that a script should take out of a chest stay in it,** and objects that a script removes stay in the world.

These bugs come and go: where the game places an object in memory varies, so the same route can work once and fail the
next time. The longer you play, the more memory the game uses and the more likely they become.

## Installation

1. Copy `Xeres_Fixes.vdf` into the `Data` folder of the Gothic 2 installation that contains Xeres' Rückkehr.
2. Start Xeres' Rückkehr as usual.

Requires Xeres' Rückkehr 1.0.9 with Union and zParserExtender – both are part of the usual installation. To remove the fix,
delete `Xeres_Fixes.vdf` again; your saves stay unaffected.

- **The earlier teleport fix** (`XeresNeu_Teleportfix.vdf`) fixed the world changes and the pass only. You can keep it or
  remove it – both work together.
- **[Gothic-I-II-Universal-Coop](https://github.com/corshaegar/Gothic-I-II-Universal-Coop)** contains the same fix for every
  mod (coop version u246 and later). With the coop installed you don't need this file, but it does no harm either.

## How it works

The fix is a Union script for zParserExtender (`System\Autorun\XERES_FIX_ZEIGER.D` inside the VDF). Each time you start a new
game or load a save, it changes exactly these comparisons in the loaded script code from `> 0` to `!= 0` – one byte per place
(Daedalus opcode 8 becomes 17). Nothing else changes: 0 still means "not found", and every valid object counts, including those
above 2 GB. A comparison is only changed if the variable holds a memory address (its name ends in `PTR`) and if it sits in one
of the 16 affected functions:

| Function | Places | What it affects |
|---|---|---|
| `B_SetLevelChange` | 1 | world changes (shrine, obelisk, runes, scrolls, stone circle, ring) |
| `Init_NewWorld`, `Info_Mod_Hagen_Hi_Info` | 1 each | the pass into the Valley of Mines |
| `Info_Mod_Vino_Brennerei_Info` | 2 | the two doors of the spider burrow |
| `LoreEisMine01/02_LetsGo_S0/S1`, `LoreEisSW01/02_LetsGo_S0/S1` | 1 each | setting off a mine cart at the wheel |
| `DauerFunc_01` | 4 | the mine carts while you are in the ice mine |
| `Mob_RemoveItems`, `MEM_RemoveVob`, `MEMINT_RemoveVob` | 1 each | taking items out of chests, removing objects |

If another script has replaced one of these functions (the earlier teleport fix does that), the fix changes the original
underneath, so both keep working. Running it a second time finds nothing left to change. The zSpy log shows the line
`Xeres-Fixes: Zeiger-Pruefungen umgestellt: 20` ("pointer checks changed: 20") once per game start.

## Test status

`Test\zeiger_test.py` checks the fix against the real script of the mod without starting the game. It takes `GOTHIC.DAT`
from `Xeres_Scripts_DE.mod`, applies the fix byte by byte with the same rules as the script and verifies the result: exactly
20 comparisons changed, no other byte touched, and a second run finds nothing more. Result with Xeres' Rückkehr 1.0.9:
passed. **It has not been played in the game yet.**

## Building it yourself

```
powershell -ExecutionPolicy Bypass -File Werkzeuge\bauen.ps1 -Test -Spiel "<Xeres' Rückkehr folder>"
```

builds `Bau\Xeres_Fixes.vdf` from `Quelltext\` after running the test (Python 3). The folder names are German: `Quelltext`
= source, `Werkzeuge` = tools, `Bau` = build output.

## Origin and license

The world-change bug was tracked down on 17 October 2026 (the earlier teleport fix); the VDF writer in `Werkzeuge\bauen.ps1`
comes from that fix. This package extends it to every place with the same cause. Licensed under the GNU Affero General Public
License 3.0 ([`LICENSE`](LICENSE)). *Xeres' Rückkehr* belongs to Clockwork Origins, Gothic to its rights holders. No warranty.

---

# Deutsch

**Fehlerbehebungen für die Gothic-2-Mod *Xeres' Rückkehr* (Clockwork Origins, Version 1.0.9).** Eine kleine Datei für den
Ordner `Data`. Sie verändert keine Datei der Mod und speichert nichts in deinen Spielständen.

**Inhalt:** [Was behoben wird](#was-behoben-wird) · [Installation](#installation-1) · [Wie es funktioniert](#wie-es-funktioniert) ·
[Teststand](#teststand) · [Selbst bauen](#selbst-bauen) · [Herkunft und Lizenz](#herkunft-und-lizenz)

## Was behoben wird

Gothic 2 darf bis zu 4 GB Arbeitsspeicher nutzen. Landet ein Objekt der Spielwelt in der oberen Hälfte davon, sehen die
Skripte der Mod seine Adresse als negative Zahl. An 20 Stellen prüft Xeres' Rückkehr eine solche Adresse mit `> 0` – und hält
ein gültiges Objekt für nicht vorhanden. Was man davon merkt, hängt von der Stelle ab:

- **Weltwechsel gehen schief** – über einen Beliar-Schrein, einen Obelisken, Teleport-Runen und -Spruchrollen,
  Steinkreistafeln oder Xardas' Ring. Man landet am zuletzt benutzten Ziel (etwa in Relendel statt am Hafen), oder das Spiel
  entlädt die Welt, lädt keine neue und stürzt ab.
- **Der Pass bei Khorinis führt nicht ins Minental.**
- **Die beiden Türen des Spinnenbaus** bleiben verschlossen, obwohl Vinos Gespräch über seine Brennerei sie aufschließen soll.
- **Die Loren in der Eismine** bekommen beim Anstoßen am Rad weder Tempo noch Kollision.
- **Gegenstände, die ein Skript aus einer Truhe nehmen soll,** bleiben darin, und Objekte, die ein Skript entfernt, bleiben
  in der Welt.

Die Fehler kommen und gehen: Wo das Spiel ein Objekt im Speicher ablegt, ist jedes Mal anders. Derselbe Weg kann einmal
klappen und beim nächsten Mal nicht. Je länger man spielt und je mehr Speicher das Spiel belegt, desto häufiger treten sie auf.

## Installation

1. `Xeres_Fixes.vdf` in den Ordner `Data` der Gothic-2-Installation kopieren, in der Xeres' Rückkehr liegt.
2. Xeres' Rückkehr wie gewohnt starten.

Voraussetzung ist Xeres' Rückkehr 1.0.9 mit Union und zParserExtender; beides gehört zur üblichen Installation. Zum
Entfernen `Xeres_Fixes.vdf` wieder löschen – die Spielstände bleiben davon unberührt.

- **Der frühere Teleport-Fix** (`XeresNeu_Teleportfix.vdf`) hat nur die Weltwechsel und den Pass behoben. Er kann bleiben
  oder weg – beide vertragen sich.
- **[Gothic-I-II-Universal-Coop](https://github.com/corshaegar/Gothic-I-II-Universal-Coop)** enthält denselben Fix für jede
  Mod (ab Coop-Fassung u246). Mit dem Coop braucht man diese Datei nicht, sie schadet aber auch nicht.

## Wie es funktioniert

Der Fix ist ein Union-Skript für zParserExtender (`System\Autorun\XERES_FIX_ZEIGER.D` im VDF). Bei jedem neuen Spiel und
jedem Laden stellt er im geladenen Skriptcode genau diese Vergleiche von `> 0` auf `!= 0` um – ein Byte je Stelle (aus
Daedalus-Opcode 8 wird 17). Sonst ändert sich nichts: 0 heißt weiterhin „nicht gefunden“, und jedes gültige Objekt zählt,
auch oberhalb von 2 GB. Umgestellt wird nur, wenn die Variable eine Speicheradresse enthält (ihr Name endet auf `PTR`) und
in einer der 16 betroffenen Funktionen steht:

| Funktion | Stellen | Wirkung |
|---|---|---|
| `B_SetLevelChange` | 1 | Weltwechsel (Schrein, Obelisk, Runen, Spruchrollen, Steinkreis, Ring) |
| `Init_NewWorld`, `Info_Mod_Hagen_Hi_Info` | je 1 | Pass ins Minental |
| `Info_Mod_Vino_Brennerei_Info` | 2 | die beiden Türen des Spinnenbaus |
| `LoreEisMine01/02_LetsGo_S0/S1`, `LoreEisSW01/02_LetsGo_S0/S1` | je 1 | Anstoßen einer Lore am Rad |
| `DauerFunc_01` | 4 | die Loren, solange man in der Eismine ist |
| `Mob_RemoveItems`, `MEM_RemoveVob`, `MEMINT_RemoveVob` | je 1 | Gegenstände aus Truhen nehmen, Objekte entfernen |

Hat ein anderes Skript eine dieser Funktionen ersetzt (das tut der frühere Teleport-Fix), stellt der Fix das Original
darunter um – beide funktionieren dann weiter. Ein zweiter Lauf findet nichts mehr. Im Log von zSpy steht je Start einmal
`Xeres-Fixes: Zeiger-Pruefungen umgestellt: 20`.

## Teststand

`Test\zeiger_test.py` prüft den Fix am echten Skript der Mod, ohne das Spiel zu starten. Er holt `GOTHIC.DAT` aus
`Xeres_Scripts_DE.mod`, wendet den Fix Byte für Byte nach denselben Regeln an wie das Skript und prüft das Ergebnis: genau 20
Vergleiche umgestellt, kein anderes Byte verändert, ein zweiter Lauf findet nichts mehr. Ergebnis mit Xeres' Rückkehr 1.0.9:
bestanden. **Im Spiel ist er noch nicht gespielt.**

## Selbst bauen

```
powershell -ExecutionPolicy Bypass -File Werkzeuge\bauen.ps1 -Test -Spiel "<Ordner von Xeres' Rückkehr>"
```

baut `Bau\Xeres_Fixes.vdf` aus `Quelltext\`, nachdem der Test gelaufen ist (Python 3).

## Herkunft und Lizenz

Der Fehler bei den Weltwechseln wurde am 17. Oktober 2026 gefunden (der frühere Teleport-Fix); der VDF-Schreiber in
`Werkzeuge\bauen.ps1` stammt daraus. Dieses Paket behebt jetzt alle Stellen mit derselben Ursache. Lizenz: GNU Affero General
Public License 3.0 ([`LICENSE`](LICENSE)). *Xeres' Rückkehr* gehört Clockwork Origins, Gothic seinen Rechteinhabern. Ohne
Gewähr.
