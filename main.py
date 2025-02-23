# main.py
import save_game
import systems.systems
import scavenge.scavenge_main  # Kept for reference, but not used in scavenging now
import fabrication.fabrication
import ships.shipsNewShip as ships
import combat.combat_main as combat
import os
import json
import random
import time
import sys

class TextStyle:
    styles = {}

    @staticmethod
    def load_styles():
        json_file = "text_styles.json"
        script_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(script_dir, json_file)
        if not os.path.exists(file_path):
            print(f"\nError: '{json_file}' not found in {script_dir}")
            return
        try:
            with open(file_path, 'r') as file:
                data = json.load(file)
                TextStyle.styles = data["styles"]
        except json.JSONDecodeError:
            print("\nError: Invalid JSON format in text_styles.json!")
            return

    @staticmethod
    def print_class(class_name, text, delay_to_display=0, display_mode="instant", char_delay=0, print_output=True):
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
        
        delay_to_display = style.get("delay_to_display", delay_to_display)
        display_mode = style.get("display_mode", display_mode)
        char_delay = style.get("char_delay", char_delay)
        
        formatted_text = f"{ansi}{text}\033[0m"
        if delay_to_display > 0:
            time.sleep(delay_to_display)
        
        if print_output:
            if display_mode == "instant" or display_mode == "line":
                print(formatted_text)
            elif display_mode == "char":
                for char in formatted_text:
                    sys.stdout.write(char)
                    sys.stdout.flush()
                    time.sleep(char_delay)
                print()
        
        return formatted_text

TextStyle.load_styles()

ship_inventory = []
home_inventory = []
current_save_file = None
explored = False
current_system = {}
player_data = {"location": "Home", "energy": 100, "universal_signature": 0}
enemy_npc = None

def load_general_data():
    json_file = "general.json"
    script_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(script_dir, json_file)
    if not os.path.exists(file_path):
        TextStyle.print_class("Warning", f"\nError: '{json_file}' not found in {script_dir}")
        input("Press Enter to continue...")
        return None
    try:
        with open(file_path, 'r') as file:
            return json.load(file)
    except json.JSONDecodeError:
        TextStyle.print_class("Warning", "\nError: Invalid JSON format in general.json!")
        input("Press Enter to continue...")
        return None

def display_initial_menu():
    TextStyle.print_class("Information", "\n=== Welcome to Space Scavenger ===")
    TextStyle.print_class("Information", "1) New Game")
    TextStyle.print_class("Information", "2) Load Game")
    TextStyle.print_class("Information", "3) Experimental")
    TextStyle.print_class("Information", "9) Exit")
    TextStyle.print_class("Information", "==============================")

def display_experimental_menu():
    TextStyle.print_class("Information", "\n=== Experimental Menu ===")
    TextStyle.print_class("Information", "1) Create Ship")
    TextStyle.print_class("Information", "2) Generate Mission")
    TextStyle.print_class("Information", "3) Combat")
    TextStyle.print_class("Information", "0) Return to Main Menu")
    TextStyle.print_class("Information", "================")

def display_create_ship_menu():
    TextStyle.print_class("Information", "\n=== Create Ship Menu ===")
    TextStyle.print_class("Information", "1) Create Enemy NPC")
    TextStyle.print_class("Information", "2) Create Neutral NPC")
    TextStyle.print_class("Information", "3) Create Trader NPC")
    TextStyle.print_class("Information", "0) Return to Experimental Menu")
    TextStyle.print_class("Information", "================")

def display_combat_menu():
    TextStyle.print_class("Information", "\n=== Combat Menu ===")
    TextStyle.print_class("Information", "1) Create Enemy NPC")
    TextStyle.print_class("Information", "2) Initiate Combat")
    TextStyle.print_class("Information", "0) Return to Experimental Menu")
    TextStyle.print_class("Information", "================")

