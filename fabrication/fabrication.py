# fabrication/fabrication.py
import json
import os
import random

def load_fabrication_data():
    json_file = "fabrication.json"
    script_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(script_dir, json_file)
    if not os.path.exists(file_path):
        print(f"\nError: '{json_file}' not found in {script_dir}")
        input("Press Enter to continue...")
        return None
    try:
        with open(file_path, 'r') as file:
            return json.load(file)
    except json.JSONDecodeError:
        print("\nError: Invalid JSON format in fabrication.json!")
        input("Press Enter to continue...")
        return None

def roll_percentile():
    tens = random.randint(0, 9) * 10
    ones = random.randint(1, 9)
    return tens + ones, f"[d10({tens//10})+{ones}]"

def fabrication_menu(player_data, ship_inventory):
    fab_data = load_fabrication_data()
    if not fab_data:
        return
    
    print("\n=== Fabrication Menu ===")
    print(f"Current Ship Energy: {player_data['energy']}/{player_data['max_energy']}")
    
    energy_cells = next((item["quantity"] for item in ship_inventory if item["name"] == "Energy Cells"), 0)
    power_cells = next((item["quantity"] for item in ship_inventory if item["name"] == "Power Cells"), 0)
    
    print(f"1) Convert Energy Cells ({energy_cells} available)")
    print(f"2) Convert Power Cells ({power_cells} available)")
    print("0) Return to Main Menu")
    
    choice = input("\nSelect an option (0-2): ")
    if choice == "0":
        return
    
    try:
        option = int(choice)
        if option not in [1, 2]:
            print("\nInvalid option! Please select 0, 1, or 2.")
            input("Press Enter to continue...")
            return
        
        item_type = "energyCells" if option == 1 else "powerCells"
        item_name = "Energy Cells" if option == 1 else "Power Cells"
        available = energy_cells if option == 1 else power_cells
        
        if available == 0:
            print(f"\nNo {item_name} available to convert!")
            input("Press Enter to continue...")
            return
        
        print(f"\nConverting {item_name}:")
        print(f"Available: {available}")
        qty = int(input(f"How many {item_name} to convert (1-{available})? "))
        if qty < 1 or qty > available:
            print(f"\nInvalid quantity! Must be between 1 and {available}.")
            input("Press Enter to continue...")
            return
        
        ratio = fab_data["fabricationVariables"][item_type]["conversionRatio"]
        success_chance = fab_data["fabricationVariables"][item_type]["successChance"]
        total_energy = 0
        
        for item in ship_inventory:
            if item["name"] == item_name:
                for _ in range(qty):
                    roll, roll_str = roll_percentile()
                    if roll > success_chance:
                        energy_gained = ratio
                        total_energy += energy_gained
                        print(f"Converting {item_name} {roll_str} ({roll}%): Success (+{energy_gained} Energy)")
                    else:
                        print(f"Converting {item_name} {roll_str} ({roll}%): Failed (Threshold {success_chance}%)")
                item["quantity"] -= qty
                if item["quantity"] <= 0:
                    ship_inventory.remove(item)
                break
        
        if total_energy > 0:
            new_energy = min(player_data["energy"] + total_energy, player_data["max_energy"])
            player_data["energy"] = new_energy
            print(f"Total Energy Gained: {total_energy}")
            print(f"New Ship Energy: {player_data['energy']}/{player_data['max_energy']}")
        else:
            print("No energy gained from conversion.")
        
    except ValueError:
        print("\nInvalid input! Please enter a number.")
    input("Press Enter to continue...")