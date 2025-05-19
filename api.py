from flask import Flask, jsonify, request
from flask_cors import CORS
import uuid
import json

app = Flask(__name__)
CORS(app)

def load_words():
    try:
        with open('words.json', 'r', encoding='utf-8') as file:
            return json.load(file)
    except FileNotFoundError:
        return []

@app.route('/')
def home():
    return jsonify({"message": "Connected to Eshakap API"})

@app.route('/get')
def search_words():
    query = request.args.get('q', '').lower()

    results = []
    if query:
        for word in load_words():
            if query in word['word'].lower() or any(query in meaning.lower() for meaning in word['meaning']):
                word["id"] = str(uuid.uuid4())
                results.append(word)
    else:
        words = load_words()
        for word in words:
            word["id"] = str(uuid.uuid4())
            results.append(word)

    return jsonify(results)

if __name__ == '__main__':
    app.run()