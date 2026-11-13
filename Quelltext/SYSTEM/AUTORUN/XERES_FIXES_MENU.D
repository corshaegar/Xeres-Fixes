META
{
  Parser = Menu;
  MergeMode = 1;
  Engine = G2A;
};

// Xeres-Fixes 1.3.0 fuer Xeres' Rueckkehr 1.0.9 (13.11.2026): Einstellung "Nebengilden" unter Optionen -> Speziell
//
// Xeres' Seite MENU_OPT_XR bleibt, wie sie ist (MENU_OPT_XR_Old). Dazu kommt eine Zeile unter Free Aim (Zeile 6, die Seite hat
// Zeilen -1 bis 5); "Zurueck" steht danach weiter unten in der Liste, damit die Pfeiltasten in der richtigen Reihenfolge laufen.
// Gothic speichert die Auswahl in der Gothic.ini unter [XERES_FIXES] nebengilden (0 = 4 wie im Original ... 5 = unbegrenzt).
// XERES_FIXES.D liest den Wert bei jeder Beitritts-Pruefung neu - die Einstellung gilt sofort, auch im laufenden Spiel.

instance MENU_OPT_XR(C_MENU_DEF)
{
	MENU_OPT_XR_Old();
	items[15] = "MENUITEM_XRFIX_NEBENGILDEN";
	items[16] = "MENUITEM_XRFIX_NEBENGILDEN_CHOICE";
	items[17] = "MENUITEM_XR_BACK";
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
