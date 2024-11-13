import requests
from bs4 import BeautifulSoup
import re
import json
import copy
from config.config import ncert_url, ncert_home_url, json_path


# Function to parse a single if-else block
def parse_if_else_block(block, flag):
    """
    Parse a single if-else block from the NCERT website, given in the 'block' parameter.

    The 'flag' parameter determines whether to parse all book options (flag="vanilla"),
    or also include commented out book options (flag="commented").

    Returns a JSON object with the class, subject, book names, and book codes, or None if
    the block does not contain a valid class and subject.

    :param block: The if-else block to parse
    :type block: str
    :param flag: Whether to parse all or only uncommented book options
    :type flag: str
    :return: A JSON object with the parsed data, or None
    :rtype: dict or None
    """
    class_match = re.search(r"document\.test\.tclass\.value\s*==\s*(\d+)", block)
    subject_match = re.search(
        r'document\.test\.tsubject\.options\[sind\]\.text\s*==\s*"([^"]+)"', block
    )

    if class_match and subject_match:
        class_value = class_match.group(1)
        subject_value = subject_match.group(1)

        if flag == "vanilla":
            book_options = re.findall(
                r'^\s*document\.test\.tbook\.options\[\d+\]\.text\s*=\s*"([^"]+)"',
                block,
                re.MULTILINE,
            )
            book_values = re.findall(
                r'^\s*document\.test\.tbook\.options\[\d+\]\.value\s*=\s*"([^"]+)"',
                block,
                re.MULTILINE,
            )

        elif flag == "commented":
            # Include commented out book options
            book_options = re.findall(
                r'^\s*//\s*document\.test\.tbook\.options\[\d+\]\.text\s*=\s*"([^"]+)"',
                block,
                re.MULTILINE,
            )
            book_values = re.findall(
                r'^\s*//\s*document\.test\.tbook\.options\[\d+\]\.value\s*=\s*"([^"]+)"',
                block,
                re.MULTILINE,
            )

        # Create a JSON object for the block
        book_data = {"CLASS": class_value, "SUBJECT": subject_value}

        for i, (book, value) in enumerate(zip(book_options, book_values)):
            book_data[f"Book{i+1}"] = book
            book_data[f"Code{i+1}"] = value

        return book_data
    return None


def merge_blocks(vanilla_list, commented_list):
    """
    Merge two lists of book data, one with vanilla entries and another with commented entries.

    This function takes two lists of dictionaries: `vanilla_list` and `commented_list`.
    Each dictionary contains information about books, including their class, subject,
    book names, and book codes. The function merges the entries from the commented list
    into the corresponding entries in the vanilla list based on matching class and subject.

    For each entry in `vanilla_list`, the function searches for a matching entry in
    `commented_list` with the same class and subject. If a match is found, the books and
    codes from the commented entry are appended to the vanilla entry. The merged entries
    are collected into a new list, which is returned as the result.

    :param vanilla_list: List of dictionaries containing vanilla book data
    :type vanilla_list: list
    :param commented_list: List of dictionaries containing commented book data
    :type commented_list: list
    :return: List of dictionaries with merged book data
    :rtype: list
    """
    merged_list = []

    for vanilla in vanilla_list:
        # Find the corresponding commented entry
        matching_commented = None
        for commented in commented_list:
            if (
                vanilla["CLASS"] == commented["CLASS"]
                and vanilla["SUBJECT"] == commented["SUBJECT"]
            ):
                matching_commented = commented
                break

        # If a matching commented entry is found, merge the blocks
        if matching_commented:
            # Determine the starting point for the next book and code
            book_counter = 1
            while f"Book{book_counter}" in vanilla:
                book_counter += 1

            # Append the books and codes from the commented entry to the vanilla entry
            next_book_counter = book_counter
            while f"Book{next_book_counter - book_counter + 1}" in matching_commented:
                vanilla[f"Book{next_book_counter}"] = matching_commented[
                    f"Book{
                    next_book_counter - book_counter + 1}"
                ]
                vanilla[f"Code{next_book_counter}"] = matching_commented[
                    f"Code{
                    next_book_counter - book_counter + 1}"
                ]
                next_book_counter += 1

        # Add the merged entry to the result list
        merged_list.append(vanilla)

    return merged_list


# Function to transform data with nested books and "title"
def transform_data(data):
    """
    Transform the given data into a more structured format.

    The function takes a list of dictionaries, where each dictionary represents a subject
    and its associated books. The function transforms this data into a more structured
    format by grouping the books for each subject under a single key, "books", which
    contains a list of dictionaries, where each dictionary represents a book and its
    associated details.

    The function returns a list of dictionaries, where each dictionary represents a
    subject and its associated books in the transformed format.

    :param data: List of dictionaries containing subject and book data
    :type data: list
    :return: List of dictionaries with transformed data
    :rtype: list
    """
    transformed_data = []
    for item in data:
        new_item = item.copy()  # Create a copy of the current item
        books = []
        for key, value in new_item.items():  # Iterate through the copied dictionary
            if key.startswith("book"):
                books.append(
                    {
                        "id": int(key[4:]),
                        "title": value,
                        "basecode": new_item[f"basecode{key[4:]}"],
                        "code": new_item[f"code{key[4:]}"],
                        "link": new_item[f"link{key[4:]}"],
                        "dlink": new_item[f"dlink{key[4:]}"],
                    }
                )
        new_item["books"] = books
        # Remove the processed book keys

        transformed_data.append(new_item)
    return transformed_data


