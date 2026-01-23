import asyncio

from flask import Blueprint, render_template_string
from services.adb_manager import homepage_restart
from services.spotify_info import control_spotify
import keyboard

actions_bp = Blueprint('actions', __name__)

TARGET_URL = "http://192.168.42.138:8000"


@actions_bp.route('/')
def index():
    return render_template_string('''
            <!DOCTYPE html>
            <html>
            <head>
            
                <meta name="mobile-web-app-capable" content="yes">
                <meta name="apple-mobile-web-app-capable" content="yes">
                
                <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
                <style>
                    body { 
                        background: #000; color: #fff; font-family: Arial, sans-serif; 
                        margin: 0; padding: 10px; text-align: center;
                    }

                    
                    .grid-container {
                        width: 660px;
                        margin: 0 auto;
                        margin-left: -20px;
                        font-size: 0;
                    }

                    .btn { 
                        display: inline-block;
                        width: 150px; height: 150px;
                        margin: 5px;
                        background: #111; border: 2px solid #333; 
                        border-radius: 12px; 
                        vertical-align: top;
                        cursor: pointer;
                        text-decoration: none; color: #0f0; font-weight: bold;
                        box-sizing: border-box;
                        -webkit-tap-highlight-color: transparent;
                        outline: none;
                        position: relative;
                        overflow: hidden;
                    }

                    /* Helper to center text/images in old browsers */
                    .btn-content {
                        display: block;
                        width: 100%;
                        height: 100%;
                        line-height: 150px; /* Vertically centers single line text */
                        font-size: 18px;    /* Restore font size */
                    }

                    .btn:active {
                        background: #222;
                        border-color: #555;
                    }

                    .btn img { 
                        max-width: 80%; 
                        max-height: 80%; 
                        vertical-align: middle;
                    }

                </style>
                <script>
                    function send(c) { 
                        var x = new XMLHttpRequest(); 
                        x.open("GET", "/action/" + c, true); 
                        x.send(); 
                    }
                </script>
            </head>
            <body>
                <div class="grid-container">
                    <div class="btn" onclick="send('restart')">
                        <span class="btn-content">RESET</span>
                    </div>
                    
                    <a href="/" class="btn"><span class="btn-content"></span></a>
                    
                    <a href="/output" class="btn">
                    <span class="btn-content"><img src="/static/output.png"></span>
                    </a>
                    
                    <a href="/volumes" class="btn">
                        <span class="btn-content"><img src="/static/mixer.png"></span>
                    </a>
                    
                    <a href="/discord" class="btn">
                        <span class="btn-content"><img src="/static/discord.png"></span>
                    </a>
                    
                    <a href="/" class="btn"><span class="btn-content"></span></a>
                    
                    <a href="/" class="btn"><span class="btn-content"></span></a>
                    
                    <a href="/spotify" class="btn">
                        <span class="btn-content"><img src="/static/spotify.png"></span>
                    </a>
                </div>
            </body>
            </html>
        ''')


@actions_bp.route('/action/<cmd>')
def perform_action(cmd):

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    if cmd == "next_track":
        loop.run_until_complete(control_spotify("next"))
    elif cmd == "previous_track":
        loop.run_until_complete(control_spotify("previous"))
    elif cmd == "play":
        loop.run_until_complete(control_spotify("play_pause"))
    elif cmd == "mic_mute":
        keyboard.press_and_release('ctrl+shift+alt+m')
    elif cmd == "mic_deafen":
        keyboard.press_and_release('ctrl+shift+alt+k')
    elif cmd == "stream":
        keyboard.press_and_release('ctrl+shift+alt+s')
    elif cmd == "end_call":
        keyboard.press_and_release('ctrl+shift+alt+å')
    elif cmd == "restart":
        homepage_restart()
    return "OK", 200
