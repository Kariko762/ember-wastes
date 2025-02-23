# save_game.py
import json
import os

def save_game(ship_inventory, home_inventory, save_file, explored, current_system, player_data):
    try:
        existing_data = load_game_data(save_file)
        if existing_data:
            game_data = existing_data
        else:
            game_data = {}
        
        game_data.update({
            "player": player_data,
            "shipInventory": ship_inventory,
            "homeInventory": home_inventory,
            "explored": explored,
            "current_system": current_system,
            "game_started": game_data.get("game_started", "2025-02-20"),
            "last_updated": "2025-02-20"
        })
        
        os.makedirs(os.path.dirname(save_file), exist_ok=True)
        
        with open(save_file, 'w') as file:
            json.dump(game_data, file, indent=4)
        
        print("\nGame saved successfully!")
        if ship_inventory or home_inventory:
            ship_items = ', '.join(f'{item["name"]} ({item["quantity"]})' for item in ship_inventory) if ship_inventory else "Empty"
            home_items = ', '.join(f'{item["name"]} ({item["quantity"]})' for item in home_inventory) if home_inventory else "Empty"
            print(f"Ship Inventory saved: {ship_items}")
            print(f"Home Inventory saved: {home_items}")
        else:
            print("Both inventories saved: Empty")
        print(f"Universal Signature saved: {player_data['universal_signature']}")

    except Exception as e:
        print(f"\nError saving game: {str(e)}")
    
    input("Press Enter to continue...")

def load_game_data(save_file):
    try:
        if os.path.exists(save_file):
            with open(save_file, 'r') as file:
                return json.load(file)
        return None
    except json.JSONDecodeError:
        print("\nError: Corrupted save file detected!")
        return None
    except Exception as e:
        print(f"\nError loading game data: {str(e)}")
        return None

if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    save_dir = os.path.join(script_dir, "savedata")
    os.makedirs(save_dir, exist_ok=True)
    sample_ship_inventory = [{"name": "Iron Ore", "quantity": 2}]
    sample_home_inventory = [{"name": "Water", "quantity": 10}]
    sample_explored = True
    sample_system = {"star": "Red Dwarf", "children": [{"type": "Planet", "name": "Planet 42", "children": [], "scavenged": False}]}
    sample_player = {
        "location": "Home", 
        "energy": 80, 
        "hull": 100, 
        "max_hull": 100, 
        "shield": 50, 
        "max_shield": 50, 
        "power": 100, 
        "max_power": 100, 
        "storage": 50, 
        "max_storage": 50, 
        "damage": 10, 
        "level": 1, 
        "ship_class": "Scout",
        "universal_signature": 30,
        "security_zone": 0.6
    }
    save_game(sample_ship_inventory, sample_home_inventory, os.path.join(save_dir, "test_game.json"), 
              sample_explored, sample_system, sample_player)