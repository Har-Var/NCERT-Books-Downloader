import os
import requests
import zipfile
from PIL import Image
from pypdf import PdfWriter
import re
import shutil
import json


def fetch_json_data(jpath):
    """
    Fetches JSON data from a given file path.

    Args:
        jpath (str): File path to the JSON data

    Returns:
        dict: JSON data
    """
    with open(jpath, "r") as j:
        json_data = json.load(j)
    return json_data


def get_classes(data):
    """
    Returns a list of unique class numbers from the given JSON data.

    Args:
        data (list): List of JSON objects

    Returns:
        list: List of unique class numbers
    """
    class_list = []
    for item in data:
        curr_class = item.get("class")
        if curr_class not in class_list:
            class_list.append(curr_class)
        else:
            pass
    return class_list


def get_subjects(data, classno):
    """
    Returns a list of unique subject names from the given JSON data for a given class number.

    Args:
        data (list): List of JSON objects
        classno (int): Class number

    Returns:
        list: List of unique subject names
    """
    subjects = []
    for item in data:
        if item.get("class") == classno:
            subjects.append(item.get("subject"))
    return subjects


def get_books(data, classno, subname):
    """
    Returns a list of book titles for a given class number and subject name from the JSON data.

    Args:
        data (list): List of JSON objects representing the books data.
        classno (int): Class number to filter the books.
        subname (str): Subject name to filter the books.

    Returns:
        list: List of book titles that match the specified class number and subject name.
    """
    book_list = []
    for item in data:
        if item.get("class") == classno and item.get("subject") == subname:
            for books in item.get("books"):
                book_list.append(books.get("title"))
    return book_list


def get_link(data, classno, subname, bookname):
    """
    Returns the download link, page link and book code for a given class number, subject name and book title.

    Args:
        data (list): List of JSON objects representing the books data.
        classno (int): Class number to filter the books.
        subname (str): Subject name to filter the books.
        bookname (str): Book title to filter the books.

    Returns:
        tuple: Tuple containing the download link, page link and book code for the given book.
    """
    for item in data:
        if item.get("class") == classno and item.get("subject") == subname:
            for books in item.get("books"):
                if books.get("title") == bookname:
                    download_link = books.get("dlink")
                    page_link = books.get("link")
                    book_code = books.get("code")
    return download_link, page_link, book_code


def download_file(link, dpath):
    """
    Downloads a file from a given URL and saves it to a specified directory.

    Args:
        link (str): The URL of the file to download.
        dpath (str): The directory path where the downloaded file will be saved.

    Returns:
        str: The full file path where the downloaded file is saved if successful.
        None: If the download fails.
    """
    # Ensure the save path exists
    if not os.path.exists(dpath):
        os.makedirs(dpath)

    # Get the file name from the download link
    file_name = link.split("/")[-1]
    # Create the full path to save the file
    file_path = os.path.join(dpath, file_name)
    # Download the file content
    response = requests.get(link)

    # Check if the request was successful
    if response.status_code == 200:
        # Write the content to the file
        with open(file_path, "wb") as file:
            file.write(response.content)
        # print(f"File downloaded successfully and saved to {file_path}")
        return file_path
    else:
        print(f"Failed to download file. Status code: {response.status_code}")
        return None


def unzip_file(zip_path, extract_to):
    """
    Unzips a zip file to a specified directory.

    Args:
        zip_path (str): The path to the zip file to be unzipped.
        extract_to (str): The directory path where the unzipped content will be saved.

    Returns:
        str: The full path where the unzipped content is saved if successful.
        None: If the unzipping fails.
    """
    # Extract the file name without extension to create the extraction folder name
    file_name = os.path.basename(zip_path)
    folder_name = os.path.splitext(file_name)[0]
    extraction_path = os.path.join(extract_to, folder_name)

    # Ensure the extraction path exists
    if not os.path.exists(extraction_path):
        os.makedirs(extraction_path)

    # Unzip the file
    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        zip_ref.extractall(extraction_path)
    # print(f"File unzipped successfully and saved to {extraction_path}")
    return extraction_path


def convert_images_to_pdfs(directory):
    """
    Converts all images in a given directory to PDFs and saves them in the same directory.

    Args:
        directory (str): The directory path where the images are located.

    Returns:
        None
    """
    for file_name in os.listdir(directory):
        if file_name.endswith((".jpg", ".png", ".jpeg")):
            image_path = os.path.join(directory, file_name)
            image = Image.open(image_path)
            pdf_path = os.path.join(directory, os.path.splitext(file_name)[0] + ".pdf")
            image.save(pdf_path, "PDF", resolution=100.0)
            print(f"Converted {image_path} to {pdf_path}")


def merge_pdfs(directory, output_path):
    """
    Merges all PDF files in a given directory into a single PDF file.

    Args:
        directory (str): The directory path where the PDF files are located.
        output_path (str): The file path where the merged PDF will be saved.

    Returns:
        None
    """
    pdf_files = [f for f in os.listdir(directory) if f.endswith(".pdf")]
    sorted_files = sorted(pdf_files, key=extract_numeric_alpha)
    print(sorted_files)
    merger = PdfWriter()
    for pdf in sorted_files:
        merger.append(os.path.join(directory, pdf))
    merger.write(output_path)
    merger.close()
    # print(f"PDFs merged into {output_path}")


