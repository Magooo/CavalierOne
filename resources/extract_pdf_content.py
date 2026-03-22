import PyPDF2
import sys

def extract_text_from_pdf(pdf_path):
    try:
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            text = ""
            for page_num, page in enumerate(reader.pages):
                text += f"--- Page {page_num + 1} ---\n"
                text += page.extract_text() + "\n"
            return text
    except Exception as e:
        return f"Error reading PDF: {str(e)}"

if __name__ == "__main__":
    if len(sys.argv) > 1:
        pdf_path = sys.argv[1]
    else:
        pdf_path = r"c:/Users/jason.m.chgv/Documents/CavalierOne/resources/Cavalier_StyleGuide_forviewing.pdf"
    
    text = extract_text_from_pdf(pdf_path)
    with open("extracted_text.txt", "w", encoding="utf-8") as f:
        f.write(text)
    print("Done")
