import streamlit as st

import json

def table2text(data):

    prompt = f"""there are {len(data.columns)} columns: {", ".join(data.columns)}. 
    These are the values: 
    """

    table_text = ""
    for row in data.astype(str).values:
        row = ", ".join(row)
        table_text += f"{row}.\n"

    prompt += table_text
    return prompt

def generate_code(client, data, prompt):
    if "chart_response" not in st.session_state:
        
        model = client.responses.create(
            model = "gpt-5", 
            instructions = """
            You are a data analyst, expert in analyzing complex and big data.
            Given the number of columns, column names and the values for each column, perform the 4 exploratory data analysis and provide the dashboard title.
            Assume there are a variable already initialized called data. 
            You should use a python package called plotly to visualize the data.
            The output must contain the first key called title for the dashboard title and second key called charts for the following items in JSON format when the main key is title, code, insights, and importance.
            1. The chart title
            2. The python code to generate the chart
            3. The explainations on the insights of each chart in details
            4. The importance or bussiness values of each chart in details
            """, 
            input = prompt
            
        )

        response = model.output_text

        st.session_state["chart_response"] = response

    response = st.session_state["chart_response"]

    res = response.replace("json", "").replace("```\n", "").replace("```", "")
    res = json.loads(res)

    dashboard_title = res["title"]

    coder = []
    explainer = []

    code_file = f"# {dashboard_title}"

    for assistant in res["charts"]:
        coder.append(assistant["code"].replace("\nfig.show()", ""))
        explainer.append(f"""<p><strong>{assistant["title"]}</strong></p>
                            <p>{assistant["insights"]} {assistant["importance"]}</p>""")

        code_file += f"\n## {assistant['title']}\n\n{assistant['code']}\n"
        
    return dashboard_title, coder, explainer, code_file
    
def react_prompt(client, data, prompt):    
    response = client.responses.create(model = "gpt-5", input = f"""
            You are a data analyst, expert in analyzing complex and big data.
            There is a CSV file called {st.session_state["file_name"]}. 
            {data}

            {prompt}

            """)

    return response.output_text