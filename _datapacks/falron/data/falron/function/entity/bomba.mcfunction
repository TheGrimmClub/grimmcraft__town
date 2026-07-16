# Bomba: TNT-Item mit gezuendetem Creeper obendrauf
# Quelle: Command Block bei 175 73 -201 (_input/world); Fuse:0.1 war ungueltig (short noetig) -> Fuse:1s
execute at @p run summon item ^ ^1 ^3 {CustomNameVisible:1b,CustomName:{"bold":true,"color":"red","italic":true,"text":"Bomba"},Item:{id:"minecraft:tnt",count:1},Passengers:[{id:"minecraft:creeper",ExplosionRadius:1b,Fuse:1s,ignited:1b}]}
