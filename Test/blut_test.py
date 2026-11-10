"""blut_test.py --spiel <Xeres-Ordner> | --dat <GOTHIC.DAT> - prueft den Blutspritzer-Fix aus XERES_FIXES.D am echten Skript.

Holt GOTHIC.DAT aus Data\\ModVDF\\Xeres_Scripts_DE.mod (oder nimmt --dat), liest Funktion und Laenge aus
Quelltext\\SYSTEM\\AUTORUN\\XERES_FIXES.D (XRFIX_BlutFunktion) und spielt die Umstellung Befehl fuer Befehl nach: jeder Aufruf
von _B_HeroDamage (CALL <Anfang von _B_HERODAMAGE>) wird ein Sprung auf den naechsten Befehl (JMP <Adresse + 5>).
Prueft: genau ein Aufruf, nur dessen 5 Bytes veraendert, der Sprung zeigt auf den naechsten Befehl, ein zweiter Lauf findet
nichts mehr. Das Union-Toolkit (LeGo 2.9), das die Umstellung im Spiel erst ausloest, gehoert nicht zur Mod - der Test nimmt es
als vorhanden an. Nur lesen."""
import argparse, os, re, struct, sys

HIER = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HIER)
from zeiger_test import vdf_datei, lade   # noqa: E402

SKRIPT = os.path.join(HIER, '..', 'Quelltext', 'SYSTEM', 'AUTORUN', 'XERES_FIXES.D')
ERWARTET = 1


def laenge(op):
    if op in (61, 62, 64, 65, 67, 75, 76, 80):
        return 5
    return 6 if op == 245 else 1


def inhalt(syms, index, name):
    i = index.get(name)
    if i is None or not isinstance(syms[i]['content'], int):
        return -1
    return syms[i]['content']


def aufloesen(code, ziel):
    """wie XRFIX_Aufloesen: einem Sprung am Anfang des Ziels folgen (Union-Toolkit), hoechstens 4-mal"""
    for _ in range(4):
        if ziel < 0 or ziel + 5 > len(code) or code[ziel] != 75:
            break
        ziel = struct.unpack_from('<i', code, ziel + 1)[0]
    return ziel


def patch(code, syms, name, lg):
    """wie XRFIX_BlutFunktion im Skript; gibt die umgestellten Stellen (Abstand zum Funktionsanfang) zurueck"""
    index = {s['name']: i for i, s in enumerate(syms)}
    start = inhalt(syms, index, name + '_OLD')
    if start < 0:
        start = inhalt(syms, index, name)
    if start < 0:
        return []
    z1, z2 = inhalt(syms, index, '_B_HERODAMAGE'), inhalt(syms, index, '_B_HERODAMAGE_OLD')
    stellen = []
    q = 0
    while q < lg - 4:
        op = code[start + q]
        if op == 61:
            ziel = aufloesen(code, struct.unpack_from('<i', code, start + q + 1)[0])
            if (ziel == z1 and z1 >= 0) or (ziel == z2 and z2 >= 0):
                code[start + q] = 75
                struct.pack_into('<i', code, start + q + 1, start + q + 5)
                stellen.append(q)
        q += laenge(op)
    return stellen


def main():
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument('--spiel')
    g.add_argument('--dat')
    a = ap.parse_args()
    if a.dat:
        roh = open(a.dat, 'rb').read()
    else:
        roh = vdf_datei(os.path.join(a.spiel, 'Data', 'ModVDF', 'Xeres_Scripts_DE.mod'), 'GOTHIC.DAT')
        if roh is None:
            sys.exit('GOTHIC.DAT nicht in Xeres_Scripts_DE.mod gefunden')
    m = re.search(r'XRFIX_BlutFunktion\("([A-Z0-9_]+)",\s*(\d+)\)', open(SKRIPT, encoding='latin-1').read())
    if not m:
        sys.exit('XRFIX_BlutFunktion nicht im Skript gefunden')
    name, lg = m.group(1), int(m.group(2))
    syms, code = lade(roh)
    vorher = bytes(code)
    stellen = patch(code, syms, name, lg)
    fehler = 0
    print('%s (%d Bytes): umgestellte Aufrufe von _B_HeroDamage: %d (erwartet %d) %s' % (name, lg, len(stellen), ERWARTET, stellen))
    if len(stellen) != ERWARTET:
        print('FEHLER: Anzahl der Stellen'); fehler += 1
    index = {s['name']: i for i, s in enumerate(syms)}
    start = inhalt(syms, index, name)
    anders = [i for i in range(len(code)) if code[i] != vorher[i]]
    erlaubt = {start + q + k for q in stellen for k in range(5)}
    if not set(anders) <= erlaubt:
        print('FEHLER: andere Bytes veraendert (%d)' % len(set(anders) - erlaubt)); fehler += 1
    for q in stellen:
        p = start + q
        if code[p] != 75 or struct.unpack_from('<i', code, p + 1)[0] != p + 5:
            print('FEHLER: kein Sprung auf den naechsten Befehl bei +%d' % q); fehler += 1
        else:
            print('  +%d: CALL _B_HeroDamage -> JMP %d (naechster Befehl)' % (q, p + 5))
    zweiter = patch(code, syms, name, lg)
    if zweiter:
        print('FEHLER: zweiter Lauf fand noch %d Stellen' % len(zweiter)); fehler += 1
    else:
        print('zweiter Lauf: nichts mehr umzustellen')

    # wie im Spiel mit dem Union-Toolkit: neues _B_HeroDamage hinten angehaengt, am alten Anfang ein Sprung dorthin, kein _OLD -
    # B_AssessDamage_Hero ruft weiter den alten Anfang auf
    syms2, code2 = lade(roh)
    alt = inhalt(syms2, {s['name']: i for i, s in enumerate(syms2)}, '_B_HERODAMAGE')
    neu = len(code2)
    code2 += bytes([60])                       # RET als neuer Code
    code2[alt] = 75
    struct.pack_into('<i', code2, alt + 1, neu)
    syms2[[s['name'] for s in syms2].index('_B_HERODAMAGE')]['content'] = neu
    stellen2 = patch(code2, syms2, name, lg)
    print('mit Union-Toolkit (Sprung am alten Anfang): umgestellte Aufrufe %d (erwartet %d)' % (len(stellen2), ERWARTET))
    if stellen2 != stellen:
        print('FEHLER: mit Sprung am alten Anfang nicht dieselbe Stelle'); fehler += 1
    print('ERGEBNIS: %s' % ('OK' if not fehler else '%d FEHLER' % fehler))
    sys.exit(1 if fehler else 0)


if __name__ == '__main__':
    main()
