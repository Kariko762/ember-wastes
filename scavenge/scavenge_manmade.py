# scavenge/scavenge_manmade.py
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

def roll_2d20():
    roll1 = random.randint(1, 20)
    roll2 = random.randint(1, 20)
    return roll1 + roll2, f"[d20({roll1}) + d20({roll2})]"

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
    loc_type = "Man-Made" if location["type"] == "Man-Made" else "Unknown"
    items = scavenge_data["locationMappings"][loc_type]["syntheticItems"]
    security_zone = player_data["security_zone"]
    
    duration = scavenge_data["locationMappings"][loc_type]["scavengeDuration"]
    scavenge_utils.show_progress_bar(duration, loc_type, location["name"], scavenge_data)
    
    print(f"\nScavenging {location['name']}:")
    print(f"Energy used: {energy_cost}")
    player_data["energy"] -= energy_cost
    success_chance = vars["successThreshold"]
    roll, roll_str = roll_percentile()
    total_items = 0
    
    # Base scavenging roll
    if roll > success_chance:
        print(f"Scanning for Resources {roll_str} ({roll}%): Success (Threshold {success_chance}%)")
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
        print(f"Scanning for Resources {roll_str} ({roll}%): No Resources Found (Threshold {success_chance}%)")
    
    # Security Zone Modifier roll (only for zones < 0.9)
    if security_zone < 0.9:
        if security_zone >= 0.6:  # Moderately Secure (0.7-0.5)
            extra_roll, extra_die = roll_dice(1, 2, "d2")
            extra_count = extra_roll - 1  # 0-1 items
            die_label = "d2"
        elif security_zone >= 0.3:  # Risky (0.4-0.2)
            extra_roll, extra_die = roll_dice(1, 3, "d3")
            extra_count = extra_roll - 1  # 0-2 items
            die_label = "d3"
        else:  # Unsecure (0.1-0.0)
            extra_roll, extra_die = roll_dice(1, 4, "d4")
            extra_count = extra_roll - 1  # 0-3 items
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
    
    # Energy Siphoning (Man-Made only)
    if loc_type == "Man-Made" and player_data["energy"] >= 5:
        choice = input(f"\nWould you like to attempt to extract residual energy from the facility (y/n) (Energy 5)? ").lower()
        if choice == "y":
            # Step 1: Scanning for Residual Energy
            scan_cost = 2
            if player_data["energy"] < scan_cost:
                print("Not enough energy to scan for residual energy!")
                return
            player_data["energy"] -= scan_cost
            scan_roll, scan_str = roll_percentile()
            siphon_chance = scavenge_data["siphoning"][loc_type]["successChance"]
            if scan_roll > siphon_chance:
                print(f"- Scanning for Residual Energy (-{scan_cost} Energy) {scan_str} ({scan_roll}%): Successfully identified residual energy.")
                
                # Step 2: Docking
                dock_cost = 2
                if player_data["energy"] < dock_cost:
                    print("Not enough energy to attempt docking!")
                    return
                player_data["energy"] -= dock_cost
                dock_roll, dock_str = roll_percentile()
                dock_chance = scavenge_data["siphoning"][loc_type]["dockChance"]
                if dock_roll > dock_chance:
                    dock_penalty = 1.0
                    print(f"-- Attempting to dock with facility (-{dock_cost} Energy) {dock_str} ({dock_roll}%): Stable Dock established.")
                else:
                    dock_penalty = 0.8
                    player_data["energy"] -= 2
                    player_data["hull"] -= 2
                    print(f"-- Attempting to dock with facility (-{dock_cost} Energy) {dock_str} ({dock_roll}%): Unstable Dock established. (-2 Energy / -2 Hull / Energy Waste * {dock_penalty})")
                
                # Step 3: Siphoning
                siphon_cost = 1
                if player_data["energy"] < siphon_cost:
                    print("Not enough energy to siphon residual energy!")
                    return
                player_data["energy"] -= siphon_cost
                siphon_roll, siphon_str = roll_2d20()
                siphon_yield = int(siphon_roll * scavenge_data["siphoning"][loc_type]["energyYield"][zone_key(security_zone)] * dock_penalty)
                print(f"-- Siphoning Energy from Facility (-{siphon_cost} Energy) {siphon_str} ({siphon_roll} * {dock_penalty} = {siphon_yield}): {siphon_yield} Energy Siphoned")
                player_data["energy"] += siphon_yield
            else:
                print(f"- Scanning for Residual Energy (-{scan_cost} Energy) {scan_str} ({scan_roll}%): No residual energy found.")
    
    # Ship Wreck Salvage (Conflict Zones only)
    if "Conflict Zone" in location["name"] and player_data["energy"] >= 5:
        wreck_roll, wreck_str = roll_percentile()
        wreck_chance = scavenge_data["wreckSalvage"]["successChance"]
        if wreck_roll > wreck_chance:
            print(f"\nScanning for Universal Signatures {wreck_str} ({wreck_roll}%): Colonial Frigate Wreckage located")
            choice = input("Would you like to attempt to salvage from the wreckage (y/n) (Energy 5)? ").lower()
            if choice == "y":
                # Step 1: Docking
                dock_cost = 2
                if player_data["energy"] < dock_cost:
                    print("Not enough energy to attempt docking!")
                    return
                player_data["energy"] -= dock_cost
                dock_roll, dock_str = roll_percentile()
                dock_chance = scavenge_data["wreckSalvage"]["dockChance"]
                if dock_roll > dock_chance:
                    dock_penalty = 1.0
                    print(f"-- Attempting to dock with the wreckage (-{dock_cost} Energy) {dock_str} ({dock_roll}%): Stable Dock established.")
                else:
                    dock_penalty = 0.8
                    player_data["energy"] -= 2
                    player_data["hull"] -= 2
                    print(f"-- Attempting to dock with the wreckage (-{dock_cost} Energy) {dock_str} ({dock_roll}%): Unstable Dock established. (-2 Energy / -2 Hull / Docking-Penalty {dock_penalty})")
                
                # Step 2: Searching for Resources
                search_cost = 2
                if player_data["energy"] < search_cost:
                    print("Not enough energy to search the wreckage!")
                    return
                player_data["energy"] -= search_cost
                search_roll, search_str = roll_percentile()
                if search_roll > success_chance:
                    print(f"-- Searching for Resources {search_str} ({search_roll}%): Success (Threshold {success_chance}%)")
                    wreck_count, wreck_die = roll_dice(vars["itemCountRange"]["min"], vars["itemCountRange"]["max"], "d3")
                    print(f"--- Determining Yield {wreck_die}: {wreck_count} Items Found")
                    for i in range(wreck_count):
                        item_name, roll, roll_str = weighted_roll(items, "chance")
                        qty_roll, qty_die = roll_dice(1, 3, "d3")
                        print(f"--- Scavenging Item {i+1} {roll_str} ({roll}%): {item_name} ({qty_roll}) Discovered")
                        found = False
                        for item in ship_inventory:
                            if item["name"] == item_name:
                                item["quantity"] += qty_roll
                                found = True
                                break
                        if not found:
                            ship_inventory.append({"name": item_name, "quantity": qty_roll})
                    
                    # Step 3: Siphoning Energy
                    siphon_cost = 1
                    if player_data["energy"] < siphon_cost:
                        print("Not enough energy to siphon residual energy!")
                        return
                    player_data["energy"] -= siphon_cost
                    siphon_roll, siphon_str = roll_2d20()
                    siphon_yield = int(siphon_roll * scavenge_data["wreckSalvage"]["energyYield"][zone_key(security_zone)] * dock_penalty)
                    print(f"--- Siphoning Energy from Wreckage (-{siphon_cost} Energy) {siphon_str} ({siphon_roll} * {dock_penalty} = {siphon_yield}): {siphon_yield} Energy Siphoned")
                    player_data["energy"] += siphon_yield
                else:
                    print(f"-- Searching for Resources {search_str} ({search_roll}%): No additional resources found.")
        else:
            print(f"\nScanning for Universal Signatures {wreck_str} ({wreck_roll}%): No viable wreckage located")

def zone_key(security_zone):
    if security_zone >= 0.9:
        return "Secure Space"
    elif security_zone >= 0.6:
        return "Moderately Secure Space"
    elif security_zone >= 0.3:
        return "Risky Space"
    else:
        return "Unsecure Space"