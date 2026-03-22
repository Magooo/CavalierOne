from pdfminer.high_level import extract_text
import sys

def extract_text_pdfminer(pdf_path):
    try:
        text = extract_text(pdf_path)
        return text
    except Exception as e:
        return f"Error reading PDF: {str(e)}"

if __name__ == "__main__":
    pdf_path = r"c:/Users/jason.m.chgv/Documents/CavalierOne/resources/Company info/Business Operation Plan - Cavalier Homes GV - Mar-25.pdf"
    text = extract_text_pdfminer(pdf_path)
    # Print to stdout for easier capture, or write to file. Let's write to a specific file.
    with open(r"c:/Users/jason.m.chgv/Documents/CavalierOne/resources/business_plan_text.txt", "w", encoding="utf-8") as f:
        f.write(text)
