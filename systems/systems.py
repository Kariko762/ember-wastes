# systems/systems.py
import json
import random
import os
import main
import systems.systemsCreateAsteroids

def load_system_data():
    json_file = "systems.json"
    script_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(script_dir, json_file)
    
    if not os.path.exists(file_path):
        main.TextStyle.print_class("Warning", f"\nError: '{json_file}' not found in {script_dir}")
        input("Press Enter to continue...")
        return None
    
    try:
        with open(file_path, 'r') as file:
            return json.load(file)
    except json.JSONDecodeError:
        main.TextStyle.print_class("Warning", f"\nError: Invalid JSON format in systems.json!")
        input("Press Enter to continue...")
        return None
    except Exception as e:
        main.TextStyle.print_class("Warning", f"\nAn error occurred: {str(e)}")
        input("Press Enter to continue...")
        return None

def roll_percentile():
    tens = random.randint(0, 9)
    ones = random.randint(1, 9)
    roll = tens * 10 + ones
    return roll, f"[d10({tens}) + {ones}]"

def roll_dice(min_val, max_val, die_name):
    roll = random.randint(min_val + 1, max_val + 1)  # +1 for dice range
    result = roll - 1  # Adjust for 0-based counting
    return result, f"[{die_name}({roll}) - 1]"

def create_system():
    system_data = load_system_data()
    if not system_data:
        return None
    
    system_id = f"X{random.randint(1000, 9999)}"
    current_system = {
        "star": None,
        "system_id": system_id,
        "children": []
    }
    
    stars = system_data["celestial_objects"]["stars"]
    star_names = [s["name"] for s in stars]
    star_chances = [s["chance"] for s in stars]
    roll, roll_str = roll_percentile()
    star = random.choices(star_names, weights=star_chances, k=1)[0]
    current_system["star"] = star
    main.TextStyle.print_class("dark-gray", f"Scanning for Star Type {roll_str} ({roll}%): {star} detected")
    
    return current_system

def create_planets(system_data, star_data):
    planets_info = system_data["celestial_objects"]["planets"]
    moons_info = system_data["celestial_objects"]["moons"]
    man_made_info = system_data["man_made_objects"]
    vars = system_data["systemVariables"]
    
    planets = []
    num_planets, planet_die = roll_dice(vars["planetCount"]["min"], vars["planetCount"]["max"], "d5")
    main.TextStyle.print_class("dark-gray", f"Searching for Planets {planet_die}: {num_planets} Detected")
    main.TextStyle.print_class("dark-gray", "= = =")
    
    planet_names = [p["name"] for p in planets_info]
    planet_chances = [p["chance"] for p in planets_info]
    moon_names = [m["name"] for m in moons_info]
    moon_chances = [m["chance"] for m in moons_info]
    man_made_types = {m["name"]: m["chance"] for m in man_made_info}
    
    for i in range(num_planets):
        roll, roll_str = roll_percentile()
        planet = random.choices(planet_names, weights=planet_chances, k=1)[0]
        planet_obj = {"type": "Planet", "name": f"{planet} {star_data['system_id']}", "children": []}
        main.TextStyle.print_class("dark-gray", f"Scanning Planet {roll_str} ({roll}%): {planet_obj['name']} Identified")
        main.TextStyle.print_class("dark-gray", f"- Surveying {planet_obj['name']}:")
        
        # Moons
        moon_roll, moon_roll_str = roll_percentile()
        if moon_roll <= vars["moonChance"] * 100:
            num_moons, moon_die = roll_dice(vars["moonCount"]["min"], vars["moonCount"]["max"], "d5")
            main.TextStyle.print_class("dark-gray", f"- - Searching for Moons {moon_roll_str} ({moon_roll}%): {num_moons} Detected")
            for j in range(num_moons):
                moon = random.choices(moon_names, weights=moon_chances, k=1)[0]
                moon_obj = {"type": "Moon", "name": f"{moon} of {planet_obj['name']}"}
                planet_obj["children"].append(moon_obj)
                main.TextStyle.print_class("dark-gray", f"- - - {moon_obj['name']} Located")
        else:
            main.TextStyle.print_class("dark-gray", f"- - Searching for Moons {moon_roll_str} ({moon_roll}%): No Moons Detected")
        
        # Man-Made Objects
        main.TextStyle.print_class("dark-gray", "- Surveying for Signs of Life:")
        for man_made_name, chance in man_made_types.items():
            roll, roll_str = roll_percentile()
            if roll <= chance * 100:
                man_made_obj = {"type": "Man-Made", "name": f"{man_made_name} {random.randint(vars['objectIdRange']['min'], vars['objectIdRange']['max'])}"}
                planet_obj["children"].append(man_made_obj)
                main.TextStyle.print_class("dark-gray", f"- - Searching of {man_made_name}s {roll_str} ({roll}%): {man_made_obj['name']} Detected")
            else:
                main.TextStyle.print_class("dark-gray", f"- - Searching of {man_made_name}s {roll_str} ({roll}%): No {man_made_name}s Detected")
        
        planets.append(planet_obj)
        main.TextStyle.print_class("dark-gray", "= = =")
    
    return planets

