
from transcript_processing_functions import \
                        full_transcript2essay, \
                        extract_metadata_as_json, \
                        json2rst, \
                        extract_text_from_docx, \
                        extract_metadata_as_json_v2, \
                        num_tokens_from_string
import os
import json
import re

def is_docx_file(file_path):
    extension = os.path.splitext(file_path)[1]
    return extension.lower() == '.docx'


# directory = r"raw_transcripts\drive-download-20230630T183317Z-001"
directory = r"raw_transcripts\drive-download-20230709T172414Z-001"

file_list = []
for file_name in os.listdir(directory):
    if os.path.isfile(os.path.join(directory, file_name)):
        file_list.append(os.path.join(directory, file_name))

# print("file_list: ",file_list)
print("Total number of files in folder: ",len(file_list))

# pattern = r"\d{4}-\d{2}-\d{2}"
pattern = r"\d{4}-\d{2}-\d{2}.*(?=\) - Transcript.docx)"

file_list_for_processing = file_list[2:]
for i, transcript_filepath in enumerate(file_list_for_processing):
    N = len(file_list_for_processing)
    print("Number of files for processing: ", N)
    print(f"\n--- {i+1}/{N} ----------------")
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

        # print("++ len(extracted_text) : ", len(extracted_text) )
        print("++ tokens in raw transcript: ", num_tokens_from_string(extracted_text) )
        print("** Last 100 characters: ")
        print(extracted_text[-100:])

    # --- begin LLM processing --- #
    start_llm_processing = True
    if start_llm_processing:
        save_directory = r"saves/2023-07-07_b/"

        essay_filepath = save_directory + savename + ' essay.txt'

        if not os.path.exists(essay_filepath):

            print('++ Generating essay...')
            final_essay = full_transcript2essay(extracted_text)

            print("Saving essay file...")
            with open(essay_filepath, 'w') as file:
                file.write(final_essay)
        else:
            print("Essay already exists")
            with open(essay_filepath, 'r') as file:
                final_essay = file.read()

        print('++ Extracting metadata...')
        metadata = extract_metadata_as_json_v2(final_essay)
        
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
