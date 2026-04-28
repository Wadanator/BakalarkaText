# TO-DO pred finálnym odovzdaním

## 1. Chýbajúce obrázky

Súbory sú referencované v texte, ale neexistujú:

- [ ] `obr/HW/chronos_celok.jpg` — fotka celej inštalácie CHRONOS (`Implementacia_hw.tex`, fig. chronos_celok)
- [ ] `obr/HW/kotol_exponat.jpg` — fotka parného kotla s elektronikou (`Implementacia_hw.tex`, fig. kotol_exponat)
- [ ] Diagram 5_7 (ESP32 porovnávacia schéma) — v texte je len `\fbox{MIESTO PRE OBRÁZOK}`, existuje iba `diagram_spec.md`. Buď diagram dorob, alebo fbox nahraď tabuľkou.

---

## 4. Experimenty — nedostatočné dáta

- [ ] **Test obnovy po výpadku**: uvedený len priemer 38 s — doplniť **n** (koľkokrát sa testovalo), min, max.
- [ ] **Laboratórny test logiky**: *"spúšťala sa niekoľkokrát"* — nahradiť konkrétnym číslom.
- [ ] **Presnosť prepínania**: *"za celú sekvenciu"* — uviesť počet prechodov (n), aby bol drift interpretovateľný.
- [ ] **Záver** tvrdí *"systém bežal niekoľko dní bez reštartu"* — toto v kapitole Experimenty nie je podložené žiadnym testom. Buď pridať dlhodobý stabilitný test (napr. log z reálnej prevádzky), alebo toto tvrdenie zo Záveru odstrániť.

## 8. Kódové identifikátory v próze (porušenie General_text_instruction)

Pravidlo: *"No code identifiers in prose"* — v texte sa priamo objavujú tieto kódové názvy:

- [ ] `MQTTActuatorStateStore`, `force_all_off()` — `Implementacia_sw.tex`, sekcia o sledovaní aktuátorov
- [ ] `threading.Timer` — `Implementacia_sw.tex`, sekcia o JSON konfigurácii
- [ ] `sfx_` (prefix) — `Implementacia_sw.tex`, sekcia o mediálnej vrstve
- [ ] `ServiceContainer` — `Implementacia_sw.tex`, sekcia o orchestrácii
- [ ] `MuseumController`, `all_relays_loop_test` — `Experimenty.tex`

Všetky nahradiť opisom funkcie (napr. namiesto "`force_all_off()`" napísať *"operácia núteného vypnutia všetkých výstupov"*).

---

## 9. Experimenty — chyby v interpretácii

- [ ] **Chýba porovnanie s literatúrou**: rešerše uvádza MQTT latenciu 11,04 ms (zdroj `mqtt_websocket_comparison`), namerané je 111,7 ms — teda 10× viac. Rozdiel je pochopiteľný (iné podmienky: feedback round-trip vs. jednosmerná latencia), ale mal by byť v diskusii vysvetlený, inak to pôsobí ako rozpor s vlastnou rešeršou.

---

## 11. Experimenty — doplnenie textu

- [ ] **Laboratórny test — počet spustení**: nájdi *"sa spúšťala niekoľkokrát v~rôznych časoch v priebehu desiatich dní"* → nahradiť za *"sa spúšťala celkovo **N-krát** v~rôznych časoch v~priebehu desiatich dní"* — doplniť reálne číslo.
- [ ] **Výpadok napájania — n, min, max**: nájdi *"obnovil do funkčného v priemere za 38 sekúnd"* → nahradiť za *"obnovil do funkčného stavu v~priemere za 38 sekúnd (n\,=\,5 meraní, min\,=\,34\,s, max\,=\,43\,s)"* — doplniť reálne hodnoty.
- [ ] **Presnosť prepínania — počet prechodov**: nájdi *"za celú sekveniu 1\,317\,ms;"* → nahradiť za *"za celú sekvenciu 1\,317\,ms pri **232 prechodoch**;"* — overiť/doplniť presné číslo (232 = 1824 príkazov / 8 výstupov + réžia).
- [ ] **Soft real-time klasifikácia**: za sekciu Zhodnotenie, pred záverečnou vetou, pridať `\subsection*{Klasifikácia časového správania systému}` — systém zaradiť do kategórie soft real-time (priemerná odozva 111,7 ms, max 219 ms, drift 2,3 %, `\cite{distributed_control_modeling}`).
- [ ] **Porovnanie s literatúrou — MQTT latencia**: do sekcie Meranie latencie, za tabuľku, pridať vysvetlenie: literatúra uvádza jednosmernú latenciu 11,04 ms (`mqtt_websocket_comparison`), namerané 111,7 ms je round-trip (RPi → ESP32 → RPi) — rozdiel treba explicitne vysvetliť v texte.

---

## 10. Drobnosti

- [ ] **"Vite" bez vysvetlenia**: `Implementacia_sw.tex` — *"Frontend je realizovaný ako React SPA (Vite)"* — Vite je build nástroj, nie framework; pri prvom použití doplniť jednoslušnú charakteristiku v zátvorke.
