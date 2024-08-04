"""Locations."""

from artifactsmmo_sdk.models.common import PointOfInterest


spawn = PointOfInterest(x=0, y=0, description="Spawn")

# CRAFTING
weapon_workshop = PointOfInterest(x=2, y=1, description="Weapon Workshop")
gear_workshop = PointOfInterest(x=3, y=1, description="Gear Workshop")
cooking_workshop = PointOfInterest(x=1, y=1, description="Cooking Workshop")
jewelry_workshop = PointOfInterest(x=1, y=3, description="Jewelry Workshop")
woodcutting_workshop = PointOfInterest(x=-2, y=-3, description="Woodcutting Workshop")
mining_workshop = PointOfInterest(x=1, y=5, description="Mining Workshop")

# MASTER
task_master = PointOfInterest(x=1, y=2, description="Task Master")

# BANK AND GRAND EXCHANGE
bank = PointOfInterest(x=4, y=1, description="Bank")
grand_exchange = PointOfInterest(x=5, y=1, description="Grand Exchange")

# FISHING
gudgeon_fishing_spot = PointOfInterest(x=4, y=2, description="Gudgeon Fishing Spot")
shrimp_fishing_spot = PointOfInterest(x=5, y=2, description="Shrimp Fishing Spot")
trout_fishing_spot = PointOfInterest(x=-2, y=6, description="Trout Fishing Spot")
bass_fishing_spot = PointOfInterest(x=-3, y=6, description="Bass Fishing Spot")

# GATHERING
ash_trees = PointOfInterest(x=-1, y=0, description="Ash Trees")
spruce_trees = PointOfInterest(x=2, y=6, description="Spruce Trees")
birch_trees = PointOfInterest(x=3, y=5, description="Birch Trees")
dead_trees = PointOfInterest(x=9, y=8, description="Dead Trees")

copper_rocks = PointOfInterest(x=2, y=0, description="Copper Rocks")
iron_rocks = PointOfInterest(x=1, y=7, description="Iron Rocks")
coal_rocks = PointOfInterest(x=1, y=6, description="Coal Rocks")
gold_rocks = PointOfInterest(x=10, y=-4, description="Gold Rocks")

# MONSTERS
chicken_monster = PointOfInterest(x=0, y=1, description="Chicken Monster")
yellow_slime_monster = PointOfInterest(x=4, y=-1, description="Yellow Slime Monster")
green_slime_monster = PointOfInterest(x=3, y=-2, description="Green Slime Monster")
blue_slime_monster = PointOfInterest(x=2, y=-1, description="Blue Slime Monster")
red_slime_monster = PointOfInterest(x=1, y=-1, description="Red Slime Monster")
cow_monster = PointOfInterest(x=0, y=2, description="Cow Monster")
mushmush_monster = PointOfInterest(x=5, y=3, description="MushMush Monster")
wolf_monster = PointOfInterest(x=-2, y=1, description="Wolf Monster")
