# Changes

> *Deutsche Fassung: [CHANGELOG.de.md](CHANGELOG.de.md).*

## 1.4.0 – Enemy AI like New Balance (option)

- **New option: Optionen → Speziell → Gegner-KI** – "Xeres (Original)" or "New Balance". It starts at Xeres, so nothing changes
  unless you switch it. A change applies after a second or two, also in a running game and in the middle of a fight. Stored
  in `Gothic.ini` under `[XERES_FIXES]` as `gegnerki`.
- "New Balance" is a way of fighting modelled on *Die Rückkehr 2.0 – New Balance*; 39 situations in 11 fighting styles change.
  Humans parry storm attacks, react when you circle them and wait at medium distance; masters use their combos; orcs wait less
  and attack in more varied ways; masters and orcs dodge sideways against a mage at a distance; minecrawlers, demons, stone
  golems, snappers and zombies hit back more often; swamp sharks no longer rush at you.
- The new moves come from this package's own rules applied to Xeres' fight tables – close to New Balance, but not the same, and
  without any of its files or data. What else New Balance changes about fighting, with its plugin and scripts, is not part of it.
- The options page "Speziell" lists the new line first and keeps all entries in screen order, so the arrow keys move from top to
  bottom.
- Checked against the real script of the mod (`Test\gegnerki_test.py`: the table matches the rules, switching changes exactly 39
  situations and restores them byte for byte, the switch in `DauerFunc_01` works with the Union Toolkit too; `Test\skript_test.py`:
  the new menu order) and in the running game on two instances: all 39 situations switched and the rest unchanged, a change of
  the option took effect after one to two and a half seconds in both directions, and the co-op mod's world test ran as before.
  Not tried yet: the menu on screen and how the fights feel.

## 1.3.0 – More than four side guilds (option)

- **New option: Optionen → Speziell → Nebengilden** – "4 (Original)", 5, 6, 7, 8 or "unbegrenzt" (no limit). It starts at 4,
  so nothing changes unless you raise it. A change applies at once, also in a running game and with four side guilds already
  joined. Stored in `Gothic.ini` under `[XERES_FIXES]` as `nebengilden`.
- **Second chances:** the four offers the mod makes only once (Brotherhood in the swamp, thieves, helping the Old Camp, the way
  to the assassins' hideout) come back at the same person if you passed them with your side guilds full – only while the option
  is above 4. In saves from before 1.3.0 the fix adds these conversations when the save is loaded.
- The Beliar shrine reward and Mario's rise to knight treat four or more side guilds the way they treated exactly four.
- What rules each other out (bandits or guards, guards or royal guard, militia, paladins) stays as it is.
- Checked against the real script of the mod (`Test\nebengilden_test.py`: 25 places in 24 functions, with the option at 4 the
  same as the original; `Test\skript_test.py`: both script files against the mod's compiled scripts) and in the running game
  with a save from 1.2.0: all places changed, the four conversations added, the menu line there, and Dragomir's join condition
  following a change of the option at once. Not tried yet: the menu on screen and the second chances in conversation.
- The tests now also find the mod's scripts directly in `Data` (not only in `Data\ModVDF`).

## 1.2.0 – Blood splatter back

- **Keeps the blood splatter.** 1.1.0 stopped the crash by cutting the mod's own call of the blood splatter. Because LeGo 2.9
  shows its splatter before the mod has worked out the damage, you then hardly saw any. 1.2.0 gives the mod's old blood splatter
  function (from LeGo 2.5) back the first instruction that the Union Toolkit had replaced with a jump to LeGo 2.9. The mod's damage
  function calls that function again: splatter for the damage actually dealt, no loop, no crash.
- If the code does not look as expected, the fix falls back to what 1.1.0 did – no crash, but hardly any splatter.
- No global script variable any more (a co-op mod would have sent it to the other player).
- Checked against the real script of the mod (`Test\blut_test.py`, now with the Toolkit's jump rebuilt) and in the running game:
  a staged hit from a bow came back without a loop, the mod dealt its damage, and the splatter showed exactly that damage.

## 1.1.0 – Blood splatter crash

- **Fixes a crash when arrows hit you with blood splatter on.** It happens when the Union Toolkit (`Data\Toolkit.vdf`, brought
  along by several Union plugins) replaces the mod's LeGo 2.5 with LeGo 2.9: the blood splatter and the mod's damage function
  then keep calling each other once a hit from a bow or crossbow leaves your health unchanged or takes just one point.
- The pointer fix from 1.0.0 is unchanged; both now live in one script, `XERES_FIXES.D`.
- Checked against the real script of the mod (`Test\blut_test.py`) and in the running game: the loop was there, and the fix
  removes it.

## 1.0.0 – Pointer checks above 2 GB

- **Fixes 20 places in Xeres' Rückkehr 1.0.9** where the scripts treat a valid object as missing because its address lies above
  2 GB: world changes via shrine, obelisk, runes, scrolls, stone circle tablets and Xardas' ring (wrong destination or crash),
  the pass into the Valley of Mines, the two doors of the spider burrow after Vino's conversation, the mine carts in the ice mine,
  taking items out of chests and removing objects.
- Covers everything the earlier teleport fix of 17 October 2026 did (world changes and the pass); both can be installed together.
- Checked against the real script of the mod (`Test\zeiger_test.py`) and confirmed in the game: all 20 places get changed.
