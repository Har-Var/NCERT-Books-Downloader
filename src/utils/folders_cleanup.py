import os
import shutil
from config.config import resources_folder, processing_folder, output_folder


def cleanup_folder(folder_path):
    """Remove all contents of the specified folder."""
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.remove(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
            print(f"Deleted: {file_path}")
        except Exception as e:
            print(f"Failed to delete {file_path}. Reason: {e}")


def cleanup_data_folders():
    """Clean up all data folders (processing, output, resources).

    This function will prompt the user for confirmation before cleaning up the
    resources folder. The processing and output folders will be cleaned without
    prompting the user. If the user chooses not to clean up the resources folder,
    it will be skipped.
    """
    # Clean up processing and output folders without prompt
    print("Cleaning up 'processing' and 'output' folders...")
    cleanup_folder(processing_folder)
    cleanup_folder(output_folder)
    print("Processing and output folders have been cleaned.\n")

    # Ask user for confirmation before cleaning up resources
    confirm = (
        input("Do you want to clean up the 'resources' folder? (y/n): ").strip().lower()
    )
    if confirm == "y":
        cleanup_folder(resources_folder)
        print("Resources folder has been cleaned.")
    else:
        print("Skipped cleaning the resources folder.")
