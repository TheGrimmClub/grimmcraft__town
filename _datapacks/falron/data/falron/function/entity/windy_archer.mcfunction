# Windy Archer als Macro: Breeze mit reitendem Stray-Bogenschuetzen
# Quelle: Command Block bei 169 63 -87 (_input/world)
#
# Pflicht-Argumente: d_x, d_y, d_z (Spawn-Versatz relativ zum naechsten Spieler)
# Aufruf-Beispiel (10 Bloecke ueber, 5 vor dem Spieler):
#   /function falron:entity/windy_archer {d_x:0,d_y:10,d_z:5}
$execute at @p run summon breeze ^$(d_x) ^$(d_y) ^$(d_z) {Tags:["falrongoon"],attributes:[{id:"minecraft:scale",base:0.9}],Passengers:[{id:"minecraft:stray",Tags:["falrongoon"],CustomName:{"bold":true,"color":"aqua","italic":true,"text":"windy archer"},equipment:{mainhand:{id:"minecraft:bow",count:1,components:{"minecraft:enchantments":{"minecraft:knockback":2,"minecraft:power":2,"minecraft:punch":2}}}},drop_chances:{mainhand:0.03},attributes:[{id:"minecraft:scale",base:0.7},{id:"minecraft:burning_time",base:0}]}]}
