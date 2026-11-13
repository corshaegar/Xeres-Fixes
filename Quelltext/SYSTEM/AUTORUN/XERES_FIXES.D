META
{
  Parser = Game;
  MergeMode = 1;
  Engine = G2A;
};

// Xeres-Fixes 1.3.0 fuer Xeres' Rueckkehr 1.0.9 (13.11.2026)
//
// 1. Zeiger-Pruefungen ueber 2 GB (seit 1.0.0)
//
// Gothic2.exe ist Large-Address-Aware (bis 4 GB Speicher). Liegt ein Objekt oberhalb von 2 GB, ist sein Zeiger als
// Daedalus-int negativ. Xeres' Rueckkehr 1.0.9 prueft Zeiger an 20 Stellen mit "if (ptr > 0)" und haelt einen solchen
// Zeiger fuer NULL. Folgen:
//   - Weltwechsel per Schrein, Obelisk, Rune, Steinkreistafel oder Xardas-Ring: falsches Ziel oder Absturz (B_SetLevelChange)
//   - der Pass fuehrt nicht ins Minental (Init_NewWorld, Gespraech mit Hagen)
//   - die Tueren des Spinnenbaus bleiben zu, obwohl Vinos Gespraech ueber die Brennerei sie aufschliessen soll
//     (Info_Mod_Vino_Brennerei_Info); die Loren in der Eismine bekommen kein Tempo und keine Kollision (LoreEis*_LetsGo_*,
//     DauerFunc_01)
//   - Gegenstaende bleiben in Truhen, Objekte in der Welt (Mob_RemoveItems, MEM_RemoveVob, MEMINT_RemoveVob)
//
// Der Fix aendert keine Spiellogik. Beim Start stellt er in genau diesen Funktionen den Vergleich "> 0" auf "!= 0" um - ein
// Byte im geladenen Skriptcode (Opcode 8 -> 17), und nur, wenn die verglichene Variable einen Zeiger haelt (Name enthaelt
// PTR). 0 bedeutet weiterhin "nicht gefunden". Er laeuft bei jedem Start und Laden mit, ein zweiter Lauf findet nichts mehr.
// Ist eine Funktion per MergeMode ersetzt (z. B. durch den Teleport-Fix vom 17.10.), wird ihr Original <Name>_OLD umgestellt.
//
// 2. Absturz bei Fernkampftreffern mit Blutspritzern (neu in 1.1.0, ab 1.2.0 mit Blutspritzern fuer den echten Schaden)
//
// Xeres startet LeGo immer mit Blutspritzern. Xeres' eigene LeGo-Schleife setzt die Schadens-Wahrnehmung des Helden auf
// B_AssessDamage_Hero, und das ruft bei "Blutspritzer: an" (Vorgabe) nach dem eigenen Schaden selbst _B_HeroDamage auf - den
// Blutspritzer. Bringt ein Union-Plugin das Union-Toolkit mit (Data\Toolkit.vdf, LeGo 2.9 - es ersetzt Xeres' LeGo 2.5, indem
// es an den Anfang jeder alten Funktion einen Sprung auf die neue schreibt), setzt dessen _Bloodsplats_Loop die Wahrnehmung auf
// _B_HeroDamage, und das ruft danach die vorige auf - B_AssessDamage_Hero. Beide rufen sich dann gegenseitig auf. Bei einem
// Angreifer mit Bogen oder Armbrust geht das ohne Ende weiter: der Stapel laeuft ueber, das Spiel stuerzt ab.
//
// Der Fix gibt Xeres' alter Blutspritzer-Funktion (LeGo 2.5) den ersten Befehl zurueck, den das Toolkit durch den Sprung ersetzt
// hat. B_AssessDamage_Hero ruft dann wieder sie auf: Sie zeigt den Blutspritzer fuer den echten Schaden und ruft nichts zurueck.
// 1.1.0 machte den Aufruf nur zu einem Sprung auf den naechsten Befehl; dann zeigte allein LeGos neue Wahrnehmung einen
// Blutspritzer, und zwar vor dem Schaden der Mod - fast immer fuer 0 oder 1 Lebenspunkt, also so gut wie keinen. Passt das
// Muster nicht (andere Fassung), bleibt es beim Sprung: kein Absturz, aber kaum Blutspritzer. Nur, wenn das neuere LeGo die
// Wahrnehmung verkettet (dann gibt es _B_HeroDamagePercFunc); ohne Union-Toolkit aendert sich nichts.
//
// 3. Mehr als vier Nebengilden, einstellbar (neu in 1.3.0)
//
// Xeres' Rueckkehr laesst hoechstens vier Nebengilden zu (const MaxNebengilden = 4, gezaehlt in Mod_AnzahlNebengilden). Die
// Grenze ist jetzt eine Einstellung: Optionen -> Speziell -> Nebengilden, "4 (Original)|5|6|7|8|unbegrenzt", gespeichert in der
// Gothic.ini unter [XERES_FIXES] nebengilden (0 = 4 wie im Original, 1 = 5 ... 4 = 8, 5 = unbegrenzt). Vorgabe ist 4: Ohne
// Eintrag spielt sich Xeres wie bisher. Die Einstellung gilt sofort, auch im laufenden Spiel und wenn man schon vier
// Nebengilden hat. Was sich gegenseitig ausschliesst (Banditen oder Gardisten, Gardisten oder Koenigliche Garde, Miliz,
// Paladin ...), bleibt, wie es ist.
//
// Dazu ersetzt der Fix beim Start in den 22 Beitritts-Pruefungen ("Mod_AnzahlNebengilden < MaxNebengilden", bei Dexters
// Begruessung ">=") die Konstante durch einen Aufruf von XRFIX_MaxNebengilden, das die Einstellung bei jeder Pruefung liest:
// PUSHVAR MaxNebengilden -> CALL XRFIX_MaxNebengilden, beide 5 Bytes. Zwei Stellen nehmen "vier Nebengilden" als Freibrief,
// weil man danach keiner Gilde mehr beitreten konnte: die Belohnung fuer alle Beliar-Schreine (B_CheckAllTeleports - der Schrein
// in der Alten Mine zaehlt sonst nur fuer Waldlaeufer, der in der Kanalisation nur fuer Diebe) und Marios Aufstieg zum Ritter
// (NebenQuests, wenn man kein Assassine ist). Beide pruefen "genau vier" und waeren mit mehr Gilden nie mehr erfuellt; der Fix
// macht daraus "mindestens vier" (== -> >=, bei den Schreinen mit der Zahl 4 statt der Konstante). Bei hoechstens vier
// Nebengilden ist das dasselbe wie im Original.
//
// Vier Angebote macht Xeres nur ein einziges Mal: Sumpflager (Baal Namib nach den Sumpfhaizombies), Diebe (Cassia), Altes Lager
// (Scatty - der Weg zu den Gardisten) und das Versteck der Assassinen (Amir). Wer an einem davon mit voller Grenze vorbeikam,
// bekommt nach dem Erhoehen bei derselben Person eine zweite Gelegenheit - nur, solange die Einstellung ueber 4 steht.
//
// Entfernen: Xeres_Fixes.vdf aus Data loeschen.

