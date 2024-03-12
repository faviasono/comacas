import os
import glob
from tqdm import tqdm


def merge_txt_files(*, path: str, output_path: str | None = "output_merged.txt"):
    """
    Merge all the .txt files in a directory into a single .txt file.

    Args:
        path (str): The path to the directory containing the .txt files.
        output_path (str): The path where to save the merged .txt file

    Returns:
        str: The path to the merged .txt file.
    """

    # Get all the .txt files in the directory.
    txt_files = glob.glob(os.path.join(path, "*.txt"))

    rows: list[str] = []
    for txt_file in tqdm(txt_files):
        with open(txt_file, "r") as file:
            rows.extend(file.readlines())

    with open(os.path.join(path, output_path), "w") as merged_file:
        merged_file.writelines(rows)

    return os.path.join(path, output_path)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--path",
        type=str,
        default="samples/merge_txt_files",
        help="The path to the directory containing the .txt files.",
    )
    args = parser.parse_args()

    merge_txt_files(args.path)
