from fastapi import FastAPI, Query
from fastapi.responses import StreamingResponse
import yt_dlp
import tempfile
import os

app = FastAPI()

@app.get("/download-audio")
def download_audio(url: str = Query(...)):
    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp:
        tmp_path = tmp.name

    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': tmp_path,
        'quiet': True,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
        }]
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        def iterfile():
            with open(tmp_path, mode="rb") as file_like:
                yield from file_like

        return StreamingResponse(iterfile(), media_type="audio/mpeg")

    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
