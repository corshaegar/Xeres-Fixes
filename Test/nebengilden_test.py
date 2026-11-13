"""nebengilden_test.py --spiel <Xeres-Ordner> | --dat <GOTHIC.DAT> - prueft die einstellbare Nebengilden-Grenze aus
XERES_FIXES.D am echten Skript, ohne das Spiel.

Holt GOTHIC.DAT aus Xeres_Scripts_DE.mod (Data\\ModVDF oder Data, oder nimmt --dat), liest die Funktionsliste samt Laengen aus
XRFIX_Nebengilden (XRFIX_NebengildenFunktion("NAME", LAENGE)) und spielt die Umstellung Befehl fuer Befehl nach (gleiche Regeln
wie XRFIX_NebengildenFunktion; XRFIX_MaxNebengilden liegt wie im Spiel hinter dem Skriptcode der Mod):
  PUSHVAR MaxNebengilden; PUSHVAR Mod_AnzahlNebengilden; < oder >=  ->  CALL XRFIX_MaxNebengilden
  PUSHVAR MaxNebengilden; PUSHVAR Mod_AnzahlNebengilden; ==         ->  PUSHINT 4; ...; >=
  PUSHINT 4;              PUSHVAR Mod_AnzahlNebengilden; ==         ->  ...; >=
Prueft: jede Laenge = Groesse der Funktion im Skript; die Liste deckt jede Stelle im ganzen Skript ab (danach bezieht sich kein
Befehl mehr auf MaxNebengilden und keiner vergleicht Mod_AnzahlNebengilden mit "== 4"); genau 25 Stellen (22 Aufrufe, 3
Vergleiche); nur diese Bytes geaendert; ein zweiter Lauf findet nichts; mit Grenze 4 entscheidet jede Stelle fuer 0 bis 4
Nebengilden wie das Original, mit hoeherer Grenze bleibt der Beitritt offen. Nur lesen."""
import argparse, os, re, struct, sys

HIER = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HIER)
from zeiger_test import skript_datei, lade   # noqa: E402

SKRIPT = os.path.join(HIER, '..', 'Quelltext', 'SYSTEM', 'AUTORUN', 'XERES_FIXES.D')
ERWARTET_AUFRUFE = 22
ERWARTET_VERGLEICHE = 3
PUSHINT, PUSHVAR, CALL, LT, EQ, GE = 64, 65, 61, 7, 16, 18
VGL = {LT: '<', EQ: '==', GE: '>='}


def laenge(op):
    if op in (61, 62, 64, 65, 67, 75, 76, 80):
        return 5
    return 6 if op == 245 else 1


def code_symbole(syms, code):
    """Anfang und Ende jeder Funktion/Instanz im Skriptcode (wie der Parser: Symbole mit Code, nach Anfang sortiert)"""
    st = sorted((s['content'], i) for i, s in enumerate(syms)
                if s['typ'] in (5, 6, 7) and (s['flags'] & 1) and not (s['flags'] & 8) and isinstance(s['content'], int)
                and 0 <= s['content'] < len(code))
    out = []
    for k, (a, i) in enumerate(st):
        e = st[k + 1][0] if k + 1 < len(st) else len(code)
        out.append((syms[i]['name'].upper(), a, e))
    return out


def stellen_im_skript(code, bereiche, grenze, anzahl):
    """alle Befehle im ganzen Skript, die MaxNebengilden lesen oder Mod_AnzahlNebengilden mit == 4 vergleichen"""
    gefunden = []
    for name, a, e in bereiche:
        q = a
        while q < e:
            op = code[q]
            if q + 11 <= len(code) and op in (PUSHVAR, PUSHINT):
                arg = struct.unpack_from('<i', code, q + 1)[0]
                if op == PUSHVAR and arg == grenze:
                    gefunden.append((name, q - a, 'MaxNebengilden'))
                elif (op == PUSHINT and arg == 4 and code[q + 5] == PUSHVAR and
                      struct.unpack_from('<i', code, q + 6)[0] == anzahl and code[q + 10] == EQ):
                    gefunden.append((name, q - a, '== 4'))
            q += laenge(op)
    return gefunden


