#!/usr/bin/env python3

import os
import secrets
import shutil
import httpx
from pytubefix import YouTube
import demucs.separate
from pydub import AudioSegment
import tempfile
import tkinter.ttk as ttk

http_client = httpx.AsyncClient()


async def extract_audio(youtube_url: str):
    yt = YouTube(youtube_url)

    yt_audio = yt.streams.get_audio_only()
    if yt_audio is None:
        print("Error")
        return None

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

    # TODO save/dispal yfile

    return None


def main() -> int:
    style = ttk.Style()
    style.configure("BW.TLabel", foreground="black", background="white")

    # textbox to input url and button to execute
    textbox = ttk.Entry()
    textbox.pack()

    button = ttk.Button(text="Download")
    button.pack()

    # progress bar
    progress = ttk.Progressbar(orient="horizontal", length=200, mode="determinate")
    progress.pack()

    # label to display status
    label = ttk.Label(text="Status", style="BW.TLabel")
    label.pack()

    # label to display download path
    download_path = ttk.Label(text="Download Path", style="BW.TLabel")
    download_path.pack()

    return 0


if __name__ == "__main__":
    exit(main())
