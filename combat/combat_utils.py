# combat/combat_utils.py
import random
import main  # Use TextStyle from main

def roll_d20():
    roll = random.randint(1, 20)
    return roll, f"[d20({roll})]"

def roll_damage(damage_die):
    if damage_die == "d8":
        roll = random.randint(1, 8)
        return roll, f"[d8({roll})]"
    elif damage_die == "2d6":
        roll1 = random.randint(1, 6)
        roll2 = random.randint(1, 6)
        return roll1 + roll2, f"[d6({roll1}) + d6({roll2})]"
    elif damage_die == "d10":
        roll = random.randint(1, 10)
        return roll, f"[d10({roll})]"
    return 0, "[d0(0)]"

def calculate_initiative(ship):
    roll, roll_str = roll_d20()
    total = roll + ship["initiative_modifier"]
    return total, f"{roll_str}+{ship['initiative_modifier']}"

def apply_damage(attacker, defender, damage):
    if defender["shield"] > 0:
        if damage <= defender["shield"]:
            defender["shield"] -= damage
        else:
            excess = damage - defender["shield"]
            defender["shield"] = 0
            defender["hull"] -= excess
    else:
        defender["hull"] -= damage