def explore_system(player_data, current_system, explored):
    if explored:
        main.TextStyle.print_class("Warning", "\nThis system has already been explored! Travel home to reset.")
        input("Press Enter to continue...")
        return player_data, current_system, explored
    
    system_data = load_system_data()
    if not system_data:
        return player_data, current_system, explored
    
    # 1. Star
    current_system = create_system()
    if not current_system:
        return player_data, current_system, explored
    
    # 2. Planets (including Moons and Man-Made Objects)
    planets = create_planets(system_data, current_system)
    current_system["children"].extend(planets)
    
    # 3. Asteroid Fields
    security_zone = 0.5  # Hardcoded for now
    zone_data = {"security_zone": security_zone, "system_id": current_system["system_id"]}
    asteroid_data = systems.systemsCreateAsteroids.create_asteroids(system_data, zone_data)
    asteroids = asteroid_data["asteroids"]
    asteroid_messages = asteroid_data["messages"]
    current_system["children"].extend(asteroids)
    
    # 4. Unknown Objects
    main.TextStyle.print_class("dark-gray", "= = =")
    unknown = system_data["unknown_objects"]
    unknown_types = {u["name"]: u["chance"] for u in unknown}
    for unknown_name, chance in unknown_types.items():
        roll, roll_str = roll_percentile()
        if roll <= chance * 100:
            event_obj = {"type": "Unknown", "name": f"{unknown_name} {random.randint(system_data['systemVariables']['objectIdRange']['min'], system_data['systemVariables']['objectIdRange']['max'])}"}
            for u in unknown:
                if u["name"] == unknown_name and "wreckage" in u:
                    event_obj["wreckage"] = u["wreckage"]
            current_system["children"].append(event_obj)
            main.TextStyle.print_class("dark-gray", f"Scanning for Anomalies ({unknown_name}s) {roll_str} ({roll}%): {event_obj['name']} Detected")
        else:
            main.TextStyle.print_class("dark-gray", f"Scanning for Anomalies ({unknown_name}s) {roll_str} ({roll}%): No {unknown_name}s Found")
    main.TextStyle.print_class("dark-gray", "= = =")
    
    # Print creation logs
    for msg in asteroid_messages:
        main.TextStyle.print_class("dark-gray", msg)
    
    # System summary
    explored = True
    player_data["location"] = f"{current_system['star']} System"
    main.TextStyle.print_class("Success", f"\nExplored new system: {current_system['star']} System (ID: {current_system['system_id']})")
    print_system(current_system)
    input("Press Enter to continue...")
    
    return player_data, current_system, explored

def print_system(current_system):
    main.TextStyle.print_class("Information", f"- {current_system['star']} (ID: {current_system['system_id']})")
    
    for obj in current_system["children"]:
        if obj["type"] == "Planet":
            main.TextStyle.print_class("Information", f"- - {obj['name']} ({obj['type']})")
            for child in obj["children"]:
                if "wreckage" in child:
                    main.TextStyle.print_class("Information", f"- - - {child['name']} ({child['type']}, {child['wreckage']} wrecks)")
                else:
                    main.TextStyle.print_class("Information", f"- - - {child['name']} ({child['type']})")
    
    for obj in current_system["children"]:
        if obj["type"] == "Asteroid Field":
            main.TextStyle.print_class("Information", f"- - {obj['name']} ({obj['type']})")
    
    for obj in current_system["children"]:
        if obj["type"] == "Unknown":
            if "wreckage" in obj:
                main.TextStyle.print_class("Information", f"- - {obj['name']} ({obj['type']}, {obj['wreckage']} wrecks)")
            else:
                main.TextStyle.print_class("Information", f"- - {obj['name']} ({obj['type']})")

def show_system(current_system, explored):
    if not current_system or not explored:
        main.TextStyle.print_class("Warning", "\nNo system explored yet! Use 'Explore System' first.")
    else:
        main.TextStyle.print_class("Success", f"\nCurrent System: {current_system['star']} System (ID: {current_system['system_id']})")
        print_system(current_system)
    input("Press Enter to continue...")

if __name__ == "__main__":
    test_player = {"location": "Home", "energy": 100}
    test_system = {}
    test_explored = False
    test_player, test_system, test_explored = explore_system(test_player, test_system, test_explored)
    show_system(test_system, test_explored)
