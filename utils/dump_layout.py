import fitz
import os

BROCHURES_DIR = r"c:/Users/jason.m.chgv/Documents/CavalierOne/resources/sharepoint_files/Brochures"

def dump_layout():
    # Find Malvern Brochure
    path = None
    for f in os.listdir(BROCHURES_DIR):
        if "Malvern Brochure - Print.pdf" in f:
            path = os.path.join(BROCHURES_DIR, f)
            break
            
    doc = fitz.open(path)
    
    # Find the Page
    for i, page in enumerate(doc):
        text = page.get_text().upper()
        if "STANDARD FLOORPLAN" in text and "MALVERN 23" in text:
            print(f"--- PAGE {i} LAYOUT ---")
            blocks = page.get_text("blocks")
            for b in blocks:
                # x0, y0, x1, y1, text, block_no, block_type
                # x0, y0, x1, y1, text, block_no, block_type
                txt = b[4].strip().replace('\n', ' ')
                print(f"Y={b[1]:.1f}-{b[3]:.1f} | X={b[0]:.1f}-{b[2]:.1f} | TEXT: {txt[:50]}")
            break

if __name__ == "__main__":
    dump_layout()
