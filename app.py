from flask import Flask, render_template, request, redirect, url_for
from supabase import create_client
from dotenv import load_dotenv
import os
import random

load_dotenv()

app = Flask(__name__)

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
BUCKET_NAME = "wedding-uploads"

# Homepage route
@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        file = request.files.get("file")
        if not file:
            return "No file received", 400

        file_path = file.filename
        res = supabase.storage.from_(BUCKET_NAME).upload(file_path, file)

        if 'error' in res:
            return f"Upload error: {res['error']['message']}", 500

        return redirect("/gallery")

    return render_template("index.html")

@app.route("/gallery", methods=["GET", "POST"])
def gallery():
    access_code = "1234"  # Replace with your actual auth logic later

    if request.method == "POST":
        code = request.form.get("code")
        if code != access_code:
            return render_template("access_denied.html")

    files = supabase.storage.from_(BUCKET_NAME).list()
    urls = [
        supabase.storage.from_(BUCKET_NAME).get_public_url(f["name"])["publicURL"]
        for f in files
    ]
    return render_template("gallery.html", urls=urls)

def generate_code():
    words = ["sunny", "smiling", "cozy", "golden", "bright", "panda", "sky", "wave", "spark"]
    return f"{random.choice(words)}-{random.choice(words)}-{random.randint(100, 999)}"

@app.route("/create", methods=["POST"])
def create_gallery():
    code = generate_code()
    return redirect(url_for("upload_with_code", code=code))

@app.route("/upload", methods=["GET", "POST"])
def upload_with_code():
    code = request.args.get("code")
    if request.method == "POST":
        file = request.files["photo"]
        if file:
            supabase.storage.from_(BUCKET_NAME).upload(f"{code}/{file.filename}", file)
            return render_template("upload.html", message="Upload successful!", code=code)
    return render_template("upload.html", code=code)

if __name__ == "__main__":
    app.run(debug=True)
