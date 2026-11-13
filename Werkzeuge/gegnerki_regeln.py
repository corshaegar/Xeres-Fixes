"""gegnerki_regeln.py --xeres <Ordner von Xeres' Rueckkehr> [--schreiben]

Gegner-KI "New Balance" (Xeres-Fixes 1.4.0): eigene Kampfregeln nach dem Vorbild der Mod "Die Rueckkehr 2.0 - New Balance".

Was ein Gegner im Nahkampf tut, steht in Gothics Kampftabellen (FIGHT.DAT, Instanzen FA_<Lage>_<Taktik>): je Kampftaktik (FAI_*)
und Lage (19 je Taktik, in der Reihenfolge, in der oCNpc::InitFightAI sie einliest) bis zu 6 Zuege, aus denen Gothic zufaellig
waehlt. Das Werkzeug liest Xeres' Tabellen, wendet die Regeln unten darauf an und schreibt den Tabellenteil von
Quelltext\\SYSTEM\\AUTORUN\\XERES_FIXES.D (zwischen den Marken "Gegner-KI New Balance: Tabellen"): je geaenderte Lage die neuen Zuege
und die von Xeres. Ohne --schreiben nur Bericht. Liest nur aus Xeres' Archiven."""
import argparse, os, re, struct, sys

HIER = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HIER, '..', 'Test'))
from zeiger_test import vdf_datei, lade, skript_mod   # noqa: E402

SKRIPT = os.path.join(HIER, '..', 'Quelltext', 'SYSTEM', 'AUTORUN', 'XERES_FIXES.D')
ANFANG = '// ===== Gegner-KI New Balance: Tabellen'
ENDE = '// ===== Ende Gegner-KI-Tabellen ====='
# Lagen in der Reihenfolge von oCNpc::InitFightAI (12 und 14 lesen beide MY_G_FK_NOFOCUS)
LAGEN = ['ENEMY_PREHIT', 'ENEMY_STORMPREHIT', 'ENEMY_TURNTOHIT_FOCUS', 'MY_W_COMBO', 'MY_W_RUNTO', 'MY_W_STRAFE', 'MY_W_FOCUS',
         'MY_W_NOFOCUS', 'MY_G_COMBO', 'MY_G_RUNTO', 'MY_G_STRAFE', 'MY_G_FOCUS', 'MY_G_FK_NOFOCUS', 'MY_FK_FOCUS', 'MY_G_FK_NOFOCUS',
         'MY_FK_FOCUS_FAR', 'MY_FK_NOFOCUS_FAR', 'MY_FK_FOCUS_MAG', 'MY_FK_NOFOCUS_MAG']
# Zuege (MOVE_* aus Gothics AI_Constants, in Xeres gleich)
RUN, RUNBACK, JUMPBACK, TURN, STRAFE, ATTACK, SIDEATTACK, FRONTATTACK = 1, 2, 3, 4, 5, 6, 7, 8
TRIPLEATTACK, WHIRLATTACK, MASTERATTACK, TURNTOHIT, PARADE, STANDUP, WAIT, WAIT_LONGER, WAIT_EXT = 9, 10, 11, 15, 17, 18, 19, 23, 24
ZUEGE = {0: '-', RUN: 'RUN', RUNBACK: 'RUNBACK', JUMPBACK: 'JUMPBACK', TURN: 'TURN', STRAFE: 'STRAFE', ATTACK: 'ATTACK',
         SIDEATTACK: 'SIDEATTACK', FRONTATTACK: 'FRONTATTACK', TRIPLEATTACK: 'TRIPLEATTACK', WHIRLATTACK: 'WHIRLATTACK',
         MASTERATTACK: 'MASTERATTACK', TURNTOHIT: 'TURNTOHIT', PARADE: 'PARADE', STANDUP: 'STANDUP', WAIT: 'WAIT',
         WAIT_LONGER: 'WAIT_LONGER', WAIT_EXT: 'WAIT_EXT'}

MENSCHEN = ('FAI_HUMAN_COWARD', 'FAI_HUMAN_NORMAL', 'FAI_HUMAN_STRONG', 'FAI_HUMAN_MASTER')
MONSTER_NAH = ('FAI_MINECRAWLER', 'FAI_DEMON', 'FAI_STONEGOLEM', 'FAI_SNAPPER', 'FAI_ZOMBIE')


def ersetzt(z, alt, neu):
    return [neu if m == alt else m for m in z]


# --- Die Regeln. Jede bekommt Xeres' Zuege einer Lage (ohne leere Stellen), die Kampftaktik und die Lage und gibt die neuen
# Zuege zurueck (hoechstens 6). Gothic waehlt gleich verteilt aus der Liste - ein Zug, der zweimal dasteht, kommt doppelt so oft.

