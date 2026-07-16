# Windy Overseer: Breeze mit reitendem Vex samt Eisenspeer
# Quelle: Command Block bei 185 63 -129 (_input/world)
#
# Pflicht-Argumente: d_x, d_y, d_z (Spawn-Versatz relativ zum naechsten Spieler)
# Aufruf-Beispiel (alter Standard-Versatz):
#   /function falron:entity/windy_overseer {d_x:0,d_y:0,d_z:3}
$execute at @p run summon breeze ^$(d_x) ^$(d_y) ^$(d_z) {Tags:["falrongoon"],attributes:[{id:"minecraft:scale",base:1.3}],Passengers:[{id:"minecraft:vex",Health:25f,Tags:["falrongoon"],CustomName:{"bold":true,"color":"aqua","italic":true,"text":"windy overseer"},equipment:{mainhand:{id:"minecraft:iron_spear",count:1,components:{"minecraft:enchantments":{"minecraft:knockback":2,"minecraft:lunge":2}}}},drop_chances:{mainhand:0.03},attributes:[{id:"minecraft:scale",base:1.5}]}]}
