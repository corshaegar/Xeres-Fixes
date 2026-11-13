"""skript_test.py --spiel <Xeres-Ordner> | --dat <GOTHIC.DAT> --menu <MENU.DAT> - prueft die Skripte in Quelltext\\SYSTEM\\AUTORUN
gegen die uebersetzten Skripte von Xeres' Rueckkehr, ohne das Spiel (zParserExtender uebersetzt sie erst beim Start; ein Fehler
darin hielte dort alles an).

Je Datei: META-Block zuerst, Aufbau nach Daedalus (Deklarationen, Bloecke, "};" nach if/func/instance, "var" ohne Zuweisung,
Ausdruecke), Zeichenketten ohne Backslash/Zeilenumbruch. Jeder Name muss in der Datei stehen oder im passenden DAT (Parser = Game
-> GOTHIC.DAT, Menu -> MENU.DAT); <Name>_OLD nur, wenn die Datei <Name> per MergeMode ersetzt. Felder (x.feld, Felder in
Instanzen) muessen zur Klasse gehoeren, Indizes in die Feldgroesse passen. Aufrufe: Anzahl der Argumente, Funktionsargumente
(Parameter vom Typ func) muessen Funktionen sein, Zahlen nicht an Zeichenketten-Parameter. Zuweisungen an func-Felder nur mit
Funktionen. Namen in Zeichenketten fuer MEM_FindParserSymbol und die XRFIX-Listen muessen im Skript stehen (sonst Hinweis, wenn
der Fix ohne sie auskommt). Im Menue: items[] und onselaction_s[] nennen vorhandene Eintraege bzw. Menues; die Seite MENU_OPT_XR
hat im Original "Zurueck" an Stelle 15 und dahinter frei, und die neue Liste enthaelt jeden Eintrag des Originals genau einmal,
ohne Luecke, mit der Ueberschrift vorn und "Zurueck" am Ende. Nur lesen."""
import argparse, glob, os, re, struct, sys

HIER = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HIER)
from zeiger_test import skript_datei   # noqa: E402

AUTORUN = os.path.join(HIER, '..', 'Quelltext', 'SYSTEM', 'AUTORUN')
T_VOID, T_FLOAT, T_INT, T_STRING, T_CLASS, T_FUNC, T_PROTO, T_INST = 0, 1, 2, 3, 4, 5, 6, 7
F_CONST, F_RETURN, F_CLASSVAR, F_EXTERNAL = 1, 2, 4, 8
TYPNAMEN = {'void': T_VOID, 'float': T_FLOAT, 'int': T_INT, 'string': T_STRING, 'func': T_FUNC, 'instance': T_INST}
# Namen in Zeichenketten, die nicht im Skript der Mod stehen muessen: der Fix prueft sie und kommt ohne sie aus
OPTIONAL = {'_B_HERODAMAGEPERCFUNC', '_B_HERODAMAGE_OLD'}


# --- DAT ---------------------------------------------------------------------------------------------------------------------

def lade_dat(d):
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
        p += 20
        content = None
        if not (flags & F_CLASSVAR):
            if typ in (T_CLASS, T_FUNC, T_PROTO, T_INST):
                content = struct.unpack_from('<i', d, p)[0]; p += 4
            elif typ in (T_FLOAT, T_INT):
                content = list(struct.unpack_from('<%di' % ele, d, p)); p += 4 * ele
            elif typ == T_STRING:
                content = []
                for _ in range(ele):
                    e = d.index(b'\n', p); content.append(d[p:e].decode('latin-1')); p = e + 1
        parent = struct.unpack_from('<i', d, p)[0]; p += 4
        syms.append(dict(i=i, name=name.upper(), typ=typ, flags=flags, ele=ele, content=content, parent=parent))
    return syms


class Dat:
    def __init__(self, roh):
        self.syms = lade_dat(roh)
        self.by = {}
        for s in self.syms:
            if s['name']:
                self.by.setdefault(s['name'], s)

    def klasse(self, s):
        """Klasse eines Symbols vom Typ instance/prototype (ueber Prototypen hinweg), sonst None"""
        k = 0
        while s and k < 8:
            if s['typ'] == T_CLASS:
                return s['name']
            if s['typ'] not in (T_INST, T_PROTO) or s['parent'] < 0:
                return None
            s = self.syms[s['parent']] if s['parent'] < len(self.syms) else None
            k += 1
        return None

    def params(self, s):
        return [self.syms[s['i'] + 1 + j] for j in range(s['ele'])] if s['typ'] == T_FUNC else []


