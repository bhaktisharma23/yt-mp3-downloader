from flask import Flask, render_template, request, send_from_directory
import yt_dlp
import os
import uuid
import shutil

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DOWNLOAD_FOLDER = os.path.join(BASE_DIR, "downloads")
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)


@app.route("/", methods=["GET", "POST"])
def index():
    files = []

    if request.method == "POST":
        links = request.form["links"].splitlines()

        # Unique session folder (prevents clash)
        session_id = str(uuid.uuid4())
        session_folder = os.path.join(DOWNLOAD_FOLDER, session_id)
        os.makedirs(session_folder, exist_ok=True)

        ydl_opts = {
            "format": "bestaudio/best",
            "outtmpl": os.path.join(session_folder, "%(title).80s_%(id)s.%(ext)s"),
            "ignoreerrors": True,
            "postprocessors": [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }],
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download(links)

        files = [f"{session_id}/{f}" for f in os.listdir(session_folder)]

    return render_template("index.html", files=files)


@app.route("/download/<path:filename>")
def download_file(filename):
    directory = os.path.join(DOWNLOAD_FOLDER, os.path.dirname(filename))
    file = os.path.basename(filename)

    return send_from_directory(
        directory,
        file,
        as_attachment=True,
        download_name=file
    )

if __name__ == "__main__":
    app.run()


