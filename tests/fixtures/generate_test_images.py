"""Generate test images with amount text for testing OCR"""
from PIL import Image, ImageDraw, ImageFont
import os
import platform


def get_system_fonts():
    """根据操作系统返回支持中文和符号的字体路径列表"""
    system = platform.system()

    if system == 'Windows':
        return [
            "C:/Windows/Fonts/msyh.ttc",     # 微软雅黑（推荐，最佳支持）
            "C:/Windows/Fonts/simhei.ttf",   # 黑体
            "C:/Windows/Fonts/simsun.ttc",   # 宋体
            "C:/Windows/Fonts/arial.ttf",    # Arial
        ]
    elif system == 'Linux':
        return [
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc",
            "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
        ]
    elif system == 'Darwin':  # macOS
        return [
            "/System/Library/Fonts/PingFang.ttc",
            "/Library/Fonts/Arial Unicode.ttf",
            "/System/Library/Fonts/Supplemental/Arial.ttf",
        ]
    else:
        print(f"Warning: Unknown system '{system}', using default fonts")
        return []


def load_font(font_size):
    """加载适合当前系统的字体"""
    font_paths = get_system_fonts()
    system = platform.system()

    for font_path in font_paths:
        try:
            font = ImageFont.truetype(font_path, font_size)
            print(f"✓ Using font: {font_path} (System: {system})")
            return font
        except Exception as e:
            continue

    # Fallback to default font
    print(f"⚠ Warning: No system fonts found, using default font (may not support all characters)")
    return ImageFont.load_default()


def create_amount_image(text, filename, size=(400, 200), font_size=60):
    """Create a simple image with amount text"""
    # Create white background
    img = Image.new('RGB', size, color='white')
    draw = ImageDraw.Draw(img)

    # Load system-appropriate font
    font = load_font(font_size)

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

    font = load_font(40)
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

    font = load_font(60)
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
