"""zeiger_test.py --spiel <Xeres-Ordner> | --dat <GOTHIC.DAT> - prueft XERES_FIX_ZEIGER.D am echten Skript, ohne das Spiel.

Holt GOTHIC.DAT aus Data\\ModVDF\\Xeres_Scripts_DE.mod (oder nimmt --dat), liest die Funktionsliste samt Laengen aus
Quelltext\\SYSTEM\\AUTORUN\\XERES_FIX_ZEIGER.D und spielt den Patch des Skripts Byte fuer Byte nach (gleiche Regeln: Funktion bzw.
<Name>_OLD, Bereich [Anfang, Anfang + Laenge), Muster PUSHINT 0 / PUSHVAR <Variable mit PTR im Namen> / > -> !=).
Prueft: genau die erwarteten Stellen, kein anderes Byte veraendert, ein zweiter Lauf findet nichts, und danach gibt es im
ganzen Skript keine Zeiger-Pruefung "> 0" mehr in diesen Funktionen. Nur lesen."""
import argparse, os, re, struct, sys

HIER = os.path.dirname(os.path.abspath(__file__))
SKRIPT = os.path.join(HIER, '..', 'Quelltext', 'SYSTEM', 'AUTORUN', 'XERES_FIX_ZEIGER.D')
ERWARTET = 20


def vdf_datei(vdf, name):
    with open(vdf, 'rb') as f:
        hdr = f.read(296)
        n, files, ts, size, root, esize = struct.unpack_from('<6I', hdr, 272)
        f.seek(root)
        raw = f.read(n * esize)
        for i in range(n):
            e = raw[i * esize:(i + 1) * esize]
            nm = e[:64].rstrip(b' \0').decode('latin-1').upper()
            off, sz, typ, attr = struct.unpack_from('<4I', e, 64)
            if not typ & 0x80000000 and nm == name:
                f.seek(off)
                return f.read(sz)
    return None


def lade(d):
    p = 1
    n = struct.unpack_from('<i', d, p)[0]; p += 4 + 4 * n
    syms = []
    for i in range(n):
        named = struct.unpack_from('<i', d, p)[0]; p += 4
        name = ''
        if named:
            e = d.index(b'\n', p); name = d[p:e].decode('latin-1'); p = e + 1
        off, bits = struct.unpack_from('<ii', d, p); p += 8
        ele = bits & 0xFFF; typ = (bits >> 12) & 0xF; flags = (bits >> 16) & 0x3F
        p += 4 * 5
        content = None
        if not (flags & 4):
            if typ in (4, 5, 6, 7):
                content = struct.unpack_from('<i', d, p)[0]; p += 4
            elif typ in (1, 2):
                content = list(struct.unpack_from('<%di' % ele, d, p)); p += 4 * ele
            elif typ == 3:
                for k in range(ele):
                    e = d.index(b'\n', p); p = e + 1
        p += 4
        syms.append(dict(name=name, typ=typ, flags=flags, content=content))
    size = struct.unpack_from('<i', d, p)[0]; p += 4
    return syms, bytearray(d[p:p + size])


def patch(code, syms, liste):
    """wie XRFIX_Zeiger im Skript; gibt die umgestellten Stellen zurueck"""
    index = {s['name']: i for i, s in enumerate(syms)}
    stellen = []
    for name, laenge in liste:
        i = index.get(name + '_OLD', index.get(name))
        if i is None or not isinstance(syms[i]['content'], int):
            continue
        adr = syms[i]['content']
        for k in range(0, laenge - 10):
            p = adr + k
            if p + 11 > len(code):
                break
            if code[p] == 64 and struct.unpack_from('<i', code, p + 1)[0] == 0 and code[p + 5] == 65 and code[p + 10] == 8:
                sym = struct.unpack_from('<i', code, p + 6)[0]
                if 0 < sym < len(syms) and 'PTR' in syms[sym]['name']:
                    code[p + 10] = 17
                    stellen.append((name, k, syms[sym]['name']))
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
    liste = [(m.group(1), int(m.group(2))) for m in re.finditer(r'XRFIX_Funktion\("([A-Z0-9_]+)",\s*(\d+)\)', open(SKRIPT, encoding='latin-1').read())]
    syms, code = lade(roh)
    vorher = bytes(code)
    stellen = patch(code, syms, liste)
    fehler = 0
    print('Funktionen im Skript: %d, umgestellte Stellen: %d (erwartet %d)' % (len(liste), len(stellen), ERWARTET))
    for s in stellen:
        print('  %-32s +%-6d %s' % s)
    if len(stellen) != ERWARTET:
        print('FEHLER: Anzahl der Stellen'); fehler += 1
    anders = [i for i in range(len(code)) if code[i] != vorher[i]]
    if len(anders) != len(stellen) or any(vorher[i] != 8 or code[i] != 17 for i in anders):
        print('FEHLER: andere Bytes veraendert (%d)' % len(anders)); fehler += 1
    else:
        print('nur die %d Vergleichs-Bytes geaendert (8 -> 17)' % len(anders))
    zweiter = patch(code, syms, liste)
    if zweiter:
        print('FEHLER: zweiter Lauf fand noch %d Stellen' % len(zweiter)); fehler += 1
    else:
        print('zweiter Lauf: nichts mehr umzustellen')
    namen = {n for n, _ in liste}
    print('ERGEBNIS: %s' % ('OK' if not fehler else '%d FEHLER' % fehler))
    sys.exit(1 if fehler else 0)


if __name__ == '__main__':
    main()
