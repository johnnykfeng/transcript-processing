from langchain.chat_models import ChatOpenAI
from langchain import PromptTemplate, LLMChain

from langchain.text_splitter import MarkdownTextSplitter
from langchain.prompts.chat import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    AIMessagePromptTemplate,
    HumanMessagePromptTemplate,
)
from langchain.schema import (
    AIMessage,
    HumanMessage,
    SystemMessage
)

import json

import api_keys

#instantiate chat model
chat = ChatOpenAI(
    # openai_api_key='Get your own API' ,
    temperature=0,
    model='gpt-3.5-turbo')

"""# Part **1**: Processing raw transcript"""

import tiktoken
price_gpt35_turbo = 0.002 # $0.002/1k tokens
def num_tokens_from_string(string: str, encoding_name="cl100k_base") -> int:
    """Returns the number of tokens in a text string."""
    encoding = tiktoken.get_encoding(encoding_name)
    num_tokens = len(encoding.encode(string))
    return num_tokens

def transcript_token_size(raw_transcript, verbose = True):
  char_len = len(raw_transcript)
  token_len = num_tokens_from_string(raw_transcript)
  if verbose:
    print(f'Character length in raw transcript: {char_len}')
    print(f'Number of tokens in raw transcript: {token_len}')
    print(f'Char_len/token_len: {char_len/token_len:.2f}')
    print(f'Cost of input prompt with gpt-3.5-turbo: ${token_len*0.002/1000}')

  return token_len

"""## Splitting raw transcript

ChatGPT models have a token limit. For GPT3.5-turbo, the limit is 4096 tokens [(docs)](https://platform.openai.com/docs/models/gpt-3-5). Most transcripts exceed that, so it must be split into chunks.
"""

def transcript_splitter(raw_transcript, chunk_size=10000, chunk_overlap=200):
  markdown_splitter = MarkdownTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
  transcript_docs = markdown_splitter.create_documents([raw_transcript])
  return transcript_docs


def transcript2essay(transcript):
  system_template = "You are a helpful assistant that summarizes the main points of a presentation about large-Language model and machine learning research"
  system_prompt = SystemMessagePromptTemplate.from_template(system_template)
  # human_template = "Summarize the main points of this presentation's transcript: {transcript}"
  human_template = """Rewrite the contents and information of the presentation into a well written essay.\
  Write the essay as if the speaker wrote it himself from the same knowledge he used to create the presentation. \
  Include the speaker's full name in the essay and refer to him/her with the full name. \
  Also include the names of the people who asked questions and the questions they asked. \
  The transcript of this presentation is delimited in triple backticks:
  ```{transcript}```"""
  human_prompt = HumanMessagePromptTemplate.from_template(human_template)
  chat_prompt = ChatPromptTemplate.from_messages([system_prompt, human_prompt])

  result = chat(chat_prompt.format_prompt(transcript=transcript).to_messages())
  return result.content

def create_essay_parts(transcript_docs):
  essay_response=''
  for i, text in enumerate(transcript_docs):
    essay = transcript2essay(text.page_content)
    essay_response = f'\n\n#Part {i+1}\n'.join([essay_response, essay])

  return essay_response

def merge_essays(essays):
  system_template = """You are a helpful assistant that preprocesses text, \
                      writings and presentation transcripts in the context of large-Language model and machine learning research"""
  system_prompt = SystemMessagePromptTemplate.from_template(system_template)

  human_template = """Consolidate the multiple parts of the text into one \
  coherent essay or article that accurately captures the content of the multiple\
  parts without losing any information. Make sure to include the speaker's full name and the \
  names of the people who asked questions and the questions they asked. \
  The entire text is delimited in triple backticks and the parts are divided by
  #heading:
  ```{essays}```"""
  human_prompt = HumanMessagePromptTemplate.from_template(human_template)
  chat_prompt = ChatPromptTemplate.from_messages([system_prompt, human_prompt])

  final_essay = chat(chat_prompt.format_prompt(essays=essays).to_messages())
  return final_essay.content


def full_transcript2essay(raw_transcript:str):
  transcript_docs = transcript_splitter(raw_transcript)
  essay_parts = create_essay_parts(transcript_docs)
  final_essay = merge_essays(essay_parts)
  return final_essay



# """# Part 2: Extracting from essay"""

# final_essay_tokens = num_tokens_from_string(final_essay, "cl100k_base")
# print(f'Number of tokens in generated essays: {final_essay_tokens}')

# """## Extracting topics and key takeaways

# Here I feed the essay into another prompt template to extract the topics and key takeaways away the original transcript. The response is formatted as a JSON object.
# """


