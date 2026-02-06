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
from services.audio_manager import volume_worker, get_resource_path
from services.audio_manager import spotify_worker
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


def quit_app(icon):
    print("Shutting down MixerApp...")
    icon.stop()
    os._exit(0)


def setup_tray():
    try:
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
    threading.Thread(target=volume_worker, daemon=True).start()
    threading.Thread(target=spotify_worker, daemon=True).start()
    threading.Thread(target=setup_tray, daemon=True).start()

    while True:
        if auto_tether():
            print("Starting Flask Server...")
            time.sleep(1)

            try:
                app.run(host=PC_IP, port=port, debug=False, threaded=True)
            except Exception as e:
                print(f"Server Stopped: {e}")

        time.sleep(5)
