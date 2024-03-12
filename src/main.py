import typer
from ocr_document.ocr_document import process_single_image, process_folder_images, to_html, to_json
import os
from typing import Optional

app = typer.Typer()

@app.command()
def greet(name: str = "World", enthusiastic: bool = False):
    """
    Greet the user.
    """
    greeting = "Hello" if not enthusiastic else "Helloooooo"
    message = f"{greeting}, {name}!"

    typer.echo(message)

@app.command()
def id2json(*, file_path: Optional[str] = None ,output_path: Optional[str] = None, path_folder: Optional[str] = None, save_html: bool = False):
    """
    Convert an image to json or html

    """
    #check either file_path or path_folder are not none
    if not file_path and not path_folder:
        raise typer.BadParameter("Please provide either file_path or path_folder")
    #check if file_path, output_path point to exististing files if they are not None
    if file_path and not os.path.exists(file_path):
        raise typer.BadParameter(f"File {file_path} does not exist")
    #check if path_folder is a directory
    if path_folder and not os.path.isdir(path_folder):
        raise typer.BadParameter(f"{path_folder} is not a directory")
    
    if file_path:
        results = process_single_image(file_path)
    if path_folder:
        results = process_folder_images(path_folder)

    if save_html:
        to_html(results, output_path if output_path else 'output.html')
    else:
        to_json(results, output_path if output_path else 'output.json')

if __name__ == "__main__":
    app()