# Extracting from generated essay
def extract_topics_from_text(text, user_prompt):
  system_template = """You are a helpful assistant that preprocesses text, \
                      writings and presentation transcripts in the context of \
                      large-language models and machine learning research"""
  system_prompt = SystemMessagePromptTemplate.from_template(system_template)

  human_template = """{user_prompt}
  The text is delimited in triple backticks:
  ```{text}```"""
  human_prompt = HumanMessagePromptTemplate.from_template(human_template)
  chat_prompt = ChatPromptTemplate.from_messages([system_prompt, human_prompt])

  result = chat(chat_prompt.format_prompt(text=text, user_prompt=user_prompt).to_messages())
  return result.content


def extract_metadata_as_json(essay):
  system_template = """You are a helpful assistant that preprocesses text, \
                      writings and presentation transcripts in the context of \
                      large-language models and machine learning research"""
  
  system_prompt = SystemMessagePromptTemplate.from_template(system_template)

  # human_template = """\
  # Given the essay delimited in triple backticks, generate and extract important \
  # information such as the title, speaker, summary, a list of key topics, and a list of important takeaways. \
  # Format the reponse as a JSON object, with the keys 'Title', 'Topics', 'Speaker', \
  # 'Summary', 'Topics', and 'Takeaways' as the keys. \
  # \n\n \
  # Essay:\n```{text}```"""

  human_template = """\
  Given the essay delimited in triple backticks, generate and extract important \
  information such as the title, speaker, summary, a list of key topics, and a list of important takeaways for each topic. \
  Format the reponse as a JSON object, with the keys 'Title', 'Topics', 'Speaker', \
  'Summary', and 'Topics' as the keys and each topic will be keys for list of takeaways. \
  \n\n \
  Essay:\n```{text}```"""
  
  human_prompt = HumanMessagePromptTemplate.from_template(human_template)
  chat_prompt = ChatPromptTemplate.from_messages([system_prompt, human_prompt])

  result = chat(chat_prompt.format_prompt(text=essay).to_messages())
  metadata_json = json.loads(result.content)

  return metadata_json

# """#Part 3: Experimental"""

def generate_qa(text):
  system_template = """You are a helpful assistant that preprocesses text, \
                      writings and presentation transcripts in the context of \
                      large-language models and machine learning research"""
  system_prompt = SystemMessagePromptTemplate.from_template(system_template)

  human_template = """Given the article, rewrite it in a question and answer \
  format, where questions are asked about the important takeaways of the article \
  and detailed answers are provided based on the content of the article. The \
  goal is to present the same important information of the article. \
  Format the questions and answers as such:
  Q. question...
  A. answer...
  The article is delimited in triple backticks:
  ```{text}```"""
  human_prompt = HumanMessagePromptTemplate.from_template(human_template)
  chat_prompt = ChatPromptTemplate.from_messages([system_prompt, human_prompt])

  result = chat(chat_prompt.format_prompt(text=text).to_messages())
  return result.content


def generate_mc_questions(text):
  system_template = """You are a helpful assistant that preprocesses text, \
                      writings and presentation transcripts in the context of \
                      large-language models and machine learning research"""
  system_prompt = SystemMessagePromptTemplate.from_template(system_template)

  human_template = """Given the essay delimited in triple backticks, \
  generate 5 multiple choice questions\
  based on the contents of the essay. The goal of the these questions is to \
  quiz the audience after who have read or listen to the essay. Format the \
  quiz as follows.
  Q. question...
  a. choice 1
  b. choice 2
  c. choice 3
  d. choice 4
  Then provide the answers to each question and explain each choice.
  The essay is delimited in triple backticks:
  ```{text}```"""
  human_prompt = HumanMessagePromptTemplate.from_template(human_template)
  chat_prompt = ChatPromptTemplate.from_messages([system_prompt, human_prompt])

  result = chat(chat_prompt.format_prompt(text=text).to_messages())
  return result.content

def json2rst(metadata, rst_filepath):
  if not isinstance(metadata, dict):
      metadata = json.loads(metadata)
  
  # rst_filepath = './essays/test.rst'
  with open(rst_filepath, 'a') as the_file:
      the_file.write("\n\n")
      for key, value in metadata.items():
          if key == "Title":
              title_mark = "=" * len(f'{value}')
              the_file.write(title_mark + '\n')
              the_file.write(f"{value} \n")
              the_file.write(title_mark + '\n')
          elif key == "Speaker":
              the_file.write('*' + f"{value}" + '* \n\n')
          elif key == "Summary":
              title_mark = '-' * len(f'{key}')
              the_file.write("Summary \n")
              the_file.write(title_mark + '\n')
              the_file.write(f"{value} \n\n")
          elif key == "Topics":
              the_file.write("Topics: \n")
              the_file.write(title_mark + '\n')
              for topic in value:
                  the_file.write("\t" + f"{topic['Topic']} \n")
                  for takeaway in topic['Takeaways']:
                      the_file.write("\t\t" + f"* {takeaway} \n")

  


