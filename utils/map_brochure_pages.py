import fitz
import os
import json

BROCHURES_DIR = r"c:/Users/jason.m.chgv/Documents/CavalierOne/resources/sharepoint_files/Brochures"

def map_pages():
    brochures = [f for f in os.listdir(BROCHURES_DIR) if f.endswith('Print.pdf')]
    mapping = {}

    for b in brochures:
        path = os.path.join(BROCHURES_DIR, b)
        doc = fitz.open(path)
        
        print(f"Scanning {b}...")
        
        for i, page in enumerate(doc):
            text = page.get_text().upper()
            
            # Heuristic: Look for "Malvern 20", "Malvern 23", "Ashwood 28" etc.
            # And also "Standard Floorplan" to ensure it's the plan page, not just a mention.
            
            # We will store: mapping["Malvern 20"] = {"file": b, "page": i}
            
            # Detect Series Name from filename (e.g. Malvern)
            series = b.split(' ')[0].upper()
            
            if "STANDARD FLOORPLAN" in text:
                # Look for specific size numbers (20, 23, 28, etc)
                # Simple parser: look for "SERIES X" or just "X" where X is a number
                # Actually, typically heading is "Malvern 20"
                
                # Check lines
                lines = text.split('\n')
                for line in lines:
                    if series in line:
                        # try to find the full model name e.g. MALVERN 20
                        # This avoids matching just "Malvern"
                        if any(char.isdigit() for char in line):
                            model_name = line.strip() 
                            # clean it up (remove extra spaces)
                            model_name = " ".join(model_name.split())
                            
                            print(f"Found plan for {model_name} on page {i+1}")
                            mapping[model_name] = {"file": b, "page_index": i}
                            break
                            
    return mapping

if __name__ == "__main__":
    m = map_pages()
    print(json.dumps(m, indent=2))