const int XRFIX_PUSHINT = 64;
const int XRFIX_PUSHVAR = 65;
const int XRFIX_GT      = 8;
const int XRFIX_NE      = 17;
const int XRFIX_CALL    = 61;
const int XRFIX_JMP     = 75;
const int XRFIX_SETINST = 80;
const int XRFIX_SUB     = 1;
const int XRFIX_LT      = 7;
const int XRFIX_EQ      = 16;
const int XRFIX_GE      = 18;

// Haelt die Variable mit dieser Symbolnummer einen Zeiger? (Name enthaelt "PTR")
func int XRFIX_IstZeiger(var int sym)
{
	if (sym <= 0) { return FALSE; };
	var int symPtr; symPtr = MEM_GetSymbolByIndex(sym);
	if (!symPtr) { return FALSE; };
	var zCPar_Symbol s; s = _^(symPtr);
	if (STR_IndexOf(s.name, "PTR") >= 0) { return TRUE; };
	return FALSE;
};

// Anfang des Bytecodes einer Funktion relativ zum Skriptcode (Symbolinhalt), -1 = gibt es nicht
func int XRFIX_Inhalt(var string name)
{
	var int id; id = MEM_FindParserSymbol(name);
	if (id < 0) { return -1; };
	var int symPtr; symPtr = MEM_GetSymbolByIndex(id);
	if (!symPtr) { return -1; };
	var zCPar_Symbol s; s = _^(symPtr);
	return s.content;
};

