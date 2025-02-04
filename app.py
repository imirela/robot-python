from flask import Flask, request, jsonify, render_template
from fuzzywuzzy import process
import os
from gtts import gTTS
import nltk
import re
from googletrans import Translator

app = Flask(__name__)
nltk.download('punkt')  # Necesită pentru tokenizare

# Funcții ajutătoare
def load_excluded_keywords():
    file_path = os.path.join(os.path.dirname(__file__), 'excluded_keywords.txt')
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return set(file.read().splitlines())
    except FileNotFoundError:
        print("Fișierul excluded_keywords.txt nu a fost găsit.")
        return set()

def translate_text(text, lang='en'):
    translator = Translator()
    translated = translator.translate(text, dest=lang)
    return translated.text

@app.after_request
def apply_cors_and_security_headers(response):
    response.headers['Content-Security-Policy'] = "frame-ancestors 'self' http://chat-widget.liveblog365.com"
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'ALLOWALL'
    return response

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/ask_chatbot', methods=['POST'])
def ask_chatbot():
    user_question = request.json.get('question', '').lower()
    language = request.json.get('language', 'en')
    exclude_keywords = load_excluded_keywords()
    file_path_txt = os.path.join(os.path.dirname(__file__), 'data.txt')

    try:
        with open(file_path_txt, 'r', encoding='utf-8') as file:
            site_content = file.read().lower()
            site_lines = site_content.split('\n')

        question_words = user_question.split()
        matched_keywords = [word for word in question_words if word not in exclude_keywords]

        # Filtrarea liniilor relevante
        if matched_keywords:
            filtered_lines = [line for line in site_lines if any(keyword in line for keyword in matched_keywords)]
        else:
            filtered_lines = site_lines

        best_match = process.extractOne(user_question, filtered_lines)

        if best_match and best_match[1] > 56:
            response = best_match[0]
        else:
            response = "Îmi pare rău, nu am găsit un răspuns potrivit."

      
        lines = extract_lines_with_w(file_path_txt)
        matched_lines = [
            (w_value, line)
            for w_value, line in lines
            if any(keyword in line for keyword in user_question.split() if keyword not in exclude_keywords)
        ]

        if not matched_lines:
            response = "Sorry, I didn't find a proper answer."
            return jsonify({"answer": response, "audio_url": None})

        best_match = max(matched_lines, key=lambda x: len(x[1]))
        response = best_match[1]
        w_value = best_match[0]

        translated_response = translate_text(response, lang=language)
        audio_file_path = os.path.join('static', f'{w_value}-{language}.mp3')

        if not os.path.exists(audio_file_path):  # Generăm fișierul doar dacă nu există deja
            tts = gTTS(translated_response, lang=language)
            tts.save(audio_file_path)

        return jsonify({"answer": translated_response, "audio_url": f"/{audio_file_path}"})

    except FileNotFoundError:
        response = "Fișierul data.txt nu a fost găsit."
        return jsonify({"answer": response, "audio_url": None})

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=10000)