# --- Zerlegen ----------------------------------------------------------------------------------------------------------------

OPS2 = ('||', '&&', '==', '!=', '<=', '>=', '<<', '>>', '+=', '-=', '*=', '/=')


def zerlege(text, fehler):
    tok, i, zeile = [], 0, 1
    while i < len(text):
        c = text[i]
        if c == '\n':
            zeile += 1; i += 1; continue
        if c in ' \t\r':
            i += 1; continue
        if text.startswith('//', i):
            while i < len(text) and text[i] != '\n':
                i += 1
            continue
        if text.startswith('/*', i):
            j = text.find('*/', i + 2)
            if j < 0:
                fehler.append('Zeile %d: Kommentar ohne Ende' % zeile); break
            zeile += text[i:j].count('\n'); i = j + 2; continue
        if c == '"':
            j = text.find('"', i + 1)
            if j < 0:
                fehler.append('Zeile %d: Zeichenkette ohne Ende' % zeile); break
            s = text[i + 1:j]
            if '\\' in s:
                fehler.append('Zeile %d: Backslash in Zeichenkette' % zeile)
            if '\n' in s:
                fehler.append('Zeile %d: Zeilenumbruch in Zeichenkette' % zeile)
            tok.append(('str', s, zeile)); i = j + 1; continue
        m = re.match(r'\d+\.\d+|\d+', text[i:])
        if m:
            tok.append(('zahl', m.group(), zeile)); i += len(m.group()); continue
        m = re.match(r'[A-Za-z_\xc0-\xff][A-Za-z0-9_@^\xc0-\xff]*', text[i:])   # Ikarus: _^, _@, _@s
        if m:
            tok.append(('name', m.group(), zeile)); i += len(m.group()); continue
        if text[i:i + 2] in OPS2:
            tok.append(('op', text[i:i + 2], zeile)); i += 2; continue
        if c in '+-*/%|&~!<>=(){}[],;.':
            tok.append(('op', c, zeile)); i += 1; continue
        fehler.append('Zeile %d: unbekanntes Zeichen %r' % (zeile, c)); i += 1
    tok.append(('ende', '', zeile))
    return tok


class Abbruch(Exception):
    pass


# --- Pruefen -----------------------------------------------------------------------------------------------------------------

