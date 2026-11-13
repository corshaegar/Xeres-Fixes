# Xeres-Fixes

**Bug fixes for the Gothic 2 mod *Xeres' Rückkehr* (Clockwork Origins, version 1.0.9) – and an option to join more than four
side guilds.** One small file for your `Data` folder. It does not modify any of the mod's files.

> *Deutsche Fassung: [weiter unten auf dieser Seite](#deutsch).*

**Contents:** [What it fixes](#what-it-fixes) · [More side guilds](#more-than-four-side-guilds) · [Installation](#installation) ·
[How it works](#how-it-works) · [Test status](#test-status) · [Building](#building-it-yourself) ·
[Origin and license](#origin-and-license)

## What it fixes

**1. Pointer checks above 2 GB.** Gothic 2 may use up to 4 GB of memory. Whenever an object of the game world lands in the upper half of that memory, the
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

**2. Crash when arrows hit you with blood splatter on** (new in 1.1.0, blood splatter kept since 1.2.0). This one needs the
Union Toolkit (`Data\Toolkit.vdf`), which several Union plugins bring along. It replaces the mod's LeGo 2.5 with LeGo 2.9, and
LeGo 2.9 handles damage to the hero differently: after showing the blood splatter it calls the mod's own damage function –
which, with the option "Blutspritzer" on (the default), calls the blood splatter again. If a hit from a bow or crossbow leaves
your health unchanged or takes just one point (the mod then works out the real damage itself), the two keep calling each other
until the game crashes. Until now the only way around it was to switch blood splatter off in the menu.

Version 1.1.0 stopped the crash by cutting that second call, which also cost you most of the blood splatter: LeGo 2.9 shows its
own splatter before the mod has worked out the damage, so it hardly ever appeared. 1.2.0 stops the crash and keeps the splatter.

## More than four side guilds

Xeres' Rückkehr lets you join at most four side guilds. From 1.3.0 on, that limit is an option: **Optionen → Speziell →
Nebengilden** offers "4 (Original)", 5, 6, 7, 8 and "unbegrenzt" (no limit). It starts at 4 – as long as you leave it there,
the game plays exactly as before. A change applies at once, also in a running game and also when you already have four side
guilds: raise the limit and you can join again. What rules each other out stays as it is (bandits or Old Camp guards, the
guards or the royal guard, militia, paladins and so on).

Most guild leaders ask again whenever you talk to them. Four offers, however, come only once in the mod: the Brotherhood in the
swamp (Baal Namib, after the undead swamp sharks), the thieves (Cassia), helping the Old Camp (Scatty – the way to the guards)
and the way to the assassins' hideout (Amir). If you passed one of them while your side guilds were full, the same person now
offers you a second chance – but only while the option is set above 4.

Two places in the mod use "four side guilds" as a free pass, because nobody could join more: the reward for activating all
Beliar shrines (unless you are a ranger or a thief, the shrines in the Old Mine and in the sewers are only waived once you have
four side guilds) and Mario's rise to knight (if you are not an assassin). Both checked for exactly four and would never be met
with five or more; the fix makes them check for four or more. Up to four guilds, that is the same as in the original.

The menu stores the option in `Gothic.ini`, section `[XERES_FIXES]`, as `nebengilden` (0 = 4 as in the original, 1 = 5 …
4 = 8, 5 = no limit). If you edit it there, do it while the game is closed – Gothic rewrites the file when it quits.

## Installation

1. Copy `Xeres_Fixes.vdf` into the `Data` folder of the Gothic 2 installation that contains Xeres' Rückkehr.
2. Start Xeres' Rückkehr as usual.

Requires Xeres' Rückkehr 1.0.9 with Union and zParserExtender – both are part of the usual installation. To remove it, delete
`Xeres_Fixes.vdf` again. Saves made with 1.3.0 also list its four extra conversations; without the file, Gothic should simply
skip them, but that has not been tested yet.

- **The earlier teleport fix** (`XeresNeu_Teleportfix.vdf`) fixed the world changes and the pass only. You can keep it or
  remove it – both work together.
- **[Gothic-I-II-Universal-Coop](https://github.com/corshaegar/Gothic-I-II-Universal-Coop)** contains both bug fixes for every
  mod from its next release on (after 0.10.3). With the coop installed you don't need this file for them, but it does no harm
  either. The side-guild option is only in this package; in co-op, both players should install it.

## How it works

Everything is in two Union scripts for zParserExtender inside the VDF: `System\Autorun\XERES_FIXES.D` and, for the menu line,
`XERES_FIXES_MENU.D`. The fixes run each time you start a new game or load a save and change only the loaded script code, never
a file.

**Pointer checks:** the fix changes exactly these comparisons in the loaded script code from `> 0` to `!= 0` – one byte per place
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

**Blood splatter:** the Union Toolkit replaces the mod's LeGo functions by writing a jump to the new LeGo 2.9 code at the start
of each old one. If LeGo 2.9 or newer handles the damage reaction (it then has the variable `_B_HeroDamagePercFunc`), the fix
gives the mod's old blood splatter function (`_B_HeroDamage` from LeGo 2.5) its first instruction back. The mod's damage function
`B_AssessDamage_Hero` then calls that old function again: it shows the splatter for the damage actually dealt and calls nothing
back. Damage, poison and everything else in that function work as before. If the code does not look as expected, the fix falls
back to what 1.1.0 did and turns the call into a jump to the next instruction – no crash, but hardly any splatter. Without the
Union Toolkit nothing changes. zSpy shows `Xeres-Fixes: Blutspritzer-Schleife behoben - B_AssessDamage_Hero ruft wieder Xeres'
eigene Blutspritzer-Funktion` ("blood splatter loop fixed – the damage function calls Xeres' own blood splatter again").

**Side guilds:** in the mod's 22 join checks (`Mod_AnzahlNebengilden < MaxNebengilden`, at Dexter's greeting `>=`), the fix
replaces the fixed limit with a call that reads the option every time – in the loaded script code, the instruction
`PUSHVAR MaxNebengilden` becomes `CALL XRFIX_MaxNebengilden`, both 5 bytes. The two "exactly four" checks become "four or more".
That makes 25 places in 24 functions; zSpy shows `Xeres-Fixes: Nebengilden-Grenze einstellbar, Stellen umgestellt: 25`. The
menu script adds one line to Xeres' own options page "Speziell", below Free Aim; all of Xeres' entries stay. The four second
chances are conversations of their own that call the mod's original dialogue functions, so you hear the original voices. A new
game lists them right away. When you load a save from before 1.3.0, though, Gothic takes its list of conversations from the save,
and the four are missing – so the fix adds them right after loading, the same way Gothic itself sets up a conversation, and from
your next save on they are part of it (zSpy: `Xeres-Fixes: zweite Gelegenheiten in die Dialogliste nachgetragen: 4`).

## Test status

`Test\zeiger_test.py` and `Test\blut_test.py` check both bug fixes against the real script of the mod without starting the
game. The pointer test takes `GOTHIC.DAT` from `Xeres_Scripts_DE.mod`, applies the fix byte by byte with the same rules as
the script and verifies the result: exactly
20 comparisons changed, no other byte touched, and a second run finds nothing more. The blood splatter test rebuilds the
Union Toolkit's jump and replays the fix instruction by instruction: exactly one call in `B_AssessDamage_Hero`; the old blood
splatter function gets its first instruction back and is then byte for byte the same as in the mod's script; the call itself
stays; a second run finds nothing. It checks the fallback as well. Result with Xeres' Rückkehr 1.0.9: both passed.

**Confirmed in the game** on 10 November 2026 (Xeres' Rückkehr 1.0.9 with Union and GD3D11): in a test start where
the co-op mod was told to leave the 20 places alone, it counted 20 open checks before the first game started and none after
each of the following loads – the fix had changed all of them. Starting a new game, changing worlds, saving and loading all
ran without problems.

The blood splatter fix was checked in the running game as well (10 and 11 November 2026, with the Union Toolkit installed).
With LeGo 2.9 the hero's damage reaction was indeed routed into `B_AssessDamage_Hero`, which still called `_B_HeroDamage` –
the loop behind the crash. The co-op mod's self-test then staged a hit from a bow: the hero with a drawn bow as the attacker,
health left unchanged by the engine, and the damage reaction called the way the engine calls it after a hit. With the loop put
back in place (as with the Toolkit and no fix), the reaction never came back: the game froze while the two functions kept
calling each other. With this package alone, with the co-op mod alone and with both, it came back right away, the mod dealt its
damage (5 to 30 points), and the blood splatter showed exactly that damage – on host and client alike.

`Test\nebengilden_test.py` replays the side-guild change on the real script: 25 places in 24 functions (22 calls, 3
comparisons), every place in the whole script covered, no other byte touched, a second run finds nothing, and with the option at
4 every place decides like the original for 0 to 4 guilds. `Test\skript_test.py` checks both script files against the mod's
compiled scripts – structure, names, fields, number of arguments, and that the menu line fits into Xeres' page – because
zParserExtender only compiles them when the game starts. All four tests pass with Xeres' Rückkehr 1.0.9.

**Checked in the running game** on 13 November 2026 (Xeres' Rückkehr 1.0.9 with Union, GD3D11 and several Union plugins),
loading a save made with 1.2.0, on two game instances: both scripts are compiled, all 25 places are changed and the 20 pointer
checks still are, the four second chances were added to the dialogue list (in the right order and for the same people as the
mod's own conversations), and the options page "Speziell" has the new line before "Zurück". A test build then changed the option
in the running game the way the menu stores it and asked Dragomir's real, changed join condition: with the option at 4 it stayed
closed at four guilds; at 5 it was open at four and closed at five; at "unbegrenzt" it was open at eight; an invalid value
counted as 4 – exactly as intended. The co-op mod's world test ran as before with the package. **Not tried yet:** using the menu
line on screen and actually talking to the four people for a second chance.

## Building it yourself

```
powershell -ExecutionPolicy Bypass -File Werkzeuge\bauen.ps1 -Test -Spiel "<Xeres' Rückkehr folder>"
```

builds `Bau\Xeres_Fixes.vdf` from `Quelltext\` after running the four tests (Python 3). The folder names are German: `Quelltext`
= source, `Werkzeuge` = tools, `Bau` = build output.

## Origin and license

The world-change bug was tracked down on 17 October 2026 (the earlier teleport fix); the VDF writer in `Werkzeuge\bauen.ps1`
comes from that fix. This package extends it to every place with the same cause. The blood splatter crash was reported by
a player on 10 November 2026; the side-guild option was added on 13 November 2026. Licensed under the GNU Affero General Public
License 3.0 ([`LICENSE`](LICENSE)). *Xeres' Rückkehr* belongs to Clockwork Origins, Gothic to its rights holders. No warranty.

---

# Deutsch

**Fehlerbehebungen für die Gothic-2-Mod *Xeres' Rückkehr* (Clockwork Origins, Version 1.0.9) – und eine Einstellung für mehr
als vier Nebengilden.** Eine kleine Datei für den Ordner `Data`. Sie verändert keine Datei der Mod.

**Inhalt:** [Was behoben wird](#was-behoben-wird) · [Mehr Nebengilden](#mehr-als-vier-nebengilden) ·
[Installation](#installation-1) · [Wie es funktioniert](#wie-es-funktioniert) · [Teststand](#teststand) ·
[Selbst bauen](#selbst-bauen) · [Herkunft und Lizenz](#herkunft-und-lizenz)

## Was behoben wird

**1. Zeiger-Prüfungen oberhalb von 2 GB.** Gothic 2 darf bis zu 4 GB Arbeitsspeicher nutzen. Landet ein Objekt der Spielwelt in der oberen Hälfte davon, sehen die
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

**2. Absturz, wenn einen Pfeile treffen und Blutspritzer an sind** (neu in 1.1.0, seit 1.2.0 mit Blutspritzern). Dazu braucht
es das Union-Toolkit (`Data\Toolkit.vdf`), das mehrere Union-Plugins mitbringen. Es ersetzt das LeGo 2.5 der Mod durch LeGo 2.9,
und das behandelt Schaden am Helden anders: Nach dem Blutspritzer ruft es die Schadens-Funktion der Mod auf – und die ruft bei
eingeschalteten Blutspritzern (Vorgabe) wieder den Blutspritzer auf. Ändert ein Treffer aus Bogen oder Armbrust die Lebenspunkte
gar nicht oder nur um einen Punkt (den eigentlichen Schaden rechnet dann die Mod selbst aus), rufen sich beide immer weiter auf,
bis das Spiel abstürzt. Bisher half nur, die Blutspritzer im Menü auszuschalten.

Version 1.1.0 verhinderte den Absturz, indem sie diesen zweiten Aufruf wegließ. Damit fehlten aber auch die meisten Blutspritzer:
LeGo 2.9 zeigt seinen Spritzer, bevor die Mod den Schaden ausgerechnet hat, also so gut wie nie. 1.2.0 verhindert den Absturz und
behält die Blutspritzer.

## Mehr als vier Nebengilden

In Xeres' Rückkehr kann man höchstens vier Nebengilden beitreten. Ab 1.3.0 ist diese Grenze einstellbar: **Optionen → Speziell →
Nebengilden** bietet „4 (Original)“, 5, 6, 7, 8 und „unbegrenzt“. Vorgabe ist 4 – solange es dabei bleibt, spielt sich Xeres
genau wie bisher. Eine Änderung gilt sofort, auch im laufenden Spiel und auch dann, wenn man schon vier Nebengilden hat: Grenze
hochsetzen, und man kann wieder beitreten. Was sich gegenseitig ausschließt, bleibt, wie es ist (Banditen oder Gardisten des
Alten Lagers, Gardisten oder Königliche Garde, Miliz, Paladine und so weiter).

Die meisten Anführer fragen bei jedem Gespräch neu. Vier Angebote macht die Mod aber nur ein einziges Mal: die Bruderschaft im
Sumpf (Baal Namib, nach den Sumpfhaizombies), die Diebe (Cassia), die Hilfe für das Alte Lager (Scatty – der Weg zu den
Gardisten) und der Weg zum Versteck der Assassinen (Amir). Wer an einem davon mit voller Grenze vorbeigekommen ist, bekommt bei
derselben Person eine zweite Gelegenheit – aber nur, solange die Einstellung über 4 steht.

Zwei Stellen der Mod nehmen „vier Nebengilden“ als Freibrief, weil man danach keiner Gilde mehr beitreten konnte: die Belohnung
für alle aktivierten Beliar-Schreine (wer weder Waldläufer noch Dieb ist, dem werden die Schreine in der Alten Mine und in der
Kanalisation erst mit vier Nebengilden erlassen) und Marios Aufstieg zum Ritter (wenn man kein Assassine ist). Beide prüften auf
genau vier und wären mit fünf oder mehr nie mehr erfüllt; der Fix prüft auf mindestens vier. Bis vier Gilden ist das dasselbe
wie im Original.

Das Menü speichert die Einstellung in der `Gothic.ini`, Abschnitt `[XERES_FIXES]`, als `nebengilden` (0 = 4 wie im Original,
1 = 5 … 4 = 8, 5 = unbegrenzt). Wer sie dort ändert, sollte das bei geschlossenem Spiel tun – Gothic schreibt die Datei beim
Beenden neu.

## Installation

1. `Xeres_Fixes.vdf` in den Ordner `Data` der Gothic-2-Installation kopieren, in der Xeres' Rückkehr liegt.
2. Xeres' Rückkehr wie gewohnt starten.

Voraussetzung ist Xeres' Rückkehr 1.0.9 mit Union und zParserExtender; beides gehört zur üblichen Installation. Zum
Entfernen `Xeres_Fixes.vdf` wieder löschen. Spielstände aus 1.3.0 führen auch die vier zusätzlichen Gespräche; ohne die Datei
sollte Gothic sie einfach übergehen, ausprobiert ist das aber noch nicht.

- **Der frühere Teleport-Fix** (`XeresNeu_Teleportfix.vdf`) hat nur die Weltwechsel und den Pass behoben. Er kann bleiben
  oder weg – beide vertragen sich.
- **[Gothic-I-II-Universal-Coop](https://github.com/corshaegar/Gothic-I-II-Universal-Coop)** enthält beide Fehlerbehebungen für
  jede Mod ab seiner nächsten Veröffentlichung (nach 0.10.3). Mit dem Coop braucht man diese Datei dafür nicht, sie schadet aber
  auch nicht. Die Nebengilden-Einstellung gibt es nur in diesem Paket; im Coop sollten beide Spieler es installieren.

## Wie es funktioniert

Alles steckt in zwei Union-Skripten für zParserExtender im VDF: `System\Autorun\XERES_FIXES.D` und, für die Menüzeile,
`XERES_FIXES_MENU.D`. Die Fixes laufen bei jedem neuen Spiel und jedem Laden und ändern nur den geladenen Skriptcode, nie eine
Datei.

**Zeiger-Prüfungen:** Der Fix stellt im geladenen Skriptcode genau diese Vergleiche von `> 0` auf `!= 0` um – ein Byte je Stelle (aus
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

**Blutspritzer:** Das Union-Toolkit ersetzt die LeGo-Funktionen der Mod, indem es an den Anfang jeder alten einen Sprung auf den
neuen Code von LeGo 2.9 schreibt. Behandelt LeGo 2.9 oder neuer den Schaden am Helden (es gibt dann die Variable
`_B_HeroDamagePercFunc`), gibt der Fix der alten Blutspritzer-Funktion der Mod (`_B_HeroDamage` aus LeGo 2.5) ihren ersten Befehl
zurück. Die Schadens-Funktion der Mod `B_AssessDamage_Hero` ruft dann wieder sie auf: Sie zeigt den Blutspritzer für den
tatsächlichen Schaden und ruft nichts zurück. Schaden, Gift und alles andere in dieser Funktion wirken wie bisher. Sieht der Code
nicht wie erwartet aus, macht der Fix es wie 1.1.0 und wandelt den Aufruf in einen Sprung auf den nächsten Befehl um – kein
Absturz, aber kaum Blutspritzer. Ohne Union-Toolkit ändert sich nichts. Im Log von zSpy steht `Xeres-Fixes: Blutspritzer-Schleife
behoben - B_AssessDamage_Hero ruft wieder Xeres' eigene Blutspritzer-Funktion`.

**Nebengilden:** In den 22 Beitritts-Prüfungen der Mod (`Mod_AnzahlNebengilden < MaxNebengilden`, bei Dexters Begrüßung `>=`)
ersetzt der Fix die feste Grenze durch einen Aufruf, der die Einstellung jedes Mal neu liest – im geladenen Skriptcode wird aus
dem Befehl `PUSHVAR MaxNebengilden` ein `CALL XRFIX_MaxNebengilden`, beide 5 Bytes. Aus den beiden Prüfungen auf „genau vier“
wird „mindestens vier“. Das sind 25 Stellen in 24 Funktionen; im Log von zSpy steht `Xeres-Fixes: Nebengilden-Grenze
einstellbar, Stellen umgestellt: 25`. Das Menü-Skript fügt Xeres' eigener Seite „Speziell“ eine Zeile unter Free Aim hinzu;
alle Einträge von Xeres bleiben. Die vier zweiten Gelegenheiten sind eigene Gespräche, die die Original-Dialoge der Mod aufrufen –
man hört also die Original-Stimmen. Ein neues Spiel führt sie sofort. Lädt man dagegen einen Spielstand von vor 1.3.0, nimmt
Gothic die Liste der Gespräche aus dem Spielstand, und die vier fehlen – der Fix trägt sie deshalb gleich nach dem Laden nach, so
wie Gothic selbst ein Gespräch anlegt; ab dem nächsten Speichern stehen sie im Spielstand (zSpy: `Xeres-Fixes: zweite
Gelegenheiten in die Dialogliste nachgetragen: 4`).

## Teststand

`Test\zeiger_test.py` und `Test\blut_test.py` prüfen beide Fehlerbehebungen am echten Skript der Mod, ohne das Spiel zu starten. Der
Zeiger-Test holt `GOTHIC.DAT` aus `Xeres_Scripts_DE.mod`, wendet den Fix Byte für Byte nach denselben Regeln an wie das
Skript und prüft das Ergebnis: genau 20
Vergleiche umgestellt, kein anderes Byte verändert, ein zweiter Lauf findet nichts mehr. Der Blutspritzer-Test baut den Sprung
des Union-Toolkits nach und spielt den Fix Befehl für Befehl nach: genau ein Aufruf in `B_AssessDamage_Hero`; die alte
Blutspritzer-Funktion bekommt ihren ersten Befehl zurück und ist danach Byte für Byte wie im Skript der Mod; der Aufruf selbst
bleibt; ein zweiter Lauf findet nichts. Auch der Rückfall wird geprüft. Ergebnis mit Xeres' Rückkehr 1.0.9: beide bestanden.

**Im Spiel bestätigt** am 10. November 2026 (Xeres' Rückkehr 1.0.9 mit Union und GD3D11): In einem Probestart ließ der
Coop die 20 Stellen absichtlich unverändert. Vor dem ersten Spielstart zählte er 20 offene Prüfungen, nach jedem weiteren
Laden keine mehr – der Fix hatte alle umgestellt. Neues Spiel, Weltwechsel, Speichern und Laden liefen ohne Probleme.

Der Blutspritzer-Fix ist ebenfalls im laufenden Spiel geprüft (10. und 11. November 2026, mit Union-Toolkit). Mit LeGo 2.9 war
die Schadens-Wahrnehmung des Helden tatsächlich auf `B_AssessDamage_Hero` verkettet, das weiter `_B_HeroDamage` aufrief – die
Schleife hinter dem Absturz. Der Selbsttest des Coops hat dann einen Treffer aus dem Bogen nachgestellt: der eigene Held mit
gezogenem Bogen als Angreifer, die Lebenspunkte von der Engine unverändert, die Schadens-Wahrnehmung so aufgerufen, wie die
Engine sie nach einem Treffer aufruft. Mit wieder eingesetzter Schleife (wie mit Toolkit ohne Fix) kam die Wahrnehmung nicht mehr
zurück: Das Spiel stand, während sich beide Funktionen immer weiter aufriefen. Mit diesem Paket allein, mit dem Coop allein und
mit beiden kam sie sofort zurück, die Mod zog ihren Schaden ab (5 bis 30 Punkte), und der Blutspritzer zeigte genau diesen
Schaden – bei Host und Client.

`Test\nebengilden_test.py` spielt die Nebengilden-Umstellung am echten Skript nach: 25 Stellen in 24 Funktionen (22 Aufrufe,
3 Vergleiche), jede Stelle im ganzen Skript erfasst, kein anderes Byte verändert, ein zweiter Lauf findet nichts, und mit der
Einstellung 4 entscheidet jede Stelle für 0 bis 4 Gilden wie das Original. `Test\skript_test.py` prüft beide Skriptdateien gegen
die übersetzten Skripte der Mod – Aufbau, Namen, Felder, Zahl der Argumente und ob die Menüzeile in Xeres' Seite passt –, weil
zParserExtender sie erst beim Spielstart übersetzt. Alle vier Tests bestehen mit Xeres' Rückkehr 1.0.9.

**Im laufenden Spiel geprüft** am 13. November 2026 (Xeres' Rückkehr 1.0.9 mit Union, GD3D11 und mehreren Union-Plugins), mit
einem Spielstand aus 1.2.0 und zwei Spielinstanzen: Beide Skripte werden übersetzt, alle 25 Stellen sind umgestellt und die 20
Zeiger-Prüfungen weiterhin, die vier zweiten Gelegenheiten wurden in die Dialogliste nachgetragen (richtig einsortiert und bei
denselben Personen wie die Gespräche der Mod), und die Seite „Speziell“ hat die neue Zeile vor „Zurück“. Ein Testbau hat dann die
Einstellung im laufenden Spiel so geändert, wie das Menü sie speichert, und Dragomirs echte, umgestellte Beitrittsbedingung
gefragt: Mit Einstellung 4 blieb sie bei vier Gilden zu; mit 5 war sie bei vier offen und bei fünf zu; mit „unbegrenzt“ bei acht
offen; ein ungültiger Wert zählte als 4 – genau wie gewollt. Der Weltentest des Coops lief mit dem Paket wie vorher. **Noch nicht
ausprobiert:** die Menüzeile am Bildschirm bedienen und mit den vier Personen tatsächlich über eine zweite Gelegenheit sprechen.

## Selbst bauen

```
powershell -ExecutionPolicy Bypass -File Werkzeuge\bauen.ps1 -Test -Spiel "<Ordner von Xeres' Rückkehr>"
```

baut `Bau\Xeres_Fixes.vdf` aus `Quelltext\`, nachdem die vier Tests gelaufen sind (Python 3).

## Herkunft und Lizenz

Der Fehler bei den Weltwechseln wurde am 17. Oktober 2026 gefunden (der frühere Teleport-Fix); der VDF-Schreiber in
`Werkzeuge\bauen.ps1` stammt daraus. Dieses Paket behebt jetzt alle Stellen mit derselben Ursache. Den Blutspritzer-Absturz
hat am 10. November 2026 ein Spieler gemeldet; die Nebengilden-Einstellung kam am 13. November 2026 dazu. Lizenz: GNU Affero General
Public License 3.0 ([`LICENSE`](LICENSE)). *Xeres' Rückkehr* gehört Clockwork Origins, Gothic seinen Rechteinhabern. Ohne
Gewähr.
