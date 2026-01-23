from flask import Blueprint, render_template_string

discord_bp = Blueprint('discord_bp', __name__)


@discord_bp.route('/discord')
def discord_page():
    return render_template_string('''
            <!DOCTYPE html>
            <html>
            <head>
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
                        text-decoration: none; color: #2596be; font-weight: bold;
                        box-sizing: border-box;
                        -webkit-tap-highlight-color: transparent;
                        outline: none;
                        position: relative;
                        overflow: hidden;
                    }

                    .btn-content {
                        display: block;
                        width: 100%; height: 100%;
                        line-height: 150px; 
                    }

                    .btn:active {
                        background: #222;
                        border-color: #2596be;
                    }

                    .btn img { 
                        max-width: 75%; max-height: 75%; 
                        vertical-align: middle; 
                    }
                    
                </style>
                <script>
                    function send(c) { 
                        var x = new XMLHttpRequest(); 
                        x.open("GET", "/action/" + c, true); 
                        x.send(); 
                    }

                    // Instant Toggle Function for Discord
                    function toggleBtn(id, cmd, onImg, offImg) {
                        var img = document.getElementById(id);
                        var isCurrentlyOn = (img.getAttribute('data-active') === 'true');

                        // Toggle state and image immediately
                        if (isCurrentlyOn) {
                            img.src = offImg;
                            img.setAttribute('data-active', 'false');
                        } else {
                            img.src = onImg;
                            img.setAttribute('data-active', 'true');
                        }

                        // Send command to the actions route
                        send(cmd);
                    }

                    // Pre-cache images to prevent blinking on first click
                    window.onload = function() {
                        var imgs = [
                            "/static/deafen.png", "/static/undeafen.png",
                            "/static/muted_mic.png", "/static/unmuted_mic.png",
                            "/static/start_stream.png", "/static/stop_stream.png"
                        ];
                        for (var i = 0; i < imgs.length; i++) {
                            (new Image()).src = imgs[i];
                        }
                    };
                </script>
            </head>
            <body>

                <div class="grid-container">
                
                    <a href="/" class="btn">
                        <span class="btn-content" style="color:#2596be; font-size:18px; font-weight:bold;">BACK</span>
                    </a>
                    
                    <div class="btn" onclick="toggleBtn('mic-img', 'mic_mute', '/static/unmuted_mic.png', '/static/muted_mic.png')">
                        <span class="btn-content">
                            <img id="mic-img" src="/static/unmuted_mic.png" data-active="true">
                        </span>
                    </div>

                    <div class="btn" onclick="toggleBtn('deaf-img', 'mic_deafen', '/static/undeafen.png', '/static/deafen.png')">
                        <span class="btn-content">
                            <img id="deaf-img" src="/static/undeafen.png" data-active="true">
                        </span>
                    </div>

                    <div class="btn" onclick="toggleBtn('stream-img', 'stream', '/static/stop_stream.png', '/static/start_stream.png')">
                        <span class="btn-content">
                            <img id="stream-img" src="/static/start_stream.png" data-active="false">
                        </span>
                    </div>

                    
                    <div class="btn"></div>
                    <div class="btn"></div>
                    <div class="btn"></div>
                    <button class="btn" onclick="send('end_call')"><img src="/static/end_call.png"></button>
                </div>
            </body>
            </html>
        ''')