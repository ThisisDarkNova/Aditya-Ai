import os
import google.generativeai as genai

# Read API key from environment variable (user will need to provide this via .env)
api_key = os.environ.get("GEMINI_API_KEY")

if api_key:
    genai.configure(api_key=api_key)
    # Using Gemini 1.5 Pro as requested for maximum cognitive intelligence
    model = genai.GenerativeModel('gemini-1.5-pro')
else:
    model = None
    print("[WARNING] GEMINI_API_KEY not found in environment variables. Cognitive capabilities limited.")

def generate_response(prompt: str, context: list = None) -> str:
    """
    Generates a response from Gemini 1.5 Pro.
    Maintains memory-aware conversational context if provided.
    """
    if not model:
        return "I am ADITYA. My cognitive connection to Gemini is offline because the API key is missing. Please provide it in the .env file."
    
    try:
        # Create a new chat session if context is provided
        if context:
            chat = model.start_chat(history=context)
            response = chat.send_message(prompt)
        else:
            response = model.generate_content(prompt)
            
        return response.text
    except Exception as e:
        return f"Cognitive Processing Error: {str(e)}"
