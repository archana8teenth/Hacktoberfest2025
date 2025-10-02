import sys

class Room:
    """Represents a location in the game world with exits."""
    def __init__(self, name, description, connections=None, is_end=False):
        self.name = name
        self.description = description
        self.connections = connections if connections is not None else {}
        self.is_end = is_end

    def add_connection(self, direction, target_room):
        self.connections[direction] = target_room

    def get_description(self):
        desc = f"--- {self.name} ---\n{self.description}\n"
        exits = ", ".join(self.connections.keys())
        desc += f"Available exits: {exits}"
        return desc

class AdventureGame:
    """Manages the state and logic for the text adventure."""
    def __init__(self):
        self.rooms = self._create_world()
        self.current_room = self.rooms['start_hall']
        self.is_running = True

    def _create_world(self):
        r1 = Room("Entrance Hall", "You are in a dusty, dimly lit hall. There is a suit of armor by the north wall.")
        r2 = Room("Treasure Chamber", "A small chamber filled with glittering gold and ancient artifacts! You win!", is_end=True)
        r3 = Room("Dark Corridor", "A narrow, dark corridor. It smells faintly of mildew.")
        r4 = Room("Storage Room", "Boxes and old crates are stacked high. A small key is visible beneath a loose floorboard.")

        r1.add_connection('north', 'dark_corridor')
        r1.add_connection('east', 'treasure_chamber')

        r3.add_connection('south', 'start_hall')
        r3.add_connection('west', 'storage_room')

        r4.add_connection('east', 'dark_corridor')

        return {
            'start_hall': r1,
            'treasure_chamber': r2,
            'dark_corridor': r3,
            'storage_room': r4,
        }

    def _handle_move(self, direction):
        if direction in self.current_room.connections:
            next_room_key = self.current_room.connections[direction]
            self.current_room = self.rooms[next_room_key]
            
            if hasattr(self.current_room, 'is_end') and self.current_room.is_end:
                print("\n" + self.current_room.get_description())
                self.is_running = False
            else:
                self.look()
        else:
            print("You cannot go that way.")

    def look(self):
        print("\n" + self.current_room.get_description())

    def quit_game(self):
        self.is_running = False
        print("\nThank you for playing. Goodbye!")

    def parse_command(self, command):
        command = command.lower().strip()
        parts = command.split()
        
        if not parts:
            return

        verb = parts[0]
        
        if verb in ('north', 'south', 'east', 'west', 'go'):
            direction = parts[-1] if verb == 'go' else verb
            self._handle_move(direction)
        elif verb in ('quit', 'exit'):
            self.quit_game()
        elif verb in ('look', 'l'):
            self.look()
        else:
            print(f"Unknown command: '{command}'. Try 'go north' or 'quit'.")


    def play(self):
        print("Welcome to the Minimal Text Adventure!")
        self.look()

        while self.is_running:
            try:
                user_input = input(">> ").strip()
                if user_input:
                    self.parse_command(user_input)
            except EOFError:
                self.quit_game()
            except KeyboardInterrupt:
                self.quit_game()
                
if __name__ == "__main__":
    game = AdventureGame()
    game.play()