def experimental_menu():
    global enemy_npc, player_data
    while True:
        display_experimental_menu()
        choice = input("\nEnter your choice (0-3): ")
        
        if choice == "0":
            TextStyle.print_class("Information", "\nReturning to main menu...")
            return
        
        try:
            choice_int = int(choice)
            if choice_int < 0 or choice_int > 3:
                TextStyle.print_class("Warning", "\nInvalid choice! Please select 0-3.")
                input("Press Enter to continue...")
                continue
            
            if choice_int == 1:
                while True:
                    display_create_ship_menu()
                    sub_choice = input("\nEnter your choice (0-3): ")
                    if sub_choice == "0":
                        break
                    try:
                        sub_choice_int = int(sub_choice)
                        if sub_choice_int < 0 or sub_choice_int > 3:
                            TextStyle.print_class("Warning", "\nInvalid choice! Please select 0-3.")
                        elif sub_choice_int == 1:
                            enemy_npc = ships.create_ship(alignment="Bad")
                        elif sub_choice_int == 2:
                            ships.create_ship(alignment="Good")
                        elif sub_choice_int == 3:
                            TextStyle.print_class("Information", "\nCreating Trader NPC... (Feature under development)")
                        input("Press Enter to continue...")
                    except ValueError:
                        TextStyle.print_class("Warning", "\nInvalid input! Please enter a number.")
                        input("Press Enter to continue...")
            elif choice_int == 2:
                TextStyle.print_class("Information", "\nGenerating Mission... (Feature under development)")
                input("Press Enter to continue...")
            elif choice_int == 3:
                while True:
                    display_combat_menu()
                    sub_choice = input("\nEnter your choice (0-2): ")
                    if sub_choice == "0":
                        break
                    try:
                        sub_choice_int = int(sub_choice)
                        if sub_choice_int < 0 or sub_choice_int > 2:
                            TextStyle.print_class("Warning", "\nInvalid choice! Please select 0-2.")
                        elif sub_choice_int == 1:
                            enemy_npc = ships.create_ship(alignment="Bad")
                        elif sub_choice_int == 2:
                            if enemy_npc:
                                if "initiative_modifier" not in player_data:
                                    TextStyle.print_class("Information", "\nInitializing test player ship for combat...")
                                    player_data = ships.create_ship(alignment="Player")
                                    player_data["location"] = "Test System"
                                    player_data["universal_signature"] = 0
                                    player_data["security_zone"] = 0.6
                                combat.initiate_combat(player_data, enemy_npc)
                            else:
                                TextStyle.print_class("Warning", "\nNo Enemy Created! Please create an Enemy NPC first.")
                        input("Press Enter to continue...")
                    except ValueError:
                        TextStyle.print_class("Warning", "\nInvalid input! Please enter a number.")
                        input("Press Enter to continue...")
        except ValueError:
            TextStyle.print_class("Warning", "\nInvalid input! Please enter a number.")
            input("Press Enter to continue...")

def display_game_menu():
    TextStyle.print_class("Information", "\n=== Main Menu ===")
    TextStyle.print_class("Information", f"Location: {player_data['location']} | Energy: {player_data['energy']} | Security Zone: {player_data.get('security_zone', 1.0):.1f} | Universal Signature: {player_data['universal_signature']}")
    TextStyle.print_class("Information", "1) " + ("[System Already Explored]" if explored else "Explore System"))
    TextStyle.print_class("Information", "2) Show System")
    TextStyle.print_class("Information", "3) Show Ship Inventory")
    TextStyle.print_class("Information", "4) Scavenge")
    TextStyle.print_class("Information", "5) Fabrication")
    TextStyle.print_class("Information", "8) Travel Home")
    TextStyle.print_class("Information", "9) Save Game")
    TextStyle.print_class("Information", "0) Exit")
    TextStyle.print_class("Information", "================")

def display_home_menu():
    TextStyle.print_class("Information", "\n=== Home Menu ===")
    TextStyle.print_class("Information", f"Location: {player_data['location']} | Energy: {player_data['energy']} | Security Zone: {player_data.get('security_zone', 1.0):.1f} | Universal Signature: {player_data['universal_signature']}")
    TextStyle.print_class("Information", "1) Travel to New System")
    TextStyle.print_class("Information", "2) Show Inventory")
    TextStyle.print_class("Information", "3) Transfer Items")
    TextStyle.print_class("Information", "4) Drydock")
    TextStyle.print_class("Information", "5) Fabrication")
    TextStyle.print_class("Information", "9) Save Game")
    TextStyle.print_class("Information", "0) Exit")
    TextStyle.print_class("Information", "================")

def display_drydock_menu():
    TextStyle.print_class("Information", "\n=== Drydock Menu ===")
    TextStyle.print_class("Information", f"Hull: {player_data['hull']}/{player_data['max_hull']} | Energy: {player_data['energy']} | Shield: {player_data['shield']}/{player_data['max_shield']}")
    TextStyle.print_class("Information", "1) Repair Ship")
    TextStyle.print_class("Information", "2) Fit Components")
    TextStyle.print_class("Information", "0) Return to Home Menu")
    TextStyle.print_class("Information", "================")

