# Scorching Flame: grosser Blaze (NoAI, Statue)
# Quelle: Command Block bei 304 78 -90 (_input/world)
#
# Pflicht-Argumente: d_x, d_y, d_z (Spawn-Versatz relativ zum naechsten Spieler)
# Aufruf-Beispiel (alter Standard-Versatz):
#   /function falron:entity/scorching_flame {d_x:0,d_y:0,d_z:3}
$execute at @p run summon blaze ^$(d_x) ^$(d_y) ^$(d_z) {CustomNameVisible:1b,PersistenceRequired:1b,NoAI:1b,CustomName:[{"bold":true,"color":"dark_red","obfuscated":true,"shadow_color":-8886491,"text":"##"},{"bold":true,"color":"dark_red","obfuscated":false,"shadow_color":-8886491,"text":"Scorching Flame","underlined":true},{"bold":true,"color":"dark_red","obfuscated":true,"shadow_color":-8886491,"text":"##"}],attributes:[{id:"minecraft:scale",base:1.8}]}
