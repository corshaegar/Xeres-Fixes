"""gegnerki_test.py --spiel <Xeres-Ordner> - prueft die einstellbare Gegner-KI aus XERES_FIXES.D am echten Skript, ohne das Spiel.

Liest die Tabelle aus XRFIX_KiTabellen (XRFIX_KiBlock(nb, Taktik, Lage, XRFIX_KiZuege(6 neue Zuege), XRFIX_KiZuege(6 Zuege
Xeres))) und Xeres' FIGHT.DAT (Xeres_Scripts.mod). Prueft:
  - die Tabelle ist die, die Werkzeuge\\gegnerki_regeln.py mit seinen Regeln aus Xeres' Tabellen erzeugt;
  - die Instanzen FA_<Lage>_<Taktik> setzen nur Zuege (keine Aufrufe, keine Prototypen) - so liest das Werkzeug sie richtig;
  - jede Zeile nennt fuer Xeres genau die Zuege aus Xeres' FIGHT.DAT (sonst schaltete der Fix diese Lage im Spiel nie um),
    jede Lage nur einmal, Taktik 0-49, Lage 0-18, jeder Zug 0-31;
  - Umschalten wie im Spiel (XRFIX_KiGleich/XRFIX_KiSchreiben, Anzahl wie oSActionBlock::InitBlock bis zum ersten leeren Zug) an
    einer nachgebauten Liste: auf New Balance aendert genau die Lagen der Tabelle, ein zweiter Lauf nichts, zurueck auf Xeres
    ergibt Byte fuer Byte wieder die Liste, die Gothic aus Xeres' FIGHT.DAT laedt;
  - DAUERFUNC_01: die Laenge im Skript ist die Groesse der Funktion, darin steht genau einmal "CALL STR_ToInt; PUSHVAR
    TimeSwitch; ASSIGN"; der Umbau aendert nur die 4 Bytes des Aufrufziels, ein zweiter Lauf findet nichts - auch mit dem
    Union-Toolkit nachgebaut (STR_ToInt zeigt auf neuen Code, am alten Anfang steht ein Sprung dorthin, wie im Spiel gemessen).
Nur lesen."""
import argparse, os, re, struct, sys

HIER = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HIER)
sys.path.insert(0, os.path.join(HIER, '..', 'Werkzeuge'))
from zeiger_test import skript_datei, lade, vdf_datei   # noqa: E402
from nebengilden_test import code_symbole, laenge      # noqa: E402
import gegnerki_regeln as regeln                        # noqa: E402

SKRIPT = os.path.join(HIER, '..', 'Quelltext', 'SYSTEM', 'AUTORUN', 'XERES_FIXES.D')
TAKTIKEN, LAGEN = 50, 19
CALL, PUSHVAR, ASSIGN, JMP, RET = 61, 65, 9, 75, 60


def packen(z):
    return z[0] | (z[1] << 5) | (z[2] << 10) | (z[3] << 15) | (z[4] << 20) | (z[5] << 25)


def entpacken(p):
    return [(p >> (5 * k)) & 31 for k in range(6)]


def anzahl(z):
    for k, w in enumerate(z):
        if w == 0:
            return k
    return 6


def luecke(z):
    """steht hinter dem ersten leeren Zug noch einer? (Gothic waehlt ihn nie)"""
    return any(z[anzahl(z):])


def liste_wie_gothic(fight):
    """{(Taktik, Lage): [6 Zuege, Anzahl]} wie oCNpc::InitFightAI: fehlt die Instanz, bleibt die Lage leer"""
    out = {}
    for t in range(TAKTIKEN):
        for s, lage in enumerate(regeln.LAGEN):
            z = list(fight.get('FA_%s_%d' % (lage, t), [0] * 6))
            out[(t, s)] = z + [anzahl(z)]
    return out


def umschalten(liste, tabelle, nb):
    """wie XRFIX_KiTabellen(nb) mit XRFIX_KiBlock; Zahl der umgestellten Lagen"""
    n = 0
    for t, s, nb_p, xr_p in tabelle:
        block = liste[(t, s)]
        alt, neu = (xr_p, nb_p) if nb else (nb_p, xr_p)
        if block[:6] == entpacken(alt):
            z = entpacken(neu)
            liste[(t, s)] = z + [anzahl(z)]
            n += 1
    return n


def nur_zuege(roh):
    """Instanzen FA_*, deren Code mehr tut als Zuege zu setzen (Befehle ausser PUSHINT/PUSHVAR/PUSHARRAYVAR/ASSIGN/RET)"""
    syms, code = lade(roh)
    andere = []
    for name, a, e in code_symbole(syms, code):
        if not name.startswith('FA_'):
            continue
        q = a
        while q < e:
            op = code[q]
            if op not in (64, 65, 245, 9, 60):
                andere.append((name, op)); break
            q += laenge(op)
    return andere


