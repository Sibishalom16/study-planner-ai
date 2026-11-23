"""
assistant_core.py
-----------------
Core AI logic for Study Planner AI:
- Google Gemini integration via LangChain (ChatGoogleGenerativeAI).
- System prompt enforcement.
- Multi-turn conversation memory.
- Exact tool execution and two-step tool synthesis.
- Safe, visitor-friendly error handling.
"""

from typing import List, Dict, Any, Optional
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, ToolMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from tools import CUSTOM_TOOLS, days_until_exam, split_study_hours

# System Prompt required by the assignment specification
SYSTEM_PROMPT = """You are Study Planner AI, a friendly and intelligent academic planning assistant.

Your responsibility is to help students organize their academic schedules, plan revisions, distribute study hours, prepare for examinations, and improve study productivity.

You must use available Python tools for exact calculations:
- Use 'days_until_exam' whenever a student asks about days remaining or countdown to an exam.
- Use 'split_study_hours' whenever a student asks to divide, distribute, or split study hours across subjects.

You must remember relevant information from the current conversation (e.g., student's name, subjects, exam dates, study hours, and preferences).

You must ask follow-up questions when necessary information is missing.

You must not invent dates, calculations, tool results, or student information.

You must politely decline questions unrelated to academic study planning.

You must clearly communicate tool errors.

You are a study assistant, not a replacement for teachers or academic professionals.

Keep your responses structured, clear, friendly, and concise."""

# Map tool names to tool callable instances
TOOL_MAP = {
    "days_until_exam": days_until_exam,
    "split_study_hours": split_study_hours,
}


class StudyPlannerAssistant:
    """
    Manages communication between the Streamlit UI, LangChain,
    and Google Gemini with custom tool integration and session memory.
    """

    def __init__(self, api_key: str, model_name: str = "gemini-1.5-flash", temperature: float = 0.3):
        self.api_key = api_key.strip() if api_key else ""
        self.model_name = model_name
        self.temperature = temperature
        self._llm = None
        self._llm_with_tools = None

        if self.api_key:
            self._init_llm()

    def _init_llm(self):
        """Initializes ChatGoogleGenerativeAI with bound tools."""
        self._llm = ChatGoogleGenerativeAI(
            model=self.model_name,
            google_api_key=self.api_key,
            temperature=self.temperature,
        )
        self._llm_with_tools = self._llm.bind_tools(CUSTOM_TOOLS)

    def generate_response(
        self,
        user_message: str,
        conversation_history: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Processes a user message with multi-turn conversation memory and tool calling.
        
        Args:
            user_message: The latest prompt from the student.
            conversation_history: List of previous messages [{"role": "user"|"assistant", "content": "..."}].
            
        Returns:
            Dict containing:
                - response (str): AI's final answer.
                - tools_used (list): Details of tools called during this turn.
                - success (bool): Whether the request succeeded.
                - error (str | None): Human-friendly error message if failed.
        """
        # Validate API Key presence
        if not self.api_key:
            return {
                "response": "⚠️ **API Key Missing**: Please enter your Google Gemini API key in the sidebar to chat with Study Planner AI.",
                "tools_used": [],
                "success": False,
                "error": "API Key is missing."
            }

        # Lazy init if not already initialized
        if self._llm_with_tools is None:
            try:
                self._init_llm()
            except Exception as e:
                return {
                    "response": f"⚠️ **Initialization Error**: Could not initialize the Gemini model. Please verify your API key.",
                    "tools_used": [],
                    "success": False,
                    "error": str(e)
                }

        # Build message history for LangChain
        messages = [SystemMessage(content=SYSTEM_PROMPT)]

        # Append previous conversation history
        for msg in conversation_history:
            role = msg.get("role")
            content = msg.get("content", "")
            if role == "user":
                messages.append(HumanMessage(content=content))
            elif role == "assistant":
                messages.append(AIMessage(content=content))

        # Append the new user message
        messages.append(HumanMessage(content=user_message))

        tools_used: List[Dict[str, Any]] = []

        try:
            # 1. Call Gemini with tools bound
            first_response = self._llm_with_tools.invoke(messages)

            # Check if Gemini decided to invoke any tools
            if hasattr(first_response, "tool_calls") and first_response.tool_calls:
                tool_messages = []
                for tc in first_response.tool_calls:
                    tool_name = tc.get("name")
                    tool_args = tc.get("args", {})
                    call_id = tc.get("id") or tool_name

                    # Execute the registered tool safely
                    if tool_name in TOOL_MAP:
                        target_tool = TOOL_MAP[tool_name]
                        try:
                            # Invoke tool
                            tool_result = target_tool.invoke(tool_args)
                        except Exception as tool_err:
                            tool_result = f"Error executing tool '{tool_name}': {str(tool_err)}"
                    else:
                        tool_result = f"Error: Tool '{tool_name}' is not recognized."

                    # Record execution for the UI "Tools Used" section
                    tools_used.append({
                        "name": tool_name,
                        "args": tool_args,
                        "output": str(tool_result),
                    })

                    # Create ToolMessage to feed back into the conversation
                    tool_messages.append(
                        ToolMessage(
                            content=str(tool_result),
                            tool_call_id=call_id,
                            name=tool_name
                        )
                    )

                # 2. Feed tool results back to Gemini to synthesize the final user-facing response
                synthesis_messages = messages + [first_response] + tool_messages
                second_response = self._llm_with_tools.invoke(synthesis_messages)

                final_text = second_response.content
                if isinstance(final_text, list):
                    # Handle complex content blocks if returned as list
                    final_text = "".join(str(part.get("text", part)) if isinstance(part, dict) else str(part) for part in final_text)

                return {
                    "response": str(final_text).strip(),
                    "tools_used": tools_used,
                    "success": True,
                    "error": None
                }

            else:
                # No tool calls needed; return direct response
                direct_text = first_response.content
                if isinstance(direct_text, list):
                    direct_text = "".join(str(part.get("text", part)) if isinstance(part, dict) else str(part) for part in direct_text)

                return {
                    "response": str(direct_text).strip(),
                    "tools_used": [],
                    "success": True,
                    "error": None
                }

        except Exception as e:
            err_msg = str(e)
            user_error = self._format_user_error(err_msg)
            return {
                "response": user_error,
                "tools_used": tools_used,
                "success": False,
                "error": err_msg
            }

    @staticmethod
    def _format_user_error(raw_error: str) -> str:
        """Translates raw exceptions into friendly, secure visitor messages without exposing secrets."""
        raw_lower = raw_error.lower()
        if "api_key" in raw_lower or "401" in raw_lower or "invalid api key" in raw_lower or "unauthenticated" in raw_lower:
            return "⚠️ **Invalid API Key**: Your Gemini API key could not be authenticated. Please verify or re-enter your key from [Google AI Studio](https://aistudio.google.com)."
        elif "quota" in raw_lower or "429" in raw_lower or "resource_exhausted" in raw_lower:
            return "⏳ **Quota Limit Reached**: The Gemini API request quota has been exceeded for this key. Please wait a minute before sending another message or use another key."
        elif "connection" in raw_lower or "timeout" in raw_lower or "dns" in raw_lower:
            return "🌐 **Connection Issue**: Unable to reach Google Gemini services. Please check your network connection and try again."
        elif "model" in raw_lower and "not found" in raw_lower:
            return "🤖 **Model Unavailable**: The specified Gemini model is not accessible with this API key. Using default 'gemini-1.5-flash'."
        else:
            return "⚠️ **Temporary AI Error**: An unexpected issue occurred while processing your request. Please try again or rephrase your study query."
