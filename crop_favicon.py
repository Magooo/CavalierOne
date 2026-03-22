from PIL import Image
import os

candidate_path = r"C:\Users\jason.m.chgv\Documents\CavalierOne\static\images\favicon_candidate_p5_0.png"
out_path = r"C:\Users\jason.m.chgv\Documents\CavalierOne\static\images\favicon.png"

img = Image.open(candidate_path)
img = img.convert("RGB")

gray = img.convert("L")
mask = gray.point(lambda p: 255 if p < 250 else 0)

bbox = mask.getbbox()

if bbox:
    cropped = img.crop(bbox)
    w, h = cropped.size
    
    # If it's a wide rectangle, the style guide probably had both the white and grey versions 
    # sitting side-by-side. We want the grey (right side) part. Favicons should be square.
    if w > h * 1.5:
        # Crop the rightmost square
        new_bbox = (w - h, 0, w, h)
        cropped = cropped.crop(new_bbox)
    
    # Force absolute square by adding a tiny bit of padding if necessary
    w, h = cropped.size
    size = max(w, h)
    
    square_img = Image.new("RGB", (size, size), (242, 243, 244)) # match typical grey
    x_offset = (size - w) // 2
    y_offset = (size - h) // 2
    square_img.paste(cropped, (x_offset, y_offset))
    
    square_img.save(out_path)
    print(f"Successfully cropped tightly! Final dimensions: {square_img.size}")
else:
    print("Could not find bounding box.")
