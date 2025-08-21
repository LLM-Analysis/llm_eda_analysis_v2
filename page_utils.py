import streamlit as st
import pandas as pd

from backend_utils import react_prompt

import time

def markdown(text, container = st):
    container.markdown(text, unsafe_allow_html = True)

def init_page_css():
    markdown("""<style>
      .rounded-corners {display: inline-flex;
                        -webkit-box-align: center;
                        align-items: center;
                        -webkit-box-pack: center;
                        justify-content: center;
                        font-weight: 400;
                        padding: 0.25rem 0.75rem;
                        border-radius: 0.5rem;
                        min-height: 2.5rem;
                        line-height: 1.6;
                        color: inherit;
                        width: 100%;
                        user-select: none;
                        background-color: rgb(255, 255, 255);
                        border: 1px solid rgba(49, 51, 63, 0.2);}       
    </style>""")

    markdown("""<link rel="stylesheet" href="https://fonts.googleapis.com/icon?family=Material+Icons">""")

def generate_chart(data, coder, container = st):
    top = container.columns(2)
    bottom = container.columns(2)

    for idx, current_coder in enumerate(coder):
        fig = {}
        exec(current_coder, locals(), fig)
        fig = fig["fig"]

        if idx < 2:
            top[idx].plotly_chart(fig, use_container_width = True)
        else:
            bottom[idx % 2].plotly_chart(fig, use_container_width = True)

def generate_chart_header(dashboard_title, code_file, container = st):
    container.header(dashboard_title)

    _, downloader = container.columns((.8, .2))
    
    file_name = "code.txt"
    downloader.download_button(""":material/download: Download Code""", 
                                code_file,
                                file_name,
                                use_container_width = True)

def write_stream_text(text):
    for t in text.split(" "):
        yield t + " "
        time.sleep(.1)

def explain_chart(client, data, explainer, container = st):
    if "messages" not in st.session_state:
        st.session_state.messages = [{"role": "Assistant", "content": "<br>".join(explainer)}]

    for message in container.session_state.messages:
        with container.chat_message(message["role"]):
            markdown(f"<p style = 'font-size: 20px; margin-bottom: 0px'><strong>{message['role']}</strong></p>")
            markdown(message["content"])

    if prompt := st.chat_input("Enter your prompt."):
        st.session_state.messages.append({"role": "You", "content": prompt})
        with st.chat_message("User"):
            markdown(f"<p style = 'font-size: 20px; margin-bottom: 0px'><strong>You</strong></p>")
            st.markdown(prompt)

        with st.chat_message("Assistant"):
            markdown(f"<p style = 'font-size: 20px; margin-bottom: 0px'><strong>Assistant</strong></p>")
            
            try:
                msg = st.empty()
    
                response = react_prompt(client, data, prompt)

            except Exception as e:
                response = f"Error occured. ERROR: {e}"

            st.write_stream(write_stream_text(response))

        st.session_state.messages.append({"role": "Assistant", "content": response})

        
