from flask import Blueprint, jsonify, render_template_string
from services import audio_manager

mixer_bp = Blueprint('mixer', __name__)

@mixer_bp.route('/get_volumes_data')
def volumes_api():
    return jsonify(audio_manager.cached_volumes)

@mixer_bp.route('/volumes')
def volumes_page():
    return render_template_string('''
            <!DOCTYPE html>
            <html>
            <head>
                <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
                <style>
                    body { 
                        background: #121826; color: #ffffff; font-family: Arial, sans-serif; 
                        margin: 0; padding: 10px; text-align: center;
                    }
                    .back-btn { 
                        display: block; color: #666; text-decoration: none; 
                        font-size: 14px; text-align: left; margin-bottom: 0px; 
                    }
                    #mixer { width: 100%; overflow: hidden; height: 350px; }
                    .channel { float: left; width: 25%; height: 100%; position: relative; }

                    .app-icon { 
                        width: 60px; height: 60px; 
                        margin: 0 auto 0px auto; 
                        display: block;
                        object-fit: contain;
                    }

                    .track-outer { position: relative; height: 240px; width: 100%; }
                    .track-line {
                        position: absolute; left: 50%; margin-left: -15px; 
                        width: 30px; height: 200px; background: #2c3440; border-radius: 2px;
                        margin-top: 12px;
                    }
                    .thumb {
                        position: absolute; left: 50%; margin-left: -20px; 
                        width: 40px; height: 40px; background: #3898ff;
                        border-radius: 10px; transition: bottom 0.1s linear;
                    }
                    .vol-box {
                        margin-top: -10px; padding: 5px 0; background: #1a212e;
                        border: 1px solid #333; border-radius: 4px; color: #3898ff;
                        font-weight: bold; font-size: 22px; width: 80%; margin-left: 10%;
                    }
                    .vol-link {
                        text-decoration: none;
                        display: block;
                        height: 100%;
                        -webkit-tap-highlight-color: transparent;
                    }
                </style>
                <script>
                    function update() {
                        var x = new XMLHttpRequest();
                        x.open("GET", "/get_volumes_data", true);
                        x.onreadystatechange = function() {
                            if (x.readyState == 4 && x.status == 200) {
                                var data = JSON.parse(x.responseText);
                                var container = document.getElementById('mixer');

                                for (var key in data) {
                                    var app = data[key];
                                    var safeKey = key.replace(/[^a-z0-9]/gi, '_'); // Unique ID for each app
                                    var channelDiv = document.getElementById('channel-' + safeKey);

                                    // If the channel doesn't exist yet, create it once
                                    if (!channelDiv) {
                                        var iconFile = app.icon ? app.icon : "terminal.png";
                                        
                                        // Define custom links based on the app key
                                        var linkUrl = "#"; // Default to no-op
                                        if (key === "Spotify") linkUrl = "/spotify";
                                        if (key === "Discord") linkUrl = "/discord";
                                        if (key === "Focused") linkUrl = "/output";
                
                                        // Wrap content in a link if it's Spotify or Discord, otherwise use a div
                                        var isLinked = (key === "Spotify" || key === "Discord" || key === "Focused");
                                        var wrapperOpen = isLinked ? '<a href="' + linkUrl + '" class="vol-link">' : '<div>';
                                        var wrapperClose = isLinked ? '</a>' : '</div>';
                                        
                                        var html = '<div class="channel" id="channel-' + safeKey + '">' + wrapperOpen + 
                                                        '<img src="/static/' + iconFile + '" class="app-icon">' +
                                                        '<div class="track-outer">' +
                                                            '<div class="track-line">' +
                                                                '<div class="thumb" id="thumb-' + safeKey + '"></div>' +
                                                            '</div>' +
                                                        '</div>' +
                                                        '<div class="vol-box" id="text-' + safeKey + '">0</div>' + 
                                                        wrapperClose + 
                                                   '</div>';
                                        container.insertAdjacentHTML('beforeend', html);
                                        channelDiv = document.getElementById('channel-' + safeKey);
                                    }

                                    // Now only update the properties that change
                                    var level = app.level;
                                    var visualBottom = ((level / 100) * 160 / 200) * 100;

                                    document.getElementById('thumb-' + safeKey).style.bottom = visualBottom + '%';
                                    document.getElementById('text-' + safeKey).innerText = level;
                                }
                            }
                        };
                        x.send();
                    }
                    setInterval(update, 150);
                </script>
            </head>
            <body>
                <a href="/" class="back-btn">&larr; BACK</a>
                <div id="mixer"></div>
            </body>
            </html>
        ''')