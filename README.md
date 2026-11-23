# Study Planner AI 🎓

An intelligent, production-ready academic planning application powered by Python, Streamlit, LangChain, and Google Gemini.

Study Planner AI is built specifically for university students to organize courses, generate balanced daily study schedules, calculate exact examination countdowns, and interact with a multi-turn conversational AI academic assistant.

---

## 📌 Problem Statement

University students, especially in technical disciplines like Computer Science, frequently struggle with:
1. **Unbalanced Study Time:** Spending excessive hours on one favorite subject while neglecting more difficult or imminent exam subjects.
2. **Date & Countdown Errors:** Manually calculating remaining days until examinations leads to last-minute cramming and missed revision targets.
3. **Static, Rigid Tools:** Traditional calendar or to-do list apps do not dynamically adapt to changing study hours or offer intelligent academic planning advice.
4. **LLM Hallucinations:** Generic AI chatbots frequently hallucinate dates, give incorrect time arithmetic, or lack awareness of user context across turns.

**Study Planner AI** solves these challenges by combining generative AI with **deterministic, offline Python calculation tools** and session-level conversation memory.

---

## ✨ Features

- **📊 Comprehensive Academic Dashboard:**
  - Real-time overview metric cards: Total Subjects, Weekly Planned Study Hours, Completed Sessions Today, and Upcoming Exams.
  - Interactive **Today's Study Plan** with one-click completion toggles that dynamically update daily progress.
  - Urgency-coded examination countdown alerts.
  - Visual weekly study progress bar charts.

- **🤖 AI Study Assistant:**
  - Powered by modern Google Gemini (`gemini-1.5-flash`) via LangChain.
  - Multi-turn conversation memory retaining student name, course details, study hours, and academic preferences.
  - **Transparent Tool Execution:** Expandable **"Tools Used"** section showing the exact tool invoked, arguments passed, and returned output.
  - Clear Chat option to instantly reset conversation memory.

- **📚 Subject Management:**
  - Add, inspect, and remove courses.
  - Configure priority levels (High, Medium, Low), difficulty ratings (Hard, Medium, Easy), planned weekly hours, and examination target dates.

- **🗓️ Study Schedule & Equal Hour Allocator:**
  - Distribute any available study hours equally among selected courses using the `split_study_hours` tool.
  - Push generated study allocations directly into Today's Study Plan with a single click.

- **⏳ Exam Countdown Board:**
  - Real-time countdown to examinations using Python `datetime` arithmetic via the `days_until_exam` tool.
  - Quick calculator to check remaining days for any custom date.

- **📈 Academic Progress Tracker:**
  - Visual metrics: Weekly study targets vs completed study hours.
  - Interactive daily trend charts and subject-wise allocation breakdowns.

- **🔒 Security & Privacy First:**
  - Users enter their own Gemini API key in the sidebar.
  - Keys and chat logs are stored strictly in session memory (`st.session_state`).
  - No keys or private chats are ever logged, printed, or saved to persistent disk.

---

## 🛠️ Technology Stack

| Component | Technology | Role / Purpose |
|---|---|---|
| **Programming Language** | Python 3.11+ | Core application language |
| **Frontend UI** | Streamlit (1.67.0) | Modern interactive SaaS dashboard & chat |
| **AI Intelligence** | Google Gemini API (`gemini-1.5-flash`) | Natural language understanding & planning |
| **AI Tool Orchestration** | LangChain & `langchain-google-genai` | Tool binding, multi-turn memory, & message flow |
| **Date Calculations** | Python `datetime` & `python-dateutil` | Offline, deterministic date arithmetic |
| **Data Visualization** | Pandas & Streamlit Native Charts | Visual progress tracking and allocation graphs |
| **Version Control** | Git & GitHub | Source code tracking and collaboration |
| **Deployment** | Streamlit Community Cloud | Zero-cost serverless cloud hosting |

---

## 🏗️ Project Architecture

```
User Query / Action
       │
       ▼
┌──────────────────────────────────────────────┐
│       Streamlit Frontend (app.py)            │
│  - Modern SaaS / Notion UI Cards             │
│  - Session State Memory Management           │
│  - Secure Password Input for API Key         │
└──────────────────────┬───────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────┐
│     AI Assistant Core (assistant_core.py)    │
│  - System Prompt Enforcement                 │
│  - Multi-Turn History (Human / AI Messages)  │
│  - LangChain Model Binding                   │
└──────────────────────┬───────────────────────┘
                       │
       ┌───────────────┴───────────────┐
       ▼                               ▼
┌─────────────────────────┐ ┌─────────────────────────┐
│ Tool 1: days_until_exam │ │ Tool 2: split_study_hrs │
│ - Python datetime       │ │ - Equal hours split     │
│ - Offline calculation   │ │ - Input validation      │
└─────────────────────────┘ └─────────────────────────┘
                       │
                       ▼
          Synthesized AI Response + Tools Used
```

---

## 📁 Folder Structure

