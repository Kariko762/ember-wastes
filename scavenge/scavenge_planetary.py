# scavenge/scavenge_planetary.py
import json
import os
import random
import scavenge.scavenge_utils as scavenge_utils

def roll_percentile():
    tens = random.randint(0, 9) * 10
    ones = random.randint(1, 9)
    return tens + ones, f"[d10({tens//10})+{ones}]"

def roll_dice(min_val, max_val, die_name):
    roll = random.randint(min_val, max_val)
    return roll, f"[{die_name}({roll})]"

def weighted_roll(options, chance_key):
    roll, roll_str = roll_percentile()
    cumulative = 0
    for option in options:
        cumulative += int(option[chance_key] * 100)
        if roll <= cumulative:
            return option["name"], roll, roll_str
    return options[-1]["name"], roll, roll_str

def scavenge(player_data, location, ship_inventory, energy_cost, scavenge_data):
    vars = scavenge_data["scavengeVariables"]
    loc_type = location["type"]
    items = scavenge_data["locationMappings"]["Planet"]["resources"]
    security_zone = player_data["security_zone"]
    
    duration = scavenge_data["locationMappings"][loc_type]["scavengeDuration"]
    scavenge_utils.show_progress_bar(duration, loc_type, location["name"], scavenge_data)
    
    print(f"\nScavenging {location['name']}:")
    print(f"Energy used: {energy_cost}")
    player_data["energy"] -= energy_cost
    success_chance = vars["successThreshold"]
    roll, roll_str = roll_percentile()
    total_items = 0
    
    if roll > success_chance:
        print(f"Scanning Planet Surface {roll_str} ({roll}%): Success (Threshold {success_chance}%)")
        base_count, base_die = roll_dice(vars["itemCountRange"]["min"], vars["itemCountRange"]["max"], "d3")
        print(f"Determining Yield {base_die}: {base_count} Items Found")
        total_items = base_count
        
        for i in range(base_count):
            item_name, roll, roll_str = weighted_roll(items, "chance")
            qty_roll, qty_die = roll_dice(1, 3, "d3")
            print(f"- Scavenging Item {i+1} {roll_str} ({roll}%): {item_name} ({qty_roll}) Discovered")
            found = False
            for item in ship_inventory:
                if item["name"] == item_name:
                    item["quantity"] += qty_roll
                    found = True
                    break
            if not found:
                ship_inventory.append({"name": item_name, "quantity": qty_roll})
    else:
        print(f"Scanning Planet Surface {roll_str} ({roll}%): No Resources Found (Threshold {success_chance}%)")
    
    if security_zone < 0.9:
        if security_zone >= 0.6:
            extra_roll, extra_die = roll_dice(1, 2, "d2")
            extra_count = extra_roll - 1
            die_label = "d2"
        elif security_zone >= 0.3:
            extra_roll, extra_die = roll_dice(1, 3, "d3")
            extra_count = extra_roll - 1
            die_label = "d3"
        else:
            extra_roll, extra_die = roll_dice(1, 4, "d4")
            extra_count = extra_roll - 1
            die_label = "d4"
        
        print(f"Rolling Security Zone Modifier [{die_label}({extra_roll})-1]: {extra_count} Additional Items Found")
        if extra_count > 0:
            total_items += extra_count
            start_index = total_items - extra_count + 1 if total_items > extra_count else 1
            for i in range(start_index, start_index + extra_count):
                item_name, roll, roll_str = weighted_roll(items, "chance")
                qty_roll, qty_die = roll_dice(1, 3, "d3")
                print(f"- Scavenging Item {i} {roll_str} ({roll}%): {item_name} ({qty_roll}) Discovered")
                found = False
                for item in ship_inventory:
                    if item["name"] == item_name:
                        item["quantity"] += qty_roll
                        found = True
                        break
                if not found:
                    ship_inventory.append({"name": item_name, "quantity": qty_roll})