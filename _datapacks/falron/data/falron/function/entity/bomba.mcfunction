# Bomba: TNT-Item mit gezuendetem Creeper obendrauf
# Quelle: Command Block bei 175 73 -201 (_input/world); Fuse:0.1 war ungueltig (short noetig) -> Fuse:1s
#
# Pflicht-Argumente: d_x, d_y, d_z (Spawn-Versatz relativ zum naechsten Spieler)
# Aufruf-Beispiel (alter Standard-Versatz):
#   /function falron:entity/bomba {d_x:0,d_y:1,d_z:3}
$execute at @p run summon item ^$(d_x) ^$(d_y) ^$(d_z) {CustomNameVisible:1b,CustomName:{"bold":true,"color":"red","italic":true,"text":"Bomba"},Item:{id:"minecraft:tnt",count:1},Passengers:[{id:"minecraft:creeper",ExplosionRadius:1b,Fuse:1s,ignited:1b}]}
