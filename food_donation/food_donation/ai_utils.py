from google import genai
from django.conf import settings

def get_gemini_client():
    return genai.Client(api_key=settings.GEMINI_API_KEY)

def analyze_food_item(image_path, food_name):
    """
    Example: Analyze a photo of donated food to check for 
    freshness or generate a description.
    """
    client = get_gemini_client()
    
    # You can pass both text and images to Gemini 1.5 Flash
    prompt = f"Identify this {food_name} and estimate its shelf life for donation. Is it safe to transport?"
    
    # Loading image from path
    with open(image_path, "rb") as f:
        image_data = f.read()

    response = client.models.generate_content(
        model="gemini-1.5-flash",
        contents=[prompt, {"mime_type": "image/jpeg", "data": image_data}]
    )
    
    return response.text