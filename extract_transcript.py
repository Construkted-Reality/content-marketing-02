#!/usr/bin/env python3
"""
extract_transcript.py

A simple script that downloads and prints the transcript (captions) of a YouTube video
using yt-dlp. If no subtitles are available, it informs the user.

Usage:
    python extract_transcript.py <video_url> [--lang en] [--output filename.txt]

Options:
    --lang LANG   Language code of subtitles to download (default: en)
    --output FILE Write the transcript to FILE instead of printing to stdout
"""

import argparse
import sys
import os
import glob
from yt_dlp import YoutubeDL
from yt_dlp.utils import DownloadError

def parse_srt(file_path):
    """
    Reads an SRT file and returns a plain‑text transcript.
    Removes numeric indices and timestamps.
    """
    transcript_lines = []
    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            # Skip empty lines, numeric indices, and timestamps
            if not line:
                continue
            if line.isdigit():
                continue
            if "-->" in line:
                continue
            transcript_lines.append(line)
    return "\n".join(transcript_lines)

def download_subtitles(url, lang):
    """
    Uses yt-dlp to download subtitles (auto‑generated if necessary) in SRT format.
    Returns the path to the downloaded subtitle file or None if not found.
    """
    ydl_opts = {
        "skip_download": True,
        "writesubtitles": True,
        "writeautomaticsub": True,
        "subtitleslangs": [lang],
        "subtitlesformat": "srt",
        "outtmpl": "%(id)s.%(ext)s",  # simplify filename
        "quiet": True,
        "no_warnings": True,
    }

    try:
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            if not info:
                print("Failed to retrieve video information.", file=sys.stderr)
                return None
            video_id = info.get("id")
            # Force a download of the subtitles (yt-dlp handles auto‑gen)
            ydl.download([url])
    except DownloadError as e:
        print(f"Error downloading subtitles: {e}", file=sys.stderr)
        return None

    # Look for a .srt file matching the video id and language
    pattern = f"{video_id}.*.{lang}.srt"
    matches = glob.glob(pattern)
    if matches:
        return matches[0]

    # Fallback: any .srt file with the video id
    generic_pattern = f"{video_id}*.srt"
    generic_matches = glob.glob(generic_pattern)
    return generic_matches[0] if generic_matches else None

def main():
    parser = argparse.ArgumentParser(description="Download and print YouTube video transcript.")
    parser.add_argument("url", help="YouTube video URL")
    parser.add_argument("--lang", default="en", help="Subtitle language code (default: en)")
    parser.add_argument("--output", help="Write transcript to a file instead of stdout")
    args = parser.parse_args()

    subtitle_path = download_subtitles(args.url, args.lang)
    if not subtitle_path or not os.path.isfile(subtitle_path):
        print("No subtitles found for this video.", file=sys.stderr)
        sys.exit(1)

    transcript = parse_srt(subtitle_path)

    if args.output:
        try:
            with open(args.output, "w", encoding="utf-8") as out_f:
                out_f.write(transcript)
            print(f"Transcript written to {args.output}")
        except OSError as e:
            print(f"Failed to write output file: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        print(transcript)

if __name__ == "__main__":
    main()
