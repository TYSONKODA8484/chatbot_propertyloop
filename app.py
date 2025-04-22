from flask import Flask, request, jsonify, session
from flask_session import Session
from flask_cors import CORS
import google.generativeai as genai
from PIL import Image, UnidentifiedImageError
import io
from dotenv import load_dotenv
import os
import secrets

# --- Config ---
# --- Load .env ---
load_dotenv()

# --- Config ---
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-2.0-flash")

# --- App Init ---
app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

# --- Session Config ---
app.config["SESSION_TYPE"] = "filesystem"
app.config["SESSION_FILE_DIR"] = "./flask_session_dir"
app.config["SESSION_PERMANENT"] = False
Session(app)

# --- CORS ---
CORS(app, supports_credentials=True)

# --- Session Helpers ---

History = []
def get_chat_history():
    if "history" not in session:
        session["history"] = []
    return History

def add_to_history(user_msg, bot_msg):
    History.append({"user": user_msg, "bot": bot_msg})
    history = get_chat_history()
    history.append({"user": user_msg, "bot": bot_msg})
    session["history"] = history
    session["last_question"] = user_msg

# --- LLM Location Extractor ---
def extract_location(text):
    history_prompt = "\n".join([f"User: {m['user']}\nBot: {m['bot']}" for m in get_chat_history()])
    prompt = (
        "You are a location extractor for a real estate chatbot.\n"
        "Extract the city or region the user is talking about based on current message and past messages.\n"
        "Only return the name of the place. If unclear, return 'unknown'.\n"
        f"Chat history:\n{history_prompt}\nUser: {text}"
    )
    try:
        response = model.generate_content(prompt)
        location = response.text.strip().split("\n")[0]
        return location if location and location.lower() != "unknown" else None
    except:
        return None

# --- Agent 1 ---
def agent_issue_detector(image_bytes, user_text=""):
    try:
        image = Image.open(io.BytesIO(image_bytes))
        history_prompt = "\n".join([f"User: {m['user']}\nBot: {m['bot']}" for m in get_chat_history()])
        prompt = (
            "You are a property issue detection assistant in an ongoing conversation.\n"
            "Use the uploaded image and any provided text to identify visible property issues.\n"
            "Draw from the previous conversation and location if relevant.\n"
            "Respond naturally with friendly, professional guidance. Limit to 700 characters.\n\n"
            f"{history_prompt}\nUser: {user_text or 'Please analyze the image and describe the problem.'}"
        )
        response = model.generate_content([prompt, image], generation_config={"max_output_tokens": 250})
        reply = response.text.strip()[:700]
        add_to_history(user_text or "(image only)", reply)
        return reply
    except UnidentifiedImageError:
        return "Sorry, I couldn't process the image. Please upload a valid JPG or PNG file."
    except Exception as e:
        return f"Error: {e}"

# --- Agent 2 ---
def agent_faq_handler(question, user_location):
    print(session['history'])
    history_prompt = "\n".join([f"User: {m['user']}\nBot: {m['bot']}" for m in get_chat_history()])
    location_note = f"User location: {user_location}\n" if user_location else ""
    prompt = (
        "You are a tenancy law assistant participating in an ongoing chat.\n"
        "Continue the conversation smoothly using previous messages, user questions, and their location if needed.\n"
        "Do not restart the conversation or repeat greetings.\n"
        "If the user's message is a location only, respond to their last question using the new location.\n"
        "Respond informatively and politely in under 700 characters.\n\n"
        f"{location_note}{history_prompt}\nUser: {question}"
    )
    try:
        response = model.generate_content(prompt, generation_config={"max_output_tokens": 250})
        reply = response.text.strip()[:700]
        add_to_history(question, reply)
        return reply
    except Exception as e:
        return f"Error: {e}"

# --- Intent ---
def classify_intent(text, has_image=False):
    prompt = (
        "You are an intent classifier for a real estate assistant chatbot.\n"
        "Classify the user's request as one of the following types:\n"
        "- 'issue': if they are reporting a visible property problem (like mold, cracks, leaks)\n"
        "- 'faq': if they are asking a question about tenancy, landlords, agreements, or legalities\n"
        "Return only one word: 'issue' or 'faq'.\n"
        f"Image Provided: {has_image}\n"
        f"User: {text}"
    )
    try:
        response = model.generate_content(prompt)
        return response.text.strip().lower()
    except Exception:
        return "faq"

# --- Router ---
def agent_router(text="", image_bytes=None, user_location=None):
    has_image = image_bytes is not None

    if has_image and not text.strip():
        return agent_issue_detector(image_bytes, "")

    intent = classify_intent(text, has_image)
    session["last_intent"] = intent

    if user_location and text.strip().lower() in ["i'm from", "i live in", "i am in", "i stay at"]:
        text = session.get("last_question", text)

    session["last_question"] = text

    if intent == "issue":
        return agent_issue_detector(image_bytes, text)
    elif intent == "faq":
        return agent_faq_handler(text, user_location)
    else:
        return "Please clarify: is this a tenancy-related question or a property issue? You can also upload a photo."

# --- Chat Endpoint ---
@app.route("/chat", methods=["POST"])
def chat():
    text = request.form.get("text", "")
    user_location = request.form.get("location")
    image_file = request.files.get("image")

    if not user_location:
        user_location = session.get("location")
    if not user_location and text:
        extracted = extract_location(text)
        if extracted:
            user_location = extracted
            session["location"] = user_location
    elif user_location:
        session["location"] = user_location

    if image_file:
        image_bytes = image_file.read()
        session["last_image"] = image_bytes
    else:
        image_bytes = session.get("last_image")

    reply = agent_router(text, image_bytes, user_location)
    return jsonify({"reply": reply})

# --- Reset ---
@app.route("/reset", methods=["POST"])
def reset():
    global  History
    History = []
    session.clear()
    return jsonify({"status": "Session cleared."})

# --- Run ---
if __name__ == "__main__":
    app.run(debug=True, port=5000)