def repair_ship(player_data, ship_inventory, home_inventory):
    general_data = load_general_data()
    if not general_data:
        return
    
    repair_ratios = general_data["repair_ratios"]
    
    TextStyle.print_class("Information", "\n=== Repair Menu ===")
    TextStyle.print_class("Information", f"Hull: {player_data['hull']}/{player_data['max_hull']} | Shield: {player_data['shield']}/{player_data['max_shield']} | Energy: {player_data['energy']}")
    
    if player_data["hull"] >= player_data["max_hull"] and player_data["shield"] >= player_data["max_shield"]:
        TextStyle.print_class("Information", "No repairs required.")
        input("Press Enter to continue...")
        return
    
    all_items = ship_inventory + home_inventory
    repair_items = [item for item in all_items if item["name"] in repair_ratios and item["quantity"] > 0]
    
    if not repair_items:
        TextStyle.print_class("Warning", "No items available to use for repairs!")
        input("Press Enter to continue...")
        return
    
    TextStyle.print_class("Information", "\nAvailable Items:")
    for i, item in enumerate(repair_items, 1):
        ratio_text = ""
        if "hull" in repair_ratios[item["name"]]:
            ratio_text += f"1 x {item['name']} = {repair_ratios[item['name']]['hull']} Hull"
        if "shield" in repair_ratios[item["name"]]:
            ratio_text += f"{' | ' if ratio_text else ''}1 x {item['name']} = {repair_ratios[item['name']]['shield']} Shield"
        TextStyle.print_class("Information", f"{i}) {item['name']} ({item['quantity']}) [{ratio_text}]")
    TextStyle.print_class("Information", "0) Cancel")
    
    try:
        choice = int(input(TextStyle.print_class("Information", "\nSelect an item to use for repairs (0-{}): ".format(len(repair_items)), delay_to_display=0, display_mode="instant", print_output=False)))
        if choice == 0:
            return
        
        if choice < 1 or choice > len(repair_items):
            TextStyle.print_class("Warning", "\nInvalid choice!")
            input("Press Enter to continue...")
            return
        
        item = repair_items[choice - 1]
        qty = int(input(TextStyle.print_class("Information", f"How many {item['name']} to use (1-{item['quantity']})? ", delay_to_display=0, display_mode="instant", print_output=False)))
        if qty < 1 or qty > item["quantity"]:
            TextStyle.print_class("Warning", f"\nInvalid quantity! Must be between 1 and {item['quantity']}.")
            input("Press Enter to continue...")
            return
        
        hull_repair = repair_ratios[item["name"]].get("hull", 0) * qty
        shield_repair = repair_ratios[item["name"]].get("shield", 0) * qty
        
        hull_restored = min(hull_repair, player_data["max_hull"] - player_data["hull"])
        shield_restored = min(shield_repair, player_data["max_shield"] - player_data["shield"])
        
        if hull_restored > 0:
            player_data["hull"] += hull_restored
            TextStyle.print_class("Information", f"\nRepaired {hull_restored} hull using {qty} {item['name']}.")
        if shield_restored > 0:
            player_data["shield"] += shield_restored
            TextStyle.print_class("Information", f"\nRepaired {shield_restored} shield using {qty} {item['name']}.")
        if hull_restored == 0 and shield_restored == 0:
            TextStyle.print_class("Warning", "\nNo repairs needed for this item!")
            input("Press Enter to continue...")
            return
        
        item["quantity"] -= qty
        if item["quantity"] <= 0:
            if item in ship_inventory:
                ship_inventory.remove(item)
            elif item in home_inventory:
                home_inventory.remove(item)
        
        if shield_restored > 0:
            player_data["armor_class"] = 10 + int(player_data["hull"] / 10) + int(player_data["shield"] / 10)
            TextStyle.print_class("Information", f"Armor Class updated to {player_data['armor_class']}.")
        
    except ValueError:
        TextStyle.print_class("Warning", "\nInvalid input! Please enter a number.")
    input("Press Enter to continue...")

def fit_components(player_data, ship_inventory):
    TextStyle.print_class("Information", "\n=== Fitting Menu ===")
    TextStyle.print_class("Information", f"Equipped Weapons: {', '.join([w['name'] for w in player_data['weapons']])}")
    TextStyle.print_class("Information", f"Hull: {player_data['hull']}/{player_data['max_hull']} | AC: {player_data['armor_class']}")
    
    TextStyle.print_class("Information", "\nAvailable Components:")
    components = [item for item in ship_inventory if item["name"] in ["Laser", "Plasma Cannon", "Shield Generator"]]
    if not components:
        TextStyle.print_class("Warning", "No components available to fit!")
    else:
        for i, item in enumerate(components, 1):
            TextStyle.print_class("Information", f"{i}) {item['name']} ({item['quantity']})")
    TextStyle.print_class("Information", "0) Return to Drydock Menu")
    
    try:
        choice = int(input(TextStyle.print_class("Information", "\nSelect a component to equip (0-{}): ".format(len(components)), delay_to_display=0, display_mode="instant", print_output=False)))
        if choice == 0:
            return
        
        if choice < 1 or choice > len(components):
            TextStyle.print_class("Warning", "\nInvalid choice!")
            input("Press Enter to continue...")
            return
        
        item = components[choice - 1]
        if item["name"] == "Laser":
            player_data["weapons"] = [{"name": "Laser", "damage": "d8"}]
            item["quantity"] -= 1
            if item["quantity"] <= 0:
                ship_inventory.remove(item)
            TextStyle.print_class("Information", "\nEquipped Laser (d8 damage).")
        elif item["name"] == "Plasma Cannon":
            player_data["weapons"] = [{"name": "Plasma Cannon", "damage": "2d6"}]
            item["quantity"] -= 1
            if item["quantity"] <= 0:
                ship_inventory.remove(item)
            TextStyle.print_class("Information", "\nEquipped Plasma Cannon (2d6 damage).")
        elif item["name"] == "Shield Generator":
            player_data["shield"] += 20
            player_data["max_shield"] += 20
            player_data["armor_class"] = 10 + int(player_data["hull"] / 10) + int(player_data["shield"] / 10)
            item["quantity"] -= 1
            if item["quantity"] <= 0:
                ship_inventory.remove(item)
            TextStyle.print_class("Information", "\nEquipped Shield Generator (+20 shield, updated AC).")
        
    except ValueError:
        TextStyle.print_class("Warning", "\nInvalid input! Please enter a number.")
    input("Press Enter to continue...")

