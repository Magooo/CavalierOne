from PIL import Image

def build_perfect_favicon():
    img = Image.open(r"C:\Users\jason.m.chgv\Documents\CavalierOne\static\images\favicon_candidate_p5_0.png").convert("RGB")
    
    W, H = img.size
    
    # 1. Mask darkest pixels (the 'ch' text)
    gray = img.convert("L")
    # Values less than 150 count as the dark letters
    text_mask = gray.point(lambda p: 255 if p < 150 else 0)
    
    text_bbox = text_mask.getbbox()
    if not text_bbox:
        print("Could not find the text 'ch'.")
        return
    
    x0, y0, x1, y1 = text_bbox
    print(f"Found dark text at: {text_bbox}")
    
    # Crop just the letters tightly
    letters = img.crop((x0, y0, x1, y1))
    w, h = letters.size
    print(f"Letter dimensions: {w}x{h}")
    
    # 2. Sample the exact background color immediately around the text
    # We look at exactly 15 pixels left of the 'c' to get the background grey color
    bg_x = max(0, x0 - 15)
    bg_y = y0 + (h // 2)
    bg_color = img.getpixel((bg_x, bg_y))
    print(f"Sampled Background color: {bg_color}")
    
    # 3. Create a mathematically perfect 1:1 square canvas
    # Let's give it plenty of aesthetic breathing room (padding)
    box_size = max(w, h) * 3
    new_img = Image.new("RGB", (box_size, box_size), bg_color)
    
    # 4. Paste the 'ch' dead-center
    paste_x = (box_size - w) // 2
    paste_y = (box_size - h) // 2
    
    new_img.paste(letters, (paste_x, paste_y))
    
    out_path = r"C:\Users\jason.m.chgv\Documents\CavalierOne\static\images\favicon.png"
    new_img.save(out_path)
    print("Success! Perfect favicon generated.")

build_perfect_favicon()
