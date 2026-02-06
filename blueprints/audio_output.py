from flask import Blueprint, jsonify, render_template_string
from services import audio_manager

audio_output_bp = Blueprint('output', __name__)


@audio_output_bp.route('/set_output/<device_id>')
def set_output(device_id):

    result = audio_manager.set_audio_playback_device(device_id)

    if result == "Success":
        return jsonify({"status": "Success"})
    else:
        return jsonify({"status": "Failed"}), 500


@audio_output_bp.route('/output')
def output():
    return render_template_string('''
                <!DOCTYPE html>
                <html>
                <head>
                    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
                    <style>
                        body { 
                            background: #121826; color: #fff; font-family: Arial, sans-serif; 
                            margin: 0; padding: 20px; text-align: center;
                        }
                        .back-btn { display: block; color: #666; text-decoration: none; text-align: left; margin-bottom: 30px; }

                        .output-container { display: flex; flex-direction: column; gap: 20px; align-items: center; }
                        
                        .home-link { position: absolute; top: 15px; left: 15px; z-index: 10; }
                        .home-link img { height: 80px; width: 80px; }

                        .device-btn {
                            width: 85%; padding: 25px; background: #1a212e;
                            border: 2px solid #333; border-radius: 12px;
                            color: #aaa; font-size: 20px; font-weight: bold;
                            transition: all 0.2s; -webkit-tap-highlight-color: transparent;
                        }

                        /* Active state uses your Spotify-style green */
                        .device-btn.active {
                            border-color: #1DB954; color: #fff;
                            box-shadow: 0 0 15px rgba(29, 185, 84, 0.3);
                        }
                        .device-btn:active { transform: scale(0.95); }
                    </style>
                    <script>
                        function setDevice(id) {
                            var x = new XMLHttpRequest();
                            x.open("GET", "/set_output/" + id, true);
                            x.onreadystatechange = function() {
                                if (x.readyState == 4 && x.status == 200) { updateUI(); }
                            };
                            x.send();
                        }

                        function updateUI() {
                            var x = new XMLHttpRequest();
                            x.open("GET", "/get_output_data", true);
                            x.onreadystatechange = function() {
                                if (x.readyState == 4 && x.status == 200) {
                                    var data = JSON.parse(x.responseText);
                                    var jblBtn = document.getElementById('btn-JBL');
                                    var hyperBtn = document.getElementById('btn-HyperX');

                                    jblBtn.classList.remove('active');
                                    hyperBtn.classList.remove('active');

                                    // Logic to check which device is active
                                    if (data.current.includes("High Definition")) {
                                        jblBtn.classList.add('active');
                                    } else if (data.current.includes("HyperX")) {
                                        hyperBtn.classList.add('active');
                                    }
                                }
                            };
                            x.send();
                        }

                        window.onload = updateUI;
                        setInterval(updateUI, 2000); // Check every 2 seconds
                    </script>
                </head>
                <body>
                    <a href="/" class="home-link"><img src="/static/green_home.png"></a>
                    <h2 style="margin-bottom:40px;">Audio Output</h2>
                    <div class="output-container">
                        <button id="btn-JBL" class="device-btn" onclick="setDevice('JBL')">🔊 JBL Speaker</button>
                        <button id="btn-HyperX" class="device-btn" onclick="setDevice('HyperX')">🎧 HyperX Headset</button>
                    </div>
                </body>
                </html>
            ''')