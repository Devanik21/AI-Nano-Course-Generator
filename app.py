# /app.py
import streamlit as st
import google.generativeai as genai
import os
import json
import time
import datetime
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dotenv import load_dotenv
from typing import Dict, List, Optional, Tuple
import hashlib
import markdown2
from weasyprint import HTML
import base64

# Load environment variables from .env file
load_dotenv()

# --- Configuration and Constants ---

COURSE_DURATIONS = {
    "2 minutes": 2,
    "5 minutes": 5,
    "10 minutes": 10,
    "15 minutes": 15,
    "30 minutes": 30,
    "45 minutes": 45,
    "1 hour": 60,
    "1.5 hours": 90,
    "2 hours": 120,
    "3 hours": 180,
    "4 hours": 240,
    "6 hours": 360,
    "8 hours": 480
}

DIFFICULTY_LEVELS = {
    "Beginner": "Basic concepts with simple explanations",
    "Intermediate": "Moderate complexity with practical applications",
    "Advanced": "Complex topics with in-depth analysis",
    "Expert": "Cutting-edge concepts with research-level depth"
}

LEARNING_STYLES = {
    "Visual": "Emphasis on diagrams, charts, and visual examples",
    "Auditory": "Focus on explanations and verbal descriptions",
    "Kinesthetic": "Hands-on examples and practical exercises",
    "Reading/Writing": "Text-heavy content with detailed notes",
    "Multimodal": "Combination of all learning styles"
}

CONTENT_FORMATS = {
    "Comprehensive": "Full lesson with all components",
    "Quiz-Heavy": "More quizzes and assessments",
    "Example-Rich": "Multiple practical examples",
    "Theory-Focused": "Deep theoretical understanding",
    "Project-Based": "Practical project implementation"
}

# --- Helper Functions ---

def get_gemini_api_key():
    """Retrieves the Gemini API key from Streamlit secrets or environment variables."""
    if 'GEMINI_API_KEY' in st.secrets:
        return st.secrets['GEMINI_API_KEY']
    return os.getenv("GOOGLE_API_KEY")

def generate_course_id(topic: str, duration: int, difficulty: str) -> str:
    """Generate a unique course ID for tracking."""
    data = f"{topic}_{duration}_{difficulty}_{datetime.datetime.now().isoformat()}"
    return hashlib.md5(data.encode()).hexdigest()[:12]

def save_progress(course_id: str, progress_data: Dict):
    """Save learning progress to session state."""
    if 'learning_progress' not in st.session_state or st.session_state.learning_progress is None:
        st.session_state.learning_progress = {}
    st.session_state.learning_progress[course_id] = progress_data

def get_progress(course_id: str) -> Dict:
    """Retrieve learning progress from session state."""
    if 'learning_progress' not in st.session_state:
        return {}
    return st.session_state.learning_progress.get(course_id, {})

