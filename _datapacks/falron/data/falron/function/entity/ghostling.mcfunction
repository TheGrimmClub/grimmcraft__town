# Ghostling: kleiner Happy Ghast mit Mace und Cyan-Geschirr
# Quelle: Command Block bei 204 63 -82 (_input/world)
#
# Pflicht-Argumente: d_x, d_y, d_z (Spawn-Versatz relativ zum naechsten Spieler)
# Aufruf-Beispiel (alter Standard-Versatz):
#   /function falron:entity/ghostling {d_x:0,d_y:0,d_z:3}
$execute at @p run summon happy_ghast ^$(d_x) ^$(d_y) ^$(d_z) {Fire:-100,Glowing:1b,CustomNameVisible:1b,LeftHanded:1b,PersistenceRequired:1b,Health:15f,CustomName:{"bold":true,"color":"dark_aqua","italic":false,"obfuscated":false,"strikethrough":false,"text":"Ghostling"},equipment:{mainhand:{id:"minecraft:mace",count:1},offhand:{id:"minecraft:mace",count:1},saddle:{id:"minecraft:cyan_harness",count:1}},attributes:[{id:"minecraft:armor",base:5},{id:"minecraft:attack_damage",base:1.5},{id:"minecraft:attack_knockback",base:0.25},{id:"minecraft:attack_speed",base:2},{id:"minecraft:scale",base:0.25}]}
