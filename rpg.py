class Game:
    def __init__(self):
        self.rooms = {
            'cabin': {'description': 'A small wooden cabin with a flickering lantern.', 'exits': {'n': 'forest'}, 'items': ['map'], 'actions':{}, 'lightLvl': 1},
            'forest': {'description': 'A dense, dark forest. Paths lead south and east.', 'exits': {'s': 'cabin', 'e': 'cave'}, 'items': [], 'actions':{}, 'lightLvl': .75},
            'cave': {'description': 'A damp cave with strange markings on the walls.', 'exits': {'w': 'forest', 'e': 'shop'}, 'items': ['torch'], 'actions':{'read markings'}, 'lightLvl': .25},
            'shop': {'description': 'A small shop run by a mysterious merchant.', 'exits': {'w': 'cave'}, 'items': [], 'shop': {'potion': 5, 'sword': 15, 'shield': 10}, 'actions':{}, 'lightLvl': 1}
        }
        self.current_room = 'cabin'
        self.inventory = []
        self.lightLvl = 1
        self.gold = 10
        self.hours = 6
        self.minutes = 0
        self.health = 100
        self.attack = 10
        self.defense = 5

        #Misc Varibles
        self.holdingTorch = 0

    def advance_time(self, minutes):
        self.minutes += minutes
        while self.minutes >= 60:
            self.minutes -= 60
            self.hours += 1
        print(f"Current time: {self.format_time()}")

    def format_time(self):
        return f"{self.hours:02}:{self.minutes:02}"

    def show_room(self):
        if self.current_room == 'shop' and self.hours < 8:
            print("The shop is closed. Come back at 8:00 or later.")
            self.current_room = 'cave'
            return
        
        room = self.rooms[self.current_room]
        print(f"\n{room['description']}")
        print("Exits:", ", ".join(room['exits'].keys()))
        if room.get('items'):
            print("Items here:", ", ".join(room['items']))
        if 'shop' in room and self.hours >= 10:
            print("Shop Items:")
            for item, price in room['shop'].items():
                print(f"- {item} ({price} gold)")
            print("Type 'buy [item]' to purchase.")

    def read(self, action):
        if action == 'map' and action in self.inventory:
            print("You look at the map, it shows paths leading out of the cabin to the forest and beyond.")
        elif action == 'markings' and self.current_room == 'cave':
            print("The markings on the cave walls are ancient symbols, possibly a warning or... an advertisement?")
        else:
            print("There's nothing to read here.")

    def use(self, item):
        if item in self.inventory:
            if item == 'potion':
                self.health = min(100, self.health + 20)
                self.inventory.remove(item)
                print("You drank a potion and restored 20 HP!")
            elif item == 'torch':
                if self.holdingTorch == 0:
                    print("The torch lights up the dark surroundings.")
                    self.lightLvl = 1
                    self.holdingTorch = 1
                    print(self.lightLvl)
                elif self.holdingTorch == 1:
                    print("You snuff out the flame of your torch onto the ground.")
                    self.lightLvl = self.rooms[self.current_room]['lightLvl']
                    self.holdingTorch = 0
                    print(self.lightLvl)
            else:
                print("Nothing happens.")
        else:
            print("You don't have that item.")

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

    def take(self, item):
        if item in self.rooms[self.current_room]['items']:
            self.rooms[self.current_room]['items'].remove(item)
            self.inventory.append(item)
            print(f"You picked up the {item}.")
        else:
            print("That item isn't here.")

    def show_inventory(self):
        print("Your inventory:", ", ".join(self.inventory) if self.inventory else "Empty")
        print(f"Gold: {self.gold}")

    def buy(self, item):
        room = self.rooms[self.current_room]
        if self.current_room != 'shop':
            print("You're not in a shop.")
            return
        if self.hours < 10:
            print("The shop is closed. Come back at 10:00 or later.")
            return
        if item in room['shop']:
            cost = room['shop'][item]
            if self.gold >= cost:
                self.gold -= cost
                self.inventory.append(item)
                print(f"You bought a {item} for {cost} gold.")
            else:
                print("Not enough gold.")
        else:
            print("That item is not for sale here.")
    def stats(self):
        print("------ STATS ------")
        print(f"{'Health:':<15} {self.health:<10}")
        print(f"{'Defense:':<15} {self.defense:<10}")
        print(f"{'Attack:':<15} {self.attack:<10}")
        print("--------------------")
    def run(self):
        self.show_room()
        while True:
            command = input("\n> ").lower().split()
            if not command:
                continue
            if command[0] in ['n', 'e', 's', 'w']:
                self.move(command[0])
            elif command[0] == 'take' and len(command) > 1:
                self.take(command[1])
            elif command[0] == 'inventory':
                self.show_inventory()
            elif command[0] == 'buy' and len(command) > 1:
                self.buy(command[1])
            elif command[0] == 'use' and len(command) > 1:
                self.use(command[1])
            elif command[0] == 'wait':
                if len(command) == 1:
                    self.advance_time(30)
                elif len(command) > 1:
                    try:
                        wait_time = int(command[1])
                        if wait_time > 0:
                            self.advance_time(wait_time)
                        else:
                            print("You can't wait for a negative amount of time!")
                    except ValueError:
                        print("Invalid wait time. Enter a number.")
            elif command[0] == 'look':
                self.show_room()
            elif command[0] == 'time':
                print(f"Current time: {self.format_time()}")
            elif command[0] == 'stats':
                self.stats()
            elif command[0] == 'read':
                self.read(''.join(command[1]))
            elif command[0] == 'quit':
                print("Thanks for playing!\n")
                break
            else:
                print("Invalid command. Type 'help' for options.")

    def menu(self):
        print("Welcome to the RPG! Type 'help' for commands.\n")
        input('Press Enter to Begin. \n>')
        self.run()


if __name__ == "__main__":
    Game().menu()
