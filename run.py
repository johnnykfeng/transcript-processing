
from transcript_processing_functions import \
                        full_transcript2essay, \
                        extract_metadata_as_json, \
                        json2rst, \
                        extract_text_from_docx
import os
import json
import re

import time

def timer_decorator(func):
    def wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        result = func(*args, **kwargs)
        end_time = time.perf_counter()
        run_time = end_time - start_time
        print(f"Finished {func.__name__!r} in {run_time:.4f} secs")
        return result
    return wrapper


def is_docx_file(file_path):
    extension = os.path.splitext(file_path)[1]
    return extension.lower() == '.docx'


directory = r"raw_transcripts\drive-download-20230630T183317Z-001"
file_list = []
for file_name in os.listdir(directory):
    if os.path.isfile(os.path.join(directory, file_name)):
        file_list.append(os.path.join(directory, file_name))

# print("file_list: ",file_list)
print("len(file_list): ",len(file_list))

# pattern = r"\d{4}-\d{2}-\d{2}"
pattern = r"\d{4}-\d{2}-\d{2}.*(?=\) - Transcript.docx)"


for i, transcript_filepath in enumerate(file_list[13:14]):
    print(f"\n--- {i} ----------------")
    print("original filepath: \n", transcript_filepath)
    match = re.search(pattern, transcript_filepath)
    
    if match:
        savename = match.group()

        print("savename: ", savename)

    with open(transcript_filepath, 'r') as file:
        if is_docx_file(transcript_filepath):
            print("== file is docx ==")
            extracted_text = extract_text_from_docx(transcript_filepath)
        else: # not docx file
            print("== file is not docx ==")
            extracted_text = file.read()

        print("** Last 100 characters: ")
        print(extracted_text[-100:])

    save_directory = r"saves/"

    print('++ Generating essay...')
    final_essay = full_transcript2essay(extracted_text)

    essay_filepath = save_directory + savename + ' essay.txt'
    with open(essay_filepath, 'w') as file:
        file.write(final_essay)

    print('++ Extracting metadata...')
    metadata = extract_metadata_as_json(final_essay)
    
    metadata_filepath = save_directory + savename + ' metadata.json'
    with open(metadata_filepath, 'w') as file:
        json.dump(metadata, file)
    
    rst_filepath = save_directory + savename + ' metadata.rst'

    try:
        json2rst(metadata, rst_filepath)
    except Exception as e:
        print(e)
        print("Error with ", rst_filepath)
        continue


# if __name__ == '__main__':
#     essay_filepath = r'./essays/test_essay.txt'
#     if not os.path.exists(essay_filepath): # if essay doesn't exist
#         print('Generating essay... (this may take a few minutes)')

#         transcript_filepath = r'./transcripts/test_transcript.md'
#         with open(transcript_filepath, 'r') as file:
#             raw_transcript = file.read()

#         # takes about 2-3 minutes to run
#         final_essay = full_transcript2essay(raw_transcript)

#         essay_filepath = r'./essays/test_essay.txt'
#         # save the final essay to a file
#         with open(essay_filepath, 'w') as file:
#             file.write(final_essay)

#     # start here if essay exists

#     # load essay from file
#     essay_filepath = r'./essays/test_essay.txt'
#     with open(essay_filepath, 'r') as file:
#         essay = file.read()

#     # 17 seconds to run
#     print('Extracting metadata...')
#     metadata = extract_metadata_as_json(essay)

#     # save metadata to file
#     metadata_filepath = r'./metadata/test_metadata.json'
#     with open(metadata_filepath, 'w') as file:
#         json.dump(metadata, file)

#     # convert metadata from json to rst
#     rst_filepath = r'./metadata/test.rst'
#     json2rst(metadata, rst_filepath)


