# Weltzeit (Tageszeit in Ticks, 0..23999) auslesen
execute store result score #daytime falron_tick run time query daytime

# Stunden = daytime / 1000 + 6, modulo 24 (Tick 0 = 06:00 morgens)
scoreboard players operation Stunden falron_uhr = #daytime falron_tick
scoreboard players operation Stunden falron_uhr /= #konst_1000 falron_tick
scoreboard players add Stunden falron_uhr 6
scoreboard players operation Stunden falron_uhr %= #konst_24 falron_tick

# Minuten = (daytime % 1000) * 60 / 1000, gekuerzt: * 3 / 50
scoreboard players operation Minuten falron_uhr = #daytime falron_tick
scoreboard players operation Minuten falron_uhr %= #konst_1000 falron_tick
scoreboard players operation Minuten falron_uhr *= #konst_3 falron_tick
scoreboard players operation Minuten falron_uhr /= #konst_50 falron_tick

# Wenn sich Minute bzw. Stunde geaendert hat: jeweilige Funktion ausfuehren
execute unless score Minuten falron_uhr = #prev_minuten falron_tick run function falron:clock/minute
scoreboard players operation #prev_minuten falron_tick = Minuten falron_uhr
execute unless score Stunden falron_uhr = #prev_stunden falron_tick run function falron:clock/hour
scoreboard players operation #prev_stunden falron_tick = Stunden falron_uhr