def sturmangriff(z, taktik, lage):
    """Menschen parieren einen Sturmangriff, statt seitwaerts auszuweichen. Feiglinge springen auch mal zurueck; wer schon zur
    Haelfte pariert (normale Kaempfer), pariert jetzt in zwei von drei Faellen und bleibt sonst stehen."""
    if PARADE in z:
        return [PARADE, PARADE, WAIT]
    z = ersetzt(z, STRAFE, PARADE)
    if taktik == 'FAI_HUMAN_COWARD':
        z.append(JUMPBACK)
    return z


def umkreist(z, taktik, lage):
    """Wer umkreist wird (der Gegner bewegt sich seitlich, Xeres sieht dafuer keinen Zug vor), dreht sich zu ihm - doppelt so
    oft wie die anderen Antworten -, weicht zurueck oder wartet ab."""
    return z or [TURN, TURN, JUMPBACK, WAIT]


def mittlere_entfernung(z, taktik, lage):
    """Auf mittlere Entfernung mit Blick auf den Gegner kein Seitschritt mehr, sondern abwarten."""
    return ersetzt(z, STRAFE, WAIT)


def meister_nah(z, taktik, lage):
    """Meister setzen in Waffenreichweite ihre Kombinationen ein: Dreifach-, Wirbel- und Meisterangriff kommen zu ihren
    Angriffen dazu, das Abwarten bleibt."""
    angriffe = [m for m in z if m != WAIT]
    neu = [m for m in (TRIPLEATTACK, WHIRLATTACK, MASTERATTACK) if m not in angriffe]
    return (angriffe + neu + [m for m in z if m == WAIT])[:6]


def meister_fern(z, taktik, lage):
    """Meister greifen auch aus der Ferne mit Kombinationen an (Front- und Dreifachangriff)."""
    return z + [m for m in (FRONTATTACK, TRIPLEATTACK) if m not in z]


def gegen_magier(z, taktik, lage):
    """Gegen Magier auf Distanz bleiben sie nicht nur stehen, sondern weichen seitlich aus: Meister ersetzen das lange Warten
    durch einen Seitschritt und zwei kurze Wartezuege, Orks behalten ihre langen Wartezuege und weichen zweimal seitlich aus."""
    if taktik == 'FAI_HUMAN_MASTER':
        return [m for m in z if m != WAIT_EXT] + [STRAFE, WAIT, WAIT]
    return [m for m in z if m != WAIT_EXT] + [STRAFE, STRAFE] + [m for m in z if m == WAIT_EXT]


def gegenangriff(z, taktik, lage):
    """Holt der Gegner zum Schlag aus, schlagen diese Wesen zurueck: ihr letzter ausweichender oder abwartender Zug wird ein
    Angriff."""
    z = list(z)
    for k in reversed(range(len(z))):
        if z[k] != ATTACK:
            z[k] = ATTACK
            break
    return z


def nah_angreifen(z, taktik, lage):
    """In Waffenreichweite mit Blick auf den Gegner greifen diese Wesen doppelt so oft an, wie sie abwarten."""
    if z and set(z) <= {ATTACK, WAIT}:
        return [ATTACK, ATTACK, WAIT]
    return z


def golem_sturm(z, taktik, lage):
    """Steingolems lassen einen Sturmangriff kommen, statt ihm entgegenzuschlagen."""
    return [WAIT]


def sumpfhai(z, taktik, lage):
    """Sumpfhaie verfolgen nicht: Umkreist, drehen sie sich zum Gegner (auf mittlere Entfernung greifen sie auch an); laeuft er
    auf sie zu, drehen sie sich, statt loszulaufen; auf weite Entfernung greifen sie nicht an, sondern warten."""
    if lage == 'MY_W_STRAFE':
        return z or [TURN]
    if lage == 'MY_G_STRAFE':
        return z or [TURN, ATTACK]
    if lage == 'MY_G_RUNTO':
        return ersetzt(z, RUN, TURN)
    if lage == 'MY_FK_FOCUS_FAR':
        return ersetzt(z, ATTACK, WAIT)
    if lage == 'MY_FK_FOCUS_MAG':
        return [m for m in z if m != ATTACK] or [WAIT]
    return z


def ork_nah(z, taktik, lage):
    """Orks warten in Waffenreichweite seltener: Vom dreifachen Abwarten bleibt eines, dafuer Wirbel- und Seitenangriff."""
    out, ersatz, gesehen = [], [WHIRLATTACK, SIDEATTACK], 0
    for m in z:
        if m == WAIT:
            gesehen += 1
            if gesehen > 1 and ersatz:
                m = ersatz.pop(0)
        out.append(m)
    return out


