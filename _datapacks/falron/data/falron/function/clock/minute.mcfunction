# Laeuft bei jedem Minutenwechsel der Spielzeit (~alle 0,83 echten Sekunden)

# Zweistellige Anzeige vorbereiten (Zehner und Einer getrennt)
scoreboard players operation #std10 falron_tick = Stunden falron_uhr
scoreboard players operation #std10 falron_tick /= #konst_10 falron_tick
scoreboard players operation #std1 falron_tick = Stunden falron_uhr
scoreboard players operation #std1 falron_tick %= #konst_10 falron_tick
scoreboard players operation #min10 falron_tick = Minuten falron_uhr
scoreboard players operation #min10 falron_tick /= #konst_10 falron_tick
scoreboard players operation #min1 falron_tick = Minuten falron_uhr
scoreboard players operation #min1 falron_tick %= #konst_10 falron_tick

# --- Hier Aktionen eintragen, die jede Spielminute laufen sollen ---
title @a actionbar [{"text":"Uhr: ","color":"gray"},{"score":{"name":"#std10","objective":"falron_tick"},"color":"yellow"},{"score":{"name":"#std1","objective":"falron_tick"},"color":"yellow"},{"text":":","color":"gray"},{"score":{"name":"#min10","objective":"falron_tick"},"color":"yellow"},{"score":{"name":"#min1","objective":"falron_tick"},"color":"yellow"}]
