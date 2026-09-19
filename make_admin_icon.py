from PIL import Image
import math

def create_admin_icon():
    # 1. Load the original favicon (to get the plane)
    plane_img = Image.open(r"C:\Users\shrey\.gemini\antigravity\brain\39593da8-a713-452d-bf37-a7de45b2a5a1\.user_uploaded\media_1789840600158.png").convert('RGBA')
    p_w, p_h = plane_img.size
    
    # Extract the plane (blue pixels)
    bg_color = (15, 23, 42)
    min_x, min_y, max_x, max_y = p_w, p_h, 0, 0
    p_pixels = plane_img.load()
    
    for y in range(p_h - 15):
        for x in range(p_w):
            r, g, b, a = p_pixels[x, y]
            dist = math.sqrt((r-bg_color[0])**2 + (g-bg_color[1])**2 + (b-bg_color[2])**2)
            if dist > 30:
                if x < min_x: min_x = x
                if x > max_x: max_x = x
                if y < min_y: min_y = y
                if y > max_y: max_y = y
                
    icon_w = max_x - min_x + 1
    icon_h = max_y - min_y + 1
    
    # Create isolated plane image
    isolated_plane = Image.new('RGBA', (icon_w, icon_h), (0,0,0,0))
    iso_pixels = isolated_plane.load()
    
    for y in range(min_y, max_y + 1):
        for x in range(min_x, max_x + 1):
            r, g, b, a = p_pixels[x, y]
            dist = math.sqrt((r-bg_color[0])**2 + (g-bg_color[1])**2 + (b-bg_color[2])**2)
            if dist > 30:
                # We will color it orange later, for now just copy alpha
                iso_pixels[x - min_x, y - min_y] = (255, 255, 255, a) # Base white template

    # 2. Load the shield image
    shield_img = Image.open(r"C:\Users\shrey\.gemini\antigravity\brain\39593da8-a713-452d-bf37-a7de45b2a5a1\.user_uploaded\media_1789840758827.png").convert('RGBA')
    s_w, s_h = shield_img.size
    s_pixels = shield_img.load()
    
    # Let's find the orange color used in the shield
    orange_color = (255, 165, 0) # Default fallback
    max_orange = 0
    bg_color_shield = (15, 23, 42) # Should be similar
    
    # We also need to remove the exclamation mark from the center.
    # Exclamation mark is orange pixels roughly in the center
    center_x = s_w // 2
    center_y = s_h // 2
    
    # Find exact orange and remove exclamation mark
    for y in range(s_h):
        for x in range(s_w):
            r, g, b, a = s_pixels[x, y]
            # Is it orange? (Red > 150, Green > 100, Blue < 100)
            if r > 150 and g > 80 and b < 100:
                orange_color = (r, g, b)
                # If it's near the center horizontally and inside the shield, it's the exclamation mark
                # Shield width is about s_w. Center is s_w//2. 
                if abs(x - center_x) < s_w * 0.15 and y > s_h * 0.25 and y < s_h * 0.8:
                    s_pixels[x, y] = (bg_color_shield[0], bg_color_shield[1], bg_color_shield[2], 255) # overwrite with bg
    
    # 3. Color the isolated plane with the exact shield orange
    for y in range(icon_h):
        for x in range(icon_w):
            r, g, b, a = iso_pixels[x, y]
            if a > 0:
                iso_pixels[x, y] = (orange_color[0], orange_color[1], orange_color[2], a)
                
    # 4. Resize plane to fit inside the shield
    # The shield center area width is roughly 40% of total width
    target_w = int(s_w * 0.45)
    scale = target_w / icon_w
    target_h = int(icon_h * scale)
    
    plane_resized = isolated_plane.resize((target_w, target_h), Image.Resampling.LANCZOS)
    
    # 5. Paste the orange plane into the shield
    paste_x = (s_w - target_w) // 2
    paste_y = (s_h - target_h) // 2 - int(s_h * 0.05) # Slightly above absolute center looks better in shields
    
    shield_img.paste(plane_resized, (paste_x, paste_y), plane_resized)
    
    # Save it
    shield_img.save("admin_icon.png")
    print("Admin icon generated successfully!")

create_admin_icon()
