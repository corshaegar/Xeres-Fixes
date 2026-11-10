META
{
  Parser = Game;
  MergeMode = 1;
  Engine = G2A;
};

// Xeres-Fixes 1.0.0: Zeiger-Pruefungen ueber 2 GB (10.11.2026)
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
// Entfernen: Xeres_Fixes.vdf aus Data loeschen.

const int XRFIX_PUSHINT = 64;
const int XRFIX_PUSHVAR = 65;
const int XRFIX_GT      = 8;
const int XRFIX_NE      = 17;

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

// Anfang des Bytecodes einer Funktion, 0 = gibt es nicht
func int XRFIX_Adresse(var string name)
{
	var int id; id = MEM_FindParserSymbol(name);
	if (id < 0) { return 0; };
	var int symPtr; symPtr = MEM_GetSymbolByIndex(id);
	if (!symPtr) { return 0; };
	var zCPar_Symbol s; s = _^(symPtr);
	return MEM_Parser.stack_stack + s.content;
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

// Die 20 Stellen aus Xeres' Rueckkehr 1.0.9 (Laengen = Groesse der Funktion im Skript)
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

// Die Engine ruft Init_Global bei jedem Spielstart und jedem Laden auf - danach ist Ikarus bereit (LeGo_Init)
func void Init_Global()
{
	Init_Global_Old();
	XRFIX_Zeiger();
};
