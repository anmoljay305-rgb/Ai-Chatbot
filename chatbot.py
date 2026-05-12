import streamlit as st
# import random
from pypdf import PdfReader
import speech_recognition as sr
import streamlit.components.v1 as components
# st.cache_resource
# import pyttsx3
# import vector_store
# print(dir(vector_store))

# from sklearn.feature_extraction.text import TfidfVectorizer
# from sklearn.metrics.pairwise import cosine_similarity

def get_voice_input():
    recognizer = sr.Recognizer()

    try:
        with sr.Microphone() as source:
            st.toast("🎤 Listening... Speak now")
            audio = recognizer.listen(source, timeout=3, phrase_time_limit=4)

        text = recognizer.recognize_google(audio)
        return text

    except sr.WaitTimeoutError:
        return "⚠️ Listening timed out"

    except sr.UnknownValueError:
        return "⚠️ Could not understand audio"

    except Exception as e:
        return f"⚠️ Error: {str(e)}"


def speak_text_browser(text):
    safe_text = text.replace("`", "\\`").replace("\n", " ")

    components.html(
        f"""
        <script>
        const text = `{safe_text}`;
        const synth = window.speechSynthesis;

        if (synth.speaking) synth.cancel();

        const utter = new SpeechSynthesisUtterance(text);
        utter.rate = 1;
        utter.pitch = 1;
        utter.lang = "en-US";

        synth.speak(utter);
        </script>
        """,
        height=0,
    )
    recognizer = sr.Recognizer()

    try:
        with sr.Microphone() as source:
            st.toast("🎤 Listening... Speak now")
            audio = recognizer.listen(source, timeout=3, phrase_time_limit=4)

        text = recognizer.recognize_google(audio)
        return text

    except sr.WaitTimeoutError:
        return "⚠️ Listening timed out"

    except sr.UnknownValueError:
        return "⚠️ Could not understand audio"

    except Exception as e:
        return f"⚠️ Error: {str(e)}"


# def speak_text(text):
#     try:
#         import pyttsx3
#         engine = pyttsx3.init()
#         engine.say(text)
#         engine.runAndWait()
#     except:
#         pass

from retriever import get_relevant_docs
from llm import get_llm
from vector_store import create_vector_store
@st.cache_resource
def load_vector_store(text):
    return create_vector_store(text)

def extract_text_from_pdf(uploaded_file):
    text = ""
    reader = PdfReader(uploaded_file)
    for page in reader.pages:
        text += page.extract_text() + " "
    return text


# ------------------ PAGE CONFIG ------------------
st.set_page_config(
    page_title="AI College Assistant | Team Debuggers",
    page_icon="🤖",
    layout="centered"
)
st.markdown(
    "<p style='text-align:center; color:gray;'>🚀 Developed by <b>Team Debuggers</b></p>",
    unsafe_allow_html=True
)



# ------------------ CUSTOM CSS ------------------
st.markdown("""
<style>

/* Background */
body {
    background-color: #0e1117;
}

/* Chat bubbles */
.stChatMessage {
    border-radius: 20px;
    padding: 14px;
    margin-bottom: 12px;
    font-size: 15px;
    max-width: 75%;
}

/* User message */
[data-testid="stChatMessage-user"] {
    background: linear-gradient(135deg, #6a11cb, #2575fc);
    color: white;
    margin-left: auto;
}

/* Bot message */
[data-testid="stChatMessage-assistant"] {
    background: #1f2937;
    color: #e5e7eb;
    margin-right: auto;
}

/* Header */
h1 {
    text-align: center;
    color: #00FFFF;
}

/* Subtitle */
.small-text {
    text-align: center;
    color: #FACC15;
    font-size: 14px;
}

/* Input box */
textarea {
    border-radius: 12px !important;
}

</style>
""", unsafe_allow_html=True)

# ------------------ HEADER ------------------
st.markdown("<h1>🤖 AI College Assistant</h1>", unsafe_allow_html=True)
st.markdown("<p class='small-text'>Your smart offline college helper</p>", unsafe_allow_html=True)
st.info("💡 Try asking: exam, syllabus, placement, attendance")


# ------------------ TRAINING DATA ------------------

# questions = [
#     "hello",
#     "hi",
#     "what is syllabus",
#     "subjects in course",
#     "when is exam",
#     "exam date",
#     "college timing",
#     "working hours",
#     "placement details",
#     "job opportunities",
#     "attendance requirement",
#     "attendance rule",
#     "faculty details",
#     "teachers info"
# ]

# answers = [
#     "Hello! How can I help you today?",
#     "Hi there! Ask me anything about your college.",
#     "Subjects include DBMS, OS, CN, AI, and Software Engineering.",
#     "Subjects include DBMS, OS, CN, AI, and Software Engineering.",
#     "Exams are expected to start from 10th May.",
#     "Exams are expected to start from 10th May.",
#     "College timing is 9:00 AM to 4:00 PM.",
#     "College timing is 9:00 AM to 4:00 PM.",
#     "Top companies visit for campus placements every year.",
#     "Top companies visit for campus placements every year.",
#     "Minimum 75% attendance is required.",
#     "Minimum 75% attendance is required.",
#     "Our faculty members are highly experienced.",
#     "Our faculty members are highly experienced."
# ]

# ------------------ MODEL ------------------