class Pruefer:
    def __init__(self, pfad, dats):
        self.pfad = os.path.basename(pfad)
        self.fehler, self.hinweise = [], []
        text = open(pfad, 'rb').read().decode('cp1252')
        self.tok = zerlege(text, self.fehler)
        self.pos = 0
        self.meta = self.lies_meta()
        self.dat = dats.get(self.meta.get('PARSER', 'GAME').upper())
        if self.dat is None:
            raise Abbruch('Parser %s unbekannt' % self.meta.get('PARSER'))
        self.merge = self.meta.get('MERGEMODE', '0').upper() in ('1', 'TRUE')
        self.glob = {}          # Name -> dict(art, typ, klasse, params)
        self.lokal = {}
        self.felder = None      # Klasse der Instanz, in deren Rumpf wir stehen
        self.rueckgabe = None
        self.namen_in_text = []
        self.menue = {}         # Instanz -> {Feld[Index]: Wert} (nur Menue)
        self.vorlauf()

    # Grundlagen
    def sieh(self, o=0):
        return self.tok[min(self.pos + o, len(self.tok) - 1)]

    def nimm(self, art=None, wert=None):
        t = self.sieh()
        if (art and t[0] != art) or (wert is not None and t[1].lower() != wert.lower()):
            raise Abbruch('Zeile %d: erwartet %s, gefunden %r' % (t[2], wert or art, t[1]))
        self.pos += 1
        return t

    def ist(self, wert, o=0):
        t = self.sieh(o)
        return t[0] in ('op', 'name') and t[1].lower() == wert.lower()

    def f(self, zeile, text):
        self.fehler.append('Zeile %d: %s' % (zeile, text))

    def lies_meta(self):
        meta = {}
        if not self.ist('META'):
            self.f(self.sieh()[2], 'META-Block muss am Anfang stehen'); return meta
        self.nimm('name'); self.nimm('op', '{')
        while not self.ist('}'):
            k = self.nimm('name')[1].upper(); self.nimm('op', '=')
            werte = []
            while not self.ist(';'):
                werte.append(self.nimm()[1])
            self.nimm('op', ';')
            meta[k] = ''.join(werte)
        self.nimm('op', '}'); self.nimm('op', ';')
        return meta

    def deklariere(self, nm, eintrag):
        """Name auf Dateiebene festhalten. Daedalus kennt keine Gross-/Kleinschreibung: zweimal derselbe Name ist ein Fehler (mit
        MergeMode meldet zParserExtender "replacement symbol ... has incorrect type", Test 13.11.2026). Steht der Name schon im
        Skript der Mod, muss MergeMode an sein und die Art passen (func ersetzt func, instance ersetzt instance)"""
        if nm in self.glob:
            self.f(eintrag['zeile'], '%s ist in dieser Datei schon deklariert (Zeile %d) - Daedalus unterscheidet keine Gross-/'
                                     'Kleinschreibung' % (nm, self.glob[nm]['zeile']))
        elif nm in self.dat.by:
            alt = self.dat.by[nm]
            art = eintrag['art']
            passt = ((art == 'func' and alt['typ'] == T_FUNC) or (art == 'instance' and alt['typ'] == T_INST) or
                     (art == 'prototype' and alt['typ'] == T_PROTO))
            if not self.merge:
                self.f(eintrag['zeile'], '%s gibt es schon im Skript der Mod (ohne MergeMode nicht erlaubt)' % nm)
            elif not passt:
                self.f(eintrag['zeile'], '%s ersetzt ein Symbol anderer Art im Skript der Mod (Typ %d)' % (nm, alt['typ']))
        self.glob[nm] = eintrag

    # Vorlauf: alle Deklarationen der Datei (Vorwaertsbezuege wie in Gothics Dialogen)
    def vorlauf(self):
        p, tiefe, t = self.pos, 0, self.tok
        while t[p][0] != 'ende':
            w = t[p][1].lower()
            if t[p][0] == 'op' and w == '{':
                tiefe += 1
            elif t[p][0] == 'op' and w == '}':
                tiefe -= 1
            elif tiefe == 0 and t[p][0] == 'name':
                if w == 'func' and t[p + 2][0] == 'name':
                    nm, ps, q = t[p + 2][1].upper(), [], p + 4
                    while not (t[q][0] == 'op' and t[q][1] == ')') and t[q][0] != 'ende':
                        if t[q][1].lower() == 'var':
                            ps.append(dict(typ=t[q + 1][1], name=t[q + 2][1]))
                        q += 1
                    self.deklariere(nm, dict(art='func', typ=t[p + 1][1].lower(), params=ps, zeile=t[p][2]))
                    p = q   # Parameter ("var int x" im Funktionskopf) sind keine globalen Namen
                elif w in ('instance', 'prototype'):
                    nm, q = [t[p + 1][1].upper()], p + 2
                    while t[q][1] == ',':
                        nm.append(t[q + 1][1].upper()); q += 2
                    eltern = t[q + 1][1].upper() if t[q][1] == '(' else None
                    for n in nm:
                        self.deklariere(n, dict(art=w, eltern=eltern, zeile=t[p][2]))
                elif w in ('const', 'var'):
                    self.deklariere(t[p + 2][1].upper(), dict(art=w, typ=t[p + 1][1].lower(), zeile=t[p][2]))
            p += 1
        for nm, g in list(self.glob.items()):
            if self.merge and nm in self.dat.by and g['art'] in ('func', 'instance'):
                self.glob[nm + '_OLD'] = dict(art='alt', von=nm)

    # Namen
    def symbol(self, name):
        """Beschreibung eines Namens: ('lokal'|'datei'|'dat', Eintrag) oder None"""
        n = name.upper()
        if n in self.lokal:
            return ('lokal', self.lokal[n])
        if self.felder and (self.felder + '.' + n) in self.dat.by:
            return ('feld', self.dat.by[self.felder + '.' + n])
        if n in self.glob:
            return ('datei', self.glob[n])
        if n in self.dat.by:
            return ('dat', self.dat.by[n])
        return None

    def klasse_von(self, name):
        s = self.symbol(name)
        if not s:
            return None
        art, e = s
        if art in ('lokal', 'datei') and e.get('typ') and e['typ'] not in TYPNAMEN:
            return e['typ'].upper()
        if art == 'datei' and e.get('art') in ('instance', 'prototype'):
            k = self.dat.by.get(e['eltern'] or '')
            return self.dat.klasse(k) if k else None
        if art == 'dat':
            return self.dat.klasse(e)
        return None

    def ist_funktion(self, name):
        s = self.symbol(name)
        if not s:
            return False
        art, e = s
        if art == 'datei':
            return e['art'] in ('func', 'alt')
        return art == 'dat' and e['typ'] == T_FUNC and bool(e['flags'] & F_CONST)

    # Dateiebene
    def pruefe(self):
        try:
            while self.sieh()[0] != 'ende':
                t = self.nimm('name')
                w = t[1].lower()
                if w == 'const':
                    self.konstante(global_=True)
                elif w == 'var':
                    self.variable(global_=True)
                elif w == 'func':
                    self.funktion()
                elif w in ('instance', 'prototype'):
                    self.instanz(w)
                else:
                    raise Abbruch('Zeile %d: unerwartet %r auf Dateiebene' % (t[2], t[1]))
        except Abbruch as ex:
            self.fehler.append(str(ex))

    def typ(self):
        t = self.nimm('name')
        if t[1].lower() not in TYPNAMEN and not (t[1].upper() in self.dat.by and self.dat.by[t[1].upper()]['typ'] == T_CLASS):
            self.f(t[2], 'unbekannter Typ %s' % t[1])
        return t[1].lower()

    def konstante(self, global_):
        ty = self.typ()
        nm = self.nimm('name')
        if self.ist('['):
            self.nimm('op', '['); self.ausdruck(); self.nimm('op', ']')
            self.nimm('op', '='); self.nimm('op', '{')
            self.ausdruck()
            while self.ist(','):
                self.nimm('op', ','); self.ausdruck()
            self.nimm('op', '}')
        else:
            self.nimm('op', '=')
            art = self.ausdruck()
            if ty == 'string' and art not in ('str', '?'):
                self.f(nm[2], 'Konstante %s: keine Zeichenkette' % nm[1])
        self.nimm('op', ';')
        if not global_:
            self.lokal[nm[1].upper()] = dict(art='const', typ=ty)

    def variable(self, global_):
        ty = self.typ()
        while True:
            nm = self.nimm('name')
            if self.ist('['):
                self.nimm('op', '['); self.ausdruck(); self.nimm('op', ']')
            if not global_:
                self.lokal[nm[1].upper()] = dict(art='var', typ=ty)
            if self.ist(','):
                self.nimm('op', ','); continue
            break
        if self.ist('='):
            self.f(self.sieh()[2], 'Daedalus kennt keine Zuweisung in "var" - erst deklarieren, dann zuweisen')
        self.nimm('op', ';')

    def funktion(self):
        ty = self.typ()
        nm = self.nimm('name')
        self.lokal = {}
        self.nimm('op', '(')
        while not self.ist(')'):
            self.nimm('name', 'var'); pty = self.typ(); pn = self.nimm('name')
            self.lokal[pn[1].upper()] = dict(art='var', typ=pty)
            if self.ist(','):
                self.nimm('op', ',')
        self.nimm('op', ')')
        self.rueckgabe = ty
        self.block()
        self.nimm('op', ';')
        self.lokal, self.rueckgabe = {}, None

    def instanz(self, art):
        namen = [self.nimm('name')[1].upper()]
        while self.ist(','):
            self.nimm('op', ','); namen.append(self.nimm('name')[1].upper())
        self.nimm('op', '(')
        el = self.nimm('name')
        self.nimm('op', ')')
        k = self.dat.by.get(el[1].upper())
        klasse = self.dat.klasse(k) if k else None
        if not klasse:
            self.f(el[2], 'Klasse/Prototyp %s fehlt' % el[1])
        if self.ist(';'):
            self.nimm('op', ';'); return
        self.felder, self.lokal, self.rueckgabe = klasse, {}, 'void'
        self.aktuell = namen[0]
        self.menue.setdefault(namen[0], {})
        self.block()
        self.nimm('op', ';')
        self.felder, self.aktuell = None, None

    # Anweisungen
    def block(self):
        self.nimm('op', '{')
        while not self.ist('}'):
            if self.sieh()[0] == 'ende':
                raise Abbruch('Datei endet im Block')
            self.anweisung()
        self.nimm('op', '}')

    def anweisung(self):
        t = self.sieh()
        w = t[1].lower() if t[0] == 'name' else None
        if w == 'var':
            self.nimm(); self.variable(global_=False); return
        if w == 'const':
            self.nimm(); self.konstante(global_=False); return
        if w == 'if':
            self.nimm()
            while True:
                self.nimm('op', '('); self.ausdruck(); self.nimm('op', ')')
                self.block()
                if self.ist('else'):
                    self.nimm()
                    if self.ist('if'):
                        self.nimm(); continue
                    self.block()
                break
            if not self.ist(';'):
                self.f(self.sieh()[2], 'nach if { } fehlt ";"')
            else:
                self.nimm('op', ';')
            return
        if w == 'return':
            self.nimm()
            if self.ist(';'):
                if self.rueckgabe not in ('void', None):
                    self.hinweise.append('Zeile %d: return ohne Wert in func %s' % (t[2], self.rueckgabe))
            else:
                self.ausdruck()
                if self.rueckgabe == 'void':
                    self.f(t[2], 'return mit Wert in func void')
            self.nimm('op', ';'); return
        # Zuweisung oder Aufruf
        start = self.pos
        if t[0] == 'name' and self.ist('(', 1):
            self.ausdruck(); self.nimm('op', ';'); return
        ziel = self.lwert()
        op = self.sieh()
        if op[1] not in ('=', '+=', '-=', '*=', '/='):
            raise Abbruch('Zeile %d: Zuweisung erwartet nach %s, gefunden %r' % (op[2], self.tok[start][1], op[1]))
        self.nimm()
        rechts = self.pos
        art = self.ausdruck()
        if ziel and ziel.get('typ') == T_FUNC:
            rt = self.tok[rechts]
            if not (rechts + 1 == self.pos and rt[0] == 'name' and self.ist_funktion(rt[1])):
                self.f(op[2], 'func-Feld %s braucht eine Funktion' % ziel['name'])
        if ziel and ziel.get('typ') == T_STRING and art == 'zahl':
            self.f(op[2], 'Zahl an Zeichenkette %s' % ziel['name'])
        if ziel and ziel.get('typ') == T_INT and art == 'str':
            self.f(op[2], 'Zeichenkette an Ganzzahl %s' % ziel['name'])
        if self.felder and ziel and ziel.get('feld') and art == 'str' and op[1] == '=':
            self.menue[self.aktuell][ziel['feld']] = self.tok[rechts][1]
        self.nimm('op', ';')

    def lwert(self):
        """Ziel einer Zuweisung: name, name[i], name.feld; gibt dict(name, typ, feld) zurueck"""
        t = self.nimm('name')
        s = self.symbol(t[1])
        if not s:
            self.f(t[2], 'unbekannt: %s' % t[1]); return None
        art, e = s
        typ, feld, ele = None, None, 1
        if art == 'feld':
            typ, feld, ele = e['typ'], t[1].lower(), e['ele']
        elif art in ('lokal', 'datei'):
            typ = TYPNAMEN.get(e.get('typ'), T_INST)
            if e.get('art') == 'const':
                self.f(t[2], 'Zuweisung an Konstante %s' % t[1])
        elif art == 'dat':
            typ, ele = e['typ'], e['ele']
            if e['flags'] & F_CONST:
                self.f(t[2], 'Zuweisung an Konstante %s' % t[1])
        if self.ist('['):
            self.nimm('op', '[')
            it = self.sieh()
            self.ausdruck()
            self.nimm('op', ']')
            if it[0] == 'zahl' and int(it[1]) >= ele:
                self.f(it[2], '%s[%s] ausserhalb (Groesse %d)' % (t[1], it[1], ele))
            if feld:
                feld = '%s[%s]' % (feld, it[1])
        elif feld:
            feld = feld + '[0]' if ele > 1 else feld
        if self.ist('.'):
            self.nimm('op', '.')
            fn = self.nimm('name')
            k = self.klasse_von(t[1])
            fe = self.dat.by.get('%s.%s' % (k, fn[1].upper())) if k else None
            if not fe:
                self.f(fn[2], '%s.%s: kein Feld (Klasse %s)' % (t[1], fn[1], k))
                return None
            return dict(name='%s.%s' % (t[1], fn[1]), typ=fe['typ'])
        return dict(name=t[1], typ=typ, feld=feld)

    # Ausdruecke (Rueckgabe: grobe Art 'zahl' | 'str' | '?')
    STUFEN = [('||',), ('&&',), ('|',), ('&',), ('==', '!='), ('<', '<=', '>', '>='), ('<<', '>>'), ('+', '-'), ('*', '/', '%')]

    def ausdruck(self, stufe=0):
        if stufe == len(self.STUFEN):
            return self.einstellig()
        links = self.ausdruck(stufe + 1)
        while self.sieh()[0] == 'op' and self.sieh()[1] in self.STUFEN[stufe]:
            op = self.nimm()
            rechts = self.ausdruck(stufe + 1)
            if 'str' in (links, rechts) and op[1] != '==':
                self.f(op[2], 'Operator %s mit Zeichenkette (Daedalus: ConcatStrings/Hlp_StrCmp)' % op[1])
            links = '?'
        return links

    def einstellig(self):
        if self.sieh()[0] == 'op' and self.sieh()[1] in ('!', '-', '+', '~'):
            self.nimm(); self.einstellig(); return '?'
        return self.grund()

    def grund(self):
        t = self.nimm()
        if t[0] == 'zahl':
            return 'zahl'
        if t[0] == 'str':
            return 'str'
        if t[0] == 'op' and t[1] == '(':
            a = self.ausdruck(); self.nimm('op', ')'); return a
        if t[0] != 'name':
            raise Abbruch('Zeile %d: Ausdruck erwartet, gefunden %r' % (t[2], t[1]))
        if self.ist('('):
            return self.aufruf(t)
        s = self.symbol(t[1])
        if not s:
            self.f(t[2], 'unbekannt: %s' % t[1]); return '?'
        if self.ist('['):
            self.nimm('op', '['); self.ausdruck(); self.nimm('op', ']')
        if self.ist('.'):
            self.nimm('op', '.')
            fn = self.nimm('name')
            k = self.klasse_von(t[1])
            if not (k and ('%s.%s' % (k, fn[1].upper())) in self.dat.by):
                self.f(fn[2], '%s.%s: kein Feld (Klasse %s)' % (t[1], fn[1], k))
            else:
                fe = self.dat.by['%s.%s' % (k, fn[1].upper())]
                return 'str' if fe['typ'] == T_STRING else '?'
        art, e = s
        if art == 'dat' and e['typ'] == T_STRING:
            return 'str'
        if art in ('lokal', 'datei') and e.get('typ') == 'string':
            return 'str'
        return '?'

    def aufruf(self, t):
        nm = t[1].upper()
        s = self.symbol(nm)
        self.nimm('op', '(')
        args = []
        while not self.ist(')'):
            a0 = self.pos
            art = self.ausdruck()
            args.append((a0, self.pos, art))
            if self.ist(','):
                self.nimm('op', ',')
            elif not self.ist(')'):
                raise Abbruch('Zeile %d: "," oder ")" erwartet, gefunden %r' % (self.sieh()[2], self.sieh()[1]))
        self.nimm('op', ')')
        if not s:
            self.f(t[2], 'unbekannte Funktion %s' % t[1]); return '?'
        art, e = s
        ptypen, rtyp = None, '?'
        if art == 'datei' and e['art'] == 'func':
            ptypen = [TYPNAMEN.get(p['typ'].lower(), T_INST) for p in e['params']]
            rtyp = 'str' if e['typ'] == 'string' else '?'
        elif art == 'datei' and e['art'] == 'alt':
            alt = self.dat.by[e['von']]
            ptypen = [p['typ'] for p in self.dat.params(alt)] if alt['typ'] == T_FUNC else []
        elif art == 'dat' and e['typ'] == T_FUNC:
            ptypen = [p['typ'] for p in self.dat.params(e)]
        else:
            self.f(t[2], '%s ist keine Funktion' % t[1]); return '?'
        if len(args) != len(ptypen):
            self.f(t[2], '%s: %d Argumente statt %d' % (t[1], len(args), len(ptypen)))
            return rtyp
        for (a0, a1, aart), pt in zip(args, ptypen):
            at = self.tok[a0]
            if pt == T_FUNC and not (a1 == a0 + 1 and at[0] == 'name' and self.ist_funktion(at[1])):
                self.f(at[2], '%s: Argument %r muss eine Funktion sein' % (t[1], at[1]))
            if pt == T_STRING and aart == 'zahl':
                self.f(at[2], '%s: Zahl an Zeichenketten-Parameter' % t[1])
            if pt == T_INT and aart == 'str':
                self.f(at[2], '%s: Zeichenkette an Ganzzahl-Parameter' % t[1])
            if at[0] == 'str' and a1 == a0 + 1 and (nm in ('MEM_FINDPARSERSYMBOL', 'MEM_GETSYMBOL') or nm.startswith('XRFIX_')):
                self.namen_in_text.append((at[2], at[1]))
        if art == 'dat' and e['flags'] & F_RETURN:
            # Rueckgabetyp steht nicht im Symbol - Zeichenketten-Funktionen erkennt man am Namen des Rueckgabewerts nicht; grob:
            rtyp = 'str' if nm in ('CONCATSTRINGS', 'INTTOSTRING', 'MEM_GETGOTHOPT', 'MEM_GETMODOPT', 'STR_SUBSTR',
                                   'STR_PREFIX', 'STR_UPPER', 'STR_LOWER', 'MEM_READSTRING') else '?'
        return rtyp


