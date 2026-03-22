import fitz
import os

BROCHURES_DIR = r"c:/Users/jason.m.chgv/Documents/CavalierOne/resources/sharepoint_files/Brochures"

def inspect_malvern():
    # Find Malvern Brochure
    path = None
    for f in os.listdir(BROCHURES_DIR):
        if "Malvern Brochure - Print.pdf" in f:
            path = os.path.join(BROCHURES_DIR, f)
            break
            
    if not path:
        print("Brochure not found")
        return

    doc = fitz.open(path)
    # Search for Malvern 23 page
    target_page = None
    for i, page in enumerate(doc):
        text = page.get_text().upper()
        if "STANDARD FLOORPLAN" in text and "MALVERN 23" in text:
            target_page = page
            print(f"Found MALVERN 23 on page {i}")
            break
            
    if target_page:
        # List images
        images = target_page.get_images(full=True)
        print(f"Found {len(images)} images on page.")
        for img in images:
            xref = img[0]
            print(f"Image XREF: {xref} - Size info: {img}")
            
    else:
        print("Page not found")

if __name__ == "__main__":
    inspect_malvern()
