# Sichtbare Bestaetigung im Chat, dass das Datapack geladen wurde
tellraw @a {"text":"[Falron] Datapack geladen","color":"green"}

# Scoreboard-Objectives anlegen (idempotent, Fehler bei Existenz wird ignoriert)
scoreboard objectives add falron_tick dummy
scoreboard objectives add falron_uhr dummy

# Konstanten fuer die Zeitumrechnung (1000 Ticks = 1 Spielstunde)
scoreboard players set #konst_1000 falron_tick 1000
scoreboard players set #konst_24 falron_tick 24
scoreboard players set #konst_3 falron_tick 3
scoreboard players set #konst_50 falron_tick 50
scoreboard players set #konst_10 falron_tick 10

# Merker auf -1, damit minute/hour beim ersten Tick sicher ausgeloest werden
scoreboard players set #prev_minuten falron_tick -1
scoreboard players set #prev_stunden falron_tick -1

# Alten Sekunden-Eintrag aus frueherer Version aufraeumen
scoreboard players reset Sekunden falron_uhr
