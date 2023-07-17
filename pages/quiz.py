import streamlit as st

from PIL import Image
import glob
import os
import random

# specify the directory you want to search in
directory = r'./tempsave/'

# find all files in the directory that end with 'summary.txt'
files = glob.glob(os.path.join(directory, '*summary.txt'))
print(files)
# if there's at least one such file
if files:
    # open the first file that matches
    with open(files[0], 'r') as file:
        summary = file.read()
        # print(summary[:200])
else:
    print("No file ending with 'summary.txt' found in the specified directory.")



from langchain.chat_models import ChatOpenAI
from transcript_processing_functions import mc_question_json
OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]

chat = ChatOpenAI(
    openai_api_key=OPENAI_API_KEY,
    temperature=0,
    model='gpt-3.5-turbo')


n_input = st.number_input("Number of questions to generate.", 
                              min_value=1,
                              max_value=10, 
                              value=3)
n_int = int(n_input)

@st.cache_data(show_spinner = f"Generating {n_int} questions from summary...")
def generate_questions(summary, _chat, n_int):
    return mc_question_json(summary, chat_model=_chat, n=n_int)

# if st.button("Create Quiz"):    
    # with st.spinner(f"Generating {n_int} questions from summary..."):
    # st.caption("LLM generating quiz from summary...")
    # results = generate_questions(summary, chat, n_int)

    # st.title('Quiz')    
    
    # user_answers = []
    # for question in results['questions']:
    #     st.write(question['question'])
    #     options = question['options']
    #     random.shuffle(options)
    #     user_answer = st.radio('Select an answer', 
    #                         options)
                            
    #     user_answers.append(user_answer)
    #     if user_answer == question['correct_answer']:
    #         st.write('Correct!')
    #         st.write('Answer: ' + question['correct_answer'])
    #         st.write('Explanation: ' + question['explanation'])
    #     else:
    #         st.write('Incorrect!')
            
    #     st.write('---')

        # list of fixes
        # 1. find a way to make app not rerun after every selection
        # 2. Add an api key or "create quiz" starting button
        # 3. also add an input box for user to add number of question

        # Initialize session state variables if they don't exist yet

# maps integers to letters for keeping track of answers
int2letter = {0:"A", 1:"B", 2:"C", 3:"D"}
letter2int = {"A":0, "B":1, "C":2, "D":3}
if "current_question" not in st.session_state:
    st.session_state.answers = {} 
    st.session_state.current_question = 1 # keeps track of current question number
    st.session_state.questions = [] 
    st.session_state.right_answers = 0 # count of right answers
    st.session_state.wrong_answers = 0 # count of wrong answers


results = generate_questions(summary, chat, n_int)


def display_question():
    # Handle first case
    if len(st.session_state.questions) == 0:
        try:
            first_question = results['questions'][0]
        except Exception as e:
            st.error(e)
            return
        st.session_state.questions.append(first_question)

    # Disable the submit button if the user has already answered this question
    submit_button_disabled = st.session_state.current_question in st.session_state.answers

    # Get the current question from the questions list
    question = st.session_state.questions[st.session_state.current_question-1]

    # Display the question prompt
    st.write(f"{st.session_state.current_question}. {question['question']}")

    # Use an empty placeholder to display the radio button options
    options = st.empty()

    # Display the radio button options and wait for the user to select an answer
    user_answer = options.radio("Your answer:", 
                                question["options"], 
                                key=st.session_state.current_question)

    # Display the submit button and disable it if necessary
    submit_button = st.button("Submit", disabled=submit_button_disabled)

    # If the user has already answered this question, display their previous answer
    if st.session_state.current_question in st.session_state.answers:
        user_choice = st.session_state.answers[st.session_state.current_question]
        options.radio(
            "Your answer:",
            question["options"],
            key=float(st.session_state.current_question),
            index=letter2int[user_choice],
        )

    answer_index = question["options"].index(user_answer)
    st.write(int2letter[answer_index])
    # If the user clicks the submit button, check their answer and show the explanation
    if submit_button:
        # Record the user's answer in the session state
        st.session_state.answers[st.session_state.current_question] = int2letter[answer_index]
        st.caption(f"You submitted choice {int2letter[answer_index]}")

        # Check if the user's answer is correct and update the score
        if user_answer == question["correct_answer"]:
            st.write("Correct!")
            st.session_state.right_answers += 1
        else:
            st.write(f"Sorry, the correct answer was {question['correct_answer']}.")
            st.session_state.wrong_answers += 1

        # Show an expander with the explanation of the correct answer
        with st.expander("Explanation"):
            st.write(question["explanation"])

    # Display the current score
    st.write(f"Right answers: {st.session_state.right_answers}")
    st.write(f"Wrong answers: {st.session_state.wrong_answers}")

    # Define a function to go to the next question
def next_question():
    # Move to the next question in the questions list
    if st.session_state.current_question == n_int:
        st.caption("No more questions")
        return
    
    st.session_state.current_question += 1

    # If we've reached the end of the questions list, get a new question
    if st.session_state.current_question > len(st.session_state.questions) - 1:
        try:
            next_question = results['questions'][st.session_state.current_question-1]
        except Exception as e:
            st.error(e)
            st.session_state.current_question -= 1
            return
        st.session_state.questions.append(next_question)
        # st.experimental_rerun()
        



# Define a function to go to the previous question
def prev_question():
    # Move to the previous question in the questions list
    if st.session_state.current_question > 1:
        st.session_state.current_question -= 1
        st.session_state.explanation = None


# Create a 3-column layout for the Prev/Next buttons and the question display
col1, col2, col3 = st.columns([1, 6, 1])

# Add a Prev button to the left column that goes to the previous question
with col1:
    if col1.button("Prev"):
        prev_question()

# Add a Next button to the right column that goes to the next question
with col3:
    if col3.button("Next"):
        next_question()

# Display the actual quiz question
with col2:
    display_question()
    

with st.sidebar:
    with st.expander("See summary"):
        st.write(summary)
    # summary_expander = st.expander("See summary")
    # st.write("this is sidebar")
    with st.expander("Streamlit session state"):
        st.write(f"Question #:")
        st.write(st.session_state.current_question)
        st.caption(f"Submitted answers: {st.session_state.answers}")
        st.write(st.session_state.answers)