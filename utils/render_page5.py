import fitz
import os

pdf_path = r"c:\Users\jason.m.chgv\Documents\CavalierOne\resources\Cavalier_StyleGuide_forviewing.pdf"
output_path = r"c:\Users\jason.m.chgv\Documents\CavalierOne\resources\brand_assets\images\logo_primary_page5.png"

def render_logo_page():
    doc = fitz.open(pdf_path)
    page = doc[4] # Page 5 is index 4
    
    # Define Crop Box for Primary Logo (Based on geometry inspection)
    # Cand 0: Rect(56.69, 113.25, 538.58, 288.29)
    logo_rect = fitz.Rect(50, 100, 550, 300) # Added padding
    
    # Render at high DPI (300 DPI - zoom 4.0)
    zoom = 4.0 
    mat = fitz.Matrix(zoom, zoom)
    
    # Render only the cropped area
    pix = page.get_pixmap(matrix=mat, clip=logo_rect, alpha=True)
    
    pix.save(output_path)
    print(f"Rendered Page 5 to {output_path} ({pix.width}x{pix.height})")

if __name__ == "__main__":
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    render_logo_page()
