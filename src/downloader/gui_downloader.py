import customtkinter as ctk
from .downloader_funcs import (
    fetch_json_data,
    get_classes,
    get_subjects,
    get_books,
    run_funcs_gui,
)
from config.config import json_path, processing_path, output_path


def run_gui_downloader():
    """
    Initializes and runs the GUI application for downloading NCERT books.

    The GUI allows users to select a class, subject, and book, and then download the selected book. The application
    displays a progress bar during the download process and shows the results including the book code, page link,
    download link, and generated PDF file name.

    The function performs the following steps:
    - Fetches JSON data containing book information from a specified path.
    - Sets up a GUI using the customtkinter library.
    - Provides dropdowns for class, subject, and book selection.
    - Updates available subjects and books based on class and subject selections.
    - Initiates a download process and updates the progress bar.
    - Displays the result of the download including links and file information.
    - Allows repeated operations through GUI interactions.

    Note: This function runs an infinite main loop to keep the GUI active.
    """
    json_data = fetch_json_data(json_path)

    def update_subjects(*args):
        """
        Updates the list of available subjects based on the selected class.

        This function is triggered whenever the class selection changes. It
        fetches the list of subjects for the selected class, updates the
        subject dropdown with the new list, and resets the subject selection
        to the first available subject.

        Args:
            *args: Ignored. The function takes arbitrary arguments to conform
                to the expected signature for a Tkinter callback function.
        """
        class_number = int(class_selected.get())
        subjects = get_subjects(json_data, class_number)
        subject_combo.configure(values=[s for s in subjects])
        subject_selected.set("")  # reset subject selection

    def update_books(*args):
        """
        Updates the list of available books based on the selected class and subject.

        This function is triggered whenever the class or subject selection changes. It
        fetches the list of books for the selected class and subject, updates the
        book dropdown with the new list, and resets the book selection to the first
        available book.

        Args:
            *args: Ignored. The function takes arbitrary arguments to conform
                to the expected signature for a Tkinter callback function.
        """
        class_number = int(class_selected.get())
        subject_name = subject_selected.get()
        books = get_books(json_data, class_number, subject_name)
        book_combo.configure(values=[b for b in books])
        book_selected.set("")  # reset book selection

    def progress_callback(progress):
        """
        Updates the progress bar with the current progress.

        This function is used as a callback to update the progress bar's value
        during the download process. It also refreshes the UI to reflect the
        current progress.

        Args:
            progress (float): The current progress as a float between 0 and 1,
                            representing the completion percentage.
        """
        progress_bar.set(progress)
        app.update_idletasks()  # Update the UI

    def start_download():
        """
        Starts the download process for the selected book.

        This function is triggered when the user clicks the "Download" button.
        It fetches the selected book's information (class number, subject name,
        book name), validates the inputs, and then initiates the download process
        using the run_funcs_gui function. The function updates the progress bar
        and displays the results (book code, page link, download link, and PDF
        file name) in the respective text boxes after the download is complete.

        If the inputs are invalid (e.g., no class, subject, or book is selected),
        the function does nothing.

        :param None:
        :return: None
        """
        class_number = int(class_selected.get())
        subject_name = subject_selected.get()
        book_name = book_selected.get()

        if class_number and subject_name and book_name:
            download_button.configure(text="Processing...", state="disabled")
            progress_bar.grid(
                row=1, column=2, columnspan=3, pady=20
            )  # Show the progress bar
            progress_bar.set(0)  # Reset progress bar to 0

            # Perform the download process
            download_link, page_link, book_code, pdf_file_name = run_funcs_gui(
                json_data,
                class_number,
                subject_name,
                book_name,
                processing_path,
                output_path,
                progress_callback,
            )
            # Hide the progress bar after completion
            progress_bar.grid_forget()
            # Display the results
            book_code_box.configure(state="normal")
            book_code_box.delete(1.0, ctk.END)  # clear previous text
            book_code_box.insert(ctk.END, book_code)
            book_code_box.configure(state="disabled")  # make the text box read-only

            page_link_box.configure(state="normal")
            page_link_box.delete(1.0, ctk.END)  # clear previous text
            page_link_box.insert(ctk.END, page_link)
            page_link_box.configure(state="disabled")  # make the text box read-only

            download_link_box.configure(state="normal")
            download_link_box.delete(1.0, ctk.END)  # clear previous text
            download_link_box.insert(ctk.END, download_link)
            download_link_box.configure(state="disabled")  # make the text box read-only

            pdf_file_name_box.configure(state="normal")
            pdf_file_name_box.delete(1.0, ctk.END)  # clear previous text
            pdf_file_name_box.insert(ctk.END, pdf_file_name)
            pdf_file_name_box.configure(state="disabled")  # make the text box read-only

            download_button.configure(text="Download", state="normal")

    app = ctk.CTk()
    app.title("NCERT Books Downloader")
    app.geometry("1200x200")

    ctk.set_appearance_mode("Dark")
    ctk.set_default_color_theme("green")

    class_label = ctk.CTkLabel(app, text="Select Class")
    class_label.grid(row=0, column=0, padx=10, pady=(20, 10), sticky="ew")
    classes = get_classes(json_data)
    class_selected = ctk.StringVar(value=0)
    class_combo = ctk.CTkComboBox(
        app, values=[str(c) for c in classes], variable=class_selected, width=10
    )
    class_combo.grid(row=0, column=1, padx=10, pady=(20, 10), sticky="ew")

    subject_label = ctk.CTkLabel(app, text="Select Subject")
    subject_label.grid(row=0, column=2, padx=10, pady=(20, 10), sticky="ew")
    subject_selected = ctk.StringVar(value="")
    subject_combo = ctk.CTkComboBox(
        app, values=[], variable=subject_selected, width=150
    )
    subject_combo.grid(row=0, column=3, padx=10, pady=(20, 10), sticky="ew")

    book_label = ctk.CTkLabel(app, text="Select Book")
    book_label.grid(row=0, column=4, padx=10, pady=(20, 10), sticky="ew")
    book_selected = ctk.StringVar(value="")
    book_combo = ctk.CTkComboBox(app, values=[], variable=book_selected, width=400)
    book_combo.grid(row=0, column=5, padx=10, pady=(20, 10), sticky="ew")

    # Progress bar
    progress_bar = ctk.CTkProgressBar(app, orientation="horizontal", mode="determinate")
    progress_bar.set(0)
    # Result labels and textboxes
    book_code_label = ctk.CTkLabel(app, text="Book Code")
    book_code_label.grid(row=3, column=0, padx=10, pady=5, sticky="ew")
    book_code_box = ctk.CTkTextbox(
        app, height=40, width=80, state="disabled", wrap="word"
    )
    book_code_box.grid(row=3, column=1, padx=10, pady=5, sticky="ew")

    page_link_label = ctk.CTkLabel(app, text="Page Link")
    page_link_label.grid(row=3, column=2, padx=10, pady=5, sticky="ew")
    page_link_box = ctk.CTkTextbox(
        app, height=40, width=300, state="disabled", wrap="word"
    )
    page_link_box.grid(row=3, column=3, padx=10, pady=5, sticky="ew")

    download_link_label = ctk.CTkLabel(app, text="Download Link")
    download_link_label.grid(row=3, column=4, padx=10, pady=5, sticky="ew")
    download_link_box = ctk.CTkTextbox(
        app, height=40, width=100, state="disabled", wrap="word"
    )
    download_link_box.grid(row=3, column=5, padx=10, pady=5, sticky="ew")

    pdf_file_name_label = ctk.CTkLabel(app, text="PDF Name")
    pdf_file_name_label.grid(row=1, column=4, padx=10, pady=5, sticky="ew")
    pdf_file_name_box = ctk.CTkTextbox(
        app, height=40, width=200, state="disabled", wrap="word"
    )
    pdf_file_name_box.grid(row=1, column=5, padx=10, pady=5, sticky="ew")

    download_button = ctk.CTkButton(app, text="Download", command=start_download)
    download_button.grid(row=1, column=1, columnspan=2, pady=20, sticky="ew")

    class_selected.trace_add(
        "write", update_subjects
    )  # bind update_subjects to class selection change
    subject_selected.trace_add(
        "write", update_books
    )  # bind update_books to subject selection change

    app.mainloop()


if __name__ == "__main__":
    run_gui_downloader()