def fetch_and_clean_request(url):
    """
    Fetches the content of a given URL and cleans the response content by parsing
    the HTML using BeautifulSoup and extracting the JavaScript code blocks using
    regular expressions. The function then parses the extracted code blocks and
    merges them into a single list of dictionaries. Finally, the function converts
    the merged list of dictionaries into a JSON string and returns it.

    :param url: URL to fetch content from
    :type url: str
    :return: JSON string representing the parsed content
    :rtype: str
    """
    # Send a GET request to the URL
    response = requests.get(ncert_url)

    # Parse the content of the response using BeautifulSoup
    soup = BeautifulSoup(response.content, "html.parser")
    script_elements = soup.find_all("td")

    # Loop through each <td> element and process further
    for element in script_elements:
        # Extract the script tag content within the <td>
        script_tag = element.find("script")
        if script_tag:
            script_content = script_tag.string

    script_content_final = re.sub(
        r'document\.test\.tbook\.options\[0\]\.text\s*=\s*"\.\.Select Book Title\.\."\s*;',
        "",
        script_content,
    )

    # Regular expression to find if-else blocks
    if_else_pattern = re.compile(r"if\s*\(.*?\)\s*\{.*?\}", re.DOTALL)

    # Extract all if-else blocks
    if_else_blocks = if_else_pattern.findall(script_content_final)

    # Parse all if-else blocks
    parsed_blocks_vanilla = [
        parse_if_else_block(block, flag="vanilla") for block in if_else_blocks
    ]
    parsed_blocks_commented = [
        parse_if_else_block(block, flag="commented") for block in if_else_blocks
    ]

    # Filter out None values

    parsed_blocks_commented = [block for block in parsed_blocks_commented if block]
    parsed_blocks_vanilla = [block for block in parsed_blocks_vanilla if block]

    parsed_blocks = merge_blocks(parsed_blocks_vanilla, parsed_blocks_commented)

    # Convert to JSON format
    js_data = json.dumps(parsed_blocks, indent=4)

    return js_data


def json_file_export(data):
    """
    Saves the JSON data to the file specified in config.json_path after sorting
    and transforming the data to the desired format.

    The function takes a string argument which is the JSON data to be processed.
    The JSON data should be a list of dictionaries, where each dictionary contains
    the following keys:

        CLASS (int): Class number
        SUBJECT (str): Subject name
        Book1, Book2, ... (str): Book titles
        Code1, Code2, ... (str): Book codes
        Link1, Link2, ... (str): Book links
        DLink1, DLink2, ... (str): Book download links

    The function returns nothing and saves the processed data to the file
    specified in config.json_path.

    The function is used by the CLI interface to save the scraped data to a
    file for further processing.
    """
    global ncert_home_url
    # Load the JSON data
    json_data_frmt = json.loads(data)
    json_data_frmt_fin = copy.deepcopy(json_data_frmt)

    # Process each element in the JSON data
    for item in json_data_frmt_fin:
        # Create a new dictionary to hold sorted items
        sorted_item = {}

        # Add CLASS and SUBJECT to the sorted_item first
        if "CLASS" in item:
            sorted_item["class"] = int(item["CLASS"])
        if "SUBJECT" in item:
            sorted_item["subject"] = item["SUBJECT"]

        # Process Book, Code, Link, and DLink
        i = 1
        while f"Book{i}" in item:
            book = item[f"Book{i}"]
            book_key = f"book{i}"
            code_key = f"code{i}"
            code = f"Code{i}"
            link_key = f"link{i}"
            dlink_key = f"dlink{i}"
            bcode_key = f"basecode{i}"

            sorted_item[book_key] = book

            if code in item:
                code_value = item[code]
                sorted_item[bcode_key] = code_value
                if code_value.startswith("textbook.php?"):
                    code_part1 = code_value.split("=")[0]
                    partcode = code_part1.split("?")[1]
                    sorted_item[code_key] = partcode
                    # Original Link
                    original_link = f"{ncert_home_url}/{code_value}"
                    sorted_item[link_key] = original_link

                    # DLink with modification

                    dlink_value = f"{ncert_home_url}/textbook/pdf/{
                        partcode}dd.zip"
                    sorted_item[dlink_key] = dlink_value

                else:
                    sorted_item[code_key] = None
                    sorted_item[link_key] = None
                    sorted_item[dlink_key] = None

            i += 1

        # Update the original item with the sorted_item
        item.clear()
        item.update(sorted_item)

    # Transform the data
    # Copy data to avoid modifying original
    transformed_data = transform_data(copy.deepcopy(json_data_frmt_fin))
    for item in transformed_data:
        for key, value in list(item.items()):
            if not key.isalpha():
                del item[key]

    # Cleaning previous json file
    open(json_path, "w").close()

    # Save to a file
    with open(json_path, "w") as f:
        json.dump(transformed_data, f, indent=4)


def scraper_run():
    """
    Executes the scraping process for NCERT book data.

    This function orchestrates the scraping workflow by first fetching
    and cleaning the data from the NCERT website using the specified
    URL. The cleaned data is then exported as a JSON file to a specified
    path. The function uses the `fetch_and_clean_request` function to
    obtain the data and the `json_file_export` function to save it.

    Returns:
        None
    """
    json_data = fetch_and_clean_request(ncert_url)
    json_file_export(json_data)
