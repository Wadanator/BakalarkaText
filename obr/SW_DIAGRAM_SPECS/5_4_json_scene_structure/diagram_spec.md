# Obrázok 5.4 — Štruktúra konfiguračnej scény JSON + príkazové formáty

## Cieľ

Ukázať dátový model scény (koreň, stav, sekcie), typy akcií s konkretnými príkazmi, typy prechodov a MQTT tópiky pre spustenie scény — všetko na jednom mieste ako referenčná karta.

---

## Mapovanie blokov na kód

### Koreň JSON scény

| Blok v diagrame | Súbor / funkcia | Čo robí v reálnom kóde |
|---|---|---|
| sceneId | `raspberry_pi/utils/state_machine.py` → `scene_id` | Identifikátor scény načítaný pri `load_scene()`; používa sa v logoch a WebSocket `scene_progress` udalostiach |
| initialState | `state_machine.py` → `initial_state` | Meno prvého stavu do ktorého FSM vstúpi pri `start()` |
| states { } | `state_machine.py` → `self.states` | Slovník všetkých stavov scény; kľúč = meno stavu, hodnota = slovník sekcií |
| globalEvents [ ] | `state_machine.py` → `self.global_events` | Prechody platné pre celú scénu vyhodnocované voči `scene_elapsed_time`; majú prednosť pred lokálnymi prechodmi v každom tiku |

### Jeden stav — štyri sekcie

| Blok v diagrame | Súbor / funkcia | Čo robí v reálnom kóde |
|---|---|---|
| onEnter [ ] | `raspberry_pi/utils/state_executor.py` → `execute_onEnter()` | Akcie vykonané ihneď pri vstupe do stavu; volané z `_change_state()` |
| timeline [ ] | `state_executor.py` → `_schedule_timeline()` | Každá timeline akcia sa naplánuje ako `threading.Timer` s oneskorením relatívnym k vstupu do stavu; pri zmene stavu sa starý generation counter zneplatní |
| onExit [ ] | `state_executor.py` → `execute_onExit()` | Akcie vykonané pri odchode zo stavu; volané z `_change_state()` pred `goto_state()` |
| transitions [ ] | `raspberry_pi/utils/transition_manager.py` → `check_transitions()` | Vyhodnocujú sa v poradí zápisu; prvý splnený prechod vyhráva a tick končí zmenou stavu |

### Typy akcií a konkrétne príkazy

| Blok v diagrame | Súbor / funkcia | Čo robí v reálnom kóde |
|---|---|---|
| mqtt — topic + message | `state_executor.py` → `_execute_mqtt()` | Publikuje správu cez `mqtt_client.publish(topic, message)`; runtime odosiela scénické MQTT akcie s `retain=False` |
| audio — PLAY:\<súbor\>[:\<vol\>] | `raspberry_pi/utils/audio_handler.py` → `handle_command()` | Prehrá zvukový súbor; súbory s prefixom `sfx_` sú preloadované do RAM, ostatné streamované z disku |
| audio — STOP / STOP:\<súbor\> | `audio_handler.py` → `handle_command()` | `STOP` zastaví všetky stopy; `STOP:<súbor>` zastaví konkrétnu stopu |
| audio — PAUSE / RESUME | `audio_handler.py` → `handle_command()` | Pozastaví / obnoví prehrávanie aktuálnej stopy |
| audio — VOLUME:\<0.0–1.0\> | `audio_handler.py` → `handle_command()` | Nastaví hlasitosť na danú hodnotu |
| video — PLAY\_VIDEO:\<súbor\> | `raspberry_pi/utils/video_handler.py` → `handle_command()` | Spustí externý video prehrávač cez IPC rozhranie |
| video — STOP\_VIDEO | `video_handler.py` → `handle_command()` | Zastaví prehrávanie videa a vráti prehrávač na idle obrázok |
| video — PAUSE / RESUME | `video_handler.py` → `handle_command()` | Pozastaví / obnoví prehrávanie videa |
| video — SEEK:\<sekundy\> | `video_handler.py` → `handle_command()` | Presunie prehrávanie na zadanú pozíciu v sekundách |

### Typy prechodov

| Blok v diagrame | Súbor / funkcia | Čo robí v reálnom kóde |
|---|---|---|
| timeout | `transition_manager.py` → `_check_timeout()` | Uplynulý čas v stave (`state_elapsed_time`) >= `delay` hodnote v JSON |
| audioEnd | `transition_manager.py` → `_check_audio_end()` | Fronta `audio_end_events` obsahuje udalosť zodpovedajúcu `target` súboru |
| videoEnd | `transition_manager.py` → `_check_video_end()` | Fronta `video_end_events` obsahuje udalosť pre `target` súbor |
| mqttMessage | `transition_manager.py` → `_check_mqtt_message()` | Fronta `mqtt_events` obsahuje správu s daným `topic` a `message` |
| always | `transition_manager.py` → `_check_always()` | Vždy vráti `True` — bezpodmienečný prechod; typicky posledný v zozname ako fallback |

### Validácia pri načítaní

| Blok v diagrame | Súbor / funkcia | Čo robí v reálnom kóde |
|---|---|---|
| Schémová validácia | `raspberry_pi/utils/schema_validator.py` → `validate_scene_json()` | Overuje povinné polia a typy hodnôt pomocou `jsonschema`; chyba = výnimka pred spustením scény |
| Logická validácia | `state_machine.py` → `load_scene()` | Každý `goto` target musí existovať v `states` alebo mať hodnotu `"END"`; chyba = `load_scene()` vráti `False` |

### Spustenie scény (MQTT tópiky)

| Blok v diagrame | Súbor / funkcia | Čo robí v reálnom kóde |
|---|---|---|
| roomX/scene + payload "START" | `mqtt_message_handler.py` → `_is_scene_start_command()` | Spustí **default scénu** nakonfigurovanú v `config.ini`; payload musí byť presne `"START"` (case-insensitive) |
| roomX/start\_scene + payload = názov súboru | `mqtt_message_handler.py` → `_is_named_scene_command()` | Spustí **konkrétnu scénu** podľa názvu súboru v payloade (napr. `scene2.json`); volá `MuseumController.start_scene_by_name()` |
| Zastavenie — roomX/STOP | `main.py` → `broadcast_stop()` | Okamžité zastavenie všetkých výstupov; odosielané backendom pri ukončení scény |

---

## Kľúčové súbory

| Súbor | Úloha |
|---|---|
| `raspberry_pi/utils/schema_validator.py` | Schémová validácia JSON scény |
| `raspberry_pi/utils/state_machine.py` | Load, logická validácia, runtime stav |
| `raspberry_pi/utils/state_executor.py` | Vykonávanie onEnter/Exit/timeline akcií |
| `raspberry_pi/utils/transition_manager.py` | Vyhodnocovanie prechodov, fronty udalostí |
| `raspberry_pi/utils/audio_handler.py` | Všetky audio príkazy |
| `raspberry_pi/utils/video_handler.py` | Všetky video príkazy |
| `raspberry_pi/utils/mqtt/topic_rules.py` | Definícia `scene_topic()` a `named_scene_topic()` |