def show_inventory():
    TextStyle.print_class("Information", "\n=== Inventory ===")
    TextStyle.print_class("Information", "Ship Inventory:")
    if not ship_inventory:
        TextStyle.print_class("Warning", "- Empty")
    else:
        for item in ship_inventory:
            TextStyle.print_class("Information", f"- {item['name']}: {item['quantity']}")
    TextStyle.print_class("Information", "Home Inventory:")
    if not home_inventory:
        TextStyle.print_class("Warning", "- Empty")
    else:
        for item in home_inventory:
            TextStyle.print_class("Information", f"- {item['name']}: {item['quantity']}")
    input("Press Enter to continue...")

def show_ship_inventory():
    TextStyle.print_class("Information", "\n=== Ship Inventory ===")
    if not ship_inventory:
        TextStyle.print_class("Warning", "- Empty")
    else:
        for item in ship_inventory:
            TextStyle.print_class("Information", f"- {item['name']}: {item['quantity']}")
    input("Press Enter to continue...")

def transfer_items(ship_inventory, home_inventory):
    TextStyle.print_class("Information", "\n=== Transfer Items ===")
    TextStyle.print_class("Information", "1) Transfer from Ship to Home")
    TextStyle.print_class("Information", "2) Transfer from Home to Ship")
    TextStyle.print_class("Information", "0) Return to Home Menu")
    
    choice = input("\nSelect an option (0-2): ")
    if choice == "0":
        return
    
    try:
        option = int(choice)
        if option not in [1, 2]:
            TextStyle.print_class("Warning", "\nInvalid option! Please select 0, 1, or 2.")
            input("Press Enter to continue...")
            return
        
        source = ship_inventory if option == 1 else home_inventory
        destination = home_inventory if option == 1 else ship_inventory
        source_name = "Ship" if option == 1 else "Home"
        dest_name = "Home" if option == 1 else "Ship"
        
        if not source:
            TextStyle.print_class("Warning", f"\n{source_name} Inventory is empty! Nothing to transfer.")
            input("Press Enter to continue...")
            return
        
        TextStyle.print_class("Information", f"\n{source_name} Inventory:")
        for i, item in enumerate(source, 1):
            TextStyle.print_class("Information", f"{i}) {item['name']} ({item['quantity']})")
        
        item_choice = int(input(TextStyle.print_class("Information", f"Select an item to transfer (1-{len(source)}): ", delay_to_display=0, display_mode="instant", print_output=False)))
        if item_choice < 1 or item_choice > len(source):
            TextStyle.print_class("Warning", "\nInvalid item selection!")
            input("Press Enter to continue...")
            return
        
        item = source[item_choice - 1]
        qty = int(input(TextStyle.print_class("Information", f"How many {item['name']} to transfer (1-{item['quantity']})? ", delay_to_display=0, display_mode="instant", print_output=False)))
        if qty < 1 or qty > item["quantity"]:
            TextStyle.print_class("Warning", f"\nInvalid quantity! Must be between 1 and {item['quantity']}.")
            input("Press Enter to continue...")
            return
        
        item["quantity"] -= qty
        if item["quantity"] <= 0:
            source.remove(item)
        
        found = False
        for dest_item in destination:
            if dest_item["name"] == item["name"]:
                dest_item["quantity"] += qty
                found = True
                break
        if not found:
            destination.append({"name": item["name"], "quantity": qty})
        
        TextStyle.print_class("Information", f"\nTransferred {qty} {item['name']} from {source_name} to {dest_name} Inventory.")
        
    except ValueError:
        TextStyle.print_class("Warning", "\nInvalid input! Please enter a number.")
    input("Press Enter to continue...")

def load_new_game_variables():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(script_dir, "functions", "newGameVariables.json")
    if not os.path.exists(file_path):
        TextStyle.print_class("Warning", f"\nError: 'newGameVariables.json' not found in {script_dir}/functions")
        input("Press Enter to continue...")
        return None
    try:
        with open(file_path, 'r') as file:
            return json.load(file)
    except json.JSONDecodeError:
        TextStyle.print_class("Warning", "\nError: Invalid JSON format in newGameVariables.json!")
        input("Press Enter to continue...")
        return None

