import streamlit as st
import requests
import pandas as pd
import uuid

API_URL = "http://localhost:8080/ask"  # Replace with your FastAPI endpoint

st.set_page_config(page_title="IT Support Assistant", layout="centered")

# --- Session state initialization ---
if "chat_blocks" not in st.session_state:
    st.session_state.chat_blocks = []

if "messages" not in st.session_state:
    st.session_state.messages = []

if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

session_id = st.session_state.session_id
print('\nsession_id >', session_id)

# --- Title ---
st.title("💬 Talk to the IT Support Assistant")

# --- Display chat history ---
for idx, block in enumerate(st.session_state.chat_blocks):
    st.markdown(f"**🧍 You:** {block['user_query']}")

    st.markdown("##### 🧠 Bot reply")
    if block['message'] == "Sorry, I am unable to answer your query at the moment.":
        st.error(block['message'])
    else:
        st.success(block['message'])

    if block['token_usage']:
        st.markdown("##### 💰 Tokens used Breakdown")
        tokens_table = pd.DataFrame([
            {"Type": "Input", "Tokens": block['token_usage'].get("input_tokens", 0)},
            {"Type": "Output", "Tokens": block['token_usage'].get("output_tokens", 0)},
        ])
        st.table(tokens_table)

# --- API Call Function ---
def call_api(query):
    payload = {
        "user_query": query,
        "session_id": session_id
    }

    try:
        response = requests.post(API_URL, json=payload)
        response.raise_for_status()
        data = response.json()

        if data.get("success") == 1:
            return data
        else:
            return {"message": "Sorry, something went wrong.", "token_usage": None}
    except Exception as e:
        return {"message": "Sorry, I am unable to answer your query at the moment.", "token_usage": None}

# --- User input form ---
with st.form("chat_form", clear_on_submit=False):
    user_query = st.text_input("Ask your question:", key="user_query")
    submitted = st.form_submit_button("Submit")

# --- Handle submission ---
if submitted and user_query.strip() != "":
    with st.spinner("⏳ Getting response..."):
        data = call_api(user_query)

    if data:
        message = data['message']
        tokens = data.get('token_usage', None)

        st.session_state.chat_blocks.append({
            "user_query": user_query,
            "message": message,
            "token_usage": tokens
        })

        st.rerun()