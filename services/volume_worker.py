import time
import pythoncom
import subprocess
import win32gui
import win32process
import psutil
from pycaw.pycaw import AudioUtilities
import asyncio
import os
import sys


from services.spotify_info import get_spotify_info

# Global storage for the app
cached_volumes = {}

spotify_cache = {"title": "Nothing", "Artist": "Bomboglad", "progress": 0}

ICON_MAP = {
    "Spotify": "spotify.png",
    "Firefox": "firefox.png",
    "Discord": "discord.png"
}


def get_focused_process_name():
    try:
        hwnd = win32gui.GetForegroundWindow()
        _, pid = win32process.GetWindowThreadProcessId(hwnd)
        process = psutil.Process(pid)
        return process.name().split('.')[0].capitalize()
    except Exception as e:
        return f"Error: {e}"


def volume_worker():
    # FIX: Initialize for multi-threaded COM
    pythoncom.CoInitializeEx(pythoncom.COINIT_MULTITHREADED)
    global cached_volumes, spotify_cache
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    while True:
        try:
            # 1. Volume Logic
            current_app = get_focused_process_name()
            display_vols = {"Focused": {"name": current_app, "level": 0, "icon": "terminal.png"}}
            for app_name in ICON_MAP:
                display_vols[app_name] = {"name": app_name, "level": 0, "icon": ICON_MAP[app_name]}

            sessions = AudioUtilities.GetAllSessions()
            for session in sessions:
                if session.Process:
                    try:
                        proc_name = session.Process.name().split('.')[0].capitalize()
                        level = int(session.SimpleAudioVolume.GetMasterVolume() * 100)
                        if proc_name == current_app:
                            display_vols["Focused"]["level"] = level
                        if proc_name in display_vols:
                            display_vols[proc_name]["level"] = level
                    except Exception as e:
                        print(f"Volumes update error{e}")
            cached_volumes = display_vols

        except Exception as e:
            print(f"Worker Error: {e}")

        time.sleep(0.1)


def spotify_worker():
    pythoncom.CoInitializeEx(pythoncom.COINIT_MULTITHREADED)
    global spotify_cache
    loop = asyncio.new_event_loop()

    while True:
        try:
            data = loop.run_until_complete(get_spotify_info())
            if data:
                spotify_cache = data
                # print(spotify_cache.get("progress"))
        except Exception as e:
            print(f"Spotify Update Error: {e}")

        time.sleep(0.5)


def get_resource_path(relative_path):
    """ Get absolute path to resource """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


def set_audio_playback_device(name):
    nircmd = get_resource_path("nircmd.exe")
    try:
        subprocess.run([nircmd, 'setdefaultsounddevice', name, '1'], check=True)
        return "Success"
    except Exception as e:
        return "Failed"