// Anfang des Bytecodes einer Funktion im Speicher, 0 = gibt es nicht
func int XRFIX_Adresse(var string name)
{
	var int start; start = XRFIX_Inhalt(name);
	if (start < 0) { return 0; };
	return MEM_Parser.stack_stack + start;
};

// "PUSHINT 0; PUSHVAR <Zeiger>; >" im Bereich [adr, adr + laenge) auf "!=" umstellen, Anzahl zurueck
func int XRFIX_Bereich(var int adr, var int laenge)
{
	if (!adr) { return 0; };
	var int n; n = 0;
	var int i; i = 0;
	var int p;
	var int schleife; schleife = MEM_StackPos.position;
	if (i <= laenge - 11)
	{
		p = adr + i;
		if (MEM_ReadByte(p) == XRFIX_PUSHINT)
		{
			if (MEM_ReadInt(p + 1) == 0)
			{
				if (MEM_ReadByte(p + 5) == XRFIX_PUSHVAR)
				{
					if (MEM_ReadByte(p + 10) == XRFIX_GT)
					{
						if (XRFIX_IstZeiger(MEM_ReadInt(p + 6)))
						{
							MEM_WriteByte(p + 10, XRFIX_NE);
							n += 1;
						};
					};
				};
			};
		};
		i += 1;
		MEM_StackPos.position = schleife;
	};
	return n;
};

// Original einer Funktion umstellen: <Name>_OLD, falls per MergeMode ersetzt, sonst <Name>
func int XRFIX_Funktion(var string name, var int laenge)
{
	var int adr; adr = XRFIX_Adresse(ConcatStrings(name, "_OLD"));
	if (!adr) { adr = XRFIX_Adresse(name); };
	return XRFIX_Bereich(adr, laenge);
};

// 1. Die 20 Stellen aus Xeres' Rueckkehr 1.0.9 (Laengen = Groesse der Funktion im Skript)
func void XRFIX_Zeiger()
{
	var int n; n = 0;
	n += XRFIX_Funktion("B_SETLEVELCHANGE", 92);
	n += XRFIX_Funktion("INIT_NEWWORLD", 4973);
	n += XRFIX_Funktion("INFO_MOD_HAGEN_HI_INFO", 730);
	n += XRFIX_Funktion("INFO_MOD_VINO_BRENNEREI_INFO", 432);
	n += XRFIX_Funktion("LOREEISMINE01_LETSGO_S0", 154);
	n += XRFIX_Funktion("LOREEISMINE01_LETSGO_S1", 154);
	n += XRFIX_Funktion("LOREEISMINE02_LETSGO_S0", 154);
	n += XRFIX_Funktion("LOREEISMINE02_LETSGO_S1", 154);
	n += XRFIX_Funktion("LOREEISSW01_LETSGO_S0", 154);
	n += XRFIX_Funktion("LOREEISSW01_LETSGO_S1", 154);
	n += XRFIX_Funktion("LOREEISSW02_LETSGO_S0", 154);
	n += XRFIX_Funktion("LOREEISSW02_LETSGO_S1", 154);
	n += XRFIX_Funktion("DAUERFUNC_01", 13786);
	n += XRFIX_Funktion("MOB_REMOVEITEMS", 129);
	n += XRFIX_Funktion("MEM_REMOVEVOB", 66);
	n += XRFIX_Funktion("MEMINT_REMOVEVOB", 55);
	if (n > 0)
	{
		MEM_Info(ConcatStrings("Xeres-Fixes: Zeiger-Pruefungen umgestellt: ", IntToString(n)));
	};
};

