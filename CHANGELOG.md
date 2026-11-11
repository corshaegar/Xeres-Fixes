# Changes

> *Deutsche Fassung: [CHANGELOG.de.md](CHANGELOG.de.md).*

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
