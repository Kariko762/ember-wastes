# systems/systemsCreateAnomalies.py
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
        adjusted_options.append({"name": opt["name"], "chance": adjusted_chance, "wreckage": opt.get("wreckage")})
    for option in adjusted_options:
        cumulative += int(option["chance"] * 100)
        if roll <= cumulative:
            return option, roll, roll_str
    return adjusted_options[-1], roll, roll_str

def create_anomalies(system_data, zone_data):
    unknown = system_data["unknown_objects"]
    system_vars = system_data["systemVariables"]
    anomalies = []
    unknown_found = False
    
    # Base Anomaly Roll
    for obj in unknown:
        roll, roll_str = roll_percentile()
        threshold = int(obj["chance"] * 100)
        if roll <= threshold:
            unknown_found = True
            obj_id = random.randint(system_vars["objectIdRange"]["min"], system_vars["objectIdRange"]["max"])
            event_obj = {"type": "Unknown", "name": f"{obj['name']} {obj_id}", "scavenged": False}
            if "wreckage" in obj:
                event_obj["wreckage"] = obj["wreckage"]
            anomalies.append(event_obj)
            print(TextStyle.print_class("RNG", f"Scanning Unknown Signals {roll_str} ({roll}%): {obj['name']} Discovered"))
        else:
            print(TextStyle.print_class("RNG", f"Scanning Unknown Signals {roll_str} ({roll}%): No {obj['name']} Detected"))
    
    # Security Zone Modifier Roll
    extra_unknown_roll, extra_die = roll_dice(zone_data["extraUnknown"]["min"], zone_data["extraUnknown"]["max"], "dX")
    extra_unknowns = extra_unknown_roll
    if extra_unknowns > 0:
        print(TextStyle.print_class("RNG", f"Security Zone Extra Anomalies {extra_die}: {extra_unknowns} Additional Unknown Objects Found"))
        for i in range(extra_unknowns):
            obj, roll, roll_str = weighted_roll(unknown, "chance", f"Extra Unknown {i+1}", zone_data["chanceBoost"])
            obj_id = random.randint(system_vars["objectIdRange"]["min"], system_vars["objectIdRange"]["max"])
            event_obj = {"type": "Unknown", "name": f"{obj['name']} {obj_id}", "scavenged": False}
            if "wreckage" in obj:
                event_obj["wreckage"] = obj["wreckage"]
            anomalies.append(event_obj)
            print(TextStyle.print_class("RNG", f"- Extra Anomaly Scan {roll_str} ({roll}%): {obj['name']} Discovered"))
    
    if not unknown_found and extra_unknowns == 0:
        print(TextStyle.print_class("RNG", "Scanning Unknown Signals: No Unknown Signals Detected"))
    
    return anomalies