def patch(code, syms, liste, aufruf):
    """wie XRFIX_NebengildenFunktion fuer jede Funktion der Liste; gibt (Funktion, Abstand, Art, Vergleich) zurueck"""
    index = {s['name'].upper(): i for i, s in enumerate(syms)}
    grenze, anzahl = index['MAXNEBENGILDEN'], index['MOD_ANZAHLNEBENGILDEN']
    stellen = []
    for name, lg in liste:
        i = index.get(name + '_OLD', index.get(name))
        if i is None or not isinstance(syms[i]['content'], int):
            continue
        start = syms[i]['content']
        q = 0
        while q < lg - 10:
            p = start + q
            op = code[p]
            if op in (PUSHVAR, PUSHINT) and code[p + 5] == PUSHVAR and struct.unpack_from('<i', code, p + 6)[0] == anzahl:
                wert = struct.unpack_from('<i', code, p + 1)[0]
                vgl = code[p + 10]
                if op == PUSHVAR and wert == grenze:
                    if vgl in (LT, GE):
                        code[p] = CALL
                        struct.pack_into('<i', code, p + 1, aufruf)
                        stellen.append((name, q, 'Aufruf', VGL[vgl]))
                    elif vgl == EQ:
                        code[p] = PUSHINT
                        struct.pack_into('<i', code, p + 1, 4)
                        code[p + 10] = GE
                        stellen.append((name, q, 'mindestens 4', '=='))
                elif op == PUSHINT and wert == 4 and vgl == EQ:
                    code[p + 10] = GE
                    stellen.append((name, q, 'mindestens 4', '=='))
            q += laenge(op)
    return stellen


def entscheidung(art, vgl, anzahl, grenze, original):
    """Ergebnis eines Vergleichs: Mod_AnzahlNebengilden <vgl> Grenze (original: Konstante 4, sonst die Einstellung)"""
    if art == 'Aufruf' or original:
        rechts = 4 if original else grenze
        if vgl == '<':
            return anzahl < rechts
        if vgl == '>=':
            return anzahl >= rechts
        return anzahl == rechts
    return anzahl >= 4   # "mindestens 4"


