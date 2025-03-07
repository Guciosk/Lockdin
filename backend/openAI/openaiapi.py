# openaiapi.py

import openai
from dotenv import load_dotenv
import os
from openai import OpenAI
import base64


load_dotenv()

client = OpenAI()
client.api_key = os.getenv("OPENAI_API_KEY")
dog_pic = "openAI/dog_pic.jpeg"


prompt = '''
    Confirm if this is a dog or not. and give a probability of it being a dog. if its over 80 percent say its a dog and if its under 20 percent say its not a dog. and also give the probability value
'''

def encode_image_to_base64(image_path):
    """Convert an image to base64 string"""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def analyze_image(image_path, custom_prompt="What's in this image?"):
    """
    Analyze an image using OpenAI's GPT-4 Vision model
    
    Args:
        image_path (str): Path to the image file
        custom_prompt (str): Question or prompt about the image
    
    Returns:
        str: The model's response about the image
    """
    try:
        # Check if the input is a local file path
        if os.path.isfile(image_path):
            # Encode the local image to base64
            base64_image = encode_image_to_base64(image_path)
            image_url = f"data:image/jpeg;base64,{base64_image}"
        else:
            # Treat it as a URL
            image_url = image_path

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": custom_prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": image_url
                            }
                        }
                    ]
                }
            ],
            max_tokens=300
        )
        
        return response.choices[0].message.content
    except Exception as e:
        return f"Error analyzing image: {str(e)}"

# Example usage
if __name__ == "__main__":
    # Test with local image
    result = analyze_image(dog_pic, prompt)
    print("Analysis of local image:")
    print(result)
    print("\n" + "-"*50 + "\n")
    
    # Test with URL
    test_image = "https://upload.wikimedia.org/wikipedia/commons/thumb/d/dd/Gfp-wisconsin-madison-the-nature-boardwalk.jpg/2560px-Gfp-wisconsin-madison-the-nature-boardwalk.jpg"
    result = analyze_image(test_image, "Describe the mood and atmosphere of this scene")
    print("Analysis of URL image:")
    print(result)

# get a response from chatgpt based on the image it sees
dog_response = analyze_image(dog_pic, prompt)
print(dog_response)