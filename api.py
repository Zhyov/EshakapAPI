from flask import Flask, jsonify, request, abort
from flask_cors import CORS
from dotenv import load_dotenv
from models import db, Word
import uuid, os, requests

load_dotenv()
app = Flask(__name__, instance_relative_config=True)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
CORS(app)
db.init_app(app)

SUPABASE_PROJECT_ID = "sblovettyyzfrvbiroiz"
SUPABASE_JWT_SECRET = os.environ.get("SUPABASE_JWT_SECRET")

def verify_token(authHeader):
    if not authHeader or not authHeader.startswith("Bearer "):
        return None
    token = authHeader.split(" ")[1]

    try:
        headers = {
            "Authorization": f"Bearer {token}",
            "apikey": SUPABASE_JWT_SECRET
        }
        response = requests.get(
            f"https://{SUPABASE_PROJECT_ID}.supabase.co/auth/v1/user",
            headers=headers
        )
        if response.status_code == 200:
            return response.json()
    except Exception:
        pass

@app.route("/")
def home():
    return jsonify({"message": "Connected to Eshakap API"})

@app.route("/names")
def get_names():
    return jsonify([word.word for word in Word.query.all()])

@app.route("/fetch")
def fetch_words():
    query = request.args.get("q", "").lower()

    words = Word.query.all()
    result = []
    if query:
        for word in words:
            if query in word.word.lower() or any(query in meaning.lower() for meaning in word.meaning):
                result.append({
                    "id": word.id,
                    "word": word.word,
                    "meaning": word.meaning,
                    "type": word.type,
                    "phonetic": word.phonetic,
                    "combination": word.combination
                })
    else:
        for word in words:
            result.append({
                "id": word.id,
                "word": word.word,
                "meaning": word.meaning,
                "type": word.type,
                "phonetic": word.phonetic,
                "combination": word.combination
            })

    return jsonify(result)

@app.route("/word")
def get_word():
    query = request.args.get("q", "").lower()

    result = []
    for word in Word.query.all():
        if query == word.word.lower():
            result.append({
                "id": word.id,
                "word": word.word,
                "meaning": word.meaning,
                "type": word.type,
                "phonetic": word.phonetic,
                "combination": word.combination
            })
    
    return jsonify(result)

@app.route("/max")
def get_all_words_count():
    return jsonify({"max": len(Word.query.all())})

@app.route("/convert")
def convert_to_script():
    query = request.args.get("q", "").lower()
    characters = list(query)
    charPath = "https://zhyov.github.io/Eshakap/assets/char/"
    consonants = ["p", "b", "f", "v", "w", "k", "g", "t", "d", "đ", "z", "ž", "h", "j", "l", "m", "n", "ň", "r", "s", "š", "c", "č", "ç"]
    vowels = ["a", "ä", "ą", "i", "į", "o", "ö"]
    eshakap = []
    final = []
    i = 0

    while i < len(characters):
        char = characters[i]
        prev = characters[i - 1] if i > 0 else None
        next = characters[i + 1] if i + 1 < len(characters) else None

        if char in vowels and (prev not in consonants):
            final.append({ "id": str(uuid.uuid4()), "path": f"{charPath}aläp.svg" })
            final.append({ "id": str(uuid.uuid4()), "path": f"{charPath}{char}.svg" })
        elif char in consonants and (next is None or next in consonants):
            final.append({ "id": str(uuid.uuid4()), "path": f"{charPath}{char}.svg" })
            final.append({ "id": str(uuid.uuid4()), "path": f"{charPath}∅.svg" })
        elif char in consonants and next in vowels:
            final.append({ "id": str(uuid.uuid4()), "path": f"{charPath}{char}.svg" })
            final.append({ "id": str(uuid.uuid4()), "path": f"{charPath}{next}.svg" })
            i += 1
        else:
            final.append({ "id": str(uuid.uuid4()), "path": f"{charPath}{char}.svg" })

        if len(final) == 2:
            eshakap.append({ "id": str(uuid.uuid4()), "syllable": final })
            final = []

        i += 1
    
    if len(final) > 0:
        eshakap.append({ "id": f"{str(uuid.uuid4())}", "syllable": final })

    return jsonify(eshakap)

@app.route("/order")
def script_order():
    order = ["a", "ä", "ą", "p", "b", "f", "v", "w", "k", "g", "t", "d", "đ", "z", "ž", "i", "į", "h", "j", "l", "m", "n", "ň", "o", "ö", "r", "s", "š", "c", "č", "ç"]

    return jsonify(order)

@app.route("/add", methods=["POST"])
def add_word():
    user = verify_token(request.headers.get("Authorization"))
    if not user:
        abort(401, "Unauthorized")

    data = request.get_json()
    word = data.get("word", "").strip()
    meaning = data.get("meaning", [])
    type = data.get("type", "")

    if not word or not isinstance(meaning, list) or not type:
        return jsonify({"error": "Invalid data"})

    newWord = Word(
        id=str(uuid.uuid4()),
        word=word,
        meaning=meaning,
        type=type
    )

    db.session.add(newWord)
    db.session.commit()

    return jsonify({"message": "Word added"})

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    
    app.run()