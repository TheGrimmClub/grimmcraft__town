# Skull-Allay: unsichtbarer, unverwundbarer Allay der einen Skelettschaedel traegt (Geister-Deko)
# Quelle: Command Block bei 182 74 -199 (_input/world)
#
# Pflicht-Argumente: d_x, d_y, d_z (Spawn-Versatz relativ zum naechsten Spieler)
# Aufruf-Beispiel (alter Standard-Versatz):
#   /function falron:entity/skull_allay {d_x:0,d_y:0,d_z:3}
$execute at @p run summon allay ^$(d_x) ^$(d_y) ^$(d_z) {Silent:1b,Invulnerable:1b,equipment:{mainhand:{id:"minecraft:skeleton_skull",count:1}},active_effects:[{id:"minecraft:invisibility",amplifier:1,duration:199999980,show_particles:0b,show_icon:0b,ambient:0b}],attributes:[{id:"minecraft:scale",base:1}]}
