
# OCR Document and Booking Reservation Management

This repository contains utilities to extract Demographic information from Passport or IDs using OCR and LLM.
Also, it provides some functionalities to create .txt files to upload to Allogiati-Web & Paytourist to register guests in owned B&Bs.

## Installation

#### Python Dependencies

To use the functionalities provided in this repository, you need to install the required dependencies. You can do this by running:

```
pip install -r requirements.txt
```

### LM Studio

The LLM used in this case [Mistral-7B-Instruct-v0.1-GGUF](https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.1-GGUF) is loaded in [LM Studio](https://lmstudio.ai) and then the server is started locally.



## OCR Document

### Usage

The `ocr_document` module provides functionalities to process images containing text and convert them to JSON or HTML format.

#### Command Line Interface

You can utilize the command line interface provided by `app`:

```bash
python main.py id2json FILE_PATH  [--output-path <output_path>] [--save-html]
```

- `FILE_PATH`: Path to the image file.
- `output_path`: Path to save the output file. Default is "output.json" if not provided.
- `save_html`: Flag to save the output as HTML. Default is False.

### Example

```bash
python main.py id2json images/sample.jpg --output-path result.json
```

## Merge TXT Files

The `merge_txt_files` module offers a utility to merge multiple text files into one.

### Usage

```bash
python main.py merge_txt FOLDER_PATH [--output-path <output_path>]
```

- `FOLDER_PATH`: Path to the folder containing text files to be merged.
- `output_path`: Path to save the merged output. Default is "output_merged.txt" if not provided.

### Example

```bash
python main.py merge_txt ./txt_files --output-path merged.txt
```

## Booking Reservation Management

The `booking_reservation` module provides utilities for managing booking reservations.

### Usage

#### JSON to TXT Conversion

```bash
python main.py json2txt JSON_FILE BOOKER [--property <property_number>] [--reservation-file <reservation_file>]
```

- `JSON_FILE`: Path to the JSON file.
- `BOOKER`: Name of the booker.
- `property`: Optional property number. Default is 2 if not provided. Either 1 or 2
- `reservation_file`: Path to the reservation file. If not provided, the newest file in `data/booking` directory will be chosen.

### Example

```bash
python main.py json2txt data/document.json John_Doe --property 2 --reservation-file data/booking/reservation.xls
```
