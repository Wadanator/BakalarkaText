# TO-DO pred finálnym odovzdaním

## 1. Chýbajúce obrázky

---

## 4. Experimenty — nedostatočné dáta

- [ ] **Test obnovy po výpadku**: uvedený len priemer 38 s — doplniť **n** (koľkokrát sa testovalo), min, max.
- [ ] **Laboratórny test logiky**: *"spúšťala sa niekoľkokrát"* — nahradiť konkrétnym číslom.
- [ ] **Presnosť prepínania**: *"za celú sekvenciu"* — uviesť počet prechodov (n), aby bol drift interpretovateľný.
- [ ] **Záver** tvrdí *"systém bežal niekoľko dní bez reštartu"* — toto v kapitole Experimenty nie je podložené žiadnym testom. Buď pridať dlhodobý stabilitný test (napr. log z reálnej prevádzky), alebo toto tvrdenie zo Záveru odstrániť.

## 8. Kódové identifikátory v próze (porušenie General_text_instruction)

Pravidlo: *"No code identifiers in prose"* — v texte sa priamo objavujú tieto kódové názvy:

Všetky nahradiť opisom funkcie (napr. namiesto "`force_all_off()`" napísať *"operácia núteného vypnutia všetkých výstupov"*).sk

## 11. Experimenty — doplnenie textu

- [ ] **Výpadok napájania — n, min, max**: nájdi *"obnovil do funkčného v priemere za 38 sekúnd"* → nahradiť za *"obnovil do funkčného stavu v~priemere za 38 sekúnd (n\,=\,5 meraní, min\,=\,34\,s, max\,=\,43\,s)"* — doplniť reálne hodnoty.
- [ ] **Soft real-time klasifikácia**: za sekciu Zhodnotenie, pred záverečnou vetou, pridať `\subsection*{Klasifikácia časového správania systému}` — systém zaradiť do kategórie soft real-time (priemerná odozva 111,7 ms, max 219 ms, drift 2,3 %, `\cite{distributed_control_modeling}`).

---

## 12. Využitie generatívnej AI — doplniť do BP (VUT norma)

To čo je v `\acknowledgements` nestačí — je to správny obsah, ale nesprávne miesto.

- [ ] **Pridať sekciu do tela práce** — krátky odstavec s nadpisom `\section*{Využitie generatívnej umelej inteligencie}`, umiestniť za `\abstract{...}` alebo pred `\input{chapters/Uvod.tex}`. Návrh textu je pripravený (Claude, GitHub Copilot, jan.–máj 2026, účel, overenie).
- [ ] **Pridať Prílohu A** — tabuľka evidencie (nástroj, obdobie, účel, overenie), umiestniť za `\input{chapters/Literatura.tex}`. Návrh LaTeX kódu je pripravený.

---

## 10. Drobnosti

- [ ] **"Vite" bez vysvetlenia**: `Implementacia_sw.tex` — *"Frontend je realizovaný ako React SPA (Vite)"* — Vite je build nástroj, nie framework; pri prvom použití doplniť jednoslušnú charakteristiku v zátvorke.