def lese_menue_items(roh, instanz):
    """items[] einer Menue-Instanz aus dem uebersetzten MENU.DAT (Zuweisungen an C_MENU.ITEMS im Code der Instanz)"""
    syms = lade_dat(roh)
    p = 1
    n = struct.unpack_from('<i', roh, p)[0]; p += 4 + 4 * n
    # Ende der Symboltabelle suchen: lade_dat liest sie ganz; Code steht dahinter
    q = 5 + 4 * n
    for s in syms:
        pass
    # Code-Anfang ueber eine zweite Lesung bestimmen
    d = roh
    p = 1
    n = struct.unpack_from('<i', d, p)[0]; p += 4 + 4 * n
    for i in range(n):
        named = struct.unpack_from('<i', d, p)[0]; p += 4
        if named:
            p = d.index(b'\n', p) + 1
        off, bits = struct.unpack_from('<ii', d, p); p += 8
        ele = bits & 0xFFF; typ = (bits >> 12) & 0xF; flags = (bits >> 16) & 0x3F
        p += 20
        if not (flags & F_CLASSVAR):
            if typ in (4, 5, 6, 7):
                p += 4
            elif typ in (1, 2):
                p += 4 * ele
            elif typ == 3:
                for _ in range(ele):
                    p = d.index(b'\n', p) + 1
        p += 4
    groesse = struct.unpack_from('<i', d, p)[0]; p += 4
    code = d[p:p + groesse]
    by = {s['name']: s for s in syms if s['name']}
    items_sym = by.get('C_MENU.ITEMS')
    s = by.get(instanz)
    if not s or not items_sym:
        return None
    starts = sorted(x['content'] for x in syms if x['typ'] in (5, 6, 7) and (x['flags'] & 1) and not (x['flags'] & 8)
                    and isinstance(x['content'], int) and 0 <= x['content'] < len(code))
    a = s['content']
    e = next((x for x in starts if x > a), len(code))
    befehle, q = [], a
    while q < e:
        op = code[q]
        if op in (61, 62, 64, 65, 67, 75, 76, 80):
            befehle.append((op, struct.unpack_from('<i', code, q + 1)[0], None)); q += 5
        elif op == 245:
            befehle.append((op, struct.unpack_from('<i', code, q + 1)[0], code[q + 5])); q += 6
        else:
            befehle.append((op, None, None)); q += 1
    items = {}
    for k, (op, arg, idx) in enumerate(befehle):
        if op == 70 and k >= 2:   # Zeichenkette zuweisen
            for (o1, a1, i1), (o2, a2, i2) in ((befehle[k - 1], befehle[k - 2]), (befehle[k - 2], befehle[k - 1])):
                if o1 in (65, 245) and a1 == items_sym['i'] and o2 == 65 and syms[a2]['typ'] == T_STRING and syms[a2]['content']:
                    items[i1 if o1 == 245 else 0] = syms[a2]['content'][0].upper()
                    break
    return items


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--spiel')
    ap.add_argument('--dat')
    ap.add_argument('--menu')
    a = ap.parse_args()
    if a.spiel:
        game, menu = skript_datei(a.spiel, 'GOTHIC.DAT'), skript_datei(a.spiel, 'MENU.DAT')
    elif a.dat and a.menu:
        game, menu = open(a.dat, 'rb').read(), open(a.menu, 'rb').read()
    else:
        sys.exit('--spiel <Xeres-Ordner> oder --dat <GOTHIC.DAT> --menu <MENU.DAT>')
    if game is None or menu is None:
        sys.exit('GOTHIC.DAT/MENU.DAT nicht in Xeres_Scripts_DE.mod gefunden (Data\\ModVDF oder Data)')
    dats = {'GAME': Dat(game), 'MENU': Dat(menu)}
    fehler = 0
    dateien = sorted(glob.glob(os.path.join(AUTORUN, '*.D')))
    for pfad in dateien:
        try:
            pr = Pruefer(pfad, dats)
        except Abbruch as ex:
            print('%s: FEHLER %s' % (os.path.basename(pfad), ex)); fehler += 1; continue
        pr.pruefe()
        dat = pr.dat
        for zeile, name in pr.namen_in_text:
            n = name.upper()
            basis = n[:-4] if n.endswith('_OLD') else n
            if n in dat.by or n in pr.glob:
                continue
            if n in OPTIONAL or (n.endswith('_OLD') and (basis in dat.by)):
                pr.hinweise.append('Zeile %d: "%s" steht nicht im Skript der Mod - der Fix kommt ohne aus' % (zeile, name))
            else:
                pr.f(zeile, 'Name "%s" steht nicht im Skript' % name)
        if pr.meta.get('PARSER', '').upper() == 'MENU':
            for inst, felder in pr.menue.items():
                for feld, wert in felder.items():
                    if feld.startswith('items') and wert.upper() not in dat.by and wert.upper() not in pr.glob:
                        pr.f(0, '%s.%s = "%s": Eintrag fehlt' % (inst, feld, wert))
                    if feld.startswith('onselaction_s') and wert and wert.upper() not in dat.by and wert.upper() not in pr.glob:
                        pr.f(0, '%s.%s = "%s": Menue fehlt' % (inst, feld, wert))
            if 'MENU_OPT_XR' in pr.glob:
                alt = lese_menue_items(menu, 'MENU_OPT_XR')
                print('  MENU_OPT_XR im Original: %s' % (alt and ', '.join('%d=%s' % kv for kv in sorted(alt.items()))))
                if not alt or alt.get(15) != 'MENUITEM_XR_BACK' or max(alt) != 15:
                    pr.f(0, 'MENU_OPT_XR: im Original steht "Zurueck" nicht an Stelle 15 oder dahinter ist belegt')
                neu = dict(alt or {})
                for feld, wert in pr.menue['MENU_OPT_XR'].items():
                    m = re.match(r'items\[(\d+)\]$', feld)
                    if m:
                        neu[int(m.group(1))] = wert.upper()
                print('  MENU_OPT_XR neu: %s' % ', '.join('%d=%s' % kv for kv in sorted(neu.items())))
                werte = list(neu.values())
                doppelt = sorted({w for w in werte if werte.count(w) > 1})
                fehlt = sorted(set((alt or {}).values()) - set(werte))
                if doppelt or fehlt:
                    pr.f(0, 'MENU_OPT_XR: doppelt %s, fehlt %s' % (doppelt, fehlt))
                if sorted(neu) != list(range(len(neu))):
                    pr.f(0, 'MENU_OPT_XR: Luecke in items[] (%s)' % sorted(neu))
                if neu.get(0) != (alt or {}).get(0) or neu.get(max(neu)) != 'MENUITEM_XR_BACK':
                    pr.f(0, 'MENU_OPT_XR: Ueberschrift nicht vorn oder "Zurueck" nicht am Ende')
                gfa = dat.by.get('MENU_ID_GFA')
                if not gfa or gfa['content'] != [5]:
                    pr.f(0, 'MENU_ID_GFA ist nicht 5 - Zeile 6 der Seite ist vielleicht belegt')
        print('%s (Parser %s, MergeMode %s): %d Token, %d eigene Namen, %d Fehler'
              % (os.path.basename(pfad), pr.meta.get('PARSER'), pr.merge, len(pr.tok), len(pr.glob), len(pr.fehler)))
        for h in pr.hinweise:
            print('  Hinweis', h)
        for e in pr.fehler:
            print('  FEHLER', e)
        fehler += len(pr.fehler)
    print('ERGEBNIS: %s' % ('OK' if not fehler else '%d FEHLER' % fehler))
    sys.exit(1 if fehler else 0)


if __name__ == '__main__':
    main()
