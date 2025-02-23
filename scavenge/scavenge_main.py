# scavenge/scavenge_main.py
import json
import os
import scavenge.scavenge_asteroids as scavenge_asteroids
import scavenge.scavenge_manmade as scavenge_manmade
import scavenge.scavenge_planetary as scavenge_planetary

class TextStyle:
    styles = {}

    @staticmethod
    def load_styles():
        json_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../text_styles.json")
        if not os.path.exists(json_file):
            print(f"\nError: 'text_styles.json' not found")
            return
        try:
            with open(json_file, 'r') as file:
                data = json.load(file)
                TextStyle.styles = data["styles"]
        except json.JSONDecodeError:
            print("\nError: Invalid JSON format in text_styles.json!")
            return

    @staticmethod
    def print_class(class_name, text):
        if not TextStyle.styles:
            TextStyle.load_styles()
        
        style = TextStyle.styles.get(class_name, {})
        color_map = {
            "white": "\033[97m",
            "red": "\033[91m",
            "blue": "\033[94m",
            "yellow": "\033[93m",
            "dark_gray": "\033[90m",
            "light_gray": "\033[37m",
            "gray": "\033[90m",
            "black": "\033[30m",
            "green": "\033[92m",
            "cyan": "\033[96m"
        }
        ansi = color_map.get(style.get("color", "white"), "\033[97m")
        if style.get("bold"):
            ansi += "\033[1m"
        if style.get("italic"):
            ansi += "\033[3m"
        return f"{ansi}{text}\033[0m"

TextStyle.load_styles()

def load_scavenge_data():
    json_file = "scavenge.json"
    script_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(script_dir, json_file)
    if not os.path.exists(file_path):
        print(TextStyle.print_class("Warning", f"\nError: '{json_file}' not found in {script_dir}"))
        input("Press Enter to continue...")
        return None
    
    try:
        with open(file_path, 'r') as file:
            return json.load(file)
    except json.JSONDecodeError:
        print(TextStyle.print_class("Warning", "\nError: Invalid JSON format in scavenge.json!"))
        input("Press Enter to continue...")
        return None

def get_all_locations(system):
    """Recursively collect all scavengeable locations from the system, including nested children."""
    locations = []
    if "children" in system:
        for loc in system["children"]:
            locations.append(loc)
            if "children" in loc:  # Check for nested children (e.g., Space Station under a planet)
                locations.extend(get_all_locations(loc))
    return locations

def scavenge_menu(player_data, current_system, ship_inventory):
    scavenge_data = load_scavenge_data()
    if not scavenge_data or not current_system or "children" not in current_system:
        print(TextStyle.print_class("Warning", "\nCannot scavenge: No system data available!"))
        input("Press Enter to continue...")
        return
    
    scavenge_vars = scavenge_data["scavengeVariables"]
    locations = get_all_locations(current_system)  # Use recursive function to get all locations
    available_locations = [loc for loc in locations if not loc.get("scavenged", False)]
    
    while True:
        print(TextStyle.print_class("Information", "\n=== Scavenge Menu ==="))
        print(f"{TextStyle.print_class('Information', 'Location: ')}{player_data['location']} | {TextStyle.print_class('Energy', f'Energy: {player_data['energy']}')}")
        print(TextStyle.print_class("Information", "\nAvailable Locations:"))
        
        if not locations:
            print(TextStyle.print_class("Warning", "No locations available to scavenge!"))
        else:
            for i, loc in enumerate(locations, 1):
                loc_type = scavenge_data["locationMappings"].get(loc["type"], scavenge_data["locationMappings"]["Unknown"])
                energy_cost = loc_type["resourceCost"]
                if loc.get("scavenged", False):
                    print(TextStyle.print_class("Scavenged", f"{i}) {loc['name']} ({loc['type']}) - (Scavenged)"))
                else:
                    print(TextStyle.print_class("Information", f"{i}) {loc['name']} ({loc['type']}) - {energy_cost} Energy"))
        
        print(TextStyle.print_class("Information", "0) Return to Main Menu"))
        
        choice = input("\nSelect a location to scavenge (0-{}): ".format(len(locations)))
        
        try:
            choice = int(choice)
            if choice == 0:
                print(TextStyle.print_class("Information", "\nReturning to main menu..."))
                return
            if choice < 1 or choice > len(locations):
                print(TextStyle.print_class("Warning", "\nInvalid choice! Please select a valid option."))
                input("Press Enter to continue...")
                continue
            
            selected_loc = locations[choice - 1]
            loc_type = selected_loc["type"]
            energy_cost = scavenge_data["locationMappings"].get(loc_type, scavenge_data["locationMappings"]["Unknown"])["resourceCost"]
            
            if selected_loc.get("scavenged", False):
                print(TextStyle.print_class("Warning", f"\n{selected_loc['name']} has already been scavenged!"))
                input("Press Enter to continue...")
                continue
            
            if player_data["energy"] < energy_cost:
                print(TextStyle.print_class("Warning", f"\nNot enough energy! Need at least {energy_cost} energy to scavenge {selected_loc['name']}."))
                input("Press Enter to continue...")
                continue
            
            if loc_type == "Planet" or loc_type == "Moon":
                scavenge_planetary.scavenge(player_data, selected_loc, ship_inventory, energy_cost, scavenge_data)
            elif loc_type == "Asteroid Field":
                scavenge_asteroids.scavenge(player_data, selected_loc, ship_inventory, energy_cost, scavenge_data)
            else:
                scavenge_manmade.scavenge(player_data, selected_loc, ship_inventory, energy_cost, scavenge_data)
            
            selected_loc["scavenged"] = True
            input("Press Enter to continue...")
        
        except ValueError:
            print(TextStyle.print_class("Warning", "\nInvalid input! Please enter a number."))
            input("Press Enter to continue...")

if __name__ == "__main__":
    test_player = {"location": "Test System", "energy": 100, "security_zone": 0.6}
    test_system = {
        "children": [
            {"type": "Planet", "name": "Rocky Planet 1", "scavenged": False, "children": []},
            {"type": "Asteroid Field", "name": "Barren Asteroid Field 1", "scavenged": True},
            {"type": "Man-Made", "name": "Space Station 42", "scavenged": False}
        ]
    }
    test_inventory = []
    scavenge_menu(test_player, test_system, test_inventory)