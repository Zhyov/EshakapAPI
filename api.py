from flask import Flask, jsonify, request
from flask_cors import CORS
import uuid
import json

app = Flask(__name__)
CORS(app)

def load_words():
    try:
        with open("words.json", "r", encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        return []

@app.route("/")
def home():
    return jsonify({"message": "Connected to Eshakap API"})

@app.route("/get")
def search_words():
    query = request.args.get("q", "").lower()

    results = []
    if query:
        for word in load_words():
            if query in word["word"].lower() or any(query in meaning.lower() for meaning in word["meaning"]):
                word["id"] = str(uuid.uuid4())
                results.append(word)
    else:
        words = load_words()
        for word in words:
            word["id"] = str(uuid.uuid4())
            results.append(word)

    return jsonify(results)

@app.route("/max")
def get_all_words_count():
    words = load_words()
    return jsonify({"max": len(words)})

@app.route("/convert")
def convert_to_script():
    query = request.args.get("q", "").lower()
    chararacters = list(query)
    charPath = "https://zhyov.github.io/Eshakap/assets/char/"
    consonants = ["p", "b", "f", "v", "w", "k", "g", "t", "d", "đ", "z", "ž", "h", "j", "l", "m", "n", "ň", "r", "s", "š", "c", "č", "ç"]
    vowels = ["a", "ä", "ą", "i", "į", "o", "ö"]
    eshakap = []
    final = []
    count = 0
    skip = False

    for index, char in enumerate(chararacters):
        if not skip:
            prev = chararacters[index - 1]
            try:
                next = chararacters[index + 1]
            except IndexError:
                next = None

            if char in vowels and prev not in consonants:
                final.append({ "id": f"{str(uuid.uuid4())}", "path": f"{charPath}aläp.svg" })
                final.append({ "id": f"{str(uuid.uuid4())}", "path": f"{charPath}{char}.svg" })
                count += 2
            elif char in consonants and (not next or next in consonants):
                final.append({ "id": f"{str(uuid.uuid4())}", "path": f"{charPath}{char}.svg" })
                final.append({ "id": f"{str(uuid.uuid4())}", "path": f"{charPath}∅.svg" })
                count += 2
            elif char in consonants and next in vowels:
                final.append({ "id": f"{str(uuid.uuid4())}", "path": f"{charPath}{char}.svg" })
                final.append({ "id": f"{str(uuid.uuid4())}", "path": f"{charPath}{next}.svg" })
                count += 2
                skip = True
            else:
                final.append({ "id": f"{str(uuid.uuid4())}", "path": f"{charPath}{char}.svg" })
                count += 2

            if len(final) == 2:
                eshakap.append({ "id": f"{str(uuid.uuid4())}", "syllable": final })
                final = []
        else:
            skip = not skip
    
    if len(final) > 0:
        eshakap.append({ "id": f"{str(uuid.uuid4())}", "syllable": final })

    return eshakap

if __name__ == "__main__":
    app.run()