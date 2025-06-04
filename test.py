import streamlit as st
import json

st.set_page_config(page_title="Interactive AI Debugger", layout="wide")
st.title("🧠 Interactive AI Code Debugger")

# Session state to hold conversation history
if "history" not in st.session_state:
    st.session_state.history = []

# --- Dummy AI Debugger Function (Replace with OpenAI or other backend) ---
def debug_code(code: str):
    # Simulated example with hardcoded logic errors
    if "total += i" in code:
        correction = code.replace("total += i", "total += nums[i]")  # or total += num if rewritten
        return {
            "checks": [
                {
                    "errorType": "logic error",
                    "range": [3, 4],
                    "advice": "Change 'total += i' to 'total += nums[i]' or iterate directly with 'for num in nums'"
                }
            ],
            "correction": correction
        }
    elif "user.age" in code:
        correction = code.replace("user.age", "user.get(\"age\", 0)")
        return {
            "checks": [
                {
                    "errorType": "runtime error",
                    "range": [6],
                    "advice": "Use user.get(\"age\", 0) instead of accessing attribute 'age'"
                }
            ],
            "correction": correction
        }
    else:
        return {
            "checks": [],
            "correction": code
        }

# --- UI ---
st.subheader("Paste your Python code below")
user_code = st.text_area("Python Code", height=300)

if st.button("🔍 Debug"):
    if user_code.strip():
        result = debug_code(user_code)
        st.session_state.history.append({"input": user_code, "output": result})
    else:
        st.warning("Please paste some code first.")

# Show history (multi-round)
for i, step in enumerate(st.session_state.history):
    with st.expander(f"🧪 Debug Round {i + 1}", expanded=(i == len(st.session_state.history) - 1)):
        st.subheader("🔢 Input Code")
        st.code(step["input"], language="python")

        if step["output"]["checks"]:
            st.subheader("⚠️ Detected Issues")
            for check in step["output"]["checks"]:
                st.markdown(f"""
                **Error Type**: `{check["errorType"]}`  
                **Line(s)**: `{check["range"]}`  
                **Advice**: {check["advice"]}
                """)
        else:
            st.success("✅ No issues detected.")

        st.subheader("✅ Suggested Correction")
        st.code(step["output"]["correction"], language="python")

        if st.button("Use this corrected code", key=f"use_{i}"):
            st.session_state.history.append({"input": step["output"]["correction"], "output": debug_code(step["output"]["correction"])})

