from fastapi import FastAPI, Query, HTTPException
from fastapi.responses import StreamingResponse, JSONResponse
import yt_dlp
import tempfile
import os

app = FastAPI()

@app.get("/download-audio")
def download_audio(url: str = Query(...)):
    tmp_path = None

    try:
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

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        if os.path.getsize(tmp_path) < 5000:  # safeguard
            raise Exception("Downloaded file too small — possibly failed silently.")

        def iterfile():
            with open(tmp_path, mode="rb") as file_like:
                yield from file_like

        return StreamingResponse(iterfile(), media_type="audio/mpeg")

    except Exception as e:
        return JSONResponse(status_code=500, content={"detail": f"Download failed: {str(e)}"})

    finally:
        if tmp_path and os.path.exists(tmp_path):
            os.remove(tmp_path)
