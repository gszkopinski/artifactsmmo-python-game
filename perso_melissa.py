"""Melissa."""

from time import sleep

from artifactsmmo_game import ArtifactsGameClient, locations


# INIT
melissa = ArtifactsGameClient(perso_name="Melissa1")
character = melissa.get_character()
sleep(character.cooldown)

melissa.move(poi=locations.bank)
melissa.flush_inventory()


# ACTIONS


# START JOB
melissa.perform_task()
# melissa.farm_monster(monster="cow")

# melissa.find_and_get_item("adventurer_vest")
# melissa.unequip_item(slot="body_armor")
# melissa.equip_item(code="adventurer_vest")

# melissa.find_and_get_item("life_amulet")
# melissa.unequip_item(slot="amulet")
# melissa.equip_item(code="life_amulet")
# melissa.equip_lvl15_equipment()

while True:
    # melissa.farm_monster(monster="wolf")
    melissa.mining_job(
        mineral="coal",
    )
    # melissa.perform_mining()
