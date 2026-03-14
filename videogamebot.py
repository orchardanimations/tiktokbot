import os
import json
import logging
from google import genai
from google.genai import types

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
client = genai.Client(api_key=GEMINI_API_KEY)

def generate_squad():
    logging.info("Step 1: Asking Gemini to design the squad...")
    
    # ---------------------------------------------------------
    # STEP 1: GENERATE THE LORE AND IMAGE PROMPTS
    # ---------------------------------------------------------
    # We ask for strict JSON so Python can easily separate the text from the visual prompts
    text_prompt = (
        "You are designing a dark, edgy squad of 3 video game characters "
        "(e.g., terrifying Ghost-type Pokémon variants, or a rogue, mechanized Sonic mercenary team). "
        "Return ONLY a valid JSON object with exactly these 4 keys: "
        "'combined_lore': A 100-word gritty backstory describing the entire squad as a unit. "
        "'image_prompt_1': A highly detailed visual description of the first character for an AI image generator. "
        "'image_prompt_2': A highly detailed visual description of the second character. "
        "'image_prompt_3': A highly detailed visual description of the third character. "
        "Do not include any markdown formatting or code blocks, just output the raw JSON."
    )

    try:
        text_response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=text_prompt,
        )
        
        # Clean the response just in case the AI added markdown backticks
        raw_text = text_response.text.strip()
        if raw_text.startswith("```json"):
            raw_text = raw_text[7:-3].strip()
        elif raw_text.startswith("```"):
            raw_text = raw_text[3:-3].strip()
        
        # Parse the JSON
        squad_data = json.loads(raw_text)
        
        # Save the overarching story
        with open("squad_lore.txt", "w", encoding="utf-8") as f:
            f.write(squad_data['combined_lore'])
        logging.info("Successfully saved squad_lore.txt")

    except Exception as e:
        logging.error(f"Failed to generate or parse the text: {e}")
        return

    # ---------------------------------------------------------
    # STEP 2: GENERATE THE 3 IMAGES IN A LOOP
    # ---------------------------------------------------------
    prompts = [
        squad_data['image_prompt_1'],
        squad_data['image_prompt_2'],
        squad_data['image_prompt_3']
    ]

    for index, img_prompt in enumerate(prompts, start=1):
        logging.info(f"Generating image {index} of 3...")
        try:
            image_response = client.models.generate_images(
                model='imagen-4.0-generate-001',
                prompt=img_prompt,
                config=types.GenerateImagesConfig(
                    number_of_images=1,
                    aspect_ratio="9:16", # Vertical for TikTok
                    output_mime_type="image/jpeg"
                )
            )
            
            # Save each image with a sequential number
            filename = f"squad_member_{index}.jpg"
            for generated_image in image_response.generated_images:
                with open(filename, "wb") as f:
                    f.write(generated_image.image.image_bytes)
            logging.info(f"Successfully saved {filename}")

        except Exception as e:
            logging.error(f"Failed to generate image {index}: {e}")

if __name__ == "__main__":
    generate_squad()
