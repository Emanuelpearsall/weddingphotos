from flask import Flask, render_template, request, redirect
from supabase import create_client
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)

# Load Supabase credentials from .env
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
BUCKET_NAME = "wedding-uploads"

# Initialize Supabase client
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

@app.route("/", methods=["GET", "POST"])
def upload():
    if request.method == "POST":
        try:
            file = request.files.get("file")
            if not file:
                return "No file received", 400

            file_path = file.filename
            response = supabase.storage.from_(BUCKET_NAME).upload(file_path, file)

            if 'error' in response:
                return f"Upload error: {response['error']['message']}", 500

            return redirect("/gallery")
        except Exception as e:
            return f"Unexpected error: {str(e)}", 500
    return render_template("index.html")

@app.route("/gallery")
def gallery():
    try:
        files = supabase.storage.from_(BUCKET_NAME).list("")
        print("FILES:", files)

        urls = [
            supabase.storage.from_(BUCKET_NAME).get_public_url(f["name"])["publicURL"]
            for f in files if f.get("name")
        ]
        print("URLS:", urls)

        return render_template("gallery.html", urls=urls)
    except Exception as e:
        return f"Error loading gallery: {str(e)}", 500

if __name__ == "__main__":
    app.run(debug=True)
