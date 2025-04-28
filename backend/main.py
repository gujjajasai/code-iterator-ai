

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import google.generativeai as genai # Import Google AI library
import os
from dotenv import load_dotenv
from fastapi.responses import FileResponse
import json # Import json library

# Load environment variables
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if GOOGLE_API_KEY:
    print("Loaded Google API Key: ", GOOGLE_API_KEY[:5] + "...") # Print only prefix for security
else:
    print("ERROR: GOOGLE_API_KEY environment variable not set!")

# Initialize FastAPI app
app = FastAPI()

# Allow CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure the Google AI Client (do this once globally is fine if key doesn't change)
# Or configure it within the endpoint if preferred
try:
    if GOOGLE_API_KEY:
        genai.configure(api_key=GOOGLE_API_KEY)
    else:
        # App will run, but endpoint will fail if key wasn't loaded
        print("Warning: Google API Key not configured due to missing environment variable.")
except Exception as config_error:
     print(f"Error configuring Google AI SDK: {config_error}")
     # Depending on your strategy, you might want the app to fail startup here


# Define the request body (remains the same)
class CodeRequest(BaseModel):
    selected_code: str
    user_prompt: str

# Root route
@app.get("/")
async def read_root():
    return {"message": "Welcome to the AI Code Iterator API (Using Google AI)"}

# Favicon (optional)
@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    static_file_path = os.path.join(os.path.dirname(__file__), "static/favicon.ico")
    if os.path.exists(static_file_path):
        return FileResponse(static_file_path)
    else:
        raise HTTPException(status_code=404, detail="Favicon not found")


# Suggest improved code
@app.post("/suggest")
async def suggest_code_improvement(request: CodeRequest):
    # Check if the API key was loaded and configured correctly
    if not GOOGLE_API_KEY:
         raise HTTPException(status_code=500, detail="Google API key not configured on the server.")
    # Re-check configuration in case it failed silently during startup
   


    try:
        # --- Google AI Specific Setup ---
        # Select the model
        # For text tasks, 'gemini-pro' is a strong choice.
        # Use 'gemini-1.5-flash' for speed or 'gemini-1.5-pro' for capability if available/needed
        model = genai.GenerativeModel('gemini-1.5-flash-latest')

        # --- Prepare the prompt for Google AI ---
        # The prompt structure asking for JSON can remain similar.
        # Gemini generally works well with direct instructions.
        prompt = (
            f"You are an expert AI assistant specializing in game development code improvement. "
            f"Analyze the following code snippet:\n\n```\n{request.selected_code}\n```\n\n"
            f"The user wants to apply this change: '{request.user_prompt}'.\n\n"
            f"Please provide:\n"
            f"1. An 'explanation' of the changes you made and why, focusing on game development best practices if applicable.\n"
            f"2. The complete 'suggested_code' block reflecting the changes.\n\n"
            f"Respond ONLY with a valid JSON object containing two keys: 'explanation' (string) and 'suggested_code' (string). "
            f"Ensure the suggested_code is formatted correctly as a single string, including necessary indentation and newlines (use \\n)."
            f"Example JSON format:\n"
            f"{{\n"
            f'  "explanation": "Refactored the loop for better readability and performance by using enumerate.",\n'
            f'  "suggested_code": "def example():\\n    items = [1, 2, 3]\\n    for i, item in enumerate(items):\\n        print(f\\"Item {{i}}: {{item}}\\")"\n'
            f"}}"
        )

        # --- Generation Configuration (Optional but recommended) ---
        generation_config = genai.types.GenerationConfig(
            temperature=0.2, # Lower temperature for more deterministic code generation
            # max_output_tokens=2048 # Optional: limit response size
        )

        # --- Safety Settings (Important for Google AI) ---
        # Adjust thresholds as needed (BLOCK_NONE, BLOCK_LOW_AND_ABOVE, BLOCK_MEDIUM_AND_ABOVE, BLOCK_ONLY_HIGH)
        safety_settings = [
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
        ]

        # --- Make the API Call to Google AI ---
        response = await model.generate_content_async( # Use async version
            prompt,
            generation_config=generation_config,
            safety_settings=safety_settings
        )

        # --- Process the Response ---
        # Check for safety blocks or other issues before accessing text
        if not response.candidates:
             block_reason = "Unknown"
             safety_ratings = []
             try:
                 # Attempt to access prompt feedback for more details
                 block_reason = response.prompt_feedback.block_reason
                 safety_ratings = response.prompt_feedback.safety_ratings
             except Exception:
                 pass # Ignore if feedback cannot be accessed
             print(f"Prompt/Response Blocked. Reason: {block_reason}, Ratings: {safety_ratings}")
             raise HTTPException(status_code=400, detail=f"Content generation blocked due to safety settings. Reason: {block_reason}")

        # Extract the text content
        try:
            ai_message_content = response.text
        except ValueError as e:
             # Handle cases where accessing .text fails (e.g., finish reason is SAFETY)
             print(f"Error accessing response text: {e}")
             finish_reason = "Unknown"
             safety_ratings = []
             try:
                finish_reason = response.candidates[0].finish_reason
                safety_ratings = response.candidates[0].safety_ratings
             except Exception:
                 pass # Ignore if candidate info cannot be accessed
             raise HTTPException(status_code=500, detail=f"Failed to get valid text from AI. Finish Reason: {finish_reason}, Safety: {safety_ratings}")


        # Attempt to parse the AI's response as JSON (same logic as before)
        try:
            # Sometimes the model might add ```json ... ``` markers, try to strip them
            ai_message_content_cleaned = ai_message_content.strip()
            if ai_message_content_cleaned.startswith("```json"):
                ai_message_content_cleaned = ai_message_content_cleaned[7:]
            if ai_message_content_cleaned.endswith("```"):
                ai_message_content_cleaned = ai_message_content_cleaned[:-3]

            parsed_response = json.loads(ai_message_content_cleaned.strip())

            # Validate the structure
            if 'explanation' not in parsed_response or 'suggested_code' not in parsed_response:
                 raise ValueError("Missing 'explanation' or 'suggested_code' in AI response")

            # Return the parsed suggestion
            return parsed_response

        except (json.JSONDecodeError, ValueError) as json_error:
             print(f"Error parsing AI response as JSON: {json_error}")
             print(f"Raw AI response:\n{ai_message_content}")
             # Fallback: Return the raw response if JSON parsing fails, but indicate the issue
             # Important: Don't send potentially unsafe raw AI content directly if safety was a concern
             return {
                 "explanation": f"Error: AI did not return valid JSON. Raw response was:\n{ai_message_content}",
                 "suggested_code": request.selected_code # Return original code on failure
             }

    # --- Specific Google API Error Handling (Optional but good) ---
    # except google.api_core.exceptions.PermissionDenied as e:
    #     print(f"Google AI Permission Denied: {e}")
    #     raise HTTPException(status_code=403, detail=f"Google AI Permission Denied: Check API Key and permissions.")
    # except google.api_core.exceptions.ResourceExhausted as e:
    #      print(f"Google AI Quota Error: {e}")
    #      raise HTTPException(status_code=429, detail=f"Google AI Quota Exceeded: {e}")
    # --- General Error Handling ---
    except Exception as e:
        # General server error
        print(f"An unexpected error occurred: {e}")
        # Be careful about returning raw exception details to the client in production
        raise HTTPException(status_code=500, detail=f"An internal server error occurred: {type(e).__name__}")