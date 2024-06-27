from flask import Flask, request, jsonify, send_file
import google.generativeai as genai
import os
import tempfile

app = Flask(__name__)

# Configure the Google API key
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY', '************************')
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-1.5-pro-latest')

@app.route('/generate', methods=['POST'])
def generate():
    data = request.json
    prompt = data.get('prompt')
    if not prompt:
        return jsonify({"error": "No prompt provided"}), 400
    
    response_Skill = model.generate_content(prompt)
    response_text = response_Skill.text
    
    # Save response to a temporary file
    with tempfile.NamedTemporaryFile(delete=False, mode='w', suffix='.txt') as temp_file:
        temp_file.write(response_text)
        temp_file_path = temp_file.name
    
    return jsonify({"response": response_text, "C:\Users\Promantus\Desktop\Git": temp_file_path})

@app.route('/download', methods=['GET'])
def download():
    file_path = request.args.get('file_path')
    if not file_path or not os.path.exists(file_path):
        return jsonify({"error": "File not found"}), 404
    
    return send_file(file_path, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
