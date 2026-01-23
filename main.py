import threading
import logging
import time
import os
from pystray import Icon, Menu, MenuItem
from PIL import Image

from flask import Flask
from dotenv import load_dotenv

from services import adb_manager
from services.adb_manager import auto_tether
from services.volume_worker import volume_worker, get_resource_path
from services.volume_worker import spotify_worker
from blueprints.mixer import mixer_bp
from blueprints.actions import actions_bp
from blueprints.spotify import spotify_bp
from blueprints.discord import discord_bp
from blueprints.audio_output import audio_output_bp

# Setup dotenv for credentials
load_dotenv()

app = Flask(__name__)
PC_IP = os.getenv('PC_IP')
port = int(os.getenv('PORT', 8000))

# Hide logs
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

# Register Modules
app.register_blueprint(mixer_bp)
app.register_blueprint(actions_bp)
app.register_blueprint(spotify_bp)
app.register_blueprint(discord_bp)
app.register_blueprint(audio_output_bp)


# --- SYSTEM TRAY FUNCTIONS ---


def quit_app(icon, item):
    """Gracefully shuts down the tray and the Flask process"""
    print("Shutting down MixerApp...")
    icon.stop()
    os._exit(0)


def setup_tray():
    """Initializes the System Tray Icon"""
    try:
        # Load the icon from your static folder inside the EXE
        icon_img = Image.open(get_resource_path("static/mixer.png"))

        menu = Menu(
            MenuItem('Restart Homepage', lambda: adb_manager.homepage_restart()),
            Menu.SEPARATOR,
            MenuItem('Quit Mixer App', quit_app)
        )

        icon = Icon("MixerApp", icon_img, "MixerApp", menu)
        icon.run()
    except Exception as e:
        print(f"Tray Icon Error: {e}")


if __name__ == '__main__':
    # Start Audio Monitor in background
    threading.Thread(target=volume_worker, daemon=True).start()
    # Spotify monitor
    threading.Thread(target=spotify_worker, daemon=True).start()
    # App tray icon
    threading.Thread(target=setup_tray, daemon=True).start()

    # Main Connection Loop
    while True:
        if auto_tether():
            print("Starting Flask Server...")
            time.sleep(1)

            try:
                # This blocks until the connection is lost or app is stopped
                app.run(host=PC_IP, port=port, debug=False, threaded=True)
            except Exception as e:
                print(f"Server Stopped: {e}")

        time.sleep(5)
