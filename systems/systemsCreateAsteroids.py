# systems/systemsCreateAsteroids.py
import json
import os
import random
import main  # Use TextStyle from main

def roll_percentile():
    tens = random.randint(0, 9) * 10
    ones = random.randint(1, 9)
    roll = tens + ones
    return roll, f"[d10({tens//10})+{ones}]"

def roll_dice(min_val, max_val, die_name):
    roll = random.randint(min_val, max_val)
    return roll, f"[{die_name}({roll})]"

def load_systems_data():
    json_file = "systems.json"
    script_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(script_dir, json_file)
    if not os.path.exists(file_path):
        main.TextStyle.print_class("Warning", f"\nError: '{json_file}' not found at {file_path}")
        return None
    try:
        with open(file_path, 'r') as file:
            return json.load(file)
    except json.JSONDecodeError:
        main.TextStyle.print_class("Warning", f"\nError: Invalid JSON format in {json_file}")
        return None

def create_asteroids(system_data, zone_data):
    systems_data = load_systems_data()
    if not systems_data:
        return []
    
    vars = systems_data["systemVariables"]
    asteroid_chance = vars.get("asteroidChance", 90)  # Fallback to 90 if missing
    asteroids = []
    
    roll, roll_str = roll_percentile()
    if roll > asteroid_chance:
        num_asteroids, asteroid_die = roll_dice(vars.get("asteroidCount", {"min": 1, "max": 3})["min"], 
                                                vars.get("asteroidCount", {"min": 1, "max": 3})["max"], "d5")
        main.TextStyle.print_class("Information", f"Scanning Asteroid Density {roll_str} ({roll}%): Asteroid Fields Detected ({num_asteroids})")
    else:
        num_asteroids = 0
        main.TextStyle.print_class("Information", f"Scanning Asteroid Density {roll_str} ({roll}%): No Asteroid Fields Detected")
    
    # Security Zone Modifier roll
    extra_asteroids = 0
    security_zone = zone_data.get("security_zone", 1.0)  # Fallback to 1.0 if missing
    if security_zone < 0.9:
        if security_zone >= 0.6:  # Moderately Secure
            extra_roll, extra_die = roll_dice(1, 2, "d2")
            extra_asteroids = extra_roll - 1  # 0-1
            die_label = "d2"
        elif security_zone >= 0.3:  # Risky
            extra_roll, extra_die = roll_dice(1, 3, "d3")
            extra_asteroids = extra_roll - 1  # 0-2
            die_label = "d3"
        else:  # Unsecure
            extra_roll, extra_die = roll_dice(1, 4, "d4")
            extra_asteroids = extra_roll - 1  # 0-3
            die_label = "d4"
        
        main.TextStyle.print_class("Information", f"Security Zone Extra Asteroids [{die_label}({extra_roll})]: {extra_asteroids} Additional Asteroid Fields Found")
    
    # Generate asteroid fields
    for i in range(num_asteroids + extra_asteroids):
        asteroid_name = f"Asteroid Field {system_data['system_id']}-{i+1}"
        asteroids.append({
            "name": asteroid_name,
            "type": "Asteroid Field",
            "resources": []
        })
        main.TextStyle.print_class("Information", f"- {asteroid_name} Located")
    
    return asteroids

if __name__ == "__main__":
    system_data = {"system_id": "X1"}
    zone_data = {"security_zone": 0.05}  # Unsecure for testing
    asteroids = create_asteroids(system_data, zone_data)
    print(asteroids)