# Falron Eye of the Storm: der Boss-Breeze (420 HP, Scale 2)
# Quelle: Command Block bei 175 63 -111 (_input/world), Score-Bedingung FalronLives entfernt
#
# Pflicht-Argumente: d_x, d_y, d_z (Spawn-Versatz relativ zum naechsten Spieler)
# Aufruf-Beispiel (alter Standard-Versatz):
#   /function falron:entity/falron_boss {d_x:0,d_y:0,d_z:5}
$execute at @p run summon breeze ^$(d_x) ^$(d_y) ^$(d_z) {PersistenceRequired:1b,CustomNameVisible:1b,Health:420f,Tags:["falron"],CustomName:{"bold":true,"color":"aqua","italic":true,"shadow_color":-16242901,"text":"Falron Eye of the Storm"},equipment:{saddle:{id:"minecraft:tnt",count:1}},attributes:[{id:"minecraft:attack_damage",base:10},{id:"minecraft:attack_knockback",base:20},{id:"minecraft:burning_time",base:0},{id:"minecraft:max_health",base:420},{id:"minecraft:movement_efficiency",base:6},{id:"minecraft:scale",base:2}]}
