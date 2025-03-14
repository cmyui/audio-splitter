#!/usr/bin/env python3

import os
import secrets
import shutil
import sys
from typing import Sequence
from pytubefix import YouTube
import demucs.separate
from pydub import AudioSegment
import tempfile


def extract_audio(youtube_url: str):
    yt = YouTube(youtube_url)

    yt_audio = yt.streams.get_audio_only()
    if yt_audio is None:
        raise ValueError("No youtube audio stream found")

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

    DESKTOP_FOLDER = os.path.join(os.path.expanduser("~"), "Desktop")
    shutil.move(f"{tmp_dir}/{model_name}/{filename}/no_vocals.mp3", DESKTOP_FOLDER)

    shutil.rmtree(tmp_dir)

    print("File saved to Desktop/no_vocals.mp3")

    return None


def main(argv: Sequence[str] | None = None) -> int:
    if argv is None:
        argv = sys.argv[1:]

    if len(argv) != 1:
        print("Usage: main.py <youtube_url>")
        return 1

    youtube_url = argv[0]

    extract_audio(youtube_url)

    # label to display error
    return 0


if __name__ == "__main__":
    exit(main(sys.argv[1:]))
