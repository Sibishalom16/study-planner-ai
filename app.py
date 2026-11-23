"""
app.py
------
Streamlit UI and Frontend for Study Planner AI.
Contains:
- Sidebar with logo, navigation, secure API key entry, and clear chat.
- Main Dashboard with overview cards, today's schedule, exam countdown, and progress chart.
- AI Study Assistant with interactive chat, memory, and visible Tools Used section.
- Subject Management (Add/View/Delete subjects).
- Study Schedule Generator with balanced hour distribution.
- Exam Countdown Board with urgency indicators.
- Progress Tracker with session metrics and visual charts.
- Settings & configuration.
"""

import os
from datetime import datetime, date
import streamlit as st
import pandas as pd
from tools import days_until_exam, split_study_hours
from assistant_core import StudyPlannerAssistant

# ---------------------------------------------------------
# Page Configuration
# ---------------------------------------------------------
st.set_page_config(
    page_title="Study Planner AI",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------
# Custom Modern SaaS & Notion-inspired CSS
# ---------------------------------------------------------
st.markdown("""
<style>
    /* Global styles */
    .main {
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
    }
    
    /* Header Styling */
    .dashboard-header {
        background: linear-gradient(135deg, #4F46E5 0%, #3B82F6 50%, #06B6D4 100%);
        color: white;
        padding: 24px 28px;
        border-radius: 14px;
        margin-bottom: 24px;
        box-shadow: 0 4px 14px rgba(79, 70, 229, 0.15);
    }
    .dashboard-header h1 {
        margin: 0;
        font-size: 26px;
        font-weight: 700;
        color: #ffffff !important;
    }
    .dashboard-header p {
        margin: 6px 0 0 0;
        font-size: 14px;
        opacity: 0.95;
        color: #f0fdf4 !important;
    }

    /* Metric Cards */
    .metric-card {
        background: #ffffff;
        border: 1px solid #E5E7EB;
        border-radius: 12px;
        padding: 18px 20px;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
        transition: transform 0.15s ease, box-shadow 0.15s ease;
        text-align: left;
    }
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
    }
    .metric-title {
        font-size: 12px;
        font-weight: 600;
        text-transform: uppercase;
        color: #6B7280;
        letter-spacing: 0.5px;
    }
    .metric-value {
        font-size: 26px;
        font-weight: 700;
        color: #111827;
        margin-top: 4px;
    }
    .metric-subtitle {
        font-size: 12px;
        color: #9CA3AF;
        margin-top: 2px;
    }

    /* Badges */
    .badge-urgent {
        background-color: #FEE2E2;
        color: #DC2626;
        padding: 3px 8px;
        border-radius: 6px;
        font-size: 11px;
        font-weight: 600;
        display: inline-block;
    }
    .badge-upcoming {
        background-color: #FEF3C7;
        color: #D97706;
        padding: 3px 8px;
        border-radius: 6px;
        font-size: 11px;
        font-weight: 600;
        display: inline-block;
    }
    .badge-safe {
        background-color: #DEF7EC;
        color: #059669;
        padding: 3px 8px;
        border-radius: 6px;
        font-size: 11px;
        font-weight: 600;
        display: inline-block;
    }
    .badge-passed {
        background-color: #F3F4F6;
        color: #6B7280;
        padding: 3px 8px;
        border-radius: 6px;
        font-size: 11px;
        font-weight: 600;
        display: inline-block;
    }

    /* Notion Card Container */
    .notion-card {
        background: #ffffff;
        border: 1px solid #E5E7EB;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 16px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.03);
    }
    .notion-card h4 {
        margin-top: 0;
        margin-bottom: 12px;
        color: #1F2937;
        font-size: 16px;
        font-weight: 600;
    }

    /* Tool Call Box in Chat */
    .tool-box {
        background: #F8FAFC;
        border-left: 4px solid #3B82F6;
        border-radius: 6px;
        padding: 10px 14px;
        margin: 8px 0;
        font-size: 13px;
        color: #1E293B;
    }

    /* Custom sidebar styles */
    .sidebar-brand {
        display: flex;
        align-items: center;
        gap: 12px;
        padding: 8px 0 16px 0;
        border-bottom: 1px solid #E5E7EB;
        margin-bottom: 16px;
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# Session State Initialization
# ---------------------------------------------------------
if "student_name" not in st.session_state:
    st.session_state["student_name"] = "Scholar"

if "gemini_api_key" not in st.session_state:
    st.session_state["gemini_api_key"] = os.environ.get("GEMINI_API_KEY", "")

if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []

if "subjects" not in st.session_state:
    # Initial sample subjects for CS student
    st.session_state["subjects"] = [
        {"name": "Python Programming", "priority": "High", "difficulty": "Medium", "exam_date": "2026-12-15", "planned_hours": 10.0},
        {"name": "Database Management (DBMS)", "priority": "High", "difficulty": "Medium", "exam_date": "2026-12-18", "planned_hours": 8.0},
        {"name": "Operating Systems (OS)", "priority": "High", "difficulty": "Hard", "exam_date": "2026-12-22", "planned_hours": 12.0},
        {"name": "Computer Networks (CN)", "priority": "Medium", "difficulty": "Medium", "exam_date": "2026-12-28", "planned_hours": 8.0},
    ]

if "today_tasks" not in st.session_state:
    st.session_state["today_tasks"] = [
        {"subject": "Python Programming", "duration": 2.0, "start_time": "09:00 AM", "task": "Functions & File I/O Revision", "completed": True},
        {"subject": "Operating Systems (OS)", "duration": 2.5, "start_time": "11:30 AM", "task": "Process Scheduling Algorithms", "completed": False},
        {"subject": "Database Management (DBMS)", "duration": 1.5, "start_time": "03:00 PM", "task": "SQL Joins & Normalization", "completed": False},
        {"subject": "Computer Networks (CN)", "duration": 1.0, "start_time": "05:30 PM", "task": "OSI Model & TCP/IP Header", "completed": False},
    ]

if "study_logs" not in st.session_state:
    st.session_state["study_logs"] = [
        {"day": "Mon", "planned": 5.0, "completed": 4.5},
        {"day": "Tue", "planned": 6.0, "completed": 5.0},
        {"day": "Wed", "planned": 5.5, "completed": 6.0},
        {"day": "Thu", "planned": 6.0, "completed": 4.0},
        {"day": "Fri", "planned": 5.0, "completed": 5.0},
        {"day": "Sat", "planned": 7.0, "completed": 6.5},
        {"day": "Sun", "planned": 4.0, "completed": 2.0},
    ]

# ---------------------------------------------------------
# Sidebar Component
# ---------------------------------------------------------
with st.sidebar:
    # Logo & App Branding
    col_logo, col_title = st.columns([1, 3])
    with col_logo:
        logo_path = "assets/logo.png"
        if os.path.exists(logo_path):
            st.image(logo_path, width=54)
        else:
            st.markdown("## 🎓")
    with col_title:
        st.markdown("### **Study Planner AI**")
        st.caption("Personal Academic Planner")

    st.markdown("---")

    # Navigation Menu
    nav_option = st.radio(
        "Navigation",
        [
            "📊 Dashboard",
            "🤖 AI Study Assistant",
            "📚 My Subjects",
            "🗓️ Study Schedule",
            "⏳ Exam Countdown",
            "📈 Progress Tracker",
            "⚙️ Settings",
        ],
        index=0,
        label_visibility="collapsed"
    )

    st.markdown("---")

    # API Key Input (Security Guaranteed)
    st.markdown("#### 🔑 Gemini API Key")
    key_input = st.text_input(
        "Enter your Gemini API Key",
        value=st.session_state["gemini_api_key"],
        type="password",
        placeholder="AIzaSy...",
        help="Required for AI Study Assistant. Key is kept in session memory only and never saved or logged.",
        label_visibility="collapsed"
    )
    if key_input != st.session_state["gemini_api_key"]:
        st.session_state["gemini_api_key"] = key_input.strip()

    if not st.session_state["gemini_api_key"]:
        st.warning("⚠️ Enter key to enable AI Assistant.")
        st.markdown("[Get free Gemini API Key](https://aistudio.google.com)", unsafe_allow_html=True)
    else:
        st.success("✅ API Key active for this session.")

    st.markdown("---")

    # Clear Chat Action
    if st.button("🗑️ Clear Chat History", use_container_width=True):
        st.session_state["chat_history"] = []
        st.toast("Chat history cleared!", icon="🧹")
        st.rerun()

    # Session Memory Note
    st.caption("🔒 **Security & Privacy:** API keys and chat interactions are kept in active memory only and never written to disk.")


# ---------------------------------------------------------
# Helper Functions
# ---------------------------------------------------------
def get_total_planned_hours() -> float:
    return sum(s.get("planned_hours", 0.0) for s in st.session_state["subjects"])

def get_completed_tasks_count() -> int:
    return sum(1 for t in st.session_state["today_tasks"] if t.get("completed", False))

def get_completed_today_hours() -> float:
    return sum(t.get("duration", 0.0) for t in st.session_state["today_tasks"] if t.get("completed", False))


# ---------------------------------------------------------
# VIEW 1: Dashboard
# ---------------------------------------------------------
if nav_option == "📊 Dashboard":
    # Header Banner
    today_str = datetime.now().strftime("%A, %d %B %Y")
    st.markdown(f"""
    <div class="dashboard-header">
        <h1>Welcome back, {st.session_state['student_name']}! 👋</h1>
        <p>Today is {today_str} • Stay focused and make progress toward your academic goals.</p>
    </div>
    """, unsafe_allow_html=True)

    # 4 Overview Cards
    total_subjects = len(st.session_state["subjects"])
    total_planned = get_total_planned_hours()
    completed_sessions = get_completed_tasks_count()
    upcoming_exams_count = len([s for s in st.session_state["subjects"] if s.get("exam_date")])

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Total Subjects</div>
            <div class="metric-value">{total_subjects}</div>
            <div class="metric-subtitle">Active courses</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Planned Hours</div>
            <div class="metric-value">{total_planned:.1f} hrs</div>
            <div class="metric-subtitle">Weekly study target</div>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Completed Today</div>
            <div class="metric-value">{completed_sessions} / {len(st.session_state['today_tasks'])}</div>
            <div class="metric-subtitle">{get_completed_today_hours():.1f} hours completed</div>
        </div>
        """, unsafe_allow_html=True)
    with col4:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Upcoming Exams</div>
            <div class="metric-value">{upcoming_exams_count}</div>
            <div class="metric-subtitle">Tracked in calendar</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Main Grid: Today's Plan & Upcoming Exams
    col_left, col_right = st.columns([3, 2])

    with col_left:
        st.markdown("### 📋 Today's Study Plan")
        st.caption("Mark sessions as completed to automatically update your progress.")

        tasks = st.session_state["today_tasks"]
        if not tasks:
            st.info("No study tasks planned for today. Go to **Study Schedule** to generate a balanced plan.")
        else:
            for idx, task in enumerate(tasks):
                c_check, c_info, c_time, c_dur = st.columns([0.5, 3.5, 1.5, 1.2])
                with c_check:
                    is_done = st.checkbox("", value=task["completed"], key=f"dash_task_{idx}")
                    if is_done != task["completed"]:
                        st.session_state["today_tasks"][idx]["completed"] = is_done
                        st.rerun()
                with c_info:
                    st_text = f"~~{task['subject']}~~" if task["completed"] else f"**{task['subject']}**"
                    st.markdown(st_text)
                    st.caption(f"{task.get('task', 'Revision & Practice')}")
                with c_time:
                    st.markdown(f"⏰ `{task.get('start_time', 'Flexible')}`")
                with c_dur:
                    st.markdown(f"⏱️ `{task.get('duration', 1.0)} hrs`")
                st.markdown("<hr style='margin: 4px 0 10px 0; border: none; border-bottom: 1px solid #f1f5f9;'>", unsafe_allow_html=True)

        # Quick Actions Bar
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("#### ⚡ Quick Actions")
        qa1, qa2, qa3 = st.columns(3)
        with qa1:
            if st.button("🤖 Ask AI Assistant", use_container_width=True):
                st.session_state["current_view"] = "🤖 AI Study Assistant"
                st.info("Tip: Select '🤖 AI Study Assistant' from the sidebar to chat.")
        with qa2:
            if st.button("➕ Add New Subject", use_container_width=True):
                st.info("Tip: Select '📚 My Subjects' from the sidebar to manage subjects.")
        with qa3:
            if st.button("🗓️ Split Study Hours", use_container_width=True):
                st.info("Tip: Select '🗓️ Study Schedule' to divide hours equally.")

    with col_right:
        st.markdown("### ⏳ Upcoming Examinations")
        st.caption("Calculated using custom Python datetime tools.")

        for subj in st.session_state["subjects"]:
            ex_date = subj.get("exam_date")
            if ex_date:
                # Use days_until_exam tool directly to compute exact countdown
                countdown_msg = days_until_exam.invoke({"exam_date": ex_date})
                
                # Determine urgency styling
                badge_html = ""
                try:
                    delta = (datetime.strptime(ex_date, "%Y-%m-%d").date() - date.today()).days
                    if delta < 0:
                        badge_html = f"<span class='badge-passed'>Passed</span>"
                    elif delta <= 7:
                        badge_html = f"<span class='badge-urgent'>{delta} days left</span>"
                    elif delta <= 30:
                        badge_html = f"<span class='badge-upcoming'>{delta} days left</span>"
                    else:
                        badge_html = f"<span class='badge-safe'>{delta} days left</span>"
                except Exception:
                    badge_html = "<span class='badge-upcoming'>Tracked</span>"

                st.markdown(f"""
                <div class="notion-card">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <span style="font-weight: 600; font-size: 14px; color: #1F2937;">{subj['name']}</span>
                        {badge_html}
                    </div>
                    <div style="font-size: 12px; color: #6B7280; margin-top: 4px;">
                        📅 Date: <b>{ex_date}</b>
                    </div>
                    <div style="font-size: 12px; color: #4F46E5; margin-top: 6px; font-weight: 500;">
                        {countdown_msg}
                    </div>
                </div>
                """, unsafe_allow_html=True)

    # Weekly Progress Chart Section
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("### 📈 Weekly Study Progress")
    df_progress = pd.DataFrame(st.session_state["study_logs"])
    df_progress["progress_pct"] = (df_progress["completed"] / df_progress["planned"] * 100).round(1)

    chart_col, stat_col = st.columns([3, 1])
    with chart_col:
        chart_data = df_progress.set_index("day")[["planned", "completed"]]
        chart_data.columns = ["Planned Hours", "Completed Hours"]
        st.bar_chart(chart_data, color=["#CBD5E1", "#4F46E5"], height=260)
    with stat_col:
        total_wk_planned = df_progress["planned"].sum()
        total_wk_completed = df_progress["completed"].sum()
        pct_wk = (total_wk_completed / total_wk_planned * 100) if total_wk_planned > 0 else 0.0

        st.markdown(f"""
        <div class="notion-card">
            <div class="metric-title">Weekly Target</div>
            <div class="metric-value">{pct_wk:.1f}%</div>
            <p style="font-size: 13px; color: #4B5563; margin-top: 8px;">
                <b>{total_wk_completed:.1f}</b> of <b>{total_wk_planned:.1f}</b> planned hours completed this week.
            </p>
        </div>
        """, unsafe_allow_html=True)


# ---------------------------------------------------------
# VIEW 2: AI Study Assistant
# ---------------------------------------------------------
elif nav_option == "🤖 AI Study Assistant":
    st.markdown("## 🤖 AI Study Assistant")
    st.caption("Powered by Google Gemini & Custom Python Tools. Ask about exam countdowns, study hour splits, or revision plans.")

    # Security check banner
    if not st.session_state["gemini_api_key"]:
        st.warning("⚠️ **Gemini API Key Required**: Please enter your Gemini API key in the sidebar to enable live AI responses and tool executions. You can get a free key at [Google AI Studio](https://aistudio.google.com).")

    # Sample prompt chips
    st.markdown("##### 💡 Try asking:")
    chip_col1, chip_col2, chip_col3 = st.columns(3)
    with chip_col1:
        if st.button("🗓️ 'How many days until my Python exam on 15 December 2026?'", use_container_width=True):
            st.session_state["pending_prompt"] = "How many days until my Python exam on 15 December 2026?"
    with chip_col2:
        if st.button("⏱️ 'I have 12 hours and four subjects: Python, DBMS, OS, and CN.'", use_container_width=True):
            st.session_state["pending_prompt"] = "I have 12 hours and four subjects: Python, DBMS, OS, and CN."
    with chip_col3:
        if st.button("🎯 'My name is Rahul. Recommend a revision plan for DBMS.'", use_container_width=True):
            st.session_state["pending_prompt"] = "My name is Rahul. Recommend a revision plan for DBMS."

    st.markdown("---")

    # Display Chat History
    for msg in st.session_state["chat_history"]:
        role = msg.get("role")
        content = msg.get("content", "")
        tools_used = msg.get("tools_used", [])

        with st.chat_message(role):
            st.markdown(content)

            # Display Tools Used Section if any tools were executed
            if tools_used:
                with st.expander(f"🛠️ **Tools Used ({len(tools_used)})**", expanded=False):
                    for t in tools_used:
                        st.markdown(f"**Tool:** `{t.get('name')}`")
                        st.markdown(f"**Input Arguments:** `{t.get('args')}`")
                        st.markdown(f"**Tool Output:**")
                        st.code(t.get("output"), language="text")

    # Chat Input Box
    user_input = st.chat_input("Ask Study Planner AI anything about your exams or schedules...")
    if "pending_prompt" in st.session_state and st.session_state["pending_prompt"]:
        user_input = st.session_state.pop("pending_prompt")

    if user_input:
        # Display user message immediately
        with st.chat_message("user"):
            st.markdown(user_input)

        # Store in session state
        st.session_state["chat_history"].append({
            "role": "user",
            "content": user_input,
            "tools_used": []
        })

        # Process with Assistant Core
        assistant = StudyPlannerAssistant(api_key=st.session_state["gemini_api_key"])

        with st.chat_message("assistant"):
            with st.spinner("Analyzing schedule and calculating details..."):
                result = assistant.generate_response(
                    user_message=user_input,
                    conversation_history=st.session_state["chat_history"][:-1]
                )

            st.markdown(result["response"])

            # Render Tools Used if executed
            if result.get("tools_used"):
                with st.expander(f"🛠️ **Tools Used ({len(result['tools_used'])})**", expanded=True):
                    for t in result["tools_used"]:
                        st.markdown(f"**Tool:** `{t.get('name')}`")
                        st.markdown(f"**Input Arguments:** `{t.get('args')}`")
                        st.markdown(f"**Tool Output:**")
                        st.code(t.get("output"), language="text")

            # Append assistant message to chat history
            st.session_state["chat_history"].append({
                "role": "assistant",
                "content": result["response"],
                "tools_used": result.get("tools_used", [])
            })


# ---------------------------------------------------------
# VIEW 3: My Subjects
# ---------------------------------------------------------
elif nav_option == "📚 My Subjects":
    st.markdown("## 📚 Subject Management")
    st.caption("Organize your academic courses, set priorities, difficulty ratings, and target examination dates.")

    # Two column layout: View Subjects & Add Subject Form
    col_view, col_add = st.columns([3, 2])

    with col_add:
        st.markdown("### ➕ Add New Subject")
        with st.form("add_subject_form", clear_on_submit=True):
            new_name = st.text_input("Subject Name", placeholder="e.g. Software Engineering")
            new_priority = st.selectbox("Priority Level", ["High", "Medium", "Low"], index=0)
            new_diff = st.selectbox("Difficulty Level", ["Easy", "Medium", "Hard"], index=1)
            new_date = st.date_input("Target Exam Date", min_value=date.today())
            new_hours = st.number_input("Planned Study Hours (per week)", min_value=1.0, max_value=40.0, value=8.0, step=0.5)

            submitted = st.form_submit_button("Add Subject", use_container_width=True)
            if submitted:
                if not new_name.strip():
                    st.error("Please provide a valid subject name.")
                else:
                    st.session_state["subjects"].append({
                        "name": new_name.strip(),
                        "priority": new_priority,
                        "difficulty": new_diff,
                        "exam_date": str(new_date),
                        "planned_hours": float(new_hours),
                    })
                    st.success(f"Added '{new_name}' to your courses!")
                    st.rerun()

    with col_view:
        st.markdown("### 📖 Registered Courses")
        if not st.session_state["subjects"]:
            st.info("No subjects added yet. Use the form on the right to add your first course.")
        else:
            for idx, subj in enumerate(st.session_state["subjects"]):
                with st.container():
                    c_title, c_del = st.columns([4, 1])
                    with c_title:
                        st.markdown(f"#### **{subj['name']}**")
                    with c_del:
                        if st.button("🗑️ Delete", key=f"del_subj_{idx}"):
                            st.session_state["subjects"].pop(idx)
                            st.toast(f"Removed {subj['name']}", icon="🗑️")
                            st.rerun()

                    c1, c2, c3, c4 = st.columns(4)
                    with c1:
                        st.caption("Priority")
                        st.markdown(f"**{subj['priority']}**")
                    with c2:
                        st.caption("Difficulty")
                        st.markdown(f"**{subj['difficulty']}**")
                    with c3:
                        st.caption("Exam Date")
                        st.markdown(f"`{subj.get('exam_date', 'Not set')}`")
                    with c4:
                        st.caption("Weekly Hours")
                        st.markdown(f"**{subj.get('planned_hours', 0.0)} hrs**")

                    st.markdown("<hr style='margin: 8px 0 16px 0; border: none; border-bottom: 1px solid #e5e7eb;'>", unsafe_allow_html=True)


# ---------------------------------------------------------
# VIEW 4: Study Schedule
# ---------------------------------------------------------
elif nav_option == "🗓️ Study Schedule":
    st.markdown("## 🗓️ Study Schedule & Hour Allocator")
    st.caption("Distribute your available study hours equally using the built-in split_study_hours tool.")

    col_calc, col_tasks = st.columns([2, 3])

    with col_calc:
        st.markdown("### ⚡ Equal Hour Allocator")
        st.write("Divide available study hours equally across your subjects.")

        subject_names = [s["name"] for s in st.session_state["subjects"]]
        default_selected = subject_names[:4] if len(subject_names) >= 4 else subject_names

        selected_subs = st.multiselect("Select Subjects to distribute:", options=subject_names, default=default_selected)
        custom_sub_str = st.text_input("Or type custom subjects (comma-separated):", placeholder="Python, DBMS, OS, CN")
        hours_to_split = st.number_input("Total Available Study Hours:", min_value=0.5, max_value=100.0, value=12.0, step=0.5)

        if st.button("⚖️ Calculate Equal Split", use_container_width=True):
            # Prioritize custom subjects string if typed, else use selected list
            target_subjects = [s.strip() for s in custom_sub_str.split(",") if s.strip()] if custom_sub_str.strip() else selected_subs

            if not target_subjects:
                st.error("Please select or enter at least one subject.")
            else:
                # Call split_study_hours tool directly
                split_result = split_study_hours.invoke({
                    "total_hours": hours_to_split,
                    "subjects": target_subjects
                })

                st.success("Study hours successfully divided!")
                st.code(split_result, language="text")

                # Action to load into today's tasks
                per_sub_hrs = hours_to_split / len(target_subjects)
                if st.button("📥 Add Sessions to Today's Tasks"):
                    st.session_state["today_tasks"] = [
                        {
                            "subject": subj,
                            "duration": round(per_sub_hrs, 2),
                            "start_time": "Flexible",
                            "task": f"Dedicated Study ({per_sub_hrs:.1f}h)",
                            "completed": False
                        }
                        for subj in target_subjects
                    ]
                    st.success("Updated today's study plan!")
                    st.rerun()

    with col_tasks:
        st.markdown("### 📋 Active Study Sessions")
        st.caption("Manage your current study agenda:")

        for idx, t in enumerate(st.session_state["today_tasks"]):
            t_col1, t_col2, t_col3 = st.columns([0.5, 3.5, 1.5])
            with t_col1:
                chk = st.checkbox("", value=t["completed"], key=f"sched_chk_{idx}")
                if chk != t["completed"]:
                    st.session_state["today_tasks"][idx]["completed"] = chk
                    st.rerun()
            with t_col2:
                name_display = f"~~{t['subject']}~~" if t["completed"] else f"**{t['subject']}**"
                st.markdown(name_display)
                st.caption(f"{t.get('task', 'Practice')} • ⏱️ {t.get('duration', 1.0)} hrs")
            with t_col3:
                status_txt = "✅ Done" if t["completed"] else "⏳ Pending"
                st.markdown(f"**{status_txt}**")

        st.markdown("<br>", unsafe_allow_html=True)
        st.info("💡 Note: Schedule is held in current session memory for maximum security and privacy.")


# ---------------------------------------------------------
# VIEW 5: Exam Countdown
# ---------------------------------------------------------
elif nav_option == "⏳ Exam Countdown":
    st.markdown("## ⏳ Examination Countdown")
    st.caption("Track the exact days remaining until your university exams using the days_until_exam tool.")

    # Exam countdown grid
    c_list, c_calc = st.columns([3, 2])

    with c_list:
        st.markdown("### 🎯 Registered Exam Deadlines")
        for subj in st.session_state["subjects"]:
            ex_date = subj.get("exam_date")
            if ex_date:
                calc_result = days_until_exam.invoke({"exam_date": ex_date})
                st.markdown(f"""
                <div class="notion-card">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <h4 style="margin: 0; color: #111827;">{subj['name']}</h4>
                        <span style="font-size: 13px; color: #6B7280;">Target: <b>{ex_date}</b></span>
                    </div>
                    <div style="margin-top: 10px; font-size: 15px; font-weight: 600; color: #4F46E5;">
                        {calc_result}
                    </div>
                    <div style="margin-top: 6px; font-size: 12px; color: #6B7280;">
                        Priority: <b>{subj.get('priority', 'Medium')}</b> • Difficulty: <b>{subj.get('difficulty', 'Medium')}</b>
                    </div>
                </div>
                """, unsafe_allow_html=True)

    with c_calc:
        st.markdown("### 🔎 Quick Date Calculator")
        st.write("Test any custom examination date directly with the `days_until_exam` tool:")

        custom_date_input = st.text_input("Enter exam date (any format):", value="15 December 2026")
        if st.button("Calculate Remaining Days", use_container_width=True):
            calc_out = days_until_exam.invoke({"exam_date": custom_date_input})
            st.markdown(f"""
            <div class="tool-box">
                <b>Tool Result:</b><br>{calc_out}
            </div>
            """, unsafe_allow_html=True)


# ---------------------------------------------------------
# VIEW 6: Progress Tracker
# ---------------------------------------------------------
elif nav_option == "📈 Progress Tracker":
    st.markdown("## 📈 Academic Progress Tracker")
    st.caption("Monitor your planned versus completed study hours across courses.")

    # Metrics Row
    total_planned = get_total_planned_hours()
    completed_today = get_completed_today_hours()
    df_logs = pd.DataFrame(st.session_state["study_logs"])
    wk_completed = df_logs["completed"].sum()
    wk_planned = df_logs["planned"].sum()
    completion_pct = (wk_completed / wk_planned * 100) if wk_planned > 0 else 0.0

    p1, p2, p3, p4 = st.columns(4)
    with p1:
        st.metric("Total Weekly Target", f"{wk_planned:.1f} hrs")
    with p2:
        st.metric("Completed This Week", f"{wk_completed:.1f} hrs")
    with p3:
        st.metric("Weekly Completion", f"{completion_pct:.1f}%")
    with p4:
        st.metric("Today's Study", f"{completed_today:.1f} hrs")

    st.markdown("<br>", unsafe_allow_html=True)
    st.progress(min(completion_pct / 100.0, 1.0))

    st.markdown("<br>", unsafe_allow_html=True)
    c_chart, c_subject = st.columns([3, 2])

    with c_chart:
        st.markdown("### 📊 Daily Study Trends")
        chart_df = df_logs.set_index("day")[["planned", "completed"]]
        chart_df.columns = ["Target (hrs)", "Studied (hrs)"]
        st.bar_chart(chart_df, color=["#E2E8F0", "#3B82F6"], height=280)

    with c_subject:
        st.markdown("### 📚 Subject-wise Allocation")
        if st.session_state["subjects"]:
            sub_df = pd.DataFrame(st.session_state["subjects"])[["name", "planned_hours", "priority"]]
            sub_df.columns = ["Subject", "Target Hours", "Priority"]
            st.dataframe(sub_df, use_container_width=True, hide_index=True)
        else:
            st.info("No courses currently registered.")

    st.caption("📌 **Session Data Notice:** Progress metrics are actively stored during your current session.")


# ---------------------------------------------------------
# VIEW 7: Settings
# ---------------------------------------------------------
elif nav_option == "⚙️ Settings":
    st.markdown("## ⚙️ Application Settings")
    st.caption("Manage student preferences and configure AI parameters.")

    col_s1, col_s2 = st.columns(2)

    with col_s1:
        st.markdown("### 👤 Student Profile")
        name_input = st.text_input("Your Name / Preferred Title", value=st.session_state["student_name"])
        if name_input != st.session_state["student_name"]:
            st.session_state["student_name"] = name_input.strip()
            st.success("Updated profile name!")

        st.markdown("### 🔑 API Key Status")
        if st.session_state["gemini_api_key"]:
            st.success("Gemini API key is configured for this session.")
        else:
            st.warning("No Gemini API key detected.")

        if st.button("🧪 Test API Key Connection"):
            if not st.session_state["gemini_api_key"]:
                st.error("Please enter your Gemini API key in the sidebar first.")
            else:
                with st.spinner("Testing connection to Gemini..."):
                    test_assistant = StudyPlannerAssistant(api_key=st.session_state["gemini_api_key"])
                    test_res = test_assistant.generate_response("Hello", [])
                    if test_res["success"]:
                        st.success("✅ Connection Successful! Gemini is responding properly.")
                    else:
                        st.error(f"❌ Connection Failed: {test_res['response']}")

    with col_s2:
        st.markdown("### ℹ️ About Study Planner AI")
        st.markdown("""
        **Study Planner AI** is a personal AI assistant built for university students to organize schedules, calculate exact exam deadlines, and distribute study hours.

        - **Frontend:** Streamlit 1.67.0
        - **AI Engine:** Google Gemini via LangChain (`langchain-google-genai`)
        - **Custom Tools:** `days_until_exam`, `split_study_hours`
        - **Architecture:** Multi-turn session memory with offline tool execution
        """)

        if st.button("🔄 Reset to Default Sample Data"):
            st.session_state["subjects"] = [
                {"name": "Python Programming", "priority": "High", "difficulty": "Medium", "exam_date": "2026-12-15", "planned_hours": 10.0},
                {"name": "Database Management (DBMS)", "priority": "High", "difficulty": "Medium", "exam_date": "2026-12-18", "planned_hours": 8.0},
                {"name": "Operating Systems (OS)", "priority": "High", "difficulty": "Hard", "exam_date": "2026-12-22", "planned_hours": 12.0},
                {"name": "Computer Networks (CN)", "priority": "Medium", "difficulty": "Medium", "exam_date": "2026-12-28", "planned_hours": 8.0},
            ]
            st.session_state["chat_history"] = []
            st.toast("Reset to default sample courses!", icon="🔄")
            st.rerun()