// Laenge eines Daedalus-Befehls in Bytes
func int XRFIX_BefehlLaenge(var int op)
{
	if ((op == 61) || (op == 62) || (op == 64) || (op == 65) || (op == 67) || (op == 75) || (op == 76) || (op == 80)) { return 5; };
	if (op == 245) { return 6; };
	return 1;
};

// Ziel eines Aufrufs: Das Union-Toolkit ersetzt eine Funktion, indem es neuen Code anhaengt und an den alten Anfang einen Sprung
// dorthin schreibt - dem Sprung folgen (hoechstens 4-mal)
func int XRFIX_Aufloesen(var int ziel)
{
	var int k; k = 0;
	var int schleife; schleife = MEM_StackPos.position;
	if ((k < 4) && (ziel >= 0))
	{
		if (MEM_ReadByte(MEM_Parser.stack_stack + ziel) == XRFIX_JMP)
		{
			ziel = MEM_ReadInt(MEM_Parser.stack_stack + ziel + 1);
			k += 1;
			MEM_StackPos.position = schleife;
		};
	};
	return ziel;
};

// Steht bei ziel (Abstand zum Anfang des Skriptcodes) Xeres' alte Blutspritzer-Funktion (LeGo 2.5), an deren Anfang das
// Union-Toolkit einen Sprung geschrieben hat? Dahinter folgt unveraendert "PUSHVAR C_NPC.ATTRIBUTE, PUSHVAR HERO_LASTHP, SUB"
// (currDam = Hero_LastHP - Leben des Helden); der ueberschriebene erste Befehl war "SETINST HERO"
func int XRFIX_BlutAlt(var int ziel)
{
	if (ziel < 0) { return FALSE; };
	var int adr; adr = MEM_Parser.stack_stack + ziel;
	if (MEM_ReadByte(adr) != XRFIX_JMP) { return FALSE; };
	if (MEM_ReadByte(adr + 5) != XRFIX_PUSHVAR) { return FALSE; };
	if (MEM_ReadInt(adr + 6) != MEM_FindParserSymbol("C_NPC.ATTRIBUTE")) { return FALSE; };
	if (MEM_ReadByte(adr + 10) != XRFIX_PUSHVAR) { return FALSE; };
	if (MEM_ReadInt(adr + 11) != MEM_FindParserSymbol("HERO_LASTHP")) { return FALSE; };
	if (MEM_ReadByte(adr + 15) != XRFIX_SUB) { return FALSE; };
	if (MEM_FindParserSymbol("HERO") < 0) { return FALSE; };
	return TRUE;
};

