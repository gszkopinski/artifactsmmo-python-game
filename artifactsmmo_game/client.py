"""Perso Billy."""

from time import sleep

from artifactsmmo_sdk import ArtifactsClient
from artifactsmmo_sdk.models.actions import ListBankItemsResponseSchema, SlotEnum
from artifactsmmo_sdk.models.common import PointOfInterest
from artifactsmmo_sdk.models.items import SingleItemSchema
from artifactsmmo_sdk.models.monsters import MonsterSchema
from dotenv import load_dotenv

from . import locations


# from .craft_recipes import CraftRecipes

load_dotenv()


class ArtifactsGameClient:
    """Artifacts MMO Game client."""

    def __init__(
        self,
        perso_name: str,
    ) -> None:
        """Init the client."""
        self.perso = ArtifactsClient()
        self.perso_name = perso_name

        # self.craft_recipes = CraftRecipes(
        #     perso=self.perso,
        #     perso_name=self.perso_name,
        # )

    def try_resolve_error(
        self,
        error: str,
    ):
        """Try to resolve error, or raise an Exception."""
        match error:
            case "Slot is empty.":
                pass
            case "Character inventory is full.":
                self.flush_inventory()
            case "Character in cooldown.":
                character = self.get_character()
                sleep(character.cooldown)
            case "Character already at destination.":
                pass
            case "An action is already in progress by your character.":
                character = self.get_character()
                sleep(character.cooldown)
            case "Character level is insufficient.":
                print("Rise LVL")
            case "This item is already equipped.":
                pass
            case _:
                raise Exception(error)

    def on_good_location(
        self,
        x: int,
        y: int,
        poi: PointOfInterest,
    ):
        """Return True if you are on the PoI."""
        return x == poi.x and y == poi.y

    # -----------------------------------------------------
    # MAPS / MONSTERS / ITEMS / RESOURCES / ...
    # -----------------------------------------------------
    def get_all_maps(
        self,
        content_code: str,
        content_type: str,
    ):
        """Get all maps."""
        error, maps = self.perso.maps.get_all_maps(
            content_code=content_code,
            content_type=content_type,
        )

        if not maps:
            self.try_resolve_error(error=error)
            self.get_all_maps(
                content_code=content_code,
                content_type=content_type,
            )

        return maps.data

    def get_all_items(
        self,
        craft_material: str,
        craft_skill: str,
        max_level: int,
        min_level: int,
        name: str,
        type_item: str,
    ):
        """Get all maps."""
        error, items = self.perso.items.get_all_items(
            craft_material=craft_material,
            craft_skill=craft_skill,
            max_level=max_level,
            min_level=min_level,
            name=name,
            type_item=type_item,
        )

        if not items:
            self.try_resolve_error(error=error)

        else:
            return items.data

    def get_all_monsters(
        self,
        item: SingleItemSchema,
    ):
        """Get all monsters."""
        error, monsters = self.perso.monsters.get_all_monsters(
                drop=item.code,
                max_level=item.level,
                min_level=item.level,
            )

        if not monsters:
            self.try_resolve_error(error=error)
            self.get_all_monsters(item=item)

        return monsters.data

    def get_monster(
        self,
        code: str,
    ):
        """Get monster."""
        error, monster = self.perso.monsters.get_monster(
            code=code,
        )

        if not monster:
            self.try_resolve_error(error=error)

        return monster.data

    def get_all_resources(
        self,
        item: SingleItemSchema,
    ):
        """Get all resources."""
        error, resources = self.perso.resources.get_all_resources(
            drop=item.code,
            max_level=item.level,
            min_level=item.level,
            skill=item.subtype,
        )

        if not resources:
            self.try_resolve_error(error=error)
            self.get_all_resources(item=item)

        return resources.data

    def get_character(
        self,
    ):
        """Return perso informations."""
        error, characters = self.perso.characters.get_character(name=self.perso_name)
        if not characters:
            self.try_resolve_error(error=error)
            self.get_character()

        return characters.data

    def get_item(
        self,
        code: str,
    ):
        """Return item informations."""
        error, item_info = self.perso.items.get_item(
            code=code,
        )

        if not item_info:
            self.try_resolve_error(error=error)
            self.get_item(code=code)

        return item_info.data.item

    def get_bank_items(
        self,
        item_code: str,
    ):
        """List all bank items."""
        error, items = self.perso.account.get_bank_items(item_code=item_code)

        if not items:
            if error == "Items not found.":
                return ListBankItemsResponseSchema.model_validate(
                    {
                        "data": [
                            {
                                "code": item_code,
                                "quantity": 0
                            }
                        ],
                        "total": 1,
                        "page": 1,
                        "size": 50,
                        "pages": 1
                    }
                ).data

            raise Exception(error=error)

        return items.data

    # -----------------------------------------------------
    # ACTIONS
    # -----------------------------------------------------
    def move(
        self,
        poi: PointOfInterest,
    ):
        """Move."""
        # Get Perso info
        character = self.get_character()

        # Move to the poi position
        if not self.on_good_location(x=character.x, y=character.y, poi=poi):
            error, move = self.perso.actions.move(
                name=self.perso_name,
                x=poi.x,
                y=poi.y,
            )

            if not move:
                self.try_resolve_error(error=error)

            else:
                sleep(move.data.cooldown.total_seconds)
                print(f"{self.perso_name} move to {poi.description}.")

    def gathering(
        self,
        quantity: int,
        poi: PointOfInterest,
    ) -> None:
        """Gathering."""
        # Move to the poi position
        self.move(poi=poi)

        for _ in range(quantity):
            error, action = self.perso.actions.gathering(name=self.perso_name)

            if not action:
                self.try_resolve_error(error=error)

            else:
                sleep(action.data.cooldown.total_seconds)

                while not action.data.details.items:
                    print("- Failed: nothing founded")
                    error, action = self.perso.actions.gathering(name=self.perso_name)

                    if not action:
                        self.try_resolve_error(error=error)
                        self.gathering(quantity=1, poi=poi)

                    sleep(action.data.cooldown.total_seconds)

                print(f"{self.perso_name} gath {action.data.details.items}")

    def recycling(
        self,
        code: str,
        quantity: int,
        poi: PointOfInterest,
    ) -> None:
        """Recycling."""
        # Move to the poi position
        self.move(poi=poi)

        print(f"{self.perso_name} will recycling {quantity} {code}.")
        error, action = self.perso.actions.recycling(
            name=self.perso_name,
            code=code,
            quantity=quantity,
        )

        if not action:
            self.try_resolve_error(error=error)
            self.recycling(code=code, quantity=quantity, poi=poi)

        else:
            print(f"{self.perso_name} recycling {action.data.details.items}")
            sleep(action.data.cooldown.total_seconds)

    def crafting(
        self,
        code: str,
        quantity: int,
        poi: PointOfInterest,
    ) -> None:
        """Crafting."""
        # Move to the poi position
        self.move(poi=poi)

        print(f"{self.perso_name} will craft {quantity} {code}.")
        error, action = self.perso.actions.crafting(
            name=self.perso_name,
            code=code,
            quantity=quantity,
        )

        if not action:
            self.try_resolve_error(error=error)

        else:
            print(f"{self.perso_name} craft {quantity} {code}")
            sleep(action.data.cooldown.total_seconds)

    def deposit_bank(
        self,
        code: str,
        quantity: int,
        poi: PointOfInterest = locations.bank,
    ):
        """Deposit bank."""
        self.move(poi=poi)

        error, action = self.perso.actions.deposit_bank(
            name=self.perso_name,
            code=code,
            quantity=quantity,
        )

        if not action:
            self.try_resolve_error(error=error)
            self.deposit_bank(code=code, quantity=quantity, poi=poi)

        else:
            print(f"{self.perso_name} deposit {quantity} {code} to bank")
            sleep(action.data.cooldown.total_seconds)

    def withdraw_bank(
        self,
        code: str,
        quantity: int,
        poi: PointOfInterest = locations.bank,
    ):
        """Withdraw bank."""
        # Move to the poi position
        self.move(poi=poi)

        error, action = self.perso.actions.withdraw_bank(
            name=self.perso_name,
            code=code,
            quantity=quantity,
        )

        if not action:
            self.try_resolve_error(error=error)
            self.withdraw_bank(code=code, quantity=quantity, poi=poi)

        else:
            sleep(action.data.cooldown.total_seconds)
            print(f"{self.perso_name} withdraw {quantity} {code} from bank")

    def deposit_bank_gold(
        self,
        quantity: int,
        poi: PointOfInterest = locations.bank,
    ) -> None:
        """Deposit gold in bank."""
        self.move(poi=poi)

        error, action = self.perso.actions.deposit_bank_gold(
            name=self.perso_name,
            quantity=quantity,
        )

        if not action:
            self.try_resolve_error(error=error)
            self.deposit_bank_gold(quantity=quantity, poi=poi)

        else:
            print(f"Success: {action.data.bank}")
            sleep(action.data.cooldown.total_seconds)

    def equip_item(
        self,
        code: str,
    ):
        """Equip item."""
        item = self.get_item(code=code)

        error, action = self.perso.actions.equip_item(
            name=self.perso_name,
            code=code,
            slot=item.type
        )

        if not action:
            if error == "Slot is not empty.":
                self.unequip_item(slot=item.type)
                self.equip_item(code=code)

            else:
                raise Exception(error)

        else:
            sleep(action.data.cooldown.total_seconds)
            print(f"{self.perso_name} equip {code} as {item.type}.")

    def unequip_item(
        self,
        slot: str,
    ):
        """Equip item."""
        error, action = self.perso.actions.unequip_item(
            name=self.perso_name,
            slot=slot,
        )

        if not action:
            self.try_resolve_error(error=error)

        else:
            sleep(action.data.cooldown.total_seconds)
            print(f"{self.perso_name} unequip {slot}.")

    def ge_sell_item(
        self,
        code: str,
        quantity: int,
        poi: PointOfInterest = locations.grand_exchange
    ):
        """Sell item to the Grand Exchange."""
        # Move to the poi position
        self.move(poi=poi)

        item_info = self.get_item(
            code=code,
        )

        if not item_info.ge:
            raise Exception(f"Item {code} don't exist on the GE market.")

        sell_price = item_info.ge.sell_price

        error, action = self.perso.actions.ge_sell_item(
            name=self.perso_name,
            code=code,
            quantity=quantity,
            price=sell_price,
        ).data

        if not action:
            self.try_resolve_error(error=error)
            self.ge_sell_item(code=code, quantity=quantity, poi=poi)

        else:
            print(f"{self.perso_name} sell {action.data.transaction}")
            sleep(action.data.cooldown.total_seconds)

    def fight(
        self,
        poi: PointOfInterest,
    ) -> None:
        """Fight."""
        # Move to the poi position
        self.move(poi=poi)

        error, action = self.perso.actions.fight(
            name=self.perso_name,
        )

        if not action:
            self.try_resolve_error(error=error)
            self.fight(poi=poi)

        else:
            print(f"{self.perso_name} fight and get {action.data.fight.drops}")
            sleep(action.data.cooldown.total_seconds)

    def accept_new_task(
        self,
        poi: PointOfInterest = locations.task_master,
    ):
        """Accept new task."""
        # Move to the poi position
        self.move(poi=poi)

        error, action = self.perso.actions.accept_new_task(
            name=self.perso_name,
        )

        if not action:
            self.try_resolve_error(error=error)
            self.accept_new_task(poi=poi)

        else:
            print(f"{self.perso_name} accept the new task {action.data.task}")
            sleep(action.data.cooldown.total_seconds)

    def complete_task(
        self,
        poi: PointOfInterest = locations.task_master,
    ):
        """Complete new task."""
        # Move to the poi position
        self.move(poi=poi)

        error, action = self.perso.actions.complete_task(
            name=self.perso_name,
        )

        if not action:
            self.try_resolve_error(error=error)
            self.complete_task(poi=poi)

        else:
            print(f"{self.perso_name} complete task and get {action.data.reward}")
            sleep(action.data.cooldown.total_seconds)

    def task_exchange(
        self,
        poi: PointOfInterest = locations.task_master,
    ):
        """Exchange task reward."""
        # Move to the poi position
        self.move(poi=poi)

        error, action = self.perso.actions.task_exchange(
            name=self.perso_name,
        )

        if not action:
            self.try_resolve_error(error=error)
            self.task_exchange(poi=poi)

        else:
            print(f"{self.perso_name} exchange task coin to {action.data.reward}")
            sleep(action.data.cooldown.total_seconds)

    # -----------------------------------------------------
    # ADVANCED FEATURES
    # -----------------------------------------------------
    def get_perso_available_inventory_space(
        self,
    ) -> int:
        """Return the space available in the perso inventory."""
        character = self.get_character()

        total_quantity: int = 0
        for item in character.inventory:
            total_quantity += item.quantity

        return character.inventory_max_items - total_quantity

    def in_inventory(
        self,
        code: str,
    ):
        """Return the item if it is in inventory, else None."""
        character = self.get_character()

        for item in character.inventory:
            if item.code == code:
                return item

        return None

    def is_equiped(
        self,
        code: str,
    ):
        """Return the item if it is equiped, else None."""
        character = self.get_character()

        for item in character.inventory:
            if item.code == code:
                return item

        return None

    def quantity_in_bank(
        self,
        item_code: str,
    ):
        """Return quantity of item in bank."""
        items = self.get_bank_items(item_code=item_code)
        for item in items:
            return item.quantity

        return 0

    def flush_inventory(
        self,
    ):
        """Flush inventory before starting job."""
        character = self.get_character()

        for item in character.inventory:
            if item.quantity != 0:
                self.deposit_bank(
                    code=item.code,
                    quantity=item.quantity,
                )

        # self.deposit_bank_gold(
        #     quantity=character.gold
        # )

    def get_item_quantity_from_bank(
        self,
        code: str,
        quantity: int,
    ):
        """Get the item quantity from bank. Return the quantity to gath."""
        quantity_in_bank = self.quantity_in_bank(item_code=code)

        quantity_to_take = 0
        if quantity_in_bank != 0:
            if quantity_in_bank >= quantity:
                quantity_to_take = quantity
                self.withdraw_bank(code=code, quantity=quantity_to_take)
            else:
                quantity_to_take = quantity_in_bank
                self.withdraw_bank(code=code, quantity=quantity_to_take)

            quantity = quantity - quantity_to_take

        return quantity

    def find_and_get_item(
        self,
        code: str,
        quantity: int = 1,
    ):
        """Find and get item."""
        item = self.get_item(code=code)
        character = self.get_character()

        needed_quantity = self.get_item_quantity_from_bank(
            code=code,
            quantity=quantity,
        )

        if needed_quantity != 0:
            if item.type == "resource" and item.subtype == "mob":
                monsters = self.get_all_monsters(item=item)

                maps = self.get_all_maps(
                    content_code=monsters[0].code,
                    content_type="monster",
                )

                item_inventory = self.in_inventory(code=code)

                while not item_inventory:
                    self.fight(
                        poi=PointOfInterest(
                            x=maps[0].x,
                            y=maps[0].y,
                            description=maps[0].skin,
                        )
                    )
                    item_inventory = self.in_inventory(code=code)

                while item_inventory.quantity < quantity:
                    self.fight(
                        poi=PointOfInterest(
                            x=maps[0].x,
                            y=maps[0].y,
                            description=maps[0].skin,
                        )
                    )
                    item_inventory = self.in_inventory(code=code)

            elif item.type == "resource" and item.subtype in [
                "mining",
                "woodcutting",
                "fishing",
            ]:
                resource = self.get_all_resources(
                    item=item
                )

                match item.subtype:
                    case "mining":
                        if character.mining_level < resource[0].level:
                            self.perform_mining()
                    case "woodcutting":
                        if character.woodcutting_level < resource[0].level:
                            self.perform_woodcutting()
                    case "fishing":
                        if character.fishing_level < resource[0].level:
                            self.perform_fishing()

                maps = self.get_all_maps(
                    content_code=resource[0].code,
                    content_type="resource",
                )

                self.gathering(
                    quantity=quantity,
                    poi=PointOfInterest(
                        x=maps[0].x,
                        y=maps[0].y,
                        description=maps[0].skin,
                    )
                )

            elif item.craft:
                maps = self.get_all_maps(
                    content_code=item.craft.skill,
                    content_type="workshop",
                )

                for needed_item in item.craft.items:
                    self.find_and_get_item(code=needed_item.code, quantity=needed_item.quantity * needed_quantity)

                self.crafting(
                    code=item.code,
                    quantity=needed_quantity,
                    poi=PointOfInterest(
                        x=maps[0].x,
                        y=maps[0].y,
                        description=maps[0].skin,
                    )
                )
            else:
                print(f"Item {code} not found on the map.")

    def list_bank_items(
        self,
    ):
        """List bank items."""

    # -----------------------------------------------------
    # FISHING
    # -----------------------------------------------------
    def get_fishing_location(
        self,
        fish: str,
    ) -> PointOfInterest:
        """Get the good fishing location for your fish."""
        match fish:
            case "gudgeon":
                return locations.gudgeon_fishing_spot

            case "shrimp":
                return locations.shrimp_fishing_spot

            case "trout":
                return locations.trout_fishing_spot

            case "bass":
                return locations.bass_fishing_spot

            case _:
                return locations.gudgeon_fishing_spot

    def fishing_job(
        self,
        fish: str,
    ):
        """Fishing Job."""
        print(f"{self.perso_name} wants to fish {fish}.")
        self.gathering(
            quantity=1,
            poi=self.get_fishing_location(fish=fish),
        )

        print(f"{self.perso_name} start cooking {fish}.")
        self.crafting(
            code=f"cooked_{fish}",
            quantity=1,
            poi=locations.cooking_workshop,
        )

        print(f"{self.perso_name} deposit cooked {fish} to the bank.")
        self.deposit_bank(
            code=f"cooked_{fish}",
            quantity=1,
            poi=locations.bank,
        )

    def perform_fishing(
        self,
    ) -> None:
        """Perform fishing."""
        # Get Perso infos
        character = self.get_character()
        perso_fishing_level = character.fishing_level
        print(f"{self.perso_name} is lvl {perso_fishing_level} in fishing")

        # Start fishing
        if perso_fishing_level < 10:
            self.fishing_job(
                fish="gudgeon",
            )

        elif perso_fishing_level < 20:
            self.fishing_job(
                fish="shrimp",
            )

        elif perso_fishing_level < 30:
            self.fishing_job(
                fish="trout",
            )

        else:
            self.fishing_job(
                fish="bass",
            )

        if perso_fishing_level == 30:
            print(f"{self.perso_name} has enough fishing for today.")
        else:
            self.perform_fishing()

    # -----------------------------------------------------
    # MINING
    # -----------------------------------------------------
    def get_mining_location(
        self,
        mineral: str,
    ) -> PointOfInterest:
        """Get the good mining location for your mineral."""
        match mineral:
            case "copper":
                return locations.copper_rocks

            case "iron":
                return locations.iron_rocks

            case "coal":
                return locations.coal_rocks

            case "gold":
                return locations.gold_rocks

            case _:
                return locations.copper_rocks

    def mining_job(
        self,
        mineral: str,
    ):
        """Mining Job."""
        if mineral == "coal":
            print(f"{self.perso_name} starts mining {mineral}.")
            self.gathering(
                quantity=64,
                poi=self.get_mining_location(mineral=mineral),
            )

            print(f"{self.perso_name} starts mining iron.")
            self.gathering(
                quantity=32,
                poi=self.get_mining_location(mineral="iron"),
            )

            print(f"{self.perso_name} starts to melt steel.")
            self.crafting(
                code="steel",
                quantity=16,
                poi=locations.mining_workshop,
            )

            print(f"{self.perso_name} deposits steel to the bank.")
            self.deposit_bank(
                code="steel",
                quantity=16,
                poi=locations.bank,
            )
        else:
            print(f"{self.perso_name} start mining {mineral}.")
            self.gathering(
                quantity=96,
                poi=self.get_mining_location(mineral=mineral),
            )

            print(f"{self.perso_name} starts to melt {mineral}.")
            self.crafting(
                code=mineral,
                quantity=16,
                poi=locations.mining_workshop,
            )

            print(f"{self.perso_name} deposits {mineral} to the bank.")
            self.deposit_bank(
                code=mineral,
                quantity=16,
                poi=locations.bank,
            )

    def perform_mining(
        self,
    ) -> None:
        """Perform mining."""
        # Get Perso infos
        character = self.get_character()
        perso_mining_level = character.mining_level
        print(f"{self.perso_name} is lvl {perso_mining_level} in mining")

        # Start fishing
        if perso_mining_level < 10:
            self.mining_job(
                mineral="copper",
            )

        elif perso_mining_level < 20:
            self.mining_job(
                mineral="iron",
            )

        elif perso_mining_level < 30:
            self.mining_job(
                mineral="coal",
            )

        else:
            self.mining_job(
                mineral="gold",
            )

        if perso_mining_level == 30:
            print(f"{self.perso_name} has enough mining for today.")
        else:
            self.perform_mining()

    # -----------------------------------------------------
    # WOODCUTTING
    # -----------------------------------------------------
    def get_woodcutting_location(
        self,
        wood: str,
    ) -> PointOfInterest:
        """Get the good woodcutting location for your wood."""
        match wood:
            case "ash":
                return locations.ash_trees

            case "spruce":
                return locations.spruce_trees

            case "birch":
                return locations.birch_trees

            case "dead_wood":
                return locations.dead_trees

            case _:
                return locations.ash_trees

    def woodcutting_job(
        self,
        wood: str,
    ):
        """Woodcutting Job."""
        if wood != "birch":
            print(f"{self.perso_name} wants to woodcutting {wood}.")
            self.gathering(
                quantity=96,
                poi=self.get_woodcutting_location(wood=wood),
            )

            print(f"{self.perso_name} start woodcutting {wood}.")
            self.crafting(
                code=f"{wood}_plank",
                quantity=16,
                poi=locations.woodcutting_workshop,
            )

            print(f"{self.perso_name} deposit cooked {wood} to the bank.")
            self.deposit_bank(
                code=f"{wood}_plank",
                quantity=16,
                poi=locations.bank,
            )

        else:
            print(f"{self.perso_name} wants to woodcutting {wood}.")
            self.gathering(
                quantity=64,
                poi=locations.birch_trees,
            )

            print(f"{self.perso_name} wants to woodcutting ash.")
            self.gathering(
                quantity=32,
                poi=locations.ash_trees,
            )

            print(f"{self.perso_name} start woodcutting {wood}.")
            self.crafting(
                code="hardwood_plank",
                quantity=16,
                poi=locations.woodcutting_workshop,
            )

            print(f"{self.perso_name} deposit cooked {wood} to the bank.")
            self.deposit_bank(
                code="hardwood_plank",
                quantity=16,
                poi=locations.bank,
            )

    def perform_woodcutting(
        self,
    ) -> None:
        """Perform woodcutting."""
        # Get Perso infos
        character = self.get_character()
        perso_woodcutting_level = character.woodcutting_level
        print(f"{self.perso_name} is lvl {perso_woodcutting_level} in woodcutting")

        # Start fishing
        if perso_woodcutting_level < 10:
            self.woodcutting_job(
                wood="ash",
            )

        elif perso_woodcutting_level < 20:
            self.woodcutting_job(
                wood="spruce",
            )

        elif perso_woodcutting_level < 30:
            self.woodcutting_job(
                wood="birch",
            )

        else:
            self.woodcutting_job(
                wood="dead_wood",
            )

        if perso_woodcutting_level == 30:
            print(f"{self.perso_name} has enough woodcutting for today.")
        else:
            self.perform_woodcutting()

    # -----------------------------------------------------
    # TASKS AND MONSTERS FARMING
    # -----------------------------------------------------

    def farming(
        self,
        poi: PointOfInterest,
        quantity: int,
    ):
        """Farming."""
        for _ in range(quantity):
            # if character.consumable1_slot_quantity <= 1:
            #     self.withdraw_bank(
            #         code="cooked_gudgeon",
            #         quantity=10,
            #     )
            #     if character.consumable1_slot != "":
            #         self.unequip_item(slot=SlotEnum.CONSUMABLE1)
            #     self.equip_item(code="cooked_gudgeon")
            if self.get_perso_available_inventory_space() < 10:
                self.flush_inventory()

            self.fight(
                poi=poi,
            )

    def farm_monster(
        self,
        monster: str,
        quantity: int = 1000,
    ):
        """Farm monster."""
        maps = self.get_all_maps(
            content_code=monster,
            content_type="monster",
        )

        self.farming(
            poi=PointOfInterest(
                x=maps[0].x,
                y=maps[0].y,
                description=maps[0].skin,
            ),
            quantity=quantity,
        )

    def perform_task(
        self,
    ):
        """Perform Task."""
        character = self.get_character()
        if character.task != "":
            print(f"{self.perso_name} has a task ...")
            if character.task_progress < character.task_total:
                print("And it's not completed.")
                if character.task_type == "monsters":
                    quantity = character.task_total - character.task_progress
                    print(f"{self.perso_name} will kill {quantity} {character.task}.")
                    monster = self.get_monster(code=character.task)
                    if self.can_win_fight(monster=monster):
                        self.farm_monster(
                            monster=character.task,
                            quantity=quantity,
                        )
                        self.perform_task()
            else:
                print("And it's already complete.")
                self.complete_task()
                self.perform_task()
        else:
            self.accept_new_task()
            self.perform_task()

    # -----------------------------------------------------
    # LVL1 TO LVL5
    # -----------------------------------------------------

    # def rise_to_lvl5(
    #     self,
    # ):
    #     """Actions for leveling until lvl5."""
    #     self.recipes.first_ash_wood()

    #     if not self.in_inventory(code="wooden_shield"): #, slot="shield"):
    #         craft_wooden_shield()

    #     if not is_available(code="wooden_staff", slot="weapon"):
    #         craft_wooden_staff()

    # -----------------------------------------------------
    # RECIPES
    # -----------------------------------------------------

    # LVL 1
    def craft_lvl1_equipments(
        self,
    ):
        """Craft Level1 equipments before fighting."""
        for code in [
            "wooden_staff",
            "wooden_shield",
            "copper_helmet",
            "copper_boots",
            "copper_ring",
            "copper_ring",
        ]:
            self.find_and_get_item(code=code)
            self.equip_item(
                code=code,
            )

        # Then fight !
        self.fight_to_lvl5()

    def chicken_loot_strategy(
        self,
    ):
        """Chicken loot strategy."""
        feathers = self.in_inventory(code="feather")
        if feathers:
            self.deposit_bank(
                code=feathers.code,
                quantity=feathers.quantity,
            )

        eggs = self.in_inventory(code="eggs")
        if eggs:
            self.deposit_bank(
                code=eggs.code,
                quantity=eggs.quantity,
            )

        golden_eggs = self.in_inventory(code="golden_egg")
        if golden_eggs:
            self.deposit_bank(
                code=golden_eggs.code,
                quantity=golden_eggs.quantity,
            )

        raw_chickens = self.in_inventory(code="raw_chicken")
        if raw_chickens:
            self.crafting(
                code="cooked_chicken",
                quantity=raw_chickens.quantity,
                poi=locations.cooking_workshop,
            )

        cooked_chickens = self.in_inventory(code="cooked_chicken")
        if cooked_chickens:
            self.deposit_bank(
                code=cooked_chickens.code,
                quantity=cooked_chickens.quantity,
            )

    # LVL 5
    def fight_to_lvl5(
        self,
    ):
        """Fight to rise lvl5."""
        character = self.get_character()

        while character.level < 5:
            if character.consumable1_slot_quantity <= 1:
                self.find_and_get_item("cooked_gudgeon", quantity=10)
                self.unequip_item(slot=SlotEnum.CONSUMABLE1)
                self.equip_item("cooked_gudgeon")
            if self.get_perso_available_inventory_space() < 10:
                self.chicken_loot_strategy()

            self.fight(
                poi=locations.chicken_monster,
            )
            character = self.get_character()

        print(character)

        self.chicken_loot_strategy()

        if character.consumable1_slot_quantity <= 1:
            self.craft_10_cooked_gudgeon_fish()

        if character.level >= 5:
            self.craft_lvl5_armor()
        else:
            self.fight_to_lvl5()

    def craft_copper_legs(
        self,
    ):
        """Craft Copper Legs.

        Need 4 copper, so we need to gather 24 copper ore
        """
        print(f"{self.perso_name} wants to craft Copper Legs.")

        # Gather 18 copper ore
        self.gathering(
            quantity=24,
            poi=locations.copper_rocks,
        )

        # Craft 3 copper
        self.crafting(
            code="copper",
            quantity=4,
            poi=locations.mining_workshop,
        )

        # Craft Copper Boots
        self.crafting(
            code="copper_legs_armor",
            quantity=1,
            poi=locations.gear_workshop,
        )

        # Equip Copper Boots
        self.equip_item(
            code="copper_legs_armor",
        )

    def craft_copper_armor(
        self,
    ):
        """Craft Copper Armor.

        Need 5 copper, so we need to gather 30 copper ore
        """
        print(f"{self.perso_name} wants to craft Copper Armor.")

        # Gather 18 copper ore
        self.gathering(
            quantity=30,
            poi=locations.copper_rocks,
        )

        # Craft 3 copper
        self.crafting(
            code="copper",
            quantity=5,
            poi=locations.mining_workshop,
        )

        # Craft Copper Boots
        self.crafting(
            code="copper_armor",
            quantity=1,
            poi=locations.gear_workshop,
        )

        # Equip Copper Boots
        self.equip_item(
            code="copper_armor",
        )

    def rise_to_lvl5_in_blacksmithing(
        self,
    ):
        """Craft Level 5 armor."""
        character = self.get_character()

        while character.weaponcrafting_level < 5:
            self.craft_copper_dagger()
            self.ge_sell_item(
                code="copper_dagger",
                quantity=1
            )
            character = self.get_character()

        while character.gearcrafting_level < 5:
            self.craft_copper_boots()
            self.ge_sell_item(
                code="copper_boots",
                quantity=1
            )
            character = self.get_character()

        while character.jewelrycrafting_level < 5:
            self.craft_copper_rings()
            self.ge_sell_item(
                code="copper_ring",
                quantity=2
            )
            character = self.get_character()

        self.craft_copper_legs()
        self.craft_copper_armor()

    def craft_life_amulet(
        self,
    ):
        """Craft Life Amulet.

        Need 1 blue and 1 red slimeball, and 2 cowhide
        """
        print(f"{self.perso_name} wants to craft Life Amulter.")

        # Necessary materials
        self.withdraw_bank(
            code="blue_slimeball",
            quantity=1,
        )

        self.withdraw_bank(
            code="red_slimeball",
            quantity=1,
        )

        self.withdraw_bank(
            code="cowhide",
            quantity=2,
        )

        # Craft Item
        self.crafting(
            code="life_amulet",
            quantity=1,
            poi=locations.jewelry_workshop,
        )

        # Deposit Bank
        self.deposit_bank(
            code="life_amulet",
            quantity=1,
        )

    # LVL 10
    def rise_lvl10_crafting(
        self,
    ):
        """Craft Level 10."""
        character = self.get_character()

        while character.gearcrafting_level < 10:
            self.craft_copper_legs()
            self.ge_sell_item(
                code="copper_legs",
                quantity=1
            )
            character = self.get_character()

        while character.weaponcrafting_level < 10:
            self.craft_copper_dagger()
            self.ge_sell_item(
                code="copper_dagger",
                quantity=1
            )
            character = self.get_character()

        while character.jewelrycrafting_level < 10:
            self.craft_life_amulet()
            character = self.get_character()

        self.rise_lvl15_crafting()

    # LVL 15
    def craft_iron_boots(
        self,
    ):
        """Craft Iron Boots.

        Need 6 iron, so we need to gather 36 iron ore
        """
        print(f"{self.perso_name} wants to craft Iron Boots.")

        # Gather 18 iron ore
        self.gathering(
            quantity=36,
            poi=locations.iron_rocks,
        )

        # Craft 3 iron
        self.crafting(
            code="iron",
            quantity=6,
            poi=locations.mining_workshop,
        )

        # self.withdraw_bank(
        #     code="iron",
        #     quantity=6,
        # )

        # Craft Iron Boots
        self.crafting(
            code="iron_boots",
            quantity=1,
            poi=locations.gear_workshop,
        )

    def craft_iron_rings(
        self,
    ):
        """Craft Iron Rings.

        Need 2*6 iron, so we need to gather 2*36 iron ore
        """
        print(f"{self.perso_name} wants to craft Iron Rings.")

        # Get 12 iron bare
        self.find_and_get_item("iron", quantity=12)

        # Craft Iron Boots
        self.crafting(
            code="iron_ring",
            quantity=2,
            poi=locations.jewelry_workshop,
        )

    def craft_iron_sword(
        self,
    ):
        """Craft Iron Sword.

        Need 8 iron, so we need to gather 48 iron ore
        """
        print(f"{self.perso_name} wants to craft Iron Sword.")

        # Gather 18 iron ore
        self.gathering(
            quantity=48,
            poi=locations.iron_rocks,
        )

        # Craft 3 iron
        self.crafting(
            code="iron",
            quantity=8,
            poi=locations.mining_workshop,
        )

        # self.withdraw_bank(
        #     code="iron",
        #     quantity=8,
        # )

        # Craft Iron Dagger
        self.crafting(
            code="iron_sword",
            quantity=1,
            poi=locations.weapon_workshop,
        )

    def rise_lvl15_crafting(
        self,
    ):
        """Rise to Level 15 in blacksmith."""
        character = self.get_character()
        while character.weaponcrafting_level < 15:
            self.craft_iron_sword()
            self.recycling(
                code="iron_sword",
                quantity=1,
                poi=locations.weapon_workshop,
            )
            self.flush_inventory()
            character = self.get_character()

        while character.gearcrafting_level < 15:
            self.craft_iron_boots()
            self.recycling(
                code="iron_boots",
                quantity=1,
                poi=locations.gear_workshop
            )
            self.flush_inventory()
            character = self.get_character()

        while character.jewelrycrafting_level < 15:
            self.craft_iron_rings()
            self.deposit_bank(
                code="iron_ring",
                quantity=2
            )
            character = self.get_character()

    def craft_multislimes_sword(
        self,
    ):
        """Craft Multislimes Sword.

        Need 1 iron, so we need to gather 48 iron ore
        """
        print(f"{self.perso_name} wants to craft Multislimes Sword.")

        self.withdraw_bank(
            code="iron_sword",
            quantity=1,
        )

        self.withdraw_bank(
            code="blue_slimeball",
            quantity=3,
        )

        self.withdraw_bank(
            code="red_slimeball",
            quantity=3,
        )

        self.withdraw_bank(
            code="green_slimeball",
            quantity=3,
        )

        self.withdraw_bank(
            code="yellow_slimeball",
            quantity=3,
        )

        # Craft Iron Dagger
        self.crafting(
            code="multislimes_sword",
            quantity=1,
            poi=locations.weapon_workshop,
        )

    def craft_lvl15_equipment(
        self,
    ):
        """Craft Level 15 equipment."""
        for item in [
            "multislimes_sword",
            "adventurer_helmet",
            "adventurer_vest",
            "adventurer_pants",
            "adventurer_boots",
        ]:
            if self.quantity_in_bank(item_code=item) < 5:
                self.find_and_get_item(code=item, quantity=5)
                self.flush_inventory()

    def equip_lvl15_equipment(
        self,
    ):
        """Equip with Level 15 equipment."""
        for item in [
            "multislimes_sword",
            "adventurer_helmet",
            "adventurer_vest",
            "adventurer_pants",
            "adventurer_boots",
            "iron_ring",
            "iron_ring",
        ]:
            if not self.is_equiped(code=item):
                self.withdraw_bank(code=item, quantity=1)
                self.equip_item(code=item)

        self.flush_inventory()

    def rise_lvl20_crafting(
        self,
    ):
        """Rise to Level 20 in blacksmith."""
        character = self.get_character()
        while character.weaponcrafting_level < 20:
            self.find_and_get_item("iron_sword", quantity=1)
            self.find_and_get_item("red_slimeball", quantity=3)
            self.find_and_get_item("blue_slimeball", quantity=3)
            self.find_and_get_item("yellow_slimeball", quantity=3)
            self.find_and_get_item("green_slimeball", quantity=3)
            self.crafting(code="multislimes_sword", quantity=1, poi=locations.weapon_workshop)
            self.recycling(code="multislimes_sword", quantity=1, poi=locations.weapon_workshop)
            self.flush_inventory()
            character = self.get_character()

        while character.gearcrafting_level < 20:
            self.find_and_get_item("cowhide", quantity=6)
            self.find_and_get_item("wolf_hair", quantity=4)
            self.find_and_get_item("mushroom", quantity=3)
            self.find_and_get_item("spruce_plank", quantity=2)
            self.crafting(code="adventurer_boots", quantity=1, poi=locations.gear_workshop)
            self.recycling(code="adventurer_boots", quantity=1, poi=locations.gear_workshop)
            self.flush_inventory()
            character = self.get_character()

        while character.jewelrycrafting_level < 20:
            self.find_and_get_item("iron_ring", quantity=2)
            self.find_and_get_item("feather", quantity=4)
            self.find_and_get_item("mushroom", quantity=4)
            self.crafting(code="life_ring", quantity=2, poi=locations.jewelry_workshop)
            self.flush_inventory()
            character = self.get_character()

    def can_win_fight(
        self,
        monster: MonsterSchema,
    ):
        """Return True if the player can with the fight against the monster."""
        character = self.get_character()

        character_damage = (
            (character.attack_fire * (1 + (character.dmg_fire / 100))) * (1 - (monster.res_fire / 100))
            + (character.attack_water * (1 + (character.dmg_water / 100))) * (1 - (monster.res_water / 100))
            + (character.attack_air * (1 + (character.dmg_air / 100))) * (1 - (monster.res_air / 100))
            + (character.attack_earth * (1 + (character.dmg_earth / 100))) * (1 - (monster.res_earth / 100))
        )

        monster_damage = (
            (monster.attack_fire * (1 - (character.res_fire / 100)))
            + (monster.attack_water * (1 - (character.res_water / 100)))
            + (monster.attack_air * (1 - (character.res_air / 100)))
            + (monster.attack_earth * (1 - (character.res_earth / 100)))
        )

        monster_hp = monster.hp
        character_hp = character.hp

        while monster_hp > 0 and character_hp > 0:
            monster_hp -= character_damage
            character_hp -= monster_damage

        if monster_hp < 0:
            print(f"{self.perso_name} should win the fight: Character:{int(character_hp)} / Monster:{int(monster_hp)}")
            return True
        print(f"{self.perso_name} should loose fight: Character:{int(character_hp)} / Monster:{int(monster_hp)}")
        return False

    def craft_lvl20_equipment(
        self,
    ):
        """Equip with Level 20 equipment."""
        for item in [
            "steel_axe",
            "steel_armor",
            "steel_legs_armor",
            # "adventurer_pants",
            # "adventurer_boots",
            # "iron_ring",
            # "iron_ring",
        ]:
            if self.quantity_in_bank(item_code=item) < 1:
                self.find_and_get_item(code=item, quantity=1)
                self.flush_inventory()

    def craft_ogre_equipment(
        self,
    ):
        """Equip with Ogre equipment."""
        for item in [
            # "steel_helm",
            # "skeleton_armor",
            # "skeleton_pants",
            # "skull_staff",
            # "ruby_amulet",
            # "ring_of_chance",
            # After killing Ogres, better stuffs and to kill vampire
            # "steel_boots",
            # "steel_shield",
            # "tromatising_mask",
            # "dreadful_ring",
            # "topaz_amulet",


        ]:
            if self.quantity_in_bank(item_code=item) < 1:
                self.find_and_get_item(code=item, quantity=1)
                self.flush_inventory()

    def rise_lvl25_crafting(
        self,
    ):
        """Rise to Level 25 in blacksmith."""
        character = self.get_character()
        while character.weaponcrafting_level < 25:
            self.find_and_get_item("steel", quantity=10)
            self.find_and_get_item("spruce_plank", quantity=4)
            self.find_and_get_item("wolf_hair", quantity=3)
            self.crafting(code="steel_axe", quantity=1, poi=locations.weapon_workshop)
            self.recycling(code="steel_axe", quantity=1, poi=locations.weapon_workshop)
            self.flush_inventory()
            character = self.get_character()

        while character.gearcrafting_level < 25:
            self.find_and_get_item("steel", quantity=10)
            self.find_and_get_item("feather", quantity=4)
            self.find_and_get_item("pig_skin", quantity=2)
            self.crafting(code="steel_legs_armor", quantity=1, poi=locations.gear_workshop)
            self.recycling(code="steel_legs_armor", quantity=1, poi=locations.gear_workshop)
            self.flush_inventory()
            character = self.get_character()

        while character.jewelrycrafting_level < 25:
            self.find_and_get_item("steel", quantity=12)
            self.crafting(code="steel_ring", quantity=2, poi=locations.jewelry_workshop)
            self.flush_inventory()
            character = self.get_character()
