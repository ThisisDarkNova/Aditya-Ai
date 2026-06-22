import os
from PIL import Image, ImageDraw

build_dir = 'build'
os.makedirs(build_dir, exist_ok=True)


# 1. Sidebar (Welcome and Finish pages): 164x314
# Background: Deep slate/charcoal dark color matching the app theme
sidebar = Image.new('RGB', (164, 314), color=(23, 23, 23)) 
draw_sidebar = ImageDraw.Draw(sidebar)

# Draw a subtle radial glow / tech grid lines in the background
# Draw circular HUD elements
for r in range(40, 160, 30):
    draw_sidebar.ellipse([(82 - r, 157 - r), (82 + r, 157 + r)], outline=(16, 185, 129, 30), width=1)

try:
    logo = Image.open('public/tray_icon.ico')
    logo = logo.convert('RGBA')
    logo.thumbnail((96, 96), Image.Resampling.LANCZOS)
    
    # Calculate centered position
    x = (164 - logo.width) // 2
    y = (314 - logo.height) // 2
    
    # Create an intermediate transparent canvas to handle RGBA pasting to RGB
    canvas = Image.new('RGBA', sidebar.size, (23, 23, 23, 255))
    # Draw circular background glow behind logo
    draw_glow = ImageDraw.Draw(canvas)
    for r in range(logo.width, 0, -2):
        alpha = int((1 - (r / logo.width)) * 25)  # Soft emerald glow
        draw_glow.ellipse([(82 - r, 157 - r), (82 + r, 157 + r)], fill=(16, 185, 129, alpha))
        
    canvas.paste(logo, (x, y), logo)
    sidebar = canvas.convert('RGB')
except Exception as e:
    print("Could not load icon for sidebar:", e)

sidebar.save(os.path.join(build_dir, 'sidebar.bmp'))
sidebar.save(os.path.join(build_dir, 'unsidebar.bmp'))

# 2. Header (Installation pages): 150x57
header = Image.new('RGB', (150, 57), color=(28, 28, 30)) # Dark header bar
draw_header = ImageDraw.Draw(header)

# Draw simple decorative horizontal line
draw_header.line([(0, 56), (150, 56)], fill=(16, 185, 129), width=1)

try:
    logo = Image.open('public/tray_icon.ico')
    logo = logo.convert('RGBA')
    logo.thumbnail((36, 36), Image.Resampling.LANCZOS)
    
    x = 150 - logo.width - 15
    y = (57 - logo.height) // 2
    
    canvas = Image.new('RGBA', header.size, (28, 28, 30, 255))
    canvas.paste(logo, (x, y), logo)
    header = canvas.convert('RGB')
except Exception as e:
    print("Could not load icon for header:", e)

header.save(os.path.join(build_dir, 'header.bmp'))
print("Successfully generated premium dark-glassmorphism NSIS installer UI assets!")