def aufloesen(code, ziel):
    """wie XRFIX_Aufloesen: steht am Ziel ein Sprung (so ersetzt das Union-Toolkit Funktionen), ihm folgen - hoechstens 4-mal"""
    for _ in range(4):
        if 0 <= ziel < len(code) and code[ziel] == JMP:
            ziel = struct.unpack_from('<i', code, ziel + 1)[0]
        else:
            break
    return ziel


def dauerfunc(syms, code, lg, aufruf, inhalt=None):
    """wie XRFIX_KiTaktEinbauen("DAUERFUNC_01", lg); gibt Anfang der Funktion und Abstaende der umgestellten Aufrufe zurueck.
    inhalt: Symbolinhalte, die im Spiel anders sind als im DAT (Union-Toolkit)"""
    index = {s['name'].upper(): i for i, s in enumerate(syms)}
    inhalt = inhalt or {}

    def von(n):
        if n in inhalt:
            return inhalt[n]
        return syms[index[n]]['content'] if n in index else -1
    i = index.get('DAUERFUNC_01_OLD', index.get('DAUERFUNC_01'))
    start = syms[i]['content']
    z1 = aufloesen(code, von('STR_TOINT'))
    z2 = aufloesen(code, von('STR_TOINT_OLD'))
    schalter = index['TIMESWITCH']
    stellen = []
    q = 0
    while q < lg - 10:
        p = start + q
        op = code[p]
        if op == CALL:
            ziel = aufloesen(code, struct.unpack_from('<i', code, p + 1)[0])
            if (ziel == z1 or (ziel == z2 and z2 >= 0)) and code[p + 5] == PUSHVAR and \
                    struct.unpack_from('<i', code, p + 6)[0] == schalter and code[p + 10] == ASSIGN:
                struct.pack_into('<i', code, p + 1, aufruf)
                stellen.append(q)
        q += laenge(op)
    return start, stellen


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--spiel', required=True)
    a = ap.parse_args()
    fehler = 0
    text = open(SKRIPT, encoding='latin-1').read()
    tabelle = []
    for m in re.finditer(r'XRFIX_KiBlock\(nb, (\d+), (\d+), XRFIX_KiZuege\(([\d, ]+)\), XRFIX_KiZuege\(([\d, ]+)\)\)', text):
        t, s = int(m.group(1)), int(m.group(2))
        nbz = [int(x) for x in m.group(3).split(',')]
        xrz = [int(x) for x in m.group(4).split(',')]
        if len(nbz) != 6 or len(xrz) != 6 or not all(0 <= w < 32 for w in nbz + xrz):
            print('FEHLER: Zeile fuer Taktik %d, Lage %d: Zuege %s / %s' % (t, s, nbz, xrz)); fehler += 1; continue
        tabelle.append((t, s, packen(nbz), packen(xrz)))
    print('Tabelle in XRFIX_KiTabellen: %d Lagen in %d Taktiken' % (len(tabelle), len({t for t, _, _, _ in tabelle})))
    if not tabelle:
        print('FEHLER: keine Tabelle gefunden'); fehler += 1
    schluessel = [(t, s) for t, s, _, _ in tabelle]
    if len(set(schluessel)) != len(schluessel):
        print('FEHLER: eine Lage steht doppelt in der Tabelle'); fehler += 1
    if not all(0 <= t < TAKTIKEN and 0 <= s < LAGEN for t, s in schluessel):
        print('FEHLER: Taktik oder Lage ausserhalb'); fehler += 1

    fight_roh = vdf_datei(os.path.join(a.spiel, 'Data', 'Xeres_Scripts.mod'), 'FIGHT.DAT')
    if fight_roh is None:
        sys.exit('FIGHT.DAT nicht in Data\\Xeres_Scripts.mod gefunden')
    andere = nur_zuege(fight_roh)
    if andere:
        print('FEHLER: FA-Instanzen mit anderen Befehlen: %s' % andere[:5]); fehler += 1
    else:
        print('Xeres FIGHT.DAT: alle FA-Instanzen setzen nur Zuege')
    fight = regeln.tabellen(fight_roh)
    gothic = liste_wie_gothic(fight)
    falsch = [(t, s, entpacken(x), gothic[(t, s)][:6]) for t, s, _, x in tabelle if gothic.get((t, s), [None])[:6] != entpacken(x)]
    if falsch:
        print('FEHLER: %d Zeilen nennen andere Xeres-Zuege als FIGHT.DAT, z. B. %s' % (len(falsch), falsch[:3])); fehler += 1
    else:
        print('alle %d Zeilen nennen fuer Xeres die Zuege aus FIGHT.DAT' % len(tabelle))

    liste = {k: list(v) for k, v in gothic.items()}
    n1 = umschalten(liste, tabelle, True)
    n2 = umschalten(liste, tabelle, True)
    nb_ok = all(liste[(t, s)][:6] == entpacken(p) for t, s, p, _ in tabelle)
    geaendert = {k for k in liste if liste[k] != gothic[k]}
    print('auf New Balance: %d Lagen umgestellt, zweiter Lauf %d; geaendert %d Lagen' % (n1, n2, len(geaendert)))
    if n1 != len(tabelle) or n2 != 0 or not nb_ok or not geaendert <= set(schluessel):
        print('FEHLER: Umschalten auf New Balance'); fehler += 1
    n3 = umschalten(liste, tabelle, False)
    n4 = umschalten(liste, tabelle, False)
    print('zurueck auf Xeres: %d Lagen umgestellt, zweiter Lauf %d; Liste wie aus FIGHT.DAT: %s' % (n3, n4, liste == gothic))
    if n3 != len(tabelle) or n4 != 0 or liste != gothic:
        print('FEHLER: Umschalten zurueck auf Xeres'); fehler += 1
    leer = [(t, s) for t, s, p, _ in tabelle if anzahl(entpacken(p)) == 0]
    luecken = [(t, s, f) for t, s, p, x in tabelle for f, z in (('NB', p), ('Xeres', x)) if luecke(entpacken(z))]
    print('Lagen, die die neue Fassung leer laesst: %s; Zuege hinter einem leeren (nie gewaehlt): %s' % (leer, luecken))
    if leer:
        print('FEHLER: leere Lagen - was Gothic dann tut, ist nicht festgelegt'); fehler += 1

    roh = skript_datei(a.spiel)
    if roh is None:
        sys.exit('GOTHIC.DAT nicht in Xeres_Scripts_DE.mod gefunden (Data\\ModVDF oder Data)')
    syms, code = lade(roh)
    m = re.search(r'XRFIX_KiTaktEinbauen\("DAUERFUNC_01", (\d+)\)', text)
    lg = int(m.group(1)) if m else 0
    groesse = {n: e - s for n, s, e in code_symbole(syms, code)}
    if groesse.get('DAUERFUNC_01') != lg:
        print('FEHLER: DAUERFUNC_01 ist %s Bytes gross, im Skript steht %d' % (groesse.get('DAUERFUNC_01'), lg)); fehler += 1
    aufruf = len(code)   # XRFIX_KiTakt: zParserExtender haengt den Code hinter den der Mod
    vorher = bytes(code)
    start, stellen = dauerfunc(syms, code, lg, aufruf)
    anders = [i for i in range(len(code)) if code[i] != vorher[i]]
    _, zweiter = dauerfunc(syms, code, lg, aufruf)
    print('DAUERFUNC_01: %d Bytes, Aufruf von STR_ToInt vor TimeSwitch bei %s, %d Bytes geaendert, zweiter Lauf %d'
          % (lg, ['+%d' % q for q in stellen], len(anders), len(zweiter)))
    # geaendert ist nur das Aufrufziel (4 Bytes; gleiche Bytes von altem und neuem Ziel bleiben), und es zeigt auf XRFIX_KiTakt
    ok = (len(stellen) == 1 and not zweiter and anders and
          set(anders) <= set(range(start + stellen[0] + 1, start + stellen[0] + 5)) and
          struct.unpack_from('<i', code, start + stellen[0] + 1)[0] == aufruf and code[start + stellen[0]] == CALL)
    if not ok:
        print('FEHLER: Umbau in DAUERFUNC_01'); fehler += 1
    # Union-Toolkit wie im Spiel gemessen (13.11.2026): STR_ToInt zeigt auf neuen Code hinter dem der Mod, am alten Anfang steht
    # ein Sprung dorthin, der Aufruf in DAUERFUNC_01 zeigt weiter auf den alten Anfang
    code2 = bytearray(vorher)
    alt = syms[[s['name'].upper() for s in syms].index('STR_TOINT')]['content']
    neu = len(code2)
    code2 += bytes([RET])
    code2[alt] = JMP
    struct.pack_into('<i', code2, alt + 1, neu)
    _, stellen2 = dauerfunc(syms, code2, lg, aufruf, {'STR_TOINT': neu})
    print('mit Union-Toolkit (STR_ToInt bei %d, am alten Anfang %d ein Sprung dorthin): Aufruf bei %s'
          % (neu, alt, ['+%d' % q for q in stellen2]))
    if stellen2 != stellen:
        print('FEHLER: mit dem Union-Toolkit findet der Umbau den Aufruf nicht'); fehler += 1

    soll = [(b['taktik'], b['lage'], packen(b['neu']), packen(b['xr'])) for b in regeln.bloecke(a.spiel)]
    print('Regeln (Werkzeuge\\gegnerki_regeln.py): %d Lagen, gleich der Tabelle im Skript: %s' % (len(soll), soll == tabelle))
    if soll != tabelle:
        print('FEHLER: Tabelle im Skript passt nicht zu den Regeln - Werkzeuge\\gegnerki_regeln.py --schreiben'); fehler += 1
    print('ERGEBNIS: %s' % ('OK' if not fehler else '%d FEHLER' % fehler))
    sys.exit(1 if fehler else 0)


if __name__ == '__main__':
    main()
