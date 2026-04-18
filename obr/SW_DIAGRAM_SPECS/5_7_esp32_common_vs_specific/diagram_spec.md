# Obrázok 5.7 - Spoločná a špecifická logika uzlov ESP32

## Cieľ

Zobraziť, že uzly zdieľajú jedno komunikačné jadro,
ale implementujú odlišnú vykonávaciu logiku podľa typu uzla.

## Povinná kompozícia

1. Jeden centrálny blok: spoločné jadro uzla
2. Tri vetvy: button, motor, relay
3. Každá vetva má vstup topic + lokálne akcie + feedback výstup

## Spoločné jadro (povinné položky)

1. Wi-Fi connect/reconnect
2. MQTT connect/reconnect
3. LWT + retained status online/offline
4. command topic subscribe
5. feedback publish
6. roomX/STOP odber

## Špecifické vetvy

### Button uzol

1. debounce + cooldown
2. publish START

### Motor uzol

1. PWM riadenie
2. smer + rýchlosť
3. bezpečná zmena smeru

### Relay uzol

1. mapovanie topic -> output
2. timed effects
3. lokálne vykonanie citlivých sekvencií

## Povinné callouty

1. Rozdiel oproti relay HW realizácii: logický model v SW, fyzické detaily v HW kapitole
2. STOP je globálny bezpečnostný mechanizmus pre všetky vetvy

## Vizualizačný štýl

1. Typ diagramu: shared core + branch capabilities
2. Spoločné jadro jedna farba, tri uzly odtiene tej istej palety
3. Vstupy z brokera hore, feedback výstupy dole

## Súlad s textom a runtime

1. sedieť s tabuľkou uzlov a podsekciami ESP32 v SW kapitole
2. nezasahovať do detailov fyzického napájania a 230 V (tie ostávajú v HW)
