# streamlit app here
import streamlit as st
import pandas as pd
from io import StringIO
import os
import json
import time
import openai

from transcript_processing_functions import \
                        full_transcript2essay, \
                        json2rst, \
                        extract_text_from_docx, \
                        extract_text_from_plaintext, \
                        extract_metadata_as_json_v2, \
                        num_tokens_from_string

# auxiliary functions

def is_docx_file(file_path):
    extension = os.path.splitext(file_path)[1]
    return extension.lower() == '.docx'

def is_txt_file(file_path):
    extension = os.path.splitext(file_path)[1]
    return extension.lower() == '.txt'

def is_md_file(file_path):
    extension = os.path.splitext(file_path)[1]
    return extension.lower() == '.md'

import zipfile

def zip_all_files_in_folder(folder_path, zip_name):
    # Create a ZipFile object in write mode
    with zipfile.ZipFile(zip_name, 'w') as zipf:
        # Iterate over all the files in the folder
        for foldername, subfolders, filenames in os.walk(folder_path):
            for filename in filenames:
                # Create the complete filepath by concatenating the folder name and filename
                file_path = os.path.join(foldername, filename)
                print(file_path)
                # Add the file to the zip
                zipf.write(file_path)

print("++ streamlit app rerun ++")

st.title("LLM Transcript Processor")
description = st.expander("**What is this app for?**", expanded=False)

description.write("""This app is for summarizing transcripts into structured format.
The process takes about 2-5 minutes per file, depending on the length 
of your transcript.
The output is a summary in txt, and metadata in json and rst format.
""")

description.markdown("""*Sometimes the metadata extraction process fails
            due to inconsitent json formatting. If this happens, you can try
            running the process again.*""")



uploaded_file = st.file_uploader("Only accept docx, txt, and md.", 
                                  type = ["docx","txt","md"], 
                                  accept_multiple_files=False)

if uploaded_file is not None:
    if is_docx_file(uploaded_file.name):
        print("== file is docx ==")
        transcript_text = extract_text_from_docx(uploaded_file)

    elif is_md_file(uploaded_file.name) or is_txt_file(uploaded_file.name):
        print("== file is md ==")
        # transcript_text = uploaded_file.readlines()
        lines = uploaded_file.readlines()
        transcript_text = [line.decode('utf-8') for line in lines]
        transcript_text = '\n'.join(transcript_text)


# st.write(type(uploaded_file))
# # st.write(type(transcript_text))
# print(type(uploaded_file))
# print(type(transcript_text))
# st.write(transcript_text[:100])
# st.write(transcript_text[-100:])

    num_tokens = num_tokens_from_string(transcript_text)
    st.info(f"Number of tokens in transcript: {num_tokens}")

    # remove the file extension from the filename
    basename = os.path.splitext(uploaded_file.name)[0]


with st.form('myform', clear_on_submit=True):
    openai_api_key = st.text_input('Enter your OpenAI API Key', type='password', 
                                   disabled=False)
    submitted = st.form_submit_button('Click here to Start processing', 
                                      disabled=not uploaded_file)

# set openai api key
openai.api_key = openai_api_key

# if uploaded_files != []:
if submitted and uploaded_file is not None:

    save_directory = r"./tempsave/"

    # if st.button("Start Processing"):

    # check if save directory exists
    if (not os.path.exists(save_directory)): # creates folder if it doesn't exist
        os.mkdir(save_directory)
    elif len(os.listdir(save_directory)) > 0: # if folder exists and is not empty
        for f in os.listdir(save_directory):  # removes all existing files in the folder
            os.remove(os.path.join(save_directory, f))


    with st.spinner("Generating summary..."):
    # st.caption("Generating summary...") 
        t1 = time.time()
        summary = full_transcript2essay(transcript_text)
        t2 = time.time() - t1
        st.caption(f"Run time for summarization: **{t2:.2f}** seconds")
    st.success('Success!', icon="🎉")

    st.info(f"Number of tokens in summary: {num_tokens_from_string(summary)}")

    essay_filepath = save_directory + basename + ' summary.txt'
    # st.caption(f"Saving summary file as {essay_filepath}...")
    with open(essay_filepath, 'w') as file:
        file.write(summary)

    essay_expander = st.expander("See full summary")
    essay_expander.write(summary)

    with st.spinner("Generating metadata..."):
        t1 = time.time()
        # st.caption("Extracting metadata...")
        max_retries = 3
        for i in range(max_retries):
            try:
                metadata = extract_metadata_as_json_v2(summary)
                break
            except Exception as e:
                st.error(f"Attempt {i+1} failed with error: {e}")
                time.sleep(1)
                if i == max_retries - 1:
                    raise
                else:
                    st.write("Retrying...")


        json_filepath = save_directory + basename + ' metadata.json'
        with open(json_filepath, 'w') as file:
            json.dump(metadata, file)

        json_expander = st.expander("See metadata json")
        json_expander.write(metadata)

        # st.caption("Converting metadata to rst...")
    
        rst_filepath = save_directory + basename + ' metadata.rst'
        json2rst(metadata, rst_filepath)

        t2 = time.time() - t1
        st.caption(f"Run time for metadata extraction: {t2:.2f} seconds")
    st.success('Done!', icon="✅")


    with open(rst_filepath, 'r') as file:
        rst_text = file.read()

    rst_expander = st.expander("See metadata rst")
    rst_expander.write(rst_text)

    zip_filename = 'transcript_summaries.zip'
    zip_all_files_in_folder(folder_path = save_directory, 
                            zip_name = zip_filename)

    st.info("Once the download button is pressed, the entire app resets.")
    with open(zip_filename, 'rb') as zipfile:
        st.download_button(label="Download all files as zip", 
                            data=zipfile, 
                            file_name=zip_filename,
                            mime="application/zip")

