# systems/systems.py
import json
import random
import os
import main
import systems.systemsCreateAsteroids  # Correct import for package structure

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
        main.TextStyle.print_class("Warning", "\nError: Invalid JSON format in systems.json!")
        input("Press Enter to continue...")
        return None
    except Exception as e:
        main.TextStyle.print_class("Warning", f"\nAn error occurred: {str(e)}")
        input("Press Enter to continue...")
        return None

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
    planets_info = system_data["celestial_objects"]["planets"]
    moons_info = system_data["celestial_objects"]["moons"]
    object_id_range = system_data["systemVariables"]["objectIdRange"]
    
    star_names = [s["name"] for s in stars]
    star_chances = [s["chance"] for s in stars]
    current_system["star"] = random.choices(star_names, weights=star_chances, k=1)[0]
    
    return current_system

def create_planets(system_data, star_data):
    planets_info = system_data["celestial_objects"]["planets"]
    moons_info = system_data["celestial_objects"]["moons"]
    man_made_info = system_data["man_made_objects"]
    
    planets = []
    num_planets = random.randint(
        system_data["systemVariables"]["planetCount"]["min"],
        system_data["systemVariables"]["planetCount"]["max"]
    )
    
    planet_names = [p["name"] for p in planets_info]
    planet_chances = [p["chance"] for p in planets_info]
    moon_names = [m["name"] for m in moons_info]
    moon_chances = [m["chance"] for m in moons_info]
    man_made_names = [m["name"] for m in man_made_info]
    man_made_chances = [m["chance"] for m in man_made_info]
    
    for i in range(num_planets):
        planet = random.choices(planet_names, weights=planet_chances, k=1)[0]
        planet_obj = {"type": "Planet", "name": f"{planet} {i+1}", "children": []}
        
        if random.random() < 0.5:
            num_moons = random.randint(
                system_data["systemVariables"]["moonCount"]["min"],
                system_data["systemVariables"]["moonCount"]["max"]
            )
            for j in range(num_moons):
                moon = random.choices(moon_names, weights=moon_chances, k=1)[0]
                planet_obj["children"].append({"type": "Moon", "name": f"{moon} of {planet_obj['name']}"})
        
        for obj in man_made_info:
            if random.random() < obj["chance"]:
                planet_obj["children"].append({"type": "Man-Made", "name": f"{obj['name']} {random.randint(1, 100)}"})
        
        planets.append(planet_obj)
    
    return planets

def explore_system(player_data, current_system, explored):
    if explored:
        main.TextStyle.print_class("Warning", "\nThis system has already been explored! Travel home to reset.")
        input("Press Enter to continue...")
        return player_data, current_system, explored
    
    system_data = load_system_data()
    if not system_data:
        return player_data, current_system, explored
    
    current_system = create_system()
    if not current_system:
        return player_data, current_system, explored
    
    planets = create_planets(system_data, current_system)
    current_system["children"].extend(planets)
    
    # Asteroid Fields
    zone_data = {"security_zone": 0.5, "system_id": current_system["system_id"]}  # Pass system_id
    asteroids = systems.systemsCreateAsteroids.create_asteroids(system_data, zone_data)
    current_system["children"].extend(asteroids)
    
    # Unknown Objects
    unknown = system_data["unknown_objects"]
    unknown_names = [u["name"] for u in unknown]
    unknown_chances = [u["chance"] for u in unknown]
    for obj in unknown:
        if random.random() < obj["chance"]:
            event_obj = {"type": "Unknown", "name": f"{obj['name']} {random.randint(1, 100)}"}
            if "wreckage" in obj:
                event_obj["wreckage"] = obj["wreckage"]
            current_system["children"].append(event_obj)
    
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
        elif "wreckage" in obj:
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