def new_game():
    global ship_inventory, home_inventory, current_save_file, explored, current_system, player_data
    script_dir = os.path.dirname(os.path.abspath(__file__))
    save_dir = os.path.join(script_dir, "savedata")
    os.makedirs(save_dir, exist_ok=True)
    
    variables = load_new_game_variables()
    if not variables:
        return False
    
    TextStyle.print_class("Information", "\nSelect Difficulty:")
    TextStyle.print_class("Information", "1) Easy")
    TextStyle.print_class("Information", "2) Medium")
    TextStyle.print_class("Information", "3) Hard")
    difficulty_choice = input("Enter your choice (1-3): ")
    
    difficulty_map = {"1": "easy", "2": "medium", "3": "hard"}
    if difficulty_choice not in difficulty_map:
        TextStyle.print_class("Warning", "\nInvalid choice! Defaulting to Medium.")
        difficulty = "medium"
    else:
        difficulty = difficulty_map[difficulty_choice]
    
    while True:
        game_name = input(TextStyle.print_class("Information", "\nEnter a name for your new game: ", delay_to_display=0, display_mode="instant", print_output=False)).strip()
        if not game_name:
            TextStyle.print_class("Warning", "Game name cannot be empty!")
            continue
        
        save_file = os.path.join(save_dir, f"{game_name}.json")
        if os.path.exists(save_file):
            TextStyle.print_class("Warning", f"A game with the name '{game_name}' already exists!")
            choice = input("Enter a different name? (y/n): ").lower()
            if choice != 'y':
                return False
        else:
            ship_inventory = []
            home_inventory = variables["difficulty_levels"][difficulty]["startingHomeInventory"]
            explored = False
            current_system = {}
            player_data = ships.create_ship(alignment="Player")
            player_data["location"] = "Home"
            player_data["universal_signature"] = 0
            player_data["security_zone"] = 1.0
            game_data = {
                "player": player_data,
                "shipInventory": ship_inventory,
                "homeInventory": home_inventory,
                "explored": explored,
                "current_system": current_system,
                "game_started": "2025-02-20",
                "last_updated": "2025-02-20"
            }
            with open(save_file, 'w') as file:
                json.dump(game_data, file, indent=4)
            current_save_file = save_file
            TextStyle.print_class("Information", f"New game '{game_name}' created successfully on {difficulty.capitalize()} difficulty!")
            return True

