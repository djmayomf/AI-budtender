from PIL import Image
from io import BytesIO
import os
from flask import request, Response
from functools import wraps

class ImageOptimizer:
    def __init__(self, quality=85, max_width=1200):
        self.quality = quality
        self.max_width = max_width
        self.supported_formats = {'jpg', 'jpeg', 'png', 'webp'}

    def optimize_image(self, image_data: bytes, format: str) -> bytes:
        """Optimize image for web delivery"""
        try:
            img = Image.open(BytesIO(image_data))
            
            # Convert RGBA to RGB if necessary
            if img.mode == 'RGBA':
                background = Image.new('RGB', img.size, (255, 255, 255))
                background.paste(img, mask=img.split()[3])
                img = background
            
            # Resize if too large
            if img.width > self.max_width:
                ratio = self.max_width / img.width
                new_height = int(img.height * ratio)
                img = img.resize((self.max_width, new_height), Image.LANCZOS)
            
            # Convert to WebP if supported
            if 'image/webp' in request.accept_mimetypes:
                format = 'webp'
            
            # Save optimized image
            output = BytesIO()
            img.save(output, format=format, quality=self.quality, optimize=True)
            return output.getvalue()
            
        except Exception as e:
            print(f"Image optimization failed: {str(e)}")
            return image_data

def optimize_images(f):
    """Middleware to optimize image responses"""
    optimizer = ImageOptimizer()
    
    @wraps(f)
    def wrapped(*args, **kwargs):
        response = f(*args, **kwargs)
        
        # Check if response is an image
        if (response.mimetype and 
            response.mimetype.startswith('image/') and 
            response.mimetype.split('/')[-1] in optimizer.supported_formats):
            
            optimized_data = optimizer.optimize_image(
                response.get_data(),
                response.mimetype.split('/')[-1]
            )
            
            return Response(
                optimized_data,
                mimetype=response.mimetype,
                headers={
                    'Cache-Control': 'public, max-age=31536000',
                    'Content-Length': len(optimized_data)
                }
            )
            
        return response
    
    return wrapped 