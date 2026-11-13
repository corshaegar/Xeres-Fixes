META
{
  Parser = Menu;
  MergeMode = 1;
  Engine = G2A;
};

// Xeres-Fixes 1.4.0 fuer Xeres' Rueckkehr 1.0.9 (13.11.2026): Einstellungen "Gegner-KI" und "Nebengilden" unter Optionen -> Speziell
//
// Xeres' Seite MENU_OPT_XR bleibt, wie sie ist (MENU_OPT_XR_Old), ihre Zeilen -1 bis 5 auch. Dazu kommen zwei Zeilen: "Gegner-KI"
// ueber Autosave (Zeile -2, zwischen Ueberschrift und Autosave ist Platz) und "Nebengilden" unter Free Aim (Zeile 6). Die Liste
// der Eintraege ist neu geordnet - Gegner-KI, Xeres' Zeilen, Nebengilden, "Zurueck" -, damit die Pfeiltasten von oben nach unten
// laufen. Gothic speichert die Auswahl in der Gothic.ini unter [XERES_FIXES] gegnerki (0 = Xeres, 1 = New Balance) und
// nebengilden (0 = 4 wie im Original ... 5 = unbegrenzt). XERES_FIXES.D liest beide im laufenden Spiel neu - sie gelten sofort.

instance MENU_OPT_XR(C_MENU_DEF)
{
	MENU_OPT_XR_Old();
	items[1]  = "MENUITEM_XRFIX_GEGNERKI";
	items[2]  = "MENUITEM_XRFIX_GEGNERKI_CHOICE";
	items[3]  = "MENUITEM_XR_AUTOSAVE";
	items[4]  = "MENUITEM_XR_AUTOSAVE_CHOICE";
	items[5]  = "MENUITEM_XR_BALKEN";
	items[6]  = "MENUITEM_XR_BALKEN_CHOICE";
	items[7]  = "MENUITEM_XR_EXP";
	items[8]  = "MENUITEM_XR_EXP_CHOICE";
	items[9]  = "MENUITEM_XR_DIFFICULTY";
	items[10] = "MENUITEM_XR_DIFFICULTY_CHOICE";
	items[11] = "MENUITEM_XR_SPIELZEIT";
	items[12] = "MENUITEM_XR_SPIELZEIT_CHOICE";
	items[13] = "MENUITEM_XR_BLOODSPLATS";
	items[14] = "MENUITEM_XR_BLOODSPLATS_CHOICE";
	items[15] = "MENUITEM_OPT_GFA";
	items[16] = "MENUITEM_OPT_GFA_CHOICE";
	items[17] = "MENUITEM_XRFIX_NEBENGILDEN";
	items[18] = "MENUITEM_XRFIX_NEBENGILDEN_CHOICE";
	items[19] = "MENUITEM_XR_BACK";
};

instance MENUITEM_XRFIX_GEGNERKI(C_MENU_ITEM_DEF)
{
	backpic = MENU_ITEM_BACK_PIC;
	text[0] = "Gegner-KI";
	text[1] = "Nahkampf von Gegnern und NPCs: wie in Xeres (Original) oder in New Balance";
	posx = 1000;
	posy = MENU_START_Y - MENU_DY * 2;
	dimx = 3000;
	dimy = 750;
	onselaction[0] = SEL_ACTION_UNDEF;
	flags = flags | IT_EFFECTS_NEXT;
};

instance MENUITEM_XRFIX_GEGNERKI_CHOICE(C_MENU_ITEM_DEF)
{
	backpic = MENU_CHOICE_BACK_PIC;
	type = MENU_ITEM_CHOICEBOX;
	text[0] = "Xeres (Original)|New Balance";
	fontname = MENU_FONT_SMALL;
	posx = 5000;
	posy = MENU_START_Y - MENU_DY * 2 + MENU_CHOICE_YPLUS;
	dimx = MENU_SLIDER_DX;
	dimy = MENU_CHOICE_DY;
	onchgsetoption = "gegnerki";
	onchgsetoptionsection = "XERES_FIXES";
	flags = flags & ~IT_SELECTABLE;
	flags = flags | IT_TXT_CENTER;
};

instance MENUITEM_XRFIX_NEBENGILDEN(C_MENU_ITEM_DEF)
{
	backpic = MENU_ITEM_BACK_PIC;
	text[0] = "Nebengilden";
	text[1] = "Wie vielen Nebengilden du beitreten kannst (Original: 4)";
	posx = 1000;
	posy = MENU_START_Y + MENU_DY * 6;
	dimx = 3000;
	dimy = 750;
	onselaction[0] = SEL_ACTION_UNDEF;
	flags = flags | IT_EFFECTS_NEXT;
};

instance MENUITEM_XRFIX_NEBENGILDEN_CHOICE(C_MENU_ITEM_DEF)
{
	backpic = MENU_CHOICE_BACK_PIC;
	type = MENU_ITEM_CHOICEBOX;
	text[0] = "4 (Original)|5|6|7|8|unbegrenzt";
	fontname = MENU_FONT_SMALL;
	posx = 5000;
	posy = MENU_START_Y + MENU_DY * 6 + MENU_CHOICE_YPLUS;
	dimx = MENU_SLIDER_DX;
	dimy = MENU_CHOICE_DY;
	onchgsetoption = "nebengilden";
	onchgsetoptionsection = "XERES_FIXES";
	flags = flags & ~IT_SELECTABLE;
	flags = flags | IT_TXT_CENTER;
};