def extract_numeric_alpha(filename):
    """
    Extracts a numeric and an alphabetic part from a filename.

    If the filename matches the regular expression (\d+)([a-zA-Z]*), it returns a tuple
    with the numeric part and the alphabetic part. If the filename does not match, it
    returns the filename as is.

    The numeric part is converted to an integer.

    This function is used to sort PDF files by their numerical and alphabetic parts.
    """
    match = re.search(r"(\d+)([a-zA-Z]*)", filename)
    if match:
        num_part = int(match.group(1))
        alpha_part = match.group(2)
        return (num_part, alpha_part)
    return filename


def clean_up_directory(directory, keep_file):
    """
    Clean up a directory by deleting all files and subdirectories except for a given file.

    Args:
        directory (str): The directory path to clean up.
        keep_file (str): The file path that should not be deleted.

    Returns:
        None
    """
    for item in os.listdir(directory):
        item_path = os.path.join(directory, item)
        if item_path != keep_file and item!='.gitkeep':
            if os.path.isdir(item_path):
                shutil.rmtree(item_path)
            else:
                os.remove(item_path)
    # print(f"Cleaned up directory, keeping only {keep_file}")


def move_file(source_path, destination_folder):
    """
    Moves a file from a source path to a destination folder.

    Args:
        source_path (str): The path of the file to move.
        destination_folder (str): The directory path where the file should be moved.

    Returns:
        None
    """
    if not os.path.exists(destination_folder):
        os.makedirs(destination_folder)
    shutil.move(source_path, destination_folder)
    # print(f"Moved {source_path} to {destination_folder}")


def file_name_gen(spath, classno, subname, bkname):
    """
    Generates a PDF file name and its full path based on class number, subject name, and book name.

    Args:
        spath (str): The directory path where the PDF file will be saved.
        classno (int): The class number to include in the PDF file name.
        subname (str): The subject name to include in the PDF file name.
        bkname (str): The book name to include in the PDF file name.

    Returns:
        tuple: A tuple containing the generated PDF file name and its full path.
    """
    opt_list = [
        str(classno),
        subname.title().replace(" ", ""),
        bkname.title().replace(" ", ""),
    ]
    merged_file_name = "_".join(opt_list) + ".pdf"
    output_pdf_path = os.path.join(spath, merged_file_name)
    return merged_file_name, output_pdf_path


def run_funcs_cli(
    json_data, class_number, subject_name, book_name, processing_path, opt_path
):
    """
    Runs the CLI downloader functions in sequence.

    Args:
        json_data (dict): The JSON data containing the links to the books.
        class_number (int): The class number to download.
        subject_name (str): The subject name to download.
        book_name (str): The book name to download.
        processing_path (str): The directory path where the downloaded file will be saved.
        opt_path (str): The directory path where the merged PDF file will be saved.

    Returns:
        tuple: A tuple containing the download link, page link, book code, and the generated PDF file name.
    """

    download_link, page_link, book_code = get_link(
        json_data, class_number, subject_name, book_name
    )
    opt_file = download_file(download_link, processing_path)
    unzip_path = unzip_file(opt_file, processing_path)
    convert_images_to_pdfs(unzip_path)
    merged_file_name, output_pdf_path = file_name_gen(
        processing_path, class_number, subject_name, book_name
    )
    merge_pdfs(unzip_path, output_pdf_path)
    clean_up_directory(processing_path, output_pdf_path)
    move_file(output_pdf_path, opt_path)
    return download_link, page_link, book_code, merged_file_name


def run_funcs_gui(
    json_data,
    class_number,
    subject_name,
    book_name,
    processing_path,
    opt_path,
    progress_callback=None,
):
    """
    Runs the GUI downloader functions in sequence.

    Args:
        json_data (dict): The JSON data containing the links to the books.
        class_number (int): The class number to download.
        subject_name (str): The subject name to download.
        book_name (str): The book name to download.
        processing_path (str): The directory path where the downloaded file will be saved.
        opt_path (str): The directory path where the merged PDF file will be saved.
        progress_callback (function): An optional callback function to update the progress of the download process.

    Returns:
        tuple: A tuple containing the download link, page link, book code, and the generated PDF file name.
    """
    steps = 8
    current_step = 0

    def update_progress():
        nonlocal current_step
        current_step += 1
        if progress_callback:
            progress_callback(current_step / steps)

    download_link, page_link, book_code = get_link(
        json_data, class_number, subject_name, book_name
    )
    update_progress()

    opt_file = download_file(download_link, processing_path)
    update_progress()

    unzip_path = unzip_file(opt_file, processing_path)
    update_progress()

    convert_images_to_pdfs(unzip_path)
    update_progress()

    merged_file_name, output_pdf_path = file_name_gen(
        processing_path, class_number, subject_name, book_name
    )
    update_progress()

    merge_pdfs(unzip_path, output_pdf_path)
    update_progress()

    clean_up_directory(processing_path, output_pdf_path)
    update_progress()

    move_file(output_pdf_path, opt_path)
    update_progress()

    return download_link, page_link, book_code, merged_file_name
