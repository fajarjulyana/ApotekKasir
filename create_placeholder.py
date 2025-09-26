
"""
Script untuk membuat gambar placeholder
"""
from PIL import Image, ImageDraw, ImageFont
import os

def create_no_image_placeholder():
    """Buat gambar placeholder untuk produk yang tidak ada gambar"""
    # Create static directories
    os.makedirs('static/images', exist_ok=True)
    os.makedirs('static/product', exist_ok=True)
    os.makedirs('static/logo', exist_ok=True)
    
    # Create a simple placeholder image
    img = Image.new('RGB', (200, 200), color='#f8f9fa')
    draw = ImageDraw.Draw(img)
    
    # Draw border
    draw.rectangle([10, 10, 190, 190], outline='#dee2e6', width=2)
    
    # Draw text
    try:
        # Try to use default font
        font = ImageFont.load_default()
    except:
        font = None
    
    text = "Tidak ada\ngambar"
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    position = ((200 - text_width) // 2, (200 - text_height) // 2)
    draw.text(position, text, fill='#6c757d', font=font, align='center')
    
    # Save placeholder
    img.save('static/images/no-image.png')
    print("Placeholder image created at static/images/no-image.png")

if __name__ == "__main__":
    create_no_image_placeholder()
