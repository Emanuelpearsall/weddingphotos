from flask import Flask, render_template, request, redirect
from supabase import create_client
from dotenv import load_dotenv
import os, random, sys

# Load environment
load_dotenv()
app = Flask(__name__)

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
BUCKET_NAME   = "wedding-uploads"

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)


def generate_code():
    words = ["sunny","smiling","cozy","golden","bright","panda","sky","wave","spark"]
    return f"{random.choice(words)}-{random.choice(words)}-{random.randint(100,999)}"


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        # Join existing
        code = request.form.get("code")
        if not code:
            return "Please enter a gallery code", 400
        return redirect(f"/upload?code={code}")
    return render_template("index.html")


@app.route("/create", methods=["POST"])
def create_gallery():
    # Create new
    code = generate_code()
    return redirect(f"/upload?code={code}")


@app.route("/upload", methods=["GET", "POST"])
def upload():
    code = request.args.get("code")
    if not code:
        return redirect("/")   # no code → back to index

    if request.method == "POST":
        file = request.files.get("file")
        if not file or file.filename == "":
            return "No file selected", 400

        try:
            data = file.read()
            res  = supabase.storage.from_(BUCKET_NAME).upload(f"{code}/{file.filename}", data)
            if res.get("error"):
                return f"Upload error: {res['error']['message']}", 500
            # Stay on the same upload page so they can add more
            return redirect(f"/upload?code={code}")
        except Exception as e:
            print("[upload error]", e, file=sys.stderr)
            return f"Unexpected upload error: {e}", 500

    # GET → show the upload form for this gallery code
    return render_template("upload.html", code=code)


@app.route("/gallery", methods=["GET"])
def gallery():
    try:
        files = supabase.storage.from_(BUCKET_NAME).list("")
        urls = []
        for f in files:
            name = f.get("name")
            if not name:
                continue
            pub = supabase.storage.from_(BUCKET_NAME).get_public_url(name)
            url = pub.get("publicURL") or pub.get("url")
            urls.append(url)
        return render_template("gallery.html", urls=urls)
    except Exception as e:
        print("[gallery error]", e, file=sys.stderr)
        return f"Error loading gallery: {e}", 500


if __name__ == "__main__":
    app.run(debug=True)
