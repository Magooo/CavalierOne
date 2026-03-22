import cv2
import numpy as np
import os

def enhance_lines_for_controlnet(image_path):
    """
    Advanced Pre-processing: "Speckle Removal / Content Filtering"
    Uses OpenCV Contour Filtering to remove text and dimensions.
    
    1. Thresholding to get binary map.
    2. Find Contours.
    3. Filter: Remove small contours (Area < Threshold).
       - Text is small isolated blobs.
       - Walls are large connected blobs.
    4. Save clean output.
    """
    try:
        print(f"Applying Speckle/Text Removal to: {image_path}")
        
        # 1. Read Image
        img = cv2.imread(image_path)
        if img is None:
            raise ValueError("Could not load image")
            
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # 2. Thresholding (Invert so lines are White, BG is Black for contour finding)
        # Using simple binary threshold usually works well for PDFs
        _, binary = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY_INV)
        
        # 3. Find Contours
        contours, hierarchy = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # 4. Filter Contours (The "Intelligence" Layer)
        # Text characters are usually small (< 500px area depends on resolution, but let's be conservative)
        # Walls are huge.
        
        clean_mask = np.zeros_like(binary)
        
        # Dynamic threshold based on image size? 
        # For a standard 2000x3000 drawing, text chars are maybe 100-300px area.
        min_area_threshold = 150 
        
        kept_count = 0
        removed_count = 0
        
        for cnt in contours:
            area = cv2.contourArea(cnt)
            if area > min_area_threshold:
                cv2.drawContours(clean_mask, [cnt], -1, 255, thickness=cv2.FILLED)
                kept_count += 1
            else:
                removed_count += 1
                
        print(f"Text Removal: Kept {kept_count} large objects (Walls). Removed {removed_count} small objects (Text/Dims).")
        
        # 5. Invert back to Black Lines on White BG
        clean_image = cv2.bitwise_not(clean_mask)
        
        # 6. Save Debug & Output
        debug_path = os.path.join(os.path.dirname(image_path), "debug_clean_input.png")
        cv2.imwrite(debug_path, clean_image)
        print(f"Saved cleaned input to: {debug_path}")
        
        return debug_path
        
    except Exception as e:
        print(f"Error in Text Removal: {e}")
        return image_path # Fallback to original
