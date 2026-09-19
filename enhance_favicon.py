from PIL import Image, ImageDraw
import math

def process_favicon():
    img = Image.open('favicon.png').convert('RGBA')
    width, height = img.size
    
    # 1. Identify background color
    bg_color = (15, 23, 42)
    
    # 2. Find bounding box of the airplane (everything not bg_color and not the bottom gray bar)
    # The gray bar is at the bottom, so we ignore y > 75 (assuming bottom is just gray bar)
    min_x = width
    min_y = height
    max_x = 0
    max_y = 0
    
    pixels = img.load()
    
    for y in range(height - 15): # Ignore bottom 15 pixels just in case
        for x in range(width):
            r, g, b, a = pixels[x, y]
            # If it's significantly different from background (i.e. it's the blue line)
            dist = math.sqrt((r-bg_color[0])**2 + (g-bg_color[1])**2 + (b-bg_color[2])**2)
            if dist > 30: # It's part of the icon
                if x < min_x: min_x = x
                if x > max_x: max_x = x
                if y < min_y: min_y = y
                if y > max_y: max_y = y
                
    # Crop the icon
    icon_w = max_x - min_x + 1
    icon_h = max_y - min_y + 1
    icon = Image.new('RGBA', (icon_w, icon_h), (0,0,0,0))
    icon_pixels = icon.load()
    
    for y in range(min_y, max_y + 1):
        for x in range(min_x, max_x + 1):
            r, g, b, a = pixels[x, y]
            dist = math.sqrt((r-bg_color[0])**2 + (g-bg_color[1])**2 + (b-bg_color[2])**2)
            if dist > 30:
                # Keep the original blue color, but make it fully opaque
                icon_pixels[x - min_x, y - min_y] = (r, g, b, 255)
                
    # 3. Create a beautiful new 128x128 favicon
    size = 128
    new_favicon = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(new_favicon)
    
    # Draw a solid white circle background for maximum visibility
    draw.ellipse((4, 4, size-4, size-4), fill=(255, 255, 255, 255))
    
    # Resize the extracted icon to fit nicely in the circle
    target_icon_size = 72
    scale = min(target_icon_size / icon_w, target_icon_size / icon_h)
    new_icon_w = int(icon_w * scale)
    new_icon_h = int(icon_h * scale)
    
    icon_resized = icon.resize((new_icon_w, new_icon_h), Image.Resampling.LANCZOS)
    
    # Paste the icon into the center
    paste_x = (size - new_icon_w) // 2
    paste_y = (size - new_icon_h) // 2
    new_favicon.paste(icon_resized, (paste_x, paste_y), icon_resized)
    
    new_favicon.save('favicon.png')
    print("Favicon updated successfully!")

process_favicon()