// Aufrufe von _B_HeroDamage im Original einer Funktion (Befehl fuer Befehl): Geht der Aufruf an die alte Fassung, die das Toolkit
// per Sprung umleitet, bekommt sie ihren ersten Befehl zurueck, und der Aufruf bleibt (zaehlt 1000). Sonst wird er zu einem Sprung
// auf den naechsten Befehl (zaehlt 1). Keine globale Variable - die gaebe ein Coop an den Mitspieler weiter
func int XRFIX_BlutFunktion(var string name, var int laenge)
{
	var int start; start = XRFIX_Inhalt(ConcatStrings(name, "_OLD"));
	if (start < 0) { start = XRFIX_Inhalt(name); };
	if (start < 0) { return 0; };
	var int z1; z1 = XRFIX_Inhalt("_B_HERODAMAGE");
	var int z2; z2 = XRFIX_Inhalt("_B_HERODAMAGE_OLD");
	var int adr; adr = MEM_Parser.stack_stack + start;
	var int n; n = 0;
	var int q; q = 0;
	var int op;
	var int direkt;
	var int ziel;
	var int schleife; schleife = MEM_StackPos.position;
	if (q < laenge - 4)
	{
		op = MEM_ReadByte(adr + q);
		if (op == XRFIX_CALL)
		{
			direkt = MEM_ReadInt(adr + q + 1);
			ziel = XRFIX_Aufloesen(direkt);
			if (((ziel == z1) && (z1 >= 0)) || ((ziel == z2) && (z2 >= 0)))
			{
				if ((direkt != ziel) && XRFIX_BlutAlt(direkt))
				{
					MEM_WriteByte(MEM_Parser.stack_stack + direkt, XRFIX_SETINST);
					MEM_WriteInt(MEM_Parser.stack_stack + direkt + 1, MEM_FindParserSymbol("HERO"));
					n += 1000;
				}
				else
				{
					MEM_WriteByte(adr + q, XRFIX_JMP);
					MEM_WriteInt(adr + q + 1, start + q + 5);
					n += 1;
				};
			};
		};
		q += XRFIX_BefehlLaenge(op);
		MEM_StackPos.position = schleife;
	};
	return n;
};

// 2. Blutspritzer-Schleife - nur, wenn ein LeGo ab 2.8 die Schadens-Wahrnehmung des Helden verkettet
func void XRFIX_Blut()
{
	if (MEM_FindParserSymbol("_B_HERODAMAGEPERCFUNC") < 0) { return; };
	var int n; n = XRFIX_BlutFunktion("B_ASSESSDAMAGE_HERO", 12486);
	if (n >= 1000)
	{
		MEM_Info("Xeres-Fixes: Blutspritzer-Schleife behoben - B_AssessDamage_Hero ruft wieder Xeres' eigene Blutspritzer-Funktion");
	}
	else if (n > 0)
	{
		MEM_Info(ConcatStrings("Xeres-Fixes: Blutspritzer-Schleife entschaerft (B_AssessDamage_Hero): ", IntToString(n)));
	};
};

// 3. Nebengilden

const int XRFIX_NEBENGILDEN = 4;   // Grenze im Original

// Grenze aus der Gothic.ini, [XERES_FIXES] nebengilden = Nummer der Auswahl im Menue: 0 = 4 (Original) ... 4 = 8, 5 = unbegrenzt.
// Fehlt der Eintrag oder steht etwas anderes dort, gilt 4. Wird bei jeder Pruefung neu gelesen - eine Aenderung im Menue gilt sofort
func int XRFIX_MaxNebengilden()
{
	var string w; w = MEM_GetGothOpt("XERES_FIXES", "nebengilden");
	if (Hlp_StrCmp(w, "1")) { return 5; };
	if (Hlp_StrCmp(w, "2")) { return 6; };
	if (Hlp_StrCmp(w, "3")) { return 7; };
	if (Hlp_StrCmp(w, "4")) { return 8; };
	if (Hlp_StrCmp(w, "5")) { return 99; };
	return XRFIX_NEBENGILDEN;
};

