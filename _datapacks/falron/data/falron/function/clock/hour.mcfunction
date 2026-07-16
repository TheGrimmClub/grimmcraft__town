# Laeuft bei jedem Stundenwechsel der Spielzeit (alle 50 echten Sekunden)

# --- Hier Aktionen eintragen, die jede Spielstunde laufen sollen ---
tellraw @a [{"text":"[Falron] Es ist ","color":"green"},{"score":{"name":"Stunden","objective":"falron_uhr"},"color":"yellow"},{"text":" Uhr","color":"green"}]
