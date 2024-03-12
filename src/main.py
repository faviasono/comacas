from ocr_document.ocr_document import process_folder_images
from ocr_document.ocr_document import process_single_image
from ocr_document.ocr_document import to_html
from ocr_document.ocr_document import to_json
from merge_txt_files.merge_txt_files import merge_txt_files
from booking_reservation.manage_reservaton import json2alloggiati
from typing import Optional

import os
import glob
import typer

app = typer.Typer()


@app.command()
def id2json(
    file_path: Optional[str] = None,
    output_path: Optional[str] = None,
    folder_path: Optional[str] = None,
    save_html: bool = False,
):
    """
    Convert an image to json or html using OCR + Mistral LLM for RAG Extraction
    """
    if not file_path and not folder_path:
        raise typer.BadParameter("Please provide either file_path or folder_path")
    if file_path and not os.path.exists(file_path):
        raise typer.BadParameter(f"File {file_path} does not exist")
    if folder_path and not os.path.isdir(folder_path):
        raise typer.BadParameter(f"{folder_path} is not a directory")

    if file_path:
        results = process_single_image(image_path=file_path)
    if folder_path:
        results = process_folder_images(folder_path=folder_path)

    out_file: str = output_path if output_path else "output.html" if save_html else "output.json"
    if save_html:
        to_html(
            results,
            out_file,
        )
    else:
        to_json(
            results,
            out_file,
        )

    typer.echo(f"Output file saved at {out_file}")


@app.command()
def merge_txt(folder_path: str, output_path: Optional[str] = "output_merged.txt"):
    """Merge .txt files by appending one row after the other"""
    if not folder_path or not os.path.isdir(folder_path):
        raise typer.BadParameter("Please provide a valid path folder")
    if not isinstance(output_path, str) or not output_path.endswith(".txt"):
        raise typer.BadParameter("Output Path must be a string with .txt as format")

    merged_document: str = merge_txt_files(path=folder_path, output_path=output_path)
    typer.echo(f"File saved at {merged_document}")


@app.command()
def json2txt(
    json_file: str,
    booker: str,
    property: Optional[int] = 2,
    reservation_file: Optional[str] = None,
):
    """ Transform a json-document to txt ready to upload using .xls reservation Booking data"""
    if not os.path.exists(json_file):
        raise typer.BadParameter("Please provide a valid json file")
    if reservation_file and os.path.exists(reservation_file):
        raise typer.BadParameter("Please provide a valid reservation file")
    if not reservation_file:
        # take the newest file in data/booking based on the name
        txt_files: list[str] = glob.glob(os.path.join("data/booking", "*.xls"))
        txt_files.sort(reverse=True)
        reservation_file = txt_files[0]

    formatted_docs: str = json2alloggiati(
        json_file=json_file, reservation_file=reservation_file, property=property, booker=booker
    )

    out_file: str = f"{formatted_docs[2:12].replace('/','_')}_com_a_cas_{property}.txt"

    with open(out_file, "w") as f:
        f.write(formatted_docs)
    typer.echo(f"File saved at {out_file}")


if __name__ == "__main__":
    app()
