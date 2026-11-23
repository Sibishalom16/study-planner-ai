# Study Planner AI — Test Scenarios & Verification Report

This document records the exact test scenarios and verification results for **Study Planner AI** as required by the assignment guidelines. Both Python tools and the assistant core are tested independently and end-to-end.

---

## Summary of Test Results

| Test ID | Test Scenario | Execution Mode | Expected Output | Actual Output | Status |
|---|---|---|---|---|---|
| **TEST-01** | Conversation Memory Test | Assistant Core Session State | Remembers student name & subject | Successfully recalls context across turns | **PASS** |
| **TEST-02** | Exam Countdown Tool Test | `days_until_exam` Tool Call | Exactly 22 days remaining | `"Your examination is 22 days away."` | **PASS** |
| **TEST-03** | Study Hours Distribution Test | `split_study_hours` Tool Call | 3 hours per subject across 4 subjects | 3 hours each for Python, DBMS, OS, CN | **PASS** |
| **TEST-04** | General Study Advice (No Tools) | AI Assistant Synthesis | Direct advice with empty `tools_used` | Academic advice returned, 0 tools called | **PASS** |
| **TEST-05** | Out-of-Scope Question Handling | AI Assistant System Prompt | Polite refusal of non-academic queries | Politely declines non-academic queries | **PASS** |
| **TEST-06** | Invalid Input & Edge Case Handling | Offline Python Validation | Graceful error messages without crash | Catches invalid dates, negative hours, & empty lists | **PASS** |

---

## Detailed Test Cases

### Scenario 1: Memory Test

- **Objective:** Verify that multi-turn conversation memory retains student identity, enrolled courses, and previous context within the active session.
- **Test Input:**
  - *Turn 1:* `"Hi, my name is Sibi and I have an examination on Operating Systems."`
  - *Turn 2:* `"What is my name and which examination did I mention earlier?"`
- **Expected Output:**
  - The assistant should address the user as Sibi and state that the upcoming examination mentioned is Operating Systems without asking for re-entry.
- **Actual Output:**
  - *"Hello Sibi! You mentioned earlier that you have an upcoming examination in Operating Systems (OS). How can I help you organize your revision schedule for it?"*
- **Pass/Fail Status:** **PASS**

---

### Scenario 2: Exam Countdown Tool Test

- **Objective:** Verify that `days_until_exam` calculates the exact number of days remaining until an upcoming examination date offline.
- **Reference Date:** `23 November 2026`
- **Test Input:**
  - `"How many days are left until my Python exam on 15 December 2026?"`
  - Tool invocation argument: `{"exam_date": "15 December 2026"}`
- **Expected Output:**
  - `"Your examination is 22 days away."`
- **Actual Output:**
  ```text
  Your examination is 22 days away.
  ```
- **Pass/Fail Status:** **PASS**

---

### Scenario 3: Study Hours Distribution Tool Test

- **Objective:** Verify that `split_study_hours` equally divides available study hours across multiple subjects with clean formatting.
- **Test Input:**
  - `"I have 12 hours and four subjects: Python, DBMS, OS, and CN."`
  - Tool invocation arguments: `{"total_hours": 12, "subjects": ["Python", "DBMS", "OS", "CN"]}`
- **Expected Output:**
  ```text
  Python: 3 hours
  DBMS: 3 hours
  OS: 3 hours
  CN: 3 hours
  ```
- **Actual Output:**
  ```text
  Python: 3 hours
  DBMS: 3 hours
  OS: 3 hours
  CN: 3 hours
  ```
- **Pass/Fail Status:** **PASS**

---

### Scenario 4: General Study Advice Without Tools

- **Objective:** Verify that non-computational academic study inquiries are answered with helpful advice without triggering calculation tools.
- **Test Input:**
  - `"Can you give me effective revision techniques for Computer Science exams?"`
- **Expected Output:**
  - Structured academic recommendations (e.g., Active Recall, Spaced Repetition, LeetCode / SQL practice) without calling any tools (`tools_used == []`).
- **Actual Output:**
  - The assistant provided a 4-point revision framework (Active Recall, Pomodoro Technique, Topic prioritization, and past paper practice). The `tools_used` inspectable expander showed 0 tools executed.
- **Pass/Fail Status:** **PASS**

---

### Scenario 5: Out-of-Scope Question Test

- **Objective:** Verify that questions completely unrelated to academic study planning are politely declined according to the system prompt.
- **Test Input:**
  - `"Can you give me a recipe for chocolate cake and tell me who won the football match yesterday?"`
- **Expected Output:**
  - Polite decline stating that the assistant specializes strictly in academic study planning and preparation.
- **Actual Output:**
  - *"I specialize strictly in academic planning, study schedules, and examination preparation for students. I cannot assist with cooking recipes or sports scores. Let me know if you need help planning your study sessions or organizing your subjects!"*
- **Pass/Fail Status:** **PASS**

---

### Scenario 6: Invalid Input Test

- **Objective:** Verify that invalid dates, negative study hours, and empty subject lists return friendly error messages without raising unhandled exceptions.
- **Test Inputs & Executions:**
  1. *Subcase A — Invalid Date Format:*
     - Input: `days_until_exam.invoke({"exam_date": "32-13-2099"})`
     - Expected: Clear parse error message.
     - Actual Output:
       ```text
       Error: Unable to parse '32-13-2099' as a valid date. Please use formats like YYYY-MM-DD (e.g., 2026-12-15) or '15 December 2026'.
       ```
  2. *Subcase B — Negative Study Hours:*
     - Input: `split_study_hours.invoke({"total_hours": -4, "subjects": ["Python"]})`
     - Expected: Clear validation error rejecting negative numbers.
     - Actual Output:
       ```text
       Error: Total available study hours must be greater than zero. Negative or zero hours cannot be distributed.
       ```
  3. *Subcase C — Empty Subject List:*
     - Input: `split_study_hours.invoke({"total_hours": 10, "subjects": []})`
     - Expected: Clear validation error rejecting empty subjects.
     - Actual Output:
       ```text
       Error: The subject list cannot be empty. Please provide at least one subject to divide hours.
       ```
- **Pass/Fail Status:** **PASS**

---

## Conclusion
All 6 test scenarios pass without errors or regressions. Both custom tools execute accurately and handle edge cases gracefully.
