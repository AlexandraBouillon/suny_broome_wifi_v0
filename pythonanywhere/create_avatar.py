from PIL import Image, ImageDraw, ImageFont
import os

def create_avatar():
    # Create directory structure if it doesn't exist
    os.makedirs('static/images', exist_ok=True)
    
    # Create a 100x100 image with gold background
    img = Image.new('RGB', (100, 100), color='#edb31f')
    draw = ImageDraw.Draw(img)
    
    # Use default font since we can't guarantee system fonts
    font = ImageFont.load_default()
    
    # Draw "TJ" in white
    text = "TJ"
    text_bbox = draw.textbbox((0, 0), text, font=font)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]
    
    # Center the text
    x = (100 - text_width) // 2
    y = (100 - text_height) // 2
    
    # Draw the text
    draw.text((x, y), text, fill='white', font=font)
    
    # Save the image
    avatar_path = 'static/images/tj-avatar.png'
    img.save(avatar_path)
    
    # Set permissions
    os.chmod(avatar_path, 0o644)
    os.chmod('static/images', 0o755)
    
    print(f"Avatar created at: {avatar_path}")

if __name__ == "__main__":
    create_avatar()