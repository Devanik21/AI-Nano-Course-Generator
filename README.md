# 🎓 Advanced Course Generator Pro

Turn *any* topic into a beautifully structured, interactive learning experience powered entirely by the **Gemini API**. This app allows learners, educators, developers, and curious minds to generate complete educational modules from scratch with AI. Whether you're prepping for exams, exploring new skills, or building learning products, this tool can create highly customized courses with quizzes, flashcards, projects, examples, and even certification support.

With just a topic and your preferences, the Advanced Course Generator Pro intelligently curates instructional content tailored to duration, complexity, and preferred learning style.

---

## 🌟 Features

* ✅ Built with Google’s Gemini 2.5 Flash Model for fast and rich generation
* 🧠 Supports adaptive **learning styles**: Visual, Auditory, Kinesthetic, Reading/Writing, and Multimodal
* 📚 Auto-generates:

  * Structured Course Modules and Educational Content
  * Interactive Flashcards with mnemonics and examples
  * Quizzes with difficulty-based questions and instant explanations
  * Real-world Practical Examples and Code Snippets
  * Assignments with deliverables and evaluation criteria
  * Supplementary Resources curated from multiple domains
* 📊 Real-time interactive learning dashboards and analytics
* 🧾 AI-based Certificate generation, Completion badges, and Assessment rubrics
* 📥 Export-ready formats: Markdown content, progress reports, and certificates
* 🌀 Optional features like Adaptive Learning, Gamification, Collaboration Tools, and Offline Mode

---

## 🚀 Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/advanced-course-generator.git
cd advanced-course-generator
```

### 2. Install Required Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Your Gemini API Key

Create a `.env` file in the project root and insert your API key:

```bash
GOOGLE_API_KEY=your-gemini-api-key-here
```

Alternatively, configure your key through Streamlit Secrets when deploying.

### 4. Launch the Application

```bash
streamlit run app.py
```

---

## 🧪 Example Use Case

* Input Topic: `Introduction to Quantum Computing`
* Course Length: `15 minutes`
* Learning Style: `Visual`
* Content Format: `Project-Based`
* Within moments, Gemini will generate an entire, well-structured course module complete with examples, quizzes, and progress features.

You can even export the content as Markdown or view analytics and competency charts once you've completed the course.

---

## 📂 File Structure Overview

```
├── app.py               # Streamlit App Core
├── requirements.txt     # Required dependencies for the app
├── .env                 # (optional) API key storage
```

---

## 🌐 Deploy on Streamlit Cloud

Want to share your project publicly? Deploying on Streamlit Cloud is easy:

1. Push your complete project to a GitHub repository.
2. Navigate to [streamlit.io/cloud](https://streamlit.io/cloud)
3. Connect your GitHub repository.
4. Set your API key using Streamlit Secrets (`GOOGLE_API_KEY`).
5. Click deploy and launch your app globally!

You now have your own AI-powered course engine running in the cloud.

---

## ❤️ Credits & Acknowledgements

* Developed by **Devanik Debnath**
* AI Model: `gemini-2.5-flash` via `google-generativeai`
* UI/UX Design: Built beautifully using **Streamlit** and **Plotly**
* Inspired by the mission to make advanced learning accessible through AI

---

## 📜 License

Released under the **MIT License** — you’re free to use, modify, and share this project for educational or personal development purposes.

---

## 🌈 Live Demo (optional)

*You can host this app on Streamlit Cloud. Insert your deployed link here for public access.*

---

> *Empowering personalized, on-demand learning experiences through AI — one brilliant topic at a time.* ✨
