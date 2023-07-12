# About
This package uses GPT to convert raw transcripts into essay format, then essay format into JSON metadata file. 

# How-To-Use
Easiest way is to clone or fork this entire repo into your own local machine. <br>
I publish the streamlit app here:
[https://transcript-summarizer.streamlit.app/](https://transcript-summarizer.streamlit.app/)


# Api key
For running in local environment
Start a .streamlit folder with a secrets.toml file inside and enter
`OPENAI_API_KEY = "your api key"`

# Pipeline
![image](images\LLM_architecture.png)

Transcript --> Essay --> Metadata (JSON) --> RST file<br>

Functions are stored in `transcript_processing_functions.py`<br>

Check out `run.py` for test and implementation.<br>

See `app.py` for deploying streamlit app <br>


