from flask import Flask, request, jsonify, send_file, render_template
import google.generativeai as genai
import os
import tempfile
import textwrap
import re

app = Flask(__name__, template_folder='templates', static_folder='static')

# Configure the Google API key
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY', 'AIzaSyArFpTILShRa8LVwG5oqHFJc4YkddY7yHA')
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-1.5-pro-latest')

# Function to convert text to markdown format
def to_markdown(text):
    # Replace bullet points with empty string
    text = text.replace('•','')
    # Add indentation for block quotes
    return textwrap.indent(text, '> ', predicate=lambda _: True)

# Helper function to ensure the table format is correct
# def ensure_table_format(text):
#     lines = text.split('\n')
#     for i in range(len(lines)):
#         if re.match(r'^\|\s*\d+\s*\|', lines[i]):
#             lines[i] = lines[i].replace(' | ', ' |').replace('| ', '|').replace(' |', '|').replace('| ', ' | ')
#     return '\n'.join(lines)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    data = request.json
    prompt = data.get('prompt')
    if not prompt:
        return jsonify({"error": "No prompt provided"}), 400

     # Add explicit instructions to the prompt
    full_prompt = (
        f"Generate test cases for the following scenario in a Markdown table format "
        f"with columns: Test Case ID, Description, Input, Expected Result.\n\n"
        f"{prompt}\n\n"
        f"## Test Cases in Markdown Table Format:\n\n"
        f"| Test Case ID | Description | Input | Expected Result |\n"
        f"|--------------|-------------|-------|-----------------|\n"
    )
    
    response_Skill = model.generate_content(full_prompt)
    response_text = response_Skill.text
    # Apply the to_markdown function
    markdown_response_text = to_markdown(response_text)
    # Ensure the table format is correct
    # formatted_text = ensure_table_format(markdown_response_text)

    # Save response to a temporary file
    temp_file = tempfile.NamedTemporaryFile(delete=False, mode='w', suffix='.xlsx')
    temp_file.write(markdown_response_text)
    temp_file_path = temp_file.name
    temp_file.close()
    
    return jsonify({"response": markdown_response_text, "file_path": temp_file_path})

@app.route('/download', methods=['GET'])
def download():
    file_path = request.args.get('file_path')
    if not file_path or not os.path.exists(file_path):
        return jsonify({"error": "File not found"}), 404
    
    return send_file(file_path, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
