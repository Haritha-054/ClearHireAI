"""
app.py — Flask ML Service for Resume Parsing
"""

import os
from flask import Flask, request, jsonify
from flask_cors import CORS

from parser import (
    extract_text_from_pdf,
    extract_text_from_docx,
    parse_resume,
)

from evaluator import evaluate_candidate

app = Flask(__name__)
CORS(app)

ALLOWED_EXTENSIONS = {'pdf', 'docx'}


# =========================
# HELPERS
# =========================
def allowed_file(filename: str) -> bool:
    return (
        '.' in filename and
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
    )


# =========================
# HEALTH ROUTE
# =========================
@app.route('/', methods=['GET'])
def home():
    return jsonify({
        'success': True,
        'message': 'ClearHireAI ML Service Running 🚀'
    })


@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({
        'status': 'ok',
        'service': 'ClearHireAI ML Service'
    })


# =========================
# RESUME PARSER
# =========================
@app.route('/api/parse', methods=['POST'])
def parse():

    if 'file' not in request.files:
        return jsonify({
            'error': 'No file uploaded'
        }), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({
            'error': 'Empty filename'
        }), 400

    if not allowed_file(file.filename):
        return jsonify({
            'error': 'Unsupported file type'
        }), 400

    try:
        file_bytes = file.read()
        filename = file.filename.lower()

        if filename.endswith('.pdf'):
            text = extract_text_from_pdf(file_bytes)

        elif filename.endswith('.docx'):
            text = extract_text_from_docx(file_bytes)

        else:
            return jsonify({
                'error': 'Unsupported format'
            }), 400

        if not text or len(text.strip()) < 20:
            return jsonify({
                'error': 'Could not extract text'
            }), 422

        parsed = parse_resume(text)

        return jsonify({
            'success': True,
            'filename': file.filename,
            'parsed': parsed
        })

    except Exception as e:
        return jsonify({
            'error': str(e)
        }), 500


# =========================
# EVALUATION ROUTE
# =========================
@app.route('/api/evaluate', methods=['POST'])
def evaluate():

    try:
        data = request.get_json()

        if not data:
            return jsonify({
                'error': 'No input data'
            }), 400

        parsed_data = data.get('parsed_data', {})
        jd_text = data.get('jd_text', '')

        evaluation = evaluate_candidate(
            parsed_data,
            jd_text
        )

        return jsonify(evaluation)

    except Exception as e:
        return jsonify({
            'error': str(e)
        }), 500


# =========================
# AI CHAT ROUTE
# =========================
@app.route('/api/chat', methods=['POST'])
def chat():

    try:
        data = request.get_json()

        query = data.get('query', '').lower()
        eval_data = data.get('evaluation_data', {})

        if not query:
            return jsonify({
                'answer': 'Please ask a valid question.'
            })

        if "why" in query and "reject" in query:
            answer = (
                "The candidate was rejected mainly due to "
                "missing required skills and experience gaps."
            )

        elif "improve" in query:
            answer = (
                "Focus on improving DSA, projects, "
                "system design, and core development skills."
            )

        elif "skill" in query:
            answer = (
                "Recommended skills: React, Node.js, "
                "Python, SQL, and System Design."
            )

        else:
            answer = (
                "I'm your AI Hiring Assistant. "
                "Ask about rejection reasons or improvements."
            )

        return jsonify({
            'answer': answer
        })

    except Exception as e:
        return jsonify({
            'error': str(e)
        }), 500


# =========================
# START SERVER
# =========================
if __name__ == '__main__':

    port = int(os.environ.get('PORT', 8000))

    app.run(
        host='0.0.0.0',
        port=port,
        debug=True
    )