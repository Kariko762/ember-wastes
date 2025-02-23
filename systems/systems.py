# systems/systems.py
import json
import random
import os
import systems.systemsCreatePlanet as create_planet
import systems.systemsCreateAsteroids as create_asteroids
import systems.systemsCreateAnomalies as create_anomalies

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
            "light_gray": "\033[37m"
        }
        ansi = color_map.get(style.get("color", "white"), "\033[97m")
        if style.get("bold"):
            ansi += "\033[1m"
        if style.get("italic"):
            ansi += "\033[3m"
        return f"{ansi}{text}\033[0m"

TextStyle.load_styles()

def load_system_data():
    json_file = "systems.json"
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
        print(TextStyle.print_class("Warning", "\nError: Invalid JSON format in systems.json!"))
        input("Press Enter to continue...")
        return None

def roll_d10_tens():
    return random.randint(0, 9) * 10

def roll_d10_ones():
    return random.randint(1, 9)

def roll_percentile():
    tens = roll_d10_tens()
    ones = roll_d10_ones()
    return tens + ones, f"[d10({tens//10})+{ones}]"

def roll_dice(min_val, max_val, die_name):
    roll = random.randint(min_val, max_val)
    return roll, f"[{die_name}({roll})]"

def weighted_roll(options, chance_key, label, chance_boost=1.0):
    roll, roll_str = roll_percentile()
    cumulative = 0
    adjusted_options = []
    for opt in options:
        adjusted_chance = min(opt[chance_key] * chance_boost, 0.9)
        adjusted_options.append({"name": opt["name"], "chance": adjusted_chance})
    for option in adjusted_options:
        cumulative += int(option["chance"] * 100)
        if roll <= cumulative:
            return option["name"], roll, roll_str
    return adjusted_options[-1]["name"], roll, roll_str

def explore_system(player_data, current_system, explored):
    if explored:
        print(TextStyle.print_class("Warning", "\nThis system has already been explored! Travel home to reset."))
        input("Press Enter to continue...")
        return player_data, current_system, explored
    
    system_data = load_system_data()
    if not system_data:
        return player_data, current_system, explored
    
    system_vars = system_data["systemVariables"]
    security_zone = player_data["security_zone"]
    zone_key = "Secure Space" if security_zone >= 0.9 else \
               "Moderately Secure Space" if security_zone >= 0.6 else \
               "Risky Space" if security_zone >= 0.3 else "Unsecure Space"
    security_rewards = system_data["securityRewards"][zone_key]
    # Pass both security_zone and securityRewards data
    zone_data = {"security_zone": security_zone, **security_rewards}
    
    current_system = {"star": None, "children": []}
    
    print(TextStyle.print_class("Information", "\nExploring New System"))
    print(TextStyle.print_class("Information", "================"))
    
    # Layer 1: Star
    stars = system_data["celestial_objects"]["stars"]
    star_name, roll, roll_str = weighted_roll(stars, "chance", "Star Type", zone_data["chanceBoost"])
    current_system["star"] = star_name
    print(TextStyle.print_class("RNG", f"Scanning Star {roll_str} ({roll}%): {star_name} Discovered"))
    
    # Layer 2: Planets (Base Roll)
    planet_roll, die_name = roll_dice(system_vars["planetCount"]["min"], system_vars["planetCount"]["max"], "d5")
    num_planets = planet_roll
    if num_planets > 0:
        print(TextStyle.print_class("RNG", f"Searching for Planets {die_name}: {num_planets} Planets Identified."))
    else:
        print(TextStyle.print_class("RNG", f"Searching for Planets {die_name}: No Planets Identified."))
    
    for i in range(num_planets):
        planet = create_planet.create_planet(i + 1, system_data, zone_data["chanceBoost"])
        current_system["children"].append(planet)
    
    # Planets (Security Modifier Roll)
    extra_planet_roll, extra_die = roll_dice(zone_data["extraPlanet"]["min"], zone_data["extraPlanet"]["max"], "dX")
    extra_planets = extra_planet_roll
    if extra_planets > 0:
        print(TextStyle.print_class("RNG", f"Security Zone Extra Planets {extra_die}: {extra_planets} Additional Planets Found"))
        for i in range(num_planets, num_planets + extra_planets):
            planet = create_planet.create_planet(i + 1, system_data, zone_data["chanceBoost"])
            current_system["children"].append(planet)
    
    # Layer 3: Asteroid Fields
    asteroids = create_asteroids.create_asteroids(system_data, zone_data)
    current_system["children"].extend(asteroids)
    
    # Layer 4: Anomalies (Unknown Objects)
    anomalies = create_anomalies.create_anomalies(system_data, zone_data)
    current_system["children"].extend(anomalies)
    
    print(TextStyle.print_class("Information", "================"))
    print(TextStyle.print_class("Information", "\nSystem Information"))
    print(TextStyle.print_class("Information", "================"))
    show_system(current_system, True)
    print(TextStyle.print_class("Information", "================"))
    
    explored = True
    player_data["location"] = f"{current_system['star']} System"
    return player_data, current_system, explored

def print_system(current_system):
    print(TextStyle.print_class("Information", f"- {current_system['star']}"))
    for obj in current_system["children"]:
        if obj["type"] == "Planet":
            print(TextStyle.print_class("Information", f"- - {obj['name']} ({obj['type']})"))
            for child in obj["children"]:
                if "wreckage" in child:
                    print(TextStyle.print_class("Information", f"- - - {child['name']} ({child['type']}, {child['wreckage']} wrecks)"))
                else:
                    print(TextStyle.print_class("Information", f"- - - {child['name']} ({child['type']})"))
        elif "wreckage" in obj:
            print(TextStyle.print_class("Information", f"- - {obj['name']} ({obj['type']}, {obj['wreckage']} wrecks)"))
        else:
            print(TextStyle.print_class("Information", f"- - {obj['name']} ({obj['type']})"))

def show_system(current_system, explored):
    if not current_system or not explored:
        print(TextStyle.print_class("Warning", "\nNo system explored yet! Use 'Explore System' first."))
    else:
        print(TextStyle.print_class("Information", f"Current System: {current_system['star']} System"))
        print_system(current_system)

if __name__ == "__main__":
    test_player = {"location": "Home", "energy": 100, "security_zone": 1.0, "universal_signature": 0}
    test_system = {}
    test_explored = False
    test_player, test_system, test_explored = explore_system(test_player, test_system, test_explored)