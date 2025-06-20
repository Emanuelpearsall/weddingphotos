from flask import Flask, render_template, request, redirect, url_for, session
from supabase import create_client
from dotenv import load_dotenv
import os, random, sys

# Load environment variables
load_dotenv()
app = Flask(__name__)

# Session secret (override via ENV in production)
app.secret_key = os.getenv("SECRET_KEY", "supersecret123")

# Supabase configuration
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
BUCKET_NAME   = "wedding-uploads"
supabase      = create_client(SUPABASE_URL, SUPABASE_KEY)

def generate_code():
    words = ["sunny","smiling","cozy","golden","bright","panda","sky","wave","spark"]
    return f"{random.choice(words)}-{random.choice(words)}-{random.randint(100,999)}"

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        code = request.form.get("code")
        if not code:
            return "Please enter a gallery code", 400
        session["my_code"] = code
        return redirect(url_for("upload", code=code))
    return render_template("index.html")

@app.route("/create", methods=["POST"])
def create_gallery():
    code = generate_code()
    session["my_code"] = code
    return redirect(url_for("upload", code=code))

@app.route("/upload", methods=["GET", "POST"])
def upload():
    code = request.args.get("code")
    if not code:
        return redirect(url_for("index"))
    session["my_code"] = code

    if request.method == "POST":
        file = request.files.get("file")
        if not file or file.filename == "":
            return "No file selected", 400
        try:
            data = file.read()
            res  = supabase.storage.from_(BUCKET_NAME).upload(f"{code}/{file.filename}", data)
            if getattr(res, "error", None):
                return f"Upload error: {res.error}", 500
            return redirect(url_for("gallery", code=code))
        except Exception as e:
            print("[upload error]", e, file=sys.stderr)
            return f"Unexpected upload error: {e}", 500

    return render_template("upload.html", code=code)

@app.route("/gallery", methods=["GET"])
def gallery():
    code = request.args.get("code")
    if not code:
        return redirect(url_for("index"))
    try:
        files = supabase.storage.from_(BUCKET_NAME).list(code)
        urls = []
        for f in files:
            path = f.get("name")            # full path: "code/filename.ext"
            if not path:
                continue
            res  = supabase.storage.from_(BUCKET_NAME).get_public_url(path)
            data = res.get("data", {})      # Supabase v2 shape
            url  = data.get("publicUrl") or data.get("publicURL")
            if url:
                urls.append(url)
        return render_template("gallery.html", urls=urls, code=code)
    except Exception as e:
        print("[gallery error]", e, file=sys.stderr)
        return f"Error loading gallery: {e}", 500

@app.route("/my-gallery")
def my_gallery():
    code = session.get("my_code")
    if not code:
        return redirect(url_for("index"))
    return redirect(url_for("gallery", code=code))

if __name__ == "__main__":
    app.run(debug=True)
