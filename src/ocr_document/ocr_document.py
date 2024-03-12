from ocr_document.constants import PROMPT_DOCUMENT
from openai import OpenAI
from PIL import Image
from transformers import pipeline
from transformers.utils import logging as HFLogging

import cv2
import json
import logging
import numpy as np
import os
import pytesseract
import re

HFLogging.set_verbosity(HFLogging.ERROR)
_LOGGER = logging.getLogger(__name__)

pipe = pipeline("object-detection", model="hustvl/yolos-tiny")
#TODO: modify with HF pipeline
client = OpenAI(base_url="http://localhost:1234/v1", api_key="not-needed")

def process_single_image(image_path: str):
    """ Process a single image"""
    image = Image.open(image_path)
    img2text = image_to_text(image)
    input_text = PROMPT_DOCUMENT.replace("{document}",_clean_text(img2text))
    result = get_result_llm(input_text)
    return [{
        'image_path': image_path,
        'texts': result
    }]

def process_folder_images(folder_path: str):
    """ Process all the images in a folder"""
    image_paths = [os.path.join(folder_path, file) for file in os.listdir(folder_path) if file.lower().endswith(('.jpg', '.jpeg', '.png'))]
    results = []
    for image_path in image_paths:
        _LOGGER.info(f"Processing image {image_path}")
        result = process_single_image(image_path)
        results.append({
                            'image_path': image_path,
                            'texts': result
                        })
    return results


def image_to_text(image: Image, res_yolo: dict | None = None) :
    """ Convert the image to text with preprocessing & tesseract"""
    _LOGGER.info("Converting image to text")
    thresholded_image = _preprocess_image(image,res_yolo)
    text = pytesseract.image_to_string(thresholded_image,config="--psm 12 --oem 3", nice=1)
    return text


def get_result_llm(prompt: str):
    """ Get the result from the LLM with a RAG prompt"""
    _LOGGER.info("Getting result from LLM")
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
    content = completion.choices[0].message.content
    return _parse_json_response(content)

def _crop_image(image: Image, res_yolo):
    """ Crop the image based on the yolo results and the 'book' label"""
    _LOGGER.info("Cropping image")
    bbox_card = [res for res in res_yolo if res["label"] == "book"]
    if bbox_card:
        xmin, ymin, xmax, ymax = bbox_card[0]["box"].values()
        return image.crop((xmin, ymin, xmax, ymax))
    return image

def _remove_faces(image: Image, res_yolo):
    """ Remove the faces from the image based on the yolo results and the 'person' label
    with a white rectangle"""
    _LOGGER.info("Removing faces")
    bbox_faces = [res for res in res_yolo if res["label"] == "person"]
    if bbox_faces:
        for bbox in bbox_faces:
            xmin, ymin, xmax, ymax = bbox["box"].values()
            # replace with white rectangle
            image.paste((255, 255, 255), (xmin, ymin, xmax, ymax))

    return image

def _preprocess_image(image: Image, res_yolo: dict | None = None):
    """ Process the image and return the thresholded image"""
    _LOGGER.info("Processing image")
    if res_yolo is None:
        res_yolo = pipe(image)
        image = _remove_faces(image, res_yolo)
        image = _crop_image(image, res_yolo).convert("L")
    else:
        image = _remove_faces(image, pipe(image)).convert("L")
    image = np.array(image)

    _, thresholded_image = cv2.threshold(image, 127, 255, cv2.THRESH_BINARY)
    return thresholded_image

def _clean_text(text):
    """ Clean the text with some heuristics"""
    cleaned_text = re.sub(r'\s+', ' ', text.strip())
    return cleaned_text


def _get_num_documents(res_yolo: dict) -> int:
    """ Get the number of documents in the image based on the yolo results"""
    bbox_documents = [res for res in res_yolo if res["label"] == "book"]
    return len(bbox_documents)



def to_json(results: list, output_path: str = 'output.json'):
    """ Save the results to a json file"""
    _LOGGER.info("Saving results to json")
    with open(output_path, 'w') as outfile:
        json.dump([res['texts'] for res in results if res['texts']], outfile)

def to_html(results: list, output_path: str = 'output.html'):
    """ Save the results to a html file"""
    _LOGGER.info("Saving results to html")
    html_content = "<html><body>"

    for result in results:
        html_content += f"<div style='display:flex;'><img src='{result['image_path']}' style='width:50%;'>"
        html_content += "<div style='width:50%; padding:10px;'>"

        if isinstance(result['texts'], list):
            for text in result['texts']:
            
                html_content += "<pre>"
                html_content += json.dumps(text, indent=4)
                html_content += "</pre>"
                html_content += "</div></div>"
        else:
                html_content += "<pre>"
                html_content += json.dumps(result['texts'], indent=4)
                html_content += "</pre>"
                html_content += "</div></div>"


    html_content += "</body></html>"

    # Save HTML file
    html_file_path = output_path
    with open(html_file_path, 'w') as html_file:
        html_file.write(html_content)
