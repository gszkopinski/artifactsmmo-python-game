"""Julia."""

from time import sleep

from artifactsmmo_game import ArtifactsGameClient, locations


# INIT
julia = ArtifactsGameClient(perso_name="Julia1")
character = julia.get_character()
sleep(character.cooldown)

julia.move(poi=locations.bank)
julia.flush_inventory()


# START JOB
julia.perform_task()
# julia.equip_lvl15_equipment()
# julia.perform_fishing()

while True:
    # julia.farm_monster(monster="mushmush")
    julia.mining_job(
        mineral="coal",
    )
    # julia.perform_mining()