// Vergleiche mit der Grenze im Original einer Funktion (bzw. <Name>_OLD) umstellen, Befehl fuer Befehl:
//   PUSHVAR MaxNebengilden; PUSHVAR Mod_AnzahlNebengilden; < oder >=  ->  CALL XRFIX_MaxNebengilden; (Rest bleibt)
//   PUSHVAR MaxNebengilden; PUSHVAR Mod_AnzahlNebengilden; ==         ->  PUSHINT 4; PUSHVAR Mod_AnzahlNebengilden; >=
//   PUSHINT 4;              PUSHVAR Mod_AnzahlNebengilden; ==         ->  PUSHINT 4; PUSHVAR Mod_AnzahlNebengilden; >=
// Anzahl der Stellen zurueck; ein zweiter Lauf findet nichts mehr
func int XRFIX_NebengildenFunktion(var string name, var int laenge)
{
	var int start; start = XRFIX_Inhalt(ConcatStrings(name, "_OLD"));
	if (start < 0) { start = XRFIX_Inhalt(name); };
	if (start < 0) { return 0; };
	var int grenze; grenze = MEM_FindParserSymbol("MAXNEBENGILDEN");
	var int anzahl; anzahl = MEM_FindParserSymbol("MOD_ANZAHLNEBENGILDEN");
	var int aufruf; aufruf = XRFIX_Inhalt("XRFIX_MAXNEBENGILDEN");
	if ((grenze < 0) || (anzahl < 0) || (aufruf < 0)) { return 0; };
	var int adr; adr = MEM_Parser.stack_stack + start;
	var int n; n = 0;
	var int q; q = 0;
	var int op;
	var int p;
	var int wert;
	var int vgl;
	var int schleife; schleife = MEM_StackPos.position;
	if (q < laenge - 10)
	{
		p = adr + q;
		op = MEM_ReadByte(p);
		if ((op == XRFIX_PUSHVAR) || (op == XRFIX_PUSHINT))
		{
			if (MEM_ReadByte(p + 5) == XRFIX_PUSHVAR)
			{
				if (MEM_ReadInt(p + 6) == anzahl)
				{
					wert = MEM_ReadInt(p + 1);
					vgl = MEM_ReadByte(p + 10);
					if ((op == XRFIX_PUSHVAR) && (wert == grenze))
					{
						if ((vgl == XRFIX_LT) || (vgl == XRFIX_GE))
						{
							MEM_WriteByte(p, XRFIX_CALL);
							MEM_WriteInt(p + 1, aufruf);
							n += 1;
						}
						else if (vgl == XRFIX_EQ)
						{
							MEM_WriteByte(p, XRFIX_PUSHINT);
							MEM_WriteInt(p + 1, XRFIX_NEBENGILDEN);
							MEM_WriteByte(p + 10, XRFIX_GE);
							n += 1;
						};
					}
					else if ((op == XRFIX_PUSHINT) && (wert == XRFIX_NEBENGILDEN) && (vgl == XRFIX_EQ))
					{
						MEM_WriteByte(p + 10, XRFIX_GE);
						n += 1;
					};
				};
			};
		};
		q += XRFIX_BefehlLaenge(op);
		MEM_StackPos.position = schleife;
	};
	return n;
};

