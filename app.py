# streamlit app here
import streamlit as st
import pandas as pd
from io import StringIO

from transcript_processing_functions import \
                        full_transcript2essay, \
                        extract_metadata_as_json, \
                        json2rst, \
                        extract_text_from_docx, \
                        extract_metadata_as_json_v2, \
                        num_tokens_from_string

# uploaded_file = st.file_uploader("Upload single file", type="docx")
# if uploaded_file is not None:
#     # To read file as bytes:
#     bytes_data = uploaded_file.getvalue()
#     st.write(bytes_data)

#     # To convert to a string based IO:
#     stringio = StringIO(uploaded_file.getvalue().decode("utf-8"))
#     st.write(stringio)

#     # To read file as string:
#     string_data = stringio.read()
#     st.write(string_data)


uploaded_files = st.file_uploader("Upload multiple files", 
                                  type = "docx", 
                                  accept_multiple_files=True)
for uploaded_file in uploaded_files:
    st.write("filename:", uploaded_file.name)
    # st.write(dir(uploaded_file))

    text = extract_text_from_docx(uploaded_file)
    st.write(text[-100:])
    
    # bytes_data = uploaded_file.read()
    # st.write(bytes_data[:100])
