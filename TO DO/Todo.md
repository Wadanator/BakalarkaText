# TO-DO pred finálnym odovzdaním

## 1. Chýbajúce obrázky

Súbory sú referencované v texte, ale neexistujú:

- [ ] `obr/HW/relay_schema.pdf` — schéma relé uzla (`Implementacia_hw.tex`, fig. relay_schema)
- [ ] `obr/HW/chronos_celok.jpg` — fotka celej inštalácie CHRONOS (`Implementacia_hw.tex`, fig. chronos_celok)
- [ ] `obr/HW/kotol_exponat.jpg` — fotka parného kotla s elektronikou (`Implementacia_hw.tex`, fig. kotol_exponat)
- [ ] Diagram 5_7 (ESP32 porovnávacia schéma) — v texte je len `\fbox{MIESTO PRE OBRÁZOK}`, existuje iba `diagram_spec.md`. Buď diagram dorob, alebo fbox nahraď tabuľkou.

---

## 2. Abstrakt

- [ ] Začína frázou *"Táto bakalárska práca sa zaoberá..."* — podľa General_text_instruction je táto fráza explicitne zakázaná. Prepísať prvú vetu tak, aby začínala priamo kľúčovým pojmom (napr. *"Modulárne riadenie interaktívnych múzejných expozícií..."*).

---

## 3. Úvod

- [ ] Veta *"Funkčnosť systému je v závere práce demonštrovaná na prototypovej miestnosti..."* patrí do Záveru, nie do Úvodu — výsledky do Úvodu nepatria. Odstrániť alebo preformulovať.
- [ ] Chýba explicitná **medzera (Gap)**: prechod z „čo existuje" na „čo robíme" je príliš priamy. Doplniť jednu vetu — čo konkrétne existujúce riešenia nevedia, a prečo si to vyžiadalo vlastný vývoj.

---

## 4. Experimenty — nedostatočné dáta

- [ ] **Test obnovy po výpadku**: uvedený len priemer 38 s — doplniť **n** (koľkokrát sa testovalo), min, max.
- [ ] **Laboratórny test logiky**: *"spúšťala sa niekoľkokrát"* — nahradiť konkrétnym číslom.
- [ ] **Presnosť prepínania**: *"za celú sekvenciu"* — uviesť počet prechodov (n), aby bol drift interpretovateľný.
- [ ] **Záver** tvrdí *"systém bežal niekoľko dní bez reštartu"* — toto v kapitole Experimenty nie je podložené žiadnym testom. Buď pridať dlhodobý stabilitný test (napr. log z reálnej prevádzky), alebo toto tvrdenie zo Záveru odstrániť.

---

## 5. Citácie

- [ ] `\cite{noural2019iot}` je použité na podporu tvrdenia o vendor lock-in show-control systémov, ale zdroj je článok o software-defined networking — nesúvisí. Nájsť priamejší zdroj alebo citáciu odstrániť.
- [ ] BTS7960B *"do 43 A"* — chýba citácia datasheetu (Infineon BTS7960B datasheet).

---

## 6. Drobná logická nejasnosť

- [ ] V sekcii o reléovom uzle je zmienka, že Waveshare modul obsahuje *"natívnu podporu pre PoE a RS485"* — tieto funkcie neboli využité a ich zmienka bez vysvetlenia mätie čitateľa. Buď doplniť jednovetnové vysvetlenie, alebo celú vetu odstrániť.

---

## 7. Chýbajúca kľúčová implementačná informácia

- [ ] **MQTT broker nie je nikde identifikovaný** — celá komunikácia prebieha cez broker, ale text nikde neuvádza, aký softvér broker zabezpečuje (Mosquitto? EMQX?), kde beží (na Raspberry Pi?) ani ako je nakonfigurovaný. Doplniť aspoň jednu vetu v kapitole Implementácia SW alebo Architektúra.
- [ ] **Video prehrávač nie je pomenovaný** — `Implementacia_sw.tex`: *"Video vrstva je realizovaná cez externý prehrávač riadený IPC rozhraním"* — ktorý prehrávač? (napr. VLC, mpv, omxplayer). Konkrétny nástroj uviesť.

---

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

- [ ] Sekcia *Meranie latencie* prepisuje čísla z tabuľky do textu (*"Najrýchlejšie odpovedali výstupy room1/light/1 a room1/light/2 (priemer okolo 82 ms)..."*) — podľa General_text_instruction sa na tabuľku len odkazuje, text má ísť priamo k interpretácii. Preformulovať.
- [ ] **Chýba porovnanie s literatúrou**: rešerše uvádza MQTT latenciu 11,04 ms (zdroj `mqtt_websocket_comparison`), namerané je 111,7 ms — teda 10× viac. Rozdiel je pochopiteľný (iné podmienky: feedback round-trip vs. jednosmerná latencia), ale mal by byť v diskusii vysvetlený, inak to pôsobí ako rozpor s vlastnou rešeršou.
- [ ] *"rozdiel pravdepodobne súvisí s internou obsluhou relé"* — vágne. Buď stručne overiť/vysvetliť mechanizmus, alebo formuláciu zmeniť na *"príčina nebola ďalej skúmaná"*.

---

## 10. Drobnosti

- [ ] **PCF8574 v rešerši bez využitia v HW kapitole**: I2C expandéry (PCF8574) sú zmienené v rešerši ako príklad rozšírenia GPIO, ale v kapitole Implementácia HW sa vôbec nevyskytujú. Ak sa v projekte nepoužili, vetu z rešerše odstrániť alebo generalizovať (bez konkrétneho čipu).
- [ ] **"Vite" bez vysvetlenia**: `Implementacia_sw.tex` — *"Frontend je realizovaný ako React SPA (Vite)"* — Vite je build nástroj, nie framework; pri prvom použití doplniť jednoslušnú charakteristiku v zátvorke.
- [ ] **"masívne dimenzovaný obvod"** (`Implementacia_hw.tex`, sekcia BTS7960B) — neakademický výraz. Nahradiť napr. *"obvod dimenzovaný na vysoké prúdové špičky"*.
- [ ] **Popisok obrázku dashboardu**: `fig:sw_dashboard_screenshot` má popisok len *"Hlavná stránka"* — príliš vágne. Doplniť napr. *"Hlavná stránka webového dashboardu s prehľadom stavu zariadení"*.
