# streamlit app here
import streamlit as st
import pandas as pd
from io import StringIO
import os
import json
import time
import openai
import zipfile

from transcript_processing_functions import \
                        full_transcript2essay, \
                        json2rst, \
                        extract_text_from_docx, \
                        extract_text_from_plaintext, \
                        extract_metadata_as_json, \
                        num_tokens_from_string

from st_pages import Page, show_pages, add_page_title

show_pages(
    [
        Page("app.py", "App", "📖"),
        Page("pages/quiz.py", "Quiz", "📝"),
        Page("pages/README.py", "README", "📜")
    ]
)

# --- HELPER_FUNCTIONS --- #
def is_docx_file(file_path):
    extension = os.path.splitext(file_path)[1]
    return extension.lower() == '.docx'

def is_txt_file(file_path):
    extension = os.path.splitext(file_path)[1]
    return extension.lower() == '.txt'

def is_md_file(file_path):
    extension = os.path.splitext(file_path)[1]
    return extension.lower() == '.md'

def zip_all_files_in_folder(folder_path, zip_name):
    import zipfile
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

def timer(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        execution_time = end_time - start_time
        st.caption(f"Execution time: {execution_time:.2f} seconds")
        return result
    return wrapper

@timer
@st.cache_data(show_spinner=f"Generating summary from transcript, takes about 1-2 minutes...")
def cached_transcript2essay(transcript_path, _chat):
    return full_transcript2essay(transcript_path, chat_model=_chat)

@timer
@st.cache_data(show_spinner=f"Gathering metadata from summary...")
def cached_extract_metadata_as_json(summary, _chat):
    return extract_metadata_as_json(summary, chat_model=_chat)

# --- INITIALIZING SESSION STATES --- #
if "summary" not in st.session_state:
    st.session_state['summary'] = None
if "api_key" not in st.session_state:
    st.session_state['api_key'] = "None"
    st.session_state['api_key_check'] = False
if "button" not in st.session_state:
    st.session_state['button'] = False
if "transcript" not in st.session_state:
    st.session_state['transcript'] = None

def toggle_button_state():
    st.session_state['button'] = not st.session_state['button']

# --- Displaying session state info on sidebar --- #
sidebar_placeholder = st.sidebar.empty()
def sidebar_session_state(sidebar_placeholder=sidebar_placeholder):
    with sidebar_placeholder.expander("Session State", expanded=False):
        if st.session_state['transcript'] is None:
            st.markdown("No transcript uploaded yet.")
        else:
            st.markdown(f"**Transcript**:\n{st.session_state['transcript'][:100]}...")
        if st.session_state['summary'] is None:
            st.markdown("No summary generated yet.")
        else:
            st.markdown(f"**Summary**:\n{st.session_state['summary'][:100]}...")

        st.markdown(f"**API Key**:\n{st.session_state['api_key']}")
        # st.markdown(f"**API Key**:\n{st.session_state['api_key'][:5]}... {st.session_state['api_key'][-5:]}")
        
        if st.session_state['api_key_check']:
            st.markdown("✅ Key is valid ")
        else:
            st.markdown("❌ Key is invalid ")
        # st.markdown(f"**api_key_check**:\n{st.session_state['api_key_check']}")

sidebar_session_state(sidebar_placeholder)

# --- HEADER of the app page --- #
print("++ streamlit app rerun ++")
st.title("Transcript Summarizer 📑")
description = st.expander("**🙋 What is this app for❓**", expanded=False)
description.write("""This app is for summarizing transcripts into structured format.
The process takes about 2-5 minutes per file, depending on the length 
of your transcript.
The output is a summary in txt, and metadata in json and rst format.
""")
description.markdown("""*Sometimes the metadata extraction process fails
            due to inconsitent json formatting. If this happens, you can try
            running the process again.*""")
    


upload_toggle = st.radio("Upload method", options=["File uploader", "Enter text manually"])
if upload_toggle == "File uploader":
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

elif upload_toggle == "Enter text manually":
    transcript_text = st.text_area("Enter your transcript here",
                                      height=300)
    
    st.session_state['transcript'] = transcript_text
    num_tokens = num_tokens_from_string(transcript_text)
    st.info(f"Number of tokens in transcript: {num_tokens}")

    # remove the file extension from the filename
    # basename = os.path.splitext(uploaded_file.name)[0]

# st.sidebar.caption(f"Stored API Key: \"{st.session_state['api_key']}\" ")

with st.sidebar.form('myform', clear_on_submit=True):
    OPENAI_API_KEY = st.text_input('🔑 Enter your OpenAI API Key', type='password', 
                                   disabled=False)
    submitted = st.form_submit_button('Submit your key',
                                      help = "Click here to submit your API key.",  
                                      disabled=False )

    if submitted:
        st.session_state['api_key'] = OPENAI_API_KEY
        st.caption(f"🔑: {OPENAI_API_KEY}")
        if OPENAI_API_KEY.startswith("sk-"):
            st.session_state['api_key_check'] = True

    # give warning message if not valid
    # openai.api_key = OPENAI_API_KEY
    if not st.session_state['api_key_check']:
        st.warning("Please enter a valid OpenAI API Key")
    
    sidebar_session_state(sidebar_placeholder)

def full_process(transcript_text):
    from langchain.chat_models import ChatOpenAI

    chat = ChatOpenAI(
        openai_api_key=st.session_state["api_key"],
        temperature=0,
        model='gpt-3.5-turbo')

    chat16k = ChatOpenAI(
        openai_api_key=st.session_state["api_key"],
        temperature=0,
        model='gpt-3.5-turbo-16k')

    save_directory = r"./tempsave/"

    # check if save directory exists
    if (not os.path.exists(save_directory)): # creates folder if it doesn't exist
        os.mkdir(save_directory)
    elif len(os.listdir(save_directory)) > 0: # if folder exists and is not empty
        for f in os.listdir(save_directory):  # removes all existing files in the folder
            os.remove(os.path.join(save_directory, f))

    # --- TRANSCRIPT SUMMARIZATION --- #
    summary = cached_transcript2essay(transcript_text, chat) 
    st.session_state['summary'] = summary
    st.write('✅ Done!')
    st.info(f"Number of tokens in summary: {num_tokens_from_string(summary)}")

    summary_filepath = save_directory + '_summary.txt'
    with open(summary_filepath, 'w') as file:
        file.write(summary)

    summary_placeholder = st.empty()
    summary_expander = summary_placeholder.expander("**See full summary**")
    summary_expander.write(st.session_state['summary'])

    # --- METADATA EXTRACTION --- #
    metadata = cached_extract_metadata_as_json(summary, chat)

    json_filepath = save_directory + '_metadata.json'
    with open(json_filepath, 'w') as file:
        json.dump(metadata, file)

    json_expander = st.expander("See metadata json")
    json_expander.write(metadata)

    rst_filepath = save_directory + '_metadata.rst'
    json2rst(metadata, rst_filepath)

    st.write('✅ Done!')

    with open(rst_filepath, 'r') as file:
        rst_text = file.read()

    rst_expander = st.expander("See metadata rst")
    rst_expander.write(rst_text)

    # --- SAVE ALL FILES AS ZIP --- #
    zip_filename = 'transcript_summaries.zip'
    zip_all_files_in_folder(folder_path = save_directory, 
                            zip_name = zip_filename)

    with open(zip_filename, 'rb') as zipfile:
        st.download_button(label="Download all files as zip", 
                            data=zipfile, 
                            file_name=zip_filename,
                            mime="application/zip")

# if uploaded_files != []:
if st.button(label="▶️ Start Processing",
             help="Click here to start processing the transcript.", 
             on_click=toggle_button_state,
             disabled=not (st.session_state['transcript'] and st.session_state["api_key_check"])):
    
    full_process(st.session_state['transcript'])
    sidebar_session_state(sidebar_placeholder)

elif st.session_state['summary'] != None:
    full_process(st.session_state['transcript'])
    sidebar_session_state(sidebar_placeholder)
