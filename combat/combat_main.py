# combat/combat_main.py
from combat.combat_utils import roll_d20, roll_damage, calculate_initiative, apply_damage
import main  # Import TextStyle from main
import sys

def print_combat_stats(player, enemy):
    main.TextStyle.print_class("Information", "Stats")
    main.TextStyle.print_class("Information", "=====")
    main.TextStyle.print_class("Information", f"{player['name']} (Hull: {player['hull']}/{player['max_hull']}, Shield: {player['shield']}/{player['max_shield']})")
    main.TextStyle.print_class("Information", f"{enemy['name']} (Hull: {enemy['hull']}/{enemy['max_hull']}, Shield: {enemy['shield']}/{enemy['max_shield']})")
    main.TextStyle.print_class("Information", "=====")

def initiate_combat(player_data, enemy_npc):
    main.TextStyle.print_class("Information", "\n=== Combat Initiated ===")
    
    # Roll initiative
    player_init, player_init_str = calculate_initiative(player_data)
    enemy_init, enemy_init_str = calculate_initiative(enemy_npc)
    main.TextStyle.print_class("Information", f"- {player_data['name']} Rolling Initiative: {player_init_str} = {player_init}")
    main.TextStyle.print_class("Information", f"- {enemy_npc['name']} Rolling Initiative: {enemy_init_str} = {enemy_init}")
    main.TextStyle.print_class("Information", "=====")
    
    turn_order = [(player_data, "Player"), (enemy_npc, "Enemy")] if player_init >= enemy_init else [(enemy_npc, "Enemy"), (player_data, "Player")]
    
    # Combat loop
    round_num = 1
    while player_data["hull"] > 0 and enemy_npc["hull"] > 0:
        print_combat_stats(player_data, enemy_npc)
        main.TextStyle.print_class("Information", f"\nRound {round_num}")
        main.TextStyle.print_class("Information", "=====")
        
        for attacker, attacker_type in turn_order:
            defender = enemy_npc if attacker_type == "Player" else player_data
            if attacker["hull"] <= 0:
                continue
            
            if attacker_type == "Player":
                prompt = "Action: (1) Attack, (2) Disengage: "
                styled_prompt = main.TextStyle.print_class("Information", prompt, delay_to_display=0, display_mode="instant", print_output=False)
                sys.stdout.write(styled_prompt)
                sys.stdout.flush()
                action = input().strip()
                full_line = main.TextStyle.print_class("Information", f"Action: (1) Attack, (2) Disengage: {action}", delay_to_display=0, display_mode="instant", print_output=False)
                #sys.stdout.write("\r" + full_line + "\n")  # Overwrite with full line once, no extra print
                sys.stdout.flush()
                
                if action == "1":
                    attack_roll, attack_str = roll_d20()
                    hit_status = "Success" if attack_roll >= defender["armor_class"] else "Warning"
                    attack_line = f"{attacker['name']} Rolling Attack (> {defender['armor_class']}): {attack_str} - {'Hit!' if attack_roll >= defender['armor_class'] else 'Miss!'}"
                    main.TextStyle.print_class(hit_status, attack_line)
                    if attack_roll >= defender["armor_class"]:
                        damage, damage_str = roll_damage(attacker["weapons"][0]["damage"])
                        main.TextStyle.print_class("Information", f"{attacker['name']} Rolling Damage : {damage_str} - {attacker['name']} Deals {damage} Damage.")
                        apply_damage(attacker, defender, damage)
                elif action == "2":
                    if player_data["energy"] < 20:
                        main.TextStyle.print_class("Warning", "Not enough energy to disengage (Need 20 Energy)!")
                        continue
                    disengage_roll, disengage_str = roll_d20()
                    disengage_status = "Success" if disengage_roll > defender["disengage"] else "Warning"
                    disengage_line = f"{attacker['name']} Rolling Disengage (> {defender['disengage']}): {disengage_str} - {'Success!' if disengage_roll > defender['disengage'] else 'Failed to Disengage'}"
                    main.TextStyle.print_class(disengage_status, disengage_line)
                    if disengage_roll > defender["disengage"]:
                        main.TextStyle.print_class("Information", f"{attacker['name']} successfully disengages! Returning to Home...")
                        player_data["energy"] -= 20
                        player_data["location"] = "Home"
                        return
            else:
                attack_roll, attack_str = roll_d20()
                hit_status = "Success" if attack_roll >= defender["armor_class"] else "Warning"
                attack_line = f"{attacker['name']} Rolling Attack (> {defender['armor_class']}): {attack_str} - {'Hit!' if attack_roll >= defender['armor_class'] else 'Miss!'}"
                main.TextStyle.print_class(hit_status, attack_line)
                if attack_roll >= defender["armor_class"]:
                    damage, damage_str = roll_damage(attacker["weapons"][0]["damage"])
                    main.TextStyle.print_class("Information", f"{attacker['name']} Rolling Damage : {damage_str} - {attacker['name']} Deals {damage} Damage.")
                    apply_damage(attacker, defender, damage)
        
        main.TextStyle.print_class("Information", "- - -")  # Separator between rounds
        
        if player_data["hull"] <= 0:
            main.TextStyle.print_class("Warning", "\nYour ship has been destroyed! Game Over.")
            return
        if enemy_npc["hull"] <= 0:
            main.TextStyle.print_class("Information", f"\n{enemy_npc['name']} has been destroyed! Victory!")
            return
        
        round_num += 1