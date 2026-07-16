# Sichtbare Bestaetigung im Chat, dass das Datapack geladen wurde
tellraw @a {"text":"[Falron] Datapack geladen","color":"green"}

# Scoreboard-Objective furr den Tick-Zaehler anlegen (idempotent, Fehler bei Existenz wird ignoriert)
scoreboard objectives add falron_tick dummy

# Zaehler auf null setzen
scoreboard players set #tick_zaehler falron_tick 0