# vectorizer = TfidfVectorizer()
# X = vectorizer.fit_transform(questions)
#-----------------------SEARCH PDF  -------------------------------
# def search_pdf(user_input, pdf_text):

    # Better splitting (VERY IMPORTANT)
    # chunks = pdf_text.split("\n")

    # best_match = ""
    # max_score = 0

    # user_words = user_input.lower().split()

    # for chunk in chunks:
    #     chunk_lower = chunk.lower()

    #     score = sum(1 for word in user_words if word in chunk_lower)

    #     # Extra weight if full phrase appears
    #     if user_input.lower() in chunk_lower:
    #         score += 5

    #     if score > max_score:
    #         max_score = score
    #         best_match = chunk

    # return best_match if max_score > 0 else ""

    # ---------------- COLLEGE DATA ----------------

college_data = {
    "hello": "Hello! How can I help you today?.",
    "exam" : "Exams are expected to start from 10th May.",
    "syllabus": "Subjects include DBMS, OS, CN, AI.",
    "timing": "College timing is 9 AM to 4 PM.",
    "placement": "Top companies visit campus.",
    "attendance": "Minimum 75% attendance required."
}

def get_college_response(user_input):
    # 🔒 Safety check (VERY IMPORTANT)
    if not user_input:
        return None

    user_input = user_input.lower()

    for key in college_data:
        if key in user_input:
            return college_data[key]

    return None

# ------------------ RESPONSE FUNCTION ------------------
# if query:

#     st.session_state.messages.append({"role": "user", "content": query})

    # 🔵 STEP 1: Check College Assistant
    # college_response = get_college_response(query)

    # if college_response:
    #     response = college_response

    # else:
    #     # 🔵 STEP 2: PDF RAG system
    #     relevant_docs = get_relevant_docs(db, query)
    #     context = " ".join([doc.page_content for doc in relevant_docs])

    #     llm = get_llm()

    #     prompt = f"""
    #     Answer the question using the context below:

    #     Context:
    #     {context}

    #     Question:
    #     {query}
    #     """

    #     response = llm.predict(prompt)

    # Show response
    # st.session_state.messages.append({"role": "assistant", "content": response})

#     with st.chat_message("assistant"):
#         st.write(response)

# # ------------------ SESSION ------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

# ------------------ CHAT DISPLAY ------------------
uploaded_file = st.file_uploader("📄 Upload PDF Notes", type="pdf")
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])



# ------------------ INPUT ------------------

# if uploaded_file:
#     text = extract_text_from_pdf(uploaded_file)
#     db = create_vector_store(text)   # from embeddings.py

# ---------------- RESPONSE MODE ----------------
response_mode = st.radio(
    "Choose Response Mode",
    ["Text Only", "Voice + Text"],
    horizontal=True
)
# ---------------- USER INPUT ----------------
response = None
input_col, mic_col = st.columns([6, 1])

with input_col:
    prompt = st.chat_input("💬 Ask something...")

with mic_col:
    if st.button("🎤", use_container_width=True):
        voice_text = get_voice_input()
        prompt = voice_text

if prompt:
    prompt = str(prompt)

    # ---------------- USER MESSAGE ----------------
    with st.chat_message("user"):
        st.markdown(prompt)

    # ---------------- STEP 1: COLLEGE RESPONSE ----------------
    college_response = get_college_response(prompt)

    if college_response:
        response = college_response

    # ---------------- STEP 2: PDF RAG ----------------
    elif uploaded_file:

        # Create DB once
        if "db" not in st.session_state:
            text = extract_text_from_pdf(uploaded_file)
            if not text or text.strip() == "":
                 st.error("❌ This PDF contains no readable text. Please upload a proper notes/document PDF.")
                 st.stop()
                 
            st.session_state.db = load_vector_store(text)

        db = st.session_state.db

        if prompt.strip() == "":
            response = "⚠️ Please enter a valid question."

        else:
            relevant_docs = get_relevant_docs(db, prompt)

            if not relevant_docs:
                response = "❌ No relevant content found in PDF."

            else:
                # -------- CONTEXT --------
                context = " ".join([doc.page_content for doc in relevant_docs])
                lines = context.split("\n")

                # -------- FILTERING --------
                filtered_lines = []
                for line in lines:
                    line = line.strip()
                    if (
                        len(line) > 40
                        and not line.lower().startswith("http")
                        and "www." not in line.lower()
                        and "http" not in line.lower()
                        and "reference" not in line.lower()
                        and "conclusion" not in line.lower()
                    ):
                        filtered_lines.append(line)

                # -------- SCORING --------
                query_words = prompt.lower().split()
                scored_lines = []

                for line in filtered_lines:
                    score = sum(word in line.lower() for word in query_words)
                    if score > 0:
                        scored_lines.append((score, line))

                scored_lines.sort(reverse=True)

                # -------- BEST LINES --------
                best_lines = [line for _, line in scored_lines[:5]]

                # -------- FINAL RESPONSE --------
                if best_lines:
                    main = best_lines[0]
                    explanation = " ".join(best_lines[1:3]) if len(best_lines) > 1 else ""

                    response = f"""📘 **Answer:**

{main}

➡️ **Explanation:**
{explanation}
"""
                else:
                    response = "❌ No clear answer found in the PDF."

    # ---------------- STEP 3: NO PDF ----------------
    else:
        response = "⚠️ Upload a PDF or ask college-related questions."

    # ---------------- DISPLAY RESPONSE ----------------
# ---------------- DISPLAY RESPONSE ----------------
if response:

    with st.chat_message("assistant"):

        st.markdown(response)

        # 🔊 Voice response
        if response_mode == "Voice + Text" and len(response) < 500:
            speak_text_browser(response)

    st.session_state.messages.append({
        "role": "assistant",
        "content": response
    })