# Intoxicated Sniper: Mini-Breeze mit reitendem Gift-Bogged samt Flame-Bogen
# Quelle: Command Block bei 178 73 -49 (_input/world)
#
# Pflicht-Argumente: d_x, d_y, d_z (Spawn-Versatz relativ zum naechsten Spieler)
# Aufruf-Beispiel (alter Standard-Versatz):
#   /function falron:entity/intoxicated_sniper {d_x:0,d_y:2,d_z:3}
$execute at @p run summon breeze ^$(d_x) ^$(d_y) ^$(d_z) {OnGround:0b,NoGravity:1b,Silent:1b,Invulnerable:0b,Glowing:0b,CustomNameVisible:0b,attributes:[{id:"minecraft:scale",base:0.09}],Passengers:[{id:"minecraft:bogged",CustomNameVisible:1b,Health:30f,Tags:["toxicbreezer"],CustomName:{"bold":true,"color":"green","italic":true,"shadow_color":-937339879,"text":"Intoxicated Sniper"},equipment:{head:{id:"minecraft:kelp",count:1,components:{"minecraft:enchantments":{"sharpness":5}}},mainhand:{id:"minecraft:bow",count:1,components:{"minecraft:custom_name":{"bold":true,"color":"dark_green","italic":true,"shadow_color":-936581090,"text":"Intoxicated Sniper´s Bow"},"minecraft:lore":[{"bold":true,"color":"green","shadow_color":-937262569,"text":"This Intoxicated Weapon uses the Power of Jade-Poisoning...","underlined":true}],"minecraft:enchantments":{"flame":1,"power":3,"infinity":1,"mending":1,"unbreaking":3}}}},drop_chances:{head:0.000,mainhand:1.000},attributes:[{id:"minecraft:armor",base:4},{id:"minecraft:max_health",base:30},{id:"minecraft:scale",base:1}]}]}
