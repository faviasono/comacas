# take a directory as path and read all the .txt files and append the rows to a final .txt file

import os
import glob
from tqdm import tqdm


def merge_txt_files(path):
    """
    Merge all the .txt files in a directory into a single .txt file.

    Args:
        path (str): The path to the directory containing the .txt files.

    Returns:
        str: The path to the merged .txt file.
    """

    # Get all the .txt files in the directory.
    txt_files = glob.glob(os.path.join(path, "*.txt"))

    #
    rows: list[str] = []
    # Iterate over the .txt files and append the rows to the merged_file.
    for txt_file in tqdm(txt_files):
        with open(txt_file, "r") as file:
            rows.extend(file.readlines())

    with open(os.path.join(path, "merged.txt"), "w") as merged_file:
        merged_file.writelines(rows)

    # Return the path to the merged .txt file.
    return os.path.join(path, "merged.txt")


if __name__ == "__main__":
    # create a cli for the function above
    import argparse

    # create argparse and use default values
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--path",
        type=str,
        default="samples/merge_txt_files",
        help="The path to the directory containing the .txt files.",
    )
    args = parser.parse_args()

    merge_txt_files(args.path)
