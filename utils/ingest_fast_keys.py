import os
from pdfminer.high_level import extract_text
import docx

BASE_DIR = r"c:/Users/jason.m.chgv/Documents/CavalierOne/resources/sharepoint_files"

def extract_from_pdf(filename):
    path = os.path.join(BASE_DIR, filename)
    try:
        text = extract_text(path)
        return f"\n--- EXTRACTED FROM {filename} ---\n{text}\n"
    except Exception as e:
        return f"Error reading {filename}: {e}"

def extract_from_docx(filename):
    path = os.path.join(BASE_DIR, filename)
    try:
        doc = docx.Document(path)
        text = "\n".join([para.text for para in doc.paragraphs])
        return f"\n--- EXTRACTED FROM {filename} ---\n{text}\n"
    except Exception as e:
        return f"Error reading {filename}: {e}"

if __name__ == "__main__":
    output = ""
    
    # Extract Process
    output += extract_from_docx("Fast Keys Process.docx")
    
    # Extract Inclusions
    output += extract_from_pdf("Fast Keys - Standard Inclusions.pdf")
    
    # Extract one brochure to see tone
    output += extract_from_pdf("Brochures/Malvern Brochure - Print.pdf")

    # Save to file
    with open("c:/Users/jason.m.chgv/Documents/CavalierOne/resources/fast_keys_extraction.txt", "w", encoding="utf-8") as f:
        f.write(output)
