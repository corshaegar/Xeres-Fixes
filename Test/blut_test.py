"""blut_test.py --spiel <Xeres-Ordner> | --dat <GOTHIC.DAT> - prueft den Blutspritzer-Fix aus XERES_FIXES.D am echten Skript.

Holt GOTHIC.DAT aus Data\\ModVDF\\Xeres_Scripts_DE.mod (oder nimmt --dat), liest Funktion und Laenge aus
Quelltext\\SYSTEM\\AUTORUN\\XERES_FIXES.D (XRFIX_BlutFunktion) und spielt den Fix Befehl fuer Befehl nach (gleiche Regeln wie
XRFIX_BlutFunktion/XRFIX_BlutAlt):

1. Wie im Spiel mit dem Union-Toolkit (LeGo 2.9): neues _B_HeroDamage hinten angehaengt, am alten Anfang ein Sprung dorthin, kein
   _OLD - B_AssessDamage_Hero ruft weiter den alten Anfang auf. Erwartet: genau ein Aufruf; der alte Anfang bekommt seinen ersten
   Befehl zurueck und ist danach Byte fuer Byte wie im Original-Skript; der Aufruf selbst und alles andere bleibt; ein zweiter Lauf
   findet nichts mehr.
2. Rueckfall (kein Sprung am alten Anfang, Muster unbekannt): der Aufruf wird ein Sprung auf den naechsten Befehl, nur diese 5 Bytes.

Das Union-Toolkit gehoert nicht zur Mod - der Test baut seinen Sprung nach. Nur lesen."""
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


def alt_da(code, index, ziel):
    """wie XRFIX_BlutAlt: Sprung am Anfang, dahinter PUSHVAR C_NPC.ATTRIBUTE, PUSHVAR HERO_LASTHP, SUB"""
    if ziel < 0 or ziel + 16 > len(code) or code[ziel] != 75:
        return False
    if code[ziel + 5] != 65 or struct.unpack_from('<i', code, ziel + 6)[0] != index.get('C_NPC.ATTRIBUTE', -2):
        return False
    if code[ziel + 10] != 65 or struct.unpack_from('<i', code, ziel + 11)[0] != index.get('HERO_LASTHP', -2):
        return False
    return code[ziel + 15] == 1 and 'HERO' in index


def patch(code, syms, name, lg):
    """wie XRFIX_BlutFunktion; gibt (Stelle im Skriptcode, 'wieder'|'sprung', alter Anfang) je Aufruf zurueck"""
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
            direkt = struct.unpack_from('<i', code, start + q + 1)[0]
            ziel = aufloesen(code, direkt)
            if (ziel == z1 and z1 >= 0) or (ziel == z2 and z2 >= 0):
                if direkt != ziel and alt_da(code, index, direkt):
                    code[direkt] = 80
                    struct.pack_into('<i', code, direkt + 1, index['HERO'])
                    stellen.append((start + q, 'wieder', direkt))
                else:
                    code[start + q] = 75
                    struct.pack_into('<i', code, start + q + 1, start + q + 5)
                    stellen.append((start + q, 'sprung', direkt))
        q += laenge(op)
    return stellen


def mit_toolkit(roh):
    """Skript wie im Spiel mit dem Union-Toolkit: neuer Code fuer _B_HeroDamage hinten, am alten Anfang ein Sprung dorthin"""
    syms, code = lade(roh)
    index = {s['name']: i for i, s in enumerate(syms)}
    alt = inhalt(syms, index, '_B_HERODAMAGE')
    neu = len(code)
    code += bytes([60])                       # RET als neuer Code
    code[alt] = 75
    struct.pack_into('<i', code, alt + 1, neu)
    syms[index['_B_HERODAMAGE']]['content'] = neu
    return syms, code, alt


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
    fehler = 0
    _, original = lade(roh)

    # 1. mit Union-Toolkit
    syms, code, alt = mit_toolkit(roh)
    vorher = bytes(code)
    stellen = patch(code, syms, name, lg)
    print('%s (%d Bytes), mit Union-Toolkit: Aufrufe von _B_HeroDamage %d (erwartet %d) %s' % (name, lg, len(stellen), ERWARTET, stellen))
    if len(stellen) != ERWARTET or any(s[1] != 'wieder' or s[2] != alt for s in stellen):
        print('FEHLER: erwartet genau einen Aufruf, alter Anfang %d wiederhergestellt' % alt); fehler += 1
    anders = {i for i in range(len(code)) if code[i] != vorher[i]}
    if not anders or not anders <= set(range(alt, alt + 5)):   # gleiche Bytes in Sprungziel und Symbolnummer bleiben stehen
        print('FEHLER: veraenderte Bytes %s statt nur der 5 am alten Anfang' % sorted(anders)[:12]); fehler += 1
    if bytes(code[alt:alt + 119]) != bytes(original[alt:alt + 119]):
        print('FEHLER: alter Anfang nicht wie im Original-Skript'); fehler += 1
    else:
        print('  alter Anfang %d: erster Befehl wieder SETINST HERO - Funktion Byte fuer Byte wie im Original (119 Bytes)' % alt)
    for p, art, d in stellen:
        if code[p] != 61 or struct.unpack_from('<i', code, p + 1)[0] != alt:
            print('FEHLER: Aufruf bei %d nicht mehr CALL %d' % (p, alt)); fehler += 1
        else:
            print('  Aufruf bei %d bleibt: CALL %d (alte Blutspritzer-Funktion, ruft nichts zurueck)' % (p, alt))
    zweiter = patch(code, syms, name, lg)
    if zweiter:
        print('FEHLER: zweiter Lauf fand noch %d Stellen' % len(zweiter)); fehler += 1
    else:
        print('zweiter Lauf: nichts mehr zu tun')

    # 2. Rueckfall ohne Sprung am alten Anfang (Original-Skript, als ob es schon verketten wuerde)
    syms2, code2 = lade(roh)
    vorher2 = bytes(code2)
    stellen2 = patch(code2, syms2, name, lg)
    print('Rueckfall ohne Sprung am alten Anfang: Aufrufe %d (erwartet %d) %s' % (len(stellen2), ERWARTET, stellen2))
    if len(stellen2) != ERWARTET or any(s[1] != 'sprung' for s in stellen2):
        print('FEHLER: Rueckfall nicht als Sprung'); fehler += 1
    anders2 = {i for i in range(len(code2)) if code2[i] != vorher2[i]}
    erlaubt2 = {p + k for p, _, _ in stellen2 for k in range(5)}
    if not anders2 <= erlaubt2:
        print('FEHLER: andere Bytes veraendert (%d)' % len(anders2 - erlaubt2)); fehler += 1
    for p, _, _ in stellen2:
        if code2[p] != 75 or struct.unpack_from('<i', code2, p + 1)[0] != p + 5:
            print('FEHLER: kein Sprung auf den naechsten Befehl bei %d' % p); fehler += 1
        else:
            print('  %d: CALL _B_HeroDamage -> JMP %d (naechster Befehl)' % (p, p + 5))
    print('ERGEBNIS: %s' % ('OK' if not fehler else '%d FEHLER' % fehler))
    sys.exit(1 if fehler else 0)


if __name__ == '__main__':
    main()
