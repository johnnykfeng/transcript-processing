import streamlit as st
from PIL import Image

image = Image.open('images/LLM_architecture_dark.png')

st.image(image, use_column_width=True)

# st.markdown doesn't display image properly
# so I removed the image from the README.md file
with open(r"./pages/streamlit_readme.md", 'r') as file:
    lines = file.readlines()

updated_lines = []
skip_next = False
for line in lines:
    if skip_next:
        skip_next = False
        continue
    if '![image]' in line:
        skip_next = True
        continue

    updated_lines.append(line)

st.markdown(''.join(updated_lines), unsafe_allow_html=True)



