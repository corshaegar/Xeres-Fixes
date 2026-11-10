# Changes

> *Deutsche Fassung: [CHANGELOG.de.md](CHANGELOG.de.md).*

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