// 3. Die 24 Funktionen mit der Grenze aus Xeres' Rueckkehr 1.0.9 (Laengen = Groesse der Funktion im Skript), 25 Stellen
func void XRFIX_Nebengilden()
{
	var int n; n = 0;
	n += XRFIX_NebengildenFunktion("B_CHECKALLTELEPORTS", 268);
	n += XRFIX_NebengildenFunktion("NEBENQUESTS", 31664);
	n += XRFIX_NebengildenFunktion("INFO_MOD_AMIR_HI_CONDITION", 96);
	n += XRFIX_NebengildenFunktion("INFO_MOD_AMIR_LEHMAR_INFO", 422);
	n += XRFIX_NebengildenFunktion("INFO_MOD_CASSIA_AUFNAHME_INFO", 364);
	n += XRFIX_NebengildenFunktion("INFO_MOD_DEXTER_AUFNAHME_CONDITION", 51);
	n += XRFIX_NebengildenFunktion("INFO_MOD_DEXTER_HI_INFO", 295);
	n += XRFIX_NebengildenFunktion("INFO_MOD_DRAGOMIR_AUFNAHME_CONDITION", 35);
	n += XRFIX_NebengildenFunktion("INFO_MOD_DRAGOMIR_JAGDGEBIETE_GAAN", 259);
	n += XRFIX_NebengildenFunktion("INFO_MOD_DRAGOMIR_JAGDGEBIETE_GRIMBALD", 400);
	n += XRFIX_NebengildenFunktion("INFO_MOD_DRAGOMIR_JAGDGEBIETE_GROM", 239);
	n += XRFIX_NebengildenFunktion("INFO_MOD_DRAGOMIR_JAGDGEBIETE_NANDOR", 349);
	n += XRFIX_NebengildenFunktion("INFO_MOD_FAICE_AUFNAHME_CONDITION", 39);
	n += XRFIX_NebengildenFunktion("INFO_MOD_FAICE_MUD_A", 187);
	n += XRFIX_NebengildenFunktion("INFO_MOD_GREG_AUFNAHME_CONDITION", 39);
	n += XRFIX_NebengildenFunktion("INFO_MOD_GREG_SCHATZSUCHE_INFO", 242);
	n += XRFIX_NebengildenFunktion("INFO_MOD_NAMIB_SUDD_INFO", 528);
	n += XRFIX_NebengildenFunktion("INFO_MOD_OLE_BEITRITT_CONDITION", 80);
	n += XRFIX_NebengildenFunktion("INFO_MOD_OLE_WARBEIANDRE_INFO", 333);
	n += XRFIX_NebengildenFunktion("INFO_MOD_SCATTY_HILFE_INFO", 177);
	n += XRFIX_NebengildenFunktion("INFO_MOD_SHAKIR_GAUNERWERDEN2_INFO", 268);
	n += XRFIX_NebengildenFunktion("INFO_MOD_SHAKIR_GAUNERWERDEN3_CONDITION", 39);
	n += XRFIX_NebengildenFunktion("INFO_MOD_THORUS_AUFNAHME_CONDITION", 80);
	n += XRFIX_NebengildenFunktion("INFO_MOD_THORUS_ZETTEL_INFO", 243);
	if (n > 0)
	{
		MEM_Info(ConcatStrings("Xeres-Fixes: Nebengilden-Grenze einstellbar, Stellen umgestellt: ", IntToString(n)));
	};
};

// Zweite Gelegenheit fuer die vier Angebote, die Xeres nur einmal macht: nur bei einer Einstellung ueber 4 und mit freiem Platz
func int XRFIX_NebengildeFrei()
{
	var int grenze; grenze = XRFIX_MaxNebengilden();
	if ((grenze > XRFIX_NEBENGILDEN) && (Mod_AnzahlNebengilden < grenze)) { return TRUE; };
	return FALSE;
};

// Sumpflager: Baal Namib bietet Guru oder Templer nur einmal an (Info_Mod_Namib_SUDD, nach den Sumpfhaizombies)
instance Info_XRFIX_Namib_Nebengilde(C_INFO)
{
	npc         = Mod_2004_GUR_BaalNamib_MT;
	nr          = 900;
	condition   = Info_XRFIX_Namib_Nebengilde_Condition;
	information = Info_XRFIX_Namib_Nebengilde_Info;
	permanent   = TRUE;
	description = "Ich will doch noch der Bruderschaft beitreten.";
};

func int Info_XRFIX_Namib_Nebengilde_Condition()
{
	if (Npc_KnowsInfo(hero, Info_Mod_Namib_SUDD) && (Guru_Dabei == FALSE) && (Templer_Dabei == FALSE) && XRFIX_NebengildeFrei())
	{
		return TRUE;
	};
	return FALSE;
};

func void Info_XRFIX_Namib_Nebengilde_Info()
{
	Info_ClearChoices(Info_XRFIX_Namib_Nebengilde);
	Info_AddChoice(Info_XRFIX_Namib_Nebengilde, "Lieber doch nicht.", Info_XRFIX_Namib_Nebengilde_Nein);
	Info_AddChoice(Info_XRFIX_Namib_Nebengilde, "Ich will Guru werden.", Info_XRFIX_Namib_Nebengilde_Guru);
	Info_AddChoice(Info_XRFIX_Namib_Nebengilde, "Ich will Templer werden.", Info_XRFIX_Namib_Nebengilde_Templer);
};

