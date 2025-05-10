from flask import Flask, render_template, request, redirect
from supabase import create_client
from dotenv import load_dotenv
import os, sys

# Load .env (locally) or real env vars (on Render)
load_dotenv()

app = Flask(__name__)
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
BUCKET_NAME   = "wedding-uploads"

# initialize client
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        if "file" not in request.files:
            return "No file part in request", 400
        file = request.files["file"]
        if file.filename == "":
            return "No file selected", 400

        try:
            data = file.read()
            res  = supabase.storage.from_(BUCKET_NAME).upload(file.filename, data)
            if res.get("error"):
                return f"Upload error: {res['error']['message']}", 500
            return redirect("/gallery")
        except Exception as e:
            print(f"[upload error] {e}", file=sys.stderr)
            return f"Internal upload error: {e}", 500

    # GET
    return render_template("index.html")


@app.route("/gallery")
def gallery():
    try:
        # list everything at bucket root
        files = supabase.storage.from_(BUCKET_NAME).list("")  
        print("FILES:", files, file=sys.stderr)

        urls = []
        for f in files:
            name = f.get("name")
            if not name: 
                continue
            pub   = supabase.storage.from_(BUCKET_NAME).get_public_url(name)
            url   = pub.get("publicURL") or pub.get("url")
            urls.append(url)
        return render_template("gallery.html", urls=urls)

    except Exception as e:
        print(f"[gallery error] {e}", file=sys.stderr)
        return f"Error loading gallery: {e}", 500


if __name__ == "__main__":
    app.run(debug=True)
