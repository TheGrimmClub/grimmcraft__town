# Tick-Zaehler hochzaehlen
scoreboard players add #tick_zaehler falron_tick 1

# Einmal pro Sekunde (alle 20 Ticks) eine Nachricht in die Actionbar schreiben
execute if score #tick_zaehler falron_tick matches 20.. run title @a actionbar {"text":"Tick-Funktion laeuft","color":"gray"}
execute if score #tick_zaehler falron_tick matches 20.. run scoreboard players set #tick_zaehler falron_tick 0