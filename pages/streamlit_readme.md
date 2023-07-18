# Transcript Summarizer and Quiz Generator with Streamlit

The Transcript Summarizer and Quiz Generator is a Streamlit web application built to help users create summary and metadata from long form text, such as a transcript or dense book. Furthermore, it allows you to create a multiple-choice quiz based on the summary created.

The application makes use of OpenAI's GPT-3.5 model for transcript summarization and quiz generation. 

**Note:** In order to use this application, you will need an API Key from OpenAI.

## Features
- Takes in long form text in DOCX, TXT, or MD format, or entered manually.
- Extracts text and processes it using OpenAI's GPT-3 model to create a summary.
- Generates metadata in JSON and RST format based on the created summary.
- Generates a multiple-choice quiz based on the created summary.

## Installation

To install the required packages, navigate to the application's directory and run:
```sh
pip install -r requirements.txt
```

## Usage

To run application on your local machine:
```sh
streamlit run app.py
```

**Deployed version of this app:** [https://transcript-summarizer.streamlit.app/](https://transcript-summarizer.streamlit.app/)

You will be prompted to enter your OpenAI API key, after which you can upload the document you wish to process. 

Upon submitting the document, the application will generate a summary, create metadata, and allow you to download these results as a zip file. You can then move on to the quiz page where multiple-choice questions are generated based on the summary.


## Pages

- **App**: This is the main page where users can upload their documents or enter text manually, and generate a summary and metadata.
- **Quiz**: This page is used to generate a multiple-choice quiz based on the summary created from the main page.
- **README**: This page displays the README information.


## How I used GPT4 to create this README file
https://chat.openai.com/share/47f4aac6-1ddf-4658-8db4-37f6cd79ebcc


## Contact and links
Feel free to leave me feedback :) <br>
Email: johnfengphd@gmail.com <br>
LinkedIn: https://www.linkedin.com/in/john-feng-phd-5735321b8/<br>
Portfolio: https://johnnykfeng.github.io/ <br>
Github repo for this app: https://github.com/johnnykfeng/transcript-processing/


