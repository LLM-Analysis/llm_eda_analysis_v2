import streamlit as st
import pandas as pd

from page_utils import *
from backend_utils import *

from openai import OpenAI

st.set_page_config(layout = "wide")
markdown("<h3>Exploratory Data Analysis with Generative AI</h3>")

init_page_css()

file = st.sidebar.file_uploader("Choose a CSV", accept_multiple_files = False)

if file is not None:
    if "file_name" not in st.session_state:
        st.session_state["file_name"] = file.name
    
    if "chart_response" in st.session_state and file.name != st.session_state["file_name"]:
        del st.session_state["chart_response"]
        del st.session_state["messages"]

    st.session_state["file_name"] = file.name

    data = pd.read_csv(file).head(5)
    api_key = st.sidebar.text_input("API Key")

    if api_key == "":
        st.info("Enter your API Key to continue.")

    else:
        client = OpenAI(api_key = api_key)

        text = table2text(data)
        n_rows = len(data)

        data = data.head(n_rows)
        prompt = table2text(data)
        
        if "progress_text" not in st.session_state:
            st.session_state["progress_text"] = {"val": 0, "text": "Analyzing the dataset"}
            st.session_state["re-attempt"] = 0

        my_bar = st.progress(st.session_state["progress_text"]["val"], 
                                text = st.session_state["progress_text"]["text"])

        try:
            
            dashboard_title, coder, explainer, code_file = generate_code(client, data, prompt)
            generate_chart(data, coder)

            my_bar.progress(50, text = "Generating charts")

        except Exception as e:
            st.write(e)
            if "chart_response" in st.session_state:
                del st.session_state["chart_response"]
            
            st.session_state['re-attempt'] += 1
            st.session_state["progress_text"] = {"val": 50, 
                                                    "text": f"{st.session_state['re-attempt']} attempt(s) to regenerate the charts"}

            st.rerun()

        my_bar.progress(100, "Done")
        my_bar.empty()

        generate_chart_header(dashboard_title, code_file)
        
        explain_chart(client, prompt, explainer)
        
        st.session_state["progress_text"] = {"val": 0, "text": "Analyzing the dataset"}
        st.session_state['re-attempt'] = 0

else:
    st.info("Upload your CSV to continue.")