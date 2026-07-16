# Falron's Sniper-Tower: vier gestapelte Breezes
# Quelle: Command Block bei 176 64 -107 (_input/world), Score-Bedingung entfernt
#
# Pflicht-Argumente: d_x, d_y, d_z (Spawn-Versatz relativ zum naechsten Spieler)
# Aufruf-Beispiel (alter Standard-Versatz):
#   /function falron:entity/sniper_tower {d_x:0,d_y:0,d_z:5}
$execute at @p run summon breeze ^$(d_x) ^$(d_y) ^$(d_z) {Silent:1b,CustomNameVisible:1b,Tags:["falronminion"],attributes:[{id:"minecraft:scale",base:0.6}],Passengers:[{id:"minecraft:breeze",Silent:1b,Tags:["falronminion"],attributes:[{id:"minecraft:scale",base:0.6}],Passengers:[{id:"minecraft:breeze",Silent:1b,Tags:["falronminion"],attributes:[{id:"minecraft:scale",base:0.6}],Passengers:[{id:"minecraft:breeze",Silent:1b,Tags:["falronminion"],CustomName:{"bold":true,"color":"white","italic":true,"obfuscated":false,"shadow_color":-925773359,"strikethrough":false,"text":"Falron´s Sniper-Tower","underlined":true},attributes:[{id:"minecraft:scale",base:0.6}]}]}]}]}
