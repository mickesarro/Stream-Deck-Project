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
    pythoncom.CoInitializeEx(pythoncom.COINIT_MULTITHREADED)
    global cached_volumes

    active_sessions = []
    last_session_refresh = 0

    while True:
        try:
            now = time.time()

            # Only scan for new apps every 2 seconds
            if now - last_session_refresh > 2.0:
                new_sessions = []
                for s in AudioUtilities.GetAllSessions():
                    if s.Process:
                        try:
                            # Cache the name for better performance
                            s._cached_name = s.Process.name().split('.')[0].capitalize()
                            new_sessions.append(s)
                        except:
                            continue
                active_sessions = new_sessions
                last_session_refresh = now

            # Get focused app
            current_app = get_focused_process_name()

            # Build the dict with the new info
            vols = {"Focused": {"name": current_app, "level": 0, "icon": "terminal.png"}}
            for app_name in ICON_MAP:
                vols[app_name] = {"name": app_name, "level": 0, "icon": ICON_MAP[app_name]}

            # Update volume from cached list
            for session in active_sessions:
                try:
                    level = int(session.SimpleAudioVolume.GetMasterVolume() * 100)
                    proc_name = session._cached_name

                    if proc_name == current_app:
                        vols["Focused"]["level"] = level
                    if proc_name in vols:
                        vols[proc_name]["level"] = level
                except Exception:
                    continue

            cached_volumes = vols

        except Exception as e:
            print(f"Worker Error: {e}")

        # Update frequently when there's new volume data
        time.sleep(0.1)


def spotify_worker():
    pythoncom.CoInitializeEx(pythoncom.COINIT_MULTITHREADED)
    global spotify_cache
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    while True:
        try:
            data = loop.run_until_complete(get_spotify_info())
            if data:
                spotify_cache = data
                is_playing = data.get("is_playing", False)
                wait_time = 1.0 if is_playing else 5.0
        except Exception as e:
            print(f"Spotify Update Error: {e}")

        time.sleep(wait_time)


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
