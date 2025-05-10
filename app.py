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
        return redirect("/")   # no code → back home

    if request.method == "POST":
        file = request.files.get("file")
        if not file or file.filename == "":
            return "No file selected", 400

        try:
            data = file.read()
            res  = supabase.storage.from_(BUCKET_NAME).upload(f"{code}/{file.filename}", data)
            if getattr(res, "error", None):
                return f"Upload error: {res.error}", 500

            # ←── Here: after a successful upload, redirect to the code-specific gallery
            return redirect(f"/gallery?code={code}")

        except Exception as e:
            return f"Unexpected upload error: {e}", 500

    # GET → render the upload form, passing the code
    return render_template("upload.html", code=code)



@app.route("/gallery", methods=["GET", "POST"])
def gallery():
    # Require a code parameter
    code = request.args.get("code")
    if not code:
        return redirect("/")  # no code, go back home

    try:
        # List only files in the folder named after the code
        files = supabase.storage.from_(BUCKET_NAME).list(code)  
        # e.g. ["sunny-day-123/image1.jpg", ...]

        urls = []
        for f in files:
            name = f.get("name")
            if not name:
                continue
            # Build the public URL
            pub = supabase.storage.from_(BUCKET_NAME).get_public_url(name)
            url = pub.get("publicURL") or pub.get("url")
            urls.append(url)

        return render_template("gallery.html", urls=urls, code=code)

    except Exception as e:
        return f"Error loading gallery for '{code}': {e}", 500




if __name__ == "__main__":
    app.run(debug=True)


