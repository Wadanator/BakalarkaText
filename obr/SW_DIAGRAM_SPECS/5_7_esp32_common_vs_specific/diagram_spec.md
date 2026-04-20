# Obrázok 5.7 — Spoločná a špecifická logika uzlov ESP32

## Cieľ

Zobraziť, že všetky tri uzly zdieľajú jedno komunikačné jadro (Wi-Fi, MQTT, LWT, STOP), ale každý implementuje odlišnú vykonávaciu logiku podľa svojho hardvérového účelu.

---

## Mapovanie blokov na kód

### Spoločné jadro (všetky tri uzly)

| Blok v diagrame | Súbor / funkcia | Čo robí v reálnom kóde |
|---|---|---|
| Wi-Fi connect / reconnect | `ArduinoIDE/*/wifi_manager.h` → `initializeWiFi()` | Pripojenie k Wi-Fi pri štarte; `connection_monitor.h` periodicky kontroluje stav a automaticky reconnectuje |
| MQTT connect / reconnect | `ArduinoIDE/*/mqtt_manager.h` → `initializeMqtt()`, `mqttLoop()` | Pripojenie k brokeru; `mqttLoop()` v každej iterácii hlavnej slučky udržiava spojenie a spracúva prichádzajúce správy |
| LWT + retained status | `ArduinoIDE/*/mqtt_manager.h` — Last Will Testament | Pri odpojení broker automaticky publikuje `offline` na `devices/<client_id>/status` s `retain=True`; pri pripojení uzol publikuje `online` |
| Odber príkazového topiku | `ArduinoIDE/*/mqtt_manager.h` → `subscribe()` | Každý uzol sa prihlási na odber svojho príkazového topiku a `roomX/STOP` |
| Feedback publish | `ArduinoIDE/*/mqtt_manager.h` → publish na `topic/feedback` | Po vykonaní príkazu uzol publikuje `OK` na `topic/feedback`; backend to zachytí a aktualizuje `confirmed_state` |
| Watchdog timer | `ArduinoIDE/*/wdt_manager.h` → `initializeWatchdog()`, `resetWatchdog()` | Hardvérový watchdog; ak hlavná slučka zamrzne a `resetWatchdog()` sa nezavolá v limite, ESP32 sa automaticky reštartuje |
| OTA aktualizácie | `ArduinoIDE/*/ota_manager.h` → `initializeOTA()`, `handleOTA()` | Vzdialená aktualizácia firmvéru cez Wi-Fi bez fyzického prístupu k zariadeniu |
| roomX/STOP odber | `ArduinoIDE/*/mqtt_manager.h` → STOP handler | Pri prijatí STOP správy uzol okamžite vypne všetky výstupy nezávisle od aktuálneho stavu |

### Button uzol (esp32_mqtt_button)

| Blok v diagrame | Súbor / funkcia | Čo robí v reálnom kóde |
|---|---|---|
| Detekcia stlačenia s debouncingom | `ArduinoIDE/esp32_mqtt_button/hardware.cpp` → `wasButtonPressed()` | Číta GPIO pin s externým pull-up rezistorom; cooldown zabraňuje viacnásobnému spusteniu pri jednom stlačení |
| LED potvrdenie | `ArduinoIDE/esp32_mqtt_button/led_manager.h` → `ledButtonConfirm()` | PWM LED 4x rýchlo blikne ako vizuálna spätná väzba pre operátora |
| Publikovanie triggeru scény | `ArduinoIDE/esp32_mqtt_button/mqtt_manager.h` → `publishSceneTrigger()` | Odošle `START` na tópik `roomX/scene`; backend to prijme a spustí default scénu |

### Motor uzol (esp32_mqtt_controller_MOTORS)

