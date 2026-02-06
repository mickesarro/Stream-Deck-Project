from flask import Blueprint, jsonify, render_template_string
from services import audio_manager

spotify_bp = Blueprint('spotify', __name__)


@spotify_bp.route('/get_spotify_data')
def spotify_api():
    return jsonify(audio_manager.spotify_cache)


@spotify_bp.route('/spotify')
def spotify_page():
    return render_template_string('''
            <!DOCTYPE html>
            <html>
            <head>
                <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
                <style>
                    body { 
                        background: #000; color: #fff; font-family: Arial, sans-serif; 
                        margin: 0; padding: 0; overflow: hidden; 
                        display: flex; flex-direction: column; height: 100vh;
                    }

                    .home-link { position: absolute; top: 15px; left: 15px; z-index: 10; }
                    .home-link img { height: 80px; width: 80px; }

                    .main-container { 
                        display: flex; 
                        align-items: center; 
                        justify-content: center; 
                        width: 100%; 
                        height: 100%;
                    }

                    .spotify-content { 
                        flex: 1; 
                        display: flex; 
                        flex-direction: column; 
                        align-items: center; 
                        text-align: center;
                    }

                    #album-art { 
                        width: 160px; height: 160px; border-radius: 12px; 
                        border: 2px solid #1DB954; object-fit: cover; 
                        box-shadow: 0px 0px 15px rgba(29, 185, 84, 0.3);
                    }

                    #song-title { 
                        font-size: 1.0em; font-weight: bold; margin-top: 10px; 
                        width: 80%; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; 
                    }
                    #song-artist { font-size: 1.1em; color: #1DB954; margin-top: 4px; }

                    .progress-container {
                        width: 70%; height: 6px; background: #333;
                        border-radius: 10px; margin: 5px 0 8px 0; overflow: hidden;
                    }
                    #progress-bar { width: 0%; height: 100%; background: #50A36B; transition: width 0.4s linear; }
                    #time-display { font-size: 0.9em; color: #aaa; font-variant-numeric: tabular-nums; }

                    .media-controls { 
                        display: flex; justify-content: space-between; 
                        width: 350px; 
                    }
                    .icon-btn { 
                        outline: none; -webkit-tap-highlight-color: transparent; 
                        background: none; border: none; width: 70px; cursor: pointer; 
                        padding: 0; transition: transform 0.2s; 
                    }
                    .icon-btn:active { transform: scale(0.8); opacity: 0.7; }
                    .icon-btn img { width: 100%; }

                    .volume-section { 
                        width: 110px;
                        padding-right: 30px; 
                        display: flex; 
                        flex-direction: column; 
                        align-items: center; 
                        justify-content: center;
                    }

                    .vol-link { text-decoration: none; display: block; height: 100%; -webkit-tap-highlight-color: transparent; }

                    .track-outer { position: relative; height:300px; width: 100%; }
                    .track-line {
                        position: absolute; left: 50%; margin-left: -15px; 
                        width: 30px; height: 260px; background: #2c3440; border-radius: 2px;
                        margin-top: 12px;
                    }
                    
                    .thumb {
                        position: absolute; left: 50%; margin-left: -20px;
                        width: 40px; height: 40px; background: #50A36B;
                        border-radius: 10px; transition: bottom 0.1s linear;
                    }
                    .vol-box {
                        margin-top: 0px; padding: 8px 0; background: #1a212e;
                        border: 1px solid #333; border-radius: 6px; color: #50A36B;
                        font-weight: bold; font-size: 22px; width: 80px; text-align: center;
                    }
                </style>
                <script>
                    var isOptimistic = false;
                    var optimisticTimeout = null;

                    function formatTime(seconds) {
                        if (isNaN(seconds)) return "0:00";
                        var mins = Math.floor(seconds / 60);
                        var secs = Math.floor(seconds % 60);
                        return mins + ":" + (secs < 10 ? '0' : '') + secs;
                    }

                    function send(c) { 
                        var x = new XMLHttpRequest(); 
                        x.open("GET", "/action/" + c, true); 
                        x.send(); 
                    }

                    function togglePlay() {
                        var icon = document.getElementById('play-icon');
                        var isPlaying = (icon.src.indexOf("pause.png") !== -1);
                        icon.src = isPlaying ? "/static/play.png" : "/static/pause.png";

                        isOptimistic = true;
                        clearTimeout(optimisticTimeout);
                        optimisticTimeout = setTimeout(function() { isOptimistic = false; }, 1500);
                        send('play');
                    }

                    // Update media info very 500ms
                    function updateMedia() {
                        var x = new XMLHttpRequest();
                        x.open("GET", "/get_spotify_data", true);
                        x.onreadystatechange = function() {
                            if (x.readyState == 4 && x.status == 200) {
                                var data = JSON.parse(x.responseText);
                                document.getElementById('song-title').innerText = data.title || "Nothing Playing";
                                document.getElementById('song-artist').innerText = data.artist || "";
                                document.getElementById('progress-bar').style.width = (data.progress || 0) + "%";

                                if (!isOptimistic) {
                                    document.getElementById('play-icon').src = data.is_playing ? "/static/pause.png" : "/static/play.png";
                                }

                                var currentTime = formatTime(data.position);
                                var totalTime = formatTime(data.duration);
                                document.getElementById('time-display').innerText = currentTime + " / " + totalTime;

                                var art = document.getElementById('album-art');
                                art.src = "/static/now_playing/cover.jpg?t=" + new Date().getTime();
                            }
                        };
                        x.send();
                    }

                    // Update volume info separately and more often
                    function updateVolume() {
                        var v = new XMLHttpRequest();
                        v.open("GET", "/get_volumes_data", true);
                        v.onreadystatechange = function() {
                            if (v.readyState == 4 && v.status == 200) {
                                var volData = JSON.parse(v.responseText);
                                if (volData["Spotify"]) {
                                    var level = volData["Spotify"].level;
                                    // Don't move the thumb farther than the slider
                                    var visualBottom = ((level / 100) * 220 / 260) * 100; 
                                    document.getElementById('vol-thumb').style.bottom = visualBottom + "%";
                                    document.getElementById('vol-text').innerText = level;
                                }
                            }
                        };
                        v.send();
                    }

                    setInterval(updateMedia, 500);
                    setInterval(updateVolume, 150);

                    // Load the play/pause icon to the cache for more responsive feel
                    window.onload = function() {
                        var p = new Image(); p.src = "/static/play.png";
                        var s = new Image(); s.src = "/static/pause.png";
                    };
                </script>
            </head>
            <body>
                <a href="/" class="home-link"><img src="/static/green_home.png"></a>

                <div class="main-container">
                    <div class="spotify-content">
                        <img id="album-art" src="/static/now_playing/cover.jpg" onerror="this.src='/static/spotify.png'">
                        <div id="song-title">Loading...</div>
                        <div id="song-artist">Waiting</div>

                        <div class="progress-container">
                            <div id="progress-bar"></div>
                        </div>
                        <div id="time-display">0:00 / 0:00</div>

                        <div class="media-controls">
                            <button class="icon-btn" onclick="send('previous_track')"><img src="/static/rewind.png"></button>
                            <button class="icon-btn" onclick="togglePlay()"><img id="play-icon" src="/static/pause.png"></button>
                            <button class="icon-btn" onclick="send('next_track')"><img src="/static/forward.png"></button>
                        </div>
                    </div>

                    <a href="/volumes" class="vol-link">
                        <div class="volume-section">
                            <div class="track-outer">
                                <div class="track-line">
                                    <div id="vol-thumb" class="thumb" style="bottom: 0%"></div>
                                </div>
                            </div>
                            <div id="vol-text" class="vol-box">0</div>
                        </div>
                    </a>
                </div>
            </body>
            </html>
        ''')