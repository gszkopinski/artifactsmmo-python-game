"""Billy."""

from time import sleep

from artifactsmmo_game import ArtifactsGameClient, locations


# INIT
billy = ArtifactsGameClient(perso_name="billy1")
character = billy.get_character()
sleep(character.cooldown)

billy.move(poi=locations.bank)
billy.flush_inventory()


# ACTIONS
billy.perform_task()

# START JOB
# monster = billy.get_monster(code="ogre")
# billy.can_win_fight(monster=monster)

# billy.farm_monster(monster="wolf")

while True:
    # billy.farm_monster(monster="wolf")
    billy.mining_job(
        mineral="coal",
    )
    # billy.perform_mining()
