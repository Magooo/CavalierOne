import fitz

pdf_path = r"c:\Users\jason.m.chgv\Documents\CavalierOne\resources\Cavalier_StyleGuide_forviewing.pdf"

def inspect_page5():
    doc = fitz.open(pdf_path)
    page = doc[4] # Page 5
    
    print(f"Page Size: {page.rect}")
    
    # 1. Look for text blocks to find landmarks
    blocks = page.get_text("dict")["blocks"]
    print("\n--- TEXT BLOCKS ---")
    for b in blocks:
        if "lines" in b:
            for line in b["lines"]:
                for span in line["spans"]:
                    text = span["text"].strip()
                    if "PRIMARY" in text or "LOGO" in text or "Cavalier" in text:
                        print(f"Text: '{text}' | BBox: {span['bbox']}")

    # 2. Look for drawings (vector paths) which likely make up the logo
    drawings = page.get_drawings()
    print(f"\n--- DRAWINGS ({len(drawings)} paths found) ---")
    
    # Group drawings to find the dense cluster (likely the logo)
    # We'll just print the bounding rect of the first few large composite drawings
    logo_candidates = []
    for i, p in enumerate(drawings):
        rect = p["rect"]
        width = rect.width
        height = rect.height
        
        # Filter out full page borders or tiny dots
        if width > 50 and height > 10 and width < 600:
             logo_candidates.append(rect)
    
    # Print candidates sorted by vertical position
    logo_candidates.sort(key=lambda r: r.y0)
    with open("page5_geometry.txt", "w") as f:
        f.write(f"Page Size: {page.rect}\n")
        
        logo_candidates.sort(key=lambda r: r.y0)
        f.write("\n--- CANDIDATES ---\n")
        for i, r in enumerate(logo_candidates[:20]): # Show more candidates
            aspect = r.width / r.height
            f.write(f"Cand {i}: {r} (WxH: {r.width:.1f}x{r.height:.1f}, AR: {aspect:.2f})\n")
            
        f.write("\n--- TEXT ---\n")
        for b in blocks:
            for line in b["lines"]:
                for span in line["spans"]:
                    text = span["text"].strip()
                    if "LOGO" in text or "Cavalier" in text or "PRIMARY" in text:
                         f.write(f"Text '{text}': {span['bbox']}\n")
                         
    print("Geometry saved to page5_geometry.txt")

if __name__ == "__main__":
    inspect_page5()
