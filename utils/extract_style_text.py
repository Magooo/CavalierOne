import fitz
import os
import json

pdf_path = r"c:\Users\jason.m.chgv\Documents\CavalierOne\resources\Cavalier_StyleGuide_forviewing.pdf"
output_path = r"c:\Users\jason.m.chgv\Documents\CavalierOne\resources\brand_assets\style_text_raw.txt"

def extract_text():
    doc = fitz.open(pdf_path)
    full_text = ""
    
    print(f"Extracting text from {len(doc)} pages...")
    
    for i, page in enumerate(doc):
        text = page.get_text("text")
        full_text += f"\n\n--- Page {i+1} ---\n\n"
        full_text += text
        
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(full_text)
        
    print(f"Text saved to {output_path}")

if __name__ == "__main__":
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    extract_text()