func void Info_XRFIX_Namib_Nebengilde_Nein()
{
	Info_ClearChoices(Info_XRFIX_Namib_Nebengilde);
};

func void Info_XRFIX_Namib_Nebengilde_Guru()
{
	Info_Mod_Namib_SUDD_Guru();
	Info_ClearChoices(Info_XRFIX_Namib_Nebengilde);
};

func void Info_XRFIX_Namib_Nebengilde_Templer()
{
	Info_Mod_Namib_SUDD_Templer();
	Info_ClearChoices(Info_XRFIX_Namib_Nebengilde);
};

// Diebe: Cassia nimmt einen nur im ersten Gespraech auf (Info_Mod_Cassia_Aufnahme), nicht als Paladin
instance Info_XRFIX_Cassia_Nebengilde(C_INFO)
{
	npc         = Mod_568_NONE_Cassia_NW;
	nr          = 900;
	condition   = Info_XRFIX_Cassia_Nebengilde_Condition;
	information = Info_XRFIX_Cassia_Nebengilde_Info;
	permanent   = TRUE;
	description = "Ich will doch einer von euch Dieben werden.";
};

func int Info_XRFIX_Cassia_Nebengilde_Condition()
{
	if (Npc_KnowsInfo(hero, Info_Mod_Cassia_Aufnahme) && (Diebe_Dabei == FALSE) && (hero.guild != GIL_PAL) && XRFIX_NebengildeFrei())
	{
		return TRUE;
	};
	return FALSE;
};

func void Info_XRFIX_Cassia_Nebengilde_Info()
{
	Info_Mod_Cassia_Aufnahme_Ja();
};

// Altes Lager: Scatty fragt nur einmal, ob man hilft (Info_Mod_Scatty_Hilfe) - der Weg zu den Gardisten
instance Info_XRFIX_Scatty_Nebengilde(C_INFO)
{
	npc         = Mod_962_STT_Scatty_MT;
	nr          = 900;
	condition   = Info_XRFIX_Scatty_Nebengilde_Condition;
	information = Info_XRFIX_Scatty_Nebengilde_Info;
	permanent   = TRUE;
	description = "Ich helfe euch doch.";
};

func int Info_XRFIX_Scatty_Nebengilde_Condition()
{
	if (Npc_KnowsInfo(hero, Info_Mod_Scatty_Hilfe) && (Scatty_Start_Dia != 5) && XRFIX_NebengildeFrei())
	{
		return TRUE;
	};
	return FALSE;
};

func void Info_XRFIX_Scatty_Nebengilde_Info()
{
	B_SetTopicStatus(TOPIC_MOD_ALTESLAGER, LOG_RUNNING);
	Info_Mod_Scatty_Hilfe_A();
};

// Assassinen: Amir bietet den Weg zum Versteck nur einmal an (Info_Mod_Amir_Lehmar)
instance Info_XRFIX_Amir_Nebengilde(C_INFO)
{
	npc         = Mod_7199_ASS_Amir_NW;
	nr          = 900;
	condition   = Info_XRFIX_Amir_Nebengilde_Condition;
	information = Info_XRFIX_Amir_Nebengilde_Info;
	permanent   = TRUE;
	description = "Bring mich doch zum Versteck der Assassinen.";
};

func int Info_XRFIX_Amir_Nebengilde_Condition()
{
	if (Npc_KnowsInfo(hero, Info_Mod_Amir_Lehmar) && (Mod_Ass_AmirLehmar == 1) && XRFIX_NebengildeFrei())
	{
		return TRUE;
	};
	return FALSE;
};

func void Info_XRFIX_Amir_Nebengilde_Info()
{
	Info_Mod_Amir_Lehmar_A();
};

// Die Engine ruft Init_Global bei jedem Spielstart und jedem Laden auf - danach ist Ikarus bereit (LeGo_Init)
func void Init_Global()
{
	Init_Global_Old();
	XRFIX_Zeiger();
	XRFIX_Blut();
	XRFIX_Nebengilden();
};
