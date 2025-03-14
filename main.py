#!/usr/bin/env python3

import os
import secrets
import shutil
import fastapi
from fastapi.responses import FileResponse
import httpx
import uvicorn
from pytubefix import YouTube
import demucs.separate
from pydub import AudioSegment
import tempfile
from starlette.background import BackgroundTask

app = fastapi.FastAPI()
http_client = httpx.AsyncClient()


@app.post("/extract-audio")
async def extract_audio(youtube_url: str) -> fastapi.Response:
    yt = YouTube(youtube_url)

    yt_audio = yt.streams.get_audio_only()
    if yt_audio is None:
        return fastapi.responses.JSONResponse(
            {"error": "No audio stream found"},
            status_code=400,
        )

    filename = secrets.token_hex(8)
    tmp_dir = tempfile.mkdtemp()

    yt_audio.download(output_path=tmp_dir, filename=f"{filename}.m4a")

    m4a_audio = AudioSegment.from_file(f"{tmp_dir}/{filename}.m4a")
    m4a_audio.export(f"{tmp_dir}/{filename}.mp3", format="mp3")

    model_name = "mdx_extra"
    demucs.separate.main(
        [
            "--mp3",
            "--two-stems",
            "vocals",
            "-n",
            model_name,
            "-o",
            tmp_dir,
            f"{tmp_dir}/{filename}.mp3",
            "-j",
            f"{os.cpu_count()}",
        ]
    )

    def cleanup_tmp_dir() -> None:
        shutil.rmtree(tmp_dir)

    return FileResponse(
        f"{tmp_dir}/{model_name}/{filename}/no_vocals.mp3",
        background=BackgroundTask(cleanup_tmp_dir),
    )


if __name__ == "__main__":
    uvicorn.run("main:app")
