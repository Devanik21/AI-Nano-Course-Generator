# /app.py
import streamlit as st
import google.generativeai as genai
import os
import json
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# --- Helper Functions ---

def get_gemini_api_key():
    """
    Retrieves the Gemini API key from Streamlit secrets or environment variables.
    """
    # First, try to get the key from Streamlit's secrets
    if 'GEMINI_API_KEY' in st.secrets:
        return st.secrets['GEMINI_API_KEY']
    # If not in secrets, try to get it from the .env file (loaded by dotenv)
    return os.getenv("GOOGLE_API_KEY")

def generate_course_content(topic, api_key):
    """
    Generates course content using the Gemini API.
    """
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-pro')

        prompt = f"""
        You are an expert instructional designer. Your task is to create a nano-course on the topic: "{topic}".
        The entire course should be concise and digestible in about 5 minutes.

        Please provide the output in a single, valid JSON object. Do not include any text, code block formatting, or explanations outside of the JSON object.

        The JSON object must have the following structure:
        {{
          "topic": "{topic}",
          "lesson": {{
            "title": "A catchy title for the lesson",
            "content": "A concise, engaging micro-lesson on the topic. Use markdown for formatting (e.g., bolding, bullet points)."
          }},
          "quiz": [
            {{
              "question": "Quiz question 1?",
              "options": ["Option A", "Option B", "Option C", "Option D"],
              "answer": "The correct option text"
            }},
            {{
              "question": "Quiz question 2?",
              "options": ["Option A", "Option B", "Option C", "Option D"],
              "answer": "The correct option text"
            }},
            {{
              "question": "Quiz question 3?",
              "options": ["Option A", "Option B", "Option C", "Option D"],
              "answer": "The correct option text"
            }}
          ],
          "flashcards": [
            {{
              "term": "Key Term 1",
              "definition": "Definition for Key Term 1."
            }},
            {{
              "term": "Key Term 2",
              "definition": "Definition for Key Term 2."
            }},
            {{
              "term": "Key Term 3",
              "definition": "Definition for Key Term 3."
            }}
          ],
          "example": {{
            "title": "A title for the example (e.g., 'Python Code Snippet', 'Baking Measurement Conversion')",
            "language": "The language for syntax highlighting (e.g., 'python', 'bash', 'text'). Use 'text' if not a programming language.",
            "code": "The example code or text snippet."
          }}
        }}

        If the topic is not technical and a code snippet is irrelevant, set the 'example' field to null.
        """

        response = model.generate_content(prompt)
        # The response.text might be enclosed in ```json ... ```, so we clean it.
        cleaned_response = response.text.strip().lstrip("```json").rstrip("```")
        return json.loads(cleaned_response)

    except Exception as e:
        st.error(f"An error occurred: {e}")
        return None

# --- Streamlit App UI ---

st.set_page_config(page_title="Nano-Course Generator", page_icon="🎓", layout="wide")

st.title("🎓 Nano-Course Generator")
st.write("Pick any topic, and Gemini will instantly create a 5-minute micro-lesson complete with a quiz, flashcards, and examples.")

# Initialize session state
if 'course_content' not in st.session_state:
    st.session_state.course_content = None
if 'quiz_submitted' not in st.session_state:
    st.session_state.quiz_submitted = False

# API Key Management
api_key = get_gemini_api_key()
if not api_key:
    st.sidebar.warning("Google API Key not found.")
    api_key = st.sidebar.text_input("Enter your Google API Key:", type="password", key="api_key_input")
    if api_key:
        st.sidebar.success("API Key loaded!")

# User Input
topic = st.text_input("Enter a topic to learn about:", "Introduction to Quantum Computing")

if st.button("Generate Course", disabled=not api_key):
    if topic:
        with st.spinner("Generating your nano-course... This may take a moment."):
            course_data = generate_course_content(topic, api_key)
            st.session_state.course_content = course_data
            st.session_state.quiz_submitted = False # Reset quiz state
            if course_data:
                st.success("Your course is ready!")
            else:
                st.error("Failed to generate course content. Please check your API key and try again.")
    else:
        st.warning("Please enter a topic.")

# --- Display Generated Content ---

if st.session_state.course_content:
    course = st.session_state.course_content
    st.header(f"📚 Lesson: {course['lesson']['title']}")
    st.markdown(course['lesson']['content'])

    st.divider()

    # --- Display Quiz ---
    st.header("🧠 Quiz Time!")
    if not st.session_state.quiz_submitted:
        with st.form("quiz_form"):
            user_answers = []
            for i, q in enumerate(course['quiz']):
                user_answers.append(st.radio(f"**{i+1}. {q['question']}**", q['options'], key=f"q{i}"))

            submitted = st.form_submit_button("Submit Answers")
            if submitted:
                st.session_state.quiz_submitted = True
                st.session_state.user_answers = user_answers
                st.rerun() # Rerun to display results immediately
    else:
        score = 0
        for i, q in enumerate(course['quiz']):
            user_answer = st.session_state.user_answers[i]
            correct_answer = q['answer']
            if user_answer == correct_answer:
                score += 1
                st.success(f"**Question {i+1}: Correct!** {q['question']}\n\nYour answer: `{user_answer}`")
            else:
                st.error(f"**Question {i+1}: Incorrect.** {q['question']}\n\nYour answer: `{user_answer}`\n\nCorrect answer: `{correct_answer}`")
        st.subheader(f"Your final score: {score}/{len(course['quiz'])}")
        if st.button("Try Quiz Again"):
            st.session_state.quiz_submitted = False
            st.rerun()

    st.divider()

    # --- Display Flashcards ---
    st.header("🃏 Flashcards")
    for card in course['flashcards']:
        with st.expander(f"**{card['term']}**"):
            st.write(card['definition'])

    st.divider()

    # --- Display Example ---
    if course.get('example') and course['example'].get('code'):
        st.header(f"💻 {course['example']['title']}")
        st.code(course['example']['code'], language=course['example']['language'])

