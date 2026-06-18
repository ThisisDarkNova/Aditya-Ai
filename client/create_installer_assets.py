import os
from PIL import Image, ImageDraw

build_dir = 'build'
os.makedirs(build_dir, exist_ok=True)

# 1. Sidebar (Welcome and Finish pages): 164x314
sidebar = Image.new('RGB', (164, 314), color=(245, 245, 247)) # Apple sleek light gray

try:
    logo = Image.open('public/tray_icon.ico')
    logo = logo.convert('RGBA')
    logo.thumbnail((120, 120), Image.Resampling.LANCZOS)
    
    # Calculate centered position
    x = (164 - logo.width) // 2
    y = (314 - logo.height) // 2
    
    # Create an intermediate transparent canvas to handle RGBA pasting to RGB
    canvas = Image.new('RGBA', sidebar.size, (245, 245, 247, 255))
    canvas.paste(logo, (x, y), logo)
    sidebar = canvas.convert('RGB')
except Exception as e:
    print("Could not load icon for sidebar:", e)

sidebar.save(os.path.join(build_dir, 'sidebar.bmp'))
sidebar.save(os.path.join(build_dir, 'unsidebar.bmp'))

# 2. Header (Installation pages): 150x57
header = Image.new('RGB', (150, 57), color=(255, 255, 255)) # Pure white header

try:
    logo = Image.open('public/tray_icon.ico')
    logo = logo.convert('RGBA')
    logo.thumbnail((40, 40), Image.Resampling.LANCZOS)
    
    x = 150 - logo.width - 15
    y = (57 - logo.height) // 2
    
    canvas = Image.new('RGBA', header.size, (255, 255, 255, 255))
    canvas.paste(logo, (x, y), logo)
    header = canvas.convert('RGB')
except Exception as e:
    print("Could not load icon for header:", e)

header.save(os.path.join(build_dir, 'header.bmp'))
print("Successfully generated premium NSIS installer UI assets!")