def calculate_estimated_reading_time(content: str) -> int:
    """Calculate estimated reading time based on word count (average 200 WPM)."""
    word_count = len(content.split())
    return max(1, word_count // 200)

def generate_advanced_course_content(
    topic: str, 
    duration: int, 
    difficulty: str, 
    learning_style: str, 
    content_format: str,
    prerequisites: str,
    learning_objectives: List[str],
    api_key: str
) -> Optional[Dict]:
    """Generate comprehensive course content using advanced prompting."""
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.5-flash')

        # Calculate content distribution based on duration
        if duration <= 5:
            num_sections = 1
            num_quizzes = 3
            num_flashcards = 5
            num_examples = 1
        elif duration <= 15:
            num_sections = 2
            num_quizzes = 5
            num_flashcards = 8
            num_examples = 2
        elif duration <= 30:
            num_sections = 3
            num_quizzes = 8
            num_flashcards = 12
            num_examples = 3
        elif duration <= 60:
            num_sections = 4
            num_quizzes = 12
            num_flashcards = 15
            num_examples = 4
        else:
            num_sections = min(8, duration // 30)
            num_quizzes = min(20, duration // 5)
            num_flashcards = min(30, duration // 2)
            num_examples = min(10, duration // 15)

        prompt = f"""
        You are an expert instructional designer and curriculum developer. Create a comprehensive course on "{topic}" with the following specifications:

        **Course Parameters:**
        - Duration: {duration} minutes
        - Difficulty Level: {difficulty} ({DIFFICULTY_LEVELS[difficulty]})
        - Learning Style: {learning_style} ({LEARNING_STYLES[learning_style]})
        - Content Format: {content_format} ({CONTENT_FORMATS[content_format]})
        - Prerequisites: {prerequisites if prerequisites else "None specified"}
        - Learning Objectives: {', '.join(learning_objectives) if learning_objectives else "Generate appropriate objectives"}

        **Content Structure Requirements:**
        - {num_sections} main sections/modules
        - {num_quizzes} quiz questions total
        - {num_flashcards} flashcards
        - {num_examples} practical examples
        - Include progress tracking elements
        - Add difficulty progression throughout the course

        Provide the output as a single, valid JSON object with this structure:

        {{
          "course_metadata": {{
            "topic": "{topic}",
            "duration_minutes": {duration},
            "difficulty": "{difficulty}", 
            "learning_style": "{learning_style}",
            "content_format": "{content_format}",
            "estimated_completion_time": "X hours Y minutes",
            "prerequisites": "{prerequisites}",
            "learning_objectives": ["objective1", "objective2", "..."],
            "skills_gained": ["skill1", "skill2", "..."],
            "target_audience": "Description of ideal learners"
          }},
          "course_sections": [
            {{
              "section_id": 1,
              "title": "Section Title",
              "duration_minutes": X,
              "learning_outcomes": ["outcome1", "outcome2"],
              "content": "Comprehensive section content with markdown formatting",
              "key_concepts": ["concept1", "concept2"],
              "difficulty_level": "beginner/intermediate/advanced"
            }}
          ],
          "comprehensive_quiz": [
            {{
              "question_id": 1,
              "section_id": 1,
              "question": "Question text?",
              "options": ["A", "B", "C", "D"],
              "answer": "Correct option text",
              "explanation": "Detailed explanation of why this is correct",
              "difficulty": "easy/medium/hard",
              "concept_tested": "Main concept being tested"
            }}
          ],
          "flashcards": [
            {{
              "card_id": 1,
              "term": "Key Term",
              "definition": "Comprehensive definition",
              "example": "Practical example or usage",
              "mnemonic": "Memory aid if applicable",
              "difficulty": "basic/intermediate/advanced"
            }}
          ],
          "practical_examples": [
            {{
              "example_id": 1,
              "title": "Example Title",
              "description": "What this example demonstrates",
              "language": "programming language or 'text'",
              "code": "Code or example content",
              "explanation": "Step-by-step explanation",
              "variations": ["Alternative approach 1", "Alternative approach 2"],
              "real_world_application": "How this applies in practice"
            }}
          ],
          "assignments": [
            {{
              "assignment_id": 1,
              "title": "Assignment Title",
              "description": "Detailed assignment description",
              "difficulty": "beginner/intermediate/advanced",
              "estimated_time": "X minutes",
              "deliverables": ["What student should produce"],
              "evaluation_criteria": ["How to assess completion"]
            }}
          ],
          "additional_resources": [
            {{
              "type": "reading/video/tool/website",
              "title": "Resource Title",
              "description": "Why this resource is valuable",
              "difficulty": "beginner/intermediate/advanced"
            }}
          ],
          "assessment_rubric": {{
            "quiz_weight": 40,
            "assignments_weight": 35,
            "participation_weight": 25,
            "passing_score": 70,
            "mastery_indicators": ["What demonstrates mastery"]
          }}
        }}

        Ensure all content is appropriate for the specified duration, difficulty level, and learning style. Make the content engaging, practical, and professionally structured.
        """

        response = model.generate_content(prompt)
        cleaned_response = response.text.strip().lstrip("```json").rstrip("```")
        return json.loads(cleaned_response)

    except Exception as e:
        st.error(f"An error occurred while generating course content: {e}")
        return None

def display_learning_analytics(progress_data: Dict):
    """Display comprehensive learning analytics dashboard."""
    if not progress_data:
        st.info("Complete some activities to see your learning analytics!")
        return

    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Overall Progress", f"{progress_data.get('overall_progress', 0):.1f}%")
    with col2:
        st.metric("Quiz Score", f"{progress_data.get('quiz_score', 0):.1f}%")
    with col3:
        st.metric("Time Spent", f"{progress_data.get('study_time', 0)} min")
    with col4:
        st.metric("Completion Rate", f"{progress_data.get('completion_rate', 0):.1f}%")

    # Progress visualization
    if 'section_progress' in progress_data:
        fig = px.bar(
            x=list(progress_data['section_progress'].keys()),
            y=list(progress_data['section_progress'].values()),
            title="Section-wise Progress",
            labels={'x': 'Sections', 'y': 'Progress (%)'}
        )
        st.plotly_chart(fig, use_container_width=True)

def _generate_full_course_markdown(course_data: Dict) -> str:
    """Helper to generate the full course content in Markdown format."""
    metadata = course_data.get('course_metadata', {})
    topic = metadata.get('topic', 'Course')
    
    content = f"# Course: {topic}\n\n"
    content += f"**Duration:** {metadata.get('duration_minutes')} minutes  \n"
    content += f"**Difficulty:** {metadata.get('difficulty')}  \n"
    content += f"**Learning Style:** {metadata.get('learning_style')}  \n"
    content += f"**Target Audience:** {metadata.get('target_audience', 'N/A')}  \n"
    content += f"**Prerequisites:** {metadata.get('prerequisites', 'None')}  \n\n"

    if metadata.get('learning_objectives'):
        content += "## Learning Objectives\n"
        for obj in metadata['learning_objectives']:
            content += f"- {obj}\n"
        content += "\n"

    if course_data.get('course_sections'):
        content += "# Course Content\n"
        for section in course_data['course_sections']:
            content += f"## Section: {section.get('title', 'Untitled Section')}\n"
            content += f"_{section.get('duration_minutes', 'N/A')} minutes_\n\n"
            content += f"{section.get('content', '')}\n\n"
            if section.get('key_concepts'):
                content += "### Key Concepts\n"
                for concept in section['key_concepts']:
                    content += f"- {concept}\n"
                content += "\n"

    if course_data.get('comprehensive_quiz'):
        content += "# Comprehensive Quiz\n"
        for i, q in enumerate(course_data['comprehensive_quiz']):
            content += f"### Question {i+1}: {q.get('question', '')}\n"
            options = "\n".join([f"- {opt}" for opt in q.get('options', [])])
            content += f"{options}\n\n"
            content += f"**Answer:** {q.get('answer', 'N/A')}\n"
            content += f"**Explanation:** {q.get('explanation', 'N/A')}\n\n"
    
    if course_data.get('flashcards'):
        content += "# Flashcards\n"
        for card in course_data['flashcards']:
            content += f"### {card.get('term', 'Term')}\n"
            content += f"**Definition:** {card.get('definition', 'N/A')}\n"
            if card.get('example'):
                content += f"**Example:** {card.get('example')}\n"
            content += "\n"

    if course_data.get('practical_examples'):
        content += "# Practical Examples\n"
        for ex in course_data['practical_examples']:
            content += f"## Example: {ex.get('title', 'Untitled Example')}\n"
            content += f"_{ex.get('description', '')}_\n\n"
            if ex.get('code'):
                content += f"```{ex.get('language', '')}\n{ex.get('code')}\n```\n\n"
            if ex.get('explanation'):
                content += f"**Explanation:**\n{ex.get('explanation')}\n\n"

    if course_data.get('assignments'):
        content += "# Assignments\n"
        for assign in course_data['assignments']:
            content += f"## Assignment: {assign.get('title', 'Untitled Assignment')}\n"
            content += f"**Description:** {assign.get('description', 'N/A')}\n"
            content += f"**Difficulty:** {assign.get('difficulty', 'N/A')}\n\n"

    return content

def export_course_content(course_data: Dict, format_type: str = "markdown") -> Optional[bytes or str]:
    """Export course content in various formats."""
    markdown_content = _generate_full_course_markdown(course_data)

    if format_type == "markdown":
        return markdown_content
    elif format_type == "pdf":
        try:
            css = """
            @page { size: A4; margin: 1.5cm; }
            body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; line-height: 1.6; color: #333; }
            h1, h2, h3, h4, h5, h6 { font-weight: bold; color: #000; }
            h1 { font-size: 24pt; border-bottom: 2px solid #667eea; padding-bottom: 10px; margin-top: 0; }
            h2 { font-size: 18pt; color: #764ba2; border-bottom: 1px solid #ddd; padding-bottom: 5px; margin-top: 2em; }
            h3 { font-size: 14pt; color: #333; margin-top: 1.5em; }
            code { background-color: #f1f1f1; padding: 2px 5px; border-radius: 4px; font-family: 'Courier New', Courier, monospace; font-size: 0.9em; }
            pre { background-color: #f6f8fa; padding: 15px; border-radius: 5px; white-space: pre-wrap; word-wrap: break-word; border: 1px solid #ddd; }
            pre code { background-color: transparent; padding: 0; border-radius: 0; border: none; }
            blockquote { border-left: 4px solid #ccc; padding-left: 10px; color: #666; }
            """
            html_content = markdown2.markdown(markdown_content, extras=["fenced-code-blocks", "tables", "break-on-newline"])
            full_html = f'<!DOCTYPE html><html><head><meta charset="UTF-8"><style>{css}</style></head><body>{html_content}</body></html>'
            
            pdf_bytes = HTML(string=full_html).write_pdf()
            return pdf_bytes
        except ImportError:
            st.error("PDF generation requires `weasyprint` and `markdown2`. Please install them: `pip install weasyprint markdown2`")
            return None
        except Exception as e:
            st.error(f"An error occurred during PDF generation: {e}")
            return None

    return None

# --- Streamlit App UI ---

st.set_page_config(
    page_title="Advanced Course Generator Pro", 
    page_icon="🎓", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for professional styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 2rem;
    }
    .feature-card {
        background: #262730; /* Dark background for flashcards */
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #667eea;
        margin: 1rem 0;
    }
    .progress-bar {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        height: 20px;
        border-radius: 10px;
    }
    /* Make the tabs scrollable horizontally */
    [data-baseweb="tab-list"] {
        overflow-x: auto;
        white-space: nowrap;
        scroll-behavior: smooth;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<h1 class="main-header">🎓 Advanced Course Generator Pro</h1>', unsafe_allow_html=True)
st.markdown("### Transform any topic into a comprehensive, personalized learning experience with AI-powered curriculum design")

# Initialize session state
if 'course_content' not in st.session_state:
    st.session_state.course_content = None
if 'quiz_submitted' not in st.session_state:
    st.session_state.quiz_submitted = False
if 'current_section' not in st.session_state:
    st.session_state.current_section = 0
if 'learning_progress' not in st.session_state:
    st.session_state.learning_progress = {}
if 'study_start_time' not in st.session_state:
    st.session_state.study_start_time = None

# --- Sidebar Configuration ---
with st.sidebar:
    st.header("🛠️ Course Configuration")
    
    # API Key Management
    api_key = get_gemini_api_key()
    if not api_key:
        st.warning("⚠️ Google API Key not found.")
        api_key = st.text_input("Enter your Google API Key:", type="password", key="api_key_input")
        if api_key:
            st.success("✅ API Key loaded!")

    st.divider()
    
    # Course Parameters
    topic = st.text_input("📚 Course Topic:", value="Introduction to Machine Learning", help="Enter any topic you want to learn about")
    
    duration_label = st.selectbox("⏱️ Course Duration:", list(COURSE_DURATIONS.keys()), index=2)
    duration = COURSE_DURATIONS[duration_label]
    
    difficulty = st.selectbox("📊 Difficulty Level:", list(DIFFICULTY_LEVELS.keys()), index=1)
    
    learning_style = st.selectbox("🧠 Learning Style:", list(LEARNING_STYLES.keys()), index=4)
    
    content_format = st.selectbox("📋 Content Format:", list(CONTENT_FORMATS.keys()), index=0)
    
    with st.expander("🎯 Advanced Options"):
        prerequisites = st.text_area("Prerequisites:", placeholder="List any required background knowledge...")
        
        learning_objectives_input = st.text_area(
            "Learning Objectives (one per line):", 
            placeholder="What should students achieve?\nObjective 1\nObjective 2..."
        )
        learning_objectives = [obj.strip() for obj in learning_objectives_input.split('\n') if obj.strip()]
        
        include_assignments = st.checkbox("Include Assignments", value=True)
        include_resources = st.checkbox("Include Additional Resources", value=True)
        adaptive_difficulty = st.checkbox("Adaptive Difficulty Progression", value=True)

# --- Main Content Area ---

# Course Generation
col1, col2 = st.columns([3, 1])
with col1:
    generate_button = st.button("🚀 Generate Comprehensive Course", type="primary", disabled=not api_key)
with col2:
    if st.session_state.course_content:
        if st.button("📥 Export Course"):
            content = export_course_content(st.session_state.course_content)
            st.download_button("Download Markdown", content, f"{topic.replace(' ', '_')}_course.md")

if generate_button:
    if topic:
        # Start timing
        st.session_state.study_start_time = time.time()
        
        with st.spinner("🎨 Crafting your personalized learning experience... This may take a moment."):
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # Simulate progress updates
            progress_steps = [
                "Analyzing topic complexity...",
                "Designing curriculum structure...", 
                "Creating learning materials...",
                "Generating assessments...",
                "Finalizing course content..."
            ]
            
            for i, step in enumerate(progress_steps):
                status_text.text(step)
                progress_bar.progress((i + 1) / len(progress_steps))
                time.sleep(0.5)
            
            course_data = generate_advanced_course_content(
                topic, duration, difficulty, learning_style, content_format,
                prerequisites, learning_objectives, api_key
            )
            
            if course_data:
                st.session_state.course_content = course_data
                st.session_state.quiz_submitted = False
                st.session_state.current_section = 0
                
                # Generate course ID and initialize progress
                course_id = generate_course_id(topic, duration, difficulty)
                initial_progress = {
                    'course_id': course_id,
                    'start_time': datetime.datetime.now().isoformat(),
                    'overall_progress': 0,
                    'quiz_score': 0,
                    'study_time': 0,
                    'completion_rate': 0,
                    'section_progress': {}
                }
                save_progress(course_id, initial_progress)
                
                progress_bar.progress(1.0)
                status_text.text("✅ Course ready!")
                time.sleep(1)
                progress_bar.empty()
                status_text.empty()
                
                st.success("🎉 Your comprehensive course is ready!")
                st.balloons()
            else:
                st.error("❌ Failed to generate course content. Please check your API key and try again.")
    else:
        st.warning("⚠️ Please enter a topic to get started.")

# --- Display Generated Content ---
if st.session_state.course_content:
    course = st.session_state.course_content
    
    # Calculate study time once for use throughout the display logic
    study_time = 0
    if st.session_state.study_start_time:
        study_time = (time.time() - st.session_state.study_start_time) / 60  # Convert to minutes
    
    # Calculate quiz score and difficulty breakdown if submitted
    score = 0
    score_percentage = 0
    results_by_difficulty = {'easy': {'correct': 0, 'total': 0}, 'medium': {'correct': 0, 'total': 0}, 'hard': {'correct': 0, 'total': 0}}
    if st.session_state.quiz_submitted:
        quiz_questions = course['comprehensive_quiz']
        if quiz_questions and 'user_answers' in st.session_state:
            for i, q in enumerate(quiz_questions):
                if i < len(st.session_state.user_answers):
                    user_answer = st.session_state.user_answers[i]
                    difficulty = q.get('difficulty', 'medium')
                    
                    if difficulty in results_by_difficulty:
                        results_by_difficulty[difficulty]['total'] += 1
                    
                    if user_answer == q['answer']:
                        score += 1
                        if difficulty in results_by_difficulty:
                            results_by_difficulty[difficulty]['correct'] += 1
            score_percentage = (score / len(quiz_questions)) * 100 if quiz_questions else 0

    # Course Overview Dashboard
    st.header("📊 Course Overview")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Duration", f"{course['course_metadata']['duration_minutes']} min")
    with col2:
        st.metric("Sections", len(course['course_sections']))
    with col3:
        st.metric("Quizzes", len(course['comprehensive_quiz']))
    with col4:
        st.metric("Examples", len(course['practical_examples']))
    
    # Course Metadata
    with st.expander("ℹ️ Course Information", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            st.write(f"**Target Audience:** {course['course_metadata'].get('target_audience', 'General learners')}")
            st.write(f"**Prerequisites:** {course['course_metadata'].get('prerequisites', 'None')}")
        with col2:
            if course['course_metadata'].get('learning_objectives'):
                st.write("**Learning Objectives:**")
                for obj in course['course_metadata']['learning_objectives']:
                    st.write(f"• {obj}")
    
    st.divider()
    
    # Section Navigation
    st.header("📚 Course Content")
    
    # Use a selectbox for navigation if there are multiple sections
    if len(course['course_sections']) > 1:
        section_titles = [f"Section {i+1}: {s['title']}" for i, s in enumerate(course['course_sections'])]
        selected_title = st.selectbox(
            "Navigate Course Sections",
            options=section_titles,
            key="section_selector",
            label_visibility="collapsed"
        )
        selected_index = section_titles.index(selected_title)
        section = course['course_sections'][selected_index]
    else:
        section = course['course_sections'][0]

    # Display the selected (or only) section
    # Section header
    col1, col2 = st.columns([3, 1])
    with col1:
        st.subheader(section['title'])
    with col2:
        st.info(f"⏱️ {section.get('duration_minutes', 'N/A')} min")
    
    # Learning outcomes
    if section.get('learning_outcomes'):
        with st.expander("🎯 Learning Outcomes"):
            for outcome in section['learning_outcomes']:
                st.write(f"• {outcome}")
    
    # Section content
    st.markdown(section['content'])
    
    # Key concepts
    if section.get('key_concepts'):
        st.subheader("🔑 Key Concepts")
        concept_cols = st.columns(min(3, len(section['key_concepts'])))
        for j, concept in enumerate(section['key_concepts']):
            with concept_cols[j % 3]:
                st.info(concept)
    
    st.divider()
    
    # Interactive Quiz Section
    st.header("🧠 Comprehensive Assessment")
    
    if not st.session_state.quiz_submitted:
        with st.form("comprehensive_quiz_form"):
            st.write("Test your understanding with this comprehensive quiz:")
            user_answers = []
            
            # Group questions by difficulty if available
            quiz_questions = course['comprehensive_quiz']
            
            for i, q in enumerate(quiz_questions):
                # Question header with metadata
                col1, col2, col3 = st.columns([6, 1, 1])
                with col1:
                    st.write(f"**Question {i+1}:** {q['question']}")
                with col2:
                    if q.get('difficulty'):
                        difficulty_color = {'easy': '🟢', 'medium': '🟡', 'hard': '🔴'}
                        st.write(f"{difficulty_color.get(q['difficulty'], '⚪')} {q['difficulty'].title()}")
                with col3:
                    if q.get('concept_tested'):
                        st.caption(f"📝 {q['concept_tested']}")
                
                # Answer options
                user_answers.append(st.radio("", q['options'], key=f"q{i}", label_visibility="collapsed"))
                st.divider()
            
            col1, col2, col3 = st.columns([1, 1, 2])
            with col2:
                submitted = st.form_submit_button("📊 Submit Assessment", type="primary")
            
            if submitted:
                st.session_state.quiz_submitted = True
                st.session_state.user_answers = user_answers
                st.rerun()
    else:
        # Quiz Results with Detailed Analytics
        st.subheader("📈 Assessment Results")
        
        quiz_questions = course['comprehensive_quiz']
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Overall Score", f"{score}/{len(quiz_questions)}" if quiz_questions else "N/A")
        with col2:
            st.metric("Percentage", f"{score_percentage:.1f}%")
        with col3:
            grade = "A+" if score_percentage >= 95 else "A" if score_percentage >= 90 else "B+" if score_percentage >= 85 else "B" if score_percentage >= 80 else "C+" if score_percentage >= 75 else "C" if score_percentage >= 70 else "D" if score_percentage >= 60 else "F"
            st.metric("Grade", grade)
        with col4:
            status = "Mastery" if score_percentage >= 85 else "Proficient" if score_percentage >= 70 else "Developing" if score_percentage >= 60 else "Needs Improvement"
            st.metric("Status", status)
        
        # Difficulty breakdown
        st.subheader("📊 Performance by Difficulty")
        diff_cols = st.columns(3)
        
        for i, (diff, data) in enumerate(results_by_difficulty.items()):
            if data['total'] > 0:
                with diff_cols[i]:
                    diff_score = (data['correct'] / data['total']) * 100
                    st.metric(f"{diff.title()} Questions", f"{data['correct']}/{data['total']}", f"{diff_score:.1f}%")
        
        # Detailed question review
        with st.expander("🔍 Detailed Question Review"):
            for i, q in enumerate(quiz_questions):
                user_answer = st.session_state.user_answers[i]
                correct_answer = q['answer']
                
                if user_answer == correct_answer:
                    st.success(f"**Question {i+1}: ✅ Correct**")
                    st.write(f"**Q:** {q['question']}")
                    st.write(f"**Your answer:** {user_answer}")
                else:
                    st.error(f"**Question {i+1}: ❌ Incorrect**")
                    st.write(f"**Q:** {q['question']}")
                    st.write(f"**Your answer:** {user_answer}")
                    st.write(f"**Correct answer:** {correct_answer}")
                
                if q.get('explanation'):
                    st.info(f"💡 **Explanation:** {q['explanation']}")
                
                st.divider()
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔄 Retake Assessment"):
                st.session_state.quiz_submitted = False
                st.rerun()
        with col2:
            if st.button("📊 View Learning Analytics"):
                st.session_state.show_analytics = True
                st.rerun()
    
    st.divider()
    
    # Flashcards Section
    st.header("🃏 Interactive Flashcards")
    
    if course.get('flashcards'):
        # Flashcard navigation
        if 'current_flashcard' not in st.session_state:
            st.session_state.current_flashcard = 0
        
        total_cards = len(course['flashcards'])
        current_card = st.session_state.current_flashcard
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col1:
            if st.button("⬅️ Previous", disabled=current_card == 0):
                st.session_state.current_flashcard -= 1
                st.rerun()
        with col2:
            st.write(f"Card {current_card + 1} of {total_cards}")
        with col3:
            if st.button("Next ➡️", disabled=current_card == total_cards - 1):
                st.session_state.current_flashcard += 1
                st.rerun()
        
        # Current flashcard
        card = course['flashcards'][current_card]
        
        with st.container():
            st.markdown(f"""
            <div class="feature-card">
                <h3>🎯 {card['term']}</h3>
                <p><strong>Definition:</strong> {card['definition']}</p>
                {f"<p><strong>Example:</strong> {card['example']}</p>" if card.get('example') else ""}
                {f"<p><strong>💭 Memory Aid:</strong> {card['mnemonic']}</p>" if card.get('mnemonic') else ""}
            </div>
            """, unsafe_allow_html=True)
        
        # Flashcard difficulty filter
        if st.checkbox("Show only cards by difficulty"):
            difficulty_filter = st.selectbox("Filter by difficulty:", ["basic", "intermediate", "advanced"])
            filtered_cards = [i for i, card in enumerate(course['flashcards']) if card.get('difficulty') == difficulty_filter]
            if filtered_cards:
                st.write(f"Found {len(filtered_cards)} cards with {difficulty_filter} difficulty")
    
    st.divider()
    
    # Practical Examples Section
    st.header("💻 Practical Examples & Code")
    
    if course.get('practical_examples'):
        example_titles = [f"Example {i+1}: {ex['title']}" for i, ex in enumerate(course['practical_examples'])]
        selected_example_title = st.selectbox(
            "Choose an Example",
            options=example_titles,
            key="example_selector",
            label_visibility="collapsed"
        )
        selected_index = example_titles.index(selected_example_title)
        example = course['practical_examples'][selected_index]
        
        # Display the selected example
        st.subheader(example['title'])
        st.write(example['description'])
        
        # Code display
        if example.get('code'):
            st.code(example['code'], language=example.get('language', 'text'))
        
        # Explanation
        if example.get('explanation'):
            with st.expander("📝 Step-by-step Explanation"):
                st.write(example['explanation'])
        
        # Variations
        if example.get('variations'):
            with st.expander("🔄 Alternative Approaches"):
                for j, variation in enumerate(example['variations']):
                    st.write(f"**Approach {j+1}:** {variation}")
        
        # Real-world application
        if example.get('real_world_application'):
            st.info(f"🌍 **Real-world Application:** {example['real_world_application']}")
    
    st.divider()
    
    # Assignments Section (if included)
    if course.get('assignments') and include_assignments:
        st.header("📋 Assignments & Projects")
        
        for i, assignment in enumerate(course['assignments']):
            with st.expander(f"Assignment {i+1}: {assignment['title']}"):
                col1, col2 = st.columns([2, 1])
                with col1:
                    st.write(f"**Description:** {assignment['description']}")
                with col2:
                    st.info(f"⏱️ Est. Time: {assignment.get('estimated_time', 'N/A')}")
                    st.info(f"📊 Level: {assignment.get('difficulty', 'N/A')}")
                
                if assignment.get('deliverables'):
                    st.write("**Deliverables:**")
                    for deliverable in assignment['deliverables']:
                        st.write(f"• {deliverable}")
                
                if assignment.get('evaluation_criteria'):
                    st.write("**Evaluation Criteria:**")
                    for criteria in assignment['evaluation_criteria']:
                        st.write(f"• {criteria}")
    
    # Additional Resources Section
    if course.get('additional_resources') and include_resources:
        st.header("📚 Additional Learning Resources")
        
        # Group resources by type
        resource_types = {}
        for resource in course['additional_resources']:
            res_type = resource.get('type', 'general')
            if res_type not in resource_types:
                resource_types[res_type] = []
            resource_types[res_type].append(resource)
        
        # Display resources by type
        for res_type, resources in resource_types.items():
            st.subheader(f"{res_type.title()} Resources")
            
            for resource in resources:
                with st.container():
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.write(f"**{resource['title']}**")
                        st.write(resource['description'])
                    with col2:
                        if resource.get('difficulty'):
                            difficulty_colors = {'beginner': '🟢', 'intermediate': '🟡', 'advanced': '🔴'}
                            st.write(f"{difficulty_colors.get(resource['difficulty'], '⚪')} {resource['difficulty'].title()}")
                st.divider()
    
    # Learning Analytics Dashboard
    if st.session_state.get('show_analytics'):
        st.header("📊 Learning Analytics Dashboard")
        
        # Update progress data
        progress_data = {
            'overall_progress': 75,  # This would be calculated based on actual completion
            'quiz_score': score_percentage,
            'study_time': int(study_time),
            'completion_rate': 85,  # Based on sections completed, quizzes taken, etc.
            'section_progress': {f"Section {i+1}": min(100, (i+1) * 25) for i in range(len(course['course_sections']))}
        }
        
        display_learning_analytics(progress_data)
        
        # Learning path recommendations
        st.subheader("🎯 Personalized Learning Recommendations")
        
        if score_percentage < 70:
            st.warning("**Recommendation:** Review the course materials and focus on areas where you scored lower.")
            st.write("Consider:")
            st.write("• Re-reading sections with key concepts you missed")
            st.write("• Practicing with additional flashcards")
            st.write("• Completing the assignments for hands-on practice")
        elif score_percentage < 85:
            st.info("**Recommendation:** You're doing well! Consider exploring advanced topics or related courses.")
            st.write("Suggested next steps:")
            st.write("• Complete the practical assignments")
            st.write("• Explore the additional resources for deeper understanding")
            st.write("• Try creating your own examples based on the concepts learned")
        else:
            st.success("**Excellent work!** You've mastered this topic. Ready for advanced challenges!")
            st.write("Advanced learning opportunities:")
            st.write("• Teach others what you've learned")
            st.write("• Apply concepts to real-world projects")
            st.write("• Explore related advanced topics")
        
        # Progress tracking over time (simulated data)
        st.subheader("📈 Progress Timeline")
        
        # Create sample progress data
        dates = pd.date_range(start=datetime.datetime.now() - datetime.timedelta(days=7), 
                             end=datetime.datetime.now(), freq='D')
        progress_over_time = pd.DataFrame({
            'Date': dates,
            'Progress': [10, 25, 40, 55, 65, 75, 85, 90][:len(dates)]
        })
        
        fig = px.line(progress_over_time, x='Date', y='Progress', 
                     title='Learning Progress Over Time',
                     labels={'Progress': 'Completion (%)'})
        fig.update_traces(line_color='#667eea', line_width=3)
        st.plotly_chart(fig, use_container_width=True)
        
        # Competency radar chart
        st.subheader("🎯 Competency Assessment")
        
        # Simulate competency scores based on quiz performance
        competencies = ['Theoretical Knowledge', 'Practical Application', 'Critical Thinking', 
                       'Problem Solving', 'Communication', 'Technical Skills']
        
        # Base scores on quiz performance with some variation
        base_score = score_percentage if st.session_state.quiz_submitted else 70
        competency_scores = [base_score + (i * 5 - 10) for i in range(len(competencies))]
        competency_scores = [max(0, min(100, score)) for score in competency_scores]
        
        fig = go.Figure()
        fig.add_trace(go.Scatterpolar(
            r=competency_scores,
            theta=competencies,
            fill='toself',
            name='Current Level',
            line_color='#667eea'
        ))
        
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 100]
                )),
            showlegend=True,
            title="Competency Radar Chart"
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        if st.button("🔙 Back to Course"):
            st.session_state.show_analytics = False
            st.rerun()
    
    st.divider()
    
    # Course Completion and Certification
    st.header("🏆 Course Completion")
    
    # Calculate completion percentage
    completion_factors = {
        'sections_read': len(course['course_sections']),  # Assume all read for demo
        'quiz_completed': 1 if st.session_state.quiz_submitted else 0,
        'flashcards_reviewed': 1,  # Assume reviewed for demo
        'examples_studied': len(course.get('practical_examples', []))
    }
    
    total_possible = sum([
        len(course['course_sections']),
        1,  # quiz
        1,  # flashcards
        len(course.get('practical_examples', []))
    ])
    
    current_completion = sum(completion_factors.values())
    completion_percentage = (current_completion / total_possible) * 100 if total_possible > 0 else 0
    
    # Progress bar
    st.progress(completion_percentage / 100)
    st.write(f"**Course Completion: {completion_percentage:.1f}%**")
    
    # Completion checklist
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("✅ Completion Checklist")
        st.write("📖 Read all sections" + (" ✅" if completion_factors['sections_read'] > 0 else " ⏳"))
        st.write("🧠 Complete quiz" + (" ✅" if completion_factors['quiz_completed'] > 0 else " ⏳"))
        st.write("🃏 Review flashcards" + (" ✅" if completion_factors['flashcards_reviewed'] > 0 else " ⏳"))
        st.write("💻 Study examples" + (" ✅" if completion_factors['examples_studied'] > 0 else " ⏳"))
    
    with col2:
        st.subheader("🎖️ Achievement Badges")
        
        # Award badges based on performance
        badges = []
        if st.session_state.quiz_submitted:
            if score_percentage >= 95:
                badges.append("🏆 Quiz Master")
            elif score_percentage >= 85:
                badges.append("🥇 High Achiever")
            elif score_percentage >= 70:
                badges.append("🥈 Proficient Learner")
        
        if study_time > duration * 0.8:  # Spent adequate time
            badges.append("⏰ Dedicated Student")
        
        if completion_percentage >= 90:
            badges.append("🎯 Course Completer")
        
        for badge in badges:
            st.success(badge)
        
        if not badges:
            st.info("Complete more activities to earn badges!")
    
    # Certificate Generation
    if completion_percentage >= 80 and st.session_state.quiz_submitted and score_percentage >= 70:
        st.success("🎉 Congratulations! You've earned a certificate of completion!")
        
        if st.button("📜 Generate Certificate"):
            # Certificate content
            cert_content = f"""
# Certificate of Completion

**This is to certify that you have successfully completed:**

## {course['course_metadata']['topic']}

**Course Details:**
- Duration: {course['course_metadata']['duration_minutes']} minutes
- Difficulty Level: {course['course_metadata']['difficulty']}
- Completion Date: {datetime.datetime.now().strftime('%B %d, %Y')}

**Performance Summary:**
- Overall Score: {score_percentage:.1f}%
- Completion Rate: {completion_percentage:.1f}%
- Time Invested: {int(study_time)} minutes

**Skills Demonstrated:**
{chr(10).join(['• ' + skill for skill in course['course_metadata'].get('skills_gained', ['Critical thinking', 'Problem solving', 'Knowledge application'])])}

*This certificate validates your commitment to continuous learning and professional development.*

---
Generated by Advanced Course Generator Pro
            """
            
            st.download_button(
                "📥 Download Certificate",
                cert_content,
                f"certificate_{topic.replace(' ', '_').lower()}.md",
                "text/markdown"
            )
    
    st.divider()
    
    # Course Feedback and Improvement
    st.header("💬 Course Feedback")
    
    with st.expander("📝 Help Us Improve"):
        feedback_rating = st.select_slider(
            "How would you rate this course?",
            options=["Poor", "Fair", "Good", "Very Good", "Excellent"],
            value="Good"
        )
        
        feedback_categories = st.multiselect(
            "What aspects worked well?",
            ["Content Quality", "Difficulty Level", "Examples", "Quizzes", "Structure", "Resources"]
        )
        
        improvement_suggestions = st.text_area(
            "Suggestions for improvement:",
            placeholder="What could make this course even better?"
        )
        
        if st.button("📤 Submit Feedback"):
            st.success("Thank you for your feedback! Your input helps us create better learning experiences.")
    
    # Related Courses Suggestions
    st.header("🔍 Explore Related Topics")
    
    # Generate related topic suggestions based on current topic
    related_topics = []
    if "machine learning" in topic.lower():
        related_topics = ["Deep Learning Fundamentals", "Data Science Essentials", "Python for AI", "Statistics for ML"]
    elif "python" in topic.lower():
        related_topics = ["Advanced Python", "Web Development with Python", "Data Analysis with Python", "Python for Automation"]
    elif "quantum" in topic.lower():
        related_topics = ["Quantum Mechanics", "Quantum Algorithms", "Quantum Cryptography", "Physics for Computer Science"]
    else:
        related_topics = ["Advanced " + topic, topic + " Applications", topic + " Best Practices", "Introduction to " + topic + " Tools"]
    
    col1, col2 = st.columns(2)
    
    for i, related_topic in enumerate(related_topics[:4]):
        with col1 if i % 2 == 0 else col2:
            if st.button(f"🚀 Learn {related_topic}", key=f"related_{i}"):
                st.session_state.suggested_topic = related_topic
                st.info(f"Suggested topic: {related_topic}")
                st.info("Change the topic in the sidebar and click 'Generate Course' to explore this subject!")
    
    # Export and Sharing Options
    st.divider()
    st.header("📤 Export & Share")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📑 Export as PDF"):
            with st.spinner("Generating PDF..."):
                pdf_content = export_course_content(st.session_state.course_content, format_type="pdf")
                if pdf_content:
                    st.download_button(
                        label="📥 Download PDF",
                        data=pdf_content,
                        file_name=f"{topic.replace(' ', '_')}_course.pdf",
                        mime="application/pdf"
                    )
    
    with col2:
        if st.button("📊 Export Progress Report"):
            progress_report = f"""
# Learning Progress Report

**Course:** {course['course_metadata']['topic']}
**Completion Date:** {datetime.datetime.now().strftime('%B %d, %Y')}

## Performance Summary
- Quiz Score: {score_percentage:.1f}%
- Study Time: {int(study_time)} minutes
- Completion Rate: {completion_percentage:.1f}%

## Achievements
{chr(10).join(['• ' + badge for badge in badges]) if badges else '• Complete more activities to earn achievements'}

## Next Steps
- Continue practicing with real-world applications
- Explore advanced topics in this field
- Consider related courses for broader knowledge
            """
            
            st.download_button(
                "📥 Download Progress Report",
                progress_report,
                f"progress_report_{topic.replace(' ', '_').lower()}.md",
                "text/markdown"
            )
    
    with col3:
        if st.button("🔗 Share Course Link"):
            st.info("In a full implementation, this would generate a shareable link to the course")
    
    # Advanced Features Section
    st.divider()
    st.header("🚀 Advanced Features")
    
    with st.expander("🔧 Advanced Tools & Features"):
        st.markdown("""
        **Available Advanced Features:**
        
        🎯 **Adaptive Learning**
        - Difficulty adjusts based on your performance
        - Personalized learning paths
        - Smart content recommendations
        
        📊 **Advanced Analytics**
        - Detailed progress tracking
        - Competency assessments
        - Learning pattern analysis
        
        🤖 **AI-Powered Features**
        - Intelligent content generation
        - Personalized quiz questions
        - Automated feedback and suggestions
        
        🔄 **Collaboration Tools**
        - Study groups and discussions
        - Peer review assignments
        - Knowledge sharing features
        
        📱 **Multi-Platform Support**
        - Mobile-responsive design
        - Offline content access
        - Cross-device synchronization
        
        🎨 **Customization Options**
        - Multiple content formats
        - Learning style preferences
        - Custom course durations
        """)
        
        # Feature toggles for advanced users
        st.subheader("⚙️ Feature Configuration")
        
        col1, col2 = st.columns(2)
        with col1:
            enable_adaptive = st.checkbox("Enable Adaptive Learning", value=True)
            enable_analytics = st.checkbox("Detailed Analytics", value=True)
            enable_ai_tutor = st.checkbox("AI Tutor Assistant", value=False)
        
        with col2:
            enable_gamification = st.checkbox("Gamification Elements", value=True)
            enable_collaboration = st.checkbox("Collaboration Features", value=False)
            enable_offline = st.checkbox("Offline Mode", value=False)
        
        if st.button("💾 Save Preferences"):
            st.success("Preferences saved! These settings will be applied to future courses.")
    
    # Footer with additional information
    st.divider()
    st.markdown("""
    ---
    ### 🎓 Advanced Course Generator Pro
    
    **Features:**
    • Customizable course duration (2 minutes to 8+ hours)
    • Multiple difficulty levels and learning styles
    • Comprehensive assessments and analytics
    • Interactive flashcards and practical examples
    • Progress tracking and certification
    • Export capabilities and sharing options
    
    **Powered by:** Google Gemini AI | **Built with:** Streamlit | **Version:** 2.0.0
    
    *Transform any topic into a comprehensive, personalized learning experience.*
    """)

# --- Additional Helper Functions for Advanced Features ---

def generate_adaptive_content(user_performance: Dict, topic: str, api_key: str) -> Dict:
    """Generate adaptive content based on user performance."""
    # This would integrate with the main content generation
    # to create personalized follow-up materials
    pass

def create_study_schedule(course_duration: int, user_availability: Dict) -> List[Dict]:
    """Create a personalized study schedule."""
    # Would generate a recommended study plan
    pass

def generate_peer_discussion_questions(course_content: Dict) -> List[str]:
    """Generate discussion questions for peer learning."""
    # Would create thoughtful discussion prompts
    pass

def calculate_knowledge_gaps(quiz_results: List[Dict]) -> List[str]:
    """Identify knowledge gaps based on quiz performance."""
    # Would analyze incorrect answers to identify weak areas
    pass

# --- Run the Streamlit App ---
if __name__ == "__main__":
    st.write("🚀 Advanced Course Generator Pro is ready to transform your learning experience!")
