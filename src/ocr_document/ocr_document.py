from PIL import Image
import pytesseract
import json
import re
from constants import PROMPT_DOCUMENT
from openai import OpenAI

client = OpenAI(base_url="http://localhost:1234/v1", api_key="not-needed")
PATTERN_DATES = "\b\d{2}\.\d{2}\.\d{4}\b"

#create a function that reads an image and extract the text
def read_image(image_path):
    image = Image.open(image_path)
    text = pytesseract.image_to_string(image,config="--psm 12 --oem 3", nice=0)
    return text

def clean_text(text):
    
    # Remove newlines and extra whitespaces
    #cleaned_text = re.sub(r'\s+', ' ', text.strip())
    # Remove sentences with two or fewer characters
    cleaned_text = re.sub(r'\b\w{1,2}\b', '', text)
    
    # # Remove specific single characters with spaces
    # cleaned_text = re.sub(r'\s?[=\\\'\(\)\!\‘\;\:\'\/\°]\s?', '', cleaned_text)

    return cleaned_text

def get_result_llm(prompt: str):

    def _parse_json_response(text: str):
        if not text:
            return None
        if text[0] == "[" and text[-1] == "]":
            return json.loads(text[0])
        if text[0] == "{" and text[-1] == "}":
            return json.loads(text)
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            return text
    completion = client.chat.completions.create(
    model="not-used", 
    messages=[
        {"role": "system", "content": "Focus on the content. It's a document with some informaition of a guest. I need to extract information"},
        {"role": "user", "content": f"{prompt}"},
    ],
    temperature=0.4,
    )
    content =  completion.choices[0].message.content
    return _parse_json_response(content)


#create a cli with argparser
if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--path', type=str, default='samples/documents/document4.jpg', help='Path to the image')
    args = parser.parse_args()
    text = read_image(args.path)
    input_text = PROMPT_DOCUMENT.replace("{document}",clean_text(text))

    print(input_text)
    result = get_result_llm(input_text)
    print(result)
    
    
