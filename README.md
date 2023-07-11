# About
This package uses GPT to convert raw transcripts into essay format, then essay format into JSON metadata file. 

# how-to-use
Easiest way is to clone or fork this entire repo into your own local machine. 

# Api key
For running in local environment
Start a .streamlit folder with a secrets.toml file inside and enter
`OPENAI_API_KEY = "your api key"`


# Pipeline
Transcript --> Essay --> Metadata (JSON) --> RST file

Functions are stored in `transcript_processing_functions.py`

Check out `run.py` for test and implementation.

Files are stored in /transcripts, /essays, and /metadata and folders.
