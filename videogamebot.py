import os
import json
import logging
from google import genai
from google.genai import types

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
client = genai.Client(api_key=GEMINI_API_KEY)

def generate_squad():
    logging.info("Step 1: Designing the squad and backstory...")
    
    text_prompt = (
        "You are designing a dark, edgy squad of 3 video game characters. "
        "Return ONLY a valid JSON object with exactly these 4 keys: "
        "'combined_lore': A 100-word gritty backstory describing the entire squad as a unit. "
        "'image_prompt_1': A highly detailed visual description of the first character for an AI image generator. "
        "'image_prompt_2': A highly detailed visual description of the second character. "
        "'image_prompt_3': A highly detailed visual description of the third character. "
        "Do not include any markdown formatting or code blocks, just output raw JSON."
    )

    try:
        text_response = client.models.generate_content(
            model='gemini-2.0-flash',
            contents=text_prompt,
        )
        
        raw_text = text_response.text.strip()
        if raw_text.startswith("```json"):
            raw_text = raw_text[7:-3].strip()
        elif raw_text.startswith("```"):
            raw_text = raw_text[3:-3].strip()
        
        squad_data = json.loads(raw_text)
        
        with open("squad_lore.txt", "w", encoding="utf-8") as f:
            f.write(squad_data['combined_lore'])
        logging.info("Successfully saved squad_lore.txt")

    except Exception as e:
        logging.error(f"Failed to generate or parse the text: {e}")
        return

    # ---------------------------------------------------------
    # STEP 2: GENERATE THE 3 IMAGES (Free Tier Multimodal)
    # ---------------------------------------------------------
    prompts = [
        squad_data['image_prompt_1'],
        squad_data['image_prompt_2'],
        squad_data['image_prompt_3']
    ]

    for index, img_prompt in enumerate(prompts, start=1):
        logging.info(f"Generating image {index} of 3...")
        try:
            # We use the multimodal model which accepts "Generate an image" instructions
            response = client.models.generate_content(
                model='gemini-3.1-flash-image-preview',
                contents=f"Generate a high-quality, gritty, 9:16 vertical video game character image. Description: {img_prompt}"
            )
            
            # Find the image data in the response parts
            image_saved = False
            for part in response.candidates[0].content.parts:
                if part.inline_data:
                    filename = f"squad_member_{index}.jpg"
                    with open(filename, "wb") as f:
                        f.write(part.inline_data.data)
                    logging.info(f"Successfully saved {filename}")
                    image_saved = True
                    break
            
            if not image_saved:
                logging.error(f"No image data returned for character {index}")

        except Exception as e:
            logging.error(f"Failed to generate image {index}: {e}")

if __name__ == "__main__":
    generate_squad()