def main():
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument('--spiel')
    g.add_argument('--dat')
    a = ap.parse_args()
    if a.dat:
        roh = open(a.dat, 'rb').read()
    else:
        roh = skript_datei(a.spiel)
        if roh is None:
            sys.exit('GOTHIC.DAT nicht in Xeres_Scripts_DE.mod gefunden (Data\\ModVDF oder Data)')
    text = open(SKRIPT, encoding='latin-1').read()
    liste = [(m.group(1), int(m.group(2))) for m in re.finditer(r'XRFIX_NebengildenFunktion\("([A-Z0-9_]+)",\s*(\d+)\)', text)]
    syms, code = lade(roh)
    index = {s['name'].upper(): i for i, s in enumerate(syms)}
    fehler = 0
    for n in ('MAXNEBENGILDEN', 'MOD_ANZAHLNEBENGILDEN'):
        if n not in index:
            sys.exit('FEHLER: %s fehlt im Skript - andere Fassung von Xeres?' % n)
    s = syms[index['MAXNEBENGILDEN']]
    print('MaxNebengilden: Konstante %s, Wert %s' % (bool(s['flags'] & 1), s['content']))
    if not (s['flags'] & 1) or s['content'] != [4]:
        print('FEHLER: MaxNebengilden ist nicht die Konstante 4'); fehler += 1
    bereiche = code_symbole(syms, code)
    groesse = {n: e - a for n, a, e in bereiche}
    for name, lg in liste:
        if groesse.get(name) != lg:
            print('FEHLER: %s ist %s Bytes gross, im Skript steht %d' % (name, groesse.get(name), lg)); fehler += 1
    vorher_stellen = stellen_im_skript(code, bereiche, index['MAXNEBENGILDEN'], index['MOD_ANZAHLNEBENGILDEN'])
    ohne = sorted({n for n, _, _ in vorher_stellen} - {n for n, _ in liste})
    print('Funktionen in XRFIX_Nebengilden: %d; Funktionen mit der Grenze im ganzen Skript: %d'
          % (len(liste), len({n for n, _, _ in vorher_stellen})))
    if ohne:
        print('FEHLER: nicht in der Liste: %s' % ohne); fehler += 1

    aufruf = len(code)   # XRFIX_MaxNebengilden: zParserExtender haengt den Code hinter den der Mod
    vorher = bytes(code)
    stellen = patch(code, syms, liste, aufruf)
    aufrufe = [s for s in stellen if s[2] == 'Aufruf']
    vergleiche = [s for s in stellen if s[2] != 'Aufruf']
    print('Stellen: %d Aufrufe (erwartet %d), %d Vergleiche (erwartet %d)'
          % (len(aufrufe), ERWARTET_AUFRUFE, len(vergleiche), ERWARTET_VERGLEICHE))
    for st in stellen:
        print('  %-42s +%-6d %-13s war %s' % st)
    if len(aufrufe) != ERWARTET_AUFRUFE or len(vergleiche) != ERWARTET_VERGLEICHE:
        print('FEHLER: Anzahl der Stellen'); fehler += 1
    erlaubt = set()
    for name, q, art, _ in stellen:
        p = syms[index[name]]['content'] + q
        erlaubt |= set(range(p, p + 5)) | {p + 10}
    anders = {i for i in range(len(code)) if code[i] != vorher[i]}
    if not anders <= erlaubt:
        print('FEHLER: andere Bytes veraendert (%d)' % len(anders - erlaubt)); fehler += 1
    else:
        print('nur diese Befehle geaendert (%d Bytes)' % len(anders))
    rest = stellen_im_skript(code, bereiche, index['MAXNEBENGILDEN'], index['MOD_ANZAHLNEBENGILDEN'])
    if rest:
        print('FEHLER: danach noch %d Stellen: %s' % (len(rest), rest[:5])); fehler += 1
    else:
        print('danach: kein Befehl liest mehr MaxNebengilden, keiner prueft "== 4"')
    zweiter = patch(code, syms, liste, aufruf)
    if zweiter:
        print('FEHLER: zweiter Lauf fand noch %d Stellen' % len(zweiter)); fehler += 1
    else:
        print('zweiter Lauf: nichts mehr umzustellen')

    # Verhalten: Grenze 4 = Original fuer 0..4 Nebengilden; hoehere Grenze haelt den Beitritt offen
    abweichung = [(st[0], n) for st in stellen for n in range(5)
                  if entscheidung(st[2], st[3], n, 4, False) != entscheidung(st[2], st[3], n, 4, True)]
    if abweichung:
        print('FEHLER: mit Grenze 4 anders als das Original: %s' % abweichung[:5]); fehler += 1
    else:
        print('Grenze 4: alle %d Stellen entscheiden fuer 0 bis 4 Nebengilden wie das Original' % len(stellen))
    offen = [st[0] for st in aufrufe if st[3] == '<' and not entscheidung('Aufruf', '<', 4, 6, False)]
    frei = [st[0] for st in vergleiche if not entscheidung(st[2], st[3], 5, 6, False)]
    if offen or frei:
        print('FEHLER: mit Grenze 6 und 4 bzw. 5 Gilden falsch: %s %s' % (offen, frei)); fehler += 1
    else:
        print('Grenze 6: Beitritt mit 4 Gilden offen; Schreine und Mario gelten mit 5 Gilden wie mit 4')
    print('ERGEBNIS: %s' % ('OK' if not fehler else '%d FEHLER' % fehler))
    sys.exit(1 if fehler else 0)


if __name__ == '__main__':
    main()
