# Changes

> *Deutsche Fassung: [CHANGELOG.de.md](CHANGELOG.de.md).*

## 1.0.0 – Pointer checks above 2 GB

- **Fixes 20 places in Xeres' Rückkehr 1.0.9** where the scripts treat a valid object as missing because its address lies above
  2 GB: world changes via shrine, obelisk, runes, scrolls, stone circle tablets and Xardas' ring (wrong destination or crash),
  the pass into the Valley of Mines, the two doors of the spider burrow after Vino's conversation, the mine carts in the ice mine,
  taking items out of chests and removing objects.
- Covers everything the earlier teleport fix of 17 October 2026 did (world changes and the pass); both can be installed together.
- Checked against the real script of the mod (`Test\zeiger_test.py`); not yet played in the game.
