from flask import Flask, render_template, request, redirect, url_for
from supabase import create_client
from dotenv import load_dotenv
import os
import random

load_dotenv()

app = Flask(__name__)

# Load environment variables
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
BUCKET_NAME = "wedding-uploads"

# Initialize Supabase
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Homepage Upload Route
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        file = request.files.get("file")
        if not file:
            return "No file uploaded", 400

        try:
            file_path = file.filename
            supabase.storage.from_(BUCKET_NAME).upload(file_path, file)
            return redirect("/gallery")
        except Exception as e:
            return f"Internal upload error: {e}", 500

    return render_template("index.html")

# Gallery route
@app.route("/gallery", methods=["GET"])
def gallery():
    try:
        files = supabase.storage.from_(BUCKET_NAME).list()
        urls = [
            supabase.storage.from_(BUCKET_NAME).get_public_url(f["name"])["publicURL"]
            for f in files
        ]
        return render_template("gallery.html", urls=urls)
    except Exception as e:
        return f"Error loading gallery: {e}", 500

# Run the app
if __name__ == "__main__":
    app.run(debug=True)
