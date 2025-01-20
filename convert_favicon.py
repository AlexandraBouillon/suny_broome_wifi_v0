from PIL import Image
import os

# Create PNG version
webp_path = 'static/images/cropped-B-Lettermark-Gold-32x32.webp'
img = Image.open(webp_path)
img.save('static/images/favicon.png', 'PNG')

# Create ICO version
img.save('static/images/favicon.ico', format='ICO', sizes=[(32, 32)])