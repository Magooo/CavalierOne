import fitz
import os

STYLE_GUIDE_PATH = r"c:/Users/jason.m.chgv/Documents/CavalierOne/resources/Cavalier_StyleGuide_forviewing.pdf"

def inspect_page_26():
    doc = fitz.open(STYLE_GUIDE_PATH)
    
    # Check page count
    print(f"Total Pages: {len(doc)}")
    
    # Pages to check (around 26)
    pages_to_check = [25, 26, 27] # 0-indexed, so 25 is Page 26
    
    for i in pages_to_check:
        if i < len(doc):
            page = doc[i]
            print(f"\n--- PAGE {i+1} ---")
            text = page.get_text()
            print(text[:1000]) # First 1000 chars
            
            # Search for specific layout keywords
            if "LAYOUT" in text.upper() or "BROCHURE" in text.upper() or "PALETTE" in text.upper():
                print(f"*** RELEVANT CONTENT FOUND ON PAGE {i+1} ***")

if __name__ == "__main__":
    inspect_page_26()