def ork_fern(z, taktik, lage):
    """Orks greifen auf Entfernung abwechslungsreicher an: meist direkt, dazu Seiten- und Dreifachangriff und ein Seitschritt."""
    if z == [ATTACK]:
        return [ATTACK, ATTACK, SIDEATTACK, TRIPLEATTACK, STRAFE]
    return z


REGELN = [
    ('Sturmangriff parieren', MENSCHEN, ('ENEMY_STORMPREHIT',), sturmangriff),
    ('Umkreist', MENSCHEN + ('FAI_ORC',), ('MY_W_STRAFE', 'MY_G_STRAFE'), umkreist),
    ('Mittlere Entfernung', ('FAI_HUMAN_COWARD', 'FAI_HUMAN_STRONG', 'FAI_HUMAN_MASTER'), ('MY_G_FOCUS',), mittlere_entfernung),
    ('Meister nah', ('FAI_HUMAN_MASTER',), ('MY_W_FOCUS',), meister_nah),
    ('Meister fern', ('FAI_HUMAN_MASTER',), ('MY_FK_FOCUS_FAR',), meister_fern),
    ('Gegen Magier', ('FAI_HUMAN_MASTER', 'FAI_ORC'), ('MY_FK_FOCUS_MAG',), gegen_magier),
    ('Gegenangriff', MONSTER_NAH, ('ENEMY_PREHIT',), gegenangriff),
    ('Nah angreifen', ('FAI_STONEGOLEM', 'FAI_SNAPPER', 'FAI_ZOMBIE', 'FAI_SWAMPSHARK'), ('MY_W_FOCUS',), nah_angreifen),
    ('Golem Sturmangriff', ('FAI_STONEGOLEM',), ('ENEMY_STORMPREHIT',), golem_sturm),
    ('Sumpfhai', ('FAI_SWAMPSHARK',), ('MY_W_STRAFE', 'MY_G_STRAFE', 'MY_G_RUNTO', 'MY_FK_FOCUS_FAR', 'MY_FK_FOCUS_MAG'), sumpfhai),
    ('Ork nah', ('FAI_ORC',), ('MY_W_FOCUS',), ork_nah),
    ('Ork fern', ('FAI_ORC',), ('MY_G_RUNTO', 'MY_FK_FOCUS_FAR'), ork_fern),
]


# --- Xeres' Tabellen lesen ---------------------------------------------------------------------------------------------------

def datei_aus(archiv, name):
    roh = vdf_datei(archiv, name)
    if roh is None:
        sys.exit('%s nicht in %s' % (name, archiv))
    return roh


def tabellen(roh):
    """{Instanzname: [6 Zuege]} aus einer FIGHT.DAT: Zuweisungen an C_FIGHTAI.MOVE im Code jeder Instanz nachspielen"""
    syms, code = lade(roh)
    index = {s['name'].upper(): i for i, s in enumerate(syms)}
    feld = index['C_FIGHTAI.MOVE']
    starts = sorted((s['content'], i) for i, s in enumerate(syms)
                    if s['typ'] in (5, 6, 7) and (s['flags'] & 1) and not (s['flags'] & 8) and isinstance(s['content'], int))
    out = {}
    for k, (a, i) in enumerate(starts):
        if syms[i]['typ'] != 7:
            continue
        e = starts[k + 1][0] if k + 1 < len(starts) else len(code)
        befehle, q = [], a
        while q < e:
            op = code[q]
            if op in (61, 62, 64, 65, 67, 75, 76, 80):
                befehle.append((op, struct.unpack_from('<i', code, q + 1)[0], None)); q += 5
            elif op == 245:
                befehle.append((op, struct.unpack_from('<i', code, q + 1)[0], code[q + 5])); q += 6
            else:
                befehle.append((op, None, None)); q += 1
        zuege = [0] * 6
        for j, (op, arg, idx) in enumerate(befehle):
            if op == 9 and j >= 2:   # Zuweisung: Wert, Ziel, =
                (o1, a1, i1), (o2, a2, _) = befehle[j - 1], befehle[j - 2]
                if o1 in (65, 245) and a1 == feld:
                    if o2 == 64:
                        wert = a2
                    elif o2 == 65 and syms[a2]['content']:
                        wert = syms[a2]['content'][0]
                    else:
                        sys.exit('unerwarteter Wert in %s' % syms[i]['name'])
                    zuege[i1 if o1 == 245 else 0] = wert
        out[syms[i]['name'].upper()] = zuege
    return out


