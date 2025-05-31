# Multi-Agent Real Estate Assistant Chatbot

## Project Title
**Multi-Agent Real Estate Assistant (Text + Image Enabled)**

### Links
- **Live Demo**: [propertyloop-chatbot.onrender.com](https://propertyloop-chatbot.onrender.com)
- **Frontend GitHub**: [PropertyLoop-Chatbot](https://github.com/TYSONKODA8484/PropertyLoop-Chatbot)
- **Backend GitHub**: [chatbot_propertyloop](https://github.com/TYSONKODA8484/chatbot_propertyloop)

---

## Submission Summary

### Tools & Technologies

| Component       | Technology Used                                      |
|----------------|------------------------------------------------------|
| Frontend        | Bolt (UI Scaffolding), ReactJS                       |
| Backend         | Python 3, Flask, Flask-Session, Flask-CORS, dotenv  |
| AI/LLM          | Gemini 2.0 Flash (Text + Image multimodal)          |
| Image Handling  | Pillow (PIL) for validation and conversion           |
| Testing         | Streamlit for API prototype                          |
| Deployment      | Render (Frontend static + Flask backend API)        |
| API             | RESTful API (`/chat`, `/reset`)                     |

---

## Agent Responsibilities

### Agent 1: Property Issue Detector
- Accepts image inputs (with/without text)
- Identifies issues like mold, leakage, cracks
- Uses image + text + chat context + location
- Response limited to 700 characters

### Agent 2: Tenancy FAQ Assistant
- Handles text-only queries
- Understands location-specific laws (notice period, rent increase)
- Remembers session context
- Offers friendly, jurisdiction-aware advice

---

## Multi-Agent Routing Logic

### Overview
This system dynamically routes inputs to the correct agent using format, keywords, and prior context.

### Logic Functions:
- `classify_intent(text, has_image)` → Gemini classifies input as `issue` or `faq`
- `extract_location(text)` → Extracts location from history/message
- `agent_router(text, image, location)` → Directs request to Agent 1 or 2

### Decision Flow:

1. Image Only → Agent 1  
2. Image + Text → Gemini determines context → Route to Agent 1 or 2  
3. Text Only → Classified based on keywords  
4. Location Handling  
   - If shared, stored in session
   - Otherwise, extracted from conversation  
5. Session Management  
   - Tracks: location, last image, last intent, chat history

### Fallbacks:
- "Please clarify: is this a tenancy-related question or a property issue?"
- "Could you please tell me which city or region you’re referring to?"

---

## Use Case Examples

| Input Type     | Input Example                          | Agent   | Output Example |
|----------------|----------------------------------------|---------|----------------|
| Image Only     | Photo of wall mold                     | Agent 1 | "This appears to be mold..." |
| Image + Text   | Crack image + "What is this?"          | Agent 1 | "Structural crack detected..." |
| Text Only      | "Can landlord increase rent mid-lease?"| Agent 2 | "Not unless stated in agreement..." |
| Text Only      | "Landlord not returning deposit"       | Agent 2 | "Must be returned within 30 days..." |
| Location Only  | "I live in Delhi now"                  | Agent 2 | Session updated, jurisdiction updated |

---

## Final Test Scenario

| Step | User Input                                      | Type         | Target Agent | Feature Tested                     |
|------|--------------------------------------------------|--------------|--------------|------------------------------------|
| 1    | "Landlord keeps entering without permission"     | Text         | Agent 2      | FAQ + privacy                      |
| 2    | "I live in Pune"                                 | Text         | Agent 2      | Location follow-up                 |
| 3    | [Upload mold image]                              | Image Only   | Agent 1      | Visual issue handling              |
| 4    | "What if I don’t pay rent until he fixes it?"    | Text         | Agent 2      | Contextual advice                  |
| 5    | "Look at this crack" + [Upload image]            | Image + Text | Agent 1      | Multi-modal input                  |
| 6    | "Can I deduct this from my rent?"                | Text         | Agent 2      | Follow-up retention                |
| 7    | "asdfghjkl"                                      | Invalid Text | Agent 2      | Fallback handling                  |
| 8    | "I’m in Delhi now."                              | Text         | Agent 2      | Location override                  |
| 9    | "What’s the notice period here?"                 | Text         | Agent 2      | Jurisdictional knowledge           |
| 10   | "Reset everything"                               | Command      | API Reset    | Memory wipe                        |

---

## Image Issue Detection (Agent 1)

### Input:
- JPG/PNG (via form upload)
- Optional accompanying user text

### Process:
- Loaded using PIL
- Prompt passed to Gemini:
  > "You are a property issue detection assistant... Use image + text + location..."

### Output:
- e.g., “I see dampness near the ceiling. Likely water seepage. Suggest contacting a plumber.”

---

## Tenancy FAQ Handler (Agent 2)

### Input:
- Text-based tenancy query

### Process:
- Gemini called with:
  > "You are a tenancy law assistant... Use previous chat + new message..."

### Output:
- e.g., "In Bangalore, 30 days' notice is required. Ensure it’s written."

---

## Deployment on Render

### Backend (Flask API)
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `gunicorn app:app --bind 0.0.0.0:5000`

### Frontend (React + Bolt)
- **Build**: `npm run build`
- **Publish Directory**: `/build`

### Environment Variable:
```env
GEMINI_API_KEY = [Your Google API Key]
