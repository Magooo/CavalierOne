import fitz
import os

STYLE_GUIDE_PATH = r"c:/Users/jason.m.chgv/Documents/CavalierOne/resources/Cavalier_StyleGuide_forviewing.pdf"

def inspect_brochure_pages():
    doc = fitz.open(STYLE_GUIDE_PATH)
    
    # Check Brochures Section (Around Page 28-32)
    # Indices 27 to 31
    for i in range(27, 32): 
        if i < len(doc):
            page = doc[i]
            print(f"\n--- PAGE {i+1} ---")
            text = page.get_text()
            print(text[:1500]) # First 1500 chars to cover full page text usually

if __name__ == "__main__":
    inspect_brochure_pages()