def fai(roh):
    """{FAI-Name: Nummer} aus GOTHIC.DAT"""
    syms, _ = lade(roh)
    return {s['name'].upper(): s['content'][0] for s in syms
            if s['name'].upper().startswith('FAI_') and s['typ'] == 2 and (s['flags'] & 1) and s['content']}


def bloecke(xeres):
    """[dict(taktik, lage, fai, name, regel, xr, neu)] - je Lage, die eine Regel aendert; xr = Xeres' 6 Zuege wie in FIGHT.DAT"""
    fight = tabellen(datei_aus(os.path.join(xeres, 'Data', 'Xeres_Scripts.mod'), 'FIGHT.DAT'))
    nummern = fai(datei_aus(skript_mod(xeres), 'GOTHIC.DAT'))
    liste, gesehen = [], set()
    for regel, taktiken, lagen, f in REGELN:
        for t in taktiken:
            if t not in nummern:
                sys.exit('%s fehlt in Xeres\' GOTHIC.DAT (Regel %s)' % (t, regel))
            for lage in lagen:
                s = LAGEN.index(lage)
                if (nummern[t], s) in gesehen:
                    sys.exit('%s %s: zwei Regeln fuer dieselbe Lage' % (t, lage))
                gesehen.add((nummern[t], s))
                xr = fight.get('FA_%s_%d' % (lage, nummern[t]), [0] * 6)
                neu = f([m for m in xr if m], t, lage)
                if len(neu) > 6 or not all(0 < m < 32 for m in neu):
                    sys.exit('%s %s: Regel %s gibt %s' % (t, lage, regel, neu))
                neu = neu + [0] * (6 - len(neu))
                if neu != xr:
                    liste.append(dict(taktik=nummern[t], lage=s, fai=t, name=lage, regel=regel, xr=xr, neu=neu))
    return sorted(liste, key=lambda b: (b['taktik'], b['lage']))


def daedalus(liste):
    zeilen = [ANFANG + ' (erzeugt von Werkzeuge\\gegnerki_regeln.py - nicht von Hand aendern) =====',
              '// Je Zeile: Kampftaktik (FAI_*), Lage (0-18 wie oCNpc::InitFightAI), neue Zuege, Zuege von Xeres, dahinter die Regel.',
              '// MOVE_*: 1 RUN, 3 JUMPBACK, 4 TURN, 5 STRAFE, 6 ATTACK, 7 SIDEATTACK, 8 FRONTATTACK, 9 TRIPLEATTACK, 10 WHIRLATTACK,',
              '// 11 MASTERATTACK, 17 PARADE, 19 WAIT, 23 WAIT_LONGER, 24 WAIT_EXT',
              'func int XRFIX_KiTabellen(var int nb)',
              '{',
              '\tvar int n; n = 0;']
    for b in liste:
        zeilen.append('\tn += XRFIX_KiBlock(nb, %d, %d, XRFIX_KiZuege(%s), XRFIX_KiZuege(%s));   // %s %s: %s' % (
            b['taktik'], b['lage'], ', '.join(str(z) for z in b['neu']), ', '.join(str(z) for z in b['xr']),
            b['fai'][4:], b['name'], b['regel']))
    zeilen += ['\treturn n;', '};', ENDE]
    return '\r\n'.join(zeilen)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--xeres', required=True)
    ap.add_argument('--schreiben', action='store_true')
    a = ap.parse_args()
    liste = bloecke(a.xeres)
    print('Lagen mit neuen Zuegen: %d in %d Taktiken' % (len(liste), len({b['taktik'] for b in liste})))
    for b in liste:
        print('  %2d %-16s %-18s %-22s %-40s -> %s' % (b['taktik'], b['fai'][4:], b['name'], b['regel'],
                                                       '/'.join(ZUEGE[z] for z in b['xr'] if z) or '-',
                                                       '/'.join(ZUEGE[z] for z in b['neu'] if z)))
    if a.schreiben:
        t = open(SKRIPT, 'rb').read().decode('cp1252')
        m = re.search(re.escape(ANFANG) + r'.*?' + re.escape(ENDE), t, re.S)
        if not m:
            sys.exit('Marken fuer die Tabellen fehlen in XERES_FIXES.D')
        t = t[:m.start()] + daedalus(liste) + t[m.end():]
        open(SKRIPT, 'wb').write(t.encode('cp1252'))
        print('geschrieben: %s (%d Lagen)' % (os.path.normpath(SKRIPT), len(liste)))


if __name__ == '__main__':
    main()
