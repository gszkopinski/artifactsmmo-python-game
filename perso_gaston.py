"""Gaston."""

import time

from artifactsmmo_game import ArtifactsGameClient, locations


# INIT
gaston = ArtifactsGameClient(perso_name="Gaston1")
character = gaston.get_character()
time.sleep(character.cooldown)

gaston.move(poi=locations.bank)
gaston.flush_inventory()


# ACTIONS
# gaston.find_and_get_item(code="")

# gaston.withdraw_bank(
#     code="iron",
#     quantity=27,
# )

# gaston.withdraw_bank(
#     code="feather",
#     quantity=6,
# )

# gaston.withdraw_bank(
#     code="cowhide",
#     quantity=6,
# )

# gaston.withdraw_bank(
#     code="spruce_plank",
#     quantity=18,
# )

# gaston.withdraw_bank(
#     code="red_slimeball",
#     quantity=12,
# )

# gaston.withdraw_bank(
#     code="yellow_slimeball",
#     quantity=12,
# )

# gaston.withdraw_bank(
#     code="green_slimeball",
#     quantity=12,
# )

# gaston.withdraw_bank(
#     code="blue_slimeball",
#     quantity=12,
# )

# gaston.crafting(
#     code="iron_armor",
#     quantity=3,
#     poi=locations.gear_workshop,
# )

# gaston.crafting(
#     code="slime_shield",
#     quantity=3,
#     poi=locations.gear_workshop,
# )

# gaston.crafting(
#     code="iron_helm",
#     quantity=3,
#     poi=locations.gear_workshop,
# )

# gaston.recycling(
#     code="iron_sword",
#     quantity=10,
#     poi=locations.weapon_workshop,
# )

# gaston.withdraw_bank(
#     code="cowhide",
#     quantity=2,
# )

# gaston.withdraw_bank(
#     code="cowhide",
#     quantity=8,
# )
# gaston.flush_inventory()

# gaston.withdraw_bank(
#     code="spruce_plank",
#     quantity=2,
# )

# gaston.crafting(
#     code="iron_pickaxe",
#     quantity=2,
#     poi=locations.weapon_workshop,
# )

# gaston.equip_item(code="iron_pickaxe")


# START JOB
gaston.perform_task()
# gaston.flush_inventory()
# gaston.perform_mining()
# gaston.craft_lvl20_equipment()
# gaston.equip_lvl15_equipment()
# gaston.rise_lvl20_crafting()
# gaston.perform_woodcutting()

# gaston.perform_task()

# gaston.craft_ogre_equipment()
gaston.rise_lvl25_crafting()
while True:
    gaston.mining_job(
        mineral="coal",
    )
