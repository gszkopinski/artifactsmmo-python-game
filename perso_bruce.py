"""Bruce."""

from time import sleep

from artifactsmmo_game import ArtifactsGameClient, locations


# INIT
bruce = ArtifactsGameClient(perso_name="Bruce1")
character = bruce.get_character()
sleep(character.cooldown)

bruce.move(poi=locations.bank)
bruce.flush_inventory()


# START JOB
# bruce.farm_monster(monster="cow")

bruce.perform_task()
# bruce.equip_lvl15_equipment()
# bruce.perform_woodcutting()

while True:
    bruce.gathering(quantity=100, poi=locations.birch_trees)
    bruce.gathering(quantity=50, poi=locations.ash_trees)
    bruce.crafting(code="hardwood_plank", quantity=25, poi=locations.woodcutting_workshop)
    bruce.flush_inventory()
    # bruce.farm_monster(monster="mushmush")
    # bruce.perform_mining()
