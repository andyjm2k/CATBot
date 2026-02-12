"""
Script to create favicon files from CATBot_logo.png.
Generates multiple sizes for different devices and browsers.
Run from project root; outputs to project root.
"""
from pathlib import Path
from PIL import Image
import os

# Project root (parent of scripts directory)
PROJECT_ROOT = Path(__file__).resolve().parent.parent
# Input logo file in project root
LOGO_PATH = str(PROJECT_ROOT / 'CATBot_logo.png')

# Favicon sizes to generate (size, filename)
FAVICON_SIZES = [
    (16, 'favicon-16x16.png'),
    (32, 'favicon-32x32.png'),
    (48, 'favicon-48x48.png'),
    (180, 'apple-touch-icon.png'),  # Apple touch icon
    (192, 'android-chrome-192x192.png'),  # Android Chrome
    (512, 'android-chrome-512x512.png'),  # Android Chrome large
]

def create_favicon():
    """
    Create favicon files from the CATBot logo in multiple sizes.
    """
    # Check if logo file exists
    if not os.path.exists(LOGO_PATH):
        print(f"Error: {LOGO_PATH} not found!")
        return False
    
    # Open the original logo
    try:
        # Open and convert to RGBA if needed (handles transparency)
        logo = Image.open(LOGO_PATH)
        # Convert to RGBA to preserve transparency if present
        if logo.mode != 'RGBA':
            logo = logo.convert('RGBA')
        
        print(f"Original logo size: {logo.size}")
        
        # Create each favicon size
        for size, filename in FAVICON_SIZES:
            # Resize with high-quality resampling
            favicon = logo.resize((size, size), Image.Resampling.LANCZOS)
            # Save as PNG in project root
            favicon.save(str(PROJECT_ROOT / filename), 'PNG', optimize=True)
            print(f"Created: {filename} ({size}x{size})")
        
        # Create standard favicon.ico (multi-size ICO file)
        # ICO format can contain multiple sizes
        ico_sizes = [16, 32, 48]
        ico_images = []
        for size in ico_sizes:
            resized = logo.resize((size, size), Image.Resampling.LANCZOS)
            ico_images.append(resized)
        
        # Save as ICO (Pillow supports ICO format) in project root
        ico_images[0].save(str(PROJECT_ROOT / 'favicon.ico'), format='ICO', sizes=[(s, s) for s in ico_sizes])
        print("Created: favicon.ico (multi-size)")
        
        print("\nAll favicon files created successfully!")
        return True
        
    except Exception as e:
        print(f"Error creating favicons: {e}")
        return False

if __name__ == '__main__':
    create_favicon()
