import fitz
import os
import sys

pdf_path = r"c:\Users\jason.m.chgv\Documents\CavalierOne\resources\Cavalier_StyleGuide_forviewing.pdf"
doc = fitz.open(pdf_path)

for i in range(len(doc)):
    page = doc[i]
    instances = page.search_for("LOGOMARK")
    if instances:
        print(f"Found 'LOGOMARK' on page {i+1}")
        for idx, rect in enumerate(instances):
            print(f"Instance {idx}: {rect}")
            
            # Create a clipping rectangle covering the "ch" grey box below the word "LOGOMARK"
            # Looking at the user's screenshot, the "ch" box is below the word.
            # We'll take a generous 200x200 pixel box below the text
            clip_rect = fitz.Rect(rect.x0 - 20, rect.y1 + 10, rect.x0 + 200, rect.y1 + 230)
            
            try:
                pix = page.get_pixmap(clip=clip_rect, dpi=300)
                out_path = fr"c:\Users\jason.m.chgv\Documents\CavalierOne\static\images\favicon_candidate_p{i+1}_{idx}.png"
                pix.save(out_path)
                print(f"Saved {out_path}")
            except Exception as e:
                print(f"Failed to snap rect: {e}")
