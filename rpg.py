import time
import pickle
import os
import random
import threading

#TOADD light description option bc its annoying

class enemy:
    def __init__(self, name, health, maxAttack, defense):
        self.name = name
        self.health = health
        self.maxAttack = maxAttack
        self.defense = defense
        self.attackCD = 3

    def takeDmg(self, dmg):
        self.health -= dmg
        if self.health < 0: 
            self.health = 0

    def isAlive(self):
        if self.health > 0:
            return 1
        if self.health <= 0:
            return 0
class weapon:
    def __init__(self, name, damage):
        self.name = name
        self.damage = damage
class armor:
    def __init__(self, name, defense):
        self.name = name 
        self.defense = defense

class LongSword(weapon):
    def __init__(self):
        super().__init__("Long Sword", damage=10)
class SteelPlate(armor):
    def __init__(self):
        super().__init__("Steel Plate", defense=10)


class Goblin(enemy):
    def __init__(self):
        super().__init__("Goblin", health=50, maxAttack=5, defense=2)
class Rat(enemy):
    def __init__(self):
        super().__init__("Rat", health=2, maxAttack=1, defense=1)

class Game:
    def __init__(self):
        self.rooms = {
            'cabin': {'description': 'A small wooden cabin with a flickering lantern.', 'exits': {'n': 'forest'}, 'items': ['map', 'cigar', 'new gun'], 'actions':{}, 'lightLvl': 1},
            'forest': {'description': 'A dense, dark forest. Paths lead in every direction.', 'exits': {'n': 'clearing', 'e': 'cave', 's': 'cabin', 'w': 'village outskirts' }, 'items': [], 'actions':{}, 'lightLvl': .75},
            'village outskirts': {'description': 'You can see a nearby village roll into view just above the horizon to the west.', 'exits': {'e': 'forest', 'w': 'villa village'}, 'items': [], 'actions':{}, 'lightLvl': 1},
            'villa village': {'description': 'The village is rather small and the smell of bread wafts through the air.\n\nThe forest looms to the east\n', 'exits': {'e': 'village outskirts'}, 'items': [], 'actions':{}, 'lightLvl': 1},
            'clearing': {'description': 'A rather empty clearing in the forest. The trees are sparse with grass covering the earth. The sun shines brightly.', 'exits': {'s': 'forest'}, 'items': ['rock'], 'actions':{}, 'lightLvl': 1, "enemies": [Rat()]},
            'cave': {'description': 'A damp cave with strange markings on the walls. \n\nThe light of the forest shines from the west.', 'exits': {'n': 'dungeon landing', 'w': 'forest', 'e': 'shop'}, 'items': ['torch'], 'actions':{'read markings'}, 'lightLvl': .25, 'enemies': [Goblin(), Rat()]},
            'dungeon landing': {'description': 'The floor is wet beneath your feet and the walls almost seem to excrete mold. \n\nThere is a slight breeze that makes your skin crawl. \n\nThe only ways out are forward or backwards.\n', 'exits': {'s': 'cave'}, 'items': [''], 'actions':{}, 'lightLvl': .50, "enemies": [Rat()]},
            'shop': {'description': 'A small shop run by a mysterious merchant.', 'exits': {'w': 'cave'}, 'items': [], 'shop': {'potion': 5, "Long Sword": 15, "Steel Plate": 10}, 'actions':{}, 'lightLvl': 1}
        }
        self.current_room = 'cabin'
        self.inventory = []
        self.lightLvl = 1
        self.gold = 100
        self.hours = 6
        self.minutes = 0
        self.maxHealth = 50
        self.health = 50
        self.attack = 5
        self.attackCD = 3
        self.defense = 2
        self.crit = 2
        self.critPercent = 1
        self.lightdesc = " "

        #SETTINGS
        self.lightDescriptionToggle = 1

        self.itemList = {
            'potion': {'item': 'potion', 'price': 5},
            'longsword': {'item': LongSword(), 'price': 15},
            'steelplate': {'item': SteelPlate(), 'price': 10}
        }
        self.abilityList = {
            'fireball': {'type': 'fire', 'damage': 5, 'cd': 3, 'unlocked': True, 'description': ' bursts into flames!'}
        }

        if 'enemies' in self.rooms[self.current_room]:
            self.curEnemy = self.rooms[self.current_room]['enemies']
        if self.health > self.maxHealth: self.health = self.maxHealth

        #Inventory Varibles
        self.curWeapon = None
        self.curArmor = None

        #Misc Varibles
        self.holdingTorch = False
        self.holdingShield = False
        self.holdingWeapon = False
        self.activeCombat = False
        self.casted = False
        self.canCast = True

        self.toggle = " "

    def onORoff(self, target):
        if target == 1:
            self.toggle = "On"
            return True
        if target == 0:
            self.toggle = "Off"
            return False
    #Combat
    def critChance(self):
        critChance = random.randint(1,10) - self.critPercent
        if critChance == 0: critChance = 1
        if critChance <= self.critPercent:
            critDMG = self.crit
            return critDMG
        else: return 1
    def spellCD(self, abilityName):
        def cd_timer():
            spell = self.abilityList.get(abilityName.lower())
            spellCD = spell['cd']
            timer = 0
            while self.casted:
                if timer >= spellCD:
                    self.canCast = True
                    self.casted = False
                    timer = 0
                    break
                else:
                    self.canCast = False
                    time.sleep(1)
                    timer += 1
        threading.Thread(target=cd_timer, daemon=True).start()

    def cast(self, abilityName, enemyName):
        statuseffectChance = random.randint(1,10)
        ability = self.abilityList.get(abilityName.lower())
        if not self.canCast: 
            print("You cannot muster the strength.")
            return
        if not ability:
            print(f"You don't know any ability called '{abilityName}'.")
            return
        if ability['unlocked'] == False:
            print(f"You haven't learned {abilityName} yet!")
            return

        room_enemies = self.rooms[self.current_room].get("enemies", [])
        for enemy in room_enemies:
            if enemy.name.lower() == enemyName.lower():
                if not enemy.isAlive():
                    print(f"{enemy.name} is already dead.")
                    return

                damage = ability['damage'] - enemy.defense
                damage = max(damage, 0)
                enemy.takeDmg(damage)
                print(f"You use {abilityName.title()} on {enemy.name} for {damage} damage!")
                print(f"{enemy.name} has {enemy.health} health left.")
                self.casted = True
                self.spellCD(abilityName)
                if statuseffectChance > 6: 
                    print(f"{enemy.name}{ability['description']}")
                    self.statusEffects(ability['type'], enemy, ability['cd'])

                
                if not enemy.isAlive():
                    print(f"You defeated the {enemy.name}!")
                    enemy.name = f"Dead {enemy.name}"
                return
        print(f"No enemy named '{enemyName}' here.")

    def statusEffects(self, effect_type, target, cd):
        def effect():
            timer = 0
            while cd:
                if timer >= cd or target.health <= 0: break
                endChance = random.randint(1, 10)
                if effect_type == 'fire':
                    burnDmg = random.randint(1, 5)
                    if endChance > 7:
                        print("The flame fizzles out.")
                        break
                    target.takeDmg(burnDmg)
                    print(f"{target.name} continues to burn! Enemy health remaining: {target.health}\n")
                timer += 1
                time.sleep(2)

        threading.Thread(target=effect).start()

    def dealdmg(self, enemy_name):
        room_enemies = self.rooms[self.current_room].get("enemies", [])
        for enemy in room_enemies:
            if enemy.name.lower() == enemy_name.lower():
                self.curEnemy = enemy
                if self.curEnemy.isAlive():
                    totalDMG = self.attack * self.critChance() - self.curEnemy.defense
                    totalDMG = max(totalDMG, 0)
                    self.curEnemy.takeDmg(totalDMG)
                    if self.curEnemy.health < 0: self.curEnemy.health = 0
                    print(f"You attack {self.curEnemy.name} for {totalDMG}!")
                    print(f"{self.curEnemy.name} has {self.curEnemy.health} health left!")
                    if not self.curEnemy.isAlive():
                        print(f"You defeated the {self.curEnemy.name}!")
                        if not self.curEnemy.name.startswith("Dead "):
                            self.curEnemy.name = (f"Dead {self.curEnemy.name}")
                else:
                    print("The corpse is now cold.")
                return
        if enemy_name.startswith("Dead"):
            print("They're already dead, nutjob.")
        print(f"{enemy_name} is not here.")

    def takeDMG(self, attackCD):
        self.activeCombat = True
        def dmg():
            if self.curEnemy.health > 0 and self.activeCombat and self.curEnemy in self.rooms[self.current_room]['enemies']:
                #if self.health <= 0: break
                time.sleep(3)
                totalDmg = self.curEnemy.maxAttack - self.defense
                self.health -= totalDmg
                print(f"\n{self.curEnemy.name} attacks you for {totalDmg}!")
                print(f"You have {self.health} health left!\n")
        threading.Thread(target=dmg).start()
    def kill(self, target_name):
        room_enemies = self.rooms[self.current_room].get("enemies", [])
        for enemy in room_enemies:
            if enemy.name.lower() == target_name.lower():
                self.curEnemy = enemy
                break
        else:
            print(f"No enemy named '{target_name}' here.")
            return

        def combat_loop(): #add time.sleep
            player_cd = self.attackCD
            enemy_cd = self.curEnemy.attackCD

            player_timer = 0
            enemy_timer = 0

            while self.health > 0 and self.curEnemy.isAlive():
                player_timer += 1
                enemy_timer += 1

                # Player's turn
                if player_timer >= player_cd:
                    totalDMG = self.attack * self.critChance() - self.curEnemy.defense
                    totalDMG = max(totalDMG, 0)
                    self.curEnemy.takeDmg(totalDMG)
                    print(f"\nYou attack {self.curEnemy.name} for {totalDMG} damage!")
                    print(f"{self.curEnemy.name} has {self.curEnemy.health} health left.")
                    player_timer = 0
                    time.sleep(1)
                    if not self.curEnemy.isAlive():
                        print(f"You defeated the {self.curEnemy.name}!")
                        if not self.curEnemy.name.startswith("Dead "):
                            self.curEnemy.name = "Dead " + self.curEnemy.name
                        break

                # Enemy's turn
                if enemy_timer >= enemy_cd:
                    totalDmg = self.curEnemy.maxAttack - self.defense
                    totalDmg = max(totalDmg, 0)
                    self.health -= totalDmg
                    print(f"\n{self.curEnemy.name} attacks you for {totalDmg}!")
                    print(f"You have {self.health} health left!")
                    enemy_timer = 0
                    time.sleep(1)
                    if self.health <= 0:
                        print("You died...")
                        break
        combat_thread = threading.Thread(target=combat_loop)
        combat_thread.start()
        combat_thread.join()

    #END combat    
    

    #Time
    def advance_time(self, minutes): #advance time WITHOUT regaining hp
        self.minutes += minutes
        while self.minutes >= 60:
            self.minutes -= 60
            self.hours += 1

    def format_time(self):
        return f"{self.hours:02}:{self.minutes:02}"

    def rest(self, minutes): #rest to pass time and recover hp, add random enemy spawns
        self.minutes += minutes
        self.health = self.minutes // 10
        while self.minutes >= 60:
            self.minutes -= 60
            self.hours += 1
        print(f"\nYou rest and gain {self.health} health.")

    #END Time

    def show_room(self):
        self.lightDescription()
        if self.current_room == 'shop' and self.hours < 8:
            print("The shop is closed. Come back at 8:00 or later.")
            self.current_room = 'cave'
            return
        
        room = self.rooms[self.current_room]
        print(f"\nCurrent time: {self.format_time()}")
        print(f"\n{room['description']}")
        if self.lightDescriptionToggle == 1: print(f"{self.lightdesc}\n")
        #if self.lightDescriptionToggle == 0: print("\n")
        print("Exits:", ", ".join(room['exits'].keys()))
        if 'shop' in room and self.hours >= 8:
            print("Shop Items:")
            for item, price in room['shop'].items():
                print(f"- {item} ({price} gold)")
            print("Type 'buy [item]' to purchase.")
        if 'enemies' in room:
            room_enemies = room['enemies']
            if room_enemies:
                enemy_names = [enemy.name for enemy in room_enemies]
                print(f"\nYou also see: {', '.join(enemy_names)}.")
            self.curEnemy = room['enemies'][0]


    #Interactions
    
    def read(self, action):
        if action == 'map' and action in self.inventory:
            print("You look at the map, it shows paths leading out of the cabin to the forest and beyond.")
        elif action == 'markings' and self.current_room == 'cave':
            print("The markings on the cave walls are ancient symbols, possibly a warning or... an advertisement?")
        else:
            print("There's nothing to read here.")

    def use(self, item_name):
        for item in self.inventory:
            if isinstance(item, str) and item == item_name:
                if item == 'potion':
                    self.health = min(100, self.health + 20)
                    self.inventory.remove(item)
                    print("You drank a potion and restored 20 HP!")
                elif item == 'torch':
                    if not self.holdingTorch:
                        print("The torch lights up the area around you.")
                        self.lightLvl = 1
                        self.holdingTorch = True
                    else:
                        print("You snuff out the flame of your torch onto the ground.")
                        self.lightLvl = self.rooms[self.current_room]['lightLvl']
                        self.holdingTorch = False
                        self.inventory.remove(item)
                else:
                    print("Nothing happens.")
                return

            elif isinstance(item, weapon) and item_name == item.name.lower():
                if not self.holdingWeapon:
                    self.attack += item.damage
                    self.curWeapon = item
                    self.holdingWeapon = True
                    print(f"You equipped your {item.name}!")
                else:
                    self.attack -= item.damage
                    self.curWeapon = None
                    self.holdingWeapon = False
                    print(f"You unequipped your {item.name}!")

                return

            elif isinstance(item, armor) and item_name == item.name.lower():
                if not self.holdingShield:
                    self.defense += item.defense
                    self.curArmor = item
                    self.holdingShield = True
                    print(f"You equipped your {item.name}!")
                else:
                    self.defense -= item.defense
                    self.curArmor = None
                    self.holdingShield = False
                    print(f"You unequipped your {item.name}!")
                return
        else:
            print("You don't have that item.")


    def buy(self, item):
        room = self.rooms[self.current_room]
        item = item.lower().replace(" ", "")  # Remove spaces and convert to lowercase

        if self.current_room != 'shop':
            print("You're not in a shop.")
            return
        if self.hours < 8:
            print("The shop is closed. Come back at 8:00 or later.")
            return
        for shop_item_name in room['shop']:
            if item == shop_item_name.lower().replace(" ", ""):
                cost = room['shop'][shop_item_name]
                if self.gold >= cost:
                    self.gold -= cost

                    key = shop_item_name.lower().replace(" ", "")
                    if key in self.itemList:
                        self.inventory.append(self.itemList[key]['item'])
                        print(f"You bought a {shop_item_name} for {cost} gold.")
                    else:
                        self.inventory.append(shop_item_name)
                        print(f"You bought a {shop_item_name} for {cost} gold.")
                else:
                    print("Not enough gold.")
                return
        else:
            print("That item is not for sale here.")
            print(item)

    def take(self, item):
        if item in self.rooms[self.current_room]['items']:
            self.rooms[self.current_room]['items'].remove(item)
            self.inventory.append(item)
            print(f"You picked up the {item}.")
        else:
            print("That item isn't here.")
    #END interactions

    def lightDescription(self): #Returns lighting desciption based on the light level.
        if self.lightDescriptionToggle == 0:
            return

        rlightlvl = self.rooms[self.current_room]['lightLvl']

        bright_descriptions = [
            "\nSunlight floods the area.",
            "\nThe area is brightly lit, without a shadow in sight.",
            "\nLight spills from all around you with a warm glow.",
            "\nThe area around you feels bright and inviting.",
            "\nEvery object is plainly visible, illuminated by strong lighting.",
        ]

        moderate_descriptions = [
            "\nShadows loom in the corners, but most of the area is visible.",
            "\nA pale light hangs in the air, leaving some details obscured.",
            "\nFlickering light makes the space feel uncertain but not unseeable.",
            "\nYou can make out shapes and outlines although finer details are lost in the dimness.",
            "\nThe dim light manages to keep the shadows at bay.",
        ]

        dark_descriptions = [
            "\nThe darkness is oppressive, swallowing up the edges of the area.",
            "\nOnly the vaguest outlines can be seen in the murky blackness.",
            "\nThe area is too dark to make out much detail.",
            "\nShadows dominate the space, hiding what may lurk within.",
            "\nIt’s pitch black. You might as well have your eyes closed.",
        ]

        if rlightlvl >= 1:
            self.lightdesc = random.choice(bright_descriptions)
        elif rlightlvl >= 0.5:
            self.lightdesc = random.choice(moderate_descriptions)
        else:
            self.lightdesc = random.choice(dark_descriptions)

    #Misc Commands
    def settings(self):
        print("\n------ Settings ------")
        print(f"Lighting Descriptions: {self.onORoff(self.lightDescriptionToggle)}")
        print("--------------------\n")
        print(f"\nTo change a setting, use: toggle <setting>")
    def toggleSettings(self, setting):
        if setting.lower() == "lighting desciption" or "lighting desciptions" or "lighting":
            if self.lightDescriptionToggle == 1:
                self.lightDescriptionToggle = 0
                print("\nSetting Changed!")
                return
            if self.lightDescriptionToggle == 0:
                self.lightDescriptionToggle = 1
                print("\nSetting Changed!")
                return

    def move(self, direction):
        if direction in self.rooms[self.current_room]['exits']:
            next_room = self.rooms[self.current_room]['exits'][direction]
            if 'shop' in next_room and self.hours < 8:
                print("The shop is closed. Come back at 8:00 or later.")
                return
            self.current_room = next_room
            self.advance_time(10)
            self.show_room()
        else:
            print("You can't go that way.")

    def show_inventory(self):
        print("Your inventory:", ", ".join(
        item.name if hasattr(item, 'name') else str(item)
        for item in self.inventory
        ) if self.inventory else "Empty")        
        print(f"Gold: {self.gold}")


    def stats(self):
        print("------ STATS ------")
        print(f"{'Health:':<15} {self.health:<10}")
        print(f"{'Defense:':<15} {self.defense:<10}")
        print(f"{'Attack:':<15} {self.attack:<10}")
        print("--------------------")

    def spellList(self):
        for spell_name, spell_info in self.abilityList.items():
            known = spell_info.get('unlocked')
            if known:
                damage = spell_info.get('damage', 0)
                spell_type = spell_info.get('type', 'Unknown')
                print(f"- {spell_name.title()} (Type: {spell_type}, Damage: {damage})")

    def save_game(self, filename='savegame.pkl'):
        with open(filename, 'wb') as f:
            pickle.dump(self.__dict__, f)
        print("Game saved successfully.")

    def load_game(self, filename='savegame.pkl'):
        if os.path.exists(filename):
            with open(filename, 'rb') as f:
                self.__dict__ = pickle.load(f)
            print("Game loaded successfully.")
            self.show_room()
        else:
            print("No save file found.")
    
    def search(self): #search the current room
        room = self.rooms[self.current_room]
        if room.get('items'):
            print("You find:", ", ".join(room['items']))
        else:
            print("You find nothing.")

    def light(self, target):
        if target == 'cigar':
            print("You light the cigar. It gives off a full, earthy aroma.")
        elif target == 'torch':
            if not self.holdingTorch:
                print("The torch lights up the dark surroundings.")
                self.lightLvl = 1
                self.holdingTorch = True
            else:
                print("You snuff out the flame of your torch onto the ground.")
                self.lightLvl = self.rooms[self.current_room]['lightLvl']
                self.holdingTorch = False
                self.inventory.remove(target)
        else:
            print(f"You shouldn't light that.")

    #END misc Commands
    def run(self):
        self.lightDescription()
        self.show_room()
        while True:
            command = input("\n> ").lower().split()
            args = command[1:]
            if not command:
                continue
            if command[0] in ['n', 'e', 's', 'w']:
                self.move(command[0])
            elif command[0] == 'take' and len(command) > 1:
                target = " ".join(args[0:])
                self.take(target)
            elif command[0] == 'inventory':
                self.show_inventory()
            elif command[0] == 'buy' and len(command) > 1:
                item_name = " ".join(command[1:]).lower()
                self.buy(item_name)
            elif command[0] == 'use' and len(command) > 1:
                item_name = " ".join(command[1:]).lower() 
                self.use(item_name)
            elif command[0] == 'wait':
                if len(command) == 1:
                    print(f"You wait for 30 minutes.")
                    self.advance_time(30)
                elif len(command) > 1:
                    try:
                        wait_time = int(command[1])
                        if wait_time > 0:
                            print(f"You wait for: {wait_time} minutes.")
                            self.advance_time(wait_time)
                        else:
                            print("You can't wait for a negative amount of time!")
                    except ValueError:
                        print("Invalid wait time. Enter a number.")
            elif command[0] == 'look':
                if self.lightLvl >= .50:
                    self.show_room()
                else:
                    print("It's a bit hard to see around you while in the dark.")
            elif command[0] == 'time':
                print(f"Current time: {self.format_time()}")
            elif command[0] == 'stats':
                self.stats()
            elif command[0] == 'spells':
                self.spellList()
            elif command[0] == 'read' and len(command) > 1:
                self.read(''.join(command[1]))
            elif command[0] == "test":
                self.curEnemy = Goblin()
                self.takeDMG()
            elif command[0] == 'attack' and len(command) > 1:
                if command[1] == 'dead':
                    print("The corpse has gone cold.")
                else:
                    self.dealdmg(command[1])
            elif command[0] == 'cast' and len(command) > 1:
                self.cast(command[1], command[2])
            elif command[0] == 'kill' and len(command) > 1:
                target = " ".join(args[0:])
                self.kill(target)
            elif command [0] == 'save':
                self.save_game()
            elif command [0] == 'load':
                self.load_game()
            elif command [0] == 'search':
                    if self.lightLvl >= .50:
                        self.search()
                    else:
                        print("You can't make anything out in the darkness.")
            elif command[0] == 'rest' and len(command) > 1:
                wait_time = int(command[1])
                if wait_time > 0:
                    self.rest(wait_time)
                else:
                     print("You can't wait for a negative amount of time!")
            elif command[0] == 'light' and len(command) > 1:
                target = " ".join(args[0:])
                self.light(target)
            elif command[0] == 'settings':
                self.settings()
            elif command[0] == 'toggle' and len(command) > 1:
                target = " ".join(args[0:])
                self.toggleSettings(target)
            elif command[0] == 'quit':
                print("Thanks for playing!\n")
                break
            elif command[0] == 'clear':
                os.system('cls')
                self.show_room()
            elif command[0] == 'help':
                print("This is an unhelpful list!")
            else:
                print("Invalid command. Type 'help' for options.")

    def menu(self):
        print("Welcome! Type 'help' for commands at any time.\n")
        input('Press Enter to Begin. \n>')
        os.system('cls')
        self.run()

Game().health = Game().maxHealth
if __name__ == "__main__":
    Game().menu()
