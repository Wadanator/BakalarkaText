# AI Kontext a logy z konverzácií

Tento súbor slúži ako dlhodobá pamäť pre AI asistenta, aby nestratil prehľad o aktuálnych rozhodnutiach a špecifikách projektu počas vypracovávania bakalárskej práce.

## 07. Marec 2026 - Úvodné nastavenie a štruktúra
1. **Analýza dokumentácie:** AI načítala 12 referenčných markdown súborov zo zložky `Instructions_READ_FIRST`. Súbor `General_text_instruction.md` prísne vyžaduje lievikový prístup, trpný rod a nulovú toleranciu halucinácií! Písať len fakty doložené dokumentáciou.
2. **Štruktúra práce a modularita:** Existujúci LaTeX systém pomocou `\input{}` bol zhodnotený ako výborný a nie je potrebné ho meniť. Vytvorená „Štruktúra plus“ (artefakt) pre cielené písanie obsahu.
3. **Mechatronické zameranie (DÔLEŽITÉ):** 
   - Používateľ je študent mechatroniky.
   - Vo výstupnom texte minimalizovať čistý programátorský kód. Softvér vysvetľovať primárne pomocou vývojových diagramov, diagramností tried a stavových schém.
   - Pri hardvéri nie je cieľom ísť do absurdných detailov nízkoúrovňovej fyziky (prúdy/napätia až na súčiastku), ale skôr obhájiť **inžiniersky prístup**: Preferuje sa spájanie a systémová integrácia hotových, otestovaných a komerčne dostupných modulov pre maximalizáciu prevádzkovej spoľahlivosti.
4. **Hardvérová úprava (Relé modul):** Systém využíva klasické mechanické relé (Waveshare modul), nie SSR. Hlavný argument pre túto voľbu v texte: ide o plne osadený, preverený a bezpečný komerčný modul, čo je z pohľadu spoľahlivosti lepšie riešenie ako navrhovať vlastné neotestované riešenia s holými SSR súčiastkami.
5. **Rešpektovanie LaTeX šablóny:** Práca sa drží striktne predpísanej .tex šablóny, do ktorej je používateľ viazaný (napr. príkazy nad \begin{document} a štýlovanie kapitol). Nikdy neupravovať fonty, okraje, riadkovanie ani prednastavenú úpravu prostredia! Zásahy sa robia výhradne do obsahovej (textovej) časti dokumentov.
6. **Formát pre fázu schvaľovania štruktúry:** Kým vedúci schvaľuje osnovu, .tex súbory nemajú obsahovať prehnane dlhé súvislé texty. Využíva sa odrážkový systém (`\begin{itemize}`), tučné písmo (`\textbf{}`) pre kľúčové slová a krátke jasné vety na odprezentovanie logiky. Dôvodom je vizuálna prehľadnosť pre rýchle čítanie a taktiež prísny celkový limit na dokument (max 60 strán rozsah celej BP).
