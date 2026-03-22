import json
import os

TEMPLATES_PATH = r"c:/Users/jason.m.chgv/Documents/CavalierOne/resources/input_templates.json"
INDEX_PATH = r"c:/Users/jason.m.chgv/Documents/CavalierOne/resources/subdivisions_index.json"

def merge_data():
    with open(TEMPLATES_PATH, 'r') as f:
        data = json.load(f)
    
    with open(INDEX_PATH, 'r') as f:
        new_estates = json.load(f)
    
    # Ensure land_details_template is a list
    current_land = data.get("land_details_template", [])
    if isinstance(current_land, dict):
        current_land = [current_land]
        
    # Append unique
    existing_names = [x.get("estate_name") for x in current_land]
    
    count = 0
    for estate in new_estates:
        if estate["estate_name"] not in existing_names:
            current_land.append(estate)
            count += 1
            
    data["land_details_template"] = current_land
    
    with open(TEMPLATES_PATH, 'w') as f:
        json.dump(data, f, indent=4)
        
    print(f"Merged {count} new estates into input_templates.json")

if __name__ == "__main__":
    merge_data()
