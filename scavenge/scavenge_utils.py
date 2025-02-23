# scavenge/scavenge_utils.py
import time
import sys
import main  # Use TextStyle from main

def show_progress_bar(duration, location_type, location_name, scavenge_data):
    steps = 10
    step_time = duration / steps
    messages = scavenge_data["locationMappings"].get(location_type, {}).get("progressMessages", {100: "Processing"})
    
    # Convert string keys to integers for comparison
    percent_keys = sorted(messages.keys(), key=int)  # Already sorted by int, but keep as strings
    percent_keys_int = [int(k) for k in percent_keys]  # Convert to integers for comparison
    
    for i in range(steps + 1):
        percent = (i * 100) // steps
        bar = "#" * i + " " * (steps - i)
        # Find the nearest lower message using integer comparison
        msg_key = next((k for k in reversed(percent_keys_int) if k <= percent), percent_keys_int[0])
        msg = messages[str(msg_key)]  # Fetch message using original string key
        line = f"Scavenging {location_name}: [{bar}] {percent}% - {msg}"
        main.TextStyle.print_class("Information", line)  # Print each step as a new line
        time.sleep(step_time)
    
    # No clearing needed since we’re not overwriting