from PIL import Image
import pytesseract
import json
import re
import cv2
from constants import PROMPT_DOCUMENT
from openai import OpenAI
import numpy as np
from transformers import pipeline

pipe = pipeline("object-detection", model="hustvl/yolos-tiny")
client = OpenAI(base_url="http://localhost:1234/v1", api_key="not-needed")

def _crop_image(image: Image, res_yolo):
    bbox_card = [res for res in res_yolo if res["label"] == "book"]
    if bbox_card:
        xmin, ymin, xmax, ymax = bbox_card[0]["box"].values()
        return image.crop((xmin, ymin, xmax, ymax))
    return image

def _remove_faces(image: Image, res_yolo):
    bbox_faces = [res for res in res_yolo if res["label"] == "person"]
    if bbox_faces:
        for bbox in bbox_faces:
            xmin, ymin, xmax, ymax = bbox["box"].values()
            # replace with white rectangle
            image.paste((255, 255, 255), (xmin, ymin, xmax, ymax))

    return image

def process_image(image: Image, res_yolo: dict | None = None):
    if res_yolo is None:
        res_yolo = pipe(image)
        image = _remove_faces(image, res_yolo)
        image = _crop_image(image, res_yolo).convert("L")
    else:
        image = _remove_faces(image, pipe(image)).convert("L")
    image = np.array(image)


    # # Apply thresholding to enhance text
    _, thresholded_image = cv2.threshold(image, 127, 255, cv2.THRESH_BINARY)
    return thresholded_image

def image_to_text(image: Image, res_yolo: dict | None = None) :
    thresholded_image = process_image(image,res_yolo)
    text = pytesseract.image_to_string(thresholded_image,config="--psm 12 --oem 3", nice=1)
    return text

def clean_text(text):
    #Remove newlines and extra whitespaces
    cleaned_text = re.sub(r'\s+', ' ', text.strip())
    return cleaned_text

def get_result_llm(prompt: str):

    def _parse_json_response(text: str):
        if not text:
            return None
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            return text
    completion = client.chat.completions.create(
    model="not-used", 
    messages=[
        {"role": "system", "content": "You are a document reader bot that extract important demographics from a document. Data can be structured or unstructured and you don't have to make up the data."},
        {"role": "user", "content": f"{prompt}"},
    ],
    temperature=0.2,
    )
    content =  completion.choices[0].message.content
    return _parse_json_response(content)


def get_num_documents(res_yolo: dict) -> int:
    bbox_documents = [res for res in res_yolo if res["label"] == "book"]
    return len(bbox_documents)


#create a cli with argparser
if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--path', type=str, default='samples/documents/document3.jpg', help='Path to the image')
    args = parser.parse_args()

    image = Image.open(args.path)
    res_yolo = pipe(image)
    texts: list = []
    if get_num_documents(res_yolo) > 1:
        for res in res_yolo:
            if res["label"] == "book":
                xmin, ymin, xmax, ymax = res["box"].values()
                image = image.crop((xmin, ymin, xmax, ymax))
                t = image_to_text(image, res_yolo)
                texts.append(t)
    else:
        texts.append(image_to_text(image))
 

        
    text = "\n".join(texts)
    input_text = PROMPT_DOCUMENT.replace("{document}",clean_text(text))

    result = get_result_llm(input_text)
    print(result)
    
    