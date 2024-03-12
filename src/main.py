from ocr_document.ocr_document import process_folder_images
from ocr_document.ocr_document import process_single_image
from ocr_document.ocr_document import to_html
from ocr_document.ocr_document import to_json
from typing import Optional

import os
import typer

app = typer.Typer()


@app.command()
def id2json(
    *,
    file_path: Optional[str] = None,
    output_path: Optional[str] = None,
    path_folder: Optional[str] = None,
    save_html: bool = False,
):
    """
    Convert an image to json or html using OCR + Mistral LLM for RAG Extraction
    """
    if not file_path and not path_folder:
        raise typer.BadParameter("Please provide either file_path or path_folder")
    if file_path and not os.path.exists(file_path):
        raise typer.BadParameter(f"File {file_path} does not exist")
    if path_folder and not os.path.isdir(path_folder):
        raise typer.BadParameter(f"{path_folder} is not a directory")

    if file_path:
        results = process_single_image(file_path)
    if path_folder:
        results = process_folder_images(path_folder)

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
def merge_txts(*, folder_path: str):
    pass



if __name__ == "__main__":
    app()
