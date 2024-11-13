from .downloader_funcs import (
    fetch_json_data,
    get_classes,
    get_subjects,
    get_books,
    run_funcs_cli,
)
import os
from config.config import json_path, processing_path, output_path


def run_cli_downloader():
    """
    This function runs the cli downloader, it will keep running until user chooses to stop downloading books.
    It will first fetch the json data from the given json file path.
    Then it will enter a loop where user will be asked to select a class, then a subject from the selected class, then a book from the selected subject.
    After selecting a book, the function will download the book and print the page link, book code and the name of the merged pdf file.
    Finally it will ask user if they want to download again, if user types 'n' then it will break the loop and stop the program, if user types 'y' then it will clear the screen and start the loop again.
    The function will also clear the screen before asking for user input every time.
    """

    json_data = fetch_json_data(json_path)

    while True:
        print("Select Class from the following list:-")
        classes = get_classes(json_data)
        print(classes)
        print()
        print()
        class_number = int(input("Type class number\n"))
        print("Select Subject from the following list:-\n")
        subject_list = get_subjects(json_data, class_number)
        for id, value in enumerate(subject_list):
            print(f"{id+1}-{value}")
        # print(subject_list)
        print()
        subject_id = int(input("Type Index of Subject you want to select\n")) - 1
        subject_name = subject_list[subject_id]
        print()
        print("Select Book from the following list:-\n")
        book_list = get_books(json_data, class_number, subject_name)
        for id, value in enumerate(book_list):
            print(f"{id+1}-{value}")
        # print(book_list)
        book_id = int(input("Type Index of Book you want to select\n")) - 1
        book_name = book_list[book_id]
        download_link, page_link, book_code, merged_file_name = run_funcs_cli(
            json_data,
            class_number,
            subject_name,
            book_name,
            processing_path,
            output_path,
        )
        print()
        print(page_link)
        print()
        re_flag = input("Do you want to download again? Type y/n \n").lower()
        if re_flag == "n":
            break
        else:
            os.system("cls")
            continue


if __name__ == "__main__":
    run_cli_downloader()
