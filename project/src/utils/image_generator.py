"""
Image Generator module
Provides AI image generation functionality for the application
"""
import os
import openai
from src.utils.logger import get_logger

class ImageGenerator:
    """Image Generator class for creating task-related images"""
    def __init__(self):
        self.logger = get_logger()
    
    def generate_image(self, prompt, size="512x512"):
        """Generate an image based on the prompt"""
        try:
            response = openai.Image.create(
                prompt=prompt,
                n=1,
                size=size
            )
            
            # Return the URL of the generated image
            return response['data'][0]['url']
            
        except Exception as e:
            self.logger.error(f"Error generating image: {e}")
            return None