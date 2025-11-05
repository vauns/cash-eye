"""Generate test images with amount text for testing OCR"""
from PIL import Image, ImageDraw, ImageFont
import os

def create_amount_image(text, filename, size=(400, 200), font_size=60):
    """Create a simple image with amount text"""
    # Create white background
    img = Image.new('RGB', size, color='white')
    draw = ImageDraw.Draw(img)

    # Try to use a default font, fall back to basic if not available
    try:
        # Use a larger font size for better OCR
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", font_size)
    except:
        # Fallback to default font
        font = ImageFont.load_default()

    # Get text size and center it
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]

    position = ((size[0] - text_width) // 2, (size[1] - text_height) // 2)

    # Draw black text
    draw.text(position, text, fill='black', font=font)

    # Save image
    filepath = os.path.join(os.path.dirname(__file__), 'images', filename)
    img.save(filepath)
    print(f"Created: {filepath}")

def main():
    """Generate various test images"""
    test_cases = [
        ('¥100.00', 'amount_100.jpg'),
        ('¥1234.56', 'amount_1234.jpg'),
        ('$99.99', 'amount_dollar_99.jpg'),
        ('￥888.88', 'amount_yuan_888.jpg'),
        ('1,234.56', 'amount_comma_1234.jpg'),
        ('50.00', 'amount_50.jpg'),
        ('0.01', 'amount_0_01.jpg'),
        ('999999.99', 'amount_large.jpg'),
    ]

    for text, filename in test_cases:
        create_amount_image(text, filename)

    # Create a blurry/low quality image
    img = Image.new('RGB', (400, 200), color='white')
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 40)
    except:
        font = ImageFont.load_default()
    draw.text((100, 80), '¥123.45', fill='gray', font=font)

    # Make it blurry by resizing down and up
    img = img.resize((100, 50), Image.LANCZOS)
    img = img.resize((400, 200), Image.NEAREST)

    blurry_path = os.path.join(os.path.dirname(__file__), 'images', 'amount_blurry.jpg')
    img.save(blurry_path, quality=30)
    print(f"Created: {blurry_path}")

    # Create an image with no text
    img = Image.new('RGB', (400, 200), color='white')
    empty_path = os.path.join(os.path.dirname(__file__), 'images', 'no_text.jpg')
    img.save(empty_path)
    print(f"Created: {empty_path}")

    # Create different formats
    img = Image.new('RGB', (400, 200), color='white')
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 60)
    except:
        font = ImageFont.load_default()
    draw.text((100, 70), '¥200.00', fill='black', font=font)

    # PNG format
    png_path = os.path.join(os.path.dirname(__file__), 'images', 'amount_200.png')
    img.save(png_path, 'PNG')
    print(f"Created: {png_path}")

    # BMP format
    bmp_path = os.path.join(os.path.dirname(__file__), 'images', 'amount_300.bmp')
    img2 = Image.new('RGB', (400, 200), color='white')
    draw2 = ImageDraw.Draw(img2)
    draw2.text((100, 70), '¥300.00', fill='black', font=font)
    img2.save(bmp_path, 'BMP')
    print(f"Created: {bmp_path}")

    print("\nAll test images generated successfully!")

if __name__ == '__main__':
    main()
