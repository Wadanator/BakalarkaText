# TO-DO pred finálnym odovzdaním

## 1. Chýbajúce obrázky

Súbory sú referencované v texte, ale neexistujú:

- [ ] `obr/HW/relay_schema.pdf` — schéma relé uzla (`Implementacia_hw.tex`, fig. relay_schema)
- [ ] `obr/HW/chronos_celok.jpg` — fotka celej inštalácie CHRONOS (`Implementacia_hw.tex`, fig. chronos_celok)
- [ ] `obr/HW/kotol_exponat.jpg` — fotka parného kotla s elektronikou (`Implementacia_hw.tex`, fig. kotol_exponat)
- [ ] Diagram 5_7 (ESP32 porovnávacia schéma) — v texte je len `\fbox{MIESTO PRE OBRÁZOK}`, existuje iba `diagram_spec.md`. Buď diagram dorob, alebo fbox nahraď tabuľkou.

---

## 4. Experimenty — nedostatočné dáta

- [ ] **Test obnovy po výpadku**: uvedený len priemer 38 s — doplniť **n** (koľkokrát sa testovalo), min, max.
- [ ] **Laboratórny test logiky**: *"spúšťala sa niekoľkokrát"* — nahradiť konkrétnym číslom.
- [ ] **Presnosť prepínania**: *"za celú sekvenciu"* — uviesť počet prechodov (n), aby bol drift interpretovateľný.
- [ ] **Záver** tvrdí *"systém bežal niekoľko dní bez reštartu"* — toto v kapitole Experimenty nie je podložené žiadnym testom. Buď pridať dlhodobý stabilitný test (napr. log z reálnej prevádzky), alebo toto tvrdenie zo Záveru odstrániť.

---

## 5. Citácie

*(Celková kontrola: umiestenie citácií pred interpunkciou je v celom texte v poriadku — žiadne citácie za bodkou.)*

### Chýbajúce citácie

- [ ] **`Resers.tex`, I2C expandéry** — veta *"Na rozšírenie výstupnej kapacity sa využívajú I2C expandéry, ktoré cez dvojvodičovú zbernicu sprístupňujú dodatočné výstupy bez obsadenia všetkých GPIO pinov."* nemá citáciu. Doplniť `\cite{maier2017esp32}` pred bodku.
- [ ] **`Resers.tex`, Zhrnutie rešerše** — veta *"Konfigurácia vo formáte JSON poskytuje ľahko editovateľné definície stavov a prechodov bez nutnosti zásahu do zdrojového kódu."* nemá citáciu (v tele kapitoly bol fakt citovaný). Doplniť `\cite{iot_data_formats_review, partarakis2016adaptable}`, alebo vetu preformulovať ako záver z vlastnej analýzy (bez citácie).
- [ ] **BTS7960B** *"do 43 A"* — chýba citácia datasheetu (Infineon BTS7960B datasheet).

### Nesprávne zdroje

- [ ] `\cite{noural2019iot}` je použité na podporu tvrdenia o vendor lock-in show-control systémov, ale zdroj je článok o software-defined networking — nesúvisí. Nájsť priamejší zdroj alebo citáciu odstrániť.

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

- [ ] **Chýba porovnanie s literatúrou**: rešerše uvádza MQTT latenciu 11,04 ms (zdroj `mqtt_websocket_comparison`), namerané je 111,7 ms — teda 10× viac. Rozdiel je pochopiteľný (iné podmienky: feedback round-trip vs. jednosmerná latencia), ale mal by byť v diskusii vysvetlený, inak to pôsobí ako rozpor s vlastnou rešeršou.

---

## 10. Drobnosti

- [ ] **"Vite" bez vysvetlenia**: `Implementacia_sw.tex` — *"Frontend je realizovaný ako React SPA (Vite)"* — Vite je build nástroj, nie framework; pri prvom použití doplniť jednoslušnú charakteristiku v zátvorke.
