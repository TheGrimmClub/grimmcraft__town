# Wind Charge Strike: laesst eine Breeze-Windkugel von oben auf den Spieler fallen
# Quelle: Command Block bei 204 92 -187 (_input/world), stellvertretend fuer alle Windkugel-Salven
#
# Pflicht-Argumente: d_x, d_y, d_z (Spawn-Versatz relativ zum naechsten Spieler)
# Aufruf-Beispiel (alter Standard-Versatz):
#   /function falron:entity/wind_charge_strike {d_x:0,d_y:5,d_z:0}
$execute at @p run summon breeze_wind_charge ^$(d_x) ^$(d_y) ^$(d_z) {Motion:[0.0,-1.0,0.0]}