```
study-planner-ai/
│
├── app.py                  # Streamlit application UI, sidebar, dashboard, and views
├── assistant_core.py       # LangChain + Gemini integration, memory, and tool flow
├── tools.py                # Exactly two custom Python tools (days_until_exam, split_study_hours)
├── requirements.txt        # Production dependencies for local run & Streamlit Cloud
├── .gitignore              # Ignores .venv, cache files, and sensitive credentials
├── README.md               # Complete project documentation and guide
├── tests.md                # 6 comprehensive test scenarios with pass/fail logs
│
└── assets/
    └── logo.png            # Application logo and brand asset
```

---

## 🚀 Installation & Local Setup

### Prerequisites
- Python 3.11 or higher installed on your system.
- Git installed.
- A free Google Gemini API key from [Google AI Studio](https://aistudio.google.com).

### 1. Clone the Repository
```bash
git clone https://github.com/Sibishalom16/study-planner-ai.git
cd study-planner-ai
```

### 2. Set Up a Virtual Environment
```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# macOS / Linux
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the Application
```bash
streamlit run app.py
```
Open your browser and navigate to `http://localhost:8501`.

---

## 🔑 Gemini API Key Setup

1. Visit [Google AI Studio](https://aistudio.google.com) and sign in with your Google account.
2. Click **Get API key** and generate a free API key.
3. Open the **Study Planner AI** application in your browser.
4. Paste your key into the **Gemini API Key** field in the sidebar.
5. Your key is active immediately for your current session!

> **Security Note:** Your API key is stored only in temporary memory (`st.session_state`). It is never written to disk, never printed in terminal logs, and never committed to version control.

---

## ⚙️ Custom Tools Explained

Study Planner AI implements **exactly two custom offline Python tools** registered with LangChain:

### 1. `days_until_exam(exam_date: str) -> str`
- **Purpose:** Calculates the exact number of days remaining from today until a specified examination date.
- **Why Offline:** Prevents LLM hallucinations regarding current date and calendar arithmetic.
- **Features:** Supports ISO format (`2026-12-15`), natural language dates (`15 December 2026`), catches past dates gracefully, and returns clear validation errors for invalid input without crashing.
- **Example Call:**
  - Input: `"15 December 2026"`
  - Output: `"Your examination is 22 days away."`

### 2. `split_study_hours(total_hours, subjects) -> str`
- **Purpose:** Evenly distributes available study hours across multiple enrolled courses.
- **Why Offline:** Ensures deterministic, exact mathematical division without rounding drift.
- **Features:** Validates positive total hours, rejects empty subject lists, cleanly formats whole and fractional hours, and accepts both Python lists and comma-separated strings.
- **Example Call:**
  - Input: `total_hours=12`, `subjects=["Python", "DBMS", "OS", "CN"]`
  - Output:
    ```text
    Python: 3 hours
    DBMS: 3 hours
    OS: 3 hours
    CN: 3 hours
    ```

---

## 📸 Screenshots

*(Add application screenshots here after deployment)*

- **Dashboard View:** Overview metric cards, Today's study plan, upcoming exam alerts, and weekly progress charts.
- **AI Study Assistant:** Interactive multi-turn chat with visible "Tools Used" expander.
- **Schedule Allocator:** Equal hours distribution and direct task loading.
- **Exam Countdown Board:** Urgency-coded examination deadlines.

---

## 🧪 Testing Instructions

Unit and integration tests are documented in [tests.md](tests.md). To run the test suite locally:

```bash
python -c "
import sys; sys.path.insert(0, '.')
from tools import days_until_exam, split_study_hours
print(days_until_exam.invoke({'exam_date': '15 December 2026'}))
print(split_study_hours.invoke({'total_hours': 12, 'subjects': ['Python', 'DBMS', 'OS', 'CN']}))
"
```

Refer to [tests.md](tests.md) for full logs covering memory retention, out-of-scope question handling, and invalid inputs.

---

## ☁️ Deployment to Streamlit Community Cloud

1. Push your repository to GitHub:
   ```bash
   git add .
   git commit -m "feat: complete production-ready Study Planner AI application"
   git push origin main
   ```
2. Log in to [Streamlit Community Cloud](https://share.streamlit.io).
3. Click **New app** and select your repository: `Sibishalom16/study-planner-ai`.
4. Set Main file path: `app.py`.
5. Click **Deploy!** Your application will be live globally within 2 minutes.

---

## ⚠️ Limitations & Future Work

- **Session-Based Storage:** Current progress and custom subjects reside in Streamlit's `st.session_state` and reset upon browser tab refresh. Future versions could integrate SQLite or Supabase for persistent student accounts.
- **Offline Mode:** The AI conversational assistant requires internet connectivity to communicate with Gemini, although custom calculation tools work 100% offline.
- **Notification Alerts:** Browser/email push notifications for upcoming exams can be added in subsequent milestones.

---

## 📝 Personal Reflections

### 1. Why did I choose these two custom tools?

<!-- Write your answer here explaining why days_until_exam and split_study_hours are essential for student academic planning -->


### 2. How does conversation memory work in my application?

<!-- Write your answer here explaining how st.session_state, HumanMessage, and AIMessage maintain multi-turn context during the session -->

