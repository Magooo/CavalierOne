import fitz
import os

BROCHURES_DIR = r"c:/Users/jason.m.chgv/Documents/CavalierOne/resources/sharepoint_files/Brochures"

def find_layout_anchors():
    # Find Malvern Brochure
    path = None
    for f in os.listdir(BROCHURES_DIR):
        if "Malvern Brochure - Print.pdf" in f:
            path = os.path.join(BROCHURES_DIR, f)
            break
            
    doc = fitz.open(path)
    target_page = None
    
    # 1. Find the Page
    for i, page in enumerate(doc):
        text = page.get_text().upper()
        if "STANDARD FLOORPLAN" in text and "MALVERN 23" in text:
            target_page = page
            print(f"Analyzing Page {i} (Width: {page.rect.width}, Height: {page.rect.height})")
            break
            
    if target_page:
        # 2. Find Anchors
        # Anchor Top: The specific model name header e.g. "Malvern 23"
        # Anchor Bottom: "Floor Plan Extensions"
        
        keywords = ["MALVERN 23", "STANDARD FLOORPLAN", "FLOOR PLAN EXTENSIONS", "TOTAL"]
        
        for k in keywords:
            rects = target_page.search_for(k)
            if rects:
                print(f"Found '{k}' at: {rects[0]}") # x0, y0, x1, y1
                # y1 is the bottom of the text
            else:
                print(f"'{k}' not found on page.")

    else:
        print("Page not found")

if __name__ == "__main__":
    find_layout_anchors()
