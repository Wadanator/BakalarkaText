# Obrázok 5.4 - Štruktúra konfiguračnej scény JSON

## Cieľ
Ukázať dátový model scény tak, aby bolo zrejmé čo je globálna časť,
čo je stavovo lokálna časť a ako súvisia transitions a timeline
s runtime spracovaním.

## Mapovanie blokov na kód

### Koreň scény
| Blok | Kód | Popis |
|------|-----|-------|
| sceneId | `state_machine.scene_id` | Identifikátor načítaný pri `load_scene()` |
| initialState | `state_machine.initial_state` | Počiatočný stav pri `start()` |
| states { } | `state_machine.states` | Slovník všetkých stavov scény |
| globalEvents [ ] | `state_machine.global_events` | Prechody platné pre celú scénu, vyhodnocované voči `scene_elapsed_time` |

### Jeden stav
| Blok | Kód | Popis |
|------|-----|-------|
| onEnter [ ] | `state_executor.execute_onEnter()` | Akcie vykonané ihneď pri vstupe do stavu |
| timeline [ ] | `state_executor._schedule_timeline()` | Akcie naplánované ako `threading.Timer` relatívne voči vstupu |
| onExit [ ] | `state_executor.execute_onExit()` | Akcie vykonané pri odchode zo stavu |
| transitions [ ] | `transition_manager.check_transitions()` | Vyhodnocujú sa v poradí zápisu, prvý splnený vyhráva |

### Typy akcií
| Blok | Kód | Popis |
|------|-----|-------|
| mqtt | `state_executor._execute_mqtt()` | Publikovanie správy cez `mqtt_client.publish()` |
| audio | `state_executor._execute_audio()` | Príkaz do `audio_handler.handle_command()` |
| video | `state_executor._execute_video()` | Príkaz do `video_handler.handle_command()` |

### Typy prechodov
| Blok | Kód | Popis |
|------|-----|-------|
| timeout | `_check_timeout()` | Čas v stave >= delay |
| audioEnd | `_check_audio_end()` | Audio súbor skončil, udalosť v `audio_end_events` fronte |
| videoEnd | `_check_video_end()` | Video súbor skončil, udalosť v `video_end_events` fronte |
| mqttMessage | `_check_mqtt_message()` | topic + message v `mqtt_events` fronte |
| always | `_check_always()` | Bezpodmienečne, vždy sa splní |

### Validácia pri načítaní
| Blok | Kód | Popis |
|------|-----|-------|
| Schémová | `validate_scene_json()` | Povinné polia, typy hodnôt cez jsonschema |
| Logická | `state_machine.load_scene()` | Každý goto target musí existovať v states alebo byť "END" |