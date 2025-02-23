# systems/systemsCreateAsteroids.py
import json
import os
import random
import main

def roll_percentile():
    tens = random.randint(0, 9)
    ones = random.randint(1, 9)
    roll = tens * 10 + ones
    return roll, f"[d10({tens}) + {ones}]"

def roll_dice(min_val, max_val, die_name):
    roll = random.randint(min_val + 1, max_val + 1)  # +1 for dice range
    result = roll - 1  # Adjust for 0-based counting
    return result, f"[{die_name}({roll}) - 1]"

def load_systems_data():
    json_file = "systems.json"
    script_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(script_dir, json_file)
    if not os.path.exists(file_path):
        return None
    try:
        with open(file_path, 'r') as file:
            return json.load(file)
    except json.JSONDecodeError:
        return None

def create_asteroids(system_data, zone_data):
    systems_data = load_systems_data()
    if not systems_data:
        return {"asteroids": [], "messages": []}
    
    system_id = zone_data.get("system_id", "X0000")
    vars = systems_data["systemVariables"]
    asteroid_fields = systems_data["asteroid_fields"]["types"]
    security_zone = zone_data.get("security_zone", 1.0)
    messages = []
    asteroids = []
    
    # Base asteroid detection
    roll, roll_str = roll_percentile()
    if roll <= vars["asteroidChance"]:
        type_names = [t["name"] for t in asteroid_fields]
        type_chances = [t["chance"] for t in asteroid_fields]
        asteroid_type = random.choices(type_names, weights=type_chances, k=1)[0]
        messages.append(f"Searching for Asteroid Fields {roll_str} ({roll}%): Asteroid Fields Detected")
        for t in asteroid_fields:
            if t["name"] == asteroid_type:
                num_asteroids, asteroid_die = roll_dice(t["min_objects"], t["max_objects"], "d5")
                messages.append(f"- Surveying Asteroid Fields {asteroid_die}: {num_asteroids} {asteroid_type} Asteroid Fields Identified")
                break
    else:
        num_asteroids = 0
        messages.append(f"Searching for Asteroid Fields {roll_str} ({roll}%): No Asteroid Fields Detected")
    
    # Security zone extra asteroids
    extra_asteroids = 0
    security_rewards = systems_data["securityRewards"]
    if security_zone < 0.9:
        if security_zone >= 0.6:
            key = "Moderately Secure Space"
            die = "d2"
        elif security_zone >= 0.3:
            key = "Risky Space"
            die = "d3"
        else:
            key = "Unsecure Space"
            die = "d4"
        extra_roll, extra_die = roll_dice(security_rewards[key]["extraAsteroidField"]["min"], 
                                          security_rewards[key]["extraAsteroidField"]["max"], die)
        extra_asteroids = extra_roll
        messages.append(f"Security Zone Extra Asteroids Roll {extra_die}: {extra_asteroids} Additional Asteroid Fields Found")
    
    for i in range(num_asteroids + extra_asteroids):
        asteroid_name = f"Asteroid Field {system_id}-{i+1}"
        asteroids.append({
            "name": asteroid_name,
            "type": "Asteroid Field",
            "resources": []
        })
        messages.append(f"- - {asteroid_name} Located")
    
    return {"asteroids": asteroids, "messages": messages}

if __name__ == "__main__":
    system_data = {}
    zone_data = {"security_zone": 0.05, "system_id": "X1234"}
    result = create_asteroids(system_data, zone_data)
    for msg in result["messages"]:
        print(msg)
    print(result["asteroids"])