def load_game():
    global ship_inventory, home_inventory, current_save_file, explored, current_system, player_data
    script_dir = os.path.dirname(os.path.abspath(__file__))
    save_dir = os.path.join(script_dir, "savedata")
    os.makedirs(save_dir, exist_ok=True)
    
    save_files = [f for f in os.listdir(save_dir) if f.endswith('.json')]
    if not save_files:
        TextStyle.print_class("Warning", "\nNo saved games found!")
        input("Press Enter to continue...")
        return False
    
    TextStyle.print_class("Information", "\n=== Available Save Files ===")
    for i, save_file in enumerate(save_files, 1):
        file_path = os.path.join(save_dir, save_file)
        game_data = save_game.load_game_data(file_path)
        if game_data:
            last_updated = game_data.get("last_updated", "Unknown")
            TextStyle.print_class("Information", f"{i}) {save_file[:-5]} (Last Saved: {last_updated})")
    
    choice = input("\nEnter the number of the game to load (or 0 to cancel): ")
    if choice == "0":
        return False
    
    try:
        index = int(choice) - 1
        if 0 <= index < len(save_files):
            current_save_file = os.path.join(save_dir, save_files[index])
            game_data = save_game.load_game_data(current_save_file)
            if game_data:
                ship_inventory = game_data["shipInventory"]
                home_inventory = game_data["homeInventory"]
                explored = game_data.get("explored", False)
                current_system = game_data.get("current_system", {})
                player_data = game_data["player"]
                player_data.setdefault("location", "Home")
                player_data.setdefault("energy", 100)
                player_data.setdefault("hull", 100)
                player_data.setdefault("max_hull", 100)
                player_data.setdefault("shield", 50)
                player_data.setdefault("max_shield", 50)
                player_data.setdefault("power", 100)
                player_data.setdefault("max_power", 100)
                player_data.setdefault("storage", 50)
                player_data.setdefault("max_storage", 50)
                player_data.setdefault("damage", 10)
                player_data.setdefault("level", 1)
                player_data.setdefault("ship_class", "Scout")
                player_data.setdefault("max_energy", 100)
                player_data.setdefault("universal_signature", 0)
                player_data.setdefault("security_zone", 1.0)
                player_data.setdefault("initiative_modifier", player_data.get("power", 100) // 10)
                player_data.setdefault("armor_class", 10 + (player_data.get("hull", 100) // 10) + (player_data.get("shield", 50) // 10))
                player_data.setdefault("disengage", 10)
                player_data.setdefault("weapons", [{"name": "Laser", "damage": "d8"}])
                TextStyle.print_class("Information", f"\nGame '{save_files[index][:-5]}' loaded successfully!")
                return True
            else:
                TextStyle.print_class("Warning", "\nFailed to load game data!")
                return False
        else:
            TextStyle.print_class("Warning", "\nInvalid selection!")
            return False
    except ValueError:
        TextStyle.print_class("Warning", "\nInvalid input! Please enter a number.")
        return False

def roll_percentile():
    tens = random.randint(0, 9)
    ones = random.randint(1, 9)
    roll = tens * 10 + ones
    return roll, f"[d10({tens}) + {ones}]"

def roll_dice(min_val, max_val, die_name):
    roll = random.randint(min_val + 1, max_val + 1)  # +1 to shift range for dice (e.g., 1-3 becomes 2-4)
    result = roll - 1  # Adjust back to 0-based (e.g., 2 becomes 1)
    return result, f"[{die_name}({roll}) - 1]"

def travel_home():
    global explored, player_data
    if player_data["location"] == "Home":
        TextStyle.print_class("Warning", "\nYou are already at Home!")
        input("Press Enter to continue...")
        return
    
    if player_data["energy"] >= 20:
        player_data["energy"] -= 20
        player_data["location"] = "Home"
        explored = False
        player_data["universal_signature"] = 0
        TextStyle.print_class("Information", "\nTraveled back to Home. Energy consumed: 20")
        TextStyle.print_class("Information", "Universal Signature reset to 0.")
        input("Press Enter to continue...")
    else:
        TextStyle.print_class("Warning", "\nNot enough energy to travel home! Need at least 20 energy.")
        input("Press Enter to continue...")

def travel_to_new_system():
    global player_data, explored
    max_energy = player_data["max_energy"]
    energy_available = player_data["energy"]
    
    while True:
        TextStyle.print_class("Information", f"\nCurrent Energy: {energy_available}/{max_energy}")
        TextStyle.print_class("Information", "Select Security Zone to travel to:")
        TextStyle.print_class("Information", "1) Secure Space - 10 Energy")
        TextStyle.print_class("Information", "2) Moderately Secure - 20 Energy")
        TextStyle.print_class("Information", "3) Risky - 30 Energy")
        TextStyle.print_class("Information", "4) Unsecure - 40 Energy")
        TextStyle.print_class("Information", "5) Space Classification Details")
        TextStyle.print_class("Information", "0) Cancel")
        
        choice = input("Enter your choice (0-5): ")
        
        if choice == "5":
            details = load_space_classification()
            if details:
                TextStyle.print_class("Information", "\n=== Space Classification Details ===")
                for zone, desc in details["classifications"].items():
                    TextStyle.print_class("Information", f"{zone}:")
                    TextStyle.print_class("Information", f"  {desc}")
                TextStyle.print_class("Information", "==================================")
            input("Press Enter to continue...")
            continue
        
        if choice == "0":
            return
        
        try:
            zone_map = {
                "1": {"cost": 10, "zone": 0.9, "name": "Secure Space"},
                "2": {"cost": 20, "zone": 0.6, "name": "Moderately Secure Space"},
                "3": {"cost": 30, "zone": 0.3, "name": "Risky Space"},
                "4": {"cost": 40, "zone": 0.05, "name": "Unsecure Space"}
            }
            
            if choice not in zone_map:
                TextStyle.print_class("Warning", "\nInvalid choice! Please select 0-5.")
                input("Press Enter to continue...")
                continue
            
            energy_cost = zone_map[choice]["cost"]
            security_zone = zone_map[choice]["zone"]
            zone_name = zone_map[choice]["name"]
            
            if energy_cost > energy_available:
                TextStyle.print_class("Warning", f"\nNot enough energy! Need at least {energy_cost} energy.")
                input("Press Enter to continue...")
                continue
            
            player_data["energy"] -= energy_cost
            player_data["universal_signature"] = min(player_data["universal_signature"] + energy_cost, 100)
            player_data["security_zone"] = security_zone
            explored = False
            player_data["location"] = "Unknown System"
            TextStyle.print_class("Information", f"\nTraveled to a new system in {zone_name}. Energy consumed: {energy_cost}")
            TextStyle.print_class("Information", f"Universal Signature increased to {player_data['universal_signature']}")
            
            encounter_chance = int((1 - security_zone) * player_data["universal_signature"])
            roll, roll_str = roll_percentile()
            if roll <= encounter_chance:
                TextStyle.print_class("Warning", f"Encounter Roll {roll_str} ({roll}%): Hostile ship detected! (Chance {encounter_chance}%)")
            else:
                TextStyle.print_class("Information", f"Encounter Roll {roll_str} ({roll}%): No encounter. (Chance {encounter_chance}%)")
            
            input("Press Enter to continue...")
            return
        
        except ValueError:
            TextStyle.print_class("Warning", "\nInvalid input! Please enter a number.")
            input("Press Enter to continue...")

def load_space_classification():
    json_file = "space_classification.json"
    script_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(script_dir, json_file)
    if not os.path.exists(file_path):
        TextStyle.print_class("Warning", f"\nError: '{json_file}' not found in {script_dir}")
        input("Press Enter to continue...")
        return None
    try:
        with open(file_path, 'r') as file:
            return json.load(file)
    except json.JSONDecodeError:
        TextStyle.print_class("Warning", "\nError: Invalid JSON format in space_classification.json!")
        input("Press Enter to continue...")
        return None

def scavenge_items(num_items_to_find, location_type):
    items = []
    script_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(script_dir, "items.json")
    
    try:
        with open(file_path, 'r') as file:
            all_items = json.load(file)
        
        available_items = all_items.get(location_type, [])
        if not available_items:
            return []
        
        for _ in range(num_items_to_find):
            roll, roll_str = roll_percentile()
            item_names = [item["name"] for item in available_items]
            chances = [item["chance"] for item in available_items]
            item_name = random.choices(item_names, weights=chances, k=1)[0]
            quantity = random.randint(1, 3)
            items.append((roll_str, roll, item_name, quantity))
    except Exception as e:
        TextStyle.print_class("Warning", f"Error scavenging items: {str(e)}")
    
    return items

def scavenge_location():
    locations_list = []
    for parent in current_system["children"]:
        # Add top-level objects (planets, asteroid fields)
        locations_list.append({"obj": parent, "parent": None})
        # Add child objects (e.g., Research Posts) if they exist
        if "children" in parent:
            for child in parent["children"]:
                locations_list.append({"obj": child, "parent": parent})
    
    if not locations_list:
        TextStyle.print_class("Warning", "\nNo locations available to scavenge!")
        input("Press Enter to continue...")
        return
    
    print("\nAvailable locations:")
    for i, loc in enumerate(locations_list):
        obj = loc["obj"]
        parent = loc["parent"]
        name = obj["name"]
        scavenged_text = " (scavenged)" if obj.get("scavenged", False) else ""
        display_name = f"{parent['name']} -> {name}" if parent else name
        print(f"{i}) {display_name}{scavenged_text if not scavenged_text else TextStyle.print_class('red', scavenged_text, print_output=False)} ({obj['type']})")
    
    try:
        choice = int(input("Select a location to scavenge (0-9): "))
        if 0 <= choice < len(locations_list):
            loc = locations_list[choice]
            obj = loc["obj"]
            if obj.get("scavenged", False):
                TextStyle.print_class("Warning", f"\n{obj['name']} has already been scavenged!")
                input("Press Enter to continue...")
                return
            
            location_name = obj["name"]
            location_type = "synthetic" if obj["type"] == "Man-Made" else "natural"
            
            TextStyle.print_class("Information", "- - -")
            progress = 0
            energy_cost = 0
            
            stages = [
                (0, "Plotting Coordinates", 0),
                (10, "Approaching Site", 0),
                (20, "Approaching Site", 10),
                (30, "Scanning Location", 0),
                (40, "Scanning Location", 2),
                (50, "Analysing Find", 0),
                (60, "Analysing Find", 0),
                (70, "Analysing Find", 3),
                (80, "Salvaging Item(s)", 0),
                (90, "Salvaging Item(s)", 5),
                (100, "Salvage Operation Concluded", 0)
            ]
            
            success_roll, success_roll_str = roll_percentile()
            threshold = 40
            items_found = False
            
            for percent, message, energy in stages:
                bar = "#" * (percent // 10) + " " * (10 - percent // 10)
                extra = ""
                
                if percent == 40:
                    extra = f" {success_roll_str} ({success_roll}%): {'Success' if success_roll >= threshold else 'Failure'}"
                    items_found = success_roll >= threshold
                elif percent == 70 and items_found:
                    num_items, yield_die = roll_dice(1, 3, "d3")
                    extra = f" {yield_die}: {num_items} Item(s) Found"
                
                TextStyle.print_class("Information", f"Scavenging {location_name}: [{bar}] {percent}% - {message}{extra}{' (-' + str(energy) + ' Energy)' if energy > 0 else ''}")
                time.sleep(0.3)
                
                if energy > 0 and player_data["energy"] >= energy:
                    player_data["energy"] -= energy
                    energy_cost += energy
                elif energy > 0:
                    TextStyle.print_class("Warning", f"Not enough energy! Required: {energy}, Available: {player_data['energy']}")
                    break
                
                if percent == 50 and not items_found:
                    TextStyle.print_class("Warning", "No resources found. Scavenging aborted.")
                    break
            
            TextStyle.print_class("Information", "- - -")
            
            if items_found:
                num_items, _ = roll_dice(1, 3, "d3")
                sec_roll, sec_roll_str = roll_dice(0, 1, "d2")
                TextStyle.print_class("dark-gray", f"Rolling Security Zone Modifier {sec_roll_str}: {sec_roll} Additional Items Found")
                TextStyle.print_class("Information", "- - -")
                
                total_items = num_items + sec_roll
                found_items = scavenge_items(total_items, location_type)
                
                TextStyle.print_class("Information", f"Total Energy Used: {energy_cost}")
                TextStyle.print_class("Information", f"Total Items Found: {len(found_items)}")
                for roll_str, roll, item_name, qty in found_items:
                    TextStyle.print_class("Information", f"- Item {found_items.index((roll_str, roll, item_name, qty)) + 1} {roll_str} ({roll}%): {item_name} ({qty}) Discovered")
                    for inv_item in ship_inventory:
                        if inv_item["name"] == item_name:
                            inv_item["quantity"] += qty
                            break
                    else:
                        ship_inventory.append({"name": item_name, "quantity": qty})
                obj["scavenged"] = True  # Set flag on the specific object (parent or child)
            else:
                TextStyle.print_class("Information", f"Total Energy Used: {energy_cost}")
                TextStyle.print_class("Information", "Total Items Found: 0")
            
            input("Press Enter to continue...")
    except ValueError:
        TextStyle.print_class("Warning", "Invalid choice! Please enter a number.")
        input("Press Enter to continue...")

def main_game_loop():
    global ship_inventory, home_inventory, current_save_file, explored, current_system, player_data
    while True:
        if player_data["location"] == "Home":
            display_home_menu()
            choice = input("\nEnter your choice (1-5, 9, 0): ")
            
            if choice == "1":
                travel_to_new_system()
            elif choice == "2":
                show_inventory()
            elif choice == "3":
                transfer_items(ship_inventory, home_inventory)
            elif choice == "4":
                while True:
                    display_drydock_menu()
                    sub_choice = input("\nEnter your choice (0-2): ")
                    if sub_choice == "0":
                        break
                    elif sub_choice == "1":
                        repair_ship(player_data, ship_inventory, home_inventory)
                    elif sub_choice == "2":
                        fit_components(player_data, ship_inventory)
                    else:
                        TextStyle.print_class("Warning", "\nInvalid choice! Please select 0-2.")
                        input("Press Enter to continue...")
            elif choice == "5":
                fabrication.fabrication.fabrication_menu(player_data, ship_inventory)
            elif choice == "9":
                if current_save_file:
                    save_game.save_game(ship_inventory, home_inventory, current_save_file, explored, current_system, player_data)
                else:
                    TextStyle.print_class("Warning", "\nNo game file selected to save to!")
                    input("Press Enter to continue...")
            elif choice == "0":
                TextStyle.print_class("Information", "\nReturning to main menu...")
                return
            else:
                TextStyle.print_class("Warning", "\nInvalid choice! Please select 1-5, 9, or 0.")
                input("Press Enter to continue...")
        
        else:
            display_game_menu()
            choice = input("\nEnter your choice (1, 2, 3, 4, 5, 8, 9, 0): ")
            
            if choice == "1":
                player_data, current_system, explored = systems.systems.explore_system(player_data, current_system, explored)
            elif choice == "2":
                systems.systems.show_system(current_system, explored)
                input("Press Enter to continue...")
            elif choice == "3":
                show_ship_inventory()
            elif choice == "4":
                scavenge_location()
            elif choice == "5":
                fabrication.fabrication.fabrication_menu(player_data, ship_inventory)
            elif choice == "8":
                travel_home()
            elif choice == "9":
                if current_save_file:
                    save_game.save_game(ship_inventory, home_inventory, current_save_file, explored, current_system, player_data)
                else:
                    TextStyle.print_class("Warning", "\nNo game file selected to save to!")
                    input("Press Enter to continue...")
            elif choice == "0":
                TextStyle.print_class("Information", "\nReturning to main menu...")
                return
            else:
                TextStyle.print_class("Warning", "\nInvalid choice! Please select 1, 2, 3, 4, 5, 8, 9, or 0.")
                input("Press Enter to continue...")

def main():
    global current_save_file
    while True:
        display_initial_menu()
        choice = input("\nEnter your choice (1-3, 9): ")
        
        if choice == "1":
            if new_game():
                main_game_loop()
        elif choice == "2":
            if load_game():
                main_game_loop()
        elif choice == "3":
            experimental_menu()
        elif choice == "9":
            TextStyle.print_class("Information", "\nGoodbye!")
            break
        else:
            TextStyle.print_class("Warning", "\nInvalid choice! Please select 1-3, or 9.")
            input("Press Enter to continue...")

if __name__ == "__main__":
    main()
