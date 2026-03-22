import fitz # PyMuPDF
import os

pdf_path = r"c:\Users\jason.m.chgv\Documents\CavalierOne\resources\Cavalier_StyleGuide_forviewing.pdf"
output_dir = r"c:\Users\jason.m.chgv\Documents\CavalierOne\static\images\extracted"

os.makedirs(output_dir, exist_ok=True)

try:
    doc = fitz.open(pdf_path)
    print(f"Opened PDF with {len(doc)} pages.")

    image_count = 0
    # Process ALL pages
    for i in range(len(doc)): 
        page = doc[i]
        image_list = page.get_images()
        
        # print(f"--- Page {i+1} ---")
        for img_index, img in enumerate(image_list, start=1):
            xref = img[0]
            base_image = doc.extract_image(xref)
            image_bytes = base_image["image"]
            image_ext = base_image["ext"]
            width = base_image["width"]
            height = base_image["height"]
            
            # Filter tiny icons/artifacts (Keep reasonable sized assets)
            if len(image_bytes) < 10000: # Increase threshold to skip noise
                continue
                
            image_name = f"page{i+1}_img{img_index}_{width}x{height}.{image_ext}"
            image_path = os.path.join(output_dir, image_name)
            
            with open(image_path, "wb") as f:
                f.write(image_bytes)
            
            # print(f"Saved: {image_name}")
            image_count += 1
            
    print(f"Extraction complete. Saved {image_count} images.")
except Exception as e:
    print(f"Error: {e}")
