from io import StringIO
import streamlit as st
import json
import difflib

from codeChecker import codeChecker

# setup page title
st.set_page_config(page_title="Interactive AI Debugger", layout="wide")
st.title("code checker")

# Session state to hold conversation history
if "history" not in st.session_state:
    st.session_state.history = []
if "tools" not in st.session_state:
    st.session_state.tools = {}

if len(st.session_state.tools) == 0:
    st.session_state.tools["checker"] = codeChecker("sk-a20fe5cabaac4bcda4af0347d3ad5038", "https://api.deepseek.com")
    
checker: codeChecker = st.session_state.tools["checker"]

# covert file to string
def readFile(uploaded_file):
    # To read file as bytes:
    bytes_data = uploaded_file.getvalue()
    st.write(bytes_data)

    # To convert to a string based IO:
    stringio = StringIO(uploaded_file.getvalue().decode("utf-8"))
    return stringio.read()

def generate_html_diff(user_code: str, corrected_code: str, highlight_lines: list[int]) -> str:
    user_lines = user_code.splitlines()
    corrected_lines = corrected_code.splitlines()

    max_len = max(len(user_lines), len(corrected_lines))
    user_lines += [""] * (max_len - len(user_lines))
    corrected_lines += [""] * (max_len - len(corrected_lines))

    html = "<div style='display: flex;'>"

    left_html = "<div style='flex: 1; padding: 10px; background-color: #f8f8f8;'><h4>User Code</h4><pre style='line-height: 1.4;'>"
    right_html = "<div style='flex: 1; padding: 10px; background-color: #f0fff0;'><h4>Corrected Code</h4><pre style='line-height: 1.4;'>"

    for i, (u, c) in enumerate(zip(user_lines, corrected_lines), start=1):
        highlight_style = "background-color: #fff8b3;" if i in highlight_lines else ""
        left_html += f"<span style='{highlight_style}'>{u}</span>\n"
        right_html += f"<span style='{highlight_style}'>{c}</span>\n"

    left_html += "</pre></div>"
    right_html += "</pre></div>"
    html += left_html + right_html + "</div>"

    return html


# select mode
mode = st.segmented_control("mode: ", ["runtime", "syntax", "logical", "style", "explanation", "chat"], default="chat")

# user input
prompt = st.chat_input(
    "Say something and/or attach an file",
    accept_file=True,
    file_type=["txt", "py", "java", "ipynb"],
)

# preprocess user input
newPrompt = False
code = ""
if prompt and prompt.text:
    newPrompt = True
    st.session_state.history.append(
        {"role" : "user", "format" : "code" if mode != "chat" and not prompt["files"] else "text", "content" : prompt.text})
    code = prompt.text
if prompt and prompt["files"]:
    newPrompt = True
    if prompt["files"] is not None:
        code = readFile(prompt["files"][0])
        st.session_state.history.append({"role" : "user", "format" : "code", "content" : code})

try:
    if newPrompt:
        
        isJson = False
        with st.status("analyzing..."):
            match mode:
                case "runtime":
                    response = checker.checkCommonRuntimeError(code)
                    isJson = True
                case "syntax":
                    response = checker.checkSyntaxError(code) 
                    isJson = True
                case "logical":
                    response = checker.AlBasedLogicErrorDetection(code)
                    isJson = True
                case "style":
                    response = checker.checkStyleViolation(code)
                    isJson = True
                case "explanation":
                    response = checker.lineByLineAIExplanation(code)
                    st.session_state.history.append({"role" : "bot", "format" : "text", "content" : response})
                case "chat":
                    response = checker.InteractiveDebugging(code)
                    st.session_state.history.append({"role" : "bot", "format" : "text", "content" : response})
            if isJson:
                # convert json data to readable words
                response = json.loads(response)
                lines = code.splitlines()
                checks = response["checks"]
                changedLines = []
                for check in checks:
                    if len(check) != 3:
                        continue
                    changedLines.append(check["range"])
                    index = check["range"][0]
                    st.session_state.history.append({"role" : "bot", "format" : "code", "content" : f"{index}: " + lines[index - 1]})
                    advice = check["advice"]
                    errorType = check["errorType"]
                    st.session_state.history.append({"role" : "bot", "format" : "text", "content" : f":red[{errorType}!] :orange[advice:] :green[{advice}]"})
                    
                st.session_state.history.append({"role" : "bot", "format" : "text", "content" : "correction:"})

                correctedCode = response["correction"]
                
                changedLines = list(set(item for sublist in changedLines for item in sublist))

                html = generate_html_diff(code, correctedCode, changedLines)
                
                st.session_state.history.append({"role" : "bot", "format" : "html", "content" : html})
                
                checker.setupConversation(code, correctedCode)
    
    # display chat history
    lastRole = None
    for message in st.session_state.history:
        if lastRole !=message["role"]:
            st.markdown("---")
            st.markdown(":blue[user:]" if message["role"] == "user" else ":green[bot:]")
        lastRole = message["role"]
        content = message["content"]
        match message["format"]:
            case "code":
                st.code(content)
            case "text":
                st.markdown(content)
            case "html":
                st.components.v1.html(content, height=400, scrolling=True)
except:
    # make sure that no error won't crush the code
    st.markdown(":red[The server is busy. Please try again later.]")