| Blok v diagrame | Súbor / funkcia | Čo robí v reálnom kóde |
|---|---|---|
| Prijatie príkazu smeru/rýchlosti | `ArduinoIDE/esp32_mqtt_controller_MOTORS/mqtt_manager.h` → MQTT callback | Parsuje príkaz obsahujúci smer (`FORWARD`/`BACKWARD`/`STOP`) a voliteľne rýchlosť |
| Plynulá PWM zmena | `ArduinoIDE/esp32_mqtt_controller_MOTORS/hardware.cpp` → `updateMotorSmoothly()` | Volané v každej iterácii hlavnej slučky; postupne mení PWM hodnotu smerom k cieľovej — zabraňuje nárazovým zmenám prúdu |
| Bezpečná zmena smeru | `hardware.cpp` — logika pred zmenou smeru | Pred zmenou smeru motor zastaví (PWM = 0) a počká krátku dobu; predchádza mechanickému poškodeniu |

### Relay uzol (esp32_mqtt_controller_RELAY)

| Blok v diagrame | Súbor / funkcia | Čo robí v reálnom kóde |
|---|---|---|
| Mapovanie topic → GPIO výstup | `ArduinoIDE/esp32_mqtt_controller_RELAY/hardware.cpp` → `initializeHardware()` | Konfigurácia mapy MQTT topic → GPIO pin; pri prijatí správy `ON`/`OFF` uzol prepne príslušný výstup |
| Efektový manažér | `ArduinoIDE/esp32_mqtt_controller_RELAY/effects_manager.h` → `initializeEffects()` | Správa časovaných sekvencií (blikanie, pulzovanie) vykonávaných lokálne na uzle bez závislosti na backende |
| Statusová LED | `ArduinoIDE/esp32_mqtt_controller_RELAY/status_led.h` → `initializeStatusLed()` | Indikuje stav MQTT spojenia a aktívne výstupy priamo na zariadení |
| Lokálne vykonanie citlivých sekvencií | `effects_manager.h` — efektová slučka | Časovo citlivé sekvencie sa vykonávajú priamo na ESP32 bez RTT oneskorenia cez MQTT |

---

## Kľúčové detaily pre obhajobu

| Otázka | Odpoveď |
|---|---|
| Prečo spoločné jadro namiesto troch samostatných firmvérov? | Zdieľaný kód pre Wi-Fi, MQTT, LWT, WDT a OTA znižuje duplicitu; každý uzol len pridá svoju špecifickú logiku |
| Čo sa stane pri výpadku Wi-Fi? | `connection_monitor.h` detekuje výpadok a pokúša sa o reconnect; LWT broker automaticky publikuje `offline` stav |
| Prečo relay uzol vykonáva efekty lokálne? | RTT oneskorenie cez MQTT by spôsobilo nepresné časovanie; lokálne vykonanie zaručuje konzistentnosť efektov |
| Ako backend vie, že uzol je online? | Uzol publikuje `online` na `devices/<client_id>/status` pri pripojení; broker publikuje `offline` (LWT) pri výpadku |
| Čo robí STOP príkaz na uzle? | Každý uzol má handler pre `roomX/STOP` ktorý okamžite vypne všetky výstupy bez čakania na ďalšie príkazy |

---

## Kľúčové súbory

| Súbor | Úloha |
|---|---|
| `ArduinoIDE/esp32_mqtt_button/esp32_mqtt_button.ino` | Button uzol — hlavná slučka |
| `ArduinoIDE/esp32_mqtt_button/hardware.cpp` | Detekcia stlačenia, cooldown, LED |
| `ArduinoIDE/esp32_mqtt_controller_MOTORS/esp32_mqtt_controller_MOTORS.ino` | Motor uzol — hlavná slučka |
| `ArduinoIDE/esp32_mqtt_controller_MOTORS/hardware.cpp` | PWM riadenie, plynulá zmena, bezpečnostná logika |
| `ArduinoIDE/esp32_mqtt_controller_RELAY/esp32_mqtt_controller_RELAY.ino` | Relay uzol — hlavná slučka |
| `ArduinoIDE/esp32_mqtt_controller_RELAY/effects_manager.h` | Lokálne časované efekty |
| `ArduinoIDE/*/wifi_manager.h` | Wi-Fi connect/reconnect (spoločné) |
| `ArduinoIDE/*/mqtt_manager.h` | MQTT connect, LWT, subscribe, publish (spoločné) |
| `ArduinoIDE/*/wdt_manager.h` | Watchdog timer (spoločné) |
| `ArduinoIDE/*/ota_manager.h` | OTA aktualizácie (spoločné) |
