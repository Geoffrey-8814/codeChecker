import streamlit as st
import difflib

# Example input and corrected code
user_code = """def MyFunction(x,y):
 a= x+y
 return a"""

corrected_code = """def my_function(x, y):
    a = x + y
    return a"""

# Split code into lines
user_lines = user_code.splitlines()
corrected_lines = corrected_code.splitlines()

# Create diff
diff = difflib.ndiff(user_lines, corrected_lines)

# Format diff as HTML
def format_diff(diff_lines):
    html = "<div style='display: flex;'>"
    left_html = "<div style='flex: 1; padding: 10px; background-color: #f8f8f8;'><h4>User Code</h4><pre>"
    right_html = "<div style='flex: 1; padding: 10px; background-color: #f0fff0;'><h4>Corrected Code</h4><pre>"

    for line in diff_lines:
        if line.startswith('- '):
            left_html += f"<span style='background-color: #ffe6e6;'>{line[2:]}</span>\n"
            right_html += "\n"
        elif line.startswith('+ '):
            left_html += "\n"
            right_html += f"<span style='background-color: #e6ffe6;'>{line[2:]}</span>\n"
        elif line.startswith('  '):
            left_html += line[2:] + "\n"
            right_html += line[2:] + "\n"
        elif line.startswith('? '):
            continue  # skip the marker lines

    left_html += "</pre></div>"
    right_html += "</pre></div>"
    html += left_html + right_html + "</div>"
    return html

# Render in Streamlit
html_diff = format_diff(diff)
st.components.v1.html(html_diff, height=400, scrolling=True)
