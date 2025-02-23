# systems/systemsCreatePlanet.py
import random
import os
import json

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

def roll_dice(min_val, max_val, die_name):
    roll = random.randint(min_val, max_val)
    return roll, f"[{die_name}({roll})]"

def roll_percentile():
    tens = random.randint(0, 9) * 10
    ones = random.randint(1, 9)
    return tens + ones, f"[d10({tens//10})+{ones}]"

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

def create_planet(planet_num, system_data, chance_boost):
    planets = system_data["celestial_objects"]["planets"]
    moons = system_data["celestial_objects"]["moons"]
    man_made = system_data["man_made_objects"]
    system_vars = system_data["systemVariables"]
    
    planet_type, roll, roll_str = weighted_roll(planets, "chance", f"Planet {planet_num} Type", chance_boost)
    planet_obj = {"type": "Planet", "name": f"{planet_type} {planet_num}", "children": [], "scavenged": False}
    print(TextStyle.print_class("RNG", f"- Scanning Planet {planet_num} {roll_str} ({roll}%): {planet_type} Discovered"))
    print(TextStyle.print_class("RNG", f"- -Surveying Planets ({planet_obj['name']})"))
    
    # Moons (Base Roll)
    moon_roll, moon_roll_str = roll_percentile()
    if moon_roll > 65:
        print(TextStyle.print_class("RNG", f"- - Scanning for Moons {moon_roll_str} ({moon_roll}%): Moons Detected"))
        moon_count_roll, die_name = roll_dice(system_vars["moonCount"]["min"], system_vars["moonCount"]["max"], "d5")
        num_moons = moon_count_roll
        print(TextStyle.print_class("RNG", f"- - - Surveying Moon Count {die_name}: {num_moons} Moons Identified"))
        for j in range(num_moons):
            moon_type, roll, roll_str = weighted_roll(moons, "chance", f"Moon {j+1} Type", chance_boost)
            planet_obj["children"].append({"type": "Moon", "name": f"{moon_type} of {planet_obj['name']}", "scavenged": False})
            print(TextStyle.print_class("RNG", f"- - - - Surveying Moon {j+1} {roll_str} ({roll}%): {moon_type} Discovered"))
    else:
        print(TextStyle.print_class("RNG", f"- - Scanning for Moons {moon_roll_str} ({moon_roll}%): No Moons Detected"))
    
    # Man-Made (Base Roll)
    for obj in man_made:
        roll, roll_str = roll_percentile()
        threshold = int(obj["chance"] * 100)
        if roll <= threshold:
            obj_id = random.randint(system_vars["objectIdRange"]["min"], system_vars["objectIdRange"]["max"])
            planet_obj["children"].append({"type": "Man-Made", "name": f"{obj['name']} {obj_id}", "scavenged": False})
            print(TextStyle.print_class("RNG", f"- - - Scanning Signs of Life {roll_str} ({roll}%): {obj['name']} Detected"))
        else:
            print(TextStyle.print_class("RNG", f"- - - Scanning Signs of Life {roll_str} ({roll}%): No {obj['name']} Detected"))
    
    return planet_obj