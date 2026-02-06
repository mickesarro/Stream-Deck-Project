
import os
import datetime

from winsdk.windows.media.control import GlobalSystemMediaTransportControlsSessionManager as MediaManager
from winsdk.windows.storage.streams import Buffer, InputStreamOptions, DataReader

from services import audio_manager

# Global to track if the song actually changed
last_title = ""


async def get_spotify_info():
    global last_title
    sessions = await MediaManager.request_async()
    TARGET_ID = "Spotify.exe"
    all_sessions = sessions.get_sessions()

    for session in all_sessions:
        if session.source_app_user_model_id == TARGET_ID:
            # Get Playback Info
            playback_info = session.get_playback_info()
            status = playback_info.playback_status  # 4 = Playing, 5 = Paused

            # Timeline
            timeline = session.get_timeline_properties()
            base_pos = timeline.position.total_seconds()
            last_updated = timeline.last_updated_time
            end_seconds = timeline.end_time.total_seconds()

            current_pos = base_pos
            if status == 4:  # Only if song is playing
                now = datetime.datetime.now(datetime.timezone.utc)
                elapsed = (now - last_updated).total_seconds()
                current_pos = min(base_pos + elapsed, end_seconds)

            # Progress bar
            progress_percent = 0
            if end_seconds > 0:
                progress_percent = (current_pos / end_seconds) * 100

            info = await session.try_get_media_properties_async()

            # Only save image if song changed
            if info.title != last_title:
                if info.thumbnail:
                    stream_ref = await info.thumbnail.open_read_async()
                    buffer = Buffer(stream_ref.size)
                    await stream_ref.read_async(buffer, buffer.capacity, InputStreamOptions.NONE)
                    reader = DataReader.from_buffer(buffer)
                    byte_data = bytearray(buffer.length)
                    reader.read_bytes(byte_data)

                    folder_path = audio_manager.get_resource_path("static/now_playing")
                    if not os.path.exists(folder_path): os.makedirs(folder_path)
                    file_path = os.path.join(folder_path, "cover.jpg")
                    with open(file_path, "wb") as f:
                        f.write(byte_data)
                last_title = info.title

            return {
                "title": info.title,
                "artist": info.artist,
                "progress": round(progress_percent, 1),
                "position": int(current_pos),
                "duration": int(end_seconds),
                "is_playing": status == 4,
                "changed": info.title != last_title
            }
    return None


async def control_spotify(command):
    sessions = await MediaManager.request_async()
    TARGET_ID = "Spotify.exe"
    all_sessions = sessions.get_sessions()

    for session in all_sessions:
        if session.source_app_user_model_id == TARGET_ID:
            if command == "play_pause":
                await session.try_toggle_play_pause_async()
            elif command == "next":
                await session.try_skip_next_async()
            elif command == "previous":
                await session.try_skip_previous_async()
            return True

        return False




