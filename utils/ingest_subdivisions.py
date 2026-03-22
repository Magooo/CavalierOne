import os
import json

BASE_DIR = r"c:/Users/jason.m.chgv/Documents/CavalierOne/resources/sharepoint_files/5 - Plan of Subdivisions & Covenants"
OUTPUT_FILE = r"c:/Users/jason.m.chgv/Documents/CavalierOne/resources/subdivisions_index.json"

def index_subdivisions():
    estates = []
    
    if not os.path.exists(BASE_DIR):
        print(f"Directory not found: {BASE_DIR}")
        return

    # Walk: Region -> Estate
    for region in os.listdir(BASE_DIR):
        region_path = os.path.join(BASE_DIR, region)
        if os.path.isdir(region_path):
            for estate in os.listdir(region_path):
                estate_path = os.path.join(region_path, estate)
                if os.path.isdir(estate_path):
                    
                    # Found an Estate!
                    estate_data = {
                        "estate_name": estate,
                        "suburb": region,
                        "lot_number": "TBA", # Placeholder for user to fill
                        "total_area_sqm": "TBC",
                        "dimensions": "Refer to Plan of Subdivision",
                        "titles_expected": "Check with Sales Manager",
                        "has_covenants": False
                    }
                    
                    # Check for keywords in filenames
                    for f in os.listdir(estate_path):
                        if "covenant" in f.lower():
                            estate_data["has_covenants"] = True
                            estate_data["covenants_file"] = f
                    
                    estates.append(estate_data)
                    print(f"Indexed: {estate} ({region})")

    # Save to temp file
    with open(OUTPUT_FILE, 'w') as f:
        json.dump(estates, f, indent=4)
    
    print(f"Complete. Found {len(estates)} estates.")

if __name__ == "__main__":
    index_subdivisions()
