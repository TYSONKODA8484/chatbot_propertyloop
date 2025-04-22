import streamlit as st
import requests
from PIL import Image
import base64

st.set_page_config(page_title="🏡 Real Estate Assistant", layout="centered")
st.title("🏡 Real Estate Chatbot")

API_URL = "http://127.0.0.1:5000/chat"
RESET_URL = "http://127.0.0.1:5000/reset"

# Initialize session state for chat history
if "history" not in st.session_state:
    st.session_state.history = []

# Sidebar Reset Button
with st.sidebar:
    if st.button("🔁 Reset Conversation"):
        requests.post(RESET_URL)
        st.session_state.history.clear()
        st.success("Chat history cleared.")

# Chat Container
chat_container = st.container()
with chat_container:
    for item in st.session_state.history:
        with st.chat_message("user"):
            st.markdown(item["user"])
        with st.chat_message("assistant"):
            st.markdown(item["bot"])

# Input area
with st.chat_message("user"):
    with st.form("chat_form", clear_on_submit=True):
        text = st.text_input("Message", placeholder="Type your question or upload an image...", label_visibility="collapsed")
        location = st.text_input("Your City (optional)", placeholder="e.g. Bangalore", key="location_input")
        uploaded_image = st.file_uploader("Upload property image (optional)", type=["jpg", "jpeg", "png"])
        submitted = st.form_submit_button("Send")

if submitted:
    files = {"image": (uploaded_image.name, uploaded_image, uploaded_image.type)} if uploaded_image else None
    data = {"text": text, "location": location}

    try:
        response = requests.post(API_URL, data=data, files=files)
        bot_reply = response.json().get("reply", "(No reply from server)")
    except Exception as e:
        bot_reply = f"❌ Error: {e}"

    st.session_state.history.append({"user": text or "(image only)", "bot": bot_reply})

    # Refresh the chat UI
    st.rerun()
